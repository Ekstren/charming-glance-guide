import { chromium } from 'playwright';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const browser=await chromium.launch({headless:true});
const page=await browser.newPage({viewport:{width:1440,height:1000}});
const errors=[];
page.on('pageerror',e=>errors.push(String(e?.stack||e)));
await page.goto(pathToFileURL(path.resolve('index.html')).href,{waitUntil:'load'});
await page.waitForTimeout(250);
await page.locator('.sectionSwitch button[data-section="builds"]').click();
await page.waitForTimeout(300);

const classes=['Guardian','Conqueror','Destroyer','Dominator'];
const sequence=Array.from({length:16},(_,i)=>classes[i%classes.length]);
let immediateFullyReady=0,firstFrameStable=0,zeroTabTransition=0;
let maxHeightDelta=0;
const samples=[];

const snap=()=>{
  const host=document.getElementById('buildContent');
  const active=document.querySelector('#classTabs button.active');
  const guide=host?.querySelector(':scope > .guideSummary');
  const grid=host?.querySelector('.buildGrid');
  const quick=host?.querySelector('.buildQuickStats');
  const roll=host?.querySelector('.rollGuide');
  const meta=host?.querySelector('.metaBuildControls');
  const hero=!!guide?.classList.contains('buildHeroLayoutV2')&&!!guide.querySelector(':scope > .buildHeroLeft')&&!!guide.querySelector(':scope > .buildHeroRoll');
  const visibleCards=[...(host?.querySelectorAll('.buildCard')||[])].filter(el=>!el.hidden&&getComputedStyle(el).display!=='none');
  const transition=active?getComputedStyle(active).transitionDuration:'missing';
  const transitionMs=transition.split(',').map(v=>v.trim()).reduce((m,v)=>{
    const n=parseFloat(v)||0;
    return Math.max(m,v.endsWith('ms')?n:n*1000);
  },0);
  const children=[...(host?.children||[])].map((el,i)=>({
    i,
    tag:el.tagName,
    cls:el.className,
    hidden:!!el.hidden,
    h:Math.round(el.getBoundingClientRect().height*10)/10,
    text:(el.textContent||'').trim().replace(/\s+/g,' ').slice(0,55)
  }));
  const counts={
    quick:host?.querySelectorAll('.buildQuickStats').length||0,
    roll:host?.querySelectorAll('.rollGuide').length||0,
    heroRoll:host?.querySelectorAll('.buildHeroRoll > .rollGuide').length||0,
    meta:host?.querySelectorAll('.metaBuildControls').length||0,
    pair:host?.querySelectorAll('.priorityPair').length||0,
    priority:host?.querySelectorAll('.priorityPanel').length||0,
    fantomon:host?.querySelectorAll('.fantomonPair').length||0,
    buildCards:host?.querySelectorAll('.buildCard').length||0,
    tooltips:host?.querySelectorAll('[data-skill-tooltip]').length||0,
  };
  return {
    cls:active?.dataset.class||'',
    quick:!!quick,
    roll:!!roll,
    meta:!!meta,
    hero,
    visibleCards:visibleCards.length,
    transitionMs,
    height:host?.scrollHeight||0,
    gridTop:grid?Math.round(grid.getBoundingClientRect().top*10)/10:null,
    quickTop:quick?Math.round(quick.getBoundingClientRect().top*10)/10:null,
    rollTop:roll?Math.round(roll.getBoundingClientRect().top*10)/10:null,
    metaTop:meta?Math.round(meta.getBoundingClientRect().top*10)/10:null,
    counts,children
  };
};

const sameLayout=(a,b)=>
  a.cls===b.cls && a.quick===b.quick && a.roll===b.roll && a.meta===b.meta && a.hero===b.hero &&
  a.visibleCards===b.visibleCards && Math.abs(a.height-b.height)<=1 &&
  a.gridTop===b.gridTop && a.quickTop===b.quickTop && a.rollTop===b.rollTop && a.metaTop===b.metaTop;

for(const cls of sequence){
  const immediate=await page.evaluate(({cls,snapSrc})=>{
    const snapshot=(0,eval)(`(${snapSrc})`);
    const btn=document.querySelector(`#classTabs button[data-class="${cls}"]`);
    if(!btn) throw new Error(`missing class tab ${cls}`);
    btn.click();
    return snapshot();
  },{cls,snapSrc:snap.toString()});
  const ready=immediate.cls===cls&&immediate.quick&&immediate.roll&&immediate.meta&&immediate.hero&&immediate.counts.heroRoll===1&&immediate.visibleCards===1;
  if(ready) immediateFullyReady++;
  if(immediate.transitionMs===0) zeroTabTransition++;

  await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
  const after=await page.evaluate(snap);
  if(sameLayout(immediate,after)) firstFrameStable++;
  maxHeightDelta=Math.max(maxHeightDelta,Math.abs(immediate.height-after.height));
  if(samples.length<4) samples.push({cls,immediate,after});
}

const result={switches:sequence.length,immediateFullyReady,firstFrameStable,zeroTabTransition,maxHeightDelta,errors,samples};
console.log('BUILD_VISUAL_JSON='+JSON.stringify(result));
await browser.close();
