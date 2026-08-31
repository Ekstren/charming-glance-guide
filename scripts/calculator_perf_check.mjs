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
await page.waitForFunction(()=>{
  const total=document.querySelector('.starTotal')?.textContent||'';
  return total && !total.includes('—');
},null,{timeout:10000});
await page.waitForTimeout(150);

const base={
  targetStars:'920',historicalStars:'253',charLevel:'130',charExp:'2005316',bedExp:'280772',
  skillLevel:'130',relicLevel:'13',fantomonLevel:'130',
  gearWeapon:'130',gearOffhand:'130',gearHelmet:'130',gearArmor:'130',gearBoots:'130',
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

const runScenario=async(name,fields)=>page.evaluate(async ({name,fields})=>{
  const resultRoot=document.querySelector('.calcResults');
  if(!resultRoot) throw new Error('calculator result root missing');
  const triggerId=Object.keys(fields).at(-1);
  for(const [id,value] of Object.entries(fields)){
    const el=document.getElementById(id);
    if(!el) throw new Error(`missing calculator input ${id}`);
    el.value=String(value);
  }

  let mutations=0;
  let lastMutation=performance.now();
  const started=performance.now();
  const observer=new MutationObserver(()=>{mutations++;lastMutation=performance.now();});
  observer.observe(resultRoot,{subtree:true,childList:true,characterData:true,attributes:true,attributeFilter:['class','style']});
  document.getElementById(triggerId).dispatchEvent(new Event('change',{bubbles:true}));

  await new Promise((resolve,reject)=>{
    const poll=()=>{
      const now=performance.now();
      if(mutations>0 && now-lastMutation>=100){ resolve(); return; }
      if(now-started>10000){ reject(new Error(`${name} did not settle within 10s`)); return; }
      setTimeout(poll,20);
    };
    poll();
  });
  observer.disconnect();

  const text=sel=>document.querySelector(sel)?.innerText?.replace(/\s+/g,' ').trim()||'';
  return {
    name,
    ms:performance.now()-started,
    mutations,
    total:text('.starTotal'),
    score:text('.resultScoreLine'),
    upgrades:text('.optimizerTargets'),
    gear:text('.suggestedGear'),
    costs:text('.planCosts'),
    stamina:text('#staminaCurrentPlan')
  };
},{name,fields});

const results=[];
const fingerprint=x=>JSON.stringify([x.total,x.score,x.upgrades,x.gear,x.costs,x.stamina]);
for(let i=0;i<scenarios.length;i++){
  const [name,fields]=scenarios[i];
  const r=await runScenario(name,fields);
  results.push(r);
  console.log(`PERF ${name}: ${r.ms.toFixed(1)}ms · mutations ${r.mutations} · ${r.total} · ${r.score}`);
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
const burst=await page.evaluate(async ()=>{
  const el=document.getElementById('targetStars');
  const root=document.querySelector('.calcResults');
  let mutations=0,last=performance.now();
  const started=performance.now();
  const obs=new MutationObserver(()=>{mutations++;last=performance.now();});
  obs.observe(root,{subtree:true,childList:true,characterData:true,attributes:true,attributeFilter:['class','style']});
  for(const value of ['681','700','760','800','840','880','900','920']){
    el.value=value;
    el.dispatchEvent(new Event('change',{bubbles:true}));
  }
  await new Promise((resolve,reject)=>{
    const poll=()=>{
      const now=performance.now();
      if(mutations>0&&now-last>=100){resolve();return;}
      if(now-started>10000){reject(new Error('rapid edit burst did not settle'));return;}
      setTimeout(poll,20);
    };poll();
  });
  obs.disconnect();
  return {ms:performance.now()-started,mutations,total:document.querySelector('.starTotal')?.innerText||''};
});
console.log(`BURST 8 target edits: ${burst.ms.toFixed(1)}ms · mutations ${burst.mutations} · final ${burst.total.replace(/\s+/g,' ')}`);
if(burst.ms>5000) throw new Error(`rapid edit burst took ${burst.ms.toFixed(1)}ms (>5s lockup guard)`);

if(errors.length) throw new Error('browser runtime errors:\n'+errors.join('\n---\n'));
const times=[...results.map(x=>x.ms),burst.ms];
const avg=times.reduce((a,b)=>a+b,0)/times.length;
const max=Math.max(...times);
console.log(`SUMMARY average ${avg.toFixed(1)}ms · worst ${max.toFixed(1)}ms · ${scenarios.length} scenarios + repeat + burst`);
await browser.close();
