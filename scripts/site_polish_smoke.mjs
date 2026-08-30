import { chromium } from 'playwright';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const browser=await chromium.launch({headless:true});
const page=await browser.newPage({viewport:{width:1440,height:1000}});
const errors=[];
page.on('pageerror',e=>errors.push(String(e?.stack||e)));
await page.goto(pathToFileURL(path.resolve('index.html')).href,{waitUntil:'load'});
await page.waitForTimeout(300);
const assert=(v,m)=>{if(!v) throw new Error(m)};

await page.locator('.sectionSwitch button[data-section="builds"]').click();
await page.waitForTimeout(180);
await page.locator('#classTabs button[data-class="Conqueror"]').click();
await page.waitForTimeout(180);

const readable=await page.evaluate(()=>{
  const px=s=>parseFloat(getComputedStyle(document.querySelector(s)).fontSize);
  return {
    skillLabel:px('#buildContent .skillGroup>span'),
    skillChip:px('#buildContent .skillGroup b'),
    cardNote:px('#buildContent .buildCard header p'),
    fantoText:px('#buildContent .fantomonPick p'),
    quickStat:px('#buildContent .quickGearRow span')
  };
});
for(const [k,v] of Object.entries(readable)) assert(v>=10,`${k} is still too small at ${v}px`);

await page.locator('#classTabs button[data-class="Dominator"]').click();
await page.waitForTimeout(220);
assert(await page.locator('#buildContent .dominatorHeadingRow .dominatorModeTabs').count()===1,'Dominator toggle is not beside the Dominator title');
assert(await page.locator('#buildContent > .dominatorModeTabs').count()===0,'standalone Dominator toggle row returned');
const titleToggleGap=await page.locator('#buildContent .dominatorHeadingRow').evaluate(row=>{
  const title=row.querySelector('strong').getBoundingClientRect();
  const tabs=row.querySelector('.dominatorModeTabs').getBoundingClientRect();
  return {gap:tabs.left-title.right,dy:Math.abs((tabs.top+tabs.height/2)-(title.top+title.height/2))};
});
assert(titleToggleGap.gap>=0 && titleToggleGap.gap<24,`Dominator toggle gap is odd: ${titleToggleGap.gap}px`);
assert(titleToggleGap.dy<8,`Dominator toggle is not vertically aligned with the title: ${titleToggleGap.dy}px`);

const calcStart=Date.now();
await page.locator('.sectionSwitch button[data-section="calculator"]').click();
await page.waitForTimeout(100);
const calcYield=Date.now()-calcStart;
assert(calcYield<5000,`calculator blocked for ${calcYield}ms`);
const calcLabelSize=await page.locator('#calculatorSection .calcGrid label').first().evaluate(el=>parseFloat(getComputedStyle(el).fontSize));
assert(calcLabelSize>=10,`calculator label readability regressed to ${calcLabelSize}px`);

await page.setViewportSize({width:390,height:844});
await page.locator('.sectionSwitch button[data-section="builds"]').click();
await page.waitForTimeout(120);
const mobile=await page.evaluate(()=>({
  topDisplay:getComputedStyle(document.querySelector('.sectionSwitch')).display,
  topCols:getComputedStyle(document.querySelector('.sectionSwitch')).gridTemplateColumns,
  classDisplay:getComputedStyle(document.querySelector('.classTabs')).display,
  classCols:getComputedStyle(document.querySelector('.classTabs')).gridTemplateColumns,
  overflow:document.documentElement.scrollWidth-document.documentElement.clientWidth
}));
assert(mobile.topDisplay==='grid' && mobile.topCols.trim().split(/\s+/).length===2,`mobile top nav is not a clean 2-column grid: ${JSON.stringify(mobile)}`);
assert(mobile.classDisplay==='grid' && mobile.classCols.trim().split(/\s+/).length===2,`mobile class nav is not a clean 2-column grid: ${JSON.stringify(mobile)}`);
assert(mobile.overflow<=3,`mobile page has ${mobile.overflow}px horizontal overflow`);

if(errors.length) throw new Error('page runtime errors:\n'+errors.join('\n---\n'));
console.log(`site polish smoke passed: readable build text, inline Dominator toggle, 2x2 mobile navs, calculator yielded in ${calcYield}ms`);
await browser.close();
