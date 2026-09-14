import {waitForCalculatorReady} from './calculator_ready.mjs';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { chromium } from 'playwright';

// Expose private engine functions only in the test response, never in the shipped site.
const runtime = readFileSync('assets/calculator.js', 'utf8').replace(
  'function initialize(',
  'window.__plannerTest = { searchPlans, searchPlansCooperative, createPlanningContext, activeCalcConfig, projectCharacter, projectedResources, createOptimizerCheckpoint }; function initialize('
);
const browser = await chromium.launch({ headless: true });
try {
  const page = await browser.newPage();
  await page.addInitScript(() => {
    const NativeDate = Date;
    const now = Date.parse('2026-08-31T01:00:00Z');
    globalThis.Date = class extends NativeDate {
      constructor(...args) { super(...(args.length ? args : [now])); }
      static now() { return now; }
    };
  });
  await page.route('http://guide.test/**', async route => {
    const file = new URL(route.request().url()).pathname.slice(1);
    const body = file === 'assets/calculator.js' ? runtime : readFileSync(file);
    const contentType = file.endsWith('.js') ? 'text/javascript' : file.endsWith('.css') ? 'text/css' : 'text/html';
    await route.fulfill({ body, contentType });
  });
  await page.goto('http://guide.test/index.html');
  await page.locator('[data-section="calculator"]').click();
  await waitForCalculatorReady(page);
  const result = await page.evaluate(async () => {
    const api = window.__plannerTest;
    const fields = { charLevel:130, bedExp:280772, oreRate:1184, essenceRate:1387,
      sandRate:850, treatRate:91, skillLevel:130, relicLevel:13, fantomonLevel:130,
      gearLevel:130, oreCurrent:240000, essenceCurrent:420000, sandCurrent:390000,
      treatCurrent:32000, hammerCurrent:110, knucklesCurrent:399, shovelCurrent:427 };
    for (const [id,value] of Object.entries(fields)) document.getElementById(id).value=String(value);
    const cfg=api.activeCalcConfig(), p=api.projectCharacter(cfg), desired=16794;
    const base=api.projectedResources(p.hours,cfg);
    const variants=[
      {...base,ore:10000000,essence:0,sand:0},
      {...base,ore:0,essence:10000000,sand:0},
      {...base,ore:0,essence:0,sand:10000000}
    ];
    const checks=[];
    const syncResults=[];
    for (const name of ['searchPlans','searchPlansCooperative']) {
      const shared=api.createPlanningContext(0,desired,p,cfg);
      for (let i=0;i<variants.length;i++) {
        const job=()=>({started:performance.now(),cancelled:false});
        const reused=await api[name](0,desired,p,{...variants[i]},cfg,shared,job());
        const fresh=await api[name](0,desired,p,{...variants[i]},cfg,null,job());
        checks.push({name,index:i,equal:JSON.stringify(reused)===JSON.stringify(fresh)});
        if(name==='searchPlans') syncResults.push(JSON.stringify(fresh));
        else checks.push({name:'sync/cooperative parity',index:i,equal:JSON.stringify(fresh)===syncResults[i]});
      }
    }
    const job={started:performance.now(),cancelled:false};
    const checkpoint=api.createOptimizerCheckpoint(job);
    let browserTurn=false;
    setTimeout(()=>{browserTurn=true;},0);
    await checkpoint(true);
    const yielded=browserTurn;
    job.cancelled=true;
    let cancelled=false;
    try { await checkpoint(); } catch(error) { cancelled=error.name==='OptimizerCancelledError'; }
    const duringYield={started:performance.now(),cancelled:false};
    const pending=api.createOptimizerCheckpoint(duringYield)(true);
    duringYield.cancelled=true;
    let cancelledDuringYield=false;
    try { await pending; } catch(error) { cancelledDuringYield=error.name==='OptimizerCancelledError'; }
    return {checks,yielded,cancelled,cancelledDuringYield};
  });
  for(const check of result.checks) assert.ok(check.equal, `${check.name}: reused context changed allocation ${check.index}`);
  assert.ok(result.yielded, 'forced checkpoint must yield to browser tasks');
  assert.ok(result.cancelled, 'checkpoint must reject a cancelled job');
  assert.ok(result.cancelledDuringYield, 'checkpoint must recheck cancellation after yielding');
  console.log('Optimizer regression: six reused/fresh context comparisons, three sync/cooperative comparisons and cancellation checks passed');
} finally {
  await browser.close();
}
