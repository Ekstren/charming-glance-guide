import assert from 'node:assert/strict';
import { chromium } from 'playwright';
import { pathToFileURL } from 'node:url';
import path from 'node:path';
import { mkdirSync } from 'node:fs';
import { waitForCalculatorReady } from './calculator_ready.mjs';

const fields={targetStars:1060,historicalStars:253,charLevel:136,charExp:7156002,
  bedExp:565321,finishEarlyDays:6.5,skillLevel:140.125,relicLevel:14.4,
  fantomonLevel:139,gearLevel:147.2,exactSkillLevels:'1x141,7x140',
  exactRelicLevels:'8x15,12x14',exactFantoLevels:'3x140,1x136',
  exactGearLevels:'2x150,2x145,1x146',oreRate:1184,essenceRate:1387,
  sandRate:850,treatRate:91,oreCurrent:240000,essenceCurrent:420000,
  sandCurrent:390000,treatCurrent:32000,hammerCurrent:110,
  knucklesCurrent:399,shovelCurrent:427};
const screenshotDir=path.resolve('test-results/cards');
mkdirSync(screenshotDir,{recursive:true});
const browser=await chromium.launch({headless:true});
try {
  for(const theme of ['dark','light']) for(const width of [320,390,650,1440]){
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
    await page.evaluate(({fields,theme})=>{
      document.documentElement.dataset.theme=theme;
      for(const [id,value] of Object.entries(fields)) document.getElementById(id).value=String(value);
      document.getElementById('shovelCurrent').dispatchEvent(new Event('change',{bubbles:true}));
      document.getElementById('characterDetails').open=true;
      document.getElementById('materialsDetails').open=true;
    },{fields,theme});
    await page.waitForTimeout(100);
    await page.waitForFunction(()=>window.__sxsCalculatorSettledV1()&&!document.getElementById('postTargetGains').hidden);
    const context=`${theme} ${width}px`;
    const before=await page.locator('#resultStaminaPlan').innerText();
    for(const id of ['characterDetails','materialsDetails']){
      await page.locator(`#${id} > summary`).click();
      assert.equal(await page.locator(`#${id}`).getAttribute('open'),null,`${context}: ${id} collapses`);
      assert.equal(await page.locator('#resultStamina').isVisible(),true,`${context}: result remains visible`);
      await page.locator(`#${id} > summary`).click();
      assert.notEqual(await page.locator(`#${id}`).getAttribute('open'),null,`${context}: ${id} reopens`);
    }
    assert.equal(await page.locator('#resultStaminaPlan').innerText(),before,`${context}: disclosures preserve result`);
    const layout=await page.evaluate(fieldIds=>{
      const visible=el=>el.getBoundingClientRect().width>0&&el.getBoundingClientRect().height>0;
      const style=el=>{
        const s=getComputedStyle(el);
        return {name:el.id||el.className,padding:[s.paddingTop,s.paddingRight,s.paddingBottom,s.paddingLeft],radius:s.borderTopLeftRadius,font:s.fontSize};
      };
      const groups=['.characterTargetCard','.characterProgressCard','.compactProgression','.materialsStaminaRow','.recommendedUpgradeCard'];
      const cards=[...document.querySelectorAll('#calculatorSection .calcFormCard,#calculatorSection .resourceCard,#calculatorSection .realmInventory,#calculatorSection .postTargetGains,#calculatorSection .resultStamina')].filter(visible);
      const ids=[...document.querySelectorAll('#calculatorSection [id]')].map(el=>el.id);
      const controls=[...document.querySelectorAll('#calculatorSection input:not([type=hidden]):not([type=radio]):not([type=checkbox]),#calculatorSection select')].filter(visible);
      return {
        cards:cards.map(style),
        groups:groups.map(selector=>({selector,count:document.querySelectorAll(selector).length,card:document.querySelector(selector)?.classList.contains('calcFormCard')})),
        bodies:['#characterDetails > .currentLevelsBody','#materialsDetails > .currentLevelsBody','#calcResults'].map(selector=>style(document.querySelector(selector))),
        headings:[...document.querySelectorAll('.characterTargetCard h3,.characterProgressCard h3,.compactProgression > h3,.recommendedUpgradeCard > h3')].map(el=>({...style(el),text:el.textContent.trim()})),
        duplicates:ids.filter((id,index)=>ids.indexOf(id)!==index),
        missing:fieldIds.filter(id=>document.querySelectorAll(`#${id}`).length!==1),
        controls:controls.map(el=>({...style(el),height:el.getBoundingClientRect().height})),
        overflow:document.documentElement.scrollWidth-innerWidth,
        clipped:cards.filter(el=>el.scrollWidth>el.clientWidth+1).map(el=>el.id||el.className)
      };
    },Object.keys(fields));
    for(const group of layout.groups){
      assert.equal(group.count,1,`${context}: one ${group.selector}`);
      assert.equal(group.card,true,`${context}: grouped ${group.selector}`);
    }
    for(const card of layout.cards){
      assert.deepEqual(card.padding,['12px','12px','12px','12px'],`${context}: ${card.name} padding`);
      assert.equal(card.radius,'12px',`${context}: ${card.name} radius`);
    }
    for(const body of layout.bodies){
      const padding=width<=960?'14px':'16px';
      assert.deepEqual(body.padding,[padding,padding,padding,padding],`${context}: ${body.name} body padding`);
    }
    assert.ok(layout.headings.length>=3,`${context}: group headings present`);
    for(const heading of layout.headings){
      assert.ok(heading.text.length>0,`${context}: heading has text`);
      assert.equal(heading.font,'13px',`${context}: ${heading.text} heading size`);
    }
    for(const control of layout.controls){
      assert.equal(control.font,'16px',`${context}: ${control.name} input text`);
      assert.ok(control.height>=44,`${context}: ${control.name} touch height`);
    }
    assert.deepEqual(layout.duplicates,[],`${context}: unique IDs`);
    assert.deepEqual(layout.missing,[],`${context}: existing inputs preserved`);
    assert.ok(layout.overflow<=1,`${context}: no page overflow`);
    assert.deepEqual(layout.clipped,[],`${context}: no clipped cards`);
    assert.deepEqual(errors,[],`${context}: browser errors`);
    if(width===390||width===1440) await page.locator('#calculatorSection').screenshot({path:path.join(screenshotDir,`${theme}-${width}.png`)});
    console.log(`Calculator card layout passed: ${context}`);
    await page.close();
  }
} finally {
  await browser.close();
}
