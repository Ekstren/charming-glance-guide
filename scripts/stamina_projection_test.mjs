import assert from 'node:assert/strict';
import { chromium } from 'playwright';
import { pathToFileURL } from 'node:url';
import path from 'node:path';
import { mkdirSync } from 'node:fs';
import { waitForCalculatorReady } from './calculator_ready.mjs';

// The projection must remain available after the input panels are collapsed,
// and must use the same completed solve as the Materials summary.
const browser=await chromium.launch({headless:true});
const screenshotDir=path.resolve('test-results/stamina');
mkdirSync(screenshotDir,{recursive:true});
async function settle(page){
  await page.waitForTimeout(100);
  await page.waitForFunction(()=>window.__sxsCalculatorSettledV1());
}
try {
  for(const width of [320,390,1440]){
    const page=await browser.newPage({viewport:{width,height:1000}});
    const errors=[];
    page.on('pageerror',error=>errors.push(String(error)));
    await page.addInitScript(()=>{
      const NativeDate=Date,now=Date.parse('2026-09-13T20:00:00Z');
      globalThis.Date=class extends NativeDate {
        constructor(...args){super(...(args.length?args:[now]));}
        static now(){return now;}
      };
    });
    await page.goto(pathToFileURL(path.resolve('index.html')).href);
    await page.locator('[data-section="calculator"]').click();
    await waitForCalculatorReady(page);
    await page.evaluate(()=>{
      const fields={targetStars:1060,historicalStars:253,charLevel:136,charExp:7156002,
        bedExp:565321,finishEarlyDays:6.5,skillLevel:140.125,relicLevel:14.4,
        fantomonLevel:139,gearLevel:147.2,exactSkillLevels:'1x141,7x140',
        exactRelicLevels:'8x15,12x14',exactFantoLevels:'3x140,1x136',
        exactGearLevels:'2x150,2x145,1x146',oreRate:1184,essenceRate:1387,
        sandRate:850,treatRate:91,oreCurrent:240000,essenceCurrent:420000,
        sandCurrent:390000,treatCurrent:32000,hammerCurrent:110,
        knucklesCurrent:399,shovelCurrent:427};
      for(const [id,value] of Object.entries(fields)) document.getElementById(id).value=String(value);
      document.getElementById('shovelCurrent').dispatchEvent(new Event('change',{bubbles:true}));
      document.getElementById('characterDetails').open=false;
      document.getElementById('materialsDetails').open=false;
    });
    await settle(page);
    if(width===390||width===1440) await page.locator('#calcResults').screenshot({path:path.join(screenshotDir,`auto-${width}.png`)});
    for(const [mode,label] of [['auto',null],['ore','Ore'],['essence','Essence'],['sand','Sand']]){
      await page.evaluate(mode=>{
        const select=document.getElementById('staminaMode');
        select.value=mode;
        select.dispatchEvent(new Event('change',{bubbles:true}));
      },mode);
      await settle(page);
      assert.equal(await page.locator('#resultStamina').isVisible(),true,`${width}px ${mode}: projection visible`);
      const display=await page.evaluate(()=>{
        const result=document.getElementById('resultStaminaPlan');
        const box=document.getElementById('resultStamina').getBoundingClientRect();
        return {
          result:result.innerHTML,
          original:document.getElementById('staminaCurrentPlan').innerHTML,
          text:result.textContent,
          horizon:document.getElementById('resultStaminaHorizon').textContent,
          collapsed:!document.getElementById('characterDetails').open&&!document.getElementById('materialsDetails').open,
          pageOverflow:document.documentElement.scrollWidth-innerWidth,
          textOverflow:result.scrollWidth-result.clientWidth,
          left:box.left,right:box.right,width:innerWidth
        };
      });
      const context=`${width}px ${mode}`;
      assert.equal(display.result,display.original,`${context}: summaries agree`);
      assert.equal(display.collapsed,true,`${context}: panels stay collapsed`);
      assert.match(display.text,/Projected gain: \+[\d,.]+[KMB]? /,`${context}: gain populated`);
      assert.match(display.text,mode==='auto'?/^Auto allocation:/:new RegExp(`^Current allocation: ${label} [\\d,]+`),`${context}: selected allocation`);
      assert.equal(display.horizon,'To target',`${context}: reachable target horizon`);
      assert.ok(display.pageOverflow<=1&&display.textOverflow<=1&&display.left>=-1&&display.right<=display.width+1,`${context}: no overflow`);
    }
    await page.evaluate(()=>{
      const input=document.getElementById('bedExp');
      input.value='';
      input.dispatchEvent(new Event('change',{bubbles:true}));
    });
    await settle(page);
    assert.equal(await page.locator('#resultStamina').isVisible(),false,`${width}px: missing required input hides previous result`);
    assert.deepEqual(errors,[],`${width}px: browser errors`);
    console.log(`Stamina projection passed: ${width}px, Auto/manual modes, collapsed panels, invalidated input`);
    await page.close();
  }
} finally {
  await browser.close();
}
