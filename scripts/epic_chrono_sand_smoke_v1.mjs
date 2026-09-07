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

const materials=page.locator('#materialsDetails');
if(!(await materials.evaluate(el=>el.open))) await materials.locator(':scope > summary').click();
await page.waitForTimeout(60);

const basic=page.locator('#sandCurrent');
const rare=page.locator('#sandBlueCurrent');
const epic=page.locator('#sandEpicCurrent');
if(await epic.count()!==1) throw new Error('Epic Chrono Sand saved input missing');

// Epic must use the exact compact-number input plumbing as the other high-volume fields.
if(await epic.getAttribute('type')!=='text') throw new Error(`Epic Sand was not converted to compact text input; type=${await epic.getAttribute('type')}`);
if(await epic.getAttribute('data-compact-number')!=='1') throw new Error('Epic Sand is missing data-compact-number=1');
const title=await epic.getAttribute('title') || '';
if(!/k\/m\/b shorthand/i.test(title)) throw new Error(`Epic Sand compact-number hint missing: ${title}`);

// Establish a committed baseline: 100 Basic + 2 Rare = 110 Basic-equivalent.
await basic.fill('100');
await basic.press('Enter');
await rare.fill('2');
await rare.press('Enter');
await page.waitForTimeout(180);
let text=(await page.locator('#sandEquivalentNow').innerText()).replace(/,/g,'');
if(!text.includes('110')) throw new Error(`Baseline Sand conversion wrong; expected 110 basic-equivalent, got: ${text}`);

// Typing must NOT run the heavy calculator. The displayed result stays at the
// committed baseline until Enter/blur/change commits the edit.
await epic.click();
await epic.press('Control+A');
await epic.pressSequentially('1.3m');
await page.waitForTimeout(350);
if(await epic.inputValue()!=='1.3m') throw new Error(`Epic Sand changed while typing instead of preserving shorthand: ${await epic.inputValue()}`);
text=(await page.locator('#sandEquivalentNow').innerText()).replace(/,/g,'');
if(!text.includes('110')) throw new Error(`Epic Sand recalculated while typing; expected committed baseline 110, got: ${text}`);

// Enter is the normal commit path: blur -> change -> shorthand normalization -> recalc.
await epic.press('Enter');
await page.waitForTimeout(300);
if(await epic.inputValue()!=='1300000') throw new Error(`Epic Sand 1.3m shorthand did not normalize on Enter: ${await epic.inputValue()}`);
const afterEnter=(await page.locator('#sandEquivalentNow').innerText()).replace(/,/g,'');
if(afterEnter===text || !/32\.5M|32500110/i.test(afterEnter)) throw new Error(`Epic Sand did not recalculate after Enter commit: ${afterEnter}`);

// Leaving the field (Tab/blur) must commit too, while still not recalculating mid-edit.
await epic.click();
await epic.press('Control+A');
await epic.pressSequentially('2k');
await page.waitForTimeout(250);
const beforeBlur=(await page.locator('#sandEquivalentNow').innerText()).replace(/,/g,'');
if(beforeBlur!==afterEnter) throw new Error(`Epic Sand recalculated before blur: before=${afterEnter} during=${beforeBlur}`);
await epic.press('Tab');
await page.waitForTimeout(300);
if(await epic.inputValue()!=='2000') throw new Error(`Epic Sand 2k shorthand did not normalize on blur: ${await epic.inputValue()}`);
const afterBlur=(await page.locator('#sandEquivalentNow').innerText()).replace(/,/g,'');
if(afterBlur===beforeBlur) throw new Error(`Epic Sand did not recalculate after blur commit: ${afterBlur}`);

const label=await epic.locator('xpath=..').innerText();
if(!/Epic \(Purple\)/i.test(label)) throw new Error(`Epic/Purple label missing: ${label}`);
if(errors.length) throw new Error('Runtime errors:\n'+errors.join('\n---\n'));

console.log('Epic Chrono Sand smoke passed: k/m shorthand works, typing is deferred, Enter/blur commit and recalculate.');
await browser.close();
