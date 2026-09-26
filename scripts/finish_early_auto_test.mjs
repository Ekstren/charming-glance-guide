import assert from 'node:assert/strict';
import {chromium} from 'playwright';
import {pathToFileURL} from 'node:url';
import path from 'node:path';
import {waitForCalculatorReady} from './calculator_ready.mjs';

const browser=await chromium.launch();
try{
  const page=await browser.newPage({viewport:{width:390,height:1000}});
  const errors=[];
  page.on('pageerror',e=>errors.push(String(e)));
  await page.addInitScript(()=>{
    const NativeDate=Date,now=Date.parse('2026-09-13T20:00:00Z');
    globalThis.Date=class extends NativeDate{constructor(...args){super(...(args.length?args:[now]));}static now(){return now;}};
  });
  await page.goto(pathToFileURL(path.resolve('index.html')).href);
  await page.locator('[data-section="calculator"]').click();
  await waitForCalculatorReady(page);
  const settle=()=>page.waitForFunction(()=>window.__sxsCalculatorSettledV1(),{},{timeout:60000});
  await page.evaluate(()=>{
    const fields={targetStars:680,historicalStars:253,charLevel:136,charExp:7156002,bedExp:565321,skillLevel:140.125,relicLevel:14.4,fantomonLevel:139,gearLevel:147.2,oreRate:1184,essenceRate:1387,sandRate:850,treatRate:91,oreCurrent:240000,essenceCurrent:420000,sandCurrent:350000};
    for(const [id,value] of Object.entries(fields))document.getElementById(id).value=value;
    document.getElementById('targetStars').dispatchEvent(new Event('change',{bubbles:true}));
  });
  await page.waitForTimeout(100);await settle();
  await page.locator('#finishEarlyAuto').check();
  await page.waitForTimeout(100);await settle();
  const low=await page.locator('#finishEarlyDays').inputValue();
  assert.ok(Number(low)>0,'automatic earliest finish is found');
  await page.locator('#targetStars').fill('1060');
  await page.locator('#targetStars').dispatchEvent('change');
  await page.waitForTimeout(100);await settle();
  const high=await page.locator('#finishEarlyDays').inputValue();
  assert.ok(Number(high)<Number(low),'higher goal automatically moves finish later');
  assert.equal(await page.locator('#finishEarlyAuto').isChecked(),true);
  await page.reload();await page.locator('[data-section="calculator"]').click();
  await waitForCalculatorReady(page);await page.waitForTimeout(100);await settle();
  assert.equal(await page.locator('#finishEarlyAuto').isChecked(),true,'automatic preference survives reload');
  assert.equal(await page.locator('#finishEarlyDays').inputValue(),high,'saved goal recalculates the same cutoff');
  await page.locator('#finishEarlyAuto').uncheck();
  await page.waitForTimeout(100);await settle();
  assert.equal(await page.locator('#finishEarlyDays').inputValue(),'0');
  assert.equal(await page.locator('#finishEarlyResult').textContent(),'Full season');
  assert.deepEqual(errors,[]);
  console.log('Automatic Finish early passed: goal changes, persistence, and full-season toggle.');
}finally{await browser.close();}
