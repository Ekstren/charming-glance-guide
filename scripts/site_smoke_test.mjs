import { chromium } from 'playwright';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const browser = await chromium.launch({headless:true});
const page = await browser.newPage();
const pageErrors=[];
page.on('pageerror', err => pageErrors.push(String(err?.stack || err)));

const url = pathToFileURL(path.resolve('index.html')).href;
await page.goto(url, {waitUntil:'load'});
await page.waitForTimeout(300);

const assert = (cond,msg)=>{ if(!cond) throw new Error(msg); };

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

// Builds navigation + Dominator DPS/Heals role switch.
await page.locator('.sectionSwitch button[data-section="builds"]').click();
await page.waitForTimeout(40);
assert(!(await page.locator('#buildsSection').evaluate(el => el.hidden)), 'Builds tab did not reveal #buildsSection');
assert(await page.locator('#classTabs button[data-class]').count() === 4, 'S2 build class tabs were not rendered');
await page.locator('#classTabs button[data-class="Dominator"]').click();
await page.waitForTimeout(40);
assert(await page.locator('#buildContent .dominatorModeTabs button').count() === 2, 'Dominator DPS/Heals tabs missing');
const visibleTitles = async () => page.locator('#buildContent .buildCard:visible h3').allTextContents();
let titles = await visibleTitles();
assert(titles.some(x=>/Single Target/i.test(x)) && titles.some(x=>/AoE \/ Erosion/i.test(x)), `Dominator DPS cards not visible: ${titles.join(' | ')}`);
await page.locator('#buildContent button[data-dominator-mode="heals"]').click();
await page.waitForTimeout(20);
titles = await visibleTitles();
assert(titles.some(x=>/Healing \/ Group/i.test(x)) && titles.some(x=>/Carry Support/i.test(x)), `Dominator healer cards not visible: ${titles.join(' | ')}`);
assert(!titles.some(x=>/Single Target|AoE \/ Erosion/i.test(x)), 'Dominator DPS cards remained visible in Heals mode');

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

if(pageErrors.length){
  throw new Error('page runtime errors:\n' + pageErrors.join('\n---\n'));
}

console.log(`runtime smoke passed: ${filterCount} filters, ${timelineCount} timeline groups, equal nav ${widths.map(x=>x.toFixed(1)).join('/')}, Dominator DPS+Heals, calculator yielded in ${calcYieldMs}ms`);
await browser.close();
