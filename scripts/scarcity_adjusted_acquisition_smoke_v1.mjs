import { chromium } from 'playwright';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const browser=await chromium.launch({headless:true});
const page=await browser.newPage({viewport:{width:1440,height:1100}});
const errors=[];
page.on('pageerror',e=>errors.push(String(e?.stack||e)));

// Freeze one minute before the S2 cutoff so no projected Stamina/shop/cart income muddies
// the saved-tool scarcity regression.
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

const parseSkillAvg=text=>{
  let total=0,count=0;
  for(const part of String(text).split(/\s*[·,]\s*/)){
    let m=part.match(/(\d+)\s*×\s*Lv\.(\d+)/i);
    if(m){total+=Number(m[1])*Number(m[2]);count+=Number(m[1]);continue;}
    m=part.match(/Lv\.(\d+)/i);
    if(m){total+=Number(m[1]);count++;}
  }
  return count?total/count:NaN;
};
const runProfile=async({hammers,knuckles})=>{
  await page.evaluate(({hammers,knuckles})=>{
    localStorage.clear();
    const set=(id,value)=>{const el=document.getElementById(id);if(el)el.value=String(value);};
    set('historicalStars',0);
    set('charLevel',160);set('charExp',0);set('bedExp',0);
    set('skillLevel',130);set('relicLevel',13);set('fantomonLevel',130);
    for(const id of ['gearWeapon','gearOffhand','gearHelmet','gearArmor','gearBoots'])set(id,130);
    set('oreCurrent',0);set('oreRate',0);
    set('essenceCurrent',0);set('essenceRate',0);
    set('sandCurrent',0);set('sandBlueCurrent',0);set('sandEpicCurrent',0);set('sandRate',0);
    set('treatCurrent',0);set('treatPremiumCurrent',0);set('treatDeluxeCurrent',0);set('treatRate',0);
    set('shopRefreshesDaily',0);
    set('hammerCurrent',hammers);set('knucklesCurrent',knuckles);set('shovelCurrent',0);
    set('realmDailyOre',0);set('realmDailyEssence',0);set('realmDailySand',0);
    document.getElementById('confirmSeasonSnapshot')?.click();
  },{hammers,knuckles});
  await page.waitForTimeout(150);
  await page.evaluate(()=>{
    const el=document.getElementById('targetStars');
    el.value='180';el.dispatchEvent(new Event('change',{bubbles:true}));
  });
  await page.waitForFunction(()=>{
    const hero=document.getElementById('currentStars')?.textContent||'';
    return hero.trim()!=='—' && document.getElementById('targetSkills')?.textContent?.trim()!=='—';
  },{timeout:30000});
  const skillText=await page.locator('#targetSkills').innerText();
  const gear=await page.locator('#targetGearWeapon,#targetGearOffhand,#targetGearHelmet,#targetGearArmor,#targetGearBoots').allInnerTexts();
  const gearAvg=gear.map(x=>Number(String(x).replace(/[^0-9.]/g,''))).reduce((a,b)=>a+b,0)/gear.length;
  const skillAvg=parseSkillAvg(skillText);
  const summary=await page.locator('#optimizerSummary').innerText();
  return {skillAvg,gearAvg,skillText,gear,summary};
};

// Pure math regression: scarcity must modify acquisition value for Ore too, and surplus
// may get cheap but never literally free because the floor is 25%.
const economics=await page.evaluate(()=>{
  const low={acquisitionHeadroomCosts:{ore:1000,essence:1000,sand:1000,treat:1000},acquisitionSupplyEquiv:{ore:100,essence:100,sand:100,treat:100}};
  const high={acquisitionHeadroomCosts:{ore:1000,essence:1000,sand:1000,treat:1000},acquisitionSupplyEquiv:{ore:2000,essence:2000,sand:2000,treat:2000}};
  return {
    oreLow:marginalWeightedSpend(100,'ore',low),oreHigh:marginalWeightedSpend(100,'ore',high),
    essenceLow:marginalWeightedSpend(100,'essence',low),essenceHigh:marginalWeightedSpend(100,'essence',high)
  };
});
if(!(economics.oreHigh<economics.oreLow && economics.oreHigh>=24.99)) throw new Error(`Ore scarcity floor/regression failed: ${JSON.stringify(economics)}`);
if(!(economics.essenceHigh<economics.essenceLow && economics.essenceHigh>=24.99)) throw new Error(`Essence scarcity floor/regression failed: ${JSON.stringify(economics)}`);

const knuckleRich=await runProfile({hammers:120,knuckles:1000});
const hammerRich=await runProfile({hammers:1000,knuckles:120});
if(!(knuckleRich.skillAvg>hammerRich.skillAvg+0.2)){
  throw new Error(`Knuckle-rich profile did not shift enough score toward Skills. knuckle-rich=${JSON.stringify(knuckleRich)} hammer-rich=${JSON.stringify(hammerRich)}`);
}
if(!(hammerRich.gearAvg>knuckleRich.gearAvg+0.2)){
  throw new Error(`Hammer-rich profile did not shift enough score toward Gear. knuckle-rich=${JSON.stringify(knuckleRich)} hammer-rich=${JSON.stringify(hammerRich)}`);
}
if(errors.length) throw new Error('Runtime errors:\n'+errors.join('\n---\n'));
console.log('Scarcity-adjusted acquisition smoke passed.',{economics,knuckleRich,hammerRich});
await browser.close();
