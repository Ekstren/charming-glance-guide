import {waitForCalculatorReady} from './calculator_ready.mjs';
import assert from 'node:assert/strict';
import {chromium} from 'playwright';
import pixelmatch from 'pixelmatch';
import {PNG} from 'pngjs';
import {execFileSync} from 'node:child_process';
import {readFileSync,writeFileSync,mkdirSync,mkdtempSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const config=JSON.parse(readFileSync('scripts/visual-baseline.json','utf8'));
const base=execFileSync('git',['rev-parse',`${config.commit}^{commit}`],{encoding:'utf8'}).trim();
const temp=mkdtempSync(path.join(tmpdir(),'sxs-visual-'));
const ref=path.join(temp,'reference');mkdirSync(ref);
execFileSync('git',['archive','--format=tar',`--output=${path.join(temp,'reference.tar')}`,base]);
execFileSync('tar',['-xf',path.join(temp,'reference.tar'),'-C',ref]);
const output=path.resolve('test-results/visual');mkdirSync(output,{recursive:true});
const browser=await chromium.launch();
const failures=[],report=[];
async function capture(root,width,theme){
 const page=await browser.newPage({viewport:{width,height:1000},locale:'en-US',timezoneId:'America/Los_Angeles',reducedMotion:'reduce'});
 const errors=[];page.on('pageerror',e=>errors.push(String(e)));
 await page.route(/^https?:/,route=>route.abort());
 await page.addInitScript(()=>{
  const NativeDate=Date,now=Date.parse('2026-11-08T20:00:00Z');
  globalThis.Date=class extends NativeDate{constructor(...args){super(...(args.length?args:[now]));}static now(){return now;}};
 });
 await page.goto(pathToFileURL(path.join(root,'index.html')).href);
 await page.evaluate(theme=>document.documentElement.dataset.theme=theme,theme);
 await page.addStyleTag({content:'*,*::before,*::after{animation:none!important;transition:none!important;caret-color:transparent!important}'});
 const shots={};
 for(const section of ['timeline','builds','companions','calculator']){
  await page.locator(`[data-section="${section}"]`).click();
  if(section==='calculator'){
   await waitForCalculatorReady(page);
   await page.evaluate(()=>{
    const fields={targetStars:2360,historicalStars:1060,charLevel:161,charExp:0,bedExp:3000000,finishEarlyDays:0,skillLevel:161,relicLevel:18,fantomonLevel:161,gearLevel:161,oreRate:3000,essenceRate:3500,sandRate:2300,treatRate:250,oreCurrent:240000,essenceCurrent:420000,sandCurrent:350000};
    for(const [id,value] of Object.entries(fields))document.getElementById(id).value=value;
    document.getElementById('targetStars').dispatchEvent(new Event('change',{bubbles:true}));
   });
   await page.waitForFunction(()=>/Lv\./.test(document.getElementById('projectedCharacter').value||document.getElementById('projectedCharacter').textContent));
   await page.waitForFunction(()=>window.__sxsCalculatorSettledV1?.(),null,{timeout:60000});
  }
  await page.evaluate(()=>scrollTo({top:0,behavior:'instant'}));
  await page.waitForTimeout(150);
  shots[section]=await page.screenshot({animations:'disabled'});
  if(section==='calculator'){
   shots.timing=await page.locator('.seasonPlanningRow').screenshot();
   shots.results=await page.locator('#calcResults').screenshot();
  }
  // Full-page comparisons cover below-the-fold rules and role variants as well
  // as the original approved viewports. Keep the intermediate width inexpensive.
  if(width!==650){
   if(section==='builds'){
    await page.waitForFunction(()=>!!document.querySelector('#classTabs button[data-class]'));
    for(const cls of await page.locator('#classTabs [data-class]').evaluateAll(nodes=>nodes.map(n=>n.dataset.class))){
     await page.locator(`#classTabs [data-class="${cls}"]`).click();
     await page.waitForFunction(name=>document.querySelector('#classTabs button.active')?.dataset.class===name,cls);
     await page.waitForTimeout(120);
     shots[`build-${({Magister:'Destroyer',Prophet:'Dominator',Ravager:'Conqueror',Templar:'Guardian'})[cls]||cls}`]=await page.locator('#buildsSection').screenshot();
    }
   }
   if(section==='companions'){
    for(const cls of await page.locator('#companionClassTabs [data-companion-class]').evaluateAll(nodes=>nodes.map(n=>n.dataset.companionClass))){
     await page.locator(`#companionClassTabs [data-companion-class="${cls}"]`).click();
     const roles=['Prophet','Dominator'].includes(cls)?['dps','heals']:[null];
     for(const role of roles){
      if(role)await page.locator(`[data-companion-role="${role}"]`).click();
      // Element screenshots scroll the page; park the pointer outside the section
      // so a tab cannot gain hover as content moves beneath the last click.
      await page.mouse.move(0,0);
      shots[`companion-${({Magister:'Destroyer',Prophet:'Dominator',Ravager:'Conqueror',Templar:'Guardian'})[cls]||cls}-${role||'default'}`]=await page.locator('#companionsSection').screenshot();
     }
    }
   }
   if(section==='calculator'){
    await page.locator('#calculatorSection details').evaluateAll(nodes=>nodes.forEach(el=>el.open=true));
    shots['calculator-expanded']=await page.locator('#calculatorSection').screenshot();
   }
   if(section==='timeline')shots['timeline-full']=await page.locator('#timelineSection').screenshot();
  }
 }
 assert.deepEqual(errors,[]);await page.close();return shots;
}
try{
 for(const theme of ['dark','light'])for(const width of [390,650,1440]){
  const expected=await capture(ref,width,theme),actual=await capture(process.cwd(),width,theme);
  for(const name of Object.keys(expected)){
   const label=`${theme}-${width}-${name}`,a=PNG.sync.read(expected[name]),b=PNG.sync.read(actual[name]);
   const sameSize=a.width===b.width&&a.height===b.height;
   const diff=new PNG({width:Math.max(a.width,b.width),height:Math.max(a.height,b.height)});
   const pixels=sameSize?pixelmatch(a.data,b.data,diff.data,a.width,a.height,{threshold:0.1}):diff.width*diff.height;
   // No differing pixels allowed (pixelmatch ignores antialiasing edges).
   report.push({label,pixels,sameSize});
   if(pixels){failures.push(label);writeFileSync(path.join(output,`${label}-expected.png`),expected[name]);writeFileSync(path.join(output,`${label}-actual.png`),actual[name]);if(sameSize)writeFileSync(path.join(output,`${label}-diff.png`),PNG.sync.write(diff));}
  }
  console.log(`Visual comparison: ${theme} ${width}px`);
 }
 writeFileSync(path.join(output,'report.json'),JSON.stringify({base,report},null,2));
 assert.deepEqual(failures,[],`Visual changes need review; see ${output}`);
 console.log(`${report.length} screenshots match baseline ${base.slice(0,7)}.`);
}finally{await browser.close();rmSync(temp,{recursive:true,force:true});}
