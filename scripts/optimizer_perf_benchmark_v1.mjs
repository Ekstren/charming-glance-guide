import { chromium } from 'playwright';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import crypto from 'node:crypto';

const browser = await chromium.launch({headless:true});
const page = await browser.newPage({viewport:{width:1600,height:1000}});
const fixedNow = Date.parse('2026-09-09T08:00:00-07:00');
await page.addInitScript(({fixedNow}) => {
  const RealDate = Date;
  class FixedDate extends RealDate {
    constructor(...args){ super(...(args.length ? args : [fixedNow])); }
    static now(){ return fixedNow; }
    static parse(v){ return RealDate.parse(v); }
    static UTC(...args){ return RealDate.UTC(...args); }
  }
  Object.setPrototypeOf(FixedDate, RealDate);
  window.Date = FixedDate;
}, {fixedNow});

const url = pathToFileURL(path.resolve('index.html')).href;
await page.goto(url,{waitUntil:'load'});
await page.locator('.sectionSwitch button[data-section="calculator"]').click();
await page.waitForFunction(()=>!!document.querySelector('#calculatorSection')?.dataset.lastSolveMs,null,{timeout:60000});

const setValue = async (id,value) => page.evaluate(({id,value})=>{ const el=document.getElementById(id); if(el) el.value=String(value); },{id,value});

async function runCase(name, values){
  const all = {
    targetStars:920,historicalStars:253,charLevel:126,charExp:0,bedExp:516970,
    skillLevel:126,relicLevel:13,fantomonLevel:130,
    gearWeapon:130,gearOffhand:130,gearHelmet:130,gearArmor:130,gearBoots:130,
    oreCurrent:0,oreRate:0,essenceCurrent:0,essenceRate:0,
    sandCurrent:0,sandBlueCurrent:0,sandEpicCurrent:0,sandRate:0,
    treatCurrent:0,treatPremiumCurrent:0,treatDeluxeCurrent:0,treatRate:0,
    hammerCurrent:0,knucklesCurrent:0,shovelCurrent:0,refinedOreCurrent:0,
    ...values
  };
  for(const [id,value] of Object.entries(all)) await setValue(id,value);
  await setValue('exactSkillLevels','');
  await setValue('exactRelicLevels','');
  await setValue('exactFantoLevels','');
  await setValue('staminaMode','auto');
  const timing = await page.evaluate(()=>{
    const t0=performance.now();
    updateCalculator();
    const t1=performance.now();
    const section=document.getElementById('calculatorSection');
    return {wallMs:t1-t0,reportedMs:Number(section?.dataset.lastSolveMs||0)};
  });
  const resultText = await page.locator('#calcResults').innerText();
  const fingerprint = crypto.createHash('sha256').update(resultText.replace(/\s+/g,' ').trim()).digest('hex');
  const summary = await page.evaluate(()=>({
    stars:document.getElementById('optimizedStars')?.textContent||document.getElementById('summaryOptimizedStars')?.textContent||'',
    score:document.getElementById('summaryOptimizedScore')?.textContent||document.getElementById('optimizedScore')?.textContent||'',
    target:document.getElementById('desiredScore')?.textContent||'',
    status:document.getElementById('targetStatus')?.textContent||'',
    projected:document.getElementById('projectedCharacter')?.textContent||''
  }));
  console.log(JSON.stringify({name,...timing,fingerprint,summary}));
  return {name,...timing,fingerprint,summary};
}

const cases=[];
cases.push(await runCase('s2-920-zero-resources',{}));
cases.push(await runCase('s2-920-zero-resources-repeat',{}));
cases.push(await runCase('s2-920-funded',{oreCurrent:50000000,essenceCurrent:50000000,sandCurrent:50000000,treatCurrent:5000000,refinedOreCurrent:5000000}));

console.log('BENCHMARK_JSON='+JSON.stringify(cases));
await browser.close();
