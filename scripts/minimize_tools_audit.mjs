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
await page.waitForTimeout(350);

const scenarios=[
  {
    name:'A · tool-rich / raw-poor',
    v:{targetStars:920,historicalStars:253,charLevel:130,charExp:2000000,bedExp:280772,skillLevel:130,relicLevel:13,fantomonLevel:130,
      gearWeapon:130,gearOffhand:130,gearHelmet:130,gearArmor:130,gearBoots:130,
      oreCurrent:1800000,essenceCurrent:900000,sandCurrent:900000,sandBlueCurrent:0,treatCurrent:200000,treatPremiumCurrent:0,treatDeluxeCurrent:0,
      oreRate:0,essenceRate:0,sandRate:0,treatRate:0,
      hammerCurrent:3500,knucklesCurrent:3500,shovelCurrent:3500,
      realmDailyOre:0,realmDailyEssence:0,realmDailySand:0,shopRefreshesDaily:0,staminaMode:'auto'}
  },
  {
    name:'B · balanced stockpile + cart + 4/day Realm',
    v:{targetStars:920,historicalStars:253,charLevel:130,charExp:2000000,bedExp:280772,skillLevel:130,relicLevel:13,fantomonLevel:130,
      gearWeapon:130,gearOffhand:130,gearHelmet:130,gearArmor:130,gearBoots:130,
      oreCurrent:4200000,essenceCurrent:3200000,sandCurrent:2400000,sandBlueCurrent:0,treatCurrent:180000,treatPremiumCurrent:0,treatDeluxeCurrent:0,
      oreRate:1000,essenceRate:1200,sandRate:800,treatRate:80,
      hammerCurrent:900,knucklesCurrent:900,shovelCurrent:900,
      realmDailyOre:4,realmDailyEssence:4,realmDailySand:4,shopRefreshesDaily:0,staminaMode:'auto'}
  },
  {
    name:'C · Essence-starved / Knuckle-rich',
    v:{targetStars:920,historicalStars:253,charLevel:130,charExp:2000000,bedExp:280772,skillLevel:130,relicLevel:13,fantomonLevel:130,
      gearWeapon:130,gearOffhand:130,gearHelmet:130,gearArmor:130,gearBoots:130,
      oreCurrent:7500000,essenceCurrent:250000,sandCurrent:3800000,sandBlueCurrent:0,treatCurrent:200000,treatPremiumCurrent:0,treatDeluxeCurrent:0,
      oreRate:1000,essenceRate:200,sandRate:800,treatRate:80,
      hammerCurrent:150,knucklesCurrent:4000,shovelCurrent:150,
      realmDailyOre:0,realmDailyEssence:0,realmDailySand:0,shopRefreshesDaily:0,staminaMode:'auto'}
  },
  {
    name:'D · raw-rich / almost no Realm tools',
    v:{targetStars:920,historicalStars:253,charLevel:130,charExp:2000000,bedExp:280772,skillLevel:130,relicLevel:13,fantomonLevel:130,
      gearWeapon:130,gearOffhand:130,gearHelmet:130,gearArmor:130,gearBoots:130,
      oreCurrent:12000000,essenceCurrent:9000000,sandCurrent:7000000,sandBlueCurrent:0,treatCurrent:250000,treatPremiumCurrent:0,treatDeluxeCurrent:0,
      oreRate:1000,essenceRate:1200,sandRate:800,treatRate:80,
      hammerCurrent:20,knucklesCurrent:20,shovelCurrent:20,
      realmDailyOre:0,realmDailyEssence:0,realmDailySand:0,shopRefreshesDaily:0,staminaMode:'auto'}
  },
  {
    name:'E · uneven Realm purchase plan',
    v:{targetStars:920,historicalStars:253,charLevel:130,charExp:2000000,bedExp:280772,skillLevel:130,relicLevel:13,fantomonLevel:130,
      gearWeapon:130,gearOffhand:130,gearHelmet:130,gearArmor:130,gearBoots:130,
      oreCurrent:3000000,essenceCurrent:1800000,sandCurrent:1600000,sandBlueCurrent:0,treatCurrent:200000,treatPremiumCurrent:0,treatDeluxeCurrent:0,
      oreRate:900,essenceRate:1100,sandRate:700,treatRate:80,
      hammerCurrent:600,knucklesCurrent:1200,shovelCurrent:500,
      realmDailyOre:2,realmDailyEssence:8,realmDailySand:1,shopRefreshesDaily:3,staminaMode:'auto'}
  }
];

function numText(s){
  const n=Number(String(s||'').replace(/[^0-9.-]/g,''));
  return Number.isFinite(n)?n:0;
}
function parseUse(text,label){
  const re=new RegExp(`Use:\\s*([0-9,]+)\\s+${label}`,'i');
  const m=String(text||'').match(re);
  return m?Number(m[1].replaceAll(',','')):0;
}

async function setScenario(values){
  await page.evaluate(values=>{
    for(const [id,val] of Object.entries(values)){
      const el=document.getElementById(id);
      if(!el) continue;
      if(el.tagName==='SELECT') el.value=String(val);
      else el.value=String(val);
    }
    for(const id of ['exactSkillLevels','exactRelicLevels','exactFantoLevels']){
      const el=document.getElementById(id); if(el) el.value='';
    }
  },values);
  await page.locator('#targetStars').dispatchEvent('change');
  await page.waitForTimeout(250);
}
async function setToggle(on){
  await page.evaluate(on=>{
    const el=document.getElementById('preserveRealmTools');
    el.checked=on;
    el.dispatchEvent(new Event('change',{bubbles:true}));
  },on);
  await page.waitForTimeout(250);
}
async function readResult(){
  return await page.evaluate(()=>{
    const txt=id=>document.getElementById(id)?.textContent?.trim()||'';
    const targetGear=['targetGearWeapon','targetGearOffhand','targetGearHelmet','targetGearArmor','targetGearBoots'].map(txt);
    return {
      score:txt('optimizedScore'),stars:txt('currentStars'),summary:txt('optimizerSummary'),
      skills:txt('targetSkills'),relics:txt('targetRelics'),fantos:txt('targetFantomons'),gear:targetGear,
      oreCost:txt('oreCost'),essenceCost:txt('essenceCost'),sandCost:txt('sandCost'),treatCost:txt('treatCost'),
      oreBalance:txt('oreBalance'),essenceBalance:txt('essenceBalance'),sandBalance:txt('sandBalance'),treatBalance:txt('treatBalance')
    };
  });
}

const rows=[];
for(const scenario of scenarios){
  await setScenario(scenario.v);
  await setToggle(false);
  const off=await readResult();
  await setToggle(true);
  const on=await readResult();
  const extract=r=>({
    h:parseUse(r.oreBalance,'Hammers'),
    k:parseUse(r.essenceBalance,'Knuckles'),
    s:parseUse(r.sandBalance,'Shovels')
  });
  const a=extract(off),b=extract(on);
  const offTotal=a.h+a.k+a.s,onTotal=b.h+b.k+b.s;
  rows.push({name:scenario.name,off,on,offTools:a,onTools:b,offTotal,onTotal,delta:onTotal-offTotal});
}

console.log('\n=== MINIMIZE TOOLS AUDIT ===');
for(const r of rows){
  console.log(`\n${r.name}`);
  console.log(`OFF tools ${r.offTotal} = H${r.offTools.h} K${r.offTools.k} S${r.offTools.s}`);
  console.log(` ON tools ${r.onTotal} = H${r.onTools.h} K${r.onTools.k} S${r.onTools.s}  delta ${r.delta>=0?'+':''}${r.delta}`);
  console.log(`OFF plan: skills ${r.off.skills}; relics ${r.off.relics}; fanto ${r.off.fantos}; gear ${r.off.gear.join('/')}`);
  console.log(` ON plan: skills ${r.on.skills}; relics ${r.on.relics}; fanto ${r.on.fantos}; gear ${r.on.gear.join('/')}`);
  console.log(`OFF costs: O ${r.off.oreCost} E ${r.off.essenceCost} S ${r.off.sandCost} T ${r.off.treatCost}`);
  console.log(` ON costs: O ${r.on.oreCost} E ${r.on.essenceCost} S ${r.on.sandCost} T ${r.on.treatCost}`);
}
const increased=rows.filter(r=>r.delta>0);
const decreased=rows.filter(r=>r.delta<0);
const same=rows.filter(r=>r.delta===0);
console.log(`\nSummary: tool total decreased in ${decreased.length}/${rows.length}, increased in ${increased.length}/${rows.length}, unchanged in ${same.length}/${rows.length}.`);
if(increased.length) console.log('Cases where ON used MORE total tools:', increased.map(x=>`${x.name} (+${x.delta})`).join('; '));
console.log('NOTE: current implementation is a 10% saved-tool / 20% paid-purchase efficiency hurdle, not a strict total-tool minimizer.');

if(errors.length) throw new Error('Runtime errors:\n'+errors.join('\n---\n'));
await browser.close();
