import assert from 'node:assert/strict';
import {readFileSync,existsSync} from 'node:fs';
import {build} from 'esbuild';
import {chromium} from 'playwright';

// A tiny controlled catalog exercises states that may be absent from today's
// researched dataset, without changing the production JSON.
const sample=(id,zone,destinyFruit,extra={})=>({id,visible:true,name:`Relic ${id}`,image:'',rarity:'Rare',element:'Fire',region:'Cinder Ridge',zone,destinyFruit,sources:[{type:'Relic Gacha',location:'Cinder Ridge'}],sourceUrl:'https://example.com/relics',...extra});
const fixtures=[sample('a','Cinder Ridge II',true,{name:'Amber Crown'}),sample('b','Cinder Ridge VII',true),sample('c','Cinder Ridge VII',true),sample('d','Cinder Ridge XVIII',true),sample('e',null,false,{rarity:'Mythic',element:'Water'}),sample('f',null,null,{rarity:'Mythic',element:'Water'}),sample('g','Verdantglade I',true,{region:'Verdantglade'}),sample('future','Aethyris I',true,{name:'Hidden Future Relic',visible:false,rarity:'Future rarity',element:'Future element'})];
const fixtureBundle=await build({entryPoints:['src/relics.mjs'],bundle:true,format:'iife',globalName:'SxsRelics',write:false,plugins:[{name:'fixture-catalog',setup(b){b.onLoad({filter:/[/\\]data[/\\]relics\.json$/},()=>({contents:JSON.stringify(fixtures),loader:'json'}));}}]});
const browser=await chromium.launch();
const errors=[];
async function open({fixture=true,blocked=false,corrupt=false,width=1440}={}){
 const page=await browser.newPage({viewport:{width,height:1000}});
 page.on('pageerror',error=>errors.push(String(error)));
 if(blocked)await page.addInitScript(()=>Object.defineProperty(window,'localStorage',{get(){throw Error('Storage blocked');}}));
 if(corrupt)await page.addInitScript(()=>localStorage.setItem('sxs-relics-owned-v1','{invalid'));
 await page.route('http://relics.test/**',route=>{
  const file=new URL(route.request().url()).pathname.slice(1);
  if(fixture&&file==='assets/relics-section.js')return route.fulfill({body:fixtureBundle.outputFiles[0].text,contentType:'text/javascript'});
  if(!existsSync(file))return route.fulfill({status:404,body:''});
  const ext=file.split('.').pop(),contentType={js:'text/javascript',css:'text/css',json:'application/json',webp:'image/webp',png:'image/png',svg:'image/svg+xml'}[ext]||'text/html';
  return route.fulfill({body:readFileSync(file),contentType});
 });
 await page.goto('http://relics.test/index.html');
 await page.locator('[data-section="relics"]').click();
 await page.waitForFunction(()=>document.getElementById('relicsSection').dataset.guideReady==='true');
 if(!fixture){
  assert.equal(await page.locator('[data-relic-region="Aethyris I"]').getAttribute('aria-pressed'),'true','current gallery defaults to Aethyris I');
  assert.equal(await page.locator('.relicCard').count(),80,'current Aethyris pool has all 80 relics');
  assert.equal(await page.locator('[data-relic-region="Loong Haven II"]').innerText(),'Loong Haven II','previous-season pool is no longer upcoming');
 }
 await page.locator('[data-relic-region="all"]').click();
 return page;
}
const ids=page=>page.locator('.relicCard').evaluateAll(xs=>xs.map(x=>x.dataset.relicId));
try{
 const page=await open();
 assert.equal(await page.locator('.relicCard').count(),7);
 assert.equal(await page.locator('#relicRarity').getByText('Future rarity',{exact:true}).count(),0);
 await page.locator('#relicSearch').fill('Hidden Future Relic');assert.deepEqual(await ids(page),[]);await page.locator('#relicReset').click();
 await page.locator('[data-relic-region="Cinder Ridge"]').click();
 assert.deepEqual(await page.locator('#relicZone option').evaluateAll(xs=>xs.map(x=>x.value)),['all','Cinder Ridge II','Cinder Ridge VII','Cinder Ridge XVIII','unknown']);
 await page.locator('#relicZone').selectOption('Cinder Ridge VII');assert.deepEqual(new Set(await ids(page)),new Set(['b','c']));
 await page.locator('#relicReset').click();assert.equal((await ids(page)).length,6,'reset retains region');
 await page.locator('[data-relic-region="all"]').click();
 assert.deepEqual(await page.locator('.relicRarityGroup h2').allTextContents(),['Mythic','Rare']);
 await page.locator('[data-owned="a"]').check();
 assert.match(await page.locator('#relicProgressText').innerText(),/1 \/ 7 owned · 14.3%/);
 await page.reload();await page.waitForFunction(()=>document.getElementById('relicsSection').dataset.guideReady==='true');
 await page.locator('[data-relic-region="all"]').click();
 assert.equal(await page.locator('[data-owned="a"]').isChecked(),true,'ownership survives reload');
 await page.locator('#relicStatus').selectOption('owned');assert.deepEqual(await ids(page),['a']);
 await page.locator('#relicStatus').selectOption('missing');assert.equal((await ids(page)).includes('a'),false);
 await page.locator('#relicReset').click();
 await page.locator('#relicRarity').selectOption('Mythic');await page.locator('#relicElement').selectOption('Water');await page.locator('#relicFruit').selectOption('no');assert.deepEqual(await ids(page),['e'],'unknown is not explicitly unavailable');
 await page.locator('#relicFruit').selectOption('unknown');assert.deepEqual(await ids(page),['f']);
 await page.locator('[data-relic-open]').click();assert.equal(await page.locator('#relicDialog .relicFruitInfo').count(),0);await page.locator('#relicDialogClose').click();
 await page.locator('#relicFruit').selectOption('no');await page.locator('[data-relic-open]').click();assert.match(await page.locator('#relicDialog .relicDetails').innerText(),/Cannot be obtained with Destiny Fruits/);await page.keyboard.press('Escape');assert.equal(await page.locator('#relicDialog').isVisible(),false);assert.equal(await page.locator('[data-relic-open="e"]').evaluate(el=>document.activeElement===el),true);
 await page.locator('#relicReset').click();await page.locator('#relicSearch').fill('  AMBER  ');assert.deepEqual(await ids(page),['a']);
 await page.locator('#relicRarity').selectOption('Mythic');assert.deepEqual(await ids(page),[]);assert.equal(await page.locator('.relicEmpty').isVisible(),true);
 await page.locator('#relicReset').click();assert.equal(await page.locator('[data-relic-mode]').count(),0,'gallery has no redundant view tabs');await page.locator('#relicStatus').selectOption('missing');await page.locator('#relicFruit').selectOption('yes');
 assert.deepEqual(new Set(await ids(page)),new Set(['b','c','d','g']),'targets contain only missing verified fruit relics');
 assert.equal(await page.locator('#relicStatus').isDisabled(),false);assert.equal(await page.locator('#relicFruit').isDisabled(),false);
 await page.locator('[data-relic-open="b"]').click();assert.match(await page.locator('#relicDialog .relicDetails').innerText(),/Destiny Fruit zone: Cinder Ridge VII/);assert.match(await page.locator('#relicDialog .relicDetails').innerText(),/Relic Gacha: Cinder Ridge/);
 assert.equal(await page.locator('#relicDialog .relicSources a').getAttribute('href'),'https://example.com/relics');await page.locator('#relicDialogClose').click();
 await page.locator('[data-owned="b"]').click();assert.equal((await ids(page)).includes('b'),false,'marking target owned removes it immediately');
 await page.locator('#relicReset').click();await page.locator('[data-owned="a"]').uncheck();assert.equal(await page.locator('[data-owned="a"]').isChecked(),false);
 await page.close();
 for(const options of [{blocked:true},{corrupt:true}]){
  const p=await open(options);assert.equal(await p.locator('.relicCard').count(),7);assert.equal(await p.locator('#relicStorageStatus').isVisible(),true);await p.locator('[data-owned="a"]').check();assert.equal(await p.locator('[data-owned="a"]').isChecked(),true);if(options.blocked)assert.match(await p.locator('#relicStorageStatus').innerText(),/could not save/);await p.close();
 }
 const dataset=JSON.parse(readFileSync('data/relics.json','utf8'));
 const visible=dataset.filter(r=>r.visible===true),hidden=dataset.filter(r=>r.visible!==true);assert.ok(visible.length&&hidden.length,'catalog retains visible and future releases');
 assert.equal(visible.length,640,'through-S3 catalog covers 400 prior and 240 Aethyris relics');
 assert.equal(new Set(dataset.map(r=>r.id)).size,dataset.length,'relic IDs are unique');
 for(const r of dataset.filter(r=>r.zone))assert.ok(r.region&&r.zone.startsWith(r.region+' '),`region/zone conflict: ${r.name}`);
 for(const region of ['Verdantglade','Cinder Ridge','Aqualis']) assert.equal(visible.filter(r=>r.region===region).length,70);
 for(const pool of ['Loong Haven I','Loong Haven II']){const rows=visible.filter(r=>r.pool===pool);assert.equal(rows.length,80);assert.equal(rows.filter(r=>r.rarity==='Mythic').length,20);}
 const aethyris=visible.filter(r=>r.region==='Aethyris');
 assert.equal(aethyris.length,240,'all current-season relic identities remain available');
 for(const pool of ['Aethyris I','Aethyris II','Aethyris III']){
  const rows=aethyris.filter(r=>r.pool===pool);assert.equal(rows.length,80);
  for(const rarity of ['Mythic','Legendary','Epic','Rare'])assert.equal(rows.filter(r=>r.rarity===rarity).length,20,`${pool}: full rarity distribution`);
 }
 assert.equal(aethyris.filter(r=>r.destinyFruit===true).length,54,'54 verified Aethyris exploration targets');
 assert.equal(new Set(aethyris.map(r=>r.zone).filter(Boolean)).size,18,'18 exact Aethyris fruit zones');
 for(const relic of aethyris){
  assert.match(relic.effectReference,/Relic \+1.*0 stars.*before equipped bonus/,`${relic.name}: explicit stat reference`);
  assert.ok(relic.set.name,`${relic.name}: game-data English set name`);
  assert.ok(relic.setBonuses.every(bonus=>/\+\d/.test(bonus.effect)),`${relic.name}: numeric set bonuses`);
 }
 assert.equal(visible.filter(r=>r.region==='Other').length,30);
 for(const [rarity,count] of [['Mythic',15],['Legendary',14],['Epic',1]]) assert.equal(visible.filter(r=>r.region==='Other'&&r.rarity===rarity).length,count);
 const images=[...new Set(dataset.map(r=>r.image).filter(Boolean))];
 assert.ok(images.length,'catalog has icons');for(const image of images){assert.ok(!/^https?:/.test(image),`icon must be local: ${image}`);assert.ok(existsSync(image),`missing icon: ${image}`);}
 for(const theme of ['light','dark'])for(const width of [320,390,1440]){
  const p=await open({fixture:false,width});await p.evaluate(t=>document.documentElement.dataset.theme=t,theme);
  assert.equal(await p.locator('.relicCard').count(),visible.length);
  if(theme==='dark'&&width===1440){
   for(const pool of ['Loong Haven I','Loong Haven II','Aethyris I','Aethyris II','Aethyris III']){await p.locator(`[data-relic-region="${pool}"]`).click();assert.equal((await ids(p)).length,80);assert.equal(await p.locator('.relicCard[data-rarity="mythic"]').count(),20);}
   const phases=await p.evaluate(()=>[window.SxsRelics.poolLabel('Aethyris II',Date.parse('2026-12-05T05:59:00-08:00')),window.SxsRelics.poolLabel('Aethyris II',Date.parse('2026-12-05T06:00:00-08:00')),window.SxsRelics.poolLabel('Aethyris III',Date.parse('2027-01-04T06:00:00-08:00'))]);
   assert.deepEqual(phases,['Aethyris II · S3 Day 31','Aethyris II','Aethyris III'],'later-pool markers follow Pacific unlock resets');
   await p.locator('[data-relic-region="Aethyris I"]').click();await p.locator('#relicFruit').selectOption('yes');assert.equal((await ids(p)).length,54);
   await p.locator('#relicZone').selectOption('Aethyris XVIII');assert.equal((await ids(p)).length,3);
   await p.locator('#relicReset').click();assert.equal(await p.locator('#relicFruit').inputValue(),'all','reset clears visible fruit selector');
   await p.locator('[data-relic-open="treasure_71606"]').click();const s3Details=await p.locator('#relicDialogContent').innerText();assert.match(s3Details,/Abyssal Lord/);assert.match(s3Details,/ATK \+58/);assert.match(s3Details,/Accuracy \+1\.2%/);await p.locator('#relicDialogClose').click();
   await p.locator('[data-relic-region="all"]').click();
  }
  const visibleIds=new Set(visible.map(r=>r.id));assert.ok((await ids(p)).every(id=>visibleIds.has(id)));
  await p.locator('#relicSearch').fill(hidden[0].name);assert.ok((await ids(p)).every(id=>visibleIds.has(id)),'hidden relic cannot appear through search');await p.locator('#relicReset').click();
  await p.locator('[data-relic-region="Verdantglade"]').click();
  assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth-document.documentElement.clientWidth)<=1,`${theme} ${width}: page overflow`);
  const bad=await p.locator('.relicCard').evaluateAll(xs=>xs.filter(x=>{const r=x.getBoundingClientRect();return r.x<0||r.right>innerWidth+1;}).length);assert.equal(bad,0,`${theme} ${width}: clipped card`);
  if(theme==='dark'&&[390,1440].includes(width))await p.screenshot({path:width===390?'../../work/relics-mobile-final.png':'../../work/relics-desktop-final.png'});
  await p.locator('[data-relic-open]').first().click();assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth-document.documentElement.clientWidth)<=1,'expanded details overflow');await p.locator('#relicDialogClose').click();
  await p.locator('.relicImage img').first().scrollIntoViewIfNeeded();await p.waitForFunction(()=>{const img=document.querySelector('.relicImage img');return img.complete&&img.naturalWidth>0;});
  if(theme==='dark'&&width===1440){const failures=await p.evaluate(async paths=>(await Promise.all(paths.map(src=>new Promise(resolve=>{const image=new Image();image.onload=()=>resolve(null);image.onerror=()=>resolve(src);image.src=src;})))).filter(Boolean),images);assert.deepEqual(failures,[],'all local icons decode');}
  await p.close();
 }
 assert.deepEqual(errors,[],'no browser runtime errors');
 console.log(`Relics passed: ownership persistence, filters, targets, Roman zone order, counts, details, unknown availability, blocked/corrupt storage, responsive themes, ${visible.length} visible / ${dataset.length} retained records and ${images.length} local icons.`);
}finally{await browser.close();}
