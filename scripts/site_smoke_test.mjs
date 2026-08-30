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

for (const [section,id] of [
  ['builds','buildsSection'],
  ['companions','companionsSection'],
  ['calculator','calculatorSection'],
  ['timeline','timelineSection'],
]) {
  await page.locator(`.sectionSwitch button[data-section="${section}"]`).click();
  await page.waitForTimeout(section==='calculator' ? 150 : 30);
  const hidden = await page.locator(`#${id}`).evaluate(el => el.hidden);
  assert(!hidden, `${section} tab did not reveal #${id}`);
}

if(pageErrors.length){
  throw new Error('page runtime errors:\n' + pageErrors.join('\n---\n'));
}

console.log(`runtime smoke passed: ${filterCount} filters, ${timelineCount} timeline groups, all tabs navigable`);
await browser.close();
