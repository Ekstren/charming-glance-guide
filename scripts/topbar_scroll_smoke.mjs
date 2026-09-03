import { chromium } from 'playwright';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const browser = await chromium.launch({headless:true});
const url = pathToFileURL(path.resolve('index.html')).href;
const assert = (cond,msg)=>{ if(!cond) throw new Error(msg); };

async function check(viewport,label){
  const page = await browser.newPage({viewport});
  await page.goto(url,{waitUntil:'load'});
  await page.waitForTimeout(250);
  const bar = page.locator('.topbar');
  assert(await bar.count()===1, `${label}: .topbar missing`);
  const pos = await bar.evaluate(el=>getComputedStyle(el).position);
  assert(pos!=='sticky' && pos!=='fixed', `${label}: topbar is still ${pos}`);

  // Guarantee enough scroll range so the test checks header behavior rather than
  // whichever section happens to be visible/default on this build of the site.
  await page.evaluate(()=>{ document.body.style.minHeight='2500px'; });
  await page.evaluate(()=>window.scrollTo(0,350));
  await page.waitForTimeout(80);
  const scrollY = await page.evaluate(()=>window.scrollY);
  assert(scrollY>=300, `${label}: test page did not create enough scroll range (${scrollY}px)`);
  const box = await bar.boundingBox();
  assert(box && box.y + box.height < 0, `${label}: topbar did not scroll fully out of view (y=${box?.y}, h=${box?.height})`);
  await page.close();
}

await check({width:1440,height:1000},'desktop');
await check({width:390,height:844},'mobile');
console.log('topbar scroll smoke passed: desktop and mobile headers are non-sticky and scroll away');
await browser.close();
