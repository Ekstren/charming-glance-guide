import { chromium } from 'playwright';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const browser = await chromium.launch({headless:true});
const page = await browser.newPage({viewport:{width:1440,height:1000}});
const pageErrors=[];
page.on('pageerror', err => pageErrors.push(String(err?.stack || err)));

const url = pathToFileURL(path.resolve('index.html')).href;
await page.goto(url, {waitUntil:'load'});
await page.waitForTimeout(350);

const assert = (cond,msg)=>{ if(!cond) throw new Error(msg); };
const waitBuild = async cls => {
  await page.locator(`#classTabs button[data-class="${cls}"]`).click();
  await page.waitForFunction(name => {
    const host=document.getElementById('buildContent');
    const active=document.querySelector('#classTabs button.active')?.dataset.class;
    return active===name && !!host?.querySelector('.buildQuickStats') && !!host?.querySelector(':scope > .priorityPair');
  }, cls, {timeout:3000});
  await page.waitForTimeout(80);
};
const buildTitles = async () => page.locator('#buildContent .buildGrid .buildCard:visible h3').allTextContents();
const normalize = s => String(s||'').toLowerCase().replace(/[’']/g,"'").replace(/\s+/g,' ').trim();

const filterCount = await page.locator('#timelineFilters button').count();
const timelineCount = await page.locator('#timeline .dayGroup').count();
assert(filterCount > 0, 'timeline filters were not initialized');
assert(timelineCount > 0, 'timeline entries were not rendered');

// Top-level tabs must be four equal direct flex items. The old Builds wrapper made
// that label look off-center and gave it different sizing behavior.
const navButtons = page.locator('.sectionSwitch > button[data-section]');
assert(await navButtons.count() === 4, 'top nav does not contain four direct section buttons');
const widths = await navButtons.evaluateAll(btns => btns.map(b => b.getBoundingClientRect().width));
assert(Math.max(...widths)-Math.min(...widths) < 2, `top nav buttons are not equal width: ${widths.join(', ')}`);

// The maintained Builds presentation is deliberately rich: per-slot stat priorities,
// full substat priority, Techniques on the LEFT, Charms on the RIGHT, Arena/Tournament
// loadouts, and Main+Alt Fantomon cards. Lock all of that in so it cannot silently
// regress to the older stacked/generic build template again.
await page.locator('.sectionSwitch button[data-section="builds"]').click();
await page.waitForTimeout(60);
assert(!(await page.locator('#buildsSection').evaluate(el => el.hidden)), 'Builds tab did not reveal #buildsSection');
assert(await page.locator('#classTabs button[data-class]').count() === 4, 'S2 build class tabs were not rendered');

for (const cls of ['Conqueror','Guardian','Destroyer']) {
  await waitBuild(cls);
  assert(await page.locator('#buildContent .quickGearRow').count() === 5, `${cls} does not show five slot-specific stat priorities`);
  const substats=await page.locator('#buildContent .quickSubstats').innerText();
  assert(/substats/i.test(substats) && substats.replace(/substats/i,'').trim().length>8, `${cls} substat priority is missing`);

  const pair=page.locator('#buildContent > .priorityPair').first();
  assert(await pair.locator(':scope > .priorityPanel').count()===2, `${cls} does not have a two-column Technique/Charm recommendation pair`);
  const panelBoxes=await pair.locator(':scope > .priorityPanel').evaluateAll(xs=>xs.map(x=>{const r=x.getBoundingClientRect();return {x:r.x,y:r.y,w:r.width};}));
  assert(panelBoxes[0].x < panelBoxes[1].x, `${cls} desktop investment panels are not Technique-left / Charm-right`);
  const panelKinds=await pair.locator('.priorityIntro span').allTextContents();
  assert(/technique/i.test(panelKinds[0]||''), `${cls} left investment panel is not Techniques: ${panelKinds.join(' | ')}`);
  assert(/charm/i.test(panelKinds[1]||''), `${cls} right investment panel is not Charms: ${panelKinds.join(' | ')}`);

  const titles=await buildTitles();
  assert(titles.some(x=>/^Arena/i.test(x)), `${cls} Arena loadout was lost: ${titles.join(' | ')}`);
  assert(titles.some(x=>/^Tournament/i.test(x)), `${cls} Tournament loadout was lost: ${titles.join(' | ')}`);
  const visibleCards=page.locator('#buildContent .buildGrid .buildCard:visible');
  assert(await visibleCards.count()>=4, `${cls} rich loadout set was reduced unexpectedly`);
  assert(await visibleCards.locator('.fantomonPair').count()===await visibleCards.count(), `${cls} does not show a Fantomon pair on every visible loadout`);
  const badFanto=await visibleCards.locator('.fantomonPair').evaluateAll(xs=>xs.filter(x=>x.querySelectorAll('.fantomonPick').length!==2).length);
  assert(badFanto===0, `${cls} has a loadout without exactly Main + Alt Fantomons`);

  // Recommendations must come from Techniques/Charms actually equipped somewhere in
  // the displayed loadouts, not from unrelated wishlist/swap-only pieces.
  const equipped=await visibleCards.evaluateAll(cards=>{
    const out={techniques:[],charms:[]};
    cards.forEach(card=>card.querySelectorAll('.skillGroup').forEach(group=>{
      const label=(group.querySelector(':scope > span')?.textContent||'').toLowerCase();
      const vals=[...group.querySelectorAll(':scope > div > b')].map(x=>x.textContent.trim());
      if(label.includes('technique')) out.techniques.push(...vals);
      if(label.includes('charm')) out.charms.push(...vals);
    }));
    return out;
  });
  const priorities=await pair.locator(':scope > .priorityPanel').evaluateAll(panels=>panels.map(p=>[...p.querySelectorAll('.priorityList strong')].map(x=>x.textContent.trim())));
  for (const [index,key] of [[0,'techniques'],[1,'charms']]) {
    const used=new Set(equipped[key].map(normalize));
    for (const recommendation of priorities[index]) {
      const pieces=recommendation.split('/').map(x=>normalize(x)).filter(Boolean);
      for (const piece of pieces) assert(used.has(piece), `${cls} ${key} recommendation "${piece}" is not actually equipped in a displayed loadout`);
    }
  }
}

// Dominator keeps its DPS / Heals switch, role-specific slot stats, and a separate
// Technique-left / Charm-right recommendation pair for each role. Arena/Tournament
// remain visible reference cards in BOTH modes; only role-specific PvE cards filter.
await waitBuild('Dominator');
assert(await page.locator('#buildContent .dominatorModeTabs button').count() === 2, 'Dominator DPS/Heals tabs missing');
let titles=await buildTitles();
assert(titles.some(x=>/Single Target DPS/i.test(x)) && titles.some(x=>/AoE DPS/i.test(x)), `Dominator DPS cards not visible: ${titles.join(' | ')}`);
assert(titles.some(x=>/^Arena/i.test(x)) && titles.some(x=>/^Tournament/i.test(x)), `Dominator PvP cards missing in DPS mode: ${titles.join(' | ')}`);
assert(!titles.some(x=>/^Healing/i.test(x)), 'Dominator Healing card visible in DPS mode');
let domPair=page.locator('#buildContent > .priorityPair[data-dominator-role="dps"]:visible');
assert(await domPair.count()===1 && await domPair.locator(':scope > .priorityPanel').count()===2, 'Dominator DPS Technique/Charm pair missing');
let domKinds=await domPair.locator('.priorityIntro span').allTextContents();
assert(/technique/i.test(domKinds[0]||'') && /charm/i.test(domKinds[1]||''), `Dominator DPS pair order wrong: ${domKinds.join(' | ')}`);
const dpsStatText=await page.locator('#buildContent .buildQuickStats').innerText();
assert(/Dark DPS|Effect Hit Rate/i.test(dpsStatText), 'Dominator DPS stat profile missing');

await page.locator('#buildContent button[data-dominator-mode="heals"]').click();
await page.waitForFunction(()=>[...document.querySelectorAll('#buildContent .buildGrid .buildCard')].filter(x=>!x.hidden&&getComputedStyle(x).display!=='none').some(x=>/^Healing/i.test(x.querySelector('h3')?.textContent||'')),null,{timeout:3000});
await page.waitForTimeout(80);
titles=await buildTitles();
assert(titles.some(x=>/^Healing/i.test(x)), `Dominator healer card not visible: ${titles.join(' | ')}`);
assert(titles.some(x=>/^Arena/i.test(x)) && titles.some(x=>/^Tournament/i.test(x)), `Dominator PvP reference cards disappeared in Heals mode: ${titles.join(' | ')}`);
assert(!titles.some(x=>/Single Target DPS|AoE DPS/i.test(x)), `Dominator DPS PvE cards remained visible in Heals mode: ${titles.join(' | ')}`);
domPair=page.locator('#buildContent > .priorityPair[data-dominator-role="heals"]:visible');
assert(await domPair.count()===1 && await domPair.locator(':scope > .priorityPanel').count()===2, 'Dominator Heals Technique/Charm pair missing');
domKinds=await domPair.locator('.priorityIntro span').allTextContents();
assert(/technique/i.test(domKinds[0]||'') && /charm/i.test(domKinds[1]||''), `Dominator Heals pair order wrong: ${domKinds.join(' | ')}`);
const healStatText=await page.locator('#buildContent .buildQuickStats').innerText();
assert(/Healing\/support|Healing Boost/i.test(healStatText), 'Dominator Heals stat profile did not switch');

// Other top-level navigation must remain usable. Record how long the calculator tab
// takes to yield the event loop back; this catches long-season reset regressions.
await page.locator('.sectionSwitch button[data-section="companions"]').click();
await page.waitForTimeout(30);
assert(!(await page.locator('#companionsSection').evaluate(el => el.hidden)), 'Companions tab did not reveal #companionsSection');

const calcStarted = Date.now();
await page.locator('.sectionSwitch button[data-section="calculator"]').click();
await page.waitForTimeout(80);
const calcYieldMs = Date.now()-calcStarted;
assert(!(await page.locator('#calculatorSection').evaluate(el => el.hidden)), 'Calculator tab did not reveal #calculatorSection');
assert(calcYieldMs < 5000, `calculator blocked the browser for ${calcYieldMs}ms`);

await page.locator('.sectionSwitch button[data-section="timeline"]').click({timeout:5000});
await page.waitForTimeout(30);
assert(!(await page.locator('#timelineSection').evaluate(el => el.hidden)), 'Timeline tab did not reveal #timelineSection after calculator');

// Phone regression check: rich desktop data must stack rather than overflow.
await page.setViewportSize({width:390,height:844});
await page.locator('.sectionSwitch button[data-section="builds"]').click();
await waitBuild('Conqueror');
const mobilePair=page.locator('#buildContent > .priorityPair').first();
const mobileBoxes=await mobilePair.locator(':scope > .priorityPanel').evaluateAll(xs=>xs.map(x=>{const r=x.getBoundingClientRect();return {x:r.x,y:r.y,w:r.width};}));
assert(mobileBoxes[1].y > mobileBoxes[0].y, 'mobile Technique/Charm panels did not stack vertically');
assert(Math.abs(mobileBoxes[1].x-mobileBoxes[0].x)<3, 'mobile Technique/Charm panels do not align after stacking');
const quickCols=await page.locator('#buildContent .quickGearGrid').evaluate(el=>getComputedStyle(el).gridTemplateColumns);
assert(!quickCols.includes(' '), `mobile stat priorities did not collapse to one column: ${quickCols}`);
const overflow=await page.evaluate(()=>document.documentElement.scrollWidth-document.documentElement.clientWidth);
assert(overflow<=3, `mobile page has ${overflow}px horizontal overflow`);

if(pageErrors.length){
  throw new Error('page runtime errors:\n' + pageErrors.join('\n---\n'));
}

console.log(`runtime smoke passed: ${filterCount} filters, ${timelineCount} timeline groups, equal nav ${widths.map(x=>x.toFixed(1)).join('/')}, rich S2 Builds + slot stats + Technique/Charm pair + Fantomon pairs + Dominator roles/PvP refs + mobile stack, calculator yielded in ${calcYieldMs}ms`);
await browser.close();
