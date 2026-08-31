import { chromium } from 'playwright';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const browser = await chromium.launch({headless:true});
const page = await browser.newPage({viewport:{width:1440,height:1000}});
const errors=[];
page.on('pageerror',e=>errors.push(String(e?.stack||e)));

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
  shopRefreshesDaily:'0',realmDailyOre:'4',realmDailyEssence:'4',realmDailySand:'4'
};

const scenarios=[
  ['realistic-mixed',{...base,oreCurrent:'240000',essenceCurrent:'420000',sandCurrent:'390000',treatCurrent:'32000',treatPremiumCurrent:'700',treatDeluxeCurrent:'4',hammerCurrent:'110',knucklesCurrent:'399',shovelCurrent:'427'}],
  ['raw-abundant',{...base,oreCurrent:'10000000',essenceCurrent:'10000000',sandCurrent:'10000000',treatCurrent:'500000',treatPremiumCurrent:'0',treatDeluxeCurrent:'0',hammerCurrent:'0',knucklesCurrent:'0',shovelCurrent:'0',realmDailyOre:'0',realmDailyEssence:'0',realmDailySand:'0'}],
  ['tool-heavy',{...base,oreCurrent:'0',essenceCurrent:'0',sandCurrent:'0',treatCurrent:'250000',treatPremiumCurrent:'0',treatDeluxeCurrent:'0',hammerCurrent:'5000',knucklesCurrent:'5000',shovelCurrent:'5000',realmDailyOre:'0',realmDailyEssence:'0',realmDailySand:'0'}],
  ['high-target-mixed',{...base,targetStars:'1060',oreCurrent:'1200000',essenceCurrent:'900000',sandCurrent:'800000',treatCurrent:'60000',treatPremiumCurrent:'800',treatDeluxeCurrent:'5',hammerCurrent:'600',knucklesCurrent:'600',shovelCurrent:'600',realmDailyOre:'8',realmDailyEssence:'8',realmDailySand:'8'}],
  ['lower-target-starved',{...base,targetStars:'680',oreCurrent:'0',essenceCurrent:'0',sandCurrent:'0',treatCurrent:'0',treatPremiumCurrent:'0',treatDeluxeCurrent:'0',hammerCurrent:'0',knucklesCurrent:'0',shovelCurrent:'0',realmDailyOre:'0',realmDailyEssence:'0',realmDailySand:'0'}]
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
    costs:text('.planCosts')
  };
},{name,fields});

const results=[];
for(const [name,fields] of scenarios){
  const r=await runScenario(name,fields);
  results.push(r);
  console.log(`PERF ${name}: ${r.ms.toFixed(1)}ms · mutations ${r.mutations} · ${r.total} · ${r.score}`);
  if(r.ms>5000) throw new Error(`${name} took ${r.ms.toFixed(1)}ms (>5s lockup guard)`);
}

// Determinism check: identical inputs must produce an identical recommendation fingerprint.
const [repeatName,repeatFields]=scenarios[0];
const repeat=await runScenario(`${repeatName}-repeat`,repeatFields);
const first=results[0];
const fingerprint=x=>JSON.stringify([x.total,x.score,x.upgrades,x.gear,x.costs]);
if(fingerprint(first)!==fingerprint(repeat)) throw new Error('same calculator inputs produced a different recommendation on repeat');
console.log(`DETERMINISM ${repeatName}: stable · repeat ${repeat.ms.toFixed(1)}ms`);

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
const times=[...results.map(x=>x.ms),repeat.ms,burst.ms];
const avg=times.reduce((a,b)=>a+b,0)/times.length;
const max=Math.max(...times);
console.log(`SUMMARY average ${avg.toFixed(1)}ms · worst ${max.toFixed(1)}ms · scenarios ${results.length} + repeat + burst`);
await browser.close();
