import assert from 'node:assert/strict';
import {chromium} from 'playwright';
import {pathToFileURL} from 'node:url';
import path from 'node:path';

const browser=await chromium.launch();
try{
 for(const width of [320,390,650,960,1440]) for(const theme of ['light','dark']){
  const page=await browser.newPage({viewport:{width,height:900}}),errors=[];
  page.on('pageerror',e=>errors.push(String(e)));
  await page.goto(pathToFileURL(path.resolve('index.html')).href);
  await page.locator('[data-section="timeline"]').click();
  if(await page.locator('html').getAttribute('data-theme')!==theme)await page.locator('#themeToggle').click();
  await page.locator('#showPast').check();
  for(const button of await page.locator('#timelineFilters button').all()){
   await button.click();
   assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),`${theme} ${width}: filter overflow`);
  }
  await page.locator('[data-filter="all"]').click();
  const result=await page.evaluate(()=>{
   const rgb=value=>{const n=value.match(/[\d.]+/g).map(Number),scale=value.startsWith('color(srgb')?255:1;return[n[0]*scale,n[1]*scale,n[2]*scale,n[3]??1]};
   const blend=(a,b)=>[0,1,2].map(i=>a[i]*a[3]+b[i]*(1-a[3])).concat(1);
   const luminance=c=>c.slice(0,3).map(v=>v/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4).reduce((sum,v,i)=>sum+v*[.2126,.7152,.0722][i],0);
   const contrast=el=>{let layers=[],p=el;while(p){layers.push(rgb(getComputedStyle(p).backgroundColor));p=p.parentElement;}let bg=[255,255,255,1];for(const a of layers.reverse())bg=blend(a,bg);const fg=blend(rgb(getComputedStyle(el).color),bg),l=[luminance(bg),luminance(fg)].sort((a,b)=>b-a);return(l[0]+.05)/(l[1]+.05)};
   return{
    cards:[...document.querySelectorAll('#timelineSummary > div')].map(el=>{const s=getComputedStyle(el);return{borders:[s.borderTopWidth,s.borderRightWidth,s.borderBottomWidth,s.borderLeftWidth],corners:[s.borderTopLeftRadius,s.borderTopRightRadius,s.borderBottomRightRadius,s.borderBottomLeftRadius]}}),
    labels:[...document.querySelectorAll('#timeline .category,#timeline .dateBlock > span')].map(el=>({text:el.textContent,contrast:contrast(el)})),
    currentHeight:document.getElementById('todayButton').getBoundingClientRect().height
   };
  });
  const label=`${theme} ${width}px`;
  assert.equal(result.cards.length,3,`${label}: summary present`);
  for(const card of result.cards){assert.ok(card.borders.every(v=>parseFloat(v)>0),`${label}: card border missing`);assert.ok(card.corners.every(v=>parseFloat(v)>=10),`${label}: detached card has square corners`);}
  assert.ok(result.labels.length>0);
  assert.deepEqual(result.labels.filter(x=>x.contrast<4.5),[],`${label}: low-contrast timeline labels`);
  assert.ok(result.currentHeight>=44,`${label}: current button touch size`);
  await page.locator('#themeToggle').click();await page.reload();
  assert.equal(await page.locator('html').getAttribute('data-theme'),theme==='dark'?'light':'dark',`${label}: theme persists`);
  assert.deepEqual(errors,[]);await page.close();console.log(`Timeline design passed: ${label}`);
 }
}finally{await browser.close();}
