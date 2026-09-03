import { chromium } from 'playwright';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const browser = await chromium.launch({headless:true});
const page = await browser.newPage({viewport:{width:1440,height:1000}});
const errors=[];
page.on('pageerror',err=>errors.push(String(err?.stack||err)));

const assert=(cond,msg)=>{if(!cond) throw new Error(msg)};
const url=pathToFileURL(path.resolve('index.html')).href;
await page.goto(url,{waitUntil:'load'});
await page.locator('.sectionSwitch button[data-section="builds"]').click();
await page.locator('#classTabs button[data-class="Dominator"]').click();
await page.waitForFunction(()=>!!document.querySelector('#buildContent .buildHeroRoll > .rollGuide'),null,{timeout:4000});
await page.waitForTimeout(120);

let roll=page.locator('#buildContent .buildHeroRoll > .rollGuide').first();
let summary=roll.locator(':scope > summary');
assert(await roll.evaluate(el=>el.open),'desktop Roll Guide is not expanded');
const desktopPointer=await summary.evaluate(el=>getComputedStyle(el).pointerEvents);
assert(desktopPointer==='none',`desktop Roll Guide summary is still interactive (${desktopPointer})`);
const desktopAfter=await summary.evaluate(el=>getComputedStyle(el,'::after').display);
assert(desktopAfter==='none',`desktop Roll Guide still shows collapse affordance (${desktopAfter})`);

// Crossing into mobile should deliberately reset the guide to its default collapsed state.
await page.setViewportSize({width:390,height:844});
await page.waitForTimeout(160);
roll=page.locator('#buildContent .buildHeroRoll > .rollGuide').first();
summary=roll.locator(':scope > summary');
assert(!(await roll.evaluate(el=>el.open)),'mobile Roll Guide did not default to collapsed');
assert(await summary.evaluate(el=>getComputedStyle(el).pointerEvents)==='auto','mobile Roll Guide summary is not interactive');

await summary.click();
await page.waitForTimeout(50);
assert(await roll.evaluate(el=>el.open),'mobile Roll Guide did not expand when tapped');
assert(await roll.locator('.rollGuideBody').isVisible(),'mobile Roll Guide body is not visible after expansion');
let overflow=await page.evaluate(()=>document.documentElement.scrollWidth-document.documentElement.clientWidth);
assert(overflow<=3,`mobile expanded Roll Guide causes ${overflow}px horizontal overflow`);

await summary.click();
await page.waitForTimeout(30);
assert(!(await roll.evaluate(el=>el.open)),'mobile Roll Guide did not collapse when tapped again');

// A class change on mobile should create the next guide collapsed by default too.
await page.locator('#classTabs button[data-class="Conqueror"]').click();
await page.waitForFunction(()=>document.querySelector('#buildContent .buildHeroRoll > .rollGuide')?.dataset.rollSig?.startsWith('Conqueror|'),null,{timeout:4000});
await page.waitForTimeout(80);
roll=page.locator('#buildContent .buildHeroRoll > .rollGuide').first();
assert(!(await roll.evaluate(el=>el.open)),'new mobile class Roll Guide did not start collapsed');
overflow=await page.evaluate(()=>document.documentElement.scrollWidth-document.documentElement.clientWidth);
assert(overflow<=3,`mobile collapsed Roll Guide causes ${overflow}px horizontal overflow`);

if(errors.length) throw new Error('page runtime errors:\n'+errors.join('\n---\n'));
console.log('roll responsive smoke passed: desktop fixed-open; mobile collapsed-by-default, expandable, no overflow');
await browser.close();
