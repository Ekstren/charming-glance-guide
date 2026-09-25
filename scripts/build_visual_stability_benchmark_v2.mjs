import {chromium} from 'playwright';
import path from 'node:path';
import {pathToFileURL} from 'node:url';

const browser=await chromium.launch({headless:true});
const page=await browser.newPage({viewport:{width:1440,height:1000}});
const errors=[];
page.on('pageerror',error=>errors.push(String(error?.stack||error)));
await page.goto(pathToFileURL(path.resolve('index.html')).href,{waitUntil:'load'});
await page.locator('.sectionSwitch button[data-section="builds"]').click();
await page.waitForFunction(()=>document.getElementById('buildsSection')?.dataset.guideReady==='true');

const counts={Guardian:4,Conqueror:2,Destroyer:4,Dominator:3};
const sequence=Array.from({length:16},(_,index)=>Object.keys(counts)[index%4]);
let immediateFullyReady=0,firstFrameStable=0,zeroTabTransition=0,maxHeightDelta=0;
const samples=[];
const snapshot=()=>{
  const host=document.getElementById('buildContent');
  const activeButton=document.querySelector('#classTabs button.active');
  const active=activeButton?.dataset.class||'';
  const transitionMs=(activeButton?.ownerDocument.defaultView.getComputedStyle(activeButton).transitionDuration||'0s').split(',').map(value=>{
    const duration=value.trim(),number=parseFloat(duration)||0;
    return Math.max(0,duration.endsWith('ms')?number:number*1000);
  }).reduce((maximum,value)=>Math.max(maximum,value),0);
  const titles=[...host.querySelectorAll('.sourceBuildCard h3')].map(element=>element.textContent.trim());
  return {active,titles,height:host.scrollHeight,source:host.querySelector('.buildSourceLink')?.getAttribute('href')||'',transitionMs};
};
const same=(first,second)=>first.active===second.active&&first.height===second.height&&first.source===second.source&&JSON.stringify(first.titles)===JSON.stringify(second.titles);

for(const cls of sequence){
  const immediate=await page.evaluate(name=>{
    document.querySelector(`#classTabs button[data-class="${name}"]`)?.click();
    const host=document.getElementById('buildContent');
    return {
      active:document.querySelector('#classTabs button.active')?.dataset.class||'',
      titles:[...host.querySelectorAll('.sourceBuildCard h3')].map(element=>element.textContent.trim()),
      height:host.scrollHeight,
      source:host.querySelector('.buildSourceLink')?.getAttribute('href')||'',
      transitionMs:getComputedStyle(document.querySelector('#classTabs button.active')).transitionDuration.split(',').map(value=>{
        const duration=value.trim(),number=parseFloat(duration)||0;
        return Math.max(0,duration.endsWith('ms')?number:number*1000);
      }).reduce((maximum,value)=>Math.max(maximum,value),0)
    };
  },cls);
  if(immediate.active===cls&&immediate.titles.length===counts[cls]&&immediate.source.startsWith('https://www.prydwen.gg/'))immediateFullyReady++;
  if(immediate.transitionMs===0)zeroTabTransition++;
  await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
  const after=await page.evaluate(snapshot);
  if(same(immediate,after))firstFrameStable++;
  maxHeightDelta=Math.max(maxHeightDelta,Math.abs(immediate.height-after.height));
  if(samples.length<4)samples.push({cls,immediate,after});
}

const result={switches:sequence.length,immediateFullyReady,firstFrameStable,zeroTabTransition,maxHeightDelta,errors,samples};
console.log('BUILD_VISUAL_JSON='+JSON.stringify(result));
await browser.close();
if(errors.length||immediateFullyReady!==sequence.length||firstFrameStable!==sequence.length||zeroTabTransition!==sequence.length||maxHeightDelta!==0){
  throw new Error('Build switching stability regression; inspect BUILD_VISUAL_JSON above');
}
