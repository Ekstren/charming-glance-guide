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

await page.evaluate(()=>{
  const el=document.getElementById('targetStars');
  el.value='60';
  el.dispatchEvent(new Event('change',{bubbles:true}));
});

await page.waitForFunction(()=>{
  const summary=document.getElementById('optimizerSummary');
  const hero=document.getElementById('currentStars')?.textContent||'';
  return summary && !summary.hidden && /projected raw-only potential/i.test(summary.textContent||'') && hero.trim()!=='—';
},{timeout:30000});

const heroText=(await page.locator('#currentStars').innerText()).replace(/,/g,'').trim();
const hero=Number(heroText);
if(hero!==60) throw new Error(`Goal plan should stop at 60, got hero ${heroText}`);

const summary=await page.locator('#optimizerSummary').innerText();
const m=summary.match(/projected raw-only potential\s+([\d,]+)/i);
if(!m) throw new Error(`Projected raw-only potential missing: ${summary}`);
const potential=Number(m[1].replace(/,/g,''));
if(!(potential>60)) throw new Error(`Expected informational raw-only potential above 60, got ${potential}`);
if(!/(goal plan happened to use raw only|raw \+ saved\/planned Realm tools optimized as one pool)/i.test(summary)){
  throw new Error(`Owned/projected pool source summary missing: ${summary}`);
}

const optimized=await page.locator('#optimizedScore').innerText();
if(!/goal\s+60/i.test(optimized)) throw new Error(`Goal result missing from optimized score: ${optimized}`);
if(/Smart Balance\s+\d+/i.test(optimized)) throw new Error(`Optimized score still promotes the raw ceiling into the recommendation: ${optimized}`);

// Owned/projected tools may now be selected even when raw alone could reach the goal; what must
// never happen here is an EXTRA Realm-purchase recommendation, because the existing pool is huge.
if(await page.locator('.applyRealmRecommendation').count()) throw new Error('Extra Realm purchase recommendation appeared despite a fully funded owned/projected pool');
if(errors.length) throw new Error('Runtime errors:\n'+errors.join('\n---\n'));

console.log(`Smart Balance goal-stop smoke passed: recommended 60, informational raw-only potential ${potential}, source=${summary}.`);
await browser.close();
