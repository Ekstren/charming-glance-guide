import assert from 'node:assert/strict';
import {chromium} from 'playwright';
import {pathToFileURL} from 'node:url';
import path from 'node:path';
import {waitForCalculatorReady} from './calculator_ready.mjs';
import {CALC_SEASONS,STORAGE_KEY,characterScore,gearScore,skillScore,relicScore,fantoScore} from '../src/calculator/model.mjs';

const NOW='2026-11-08T20:00:00Z';
const cfg=CALC_SEASONS.s3;
// Independent arithmetic: five gear, eight skills, twenty relics, four Fantomons.
// Relics score above +17, even though a fresh normal-growth profile starts at +16.
assert.deepEqual(cfg.weights,{character:100,gear:14,skill:5,relic:26,fanto:6});
assert.equal(cfg.scoreFloor,160);assert.equal(cfg.relicFloor,17);
assert.equal(cfg.starBase,65);assert.equal(cfg.scorePerStar,13);
const exampleScore=125+5*14+8*5+20*26+4*6;
assert.equal(exampleScore,779);
assert.equal(characterScore({decimal:161.25},cfg)+gearScore(Array(5).fill(161),cfg)+skillScore(161,cfg)+relicScore(18,cfg)+fantoScore(161,cfg),exampleScore);
assert.equal(1060+cfg.starBase+Math.floor(exampleScore/cfg.scorePerStar),1184);
assert.equal(relicScore(16,cfg),0);assert.equal(relicScore(17,cfg),0);

const browser=await chromium.launch({headless:true});
const url=pathToFileURL(path.resolve('index.html')).href;
const actuals={targetStars:2360,historicalStars:1060,charLevel:161,charExp:0,bedExp:3000000,
  gearLevel:161,skillLevel:161,relicLevel:18,fantomonLevel:161,
  exactGearLevels:'',exactSkillLevels:'',exactRelicLevels:'',exactFantoLevels:'',
  oreRate:3000,essenceRate:3500,sandRate:2300,treatRate:250,
  staminaMode:'ore',staminaOreYield:0,staminaEssenceYield:0,staminaSandYield:0};
async function settle(page){await page.waitForFunction(()=>typeof window.__sxsCalculatorSettledV1==='function'&&window.__sxsCalculatorSettledV1(),null,{timeout:60000});}
async function open(page){
  await page.goto(url);
  await page.locator('[data-section="calculator"]').click();
  await waitForCalculatorReady(page);await settle(page);
}
async function fixture(width,saved){
  const page=await browser.newPage({viewport:{width,height:1000}}),errors=[];
  page.setDefaultTimeout(60000);page.on('pageerror',error=>errors.push(String(error)));
  await page.addInitScript(({now,key,saved})=>{
    const NativeDate=Date,stamp=NativeDate.parse(now);
    globalThis.Date=class extends NativeDate{constructor(...args){super(...(args.length?args:[stamp]));}static now(){return stamp;}};
    if(saved&&!localStorage.getItem(key))localStorage.setItem(key,JSON.stringify(saved));
  },{now:NOW,key:STORAGE_KEY,saved});
  await open(page);return {page,errors};
}
async function enter(page,fields){
  await page.evaluate(fields=>{
    for(const [id,value]of Object.entries(fields))document.getElementById(id).value=String(value);
    // One committed input observes the whole coherent account snapshot.
    const id=Object.keys(fields).at(-1);
    document.getElementById(id).dispatchEvent(new Event('change',{bubbles:true}));
  },fields);await settle(page);
}
async function state(page){return page.evaluate(key=>JSON.parse(localStorage.getItem(key)),STORAGE_KEY);}
async function assertFresh(page){
  // The lazy bundle can be ready before its first scheduled calculator paint.
  await page.waitForFunction(()=>/carried|Primostars/i.test(document.getElementById('targetMessage')?.textContent||''));
  await settle(page);
  for(const [id,value]of Object.entries({charLevel:'160',gearLevel:'160',skillLevel:'160',fantomonLevel:'160',relicLevel:'16',historicalStars:'',realmDailyOre:'0',realmDailyEssence:'0',realmDailySand:'0',bedExp:'0',oreRate:'0',essenceRate:'0',sandRate:'0',treatRate:'0',staminaOreYield:'0',staminaEssenceYield:'0',staminaSandYield:'0'}))assert.equal(await page.locator(`#${id}`).inputValue(),value,`fresh S3 ${id}`);
  assert.equal(await page.locator('#calcSeasonNotice').isVisible(),false);
  assert.equal(await page.locator('.shopEstimatePanel').evaluate(el=>el.hidden),true,'Unverified S3 shop sample must not expose an active projection control');
  assert.equal(await page.locator('#summaryOptimizedScore').textContent(),'—');
  assert.match(await page.locator('#targetMessage').textContent(),/carried|Primostars/i);
}
function numeric(text){assert.match(text,/^[\d,.]+$/);return Number(text.replaceAll(',',''));}
try{
  for(const width of [320,390,1200]){
    const {page,errors}=await fixture(width);
    await assertFresh(page);
    assert.equal(await page.locator('#seasonDeadlineLabel').textContent(),'Season 3 ends');
    assert.equal(await page.locator('#seasonEndDate').inputValue(),'2027-02-25');
    assert.match(await page.locator('#seasonDeadlineDate').textContent(),/Feb(?:ruary)? 25,? 2027/);
    assert.match(await page.locator('#seasonEndDateField').textContent(),/estimated/i);
    for(const target of [2120,2360]){
      const shortcut=page.locator(`#s2TargetPresets [data-s2-target="${target}"]`);
      await shortcut.click();
      await page.waitForFunction(target=>document.getElementById('targetStars').value===String(target),target,{timeout:60000});
      await settle(page);
      assert.equal(await shortcut.evaluate(button=>button.classList.contains('active')),true,`S3 ${target} shortcut active`);
      assert.equal((await state(page)).targetStars,String(target),`S3 ${target} shortcut persisted`);
    }
    await enter(page,{historicalStars:1060,bedExp:3000000});
    assert.equal(await page.locator('#summaryOptimizedScore').textContent(),'—','Bed projection alone must not start the heavy optimizer without actual Cart rates');
    assert.match(await page.locator('#targetMessage').textContent(),/Cart|production/i);
    await enter(page,actuals);
    const score=numeric(await page.locator('#summaryOptimizedScore').textContent());
    assert.ok(Number.isFinite(score)&&score>0,`${width}px: a real S3 plan is produced`);
    assert.equal(numeric(await page.locator('#desiredScore').textContent()),(2360-1060-65)*13);
    assert.equal(numeric(await page.locator('#currentScoreNow').textContent()),100+5*14+8*5+20*26+4*6);
    for(const [id,value]of Object.entries({currentBreakCharacter:100,currentBreakGear:70,currentBreakSkills:40,currentBreakRelics:520,currentBreakFantomons:24}))assert.equal(numeric(await page.locator(`#${id}`).textContent()),value,`${width}px ${id}`);
    for(const id of ['targetSkills','targetRelics','targetFantomons','targetGearWeapon','oreCost','essenceCost','sandCost','treatCost'])assert.doesNotMatch(await page.locator(`#${id}`).textContent(),/NaN|Infinity|undefined|^—$/);
    assert.match(await page.locator('#primostarRewardsIntro').textContent(),/^1,060 current/);
    const rewards=await page.locator('.primostarRewardRow').evaluateAll(rows=>rows.map(row=>({value:Number(row.querySelector('.rewardThreshold')?.textContent.replaceAll(',','')||row.textContent.replaceAll(',','')),reached:row.classList.contains('reached')})));
    assert.ok(rewards.length>80,'S3 threshold reference is included');
    assert.ok(rewards.every(row=>row.reached===(row.value<=1060)),'only actually carried Primostars mark rewards collected');
    assert.equal(await page.locator('.primostarThresholdGrid .primostarRewardRow').count(),40,'all forty documented S3 thresholds are shown');
    assert.equal(await page.locator('.primostarThresholdGrid .rewardValue, .primostarThresholdGrid .rewardName').count(),0,'unknown S3 reward effects are not manufactured');
    assert.doesNotMatch(await page.locator('.primostarThresholdGrid').textContent(),/undefined|null|NaN|%/);
    assert.match(await page.locator('.primostarS3Note').textContent(),/not.*verified|not.*guessed/i);
    assert.match(await page.locator('#astralRewardCount').textContent(),/Season 3 bonus effects are not verified/);
    assert.doesNotMatch(await page.locator('#resultStaminaPlan').textContent(),/Projected gain: \+[1-9]/,'unknown S3 map yield contributes no invented S2 resources');
    await enter(page,{staminaOreYield:2100});
    assert.match(await page.locator('#resultStaminaPlan').textContent(),/Projected gain: \+[\d,.]+[KMB]? Ore/);
    assert.equal(await page.locator('#resultStaminaPlan').innerHTML(),await page.locator('#staminaCurrentPlan').innerHTML());
    const oldRemaining=await page.locator('#seasonRemaining').textContent();
    await enter(page,{seasonEndDate:'2027-02-26'});
    const newRemaining=await page.locator('#seasonRemaining').textContent();
    assert.notEqual(newRemaining,oldRemaining,'manual deadline affects projection countdown');
    assert.match(await page.locator('#seasonDeadlineDate').textContent(),/Feb(?:ruary)? 26,? 2027/);
    assert.equal((await state(page)).seasonEndDate,'2027-02-26');
    assert.equal((await state(page)).staminaOreYield,'2100');
    await page.reload();await waitForCalculatorReady(page);await settle(page);
    await page.waitForFunction(expected=>document.getElementById('seasonRemaining').textContent===expected,newRemaining,{timeout:60000});
    await settle(page);
    assert.equal(await page.locator('#seasonEndDate').inputValue(),'2027-02-26');
    assert.equal(await page.locator('#staminaOreYield').inputValue(),'2100');
    assert.equal(await page.locator('#seasonRemaining').textContent(),newRemaining,'reloaded deadline keeps the same countdown');
    assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),`${width}px: no horizontal overflow`);
    assert.deepEqual(errors,[],`${width}px: browser errors`);await page.close();
    console.log(`Season 3 calculator passed ${width}px: safe defaults, exact score, real solve, reward ownership, Stamina and editable deadline persistence.`);
  }
  const savedS2={snapshotSchema:8,snapshotSeason:'s2',snapshotAt:Date.parse('2026-11-04T20:00:00Z'),historicalStars:253,targetStars:1060,charLevel:153,charExp:0,bedExp:0,gearLevel:180,skillLevel:170,relicLevel:19,fantomonLevel:170,oreCurrent:12345,oreRate:0,essenceRate:0,sandRate:0,treatRate:0};
  for(const action of ['reset','confirm']){
    const {page,errors}=await fixture(390,savedS2);
    assert.equal(await page.locator('#calcSeasonNotice').isVisible(),true);
    assert.equal((await state(page)).snapshotSeason,'s2');
    assert.equal(await page.locator('#gearLevel').inputValue(),'180');
    await enter(page,{historicalStars:1060,charLevel:161});
    assert.equal(await page.locator('#calcSeasonNotice').isVisible(),true,'editing a field never implicitly approves a season rollover');
    assert.equal((await state(page)).snapshotSeason,'s2');
    assert.equal(await page.locator('#summaryOptimizedScore').textContent(),'—');
    if(action==='reset'){
      await page.locator('#resetSeasonSnapshot').click();await settle(page);await assertFresh(page);
      assert.equal(await page.locator('#oreCurrent').inputValue(),'0');
    }else{
      await enter(page,actuals);
      assert.equal(await page.locator('#calcSeasonNotice').isVisible(),true);
      await page.locator('#confirmSeasonSnapshot').click();await settle(page);
      assert.equal(await page.locator('#calcSeasonNotice').isVisible(),false);
  assert.equal(await page.locator('.shopEstimatePanel').evaluate(el=>el.hidden),true,'Unverified S3 shop sample must not expose an active projection control');
      assert.ok(numeric(await page.locator('#summaryOptimizedScore').textContent())>0);
      assert.equal(await page.locator('#historicalStars').inputValue(),'1060');
    }
    assert.equal((await state(page)).snapshotSeason,'s3');
    assert.deepEqual(errors,[]);await page.close();
    console.log(`Season 3 rollover passed: S2 schema-8 state stays blocked until explicit ${action}.`);
  }
}finally{await browser.close();}
