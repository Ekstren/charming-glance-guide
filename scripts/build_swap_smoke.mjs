import assert from 'node:assert/strict';
import {chromium} from 'playwright';
import {pathToFileURL} from 'node:url';
import path from 'node:path';

const expected={
  Magister:{
    url:'https://www.prydwen.gg/sword-x-staff/guides/build-guide-magister',
    builds:['Wind AOE Build','ST Build','Fire AoE Build','PVP Build'],previous:'Destroyer',legacyCount:4
  },
  Prophet:{
    url:'https://www.prydwen.gg/sword-x-staff/guides/build-guide-prophet',
    builds:['Direct Single Target','Pure Erosion Remastered Edition','Direct AoE','Healing Build'],previous:'Dominator',legacyCount:3
  },
  Ravager:{
    url:'https://www.prydwen.gg/sword-x-staff/guides/build-guide-ravager',
    builds:['Stages and Dungeons Build','Dragon Build','PVP Build'],previous:'Conqueror',legacyCount:2
  },
  Templar:{
    url:'https://www.prydwen.gg/sword-x-staff/guides/build-guide-templar',
    builds:['Generic Dungeon/4vs4 Build','Water Templar','PvP Templar','Light Templar'],previous:'Guardian',legacyCount:4
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
assert(await page.locator('#classTabs button[data-class]').count()===classNames.length,'expected exactly four current T5 class tabs');
assert((await page.locator('#buildContent .sourceBuildNote').innerText()).includes('T5'),'Builds note must identify the current T5 sources');
assert(await page.locator('#buildContent .metaBuildTabs,#buildContent [data-meta-mode],#buildContent .buildRoleTabs').count()===0,'custom activity or role mapping controls must not render');

let checked=0;
for(const [cls,source] of Object.entries(expected)){
  await page.locator(`#classTabs button[data-class="${cls}"]`).click();
  await page.waitForFunction(name=>document.querySelector('#classTabs button.active')?.dataset.class===name,cls);
  const cards=page.locator('#buildContent .publishedBuildSource .sourceBuildCard');
  const names=(await cards.locator('h3').allTextContents()).map(value=>value.trim());
  assert(JSON.stringify(names)===JSON.stringify(source.builds),`${cls}: displayed source presets differ: ${names.join(' | ')}`);
  assert(await page.locator('#buildContent .publishedBuildSource a.buildSourceLink').getAttribute('href')===source.url,`${cls}: Prydwen guide link is wrong`);
  assert(await page.locator('#buildContent .sourceBuildNote').count()===1,`${cls}: source-use note missing`);
  assert(await page.locator('#buildContent .gearAdvicePanel .quickGearRow').count()===5,`${cls}: gear priorities missing`);
  assert(await page.locator('#buildContent .gearAdvicePanel .quickSubstats').count()===1,`${cls}: substat ranking missing`);
  assert(await page.locator('#buildContent .gearAdvicePanel .rollGuide').count()===1,`${cls}: roll guide missing`);
  assert(await page.locator('#buildContent .fantomonAdvicePanel .fantomonSuggestion').count()>=2,`${cls}: Fantomon recommendations missing`);
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
    assert(!/\bT4\b|2\s*[xv]\s*2/i.test(await cards.nth(index).innerText()),`${cls} ${names[index]}: previous-tier or nonexistent 2v2 content`);
    checked++;
  }
  const archive=page.locator('#buildContent .legacyBuildArchive');
  assert.equal(await archive.count(),1,`${cls}: previous-tier archive is missing`);
  assert.match(await archive.locator(':scope > summary').innerText(),new RegExp(`Season 2.*${source.previous}`));
  assert.equal(await archive.getAttribute('open'),null,`${cls}: previous-tier builds must start collapsed`);
  assert.equal(await archive.locator('.legacyBuildCard').count(),source.legacyCount,`${cls}: historical T4 presets were lost`);
  const communityCards=archive.locator('.communityBuildCard');
  assert.equal(await communityCards.count(),cls==='Magister'?1:0,`${cls}: historical community preset count`);
  if(cls==='Magister'){
    assert.match(await communityCards.first().locator('h3').textContent(),/Wind Tournament/);
    assert.ok((await communityCards.first().textContent()).includes('Wind’s Delight'),'historical community build entries missing');
  }
  assert.equal(await archive.locator('.otherSourceNotes').count(),1,`${cls}: historical source notes are missing`);
  const playerSources=page.locator('#buildContent .sourceBuildCollection > .otherSourceNotes:not(.legacyBuildArchive)');
  assert.equal(await playerSources.count(),1,`${cls}: current player-source directory missing`);
  assert.equal(await playerSources.locator(`a[href="https://www.sxscompanion.com/builds/t5/${cls.toLowerCase()}"]`).count(),1,`${cls}: current player loadout source`);
  assert.equal(await cards.locator('.buildCaveat').count(),source.builds.length,`${cls}: every current preset needs its published caveat`);
  if(['Prophet','Templar'].includes(cls)){
    const modes=cls==='Prophet'?['heals','dps']:['dps','tank'];
    for(const mode of modes){
      await page.locator(`#buildContent [data-build-mode="${mode}"]`).click();
      assert.equal(await page.locator('#buildContent .rollGuide').getAttribute('data-roll-sig'),`${cls}|${mode}`,`${cls}: roll guide follows selected gear profile`);
      assert.equal(await page.locator('#buildContent .quickGearRow').count(),5,`${cls}: all gear slots survive profile switching`);
      assert.equal(await page.locator('#buildContent .sourceBuildCard').count(),source.builds.length,`${cls}: gear profiles must not replace published presets`);
    }
  }
}

assert(errors.length===0,`browser errors: ${errors.join('\n')}`);
console.log(`source-build smoke passed: ${checked} Prydwen T5 preset cards, preserved gear/substats/rolls/Fantomons and historical T4 archive, no invented activity mappings`);
await browser.close();
