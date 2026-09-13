import { chromium } from 'playwright';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const browser = await chromium.launch({headless:true});
const page = await browser.newPage({viewport:{width:1440,height:1000}});
const errors=[];
page.on('pageerror',e=>errors.push(String(e?.stack||e)));

// Freeze wall-clock time so snapshot aging / future-reset counts cannot make the same
// input fingerprint drift while the benchmark is running.
const FIXED_NOW=Date.parse('2026-08-31T01:00:00Z');
await page.addInitScript(now=>{
  const NativeDate=Date;
  class FixedDate extends NativeDate{
    constructor(...args){ super(...(args.length?args:[now])); }
    static now(){ return now; }
  }
  globalThis.Date=FixedDate;
},FIXED_NOW);

await page.goto(pathToFileURL(path.resolve('index.html')).href,{waitUntil:'load'});
await page.waitForTimeout(250);
await page.locator('.sectionSwitch button[data-section="calculator"]').click();
// S2 defaults have zero production inputs, so seed Bed EXP + Cart rates before waiting
// for the calculator to render a non-placeholder result.
await page.evaluate(()=>{
  const set=(id,v)=>{const el=document.getElementById(id);if(el){el.value=v;el.dispatchEvent(new Event('change',{bubbles:true}));}};
  set('bedExp','280772');
  set('oreRate','1184');
  set('essenceRate','1387');
  set('sandRate','850');
  set('treatRate','91');
});
await page.waitForFunction(()=>{
  const total=document.querySelector('.starTotal')?.textContent||'';
  return total && !total.includes('—');
},null,{timeout:10000});
await page.waitForTimeout(150);
// The initial solve must be fully settled before scenario reads, otherwise the first
// scenario can race an in-flight cooperative search and read the previous result.
await waitCalculatorSettled(page,'initial solve',15000);

// S2_ABOVE_CHARACTER_UPGRADES_V1: at Character Lv.131 the planner must not cap
// Gear, Skills, or Relic ranks to the Character level. These are the supported
// ceilings of the extracted S2 cost tables, not claims about a lower character gate.
const s2Caps=await page.evaluate(()=>window.__sxsPlannerCapProbeV1?.(131));
if(!s2Caps) throw new Error('missing S2 planner-cap regression probe');
if(s2Caps.skill!==280 || s2Caps.relic!==28 || s2Caps.gear!==430){
  throw new Error(`S2 above-character planning regressed: ${JSON.stringify(s2Caps)}`);
}
if(!(s2Caps.skill>131 && s2Caps.relic>15 && s2Caps.gear>131)){
  throw new Error(`S2 Gear/Skill/Relic planner is still Character-level capped: ${JSON.stringify(s2Caps)}`);
}
console.log(`S2 CAPS char131: Gear ${s2Caps.gear} · Skills ${s2Caps.skill} · Relics +${s2Caps.relic} · Fantomon ${s2Caps.fanto}`);
if(!(s2Caps.fanto>140)) throw new Error(`S2 Fantomon planning is still Character-level capped: ${JSON.stringify(s2Caps)}`);
const resonance=await page.evaluate(()=>window.__sxsResonanceGateProbeV1?.());
if(!resonance) throw new Error('missing S2 resonance-gate regression probe');
if(!resonance.relicLegal || resonance.relicFirst16!==resonance.relicAll15+1){
  throw new Error(`Relic resonance gate regressed: ${JSON.stringify(resonance)}`);
}
if(!resonance.fantoLegal || resonance.fantoFirst151!==resonance.fantoAll150+1){
  throw new Error(`Fantomon decade resonance gate regressed: ${JSON.stringify(resonance)}`);
}
console.log(`S2 GATES relic all +15 @${resonance.relicAll15}, first +16 @${resonance.relicFirst16} · Fanto all 150 @${resonance.fantoAll150}, first 151 @${resonance.fantoFirst151}`);

const gearEditor=await page.evaluate(()=>({
  average:!!document.getElementById('gearLevel'),
  exact:!!document.getElementById('exactGearLevels'),
  legacy:['gearWeapon','gearOffhand','gearHelmet','gearArmor','gearBoots'].filter(id=>document.getElementById(id)).length,
  cartLine:!!document.getElementById('graceText')
}));
if(!gearEditor.average || !gearEditor.exact || gearEditor.legacy!==0 || gearEditor.cartLine){
  throw new Error(`compact Gear editor regression: ${JSON.stringify(gearEditor)}`);
}
console.log('GEAR EDITOR average + exact override · legacy five-field row removed · cart production line removed');

const base={
  targetStars:'920',historicalStars:'253',charLevel:'130',charExp:'2005316',bedExp:'280772',
  skillLevel:'130',relicLevel:'13',fantomonLevel:'130',gearLevel:'130',exactGearLevels:'',
  oreRate:'1184',essenceRate:'1387',sandRate:'850',treatRate:'91',
  shopRefreshesDaily:'0',realmDailyOre:'4',realmDailyEssence:'4',realmDailySand:'4'
};

const noCart={oreRate:'0',essenceRate:'0',sandRate:'0',treatRate:'0'};
const scenarios=[
  ['realistic-mixed',{...base,oreCurrent:'240000',essenceCurrent:'420000',sandCurrent:'390000',treatCurrent:'32000',treatPremiumCurrent:'700',treatDeluxeCurrent:'4',hammerCurrent:'110',knucklesCurrent:'399',shovelCurrent:'427'}],
  ['raw-abundant',{...base,...noCart,oreCurrent:'10000000',essenceCurrent:'10000000',sandCurrent:'10000000',treatCurrent:'500000',treatPremiumCurrent:'0',treatDeluxeCurrent:'0',hammerCurrent:'0',knucklesCurrent:'0',shovelCurrent:'0',realmDailyOre:'0',realmDailyEssence:'0',realmDailySand:'0'}],
  ['tool-heavy',{...base,...noCart,oreCurrent:'0',essenceCurrent:'0',sandCurrent:'0',treatCurrent:'250000',treatPremiumCurrent:'0',treatDeluxeCurrent:'0',hammerCurrent:'5000',knucklesCurrent:'5000',shovelCurrent:'5000',realmDailyOre:'0',realmDailyEssence:'0',realmDailySand:'0'}],
  ['high-target-mixed',{...base,targetStars:'1060',oreCurrent:'1200000',essenceCurrent:'900000',sandCurrent:'800000',treatCurrent:'60000',treatPremiumCurrent:'800',treatDeluxeCurrent:'5',hammerCurrent:'600',knucklesCurrent:'600',shovelCurrent:'600',realmDailyOre:'8',realmDailyEssence:'8',realmDailySand:'8'}],
  ['production-only-low-target',{...base,targetStars:'680',oreCurrent:'0',essenceCurrent:'0',sandCurrent:'0',treatCurrent:'0',treatPremiumCurrent:'0',treatDeluxeCurrent:'0',hammerCurrent:'0',knucklesCurrent:'0',shovelCurrent:'0',realmDailyOre:'0',realmDailyEssence:'0',realmDailySand:'0'}],
  ['true-starved-low-target',{...base,...noCart,targetStars:'680',oreCurrent:'0',essenceCurrent:'0',sandCurrent:'0',treatCurrent:'0',treatPremiumCurrent:'0',treatDeluxeCurrent:'0',hammerCurrent:'0',knucklesCurrent:'0',shovelCurrent:'0',realmDailyOre:'0',realmDailyEssence:'0',realmDailySand:'0'}]
];

// CALC_SETTLE_PROBE_V1: resolve only after the app reports every scheduled
// updateCalculator() run has completed. A DOM quiet window is not enough: a cooperative
// optimizer search renders nothing until it finishes, so "no mutations for 100 ms" can
// resolve mid-search and read the previous (stale) result.
async function waitCalculatorSettled(page,label,timeoutMs=10000){
  // Give the app one paint turn so rAF/setTimeout-scheduled updates commit to the settle
  // counter before we start observing it (the goal control schedules via rAF).
  await page.waitForTimeout(50);
  try{
    await page.waitForFunction(
      ()=>typeof window.__sxsCalculatorSettledV1==='function' && window.__sxsCalculatorSettledV1()===true,
      null,
      { timeout: timeoutMs, polling: 'raf' }
    );
  }catch(err){
    throw new Error(`${label} did not settle within ${timeoutMs}ms (calculator still running or settle probe missing)`);
  }
}

const runScenario=async(name,fields)=>{
  const t0=performance.now();
  await page.evaluate(({fields})=>{
    const resultRoot=document.querySelector('.calcResults');
    if(!resultRoot) throw new Error('calculator result root missing');
    const triggerId=Object.keys(fields).at(-1);
    for(const [id,value] of Object.entries(fields)){
      const el=document.getElementById(id);
      if(!el) throw new Error(`missing calculator input ${id}`);
      el.value=String(value);
    }
    document.getElementById(triggerId).dispatchEvent(new Event('change',{bubbles:true}));
  },{fields});
  await waitCalculatorSettled(page,`${name} solve`,10000);
  const ms=performance.now()-t0;
  const read=await page.evaluate(()=>{
    const text=sel=>document.querySelector(sel)?.innerText?.replace(/\s+/g,' ').trim()||'';
    return {
      total:text('.starTotal'),
      score:text('.resultScoreLine'),
      upgrades:text('.optimizerTargets'),
      gear:text('.suggestedGear'),
      costs:text('.planCosts'),
      stamina:text('#staminaCurrentPlan')
    };
  });
  return { name, ms, ...read };
}

const results=[];
const fingerprint=x=>JSON.stringify([x.total,x.score,x.upgrades,x.gear,x.costs,x.stamina]);
for(let i=0;i<scenarios.length;i++){
  const [name,fields]=scenarios[i];
  const r=await runScenario(name,fields);
  results.push(r);
  console.log(`PERF ${name}: ${r.ms.toFixed(1)}ms · ${r.total} · ${r.score}`);
  if(r.ms>5000) throw new Error(`${name} took ${r.ms.toFixed(1)}ms (>5s lockup guard)`);

  // Check determinism immediately on the representative real-world case, before any
  // other scenario has changed the resource controls.
  if(i===0){
    const repeat=await runScenario(`${name}-repeat`,fields);
    if(fingerprint(r)!==fingerprint(repeat)){
      console.error('FIRST ',fingerprint(r));
      console.error('REPEAT',fingerprint(repeat));
      throw new Error('same frozen-time calculator inputs produced a different recommendation on repeat');
    }
    results.push({...repeat,name:`${name}-repeat`});
    console.log(`DETERMINISM ${name}: stable · repeat ${repeat.ms.toFixed(1)}ms`);
  }
}

// Event-coalescing check: a burst of target edits should settle once, not queue a backlog.
const burstT0=performance.now();
for(const value of ['681','700','760','800','840','880','900','920']){
  await page.evaluate(v=>{
    const el=document.getElementById('targetStars');
    el.value=v;
    el.dispatchEvent(new Event('change',{bubbles:true}));
  },value);
  await page.waitForTimeout(10);
}
await waitCalculatorSettled(page,'rapid edit burst',10000);
const burst={
  ms:performance.now()-burstT0,
  total:(await page.evaluate(()=>document.querySelector('.starTotal')?.innerText||'')).replace(/\s+/g,' ')
};
console.log(`BURST 8 target edits: ${burst.ms.toFixed(1)}ms · final ${burst.total}`);
if(burst.ms>5000) throw new Error(`rapid edit burst took ${burst.ms.toFixed(1)}ms (>5s lockup guard)`);

if(errors.length) throw new Error('browser runtime errors:\n'+errors.join('\n---\n'));
const times=[...results.map(x=>x.ms),burst.ms];
const avg=times.reduce((a,b)=>a+b,0)/times.length;
const max=Math.max(...times);
console.log(`SUMMARY average ${avg.toFixed(1)}ms · worst ${max.toFixed(1)}ms · ${scenarios.length} scenarios + repeat + burst`);
await browser.close();
