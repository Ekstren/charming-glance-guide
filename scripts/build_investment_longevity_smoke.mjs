import { chromium } from 'playwright';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const browser = await chromium.launch({headless:true});
const page = await browser.newPage({viewport:{width:1440,height:1000}});
const pageErrors=[];
page.on('pageerror', err => pageErrors.push(String(err?.stack || err)));

const url=pathToFileURL(path.resolve('index.html')).href;
await page.goto(url,{waitUntil:'load'});
await page.waitForTimeout(350);
const assert=(cond,msg)=>{ if(!cond) throw new Error(msg); };

await page.locator('.sectionSwitch button[data-section="builds"]').click();

async function selectClass(cls){
  await page.locator(`#classTabs button[data-class="${cls}"]`).click();
  await page.waitForFunction(c=>document.querySelector('#classTabs button.active')?.dataset.class===c && !!document.querySelector('#buildContent > .priorityPair'),cls);
}

async function visiblePair(){
  const pair=page.locator('#buildContent > .priorityPair:visible');
  assert(await pair.count()===1,`expected one visible priority pair, found ${await pair.count()}`);
  const panels=pair.locator(':scope > .priorityPanel');
  assert(await panels.count()===2,`expected Technique + Charm panels, found ${await panels.count()}`);
  const out=[];
  for(let i=0;i<2;i++){
    const panel=panels.nth(i);
    out.push({
      kind:(await panel.locator('.priorityIntro > span').innerText()).trim(),
      title:(await panel.locator('.priorityIntro > strong').innerText()).trim(),
      desc:(await panel.locator('.priorityIntro > p').innerText()).trim(),
      names:(await panel.locator('.priorityList li strong').allTextContents()).map(x=>x.trim())
    });
  }
  return out;
}

function assertOrder(actual, expected, label){
  assert(actual.length===4,`${label}: expected 4 investments, got ${actual.join(' | ')}`);
  expected.forEach((name,i)=>assert(actual[i]===name,`${label}: #${i+1} expected ${name}, got ${actual[i]}`));
}

await selectClass('Conqueror');
{
  const [tech,charm]=await visiblePair();
  assertOrder(tech.names,['Flickering Blade','Blade Storm','Flash Fire','Flame Aura'],'Conqueror Techniques');
  assertOrder(charm.names,['Piercing Assault','Tactical Adaptation','Soul Breaker','Indomitable Will'],'Conqueror Charms');
  assert(charm.title.includes('long-term'),`Conqueror charm longevity title missing: ${charm.title}`);
  assert(!charm.names.includes('Insightful Eye'),'Conqueror should not recommend deep Insightful Eye investment after S2 gear solves Crit');
}

await selectClass('Guardian');
for(const role of ['tank','dps']){
  await page.locator(`#buildContent button[data-guardian-mode="${role}"]`).click();
  await page.waitForFunction(r=>document.querySelector(`#buildContent button[data-guardian-mode="${r}"]`)?.classList.contains('active'),role);
  const [tech,charm]=await visiblePair();
  assert(tech.names[0]==='Valor Surge',`Guardian ${role}: Valor Surge should be #1, got ${tech.names[0]}`);
  assert(!tech.names.includes('Seismic Tide'),`Guardian ${role}: swap-only Seismic Tide must not be ranked`);
  if(role==='dps') assertOrder(tech.names,['Valor Surge','Swirling Blade','Lunarwater Threads','Raging Maelstrom / Star Shattering Slash'],'Guardian DPS Techniques');
  assert(charm.names.length===4,`Guardian ${role}: expected 4 Charm investments`);
}

await selectClass('Destroyer');
{
  const [tech,charm]=await visiblePair();
  assertOrder(tech.names,['Formation Breaker','Wind Blade Spiral','Thunder of Judgment','Meteoric Flames'],'Destroyer Techniques');
  assertOrder(charm.names,['Radiant Sear','Cyclone Lament','Mana Surge','Fiery Burst / Explosive Spirit'],'Destroyer Charms');
  assert(!charm.names.includes('Rapid Cast'),'Destroyer Rapid Cast should be demoted from scarce-rank top 4 because T5 showcased builds replace it');
}

await selectClass('Dominator');
for(const role of ['dps','heals']){
  await page.locator(`#buildContent button[data-dominator-mode="${role}"]`).click();
  await page.waitForFunction(r=>document.querySelector(`#buildContent button[data-dominator-mode="${r}"]`)?.classList.contains('active'),role);
  const [tech,charm]=await visiblePair();
  if(role==='dps'){
    assertOrder(tech.names,['Dark Starburst','Shadow of Termination','Abyssal Hand','Dark Bullet'],'Dominator DPS Techniques');
    assertOrder(charm.names,['Shadow Vengeance','Shadow Erosion','Linked Misfortune',"Night's Blessing"],'Dominator DPS Charms');
    assert(tech.title.includes('save'),`Dominator DPS should explicitly preserve tickets for T5: ${tech.title}`);
  }else{
    assertOrder(tech.names,['Radiant Restoration','Rejuvenating Rain','Frenzy Totem','Waterling Summon'],'Dominator Healer Techniques');
    assertOrder(charm.names,['Phantom Light','Overhealing','Healing Mastery','Resurrection / Mantra of Blessings'],'Dominator Healer Charms');
  }
}

const visibleFuture=await page.locator('#buildContent > .priorityPair:visible').innerText();
for(const unavailable of ['Radiant Rhythm','Radiant Warp','Twin Gale','Hexed Blast','Soul Reap']){
  assert(!visibleFuture.includes(unavailable),`current-season investment panel should not rank unavailable T5 skill ${unavailable}`);
}

assert(pageErrors.length===0,`runtime errors: ${pageErrors.join('\n')}`);
console.log('build investment longevity smoke passed: current equipped rank priorities reflect verified T5 carryover without recommending unavailable T5 skills');
await browser.close();
