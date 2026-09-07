import { chromium } from 'playwright';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const browser = await chromium.launch({headless:true});
const page = await browser.newPage({viewport:{width:1280,height:1000}});
const errors=[];
page.on('pageerror', e => errors.push(String(e?.stack || e)));
await page.goto(pathToFileURL(path.resolve('index.html')).href,{waitUntil:'load'});
await page.evaluate(()=>localStorage.clear());
await page.reload({waitUntil:'load'});
await page.locator('.sectionSwitch button[data-section="calculator"]').click();
await page.waitForTimeout(100);

// Put the calculator in a deterministic S2 state. Raw materials are deliberately ample,
// while a large Realm-tool inventory is present so the regression proves Smart Balance
// does NOT consume tools merely because they exist.
await page.evaluate(()=>{
  const set=(id,value)=>{const el=document.getElementById(id);if(el)el.value=String(value);};
  set('historicalStars',0);
  set('charLevel',130); set('charExp',0); set('bedExp',0);
  set('skillLevel',130); set('relicLevel',13); set('fantomonLevel',130);
  for(const id of ['gearWeapon','gearOffhand','gearHelmet','gearArmor','gearBoots']) set(id,130);
  set('oreCurrent',2000000); set('oreRate',0);
  set('essenceCurrent',1000000); set('essenceRate',0);
  set('sandCurrent',1000000); set('sandBlueCurrent',0); set('sandEpicCurrent',0); set('sandRate',0);
  set('treatCurrent',100000); set('treatPremiumCurrent',0); set('treatDeluxeCurrent',0); set('treatRate',0);
  set('shopRefreshesDaily',0);
  set('hammerCurrent',999); set('knucklesCurrent',999); set('shovelCurrent',999);
  set('realmDailyOre',4); set('realmDailyEssence',4); set('realmDailySand',4);
  document.getElementById('confirmSeasonSnapshot')?.click();
});
await page.waitForTimeout(250);

// Confirming an S2 snapshot may restore the normal S2 target. Set our explicit minimum
// afterwards and commit it through the same `change` path used by real calculator fields.
await page.evaluate(()=>{
  const el=document.getElementById('targetStars');
  el.value='60';
  el.dispatchEvent(new Event('change',{bubbles:true}));
});
await page.waitForFunction(()=>{
  const t=document.getElementById('optimizedScore')?.textContent||'';
  return /Smart Balance/i.test(t) && /goal\s+60/i.test(t);
},{timeout:30000});

const projectedText=(await page.locator('#currentStars').innerText()).replace(/,/g,'').trim();
const projected=Number(projectedText);
if(!Number.isFinite(projected) || projected<=60) throw new Error(`Expected Smart Balance projection above goal 60, got ${projectedText}`);

const optimized=await page.locator('#optimizedScore').innerText();
if(!/Smart Balance/i.test(optimized) || !/goal\s+60/i.test(optimized)) throw new Error(`Smart Balance result label missing: ${optimized}`);
const summary=await page.locator('#optimizerSummary').innerText();
if(!/raw projected materials only/i.test(summary)) throw new Error(`Raw-first source summary missing: ${summary}`);

for(const id of ['oreToolBalance','essenceToolBalance','sandToolBalance']){
  const uses=await page.locator(`#${id} .toolUseLine`).count();
  if(uses) throw new Error(`${id} consumed Realm tools even though raw-only Smart Balance was fundable`);
}
if(await page.locator('.applyRealmRecommendation').count()) throw new Error('Extra Realm purchase recommendation appeared on a raw-only Smart Balance plan');
if(errors.length) throw new Error('Runtime errors:\n'+errors.join('\n---\n'));

console.log(`Smart Balance smoke passed: goal 60 -> projected ${projected}; raw-only route preserved all Realm tools.`);
await browser.close();
