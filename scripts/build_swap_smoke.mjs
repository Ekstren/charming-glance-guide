import { chromium } from 'playwright';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const browser=await chromium.launch({headless:true});
const page=await browser.newPage({viewport:{width:1440,height:1000}});
const pageErrors=[];
page.on('pageerror',err=>pageErrors.push(String(err?.stack||err)));
await page.goto(pathToFileURL(path.resolve('index.html')).href,{waitUntil:'load'});
await page.waitForTimeout(350);

const assert=(cond,msg)=>{if(!cond) throw new Error(msg)};
const waitBuild=async cls=>{
  await page.locator('.sectionSwitch button[data-section="builds"]').click();
  await page.locator(`#classTabs button[data-class="${cls}"]`).click();
  await page.waitForFunction(name=>document.querySelector('#classTabs button.active')?.dataset.class===name,cls);
  await page.waitForTimeout(70);
};

async function assertVisibleBuild(label){
  const card=page.locator('#buildContent .buildGrid .buildCard:visible');
  assert(await card.count()===1,`${label}: expected one visible build, found ${await card.count()}`);
  const groups=card.locator('.skillGroup');
  let techniques=[],charms=[];
  for(let i=0;i<await groups.count();i++){
    const g=groups.nth(i);
    const heading=(await g.locator(':scope > span').innerText()).trim().toLowerCase();
    const names=(await g.locator(':scope > div > b').allTextContents()).map(x=>x.trim());
    if(heading.includes('technique')) techniques=names;
    if(heading.includes('charm')) charms=names;
  }
  assert(techniques.length===4,`${label}: expected four Techniques, got ${techniques.join(' | ')}`);
  assert(charms.length===4,`${label}: expected four Charms, got ${charms.join(' | ')}`);
  const swaps=card.locator('.buildSwapRows p');
  for(let i=0;i<await swaps.count();i++){
    const row=swaps.nth(i);
    const kind=(await row.locator(':scope > strong').innerText()).trim().toLowerCase();
    const names=(await row.locator('.swapNames').innerText()).split('→').map(x=>x.trim());
    assert(names.length===2,`${label}: malformed swap row: ${await row.innerText()}`);
    const [from,to]=names;
    const equipped=kind.includes('technique')?techniques:charms;
    assert(equipped.includes(from),`${label}: ${kind} source "${from}" is not equipped; equipped: ${equipped.join(' | ')}`);
    assert(!equipped.includes(to),`${label}: ${kind} target "${to}" is already equipped; equipped: ${equipped.join(' | ')}`);
  }
}

const activities=['Dungeon','Crucible / Conquest','Arena'];
let checked=0;
for(const cls of ['Conqueror','Guardian','Destroyer','Dominator']){
  await waitBuild(cls);
  const modes=await page.locator('#buildContent .metaBuildTabs [data-meta-mode]').evaluateAll(xs=>xs.map(x=>x.dataset.metaMode));
  assert(JSON.stringify(modes)===JSON.stringify(['Dungeon','Crucible / Conquest','Arena','Tournament']),`${cls}: activity tabs wrong: ${modes.join(' | ')}`);
  assert(await page.locator('#buildContent .buildCard[data-role^="Fantasia Ascent"]').count()===0,`${cls}: Fantasia Ascent build data still rendered`);
  const roles=cls==='Guardian'?['tank','dps']:(cls==='Dominator'?['dps','heals']:[null]);
  for(const role of roles){
    if(role){
      const attr=cls==='Guardian'?'guardian':'dominator';
      await page.locator(`#buildContent button[data-${attr}-mode="${role}"]`).click();
      await page.waitForTimeout(60);
    }
    for(const mode of activities){
      await page.locator(`#buildContent .metaBuildTabs [data-meta-mode="${mode}"]`).click();
      await page.waitForTimeout(60);
      await assertVisibleBuild(`${cls}${role?` ${role}`:''} ${mode}`);
      checked++;
    }
    await page.locator('#buildContent .metaBuildTabs [data-meta-mode="Tournament"]').click();
    await page.waitForTimeout(60);
    for(const size of ['2v2','4v4']){
      await page.locator(`#buildContent .metaTournamentScenario [data-tournament-size="${size}"]`).click();
      await page.waitForTimeout(60);
      await assertVisibleBuild(`${cls}${role?` ${role}`:''} Tournament ${size}`);
      checked++;
    }
  }
}
assert(checked===30,`expected 30 current S2 build variants, checked ${checked}`);
assert(pageErrors.length===0,`runtime errors: ${pageErrors.join('\n')}`);
console.log('build swap smoke passed: all 30 current S2 build variants use equipped swap sources and unequipped targets');
await browser.close();
