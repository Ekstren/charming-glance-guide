import { chromium } from 'playwright';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const browser = await chromium.launch({headless:true});
const page = await browser.newPage({viewport:{width:1440,height:1000}});
const pageErrors=[];
page.on('pageerror', err => pageErrors.push(String(err?.stack || err)));

const url = pathToFileURL(path.resolve('index.html')).href;
await page.goto(url,{waitUntil:'load'});
await page.waitForTimeout(350);

const assert=(cond,msg)=>{ if(!cond) throw new Error(msg); };
await page.locator('.sectionSwitch button[data-section="builds"]').click();
await page.locator('#classTabs button[data-class="Guardian"]').click();
await page.waitForFunction(()=>document.querySelector('#classTabs button.active')?.dataset.class==='Guardian' && !!document.querySelector('#buildContent .guardianModeTabs'));

async function assertVisibleGuardianBuild(label){
  const card=page.locator('#buildContent .buildGrid .buildCard:visible');
  assert(await card.count()===1, `${label}: expected one visible Guardian build, found ${await card.count()}`);
  const groups=card.locator('.skillGroup');
  let techniques=[];
  for(let i=0;i<await groups.count();i++){
    const g=groups.nth(i);
    const heading=(await g.locator(':scope > span').innerText()).trim().toLowerCase();
    if(heading.includes('technique')){
      techniques=(await g.locator(':scope > div > b').allTextContents()).map(x=>x.trim());
      break;
    }
  }
  assert(techniques.length===4, `${label}: expected four Techniques, got ${techniques.join(' | ')}`);
  assert(techniques.includes('Valor Surge'), `${label}: Valor Surge missing: ${techniques.join(' | ')}`);
}

let checked=0;
for(const role of ['tank','dps']){
  await page.locator(`#buildContent button[data-guardian-mode="${role}"]`).click();
  await page.waitForFunction(r=>localStorage.getItem('sxs-build-guardian-mode')===r,role);
  for(const mode of ['Dungeon','Crucible / Conquest','Fantasia Ascent','Arena']){
    await page.locator(`#buildContent .metaBuildTabs [data-meta-mode="${mode}"]`).click();
    await page.waitForTimeout(70);
    await assertVisibleGuardianBuild(`Guardian ${role} ${mode}`);
    checked++;
  }
  await page.locator('#buildContent .metaBuildTabs [data-meta-mode="Tournament"]').click();
  await page.waitForTimeout(70);
  for(const size of ['2v2','4v4']){
    await page.locator(`#buildContent .metaTournamentScenario [data-tournament-size="${size}"]`).click();
    await page.waitForTimeout(70);
    await assertVisibleGuardianBuild(`Guardian ${role} Tournament ${size}`);
    checked++;
  }
}

assert(checked===12, `expected to validate 12 Guardian builds, checked ${checked}`);
assert(pageErrors.length===0, `runtime errors: ${pageErrors.join('\n')}`);
console.log('guardian valor smoke passed: Valor Surge present in all 12 Tank/DPS Guardian builds');
await browser.close();
