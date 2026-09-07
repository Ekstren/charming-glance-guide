import { chromium } from 'playwright';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const browser = await chromium.launch({headless:true});
const page = await browser.newPage({viewport:{width:1200,height:900}});
const errors=[];
page.on('pageerror', e => errors.push(String(e?.stack || e)));
await page.goto(pathToFileURL(path.resolve('index.html')).href,{waitUntil:'load'});
await page.locator('.sectionSwitch button[data-section="calculator"]').click();
await page.waitForTimeout(100);

const basic=page.locator('#sandCurrent');
const rare=page.locator('#sandBlueCurrent');
const epic=page.locator('#sandEpicCurrent');
if(await epic.count()!==1) throw new Error('Epic Chrono Sand saved input missing');

await basic.fill('100');
await rare.fill('2');
await epic.fill('3');
for (const el of [basic,rare,epic]) await el.dispatchEvent('input');
await page.waitForTimeout(150);

const text=(await page.locator('#sandEquivalentNow').innerText()).replace(/,/g,'');
if(!text.includes('185')) throw new Error(`Epic Chrono Sand conversion wrong; expected 185 basic-equivalent, got: ${text}`);
const label=await epic.locator('xpath=..').innerText();
if(!/Epic \(Purple\)/i.test(label)) throw new Error(`Epic/Purple label missing: ${label}`);
if(errors.length) throw new Error('Runtime errors:\n'+errors.join('\n---\n'));

console.log('Epic Chrono Sand smoke passed: 100 + 2×5 + 3×25 = 185 basic-equivalent.');
await browser.close();
