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
  const NativeDate=Date,now=Date.parse('2026-09-13T20:00:00Z');
  globalThis.Date=class extends NativeDate{constructor(...args){super(...(args.length?args:[now]));}static now(){return now;}};
 });
 await page.goto(pathToFileURL(path.join(root,'index.html')).href);
 await page.evaluate(theme=>document.documentElement.dataset.theme=theme,theme);
 await page.addStyleTag({content:'*,*::before,*::after{animation:none!important;transition:none!important;caret-color:transparent!important}'});
 const shots={};
 for(const section of ['timeline','builds','companions','calculator']){
  await page.locator(`[data-section="${section}"]`).click();
  if(section==='calculator'){
   await page.evaluate(()=>{
    const fields={targetStars:1060,historicalStars:253,charLevel:136,charExp:7156002,bedExp:565321,finishEarlyDays:6.5,skillLevel:140.125,relicLevel:14.4,fantomonLevel:139,gearLevel:147.2,oreRate:1184,essenceRate:1387,sandRate:850,treatRate:91,oreCurrent:240000,essenceCurrent:420000,sandCurrent:350000};
    for(const [id,value] of Object.entries(fields))document.getElementById(id).value=value;
    document.getElementById('targetStars').dispatchEvent(new Event('change',{bubbles:true}));
   });
   await page.waitForFunction(()=>/Lv\./.test(document.getElementById('projectedCharacter').value||document.getElementById('projectedCharacter').textContent));
   await page.waitForTimeout(700);
  }
  await page.evaluate(()=>scrollTo({top:0,behavior:'instant'}));
  await page.waitForTimeout(150);
  shots[section]=await page.screenshot({animations:'disabled'});
  if(section==='calculator'){
   shots.timing=await page.locator('.seasonPlanningRow').screenshot();
   shots.results=await page.locator('#calcResults').screenshot();
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
