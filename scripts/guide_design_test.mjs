import assert from 'node:assert/strict';
import {chromium} from 'playwright';
import {pathToFileURL} from 'node:url';
import path from 'node:path';

const browser=await chromium.launch();
const cardCounts={Destroyer:4,Dominator:3,Conqueror:2,Guardian:4};

async function checkContrast(page,selector,label){
  const samples=await page.locator(selector).evaluateAll(elements=>{
    const canvas=document.createElement('canvas');canvas.width=canvas.height=1;
    const ctx=canvas.getContext('2d',{willReadFrequently:true});
    const rgba=color=>{ctx.clearRect(0,0,1,1);ctx.fillStyle=color;ctx.fillRect(0,0,1,1);return [...ctx.getImageData(0,0,1,1).data];};
    const blend=(fg,bg)=>fg.slice(0,3).map((value,index)=>value*fg[3]/255+bg[index]*(1-fg[3]/255));
    const luminance=color=>color.map(value=>value/255).map(value=>value<=.04045?value/12.92:((value+.055)/1.055)**2.4).reduce((sum,value,index)=>sum+value*[.2126,.7152,.0722][index],0);
    return elements.filter(element=>element.getBoundingClientRect().height).map(element=>{
      const ancestors=[];for(let node=element;node;node=node.parentElement)ancestors.unshift(node);
      let background=[255,255,255];
      for(const node of ancestors)background=blend(rgba(getComputedStyle(node).backgroundColor),background);
      const foreground=blend(rgba(getComputedStyle(element).color),background);
      const a=luminance(foreground),b=luminance(background);
      return {text:element.textContent.trim(),ratio:(Math.max(a,b)+.05)/(Math.min(a,b)+.05)};
    });
  });
  assert.ok(samples.length,`${label}: missing contrast samples`);
  for(const sample of samples)assert.ok(sample.ratio>=4.5,`${label}: ${sample.text} contrast ${sample.ratio.toFixed(2)}:1`);
}

try{
  for(const theme of ['light','dark'])for(const width of [320,390,1440]){
    const page=await browser.newPage({viewport:{width,height:1000}});
    const label=`${theme} ${width}px`,errors=[];
    page.on('pageerror',error=>errors.push(String(error)));
    await page.goto(pathToFileURL(path.resolve('index.html')).href);
    await page.evaluate(value=>document.documentElement.dataset.theme=value,theme);
    await page.locator('[data-section="builds"]').click();
    await page.waitForFunction(()=>document.getElementById('buildsSection').dataset.guideReady==='true');

    for(const cls of Object.keys(cardCounts)){
      await page.locator(`#classTabs button[data-class="${cls}"]`).click();
      const cards=page.locator('#buildContent .sourceBuildCard');
      await page.waitForFunction(name=>document.querySelector('#classTabs button.active')?.dataset.class===name,cls);
      assert.equal(await cards.count(),cardCounts[cls],`${label} ${cls}: source card count`);
      assert.equal(await page.locator('#buildContent .buildSourceLink').count(),1,`${label} ${cls}: source link`);
      assert.equal(await page.locator('#buildContent .metaBuildTabs').count(),0,`${label} ${cls}: invented activity selector`);
      const clipped=await page.locator('#buildContent .sourceBuildCard,#buildContent .sourceBuildCard h3,#buildContent .sourceBuildCard .skillGroup,#buildContent .sourceBuildCard .skillGroup b').evaluateAll(elements=>elements.filter(element=>{
        const rect=element.getBoundingClientRect();
        return rect.height&&(rect.left<0||rect.right>innerWidth+1||element.scrollWidth>element.clientWidth+2);
      }).map(element=>element.textContent.trim().slice(0,70)));
      assert.deepEqual(clipped,[],`${label} ${cls}: clipped or overflowing source card content`);
      const targets=await page.locator('#classTabs button[data-class]').evaluateAll(elements=>elements.map(element=>element.getBoundingClientRect().height));
      assert.ok(targets.every(height=>height>=40),`${label} ${cls}: undersized class tab target ${targets}`);
      await checkContrast(page,'#classTabs button[data-class],#buildContent .skillGroup b,#buildContent .sourceBuildNote,#buildContent .buildSourceLink',`${label} ${cls} Builds text`);
    }
    const overflow=await page.evaluate(()=>document.documentElement.scrollWidth-document.documentElement.clientWidth);
    assert.ok(overflow<=2,`${label}: horizontal page overflow ${overflow}px`);

    await page.locator('[data-section="companions"]').click();
    await page.waitForFunction(()=>document.getElementById('companionsSection').dataset.guideReady==='true');
    await checkContrast(page,'#companionsSection .companionNames span,#companionsSection .companionLadder b,#companionsSection .companionGroupHead small,#companionsSection .companionBreakpointTable th,#companionsSection .companionRule > b',`${label} companion accents`);
    assert.deepEqual(errors,[],`${label}: browser errors`);
    console.log(`Guide design passed: ${label}, source build cards, contrast, overflow, touch targets and companions`);
    await page.close();
  }
}finally{await browser.close();}
