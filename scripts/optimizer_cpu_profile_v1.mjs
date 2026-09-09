import { chromium } from 'playwright';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const browser=await chromium.launch({headless:true});
const page=await browser.newPage({viewport:{width:1600,height:1000}});
const fixedNow=Date.parse('2026-09-09T08:00:00-07:00');
await page.addInitScript(({fixedNow})=>{
  const RealDate=Date;
  class FixedDate extends RealDate{
    constructor(...args){super(...(args.length?args:[fixedNow]));}
    static now(){return fixedNow;}
    static parse(v){return RealDate.parse(v);}
    static UTC(...args){return RealDate.UTC(...args);}
  }
  Object.setPrototypeOf(FixedDate,RealDate);
  window.Date=FixedDate;
},{fixedNow});

await page.goto(pathToFileURL(path.resolve('index.html')).href,{waitUntil:'load'});
await page.locator('.sectionSwitch button[data-section="calculator"]').click();
await page.waitForFunction(()=>!!document.querySelector('#calculatorSection')?.dataset.lastSolveMs,null,{timeout:60000});

const values={
  targetStars:920,historicalStars:253,charLevel:126,charExp:0,bedExp:516970,
  skillLevel:126,relicLevel:13,fantomonLevel:130,
  gearWeapon:130,gearOffhand:130,gearHelmet:130,gearArmor:130,gearBoots:130,
  oreCurrent:50000000,oreRate:1000,essenceCurrent:50000000,essenceRate:1200,
  sandCurrent:50000000,sandBlueCurrent:0,sandEpicCurrent:0,sandRate:800,
  treatCurrent:5000000,treatPremiumCurrent:0,treatDeluxeCurrent:0,treatRate:80,
  hammerCurrent:0,knucklesCurrent:0,shovelCurrent:0,refinedOreCurrent:5000000
};
await page.evaluate(({values})=>{
  for(const [id,value] of Object.entries(values)){
    const el=document.getElementById(id); if(el) el.value=String(value);
  }
  for(const id of ['exactSkillLevels','exactRelicLevels','exactFantoLevels']){
    const el=document.getElementById(id); if(el) el.value='';
  }
  const mode=document.getElementById('staminaMode'); if(mode) mode.value='auto';
  const section=document.getElementById('calculatorSection'); if(section) section.dataset.lastSolveMs='';
},{values});

const cdp=await page.context().newCDPSession(page);
await cdp.send('Profiler.enable');
await cdp.send('Profiler.setSamplingInterval',{interval:100});
await cdp.send('Profiler.start');
const wallStart=Date.now();
await page.evaluate(()=>document.getElementById('targetStars')?.dispatchEvent(new Event('change',{bubbles:true})));
await page.waitForFunction(()=>!!document.querySelector('#calculatorSection')?.dataset.lastSolveMs,null,{timeout:60000});
const wallMs=Date.now()-wallStart;
const reportedMs=await page.evaluate(()=>Number(document.querySelector('#calculatorSection')?.dataset.lastSolveMs||0));
const {profile}=await cdp.send('Profiler.stop');

const nodes=new Map(profile.nodes.map(n=>[n.id,n]));
const selfUs=new Map();
const samples=profile.samples||[],deltas=profile.timeDeltas||[];
for(let i=0;i<samples.length;i++){
  const node=nodes.get(samples[i]); if(!node) continue;
  const f=node.callFrame||{};
  const key=`${f.functionName||'(anonymous)'} @ ${path.basename(f.url||'inline')}:${(f.lineNumber??-1)+1}`;
  selfUs.set(key,(selfUs.get(key)||0)+(Number(deltas[i])||0));
}
const totalUs=[...selfUs.values()].reduce((a,b)=>a+b,0);
const top=[...selfUs.entries()].sort((a,b)=>b[1]-a[1]).slice(0,35);
console.log(`PROFILE reported=${reportedMs.toFixed(1)}ms wall=${wallMs}ms sampled=${(totalUs/1000).toFixed(1)}ms samples=${samples.length}`);
for(const [name,us] of top){
  console.log(`${(us/1000).toFixed(1).padStart(8)} ms  ${(100*us/Math.max(1,totalUs)).toFixed(1).padStart(5)}%  ${name}`);
}

await browser.close();
