import { chromium } from 'playwright';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const browser=await chromium.launch({headless:true});
const page=await browser.newPage({viewport:{width:1500,height:1000}});
const errors=[];
page.on('pageerror',e=>errors.push(String(e?.stack||e)));
await page.goto(pathToFileURL(path.resolve('index.html')).href,{waitUntil:'load'});
await page.waitForTimeout(250);
await page.evaluate(()=>{try{localStorage.clear();}catch(_){}});
await page.reload({waitUntil:'load'});
await page.waitForTimeout(250);
await page.locator('.sectionSwitch button[data-section="calculator"]').click();
await page.waitForTimeout(300);

const common={historicalStars:253,charLevel:130,charExp:2000000,bedExp:280772,skillLevel:130,relicLevel:13,fantomonLevel:130,
  gearWeapon:130,gearOffhand:130,gearHelmet:130,gearArmor:130,gearBoots:130,
  sandBlueCurrent:0,treatPremiumCurrent:0,treatDeluxeCurrent:0,staminaMode:'auto'};
const scenarios=[
  {name:'A · 800 · low raw / huge tool bank',v:{...common,targetStars:800,oreCurrent:900000,essenceCurrent:500000,sandCurrent:450000,treatCurrent:350000,oreRate:0,essenceRate:0,sandRate:0,treatRate:0,hammerCurrent:9000,knucklesCurrent:9000,shovelCurrent:9000,realmDailyOre:0,realmDailyEssence:0,realmDailySand:0,shopRefreshesDaily:0}},
  {name:'B · 920 · balanced + cart + 4/day Realm',v:{...common,targetStars:920,oreCurrent:5000000,essenceCurrent:3200000,sandCurrent:2800000,treatCurrent:350000,oreRate:1000,essenceRate:1200,sandRate:800,treatRate:80,hammerCurrent:5000,knucklesCurrent:5000,shovelCurrent:5000,realmDailyOre:4,realmDailyEssence:4,realmDailySand:4,shopRefreshesDaily:0}},
  {name:'C · 920 · Essence-starved / Knuckle-heavy',v:{...common,targetStars:920,oreCurrent:7000000,essenceCurrent:350000,sandCurrent:4000000,treatCurrent:350000,oreRate:1000,essenceRate:200,sandRate:800,treatRate:80,hammerCurrent:3000,knucklesCurrent:10000,shovelCurrent:3000,realmDailyOre:1,realmDailyEssence:0,realmDailySand:1,shopRefreshesDaily:0}}
];

const txt=async id=>page.locator(`#${id}`).textContent().then(x=>(x||'').trim());
function parseUse(text,label){
  const m=String(text||'').match(new RegExp(`Use:\\s*([0-9,]+)\\s+${label}`,'i'));
  return m?Number(m[1].replaceAll(',','')):0;
}
async function setScenario(v,on){
  await page.evaluate(({v,on})=>{
    for(const [id,val] of Object.entries(v)){const el=document.getElementById(id);if(el)el.value=String(val);}
    ['exactSkillLevels','exactRelicLevels','exactFantoLevels'].forEach(id=>{const el=document.getElementById(id);if(el)el.value='';});
    const t=document.getElementById('preserveRealmTools');if(t)t.checked=on;
  },{v,on});
  await page.locator('#targetStars').dispatchEvent('change');
  await page.waitForTimeout(180);
}
async function readResult(){
  const [hText,kText,sText]=await Promise.all([txt('oreToolBalance'),txt('essenceToolBalance'),txt('sandToolBalance')]);
  const h=parseUse(hText,'Hammers'),k=parseUse(kText,'Knuckles'),s=parseUse(sText,'Shovels');
  return {
    tools:{h,k,s,total:h+k+s},toolText:[hText,kText,sText],
    skills:await txt('targetSkills'),relics:await txt('targetRelics'),fantos:await txt('targetFantomons'),
    gear:await Promise.all(['targetGearWeapon','targetGearOffhand','targetGearHelmet','targetGearArmor','targetGearBoots'].map(txt)),
    costs:await Promise.all(['oreCost','essenceCost','sandCost','treatCost'].map(txt)),
    status:await txt('targetStatus')
  };
}

const rows=[];
for(const sc of scenarios){
  let t=Date.now();await setScenario(sc.v,false);const off=await readResult();const offMs=Date.now()-t;
  t=Date.now();await setScenario(sc.v,true);const on=await readResult();const onMs=Date.now()-t;
  rows.push({name:sc.name,off,on,offMs,onMs,delta:on.tools.total-off.tools.total});
}
console.log('\n=== MINIMIZE TOOLS AUDIT ===');
for(const r of rows){
  console.log(`\n${r.name}`);
  console.log(`OFF ${r.off.status}: ${r.off.tools.total} tools = H${r.off.tools.h} K${r.off.tools.k} S${r.off.tools.s} (${r.offMs}ms)`);
  console.log(` ON ${r.on.status}: ${r.on.tools.total} tools = H${r.on.tools.h} K${r.on.tools.k} S${r.on.tools.s} (${r.onMs}ms), delta ${r.delta>=0?'+':''}${r.delta}`);
  console.log('OFF tool rows:',r.off.toolText.join(' | '));
  console.log(' ON tool rows:',r.on.toolText.join(' | '));
  console.log(`OFF plan: Skills ${r.off.skills}; Relics ${r.off.relics}; Fanto ${r.off.fantos}; Gear ${r.off.gear.join('/')}; Costs ${r.off.costs.join('/')}`);
  console.log(` ON plan: Skills ${r.on.skills}; Relics ${r.on.relics}; Fanto ${r.on.fantos}; Gear ${r.on.gear.join('/')}; Costs ${r.on.costs.join('/')}`);
}
const down=rows.filter(r=>r.delta<0),up=rows.filter(r=>r.delta>0),same=rows.filter(r=>r.delta===0);
console.log(`\nSummary: ON decreased total tools ${down.length}/${rows.length}, increased ${up.length}/${rows.length}, unchanged ${same.length}/${rows.length}.`);
if(up.length)console.log('Counterexamples:',up.map(r=>`${r.name} (+${r.delta})`).join('; '));
console.log('Reminder: the live toggle is a >10% saved-tool / >20% paid-purchase efficiency hurdle, NOT a strict total-tool minimizer.');
if(errors.length)throw new Error('Runtime errors:\n'+errors.join('\n---\n'));
await browser.close();
