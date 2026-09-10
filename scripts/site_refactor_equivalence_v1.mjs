import { chromium } from 'playwright';
import crypto from 'node:crypto';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const [beforePath, afterPath] = process.argv.slice(2);
if(!beforePath || !afterPath) throw new Error('usage: node site_refactor_equivalence_v1.mjs <before-index> <after-index>');

const FIXED_MS = Date.parse('2026-09-10T15:30:00Z');
const browser = await chromium.launch({headless:true});

const makePage = async file => {
  const page = await browser.newPage({viewport:{width:1440,height:1000}});
  await page.addInitScript(ms => {
    const RealDate = Date;
    class FixedDate extends RealDate {
      constructor(...args){ super(...(args.length ? args : [ms])); }
      static now(){ return ms; }
    }
    FixedDate.UTC = RealDate.UTC;
    FixedDate.parse = RealDate.parse;
    Object.setPrototypeOf(FixedDate, RealDate);
    globalThis.Date = FixedDate;
  }, FIXED_MS);
  const errors=[];
  page.on('pageerror', e=>errors.push(String(e?.stack||e)));
  await page.goto(pathToFileURL(path.resolve(file)).href,{waitUntil:'load'});
  await page.addStyleTag({content:'*,*::before,*::after{transition:none!important;animation:none!important;scroll-behavior:auto!important;}'});
  await page.waitForTimeout(450);
  if(errors.length) throw new Error(`${file} runtime errors:\n${errors.join('\n---\n')}`);
  return page;
};

const before = await makePage(beforePath);
const after = await makePage(afterPath);

const normalizeBody = async page => page.evaluate(() => {
  const clone=document.body.cloneNode(true);
  clone.querySelectorAll('script,style,link[rel~="stylesheet"]').forEach(x=>x.remove());
  clone.querySelectorAll('[data-last-solve-ms]').forEach(x=>x.removeAttribute('data-last-solve-ms'));
  return clone.innerHTML;
});

const visualFingerprint = async page => page.evaluate(() => {
  const round=n=>Math.round(n*10)/10;
  const skip=new Set(['SCRIPT','STYLE','LINK','NOSCRIPT']);
  return [...document.body.querySelectorAll('*')]
    .filter(el=>!skip.has(el.tagName))
    .map((el,i)=>{
      const r=el.getBoundingClientRect();
      const cs=getComputedStyle(el);
      const visible=cs.display!=='none' && cs.visibility!=='hidden' && r.width>0 && r.height>0;
      if(!visible) return null;
      return {
        i, tag:el.tagName, id:el.id||'', cls:typeof el.className==='string'?el.className:'',
        x:round(r.x), y:round(r.y), w:round(r.width), h:round(r.height),
        display:cs.display, position:cs.position, overflow:cs.overflow,
        color:cs.color, background:cs.backgroundColor, border:cs.border,
        radius:cs.borderRadius, opacity:cs.opacity,
        fontSize:cs.fontSize, fontWeight:cs.fontWeight, lineHeight:cs.lineHeight,
        padding:cs.padding, margin:cs.margin, gap:cs.gap,
        grid:cs.gridTemplateColumns, flex:cs.flexDirection,
      };
    }).filter(Boolean);
});

const screenshotHash = async page => {
  const buf=await page.screenshot({fullPage:true,animations:'disabled'});
  return crypto.createHash('sha256').update(buf).digest('hex');
};

const waitBuild = async (page, cls) => {
  await page.locator('.sectionSwitch button[data-section="builds"]').click();
  await page.locator(`#classTabs button[data-class="${cls}"]`).click();
  await page.waitForFunction(name=>{
    const active=document.querySelector('#classTabs button.active')?.dataset.class;
    const host=document.getElementById('buildContent');
    return active===name && !!host?.querySelector('.buildQuickStats') && !!host?.querySelector(':scope > .priorityPair');
  }, cls, {timeout:3000});
  await page.waitForTimeout(120);
};

async function state(page, name){
  if(name==='timeline'){
    await page.setViewportSize({width:1440,height:1000});
    await page.locator('.sectionSwitch button[data-section="timeline"]').click();
  } else if(name==='companions'){
    await page.setViewportSize({width:1440,height:1000});
    await page.locator('.sectionSwitch button[data-section="companions"]').click();
  } else if(name==='calculator'){
    await page.setViewportSize({width:1440,height:1000});
    await page.locator('.sectionSwitch button[data-section="calculator"]').click();
    await page.waitForTimeout(500);
  } else if(name.startsWith('build-')){
    await page.setViewportSize({width:1440,height:1000});
    const cls=name.split('-')[1];
    await waitBuild(page,cls);
    if(name.endsWith('-heals')){
      await page.locator('#buildContent button[data-dominator-mode="heals"]').click();
    }
    if(name.endsWith('-tournament')){
      await page.locator('#buildContent .metaBuildTabs [data-meta-mode="Tournament"]').click();
      await page.locator('#buildContent .metaTournamentScenario [data-tournament-size="4v4"]').click();
    }
  } else if(name==='mobile-build'){
    await page.setViewportSize({width:390,height:844});
    await waitBuild(page,'Conqueror');
  } else throw new Error(`unknown state ${name}`);
  await page.waitForTimeout(160);
}

const states=[
  'timeline','build-Conqueror','build-Guardian','build-Destroyer','build-Dominator',
  'build-Dominator-heals','build-Conqueror-tournament','companions','calculator','mobile-build'
];

for(const name of states){
  await state(before,name);
  await state(after,name);
  const [bodyA,bodyB,fpA,fpB,shotA,shotB]=await Promise.all([
    normalizeBody(before), normalizeBody(after), visualFingerprint(before), visualFingerprint(after),
    screenshotHash(before), screenshotHash(after)
  ]);
  if(bodyA!==bodyB){
    let at=0; while(at<bodyA.length && at<bodyB.length && bodyA[at]===bodyB[at]) at++;
    throw new Error(`${name}: body DOM differs at ${at}\nBEFORE ${bodyA.slice(Math.max(0,at-180),at+300)}\nAFTER  ${bodyB.slice(Math.max(0,at-180),at+300)}`);
  }
  const jA=JSON.stringify(fpA), jB=JSON.stringify(fpB);
  if(jA!==jB){
    let at=0; while(at<jA.length && at<jB.length && jA[at]===jB[at]) at++;
    throw new Error(`${name}: computed layout/style fingerprint differs at ${at}\nBEFORE ${jA.slice(Math.max(0,at-180),at+400)}\nAFTER  ${jB.slice(Math.max(0,at-180),at+400)}`);
  }
  if(shotA!==shotB) throw new Error(`${name}: screenshot differs ${shotA} != ${shotB}`);
  console.log(`EQUIV ${name}: DOM + computed layout + pixels identical · ${shotA.slice(0,12)}`);
}

await browser.close();
console.log(`SITE_REFACTOR_EQUIVALENCE: ${states.length}/${states.length} states exact`);
