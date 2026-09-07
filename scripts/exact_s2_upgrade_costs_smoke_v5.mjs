import { chromium } from 'playwright';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const browser=await chromium.launch({headless:true});
const page=await browser.newPage({viewport:{width:1440,height:1100}});
const errors=[];
page.on('pageerror',e=>errors.push(String(e?.stack||e)));

await page.addInitScript(()=>{
  const fixed=Date.parse('2026-09-07T12:00:00-07:00');
  const RealDate=Date;
  class FixedDate extends RealDate{
    constructor(...args){super(...(args.length?args:[fixed]));}
    static now(){return fixed;}
  }
  Object.setPrototypeOf(FixedDate,RealDate);
  window.Date=FixedDate;
});

await page.goto(pathToFileURL(path.resolve('index.html')).href,{waitUntil:'load'});
const got=await page.evaluate(()=>{
  const cfg=CALC_SEASONS.s2;
  return {
    marker:document.documentElement.innerHTML.includes('EXACT_S2_UPGRADE_COSTS_V5'),
    charLen:S2_EXACT_CHARACTER_EXP_FROM_130.length,
    fantoLen:S2_EXACT_FANTOMON_EXP_FROM_130.length,
    gear130:gearStepCost(130,cfg),
    gear131:gearStepCost(131,cfg),
    gear160:gearStepCost(160,cfg),
    gear188:gearStepCost(188,cfg),
    skill130:skillStepCost(130,cfg),
    skill140:skillStepCost(140,cfg),
    skill160:skillStepCost(160,cfg),
    skill180:skillStepCost(180,cfg),
    relic13:relicStepSand(13,cfg),
    relic18:relicStepSand(18,cfg),
    relic27:relicStepSand(27,cfg),
    fanto130:fantoStepTreatCost(130,cfg),
    fanto160:fantoStepTreatCost(160,cfg),
    xp130:expRequiredForLevel(130,cfg),
    xp210:expRequiredForLevel(210,cfg),
    xp281:expRequiredForLevel(281,cfg),
    xp282:expRequiredForLevel(282,cfg),
    refined134:gearStepRefined(134,cfg),
    refined139:gearStepRefined(139,cfg),
    refined135:gearStepRefined(135,cfg),
    preGear121:gearStepCost(121,cfg),
    preSkill121:skillStepCost(121,cfg),
    secondaryStyle:document.getElementById('secondaryCostNote')?.getAttribute('style')||'',
    methodText:document.querySelector('.methodPanel')?.innerText||''
  };
});

const eq=(key,expected,tol=1e-9)=>{
  const actual=got[key];
  if(!Number.isFinite(expected)){
    if(actual!==null && actual!==Infinity && Number.isFinite(actual)) throw new Error(`${key}: expected Infinity, got ${actual}`);
    return;
  }
  if(!Number.isFinite(actual)||Math.abs(actual-expected)>tol) throw new Error(`${key}: expected ${expected}, got ${actual}`);
};

if(!got.marker) throw new Error('Exact S2 marker missing');
if(got.charLen!==152) throw new Error(`Expected 152 extracted S2 Character EXP rows, got ${got.charLen}`);
if(got.fantoLen!==150) throw new Error(`Expected 150 extracted S2 Fantomon EXP rows, got ${got.fantoLen}`);
eq('gear130',16630);          // Lv.130 -> 131
eq('gear131',16795);          // Lv.131 -> 132
eq('gear160',21620);          // Lv.160 -> 161
eq('gear188',26275);          // Lv.188 -> 189
eq('skill130',12025);
eq('skill140',13230);
eq('skill160',15635);
eq('skill180',18040);
eq('relic13',33750);          // 1,350 Purple x25
eq('relic18',50625);          // 2,025 Purple x25
eq('relic27',81000);          // 3,240 Purple x25, 15th known S2 blessing
eq('fanto130',57370/50);
eq('fanto160',91790/50);
eq('xp130',6342809);
eq('xp210',13478732);
eq('xp281',13478732);
if(Number.isFinite(got.xp282)) throw new Error(`xp282 should stop outside extracted range, got ${got.xp282}`);
eq('refined134',510);         // target Lv.135 = S2 blessing 5
eq('refined139',510);         // target Lv.140 = S2 blessing 10
eq('refined135',0);
// Pre-floor catch-up math intentionally remains unchanged.
eq('preGear121',14630);
eq('preSkill121',10265);
if(/display\s*:\s*none\s*!important/i.test(got.secondaryStyle)) throw new Error('Secondary exact Gear costs are still force-hidden');
if(!got.methodText.includes('1,350 Purple Sand')||!got.methodText.includes('510 Refined Ore')||!got.methodText.includes('Rolla is 2× Gear Ore')){
  throw new Error('Exact S2 method/source note is incomplete');
}
if(errors.length) throw new Error('Runtime errors:\n'+errors.join('\n---\n'));

console.log('Exact S2 upgrade-cost smoke passed.',got);
await browser.close();
