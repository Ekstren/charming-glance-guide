import { chromium } from 'playwright';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const browser=await chromium.launch({headless:true});
const page=await browser.newPage({viewport:{width:1440,height:1100}});
const errors=[];
page.on('pageerror',e=>errors.push(String(e?.stack||e)));

// Freeze at the final minute so saved tools are available but no future paid-refresh day can
// muddy the raw-vs-owned-pool behavior being tested.
await page.addInitScript(()=>{
  const fixed=Date.parse('2026-11-05T05:59:00-08:00');
  const RealDate=Date;
  class FixedDate extends RealDate{
    constructor(...args){super(...(args.length?args:[fixed]));}
    static now(){return fixed;}
  }
  Object.setPrototypeOf(FixedDate,RealDate);
  window.Date=FixedDate;
});

await page.goto(pathToFileURL(path.resolve('index.html')).href,{waitUntil:'load'});
await page.evaluate(()=>localStorage.clear());
await page.reload({waitUntil:'load'});
await page.locator('.sectionSwitch button[data-section="calculator"]').click();

await page.evaluate(()=>{
  const set=(id,value)=>{const el=document.getElementById(id);if(el)el.value=String(value);};
  set('historicalStars',0);
  set('charLevel',160);set('charExp',0);set('bedExp',0);
  set('skillLevel',130);set('relicLevel',13);set('fantomonLevel',130);
  for(const id of ['gearWeapon','gearOffhand','gearHelmet','gearArmor','gearBoots'])set(id,130);

  // Raw Ore alone is intentionally enough to reach the target through Gear, while the much
  // larger Essence family is mostly represented by saved Knuckles. The new optimizer should
  // be allowed to choose that healthier pooled Skill route instead of forcing raw-only Gear.
  set('oreCurrent',700000);set('oreRate',0);set('hammerCurrent',0);
  set('essenceCurrent',60000);set('essenceRate',0);set('knucklesCurrent',1000);
  set('sandCurrent',0);set('sandBlueCurrent',0);set('sandEpicCurrent',0);set('sandRate',0);set('shovelCurrent',0);
  set('treatCurrent',0);set('treatPremiumCurrent',0);set('treatDeluxeCurrent',0);set('treatRate',0);
  set('shopRefreshesDaily',0);
  set('realmDailyOre',0);set('realmDailyEssence',0);set('realmDailySand',0);
  document.getElementById('confirmSeasonSnapshot')?.click();
});
await page.waitForTimeout(150);
await page.evaluate(()=>{
  const el=document.getElementById('targetStars');
  el.value='180';el.dispatchEvent(new Event('change',{bubbles:true}));
});
await page.waitForFunction(()=>{
  const hero=document.getElementById('currentStars')?.textContent||'';
  const summary=document.getElementById('optimizerSummary')?.textContent||'';
  return hero.trim()==='180' && /Goal\s+180/i.test(summary);
},{timeout:30000});

const summary=await page.locator('#optimizerSummary').innerText();
if(!/projected raw-only potential\s+(?:18\d|19\d|[2-9]\d\d)/i.test(summary)){
  throw new Error(`Test setup did not prove raw-only reachability: ${summary}`);
}
if(!/raw \+ saved\/planned Realm tools optimized as one pool/i.test(summary)){
  throw new Error(`Optimizer still forced the raw-only route instead of the healthier owned pool: ${summary}`);
}
if(/extra Realm purchases required/i.test(summary)) throw new Error(`Extra purchases appeared despite saved Knuckles: ${summary}`);

const parseNum=txt=>Number(String(txt).replace(/[^0-9.]/g,''));
const essenceCost=parseNum(await page.locator('#essenceCost').innerText());
if(!(essenceCost>60000)) throw new Error(`Expected pooled plan to lean into Skills beyond raw Essence; cost=${essenceCost}`);
const essenceToolText=await page.locator('#essenceToolBalance').innerText();
const useMatch=essenceToolText.match(/Use:\s*([\d,]+)\s+Knuckles/i);
if(!useMatch) throw new Error(`Expected saved Knuckles to fund the pooled plan: ${essenceToolText}`);
const used=Number(useMatch[1].replace(/,/g,''));
const expected=Math.ceil(Math.max(0,essenceCost-60000)/1500);
if(used!==expected){
  throw new Error(`Raw-before-tools funding violated: Essence cost ${essenceCost}, raw 60000, expected ${expected} Knuckles, displayed ${used}. ${essenceToolText}`);
}

// There are no Hammers. The selected Gear spend must therefore stay within the raw Ore budget.
const oreCost=parseNum(await page.locator('#oreCost').innerText());
if(oreCost>700000+0.5) throw new Error(`Gear exceeded raw Ore despite no Hammers: ${oreCost}`);
if(await page.locator('.applyRealmRecommendation').count()) throw new Error('Unexpected extra Realm-purchase recommendation');
if(errors.length) throw new Error('Runtime errors:\n'+errors.join('\n---\n'));

console.log('Total-pool Smart Balance smoke passed.',{summary,oreCost,essenceCost,knucklesUsed:used,expectedKnuckles:expected});
await browser.close();
