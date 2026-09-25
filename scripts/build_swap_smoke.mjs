import assert from 'node:assert/strict';
import {chromium} from 'playwright';
import {pathToFileURL} from 'node:url';
import path from 'node:path';

const expected={
  Destroyer:{
    url:'https://www.prydwen.gg/sword-x-staff/guides/build-guide-destroyer',
    builds:['AOE Build','ST Build','Fire AoE Build','Elsa Build']
  },
  Dominator:{
    url:'https://www.prydwen.gg/sword-x-staff/guides/build-guide-dominator',
    builds:['Single Target','AoE','Healing Build']
  },
  Conqueror:{
    url:'https://www.prydwen.gg/sword-x-staff/guides/build-guide-conqueror',
    builds:['Generic Build for all Content','Dragon Build']
  },
  Guardian:{
    url:'https://www.prydwen.gg/sword-x-staff/guides/build-guide-guardian',
    builds:['Generic Dungeon Grid','Water Paladin','Support Knight','Secondary PvE build']
  }
};

const browser=await chromium.launch({headless:true});
const page=await browser.newPage({viewport:{width:1280,height:900}});
const errors=[];
page.on('pageerror',error=>errors.push(String(error?.stack||error)));
await page.goto(pathToFileURL(path.resolve('index.html')).href,{waitUntil:'load'});
await page.locator('.sectionSwitch button[data-section="builds"]').click();
await page.waitForFunction(()=>document.getElementById('buildsSection')?.dataset.guideReady==='true');

const classNames=Object.keys(expected);
assert(await page.locator('#classTabs button[data-class]').count()===classNames.length,'expected exactly four current T4 class tabs');
assert((await page.locator('#buildContent .sourceBuildNote').innerText()).includes('T4'),'Builds note must identify the current T4 sources');
assert(await page.locator('#buildContent .metaBuildTabs,#buildContent [data-meta-mode],#buildContent .buildRoleTabs').count()===0,'custom activity or role mapping controls must not render');

let checked=0;
for(const [cls,source] of Object.entries(expected)){
  await page.locator(`#classTabs button[data-class="${cls}"]`).click();
  await page.waitForFunction(name=>document.querySelector('#classTabs button.active')?.dataset.class===name,cls);
  const cards=page.locator('#buildContent .sourceBuildCard');
  const names=(await cards.locator('h3').allTextContents()).map(value=>value.trim());
  assert(JSON.stringify(names)===JSON.stringify(source.builds),`${cls}: displayed source presets differ: ${names.join(' | ')}`);
  assert(await page.locator('#buildContent a.buildSourceLink').getAttribute('href')===source.url,`${cls}: Prydwen guide link is wrong`);
  assert(await page.locator('#buildContent .sourceBuildNote').count()===1,`${cls}: source-use note missing`);
  for(let index=0;index<await cards.count();index++){
    const groups=cards.nth(index).locator('.skillGroup');
    assert(await groups.count()===2,`${cls} ${names[index]}: expected Techniques and Charms groups`);
    for(let group=0;group<2;group++){
      const current=groups.nth(group);
      const label=(await current.locator(':scope > span').innerText()).trim();
      const items=await current.locator(':scope > div > b').count();
      assert(/^(techniques|charms)$/.test(label.toLowerCase()),`${cls} ${names[index]}: unexpected group label ${label}`);
      assert(items===4,`${cls} ${names[index]} ${label}: expected four source entries, found ${items}`);
    }
    assert(!/\bT5\b|2\s*[xv]\s*2/i.test(await cards.nth(index).innerText()),`${cls} ${names[index]}: out-of-scope tier or nonexistent 2v2 content`);
    checked++;
  }
}

assert(errors.length===0,`browser errors: ${errors.join('\n')}`);
console.log(`source-build smoke passed: ${checked} Prydwen T4 preset cards, exact source names and links, four Techniques/Charms each, no invented activity mappings`);
await browser.close();
