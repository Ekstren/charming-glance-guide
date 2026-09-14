import assert from 'node:assert/strict';
import {chromium} from 'playwright';
import {readFileSync} from 'node:fs';
import {waitForCalculatorReady} from './calculator_ready.mjs';
const browser=await chromium.launch();
const seed={targetStars:'920',historicalStars:'253',charLevel:'136',charExp:'7156002',bedExp:'565321',oreRate:'1184',essenceRate:'1387',sandRate:'850',treatRate:'91',theme:'light',snapshotSchema:8,snapshotAt:Date.parse('2026-09-13T20:00:00Z'),snapshotSeason:'s2',snapshotCarry:{ore:0,essence:0,sand:0,treat:0,exp:0},panelOpen:{characterDetails:true,materialsDetails:false}};
async function fixture({saved=false,failFirst=false,blockedStorage=false}={}){
 const page=await browser.newPage({viewport:{width:390,height:1000}}),errors=[];
 page.on('pageerror',e=>errors.push(String(e)));
 await page.addInitScript(({seed,saved,blockedStorage})=>{
  const NativeDate=Date,now=seed.snapshotAt;globalThis.Date=class extends NativeDate{constructor(...args){super(...(args.length?args:[now]));}static now(){return now;}};
  if(blockedStorage)Object.defineProperty(window,'localStorage',{get(){throw new Error('Storage unavailable');}});
  else if(saved&&!localStorage.getItem('charmingGlanceCloneV1')){localStorage.setItem('charmingGlanceCloneV1',JSON.stringify(seed));localStorage.setItem('sxs-shop-refresh-default-zero-v1','1');}
 },{seed,saved,blockedStorage});
 const state={requests:0,gate:null};
 await page.route('http://guide.test/**',async route=>{
  const url=new URL(route.request().url()),file=url.pathname.slice(1);
  if(file==='assets/calculator.js'){
   state.requests++;assert.match(url.searchParams.get('v'),/^[a-f0-9]{12}$/,'chunk needs its build version');
   if(failFirst&&state.requests===1)return route.abort();
   if(state.gate)await state.gate;
  }
  let body;try{body=readFileSync(file);}catch(_){return route.fulfill({status:404,body:''});}
  await route.fulfill({body,contentType:file.endsWith('.js')?'text/javascript':file.endsWith('.css')?'text/css':file.endsWith('.json')?'application/json':'text/html'});
 });
 await page.goto('http://guide.test/index.html');
 return {page,state,errors};
}
try{
 const {page,state,errors}=await fixture({saved:true});
 assert.equal(state.requests,0,'initial Timeline must not request the calculator');
 assert.equal(await page.evaluate(()=>typeof window.SxsCalculator),'undefined');
 assert.equal(await page.evaluate(()=>document.documentElement.dataset.theme),'light');
 for(const section of ['builds','companions'])await page.locator(`[data-section="${section}"]`).click();
 assert.equal(state.requests,0,'guide tabs must not request the calculator');
 await page.locator('#themeToggle').click();
 assert.deepEqual(await page.evaluate(()=>JSON.parse(localStorage.getItem('charmingGlanceCloneV1'))),seed,'theme change overwrote unloaded calculator settings');
 let release;state.gate=new Promise(resolve=>release=resolve);
 await page.locator('[data-section="calculator"]').click();
 await page.waitForFunction(()=>document.getElementById('calculatorSection').getAttribute('aria-busy')==='true');
 assert(await page.locator('.calculatorLayout').evaluate(el=>el.inert),'inputs must be protected during load');
 let edited=false;
 const edit=page.locator('#targetStars').click().then(()=>page.locator('#targetStars').fill('1060')).then(()=>edited=true);
 await page.waitForTimeout(80);assert.equal(edited,false,'input received a click while loading');
 release();await waitForCalculatorReady(page);await edit;
 await page.locator('#targetStars').blur();
 assert.equal(await page.locator('#targetStars').inputValue(),'1060');
 assert.equal(await page.locator('#charLevel').inputValue(),'136','saved character was not restored');
 assert.equal(await page.evaluate(()=>document.documentElement.dataset.theme),'dark','calculator reverted the selected theme');
 await page.locator('[data-section="timeline"]').click();await page.locator('[data-section="calculator"]').click();
 assert.equal(state.requests,1,'warm navigation downloaded calculator again');
 state.gate=null;await page.reload();await waitForCalculatorReady(page);
 assert.equal(state.requests,2,'saved Calculator tab should load once on refresh');
 assert.equal(await page.locator('#targetStars').inputValue(),'1060','edited target did not survive refresh');
 assert.deepEqual(errors,[]);await page.close();
 const retry=await fixture({failFirst:true});
 await retry.page.locator('[data-section="calculator"]').click();
 await retry.page.getByRole('button',{name:'Retry',exact:true}).waitFor();
 assert.equal(await retry.page.locator('#calculatorSection').getAttribute('aria-busy'),'false');
 let resume;retry.state.gate=new Promise(resolve=>resume=resolve);
 await retry.page.getByRole('button',{name:'Retry',exact:true}).click();
 await retry.page.locator('[data-section="builds"]').click();resume();await waitForCalculatorReady(retry.page);
 assert(await retry.page.locator('#buildsSection').isVisible(),'download completion switched the selected tab');
 assert.equal((await retry.page.locator('#currentStars').textContent()).trim(),'—','hidden calculator started a solve');
 await retry.page.locator('[data-section="calculator"]').click();await waitForCalculatorReady(retry.page);
 assert.equal(retry.state.requests,2);assert.deepEqual(retry.errors,[]);await retry.page.close();
 const blocked=await fixture({blockedStorage:true});
 await blocked.page.locator('[data-section="calculator"]').click();await waitForCalculatorReady(blocked.page);
 assert.deepEqual(blocked.errors,[]);await blocked.page.close();
 console.log('Lazy loading, saved state, theme, guarded input, warm navigation, reload, retry, rapid tab switch and unavailable storage passed.');
}finally{await browser.close();}
