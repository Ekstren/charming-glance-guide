import assert from 'node:assert/strict';
import {readFileSync,mkdirSync} from 'node:fs';
import {pathToFileURL} from 'node:url';
import path from 'node:path';
import {chromium} from 'playwright';

const baseline=JSON.parse(readFileSync('data/affix-preview-baseline.json','utf8'));
const rows=Object.fromEntries(baseline.affixes.map(row=>[row.id,row]));
assert.equal(new Set(baseline.affixes.map(row=>row.id)).size,baseline.affixes.length,'unique evidence IDs');
assert.equal(baseline.affixes.length,55,'all six screenshots transcribed without duplicate overlaps');
for(const [kind,count] of [['normal',20],['paired',7],['effect',15],['proc',13]])assert.equal(baseline.affixes.filter(row=>row.kind===kind).length,count,`${kind} evidence rows`);
// Pin the corrections to the numbers displayed in the supplied screenshots.
for(const [id,values] of Object.entries({atk:['3.42K–5.36K'],def:['3.42K–5.36K'],hp:['17.1K–26.8K'],spd:['2.74K–4.28K'],em:['3.42K–5.36K'],ehr:['3.42K–5.36K'],atkpct:['12%–18.7%'],defpct:['12%–18.7%'],hppct:['12%–18.7%'],spdpct:['12%–18.7%'],crit:['4.8%–7.5%'],critdmg:['7.2%–11.2%'],acc:['4.8%–7.5%'],block:['4.8%–7.5%'],heal:['9.6%–15%'],critpair:['9.6%–15.3%','14.4%–23%'],critacc:['9.6%–15.3%','9.6%–15.3%'],blockpair:['9.6%–15.3%','14.4%–23%'],healpair:['4.8%–7.68%','19.2%–30.7%']})){
 assert.deepEqual(rows[id]?.components.map(p=>p.range.replaceAll('+','')),values,`${id}: screenshot precision and range`);
}
const browser=await chromium.launch();mkdirSync('test-results/affix-ranges',{recursive:true});
try{
 for(const theme of ['light','dark'])for(const width of [320,650,1440]){
  const page=await browser.newPage({viewport:{width,height:1000}}),errors=[];
  page.on('pageerror',e=>errors.push(String(e)));
  await page.goto(pathToFileURL(path.resolve('index.html')).href);
  await page.evaluate(t=>document.documentElement.dataset.theme=t,theme);
  await page.locator('[data-section="builds"]').click();
  await page.waitForFunction(()=>document.getElementById('buildsSection').dataset.guideReady==='true');
  for(const cls of ['Conqueror','Guardian','Destroyer','Dominator']){
   await page.locator(`#classTabs [data-class="${cls}"]`).click();
   for(const role of cls==='Guardian'?['tank','dps']:cls==='Dominator'?['dps','heals']:[null]){
    if(role)await page.locator(`#buildContent button[data-${cls.toLowerCase()}-mode="${role}"]`).click();
    await page.locator('#buildsSection details.rollGuide').evaluateAll(xs=>xs.forEach(x=>x.open=true));
    const guide=page.locator('#buildContent .buildHeroRoll .rollGuide');
    const label=`${theme} ${width}px ${cls} ${role||''}`;
    assert.equal(await guide.count(),1,`${label}: one visible guide`);
    const displayed=await guide.locator('[data-affix-id]').evaluateAll(xs=>xs.map(x=>({id:x.dataset.affixId,name:x.querySelector('.rollGuideName').textContent,values:x.querySelector('.rollGuideValue').innerText.split('\n').filter(Boolean),tip:x.querySelector('.rollHelp').dataset.tip})));
    assert.ok(displayed.length>=6,`${label}: class recommendations present`);
    for(const row of displayed){assert.ok(rows[row.id],`${label}: known affix`);if(row.id.endsWith('pct'))assert.ok(row.name.includes(rows[row.id].name+'%'),`${label}: percent stat distinguished from flat`);assert.deepEqual(row.values,rows[row.id].components.map(p=>p.range),`${label}: ${row.id} confirmed ranges`);assert.ok(row.tip.includes(`${rows[row.id].drop_rate_percent.toFixed(3)}%`),`${label}: correct drop rate`);}
    assert.ok(!displayed.some(row=>row.id==='dmgres'),`${label}: no invented standalone DMG RES`);
    assert.doesNotMatch(await guide.innerText(),/Warlord|Lv162|unconfirmed|approximate|11\.25%/i,`${label}: no obsolete labels or estimates`);
    const clipped=await guide.locator('.rollGuideRow,.rollGuideValue').evaluateAll(xs=>xs.filter(x=>x.scrollWidth>x.clientWidth+2).map(x=>x.textContent));
    assert.deepEqual(clipped,[],`${label}: ranges fit`);
    assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),`${label}: page fits`);
    if(cls==='Dominator'&&role==='heals'||cls==='Conqueror')await guide.screenshot({path:`test-results/affix-ranges/${theme}-${width}-${cls}-${role||'dps'}.png`});
   }
  }
  assert.deepEqual(errors,[]);await page.close();console.log(`Affix ranges passed: ${theme} ${width}px, all classes and roles`);
 }
}finally{await browser.close();}
