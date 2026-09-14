import assert from 'node:assert/strict';
import {chromium} from 'playwright';
import {readFileSync,mkdirSync,writeFileSync} from 'node:fs';
const browser=await chromium.launch();
const reports=[];
async function fixture({saved,fail,delayed,storageBlocked=false}={}){
 const page=await browser.newPage({viewport:{width:390,height:1000}}),requests=[],errors=[];
 let release;const gate=new Promise(resolve=>release=resolve);
 await page.addInitScript(({saved,storageBlocked})=>{
  if(storageBlocked)Object.defineProperty(window,'localStorage',{get(){throw Error('Blocked storage');}});
  else if(saved)localStorage.setItem('sxs-active-section',saved);
  window.startupTasks=[];
  new PerformanceObserver(list=>window.startupTasks.push(...list.getEntries().map(e=>e.duration))).observe({type:'longtask',buffered:true});
 },{saved,storageBlocked});
 const cdp=await page.context().newCDPSession(page);await cdp.send('Emulation.setCPUThrottlingRate',{rate:4});
 page.on('pageerror',e=>errors.push(String(e)));
 await page.route('http://guide.test/**',async route=>{
  const url=new URL(route.request().url()),file=url.pathname.slice(1);requests.push(file);
  if(file.endsWith('-section.js')){
   assert.match(url.searchParams.get('v'),/^[a-f0-9]{12}$/);
   if(file===fail&&requests.filter(x=>x===file).length===1)return route.abort();
   if(file===delayed)await gate;
  }
  let body;try{body=readFileSync(file);}catch{return route.fulfill({status:404,body:''});}
  return route.fulfill({body,contentType:file.endsWith('.js')?'text/javascript':file.endsWith('.css')?'text/css':'text/html'});
 });
 await page.goto('http://guide.test/index.html');
 return {page,requests,errors,release};
}
const open=async(page,name)=>{await page.locator(`[data-section="${name}"]`).click();};
const ready=(page,name)=>page.waitForFunction(name=>document.getElementById(`${name}Section`).dataset.guideReady==='true',name);
try{
 const f=await fixture();await f.page.waitForTimeout(350);
 assert.deepEqual(f.requests.filter(x=>x.endsWith('.js')),['assets/runtime.js'],'only the shell loads at startup');
 assert.equal(await f.page.locator('#buildContent .guideSummary, #companionContent .companionHero').count(),0);
 const cssBytes=readFileSync('assets/site.css').length;
 assert.ok(cssBytes<=220000,`stylesheet exceeds 220 KB: ${cssBytes}`);
 const bytes=readFileSync('assets/runtime.js').length;
 assert.ok(bytes<=60000,`startup JavaScript exceeds 60 KB: ${bytes}`);
 const tasks=await f.page.evaluate(()=>startupTasks);
 assert.ok(Math.max(0,...tasks)<1000,`startup task exceeds 1 second under 4x CPU: ${tasks}`);
 reports.push({initialJavaScriptBytes:bytes,stylesheetBytes:cssBytes,cpuSlowdown:4,longTasksMs:tasks});
 for(const name of ['builds','companions']){
  await open(f.page,name);await ready(f.page,name);await open(f.page,'timeline');await open(f.page,name);
  assert.equal(f.requests.filter(x=>x===`assets/${name}-section.js`).length,1);
 }
 assert.ok(!f.requests.includes('assets/calculator.js'));assert.deepEqual(f.errors,[]);await f.page.close();
 for(const name of ['builds','companions']){
  const f=await fixture({saved:name});await ready(f.page,name);
  assert.equal(await f.page.locator(`#${name}Section`).evaluate(el=>el.hidden),false);
  assert.ok(!f.requests.includes(`assets/${name==='builds'?'companions':'builds'}-section.js`));
  assert.deepEqual(f.errors,[]);await f.page.close();
  const r=await fixture({fail:`assets/${name}-section.js`,delayed:`assets/${name}-section.js`,storageBlocked:true});
  await open(r.page,name);await r.page.getByRole('button',{name:'Retry',exact:true}).click();
  await open(r.page,'timeline');r.release();await ready(r.page,name);
  assert.equal(await r.page.locator('#timelineSection').evaluate(el=>el.hidden),false,'late load must not change the active section');
  await open(r.page,name);assert.equal(r.requests.filter(x=>x===`assets/${name}-section.js`).length,2);
  assert.deepEqual(r.errors,[]);await r.page.close();
 }
 mkdirSync('test-results',{recursive:true});writeFileSync('test-results/startup.json',JSON.stringify(reports,null,2));
 console.log('Guide loading passed: deferred downloads, saved sections, retry, navigation races, blocked storage, and startup budgets.',reports);
}finally{await browser.close();}
