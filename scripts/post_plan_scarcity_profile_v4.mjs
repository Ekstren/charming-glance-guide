import { chromium } from 'playwright';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const browser=await chromium.launch({headless:true});
const page=await browser.newPage({viewport:{width:1500,height:1100}});
const errors=[];
page.on('pageerror',e=>errors.push(String(e?.stack||e)));

// Freeze at season end so the profile tests only the optimizer economics supplied below.
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
  set('historicalStars',253);set('targetStars',800);
  set('charLevel',188);set('charExp',0);set('bedExp',0);
  set('skillLevel',130);set('relicLevel',13);set('fantomonLevel',130);
  for(const id of ['gearWeapon','gearOffhand','gearHelmet','gearArmor','gearBoots'])set(id,130);

  // Approximate the resource/tool shape from the Sep 6 user screenshot: enough raw for the
  // goal, but materially more Essence/Knuckle reserve than Ore/Hammer reserve.
  set('oreCurrent',2808105);set('oreRate',0);
  set('essenceCurrent',2770881);set('essenceRate',0);
  set('sandCurrent',3862307);set('sandBlueCurrent',0);set('sandEpicCurrent',0);set('sandRate',0);
  set('treatCurrent',188933);set('treatPremiumCurrent',0);set('treatDeluxeCurrent',0);set('treatRate',0);
  set('shopRefreshesDaily',0);
  set('hammerCurrent',1253);set('knucklesCurrent',1572);set('shovelCurrent',1310);
  set('realmDailyOre',0);set('realmDailyEssence',0);set('realmDailySand',0);
  document.getElementById('confirmSeasonSnapshot')?.click();
});

await page.waitForFunction(()=>{
  const hero=document.getElementById('currentStars')?.textContent?.trim()||'';
  return hero && hero!=='—' && document.getElementById('targetSkills')?.textContent?.trim()!=='—';
},{timeout:30000});
await page.waitForTimeout(100);

const parseMixAvg=text=>{
  let total=0,count=0;
  for(const part of String(text).split(/\s*[·,]\s*/)){
    let m=part.match(/(\d+)\s*×\s*(?:Lv\.|\+)(\d+)/i);
    if(m){total+=Number(m[1])*Number(m[2]);count+=Number(m[1]);continue;}
    m=part.match(/(?:Lv\.|\+)(\d+)/i);
    if(m){total+=Number(m[1]);count++;}
  }
  return count?total/count:NaN;
};
const parseRemaining=text=>{
  const m=String(text).replace(/,/g,'').match(/Remaining:\s*([0-9]+)/i);
  return m?Number(m[1]):NaN;
};
const text=sel=>page.locator(sel).innerText().catch(()=> '');
const skills=await text('#targetSkills');
const gear=await page.locator('#targetGearWeapon,#targetGearOffhand,#targetGearHelmet,#targetGearArmor,#targetGearBoots').allInnerTexts();
const gearAvg=gear.map(x=>Number(String(x).replace(/[^0-9.]/g,''))).reduce((a,b)=>a+b,0)/gear.length;
const oreBalance=await text('#oreBalance');
const essenceBalance=await text('#essenceBalance');
const sandBalance=await text('#sandBalance');
const oreTool=await text('#oreToolBalance');
const essenceTool=await text('#essenceToolBalance');
const sandTool=await text('#sandToolBalance');
const result={
  stars:await text('#currentStars'),
  summary:await text('#optimizerSummary'),
  skills,skillAvg:parseMixAvg(skills),gear,gearAvg,
  oreRemaining:parseRemaining(oreBalance),
  essenceRemaining:parseRemaining(essenceBalance),
  sandRemaining:parseRemaining(sandBalance),
  oreTool,essenceTool,sandTool,
  costs:await text('.planCosts')
};
if(errors.length) throw new Error('Runtime errors:\n'+errors.join('\n---\n'));
if(!String(result.stars).includes('800')) throw new Error(`Profile missed 800 target: ${JSON.stringify(result)}`);
console.log('POST_PLAN_PROFILE',JSON.stringify(result,null,2));
await browser.close();
