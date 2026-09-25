import assert from 'node:assert/strict';
import {chromium} from 'playwright';
import {pathToFileURL} from 'node:url';
import path from 'node:path';

const browser=await chromium.launch();
// Resolve CSS colors through canvas, including color-mix()/color(srgb), before
// compositing ancestor backgrounds. These checks target solid guide surfaces.
async function checkContrast(page,selector,label){
  const samples=await page.locator(selector).evaluateAll(elements=>{
    const canvas=document.createElement('canvas');canvas.width=canvas.height=1;
    const ctx=canvas.getContext('2d',{willReadFrequently:true});
    const rgba=color=>{ctx.clearRect(0,0,1,1);ctx.fillStyle=color;ctx.fillRect(0,0,1,1);return [...ctx.getImageData(0,0,1,1).data];};
    const blend=(fg,bg)=>fg.slice(0,3).map((v,i)=>v*fg[3]/255+bg[i]*(1-fg[3]/255));
    const luminance=c=>c.map(v=>v/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4).reduce((sum,v,i)=>sum+v*[.2126,.7152,.0722][i],0);
    return elements.filter(el=>el.getBoundingClientRect().height).map(el=>{
      const ancestors=[];for(let node=el;node;node=node.parentElement)ancestors.unshift(node);
      let background=[255,255,255];
      for(const node of ancestors)background=blend(rgba(getComputedStyle(node).backgroundColor),background);
      const foreground=blend(rgba(getComputedStyle(el).color),background);
      const a=luminance(foreground),b=luminance(background);
      return {text:el.textContent.trim(),ratio:(Math.max(a,b)+.05)/(Math.min(a,b)+.05)};
    });
  });
  assert.ok(samples.length,`${label}: missing contrast samples`);
  for(const sample of samples)assert.ok(sample.ratio>=4.5,`${label}: ${sample.text} contrast ${sample.ratio.toFixed(2)}:1`);
}

try{
  for(const theme of ['light','dark'])for(const width of [320,390,1440]){
    const page=await browser.newPage({viewport:{width,height:1000}});
    const label=`${theme} ${width}px`,errors=[];
    page.on('pageerror',e=>errors.push(String(e)));
    await page.goto(pathToFileURL(path.resolve('index.html')).href);
    await page.evaluate(theme=>document.documentElement.dataset.theme=theme,theme);
    await page.locator('[data-section="builds"]').click();
    await page.waitForFunction(()=>document.getElementById('buildsSection').dataset.guideReady==='true');
    await page.locator('#buildsSection details').evaluateAll(elements=>elements.forEach(el=>el.open=true));
    for(const [selector,size] of [['.fantomonPick b',15],['.fantomonPick small',11]]){
      const sizes=await page.locator(`#buildsSection ${selector}:visible`).evaluateAll(elements=>elements.map(el=>parseFloat(getComputedStyle(el).fontSize)));
      assert.ok(sizes.length,`${label}: missing ${selector}`);
      assert.ok(sizes.every(value=>value>=size),`${label}: undersized ${selector}: ${sizes}`);
    }
    await checkContrast(page,'#buildsSection .priorityList > li > b,#buildsSection .skillGroup b',`${label} priority badges`);
    await checkContrast(page,'#buildsSection .rollGuide summary > span',`${label} roll labels`);
    if(width!==390){
      let states=0;
      for(const cls of ['Conqueror','Guardian','Destroyer','Dominator']){
        await page.locator(`#classTabs button[data-class="${cls}"]`).click();
        for(const role of cls==='Guardian'?['tank','dps']:cls==='Dominator'?['dps','heals']:[null]){
          if(role)await page.locator(`#buildContent button[data-${cls.toLowerCase()}-mode="${role}"]`).click();
          for(const activity of ['Dungeons','Crucible','Conquest','Mirage','Arena','Tournament']){
            await page.locator(`#buildContent .metaBuildTabs [data-meta-mode="${activity}"]`).click();
            const state=`${label} ${cls} ${role||''} ${activity}`;
            assert.equal(await page.locator('#buildContent .buildGrid .buildCard:visible').count(),1,`${state}: one visible build`);
            const clipped=await page.locator('#buildContent .metaBuildTabs button:visible,#buildContent .buildCard:visible,#buildContent .buildCard:visible header,#buildContent .buildCard:visible h3,#buildContent .buildCard:visible .skillGroup').evaluateAll(elements=>elements.filter(el=>{
              const r=el.getBoundingClientRect();
              return r.height&&(r.left<0||r.right>innerWidth+1||el.scrollWidth>el.clientWidth+2);
            }).map(el=>el.textContent.trim().slice(0,80)));
            assert.deepEqual(clipped,[],`${state}: clipped activity labels or cards`);
            await checkContrast(page,'#buildContent .metaBuildTabs button:visible',`${state} activity buttons`);
            const targets=await page.locator('#buildContent .metaBuildTabs button:visible').evaluateAll(elements=>elements.map(el=>el.getBoundingClientRect().height));
            assert.ok(targets.every(height=>height>=40),`${state}: undersized activity target`);
            states++;
          }
        }
      }
      assert.equal(states,36,`${label}: all build activities and roles checked`);
    }

    await page.locator('[data-section="companions"]').click();
    await page.waitForFunction(()=>document.getElementById('companionsSection').dataset.guideReady==='true');
    await checkContrast(page,'#companionsSection .companionNames span,#companionsSection .companionLadder b,#companionsSection .companionGroupHead small,#companionsSection .companionBreakpointTable th,#companionsSection .companionRule > b',`${label} companion accents`);
    assert.deepEqual(errors,[],`${label}: browser errors`);
    console.log(`Guide design passed: ${label}, typography, contrast, layout and touch targets`);
    await page.close();
  }
}finally{await browser.close();}
