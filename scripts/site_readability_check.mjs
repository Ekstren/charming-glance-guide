import assert from 'node:assert/strict';
import { chromium } from 'playwright';
import { pathToFileURL } from 'node:url';
import path from 'node:path';
import { mkdirSync } from 'node:fs';

const widths=[320,390,620,650,960,1440,1710];
const output=process.env.SXS_READABILITY_SCREENSHOTS;
if(output) mkdirSync(output,{recursive:true});
const browser=await chromium.launch({headless:true});
try {
  for(const theme of ['dark','light']) for(const width of widths){
    const page=await browser.newPage({viewport:{width,height:1000}});
    const errors=[];
    page.on('pageerror',error=>errors.push(String(error)));
    await page.goto(pathToFileURL(path.resolve('index.html')).href);
    await page.evaluate(theme=>document.documentElement.dataset.theme=theme,theme);
    for(const section of ['timeline','builds','companions','calculator']){
      await page.locator(`[data-section="${section}"]`).click();
      await page.waitForTimeout(60);
      if(section==='builds'||section==='companions'){
        const selector=section==='builds'?'#classTabs button':'#companionClassTabs button';
        for(const button of await page.locator(selector).all()){
          // Companion tabs are re-rendered on selection; use their stable text.
          const label=await button.innerText();
          await page.locator(selector).filter({hasText:label}).click();
          assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),`${section} ${label} ${width}px overflow`);
        }
      }
      const result=await page.evaluate(section=>{
        const nav=document.querySelector('.sectionSwitch'),bar=nav.getBoundingClientRect();
        const tabs=[...nav.children].map(el=>{
          const r=el.getBoundingClientRect();
          return {x:r.x,y:r.y,right:r.right,width:r.width,height:r.height,clipped:el.scrollWidth>el.clientWidth+1};
        });
        const root=document.getElementById(`${section}Section`),box=root.getBoundingClientRect(),style=getComputedStyle(root);
        const readingSelectors={timeline:'.entry p',builds:'.guideSummary p,.priorityList p,.fantomonPick p',companions:'.companionPanel p,.companionLadder span,.companionBreakpointTable td',calculator:'.postTargetHeader small'};
        const smallText=[...root.querySelectorAll(readingSelectors[section])].filter(el=>el.getBoundingClientRect().height>0&&parseFloat(getComputedStyle(el).fontSize)<(section==='calculator'?12:13)).map(el=>el.textContent.slice(0,50));
        return {tabs,bar:{x:bar.x,right:bar.right},left:box.left+parseFloat(style.paddingLeft),right:box.right-parseFloat(style.paddingRight),smallText,overflow:document.documentElement.scrollWidth-innerWidth};
      },section);
      const label=`${theme} ${width}px ${section}`;
      assert.equal(result.tabs.length,4,`${label}: four section tabs`);
      assert.equal(new Set(result.tabs.map(t=>Math.round(t.y))).size,width<=360?2:1,`${label}: unexpected navigation rows`);
      assert.ok(Math.max(...result.tabs.map(t=>t.width))-Math.min(...result.tabs.map(t=>t.width))<2,`${label}: uneven tab widths`);
      assert.ok(result.tabs.every(t=>t.height>=44&&!t.clipped),`${label}: clipped/small navigation tab ${JSON.stringify(result.tabs)}`);
      assert.ok(result.bar.right-result.tabs.at(-1).right<=10,`${label}: unused space at end of navigation`);
      assert.ok(Math.abs(result.left-result.bar.x)<2&&Math.abs(result.right-result.bar.right)<2,`${label}: content/nav margins differ`);
      assert.ok(result.overflow<=1,`${label}: page overflow`);
      assert.deepEqual(result.smallText,[],`${label}: undersized reading text`);
      if(output){
        await page.evaluate(()=>scrollTo({top:0,behavior:'instant'}));
        await page.screenshot({path:path.join(output,`${theme}-${width}-${section}.png`)});
      }
    }
    assert.deepEqual(errors,[],`${theme} ${width}px: browser errors`);
    console.log(`Site readability passed: ${theme} ${width}px, all four sections and class variants`);
    await page.close();
  }
} finally {
  await browser.close();
}
