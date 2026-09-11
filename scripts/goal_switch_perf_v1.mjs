import { chromium } from 'playwright';
import { spawn } from 'node:child_process';

const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const server=spawn('python3',['-m','http.server','4173','--bind','127.0.0.1'],{stdio:'ignore'});
try{
  await sleep(500);
  const browser=await chromium.launch({headless:true});
  const page=await browser.newPage({viewport:{width:390,height:844},deviceScaleFactor:1});
  await page.goto('http://127.0.0.1:4173/',{waitUntil:'networkidle'});
  await page.evaluate(()=>localStorage.clear());
  await page.reload({waitUntil:'networkidle'});
  await page.click('[data-section="calculator"]');
  await page.waitForFunction(()=>document.querySelector('#calculatorSection')?.dataset.lastSolveMs);

  // Force a representative S2/mobile state that is well above the scoring floor.
  await page.evaluate(()=>{
    const set=(id,v)=>{const el=document.getElementById(id);if(el){el.value=String(v);el.dispatchEvent(new Event('change',{bubbles:true}));}};
    set('charLevel',131); set('charExp',0); set('bedExp',400000);
    set('historicalStars',128); set('skillLevel',137); set('relicLevel',14.1); set('fantomonLevel',140); set('gearLevel',137);
    set('oreCurrent',250000); set('essenceCurrent',250000); set('sandCurrent',250000); set('treatCurrent',50000);
    set('oreRate',1000); set('essenceRate',1200); set('sandRate',800); set('treatRate',80);
  });
  await page.waitForTimeout(2500);

  const targets=[680,800,920,1060,920,800];
  const rows=[];
  for(const target of targets){
    const before=await page.evaluate(()=>({stamp:performance.now(),last:document.querySelector('#calculatorSection')?.dataset.lastSolveMs||''}));
    await page.evaluate(target=>{
      const el=document.getElementById('targetStars');
      el.value=String(target);
      el.dispatchEvent(new Event('change',{bubbles:true}));
    },target);
    await page.waitForFunction(last=>{
      const v=document.querySelector('#calculatorSection')?.dataset.lastSolveMs||'';
      return v && v!==last;
    },before.last,{timeout:15000});
    const after=await page.evaluate(stamp=>({wall:performance.now()-stamp,solve:Number(document.querySelector('#calculatorSection')?.dataset.lastSolveMs||0)}),before.stamp);
    rows.push({target,...after});
  }

  // Verify the projected-floor fast path separately.
  await page.evaluate(()=>{
    const set=(id,v)=>{const el=document.getElementById(id);el.value=String(v);el.dispatchEvent(new Event('change',{bubbles:true}));};
    set('charLevel',130); set('charExp',0); set('bedExp',0);
  });
  await page.waitForTimeout(300);
  const floor=await page.evaluate(()=>({
    projected:document.getElementById('projectedCharacter')?.value,
    summary:document.getElementById('optimizerSummary')?.textContent||'',
    lastSolve:document.querySelector('#calculatorSection')?.dataset.lastSolveMs||''
  }));

  console.log('GOAL_SWITCH_PERF='+JSON.stringify({rows,floor}));
  await browser.close();
} finally {
  server.kill('SIGTERM');
}
