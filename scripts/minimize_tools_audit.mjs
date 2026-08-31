import { chromium } from 'playwright';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const browser = await chromium.launch({headless:true});
const page = await browser.newPage({viewport:{width:1500,height:1000}});
const errors=[];
page.on('pageerror', e=>errors.push(String(e?.stack||e)));
await page.goto(pathToFileURL(path.resolve('index.html')).href,{waitUntil:'load'});
await page.waitForTimeout(250);
await page.evaluate(()=>{ try{localStorage.clear();}catch(_){} });
await page.reload({waitUntil:'load'});
await page.waitForTimeout(250);
await page.locator('.sectionSwitch button[data-section="calculator"]').click();
await page.waitForTimeout(300);

const common={historicalStars:253,charLevel:130,charExp:2000000,bedExp:280772,skillLevel:130,relicLevel:13,fantomonLevel:130,
  gearWeapon:130,gearOffhand:130,gearHelmet:130,gearArmor:130,gearBoots:130,
  sandBlueCurrent:0,treatPremiumCurrent:0,treatDeluxeCurrent:0,staminaMode:'auto'};
const scenarios=[
  {
    name:'A · 800 target · tool-rich / raw-poor',
    v:{...common,targetStars:800,oreCurrent:900000,essenceCurrent:500000,sandCurrent:450000,treatCurrent:150000,
      oreRate:0,essenceRate:0,sandRate:0,treatRate:0,hammerCurrent:2500,knucklesCurrent:2500,shovelCurrent:2500,
      realmDailyOre:0,realmDailyEssence:0,realmDailySand:0,shopRefreshesDaily:0}
  },
  {
    name:'B · 800 target · balanced + daily Realm',
    v:{...common,targetStars:800,oreCurrent:3000000,essenceCurrent:2200000,sandCurrent:1800000,treatCurrent:160000,
      oreRate:1000,essenceRate:1200,sandRate:800,treatRate:80,hammerCurrent:700,knucklesCurrent:700,shovelCurrent:700,
      realmDailyOre:4,realmDailyEssence:4,realmDailySand:4,shopRefreshesDaily:0}
  },
  {
    name:'C · 920 target · Essence-starved / Knuckle-rich',
    v:{...common,targetStars:920,oreCurrent:7500000,essenceCurrent:300000,sandCurrent:4200000,treatCurrent:210000,
      oreRate:1000,essenceRate:200,sandRate:800,treatRate:80,hammerCurrent:150,knucklesCurrent:4000,shovelCurrent:150,
      realmDailyOre:0,realmDailyEssence:0,realmDailySand:0,shopRefreshesDaily:0}
  }
];

function parseUse(text,label){
  const re=new RegExp(`Use:\\s*([0-9,]+)\\s+${label}`,'i');
  const m=String(text||'').match(re);
  return m?Number(m[1].replaceAll(',','')):0;
}
async function applyScenario(values){
  await page.evaluate(values=>{
    for(const [id,val] of Object.entries(values)){
      const el=document.getElementById(id);
      if(el) el.value=String(val);
    }
    for(const id of ['exactSkillLevels','exactRelicLevels','exactFantoLevels']){
      const el=document.getElementById(id); if(el) el.value='';
    }
    const preserve=document.getElementById('preserveRealmTools');
    preserve.checked=false;
  },values);
  // One solve for OFF. Avoid a redundant pre-toggle solve.
  await page.locator('#targetStars').dispatchEvent('change');
  await page.waitForTimeout(150);
}
async function toggleOn(){
  await page.evaluate(()=>{
    const el=document.getElementById('preserveRealmTools');
    el.checked=true;
    el.dispatchEvent(new Event('change',{bubbles:true}));
  });
  await page.waitForTimeout(150);
}
async function readResult(){
  return await page.evaluate(()=>{
    const txt=id=>document.getElementById(id)?.textContent?.trim()||'';
    return {
      score:txt('optimizedScore'),skills:txt('targetSkills'),relics:txt('targetRelics'),fantos:txt('targetFantomons'),
      gear:['targetGearWeapon','targetGearOffhand','targetGearHelmet','targetGearArmor','targetGearBoots'].map(txt),
      oreCost:txt('oreCost'),essenceCost:txt('essenceCost'),sandCost:txt('sandCost'),treatCost:txt('treatCost'),
      oreBalance:txt('oreBalance'),essenceBalance:txt('essenceBalance'),sandBalance:txt('sandBalance')
    };
  });
}

const rows=[];
for(const scenario of scenarios){
  const started=Date.now();
  await applyScenario(scenario.v);
  const off=await readResult();
  const offMs=Date.now()-started;
  const onStarted=Date.now();
  await toggleOn();
  const on=await readResult();
  const onMs=Date.now()-onStarted;
  const extract=r=>({h:parseUse(r.oreBalance,'Hammers'),k:parseUse(r.essenceBalance,'Knuckles'),s:parseUse(r.sandBalance,'Shovels')});
  const a=extract(off),b=extract(on);
  const offTotal=a.h+a.k+a.s,onTotal=b.h+b.k+b.s;
  rows.push({name:scenario.name,off,on,offTools:a,onTools:b,offTotal,onTotal,delta:onTotal-offTotal,offMs,onMs});
}

console.log('\n=== MINIMIZE TOOLS AUDIT ===');
for(const r of rows){
  console.log(`\n${r.name}`);
  console.log(`OFF tools ${r.offTotal} = H${r.offTools.h} K${r.offTools.k} S${r.offTools.s} (${r.offMs} ms)`);
  console.log(` ON tools ${r.onTotal} = H${r.onTools.h} K${r.onTools.k} S${r.onTools.s}  delta ${r.delta>=0?'+':''}${r.delta} (${r.onMs} ms)`);
  console.log(`OFF plan: skills ${r.off.skills}; relics ${r.off.relics}; fanto ${r.off.fantos}; gear ${r.off.gear.join('/')}`);
  console.log(` ON plan: skills ${r.on.skills}; relics ${r.on.relics}; fanto ${r.on.fantos}; gear ${r.on.gear.join('/')}`);
  console.log(`OFF costs: O ${r.off.oreCost} E ${r.off.essenceCost} S ${r.off.sandCost} T ${r.off.treatCost}`);
  console.log(` ON costs: O ${r.on.oreCost} E ${r.on.essenceCost} S ${r.on.sandCost} T ${r.on.treatCost}`);
}
const increased=rows.filter(r=>r.delta>0),decreased=rows.filter(r=>r.delta<0),same=rows.filter(r=>r.delta===0);
console.log(`\nSummary: decreased ${decreased.length}/${rows.length}; increased ${increased.length}/${rows.length}; unchanged ${same.length}/${rows.length}.`);
if(increased.length) console.log('ON used MORE total tools in:',increased.map(x=>`${x.name} (+${x.delta})`).join('; '));
console.log('Implementation note: this control applies a >10% hurdle to spending extra saved tools and >20% to extra paid Realm purchases. It is not a strict total-tool minimizer.');
if(errors.length) throw new Error('Runtime errors:\n'+errors.join('\n---\n'));
await browser.close();
