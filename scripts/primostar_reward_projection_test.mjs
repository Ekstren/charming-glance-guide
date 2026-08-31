import { chromium } from 'playwright';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const browser=await chromium.launch({headless:true});
const page=await browser.newPage({viewport:{width:1440,height:1000}});
const errors=[];
page.on('pageerror',e=>errors.push(String(e?.stack||e)));
await page.goto(pathToFileURL(path.resolve('index.html')).href,{waitUntil:'load'});
await page.locator('.sectionSwitch button[data-section="calculator"]').click();
await page.waitForTimeout(200);

// Use a 920 S2 projection similar to the live screenshot. Exact current total can vary with
// the entered snapshot, but the reward reference must never call a threshold below the
// projected total the "next" reward.
const set=(id,val)=>page.evaluate(({id,val})=>{const el=document.getElementById(id);if(!el)throw new Error(`missing ${id}`);el.value=String(val);},{id,val});
await set('targetStars',920);
await set('historicalStars',253);
await set('charLevel',130);
await set('charExp',2327303);
await set('bedExp',280772);
await set('skillLevel',130);
await set('relicLevel',13);
await set('fantomonLevel',130);
for(const id of ['gearWeapon','gearOffhand','gearHelmet','gearArmor','gearBoots']) await set(id,130);
await page.evaluate(()=>document.getElementById('targetStars').dispatchEvent(new Event('change',{bubbles:true})));
await page.waitForFunction(()=>/920/.test(document.querySelector('.starTotal')?.innerText||''),null,{timeout:10000});
await page.locator('.primostarRewardsDetails').evaluate(el=>el.open=true);
await page.waitForTimeout(120);

const data=await page.evaluate(()=>{
  const intro=document.getElementById('primostarRewardsIntro')?.textContent||'';
  const projected=[...document.querySelectorAll('.primostarRewardRow.projected .rewardThreshold')].map(x=>parseInt(x.textContent.replace(/\D/g,''),10)).filter(Number.isFinite);
  const reached=[...document.querySelectorAll('.primostarRewardRow.reached .rewardThreshold')].map(x=>parseInt(x.textContent.replace(/\D/g,''),10)).filter(Number.isFinite);
  const next=[...document.querySelectorAll('.primostarRewardRow.next .rewardThreshold')].map(x=>parseInt(x.textContent.replace(/\D/g,''),10)).filter(Number.isFinite);
  return {intro,projected,reached,next};
});

if(!/920 projected/.test(data.intro)) throw new Error(`projection summary missing 920 projected: ${data.intro}`);
if(!/next after projection/.test(data.intro)) throw new Error(`projection summary still describes current-only next reward: ${data.intro}`);
if(!data.projected.includes(920)) throw new Error(`920 threshold is not visually marked projected: ${data.projected.join(',')}`);
if(data.next.length!==1 || data.next[0]<=920) throw new Error(`next reward must be above projected 920, got ${data.next.join(',')}`);
if(data.reached.some(x=>x>920)) throw new Error('actually-reached styling leaked above projection');
if(errors.length) throw new Error('runtime errors:\n'+errors.join('\n---\n'));

console.log(`reward projection passed: ${data.intro} · projected through ${Math.max(...data.projected)} · next ${data.next[0]}`);
await browser.close();
