import { chromium } from 'playwright';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const browser = await chromium.launch({headless:true});
const page = await browser.newPage({viewport:{width:1600,height:1000}});
const errors=[];
page.on('pageerror', e => errors.push(String(e?.stack || e)));
await page.goto(pathToFileURL(path.resolve('index.html')).href,{waitUntil:'load'});
await page.locator('.sectionSwitch button[data-section="calculator"]').click();
await page.waitForTimeout(150);

const result = await page.evaluate(()=>{
  const sand=document.querySelector('.sandResourceFields');
  const treats=document.querySelector('.treatResourceFields');
  if(!sand||!treats) return {missing:true};
  const sw=[...sand.querySelectorAll('label')].slice(0,4).map(el=>el.getBoundingClientRect().width);
  const tw=[...treats.querySelectorAll('label')].slice(0,4).map(el=>el.getBoundingClientRect().width);
  return {
    missing:false,
    sandTemplate:getComputedStyle(sand).gridTemplateColumns,
    treatTemplate:getComputedStyle(treats).gridTemplateColumns,
    sw,tw
  };
});
if(result.missing) throw new Error('Sand or Treat resource grid missing');
if(result.sw.length<4 || result.tw.length<4) throw new Error(`Expected four fields in each grid: ${JSON.stringify(result)}`);
const spread=a=>Math.max(...a)-Math.min(...a);
if(spread(result.sw)>1.5) throw new Error(`Sand columns are not equal width: ${JSON.stringify(result)}`);
if(spread(result.tw)>1.5) throw new Error(`Treat columns unexpectedly unequal: ${JSON.stringify(result)}`);
if(Math.abs(result.sw[0]-result.tw[0])>3) throw new Error(`Sand/Treat field widths do not match closely: ${JSON.stringify(result)}`);
if(errors.length) throw new Error('Runtime errors:\n'+errors.join('\n---\n'));
console.log(`Sand spacing smoke passed. Sand=${result.sandTemplate}; Treats=${result.treatTemplate}`);
await browser.close();
