import { chromium } from 'playwright';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const browser=await chromium.launch({headless:true});
const page=await browser.newPage({viewport:{width:1440,height:1000}});
const errors=[];
page.on('pageerror',e=>errors.push(String(e?.stack||e)));
await page.goto(pathToFileURL(path.resolve('index.html')).href,{waitUntil:'load'});
await page.locator('.sectionSwitch button[data-section="builds"]').click();
await page.waitForTimeout(120);

const result=await page.evaluate(async()=>{
  const classes=['Conqueror','Guardian','Destroyer','Dominator'];
  const tabs=document.getElementById('classTabs');
  const host=document.getElementById('buildContent');
  const firstRefs=new Map([...tabs.querySelectorAll('button[data-class]')].map(x=>[x.dataset.class,x]));
  let tabChildMutations=0,contentChildMutations=0,immediateMetaReady=0;
  const tabObs=new MutationObserver(rows=>{for(const r of rows) if(r.type==='childList') tabChildMutations++;});
  const contentObs=new MutationObserver(rows=>{for(const r of rows) if(r.type==='childList') contentChildMutations++;});
  tabObs.observe(tabs,{childList:true});
  contentObs.observe(host,{childList:true,subtree:true});
  const times=[];
  const sequence=[];
  for(let round=0;round<5;round++) sequence.push(...classes);
  for(const cls of sequence){
    const btn=tabs.querySelector(`button[data-class="${cls}"]`);
    const start=performance.now();
    btn.click();
    times.push(performance.now()-start);
    const active=tabs.querySelector('button.active')?.dataset.class;
    const meta=host.querySelector('.metaBuildTabs');
    const visibleCard=host.querySelector('.buildGrid .buildCard:not([hidden])');
    if(active===cls && meta && visibleCard) immediateMetaReady++;
    await new Promise(resolve=>requestAnimationFrame(()=>resolve()));
  }
  await new Promise(resolve=>setTimeout(resolve,0));
  tabObs.disconnect();contentObs.disconnect();
  const stableTabs=[...firstRefs].every(([cls,node])=>tabs.querySelector(`button[data-class="${cls}"]`)===node);
  const sorted=[...times].sort((a,b)=>a-b);
  return {
    switches:sequence.length,
    averageMs:times.reduce((a,b)=>a+b,0)/times.length,
    p95Ms:sorted[Math.min(sorted.length-1,Math.floor(sorted.length*.95))],
    maxMs:Math.max(...times),
    tabChildMutations,contentChildMutations,immediateMetaReady,stableTabs,
    activeClass:tabs.querySelector('button.active')?.dataset.class||'',
    visibleBuildCards:host.querySelectorAll('.buildGrid .buildCard:not([hidden])').length
  };
});
result.errors=errors;
console.log('BUILD_SWITCH_JSON='+JSON.stringify(result));
if(errors.length) throw new Error('runtime errors: '+errors.join('\n'));
await browser.close();
