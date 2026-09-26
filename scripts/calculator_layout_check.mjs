import {waitForCalculatorReady} from './calculator_ready.mjs';
import assert from 'node:assert/strict';
import { chromium } from 'playwright';
import { pathToFileURL } from 'node:url';
import path from 'node:path';
import { mkdirSync } from 'node:fs';

// Filled results and expanded custom settings catch clipping that the empty-input
// mobile audit cannot exercise. Cover narrow phones, the column transition and desktop.
const browser=await chromium.launch({headless:true});
const widths=[320,390,768,960,1090,1440];
const screenshotDir=process.env.SXS_LAYOUT_SCREENSHOTS;
if(screenshotDir) mkdirSync(screenshotDir,{recursive:true});
try {
  for(const theme of ['dark','light']) for(const width of widths){
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
    await page.evaluate(theme=>{
      document.documentElement.dataset.theme=theme;
      const fields={targetStars:1060,historicalStars:253,charLevel:136,charExp:7156002,
        bedExp:565321,finishEarlyDays:14,skillLevel:140.125,relicLevel:14.4,
        fantomonLevel:139,gearLevel:147.2,exactSkillLevels:'1x141,7x140',
        exactRelicLevels:'8x15,12x14',exactFantoLevels:'3x140,1x136',
        exactGearLevels:'2x150,2x145,1x146',oreRate:1184,essenceRate:1387,
        sandRate:850,treatRate:91,oreCurrent:240000,essenceCurrent:420000,
        sandCurrent:390000,treatCurrent:32000,hammerCurrent:110,
        knucklesCurrent:399,shovelCurrent:427};
      for(const [id,value] of Object.entries(fields)) document.getElementById(id).value=String(value);
      document.getElementById('shovelCurrent').dispatchEvent(new Event('change',{bubbles:true}));
    },theme);
    await page.waitForTimeout(100);
    await page.waitForFunction(()=>window.__sxsCalculatorSettledV1() && !document.getElementById('postTargetGains').hidden);
    const rewardState=await page.evaluate(()=>({
      heading:document.querySelector('#astralBonusReference h3')?.textContent,
      summary:document.getElementById('astralRewardCount')?.textContent.trim(),
      intro:document.getElementById('primostarRewardsIntro')?.textContent.trim(),
      reached:[...document.querySelectorAll('.primostarRewardRow.reached .rewardThreshold')].map(el=>el.textContent),
      projected:[...document.querySelectorAll('.primostarRewardRow.projected .rewardThreshold')].map(el=>el.textContent),
      next:[...document.querySelectorAll('.primostarRewardRow.next .rewardThreshold')].map(el=>el.textContent)
    }));
    assert.equal(rewardState.heading,'Astral Pact bonuses at season end',`${theme} ${width}px: bonus projection horizon`);
    assert.match(rewardState.summary,/^1,110 season-end total Primostars/,`${theme} ${width}px: season-end bonuses use projected total`);
    assert.match(rewardState.intro,/^253 current · 1,110 projected/,`${theme} ${width}px: collected carryover is separated from projected rewards`);
    assert.ok(rewardState.reached.every(value=>Number(value.replaceAll(',',''))<=253),`${theme} ${width}px: only collected tiers are marked reached`);
    assert.ok(rewardState.projected.includes('1,095'),`${theme} ${width}px: season-end reward is projected until collection`);
    assert.ok(rewardState.next.includes('1,130'),`${theme} ${width}px: next tier follows season-end projection`);
    assert.equal(await page.locator('.postTargetOptions').getAttribute('open'),null,'optional settings start collapsed');
    if(width<=960){
      await page.locator('.calculatorJumpNav a[href="#calcResults"]').click();
      await page.waitForFunction(()=>{
        const top=document.getElementById('calcResults').getBoundingClientRect().top;
        return top>=0 && top<innerHeight/2;
      });
    }
    if(screenshotDir){
      await page.locator('#calculatorSection').screenshot({path:path.join(screenshotDir,`${theme}-${width}.png`)});
    }
    await page.locator('.postTargetOptions > summary').click();
    await page.locator('input[name="postTargetToolMode"][value="custom"]').check();
    for(const id of ['postTargetOreDaily','postTargetEssenceDaily','postTargetSandDaily']) await page.locator(`#${id}`).fill('4');
    const layout=await page.evaluate(()=>{
      const rect=el=>el.getBoundingClientRect();
      const visible=el=>rect(el).width>0 && rect(el).height>0;
      const clipped=[...document.querySelectorAll('.postTargetGainGrid b,.postTargetCustom label > span,.targetTiming b')]
        .filter(el=>visible(el)&&el.scrollWidth>el.clientWidth+1).map(el=>el.id||el.textContent);
      const controls=[...document.querySelectorAll('#s2TargetPresets button,.postTargetPlanControls label,.postTargetCustom input')]
        .filter(visible).map(el=>({name:el.id||el.textContent.trim(),height:rect(el).height}));
      const rows=[...new Set([...document.querySelectorAll('#s2TargetPresets button')].map(el=>Math.round(rect(el).top)))];
      const bed=rect(document.getElementById('bedExp')),projected=rect(document.getElementById('projectedCharacter'));
      const values=[...document.querySelectorAll('.postTargetGainGrid b')].map(el=>el.textContent);
      return {overflow:document.documentElement.scrollWidth-innerWidth,clipped,controls,rows:rows.length,
        fieldAlignment:Math.abs(bed.top-projected.top),values};
    });
    const label=`${theme} ${width}px`;
    assert.ok(layout.overflow<=1,`${label}: page overflow`);
    assert.deepEqual(layout.clipped,[],`${label}: clipped labels or result values`);
    assert.equal(layout.rows,2,`${label}: breakpoints should use two rows`);
    assert.ok(layout.fieldAlignment<=1,`${label}: paired inputs do not align`);
    assert.ok(layout.values.every(value=>/\d/.test(value)),`${label}: populated inventory required`);
    for(const control of layout.controls) assert.ok(control.height>=44,`${label}: small touch target ${control.name}`);
    assert.deepEqual(errors,[],`${label}: browser errors`);
    if(screenshotDir) await page.locator('#calcResults').screenshot({path:path.join(screenshotDir,`${theme}-${width}-expanded.png`)});
    console.log(`Calculator layout passed: ${label}, filled inventory and custom controls`);
    await page.close();
  }
} finally {
  await browser.close();
}
