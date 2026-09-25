import {waitForCalculatorReady} from './calculator_ready.mjs';
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
    return active===name && !!host?.querySelector('.sourceBuildCollection') && !!host?.querySelector('.sourceBuildCard');
  }, cls, {timeout:3000});
  await page.waitForTimeout(80);
};
const buildTitles = async () => page.locator('#buildContent .sourceBuildCard h3').allTextContents();
const normalize = s => String(s||'').toLowerCase().replace(/[’']/g,"'").replace(/\s+/g,' ').trim();

const filterCount = await page.locator('#timelineFilters button').count();
const timelineCount = await page.locator('#timeline .dayGroup').count();
assert(filterCount > 0, 'timeline filters were not initialized');
assert(timelineCount > 0, 'timeline entries were not rendered');

// Top-level tabs must be five equal direct flex items. The old Builds wrapper made
// that label look off-center and gave it different sizing behavior.
const navButtons = page.locator('.sectionSwitch > button[data-section]');
assert(await navButtons.count() === 5, 'top nav does not contain five direct section buttons');
const widths = await navButtons.evaluateAll(btns => btns.map(b => b.getBoundingClientRect().width));
assert(Math.max(...widths)-Math.min(...widths) < 2, `top nav buttons are not equal width: ${widths.join(', ')}`);

await page.locator('.sectionSwitch button[data-section="builds"]').click();
await page.waitForTimeout(60);
assert(!(await page.locator('#buildsSection').evaluate(el => el.hidden)), 'Builds tab did not reveal #buildsSection');
assert(await page.locator('#classTabs button[data-class]').count() === 4, 'current T4 class tabs were not rendered');
assert((await page.locator('#buildContent .sourceBuildNote').innerText()).includes('T4'), 'Builds page does not identify the current tier');

const buildSources = {
  Destroyer: 'build-guide-destroyer',
  Dominator: 'build-guide-dominator',
  Conqueror: 'build-guide-conqueror',
  Guardian: 'build-guide-guardian'
};
for (const [cls, source] of Object.entries(buildSources)) {
  await waitBuild(cls);
  assert(await page.locator('#buildContent .sourceBuildCard').count() > 0, cls + ' has no source build cards');
  assert((await page.locator('#buildContent .publishedBuildSource .buildSourceLink').getAttribute('href')).endsWith(source), cls + ' source link is incorrect');
  assert(await page.locator('#buildContent .metaBuildTabs,#buildContent .dominatorModeTabs,#buildContent [data-guardian-mode]').count() === 0, cls + ' still has custom activity or role selectors');
  assert((await buildTitles()).every(title => !/2\s*[xv]\s*2/i.test(title)), cls + ' contains a nonexistent 2v2 build');
}
// Other top-level navigation must remain usable. Record how long the calculator tab
// takes to yield the event loop back; this catches long-season reset regressions.
await page.locator('.sectionSwitch button[data-section="companions"]').click();
await page.waitForTimeout(30);
assert(!(await page.locator('#companionsSection').evaluate(el => el.hidden)), 'Companions tab did not reveal #companionsSection');

const calcStarted = Date.now();
await page.locator('.sectionSwitch button[data-section="calculator"]').click();
await waitForCalculatorReady(page);
await page.waitForTimeout(80);
const calcYieldMs = Date.now()-calcStarted;
assert(!(await page.locator('#calculatorSection').evaluate(el => el.hidden)), 'Calculator tab did not reveal #calculatorSection');
assert(calcYieldMs < 5000, `calculator blocked the browser for ${calcYieldMs}ms`);
const targetTiming=page.locator('#targetTiming');
assert(await targetTiming.count()===1, 'target timing strip missing');
const targetTimingState=await targetTiming.evaluate(el=>({text:el.innerText,overflow:Math.max(0,el.scrollWidth-el.clientWidth)}));
assert(/Projected target/i.test(targetTimingState.text) && /Season left after target/i.test(targetTimingState.text), `target timing labels missing: ${targetTimingState.text}`);
assert(targetTimingState.overflow<=1, `target timing strip overflows by ${targetTimingState.overflow}px`);
assert((await page.locator('#targetReachedDate').innerText()).trim().length>0, 'target timing date did not render');

// Pixel geometry regression: projected level must exactly match Bed EXP.
const projectionGeometry = await page.evaluate(()=>{
  const bed=document.getElementById('bedExp')?.getBoundingClientRect();
  const projected=document.getElementById('projectedCharacter')?.getBoundingClientRect();
  return bed&&projected?{bed:{top:bed.top,height:bed.height},projected:{top:projected.top,height:projected.height}}:null;
});
assert(projectionGeometry, 'projection/Bed EXP geometry unavailable');
const projectedFieldKind = await page.evaluate(()=>{
  const el=document.getElementById('projectedCharacter');
  return el?{tag:el.tagName,readOnly:!!el.readOnly}:null;
});
assert(projectedFieldKind?.tag==='INPUT' && projectedFieldKind.readOnly,
  `projected season-end field must reuse the native readonly input geometry: ${JSON.stringify(projectedFieldKind)}`);
assert(Math.abs(projectionGeometry.bed.height-projectionGeometry.projected.height)<0.51,
  `projected field height mismatch: Bed ${projectionGeometry.bed.height}px vs projected ${projectionGeometry.projected.height}px`);
assert(Math.abs(projectionGeometry.bed.top-projectionGeometry.projected.top)<0.51,
  `projected field top mismatch: Bed ${projectionGeometry.bed.top}px vs projected ${projectionGeometry.projected.top}px`);
const projectionColors = await page.evaluate(()=>{
  const bed=getComputedStyle(document.getElementById('bedExp'));
  const projected=getComputedStyle(document.getElementById('projectedCharacter'));
  return {bedBg:bed.backgroundColor,projectedBg:projected.backgroundColor,bedBorder:bed.borderTopColor,projectedBorder:projected.borderTopColor};
});
assert(projectionColors.projectedBg!==projectionColors.bedBg,
  `projected field should keep its distinct read-only tint: ${JSON.stringify(projectionColors)}`);

await page.locator('.sectionSwitch button[data-section="timeline"]').click({timeout:5000});
await page.waitForTimeout(30);
assert(!(await page.locator('#timelineSection').evaluate(el => el.hidden)), 'Timeline tab did not reveal #timelineSection after calculator');

await page.setViewportSize({width:390,height:844});
await page.locator('.sectionSwitch button[data-section="builds"]').click();
for (const cls of Object.keys(buildSources)) {
  await waitBuild(cls);
  const badCards = await page.locator('#buildContent .sourceBuildCard,#buildContent .sourceBuildCard h3,#buildContent .sourceBuildCard .skillGroup b').evaluateAll(elements=>elements.filter(el=>{
    const r=el.getBoundingClientRect();
    return r.height&&(r.left<0||r.right>innerWidth+1||el.scrollWidth>el.clientWidth+2);
  }).map(el=>el.textContent.trim().slice(0,60)));
  assert(badCards.length===0, 'mobile ' + cls + ' cards overflow or clip: ' + badCards.join(' | '));
}
const mobileNavTargets=await page.locator('#classTabs button[data-class]').evaluateAll(xs=>xs.map(x=>x.getBoundingClientRect().height));
assert(mobileNavTargets.every(height=>height>=40), 'mobile class tabs have undersized touch targets: ' + mobileNavTargets.join(','));
const overflow=await page.evaluate(()=>document.documentElement.scrollWidth-document.documentElement.clientWidth);
assert(overflow<=3, 'mobile page has ' + overflow + 'px horizontal overflow');
// Calculator jumps scroll/focus without leaving fragments or extra history entries.
await page.goto(url+'?navigation-check=1#calcResults');
assert(await page.evaluate(()=>location.hash===''&&location.search==='?navigation-check=1'), 'stale calculator fragment was not cleaned');
await page.locator('[data-section="calculator"]').click();
await waitForCalculatorReady(page);
const historyBefore=await page.evaluate(()=>history.length);
for(const target of ['calcResults','characterDetails']){
  await page.locator(`.calculatorJumpNav a[href="#${target}"]`).click();
  assert(await page.evaluate(id=>document.activeElement.id===id&&location.hash==='',target), 'calculator jump changed URL or failed to move focus');
  assert(await page.evaluate(()=>history.length)===historyBefore, 'calculator jump added browser history');
}

if(pageErrors.length){
  throw new Error('page runtime errors:\n' + pageErrors.join('\n---\n'));
}

console.log(`runtime smoke passed: ${filterCount} filters, ${timelineCount} timeline groups, equal nav ${widths.map(x=>x.toFixed(1)).join('/')}, source-linked T4 Builds + mobile layout, calculator yielded in ${calcYieldMs}ms`);
await browser.close();
