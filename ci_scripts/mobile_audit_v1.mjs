import { chromium } from 'playwright';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const browser = await chromium.launch({headless:true});
const widths = [320, 360, 390, 430, 768];
const failures=[];
const report=[];

const assert=(cond,msg)=>{ if(!cond) failures.push(msg); };

for (const width of widths) {
  const page=await browser.newPage({viewport:{width,height:900},deviceScaleFactor:1});
  const pageErrors=[];
  page.on('pageerror', e=>pageErrors.push(String(e?.stack||e)));
  await page.goto(pathToFileURL(path.resolve('index.html')).href,{waitUntil:'load'});
  await page.waitForTimeout(350);

  const base=await page.evaluate(()=>({
    innerWidth:window.innerWidth,
    docWidth:document.documentElement.scrollWidth,
    bodyWidth:document.body.scrollWidth,
    topbar:document.querySelector('.topbar')?.getBoundingClientRect().height||0,
    nav:document.querySelector('.sectionSwitch')?.getBoundingClientRect().height||0,
  }));
  assert(base.docWidth<=width+1,`w${width}: page horizontally overflows (${base.docWidth}px)`);
  assert(base.bodyWidth<=width+1,`w${width}: body horizontally overflows (${base.bodyWidth}px)`);
  assert(pageErrors.length===0,`w${width}: page errors: ${pageErrors.join(' | ')}`);

  // Top-level navigation should fit and remain comfortably tappable.
  const nav=await page.locator('.sectionSwitch > button[data-section]').evaluateAll(btns=>btns.map(b=>{const r=b.getBoundingClientRect();return {text:b.textContent.trim(),x:r.x,y:r.y,w:r.width,h:r.height};}));
  assert(nav.length===4,`w${width}: expected four top nav buttons`);
  nav.forEach(b=>assert(b.h>=44,`w${width}: top nav ${b.text} tap target only ${b.h}px`));
  if(width<=430) assert(base.nav<=62,`w${width}: top navigation still consumes ${base.nav}px vertically`);
  if(nav.length===4) assert(nav[3].x+nav[3].w<=width+1,`w${width}: top nav clips right edge`);

  // Timeline.
  await page.locator('.sectionSwitch button[data-section="timeline"]').click();
  await page.waitForTimeout(80);
  const timeline=await page.evaluate(()=>({
    overflow:document.documentElement.scrollWidth-window.innerWidth,
    filters:[...document.querySelectorAll('#timelineFilters button')].filter(x=>x.offsetParent!==null).map(x=>{const r=x.getBoundingClientRect();return {w:r.width,h:r.height}}),
    groups:document.querySelectorAll('#timeline .dayGroup').length
  }));
  assert(timeline.overflow<=1,`w${width}: Timeline overflows by ${timeline.overflow}px`);
  assert(timeline.groups>0,`w${width}: Timeline did not render`);
  timeline.filters.forEach((b,i)=>assert(b.h>=40,`w${width}: timeline filter ${i+1} only ${b.h}px tall`));

  // Builds.
  await page.locator('.sectionSwitch button[data-section="builds"]').click();
  await page.waitForTimeout(100);
  const buildMetrics=await page.evaluate(()=>({
    overflow:document.documentElement.scrollWidth-window.innerWidth,
    classTabs:[...document.querySelectorAll('#classTabs button')].filter(x=>x.offsetParent!==null).map(x=>{const r=x.getBoundingClientRect();return {text:x.textContent.trim(),w:r.width,h:r.height,x:r.x,y:r.y}}),
    scenarioTabs:[...document.querySelectorAll('#buildContent .metaBuildTabs button')].filter(x=>x.offsetParent!==null).map(x=>{const r=x.getBoundingClientRect();return {text:x.textContent.trim(),w:r.width,h:r.height,x:r.x,y:r.y}}),
    cards:[...document.querySelectorAll('#buildContent .buildCard')].filter(x=>x.offsetParent!==null).map(x=>{const r=x.getBoundingClientRect();return {w:r.width,x:r.x,right:r.right}})
  }));
  assert(buildMetrics.overflow<=1,`w${width}: Builds overflows by ${buildMetrics.overflow}px`);
  buildMetrics.classTabs.forEach(b=>assert(b.h>=44,`w${width}: Builds class tab ${b.text} only ${b.h}px tall`));
  buildMetrics.scenarioTabs.forEach(b=>assert(b.h>=40,`w${width}: Builds scenario tab ${b.text} only ${b.h}px tall`));
  if(width<=600 && buildMetrics.classTabs.length===4){
    const rows=[...new Set(buildMetrics.classTabs.map(b=>Math.round(b.y)))];
    assert(rows.length===2,`w${width}: Builds class tabs should be a compact 2x2 grid, found ${rows.length} rows`);
  }
  buildMetrics.cards.forEach(c=>assert(c.x>=-0.5 && c.right<=width+0.5,`w${width}: Builds card clips viewport (${c.x}..${c.right})`));

  // Companions.
  await page.locator('.sectionSwitch button[data-section="companions"]').click();
  await page.waitForTimeout(80);
  const companions=await page.evaluate(()=>({
    overflow:document.documentElement.scrollWidth-window.innerWidth,
    buttons:[...document.querySelectorAll('#companionsSection button')].filter(x=>x.offsetParent!==null).slice(0,20).map(x=>{const r=x.getBoundingClientRect();return {text:x.textContent.trim(),h:r.height,w:r.width}})
  }));
  assert(companions.overflow<=1,`w${width}: Companions overflows by ${companions.overflow}px`);
  companions.buttons.forEach(b=>assert(b.h>=44,`w${width}: Companion class tab ${b.text} only ${b.h}px tall`));

  // Calculator.
  await page.locator('.sectionSwitch button[data-section="calculator"]').click();
  await page.waitForTimeout(180);
  const calc=await page.evaluate(()=>{
    const rect=id=>{const r=document.getElementById(id)?.getBoundingClientRect();return r?{x:r.x,y:r.y,w:r.width,h:r.height,right:r.right}:null};
    const layout=document.querySelector('.calculatorLayout');
    const cs=layout?getComputedStyle(layout):null;
    return {
      overflow:document.documentElement.scrollWidth-window.innerWidth,
      cols:cs?.gridTemplateColumns||'',
      bed:rect('bedExp'),
      projected:rect('projectedCharacter'),
      inputs:[...document.querySelectorAll('#calculatorSection input:not([type="checkbox"]),#calculatorSection select')].filter(x=>x.offsetParent!==null).map(x=>{const r=x.getBoundingClientRect();return {id:x.id,h:r.height,x:r.x,right:r.right}}),
      presetWrap:document.getElementById('s2TargetPresets')?(()=>{const r=document.getElementById('s2TargetPresets').getBoundingClientRect();return {x:r.x,right:r.right,w:r.width,scroll:document.getElementById('s2TargetPresets').scrollWidth}})():null
    };
  });
  assert(calc.overflow<=1,`w${width}: Calculator overflows by ${calc.overflow}px`);
  if(width<=430) assert(calc.cols.trim().split(/\s+/).length===1 || calc.cols==='none',`w${width}: calculator still multi-column (${calc.cols})`);
  calc.inputs.forEach(i=>{
    assert(i.h>=40,`w${width}: calculator field ${i.id||'(unnamed)'} only ${i.h}px tall`);
    assert(i.x>=-0.5 && i.right<=width+0.5,`w${width}: calculator field ${i.id||'(unnamed)'} clips viewport`);
  });
  if(calc.bed&&calc.projected){
    assert(Math.abs(calc.bed.h-calc.projected.h)<0.51,`w${width}: projected height ${calc.projected.h} != bed ${calc.bed.h}`);
    assert(Math.abs(calc.bed.w-calc.projected.w)<0.51,`w${width}: projected width ${calc.projected.w} != bed ${calc.bed.w}`);
  }

  report.push({width,base,timeline,buildMetrics,companions,calc});
  await page.close();
}

console.log('MOBILE_AUDIT_JSON='+JSON.stringify(report));
if(failures.length){
  console.error('MOBILE_AUDIT_FAILURES');
  failures.forEach(x=>console.error('- '+x));
  await browser.close();
  process.exit(1);
}
console.log(`Mobile audit passed at ${widths.join(', ')}px`);
await browser.close();
