import { nextPacificResetMs, countFuturePacificResets } from '../time.mjs';
import { seasonKeyAt } from '../season-clock.mjs';
import { nextResetLocalLabel } from '../display-time.mjs';
import { PANEL_OPEN_IDS, CALC_SEASONS, S2_PLANNER_START_LEVEL, S2_FULL_SEASONAL_PREVIEW_LEVEL, S2_SCORING_START_DEFAULTS, S2_SCORING_START_CHECKS, validateS2ScoringStartDefaults, validateS2PrimoModel, GEAR_OUTPUT_IDS, INPUT_IDS, CHECK_IDS, defaults, COMPACT_NUMBER_INPUT_IDS, parseCompactNumber, SAND_BLUE_EQ, SAND_EPIC_EQ, TREAT_BASIC_EXP, TREAT_PREMIUM_EQ, TREAT_DELUXE_EQ, S2_SHOP_OBSERVED_PAGES, dailyShopMatsPerRefresh, fmt, fmtCompact, clamp, activeCalcConfig, PRESEASON_BED_HOLD_WALL_HOURS, PRESEASON_BED_FINAL_RESET_BOOST_HOURS, characterExpCollectionCutoffMs, formatRemaining, S2_EXACT_CHARACTER_EXP_FROM_130, S2_EXACT_FANTOMON_EXP_FROM_130, S2_EXACT_UPGRADE_RULES, expRequiredForLevel, s1ProjectionUsesEstimatedExp, maxFinishEarlyDays, gearScore, characterScore, levelsFromAverage, averageLevels, categoryScoreFromLevels, formatAverage, formatLevelMix, EXACT_LEVEL_AVERAGE_BINDINGS, categoryStateFromAverage, buildCategoryOptionsFromLevels, categoryCapsForCharacter, categoryInputCapsForCharacter, gearStepCost, gearStepRefined, skillStepCost, relicStepSand, fantoStepTreatCost, automaticResourceYields, applyStaminaAllocation, staminaPlanCost, MAX_REALM_REFRESHES_PER_DAY, REALM_RUNS_PER_REFRESH, realmYieldFor, realmTopup, formatRealmSchedule, candidateRealmStage, OptimizerCancelledError, smartBalanceHighestAffordable } from './model.mjs';
import { createPlannerEngine } from './engine.mjs';
import { createSavedState } from './state.mjs';
import { createCalculatorRenderer } from './render.mjs';
validateS2ScoringStartDefaults();

if(!(S2_PLANNER_START_LEVEL < CALC_SEASONS.s2.scoreFloor)){
    console.warn('S2_PLANNER_START_V1: planning start must remain below the Season Power score floor.',{plannerStart:S2_PLANNER_START_LEVEL,scoreFloor:CALC_SEASONS.s2.scoreFloor});
  }

validateS2PrimoModel();

INPUT_IDS.forEach(id => defaults[id] = document.getElementById(id)?.value ?? '');

CHECK_IDS.forEach(id => defaults[id] = document.getElementById(id)?.checked ?? false);

defaults.gearLocked = false;

defaults.theme = 'dark';

if(!defaults.staminaMode) defaults.staminaMode = 'auto';

// STAMINA_AUTO_DEFAULT_V1
const $ = id => document.getElementById(id);

function normalizeCompactNumberInput(id){
    if(!COMPACT_NUMBER_INPUT_IDS.has(id)) return;
    const el=$(id);
    if(!el) return;
    const raw=String(el.value ?? '').trim();
    if(!raw) return;
    const value=parseCompactNumber(raw,NaN);
    if(Number.isFinite(value)) el.value=String(value);
  }

function enableCompactNumberInputs(){
    COMPACT_NUMBER_INPUT_IDS.forEach(id=>{
      const el=$(id);
      if(!el) return;
      if(el.type==='number') el.type='text';
      el.inputMode='decimal';
      el.autocomplete='off';
      el.dataset.compactNumber='1';
      const hint='Supports k/m/b shorthand (example: 22.7k = 22700, 1.3m = 1300000).';
      el.title=el.title?`${el.title} ${hint}`:hint;
    });
  }

enableCompactNumberInputs();

const n = (id, fallback=0) => parseCompactNumber($(id)?.value,fallback);

const staminaMode = () => {
    const raw = $('staminaMode')?.value || 'auto';
    return ['auto','ore','essence','sand'].includes(raw) ? raw : 'auto';
  };

const staminaModeLabel = (mode = staminaMode()) => ({ore:'Ore',auto:'Auto',essence:'Skill Essence',sand:'Chrono Sand'})[mode] || 'Ore';

function savedSandEquivalent(){
    return Math.max(0,n('sandCurrent')) + Math.max(0,n('sandBlueCurrent'))*SAND_BLUE_EQ + Math.max(0,n('sandEpicCurrent'))*SAND_EPIC_EQ;
  }

function savedTreatEquivalent(){
    return Math.max(0,n('treatCurrent')) + Math.max(0,n('treatPremiumCurrent'))*TREAT_PREMIUM_EQ + Math.max(0,n('treatDeluxeCurrent'))*TREAT_DELUXE_EQ;
  }

function dailyShopMaterialEstimate(cfg=activeCalcConfig(),daysOverride=null){
    const active=cfg.key==='s1'||cfg.key==='s2';
    // SHOP_BUYOUTS_V1: input counts full shop pages purchased, not refresh presses.
    // 0 = off; 1 = base page only; 2 = base page + one restock + second full-page buyout.
    const buyouts=active?clamp(Math.floor(n('shopRefreshesDaily',0)),0,20):0;
    const days=active?Math.max(0,Number.isFinite(Number(daysOverride))?Math.floor(Number(daysOverride)):futureRealmPurchaseDays(cfg)):0;
    const perBuyout=dailyShopMatsPerRefresh(cfg);
    const perDay=Object.fromEntries(Object.entries(perBuyout).map(([k,v])=>[k,v*buyouts]));
    const total=Object.fromEntries(Object.entries(perDay).map(([k,v])=>[k,v*days]));
    return {
      active,refreshes:buyouts,buyouts,days,perRefresh:perBuyout,perBuyout,perDay,total,
      sampleCount:cfg.key==='s2'?S2_SHOP_OBSERVED_PAGES.length:0
    };
  }

function applyS2ScoringStartDefaults(){
    Object.entries(S2_SCORING_START_DEFAULTS).forEach(([id,value])=>{ if($(id)) $(id).value=String(value); });
    Object.entries(S2_SCORING_START_CHECKS).forEach(([id,value])=>{ if($(id)) $(id).checked=!!value; });
  }

function realmDailyValue(key){
    const ids={ore:'realmDailyOre',essence:'realmDailyEssence',sand:'realmDailySand'};
    const id=ids[key];
    return clamp(Math.floor(n(id,4)),0,MAX_REALM_REFRESHES_PER_DAY);
  }

function applyRecommendedRealmRefreshes(button){
    const values={
      realmDailyOre:clamp(Math.floor(Number(button?.dataset?.ore)||0),0,MAX_REALM_REFRESHES_PER_DAY),
      realmDailyEssence:clamp(Math.floor(Number(button?.dataset?.essence)||0),0,MAX_REALM_REFRESHES_PER_DAY),
      realmDailySand:clamp(Math.floor(Number(button?.dataset?.sand)||0),0,MAX_REALM_REFRESHES_PER_DAY)
    };
    Object.entries(values).forEach(([id,value])=>{
      const el=$(id);
      if(!el) return;
      el.value=String(value);
      markManualSnapshot(id);
    });
    resetMaxAchievableUi();
    saveState();
    scheduleCalculatorUpdate(0);
  }

function futureRealmPurchaseDays(cfg=activeCalcConfig()){
    const now=Date.now();
    const cutoff=upgradeFinishCutoffMs(cfg);
    if(cutoff<=now) return 0;
    const key=`${cfg.key}|${cutoff}`;
    if(FUTURE_REALM_DAY_CACHE.key===key && now<FUTURE_REALM_DAY_CACHE.validUntil) return FUTURE_REALM_DAY_CACHE.value;
    const nextReset=nextPacificResetMs(now);
    const value=countFuturePacificResets(now,cutoff);
    FUTURE_REALM_DAY_CACHE={key,value,validUntil:Math.min(nextReset,now+60_000)};
    return value;
  }

function plannedRealmRunsFor(key,cfg=activeCalcConfig()){
    return futureRealmPurchaseDays(cfg)*realmDailyValue(key)*REALM_RUNS_PER_REFRESH;
  }

function suggestedRealmDailyPlan(plan,cfg=activeCalcConfig()){
    const current={ore:realmDailyValue('ore'),essence:realmDailyValue('essence'),sand:realmDailyValue('sand')};
    const out={...current,changed:false,needsExtra:false,impossible:false,futureDays:Math.max(0,Math.floor(futureRealmPurchaseDays(cfg)||0))};
    if(!plan?.realm) return out;
    for(const key of ['ore','essence','sand']){
      const top=plan.realm?.[key];
      if(!top) continue;
      const packs=Number(top.packs);
      if(Number.isFinite(packs)&&packs>0&&out.futureDays>0&&top.feasible!==false){
        const counts=Array.isArray(top.dailyCounts)?top.dailyCounts.slice(1).map(v=>Math.max(0,Math.floor(Number(v)||0))):[];
        const maxExtra=counts.length?Math.max(0,...counts):Math.ceil(packs/out.futureDays);
        out[key]=clamp(current[key]+maxExtra,0,MAX_REALM_REFRESHES_PER_DAY);
        out.needsExtra=true;
        if(out[key]!==current[key]) out.changed=true;
      }else if(top.feasible===false && Number(top.remainingAfterMax)>0 && Number(top.maxPacks)>0){
        out[key]=MAX_REALM_REFRESHES_PER_DAY;
        out.impossible=true;
        if(out[key]!==current[key]) out.changed=true;
      }
    }
    return out;
  }

let gearLocked = false;

let snapshotAtMs = Date.now();

let snapshotSeason = seasonKeyAt(snapshotAtMs);

let snapshotCarry = {ore:0, essence:0, sand:0, treat:0, exp:0};

let snapshotStateLoaded = false;

// BUILD_DOMINATOR_RESET_PERF_V1
  // Pacific reset math is hot in S2: Realm/tool/resource projection asks the same
  // question many times during a solve. Reuse Intl formatters and memoize each
  // first-reset/cutoff pair while preserving exact PDT/PST behavior.
let FUTURE_REALM_DAY_CACHE={key:'',value:0,validUntil:0};

function resourceCutoffMs(cfg=activeCalcConfig()){
    return upgradeFinishCutoffMs(cfg);
  }

function projectionResourceHoursAt(ms,cfg=activeCalcConfig()){
    const cutoff=upgradeFinishCutoffMs(cfg);
    const capped=Math.min(ms,cutoff);
    if(capped>=cutoff) return 0;
    const wallHours=(cutoff-capped)/3_600_000;
    const boostHours=2*countFuturePacificResets(capped,cutoff);
    return Math.max(0,wallHours+boostHours);
  }

function characterSnapshot(cfg=activeCalcConfig()){
    let lvl=Math.max(1,Math.floor(n('charLevel',cfg.key==='s2'?100:122)));
    let exp=Math.max(0,n('charExp',0));
    let safety=0;
    while(safety++<400){
      const req=expRequiredForLevel(lvl,cfg);
      if(exp<req) break;
      exp-=req; lvl++;
    }
    const req=expRequiredForLevel(lvl,cfg);
    const pct=req>0?clamp(exp/req,0,0.999999999):0;
    return {level:lvl,exp,req,pct,decimal:lvl+pct};
  }

/* PRESEASON_BED_RESERVE_V1
     Character progression assumes the recommended rollover strategy by default: stop claiming
     Bed EXP 34 hours before season end, then use the final reset's 2-hour speed-up without
     claiming it. That leaves 36 hours of Bed EXP ready for the next season. The returned
     `hours` remains the full requested wall-clock horizon so Cart/material projections do not
     inherit this Character-only hold. */
function projectCharacterTo(targetMs,cfg=activeCalcConfig()){
    const now=Date.now();
    const current=characterSnapshot(cfg);
    let lvl=current.level, exp=current.exp;
    const endMs=cfg.end.getTime();
    const target=Math.max(now,Math.min(Number(targetMs)||endMs,endMs));
    const expTarget=Math.min(target,characterExpCollectionCutoffMs(cfg));
    const naturalHours=Math.max(0,(target-now)/3_600_000);
    const expNaturalHours=Math.max(0,(expTarget-now)/3_600_000);
    const boostResets=expTarget>now?countFuturePacificResets(now,expTarget):0;
    const boostHours=2*boostResets;
    const acceleratedHours=expNaturalHours+boostHours;
    exp += Math.max(0,n('bedExp',0))*acceleratedHours;
    let safety=0;
    while(safety++<400){
      const req=expRequiredForLevel(lvl,cfg);
      if(exp<req) break;
      exp-=req; lvl++;
    }
    const req=expRequiredForLevel(lvl,cfg);
    const pct=req>0?clamp(exp/req,0,0.999999999):0;
    return {level:lvl,exp,req,pct,decimal:lvl+pct,hours:naturalHours,reserve:0,acceleratedHours,naturalHours,expNaturalHours,boostHours,boostResets,current,targetMs:target,expTargetMs:expTarget,preseasonBedReserveHours:PRESEASON_BED_HOLD_WALL_HOURS+PRESEASON_BED_FINAL_RESET_BOOST_HOURS};
  }

function projectCharacter(cfg=activeCalcConfig()){
    return projectCharacterTo(cfg.end.getTime(),cfg);
  }

function syncFinishEarlyInputLimit(cfg=activeCalcConfig(),normalize=false){
    const el=$('finishEarlyDays');
    if(!el) return 0;
    const max=maxFinishEarlyDays(cfg);
    el.max=String(max);
    el.title=`Maximum possible right now: ${max} days early, based on time remaining this season.`;
    if(normalize){
      const raw=Number(el.value);
      const value=Number.isFinite(raw)?Math.min(max,Math.max(0,Math.round(raw*2)/2)):0;
      el.value=String(value);
    }
    return max;
  }

function finishEarlyDaysValue(cfg=activeCalcConfig()){
    const raw=Number($('finishEarlyDays')?.value);
    const max=maxFinishEarlyDays(cfg);
    // FINISH_EARLY_INPUT_CAP_V1: planner cutoff supports 0.5-day increments and cannot predate now.
    return Number.isFinite(raw)?Math.min(max,Math.max(0,Math.round(raw*2)/2)):0;
  }

/* GOAL_CHANGE_FINISH_EARLY_RESET_V1
     Finish Early is target-specific. If the user changes the Primostar goal after Max
     found (for example) 38 days early for a lower goal, do not let that stale cutoff make
     the new goal look impossible. New goals always solve from the full remaining season;
     Max can then be run again for the new target. */
function resetFinishEarlyForGoalChange(){
    const input=$('finishEarlyDays');
    if(!input || finishEarlyDaysValue()<=0) return false;
    input.value='0';
    return true;
  }

function finishScoreCutoffMs(cfg=activeCalcConfig()){
    const days=finishEarlyDaysValue();
    if(days<=0) return cfg.end.getTime();
    // FINISH_EARLY_DEVICE_LOCAL_V1: "days early" is an elapsed duration from the
    // actual season-end instant. Server/reset math remains Pacific internally, while
    // any displayed cutoff/deadline is formatted in the viewer device's local zone.
    const cutoff=cfg.end.getTime()-(days*24*60*60*1000);
    return Math.min(cfg.end.getTime(),cutoff);
  }

function upgradeFinishCutoffMs(cfg=activeCalcConfig()){
    return Math.max(Date.now(),finishScoreCutoffMs(cfg));
  }

function parseExactLevelInput(id,count,minLevel,maxLevel){
    const raw=String($(id)?.value||'').trim();
    if(!raw) return {active:false,valid:true,levels:null};
    const levels=[];
    const tokens=raw.split(/[,;\n]+/).map(x=>x.trim()).filter(Boolean);
    for(const token of tokens){
      let m=token.match(/^(\d+)\s*[x×]\s*(\d+)$/i);
      if(m){
        const qty=parseInt(m[1],10),lvl=parseInt(m[2],10);
        for(let i=0;i<qty&&levels.length<=count;i++) levels.push(lvl);
        continue;
      }
      if(/^\d+$/.test(token)){levels.push(parseInt(token,10));continue;}
      return {active:true,valid:false,levels:null,reason:'format'};
    }
    const min=Math.floor(minLevel),max=Math.floor(maxLevel);
    if(levels.length!==count) return {active:true,valid:false,levels:null,reason:`needs ${count} slots`};
    if(levels.some(l=>!Number.isFinite(l)||l<min||l>max)) return {active:true,valid:false,levels:null,reason:`levels must be ${min}–${max}`};
    return {active:true,valid:true,levels};
  }

function exactProgressionHasEntries(){
    return EXACT_LEVEL_AVERAGE_BINDINGS.some(({exactId})=>String($(exactId)?.value||'').trim().length>0);
  }

function exactProgressionDetails(){ return document.querySelector('details.progressionExactInputs'); }

function syncExactProgressionPanelLock(){
    const details=exactProgressionDetails();
    if(!details) return false;
    const locked=exactProgressionHasEntries();
    if(locked) details.open=true;
    details.dataset.exactLocked=locked?'true':'false';
    const hint=details.querySelector('summary small');
    if(hint) hint.textContent=locked?'Exact entries active · clear to collapse':'Optional · overrides averages';
    if(!details.dataset.exactLockBound){
      details.dataset.exactLockBound='1';
      const summary=details.querySelector(':scope > summary');
      summary?.addEventListener('click',event=>{
        if(exactProgressionHasEntries()){
          event.preventDefault();
          details.open=true;
        }
      });
      details.addEventListener('toggle',()=>{
        if(exactProgressionHasEntries()&&!details.open) details.open=true;
      });
    }
    return locked;
  }

function syncAverageInputsFromExact(cfg=activeCalcConfig(),providedCaps=null){
    const characterLevel=Math.max(1,Math.floor(n('charLevel',cfg.key==='s2'?130:100)));
    const caps=providedCaps||categoryInputCapsForCharacter(characterLevel,cfg);
    for(const binding of EXACT_LEVEL_AVERAGE_BINDINGS){
      const max=Number(caps?.[binding.capKey]);
      const parsed=parseExactLevelInput(binding.exactId,binding.count,binding.min,Number.isFinite(max)?max:Infinity);
      if(!parsed.active||!parsed.valid) continue;
      const average=averageLevels(parsed.levels);
      const input=$(binding.avgId);
      if(input) input.value=formatAverage(average,3);
    }
  }

function syncExactProgressionUi(cfg=activeCalcConfig(),providedCaps=null){
    syncExactProgressionPanelLock();
    syncAverageInputsFromExact(cfg,providedCaps);
  }

document.addEventListener('input',event=>{
    if(!EXACT_LEVEL_AVERAGE_BINDINGS.some(({exactId})=>exactId===event.target?.id)) return;
    syncExactProgressionUi(activeCalcConfig());
  },true);

function categoryStateFromUser(avgId,exactId,count,minLevel,maxLevel,floor,weight,fallback){
    const parsed=parseExactLevelInput(exactId,count,minLevel,maxLevel);
    if(parsed.active&&parsed.valid){
      const levels=parsed.levels.slice();
      return {levels,avg:averageLevels(levels),score:categoryScoreFromLevels(levels,floor,weight),exact:true};
    }
    return categoryStateFromAverage(n(avgId,fallback),count,minLevel,maxLevel,floor,weight);
  }

function gearStateFromUser(cfg,maxLevel,fallback){
    return categoryStateFromUser('gearLevel','exactGearLevels',5,100,maxLevel,cfg.scoreFloor,cfg.weights.gear,fallback);
  }

function optimizerPlanningLevel(projectedLevel,cfg=activeCalcConfig()){
    const projected=Math.max(1,Math.floor(Number(projectedLevel)||1));
    if(cfg.key!=='s2') return projected;
    const current=Math.max(1,Math.floor(Number(characterSnapshot(cfg).level)||1));
    if(current>=S2_PLANNER_START_LEVEL && current<S2_FULL_SEASONAL_PREVIEW_LEVEL){
      return Math.max(projected,S2_FULL_SEASONAL_PREVIEW_LEVEL);
    }
    return projected;
  }

function optimizerCategoryCaps(p,cfg=activeCalcConfig()){
    const projectedLevel=p?.upgradeCapLevel ?? p?.level ?? 1;
    return categoryCapsForCharacter(optimizerPlanningLevel(projectedLevel,cfg),cfg);
  }

window.__sxsPlannerCapProbeV1=(characterLevel=131)=>({...categoryCapsForCharacter(characterLevel,CALC_SEASONS.s2)});

window.__sxsResonanceGateProbeV1=()=>{
    const cfg=CALC_SEASONS.s2;
    const relicBase=[15,15,...Array(18).fill(14)];
    const relic=buildCategoryOptionsFromLevels(relicBase,18,cfg.relicFloor,cfg.weights.relic,l=>relicStepSand(l,cfg),1);
    const relicAll15=relic.findIndex(o=>Math.min(...o.levels)>=15);
    const relicFirst16=relic.findIndex(o=>Math.max(...o.levels)>=16);
    const relicLegal=relic.every(o=>Math.max(...o.levels)<=Math.min(...o.levels)+1);
    const fantoBase=[150,150,150,140];
    const fanto=buildCategoryOptionsFromLevels(fantoBase,170,cfg.scoreFloor,cfg.weights.fanto,l=>fantoStepTreatCost(l,cfg),10);
    const fantoAll150=fanto.findIndex(o=>Math.min(...o.levels)>=150);
    const fantoFirst151=fanto.findIndex(o=>Math.max(...o.levels)>=151);
    const fantoLegal=fanto.every(o=>{
      const min=Math.min(...o.levels),max=Math.max(...o.levels);
      return max<=Math.floor(min/10)*10+10;
    });
    return {relicLegal,relicAll15,relicFirst16,fantoLegal,fantoAll150,fantoFirst151};
  };

window.__sxsExactCostProbeV5=()=>{
    const cfg=CALC_SEASONS.s2;
    return {
      charLen:S2_EXACT_CHARACTER_EXP_FROM_130.length,
      fantoLen:S2_EXACT_FANTOMON_EXP_FROM_130.length,
      gear130:gearStepCost(130,cfg),gear131:gearStepCost(131,cfg),gear160:gearStepCost(160,cfg),gear188:gearStepCost(188,cfg),
      skill130:skillStepCost(130,cfg),skill140:skillStepCost(140,cfg),skill160:skillStepCost(160,cfg),skill180:skillStepCost(180,cfg),
      relic13:relicStepSand(13,cfg),relic18:relicStepSand(18,cfg),relic27:relicStepSand(27,cfg),
      fanto130:fantoStepTreatCost(130,cfg),fanto160:fantoStepTreatCost(160,cfg),
      xp130:expRequiredForLevel(130,cfg),xp210:expRequiredForLevel(210,cfg),xp281:expRequiredForLevel(281,cfg),xp287:expRequiredForLevel(287,cfg),xp288:expRequiredForLevel(288,cfg),
      refined134:gearStepRefined(134,cfg),refined139:gearStepRefined(139,cfg),refined135:gearStepRefined(135,cfg),
      preGear121:gearStepCost(121,cfg),preSkill121:skillStepCost(121,cfg)
    };
  };

// Build a resource snapshot up to an arbitrary point in the active season.
  // Season-end projection calls this with cfg.end; target ETA reuses it without rerunning the optimizer.
function futureRealmPurchaseDaysUntil(targetMs,cfg=activeCalcConfig()){
    const now=Date.now();
    const plannerCutoff=upgradeFinishCutoffMs(cfg);
    const cutoff=Math.max(now,Math.min(Number(targetMs)||plannerCutoff,plannerCutoff));
    return cutoff>now?countFuturePacificResets(now,cutoff):0;
  }

function projectedResourcesTo(targetMs,cfg=activeCalcConfig()){
    const now=Date.now();
    const plannerCutoff=upgradeFinishCutoffMs(cfg);
    const cutoff=Math.max(now,Math.min(Number(targetMs)||plannerCutoff,plannerCutoff));
    const fullRemaining=projectionResourceHoursAt(now,cfg);
    const afterCutoffRemaining=projectionResourceHoursAt(cutoff,cfg);
    const resourceHours=Math.max(0,fullRemaining-afterCutoffRemaining);
    const wallResourceHours=Math.max(0,(cutoff-now)/3_600_000);
    const boostResets=countFuturePacificResets(now,cutoff);
    const futureDays=futureRealmPurchaseDaysUntil(cutoff,cfg);
    const staminaStart=0;
    const yields=automaticResourceYields(n('charLevel',cfg.key==='s2'?100:122),cfg);
    // Stamina regenerates from real wall-clock time only; idle/2h speed-ups do not create Stamina.
    const staminaGenerated=Math.max(0,Math.floor(wallResourceHours*5));
    const staminaSpendable=staminaStart+staminaGenerated;
    const staminaNodes=Math.floor(staminaSpendable/yields.staminaPerNode);
    const staminaUnused=staminaSpendable-staminaNodes*yields.staminaPerNode;
    const cartOre=Math.max(0,n('oreRate'))*resourceHours;
    const shopEstimate=dailyShopMaterialEstimate(cfg,futureDays);
    const refinedRaw=$('refinedOreCurrent')?.value?.trim?.() ?? '';
    const refinedTracked=refinedRaw!=='';
    const refined=refinedTracked?Math.max(0,Number(refinedRaw)||0):0;
    return {
      cartHours:resourceHours,wallResourceHours,boostResets,resourceCutoffMs:cutoff,realmDays:1+futureDays,
      staminaHours:resourceHours,staminaStart,staminaGenerated,staminaSpendable,staminaNodes,staminaUnused,
      yields,cartOre,shopEstimate,
      ore:Math.max(0,n('oreCurrent'))+cartOre+shopEstimate.total.ore,
      essence:Math.max(0,n('essenceCurrent'))+Math.max(0,n('essenceRate'))*resourceHours+shopEstimate.total.essence,
      sand:savedSandEquivalent()+Math.max(0,n('sandRate'))*resourceHours+shopEstimate.total.sand,
      treat:savedTreatEquivalent()+Math.max(0,n('treatRate'))*resourceHours+shopEstimate.total.treat,
      refinedTracked,refined,
      staminaAllocation:{ore:0,essence:0,sand:0,rolla:0,unassigned:staminaNodes},
      staminaAdded:{ore:0,essence:0,sand:0,rolla:0}
    };
  }

function projectedResources(hours,cfg=activeCalcConfig()){
    return projectedResourcesTo(upgradeFinishCutoffMs(cfg),cfg);
  }

// AUTO_STAMINA_THREE_WAY_V2: Auto intentionally recommends ONE destination.
  // Evaluate exactly the three actionable states (all Ore / all Essence / all Sand),
  // including S2 reserve-aware tool usage, instead of building O(nodes) tables that are
  // never consulted by the single-target UI.
function allocateStaminaForPlan(plan,base,cfg=activeCalcConfig(),p=null){
    const total=Math.max(0,Math.floor(base.staminaNodes||0));
    const empty={ore:0,essence:0,sand:0,rolla:0,unassigned:0};
    if(total<=0) return empty;
    const map=base.yields?.map||{};
    if(!base.yields?.mapReady) return {...empty,unassigned:total};
    const mode=staminaMode();
    if(mode!=='auto'){
      const allocation={...empty};
      if((Number(map[mode])||0)>0) allocation[mode]=total;
      else allocation.unassigned=total;
      return allocation;
    }
    if(!plan){
      if((Number(map.ore)||0)>0) return {...empty,ore:total};
      return {...empty,unassigned:total};
    }
    const keys=['ore','essence','sand'];
    const costs={ore:staminaPlanCost(plan,'ore'),essence:staminaPlanCost(plan,'essence'),sand:staminaPlanCost(plan,'sand')};
    const yields={ore:Number(map.ore)||0,essence:Number(map.essence)||0,sand:Number(map.sand)||0};
    const finiteOr=(v,fallback)=>Number.isFinite(Number(v))?Number(v):fallback;
    const topupFor=(key,nodes)=>{
      const budget=(Number(base[key])||0)+Math.max(0,nodes)*yields[key];
      const sim={...base,[key]:budget};
      return realmTopupFor(key,costs[key],budget,sim,cfg,p);
    };
    const topupStates=Object.fromEntries(keys.map(key=>[key,{base:topupFor(key,0),full:topupFor(key,total)}]));
    const metricFor=targetKey=>{
      const allocation={...empty,[targetKey]:total};
      const tops=keys.map(key=>topupStates[key][key===targetKey?'full':'base']);
      const feasible=tops.every(x=>!!x?.feasible);
      const remainingAfterMax=tops.reduce((sum,x)=>sum+Math.max(0,finiteOr(x?.remainingAfterMax,1e15)),0);
      const realmOverflow=tops.reduce((sum,x)=>sum+Math.max(0,finiteOr(x?.packs,1e9)-finiteOr(x?.maxPacks,0)),0);
      const unknownPriceRefreshes=tops.reduce((sum,x)=>sum+Math.max(0,finiteOr(x?.unknownPriceRefreshes,0)),0);
      const dawnium=feasible?tops.reduce((sum,x)=>sum+finiteOr(x?.dawnium,1e15),0):Infinity;
      const realmPacks=tops.reduce((sum,x)=>sum+finiteOr(x?.packs,1e9),0);
      const bankedToolsUsed=tops.reduce((sum,x)=>sum+Math.max(0,finiteOr(x?.bankedUsed,0)),0);
      const rawShortfall=tops.reduce((sum,x)=>sum+Math.max(0,finiteOr(x?.planShortfall,x?.shortfall||0)),0);
      return {allocation,feasible,remainingAfterMax,realmOverflow,unknownPriceRefreshes,dawnium,realmPacks,bankedToolsUsed,rawShortfall};
    };
    const better=(c,b)=>{
      if(!b) return true;
      if(c.feasible!==b.feasible) return c.feasible;
      if(c.feasible){
        if(c.unknownPriceRefreshes<b.unknownPriceRefreshes) return true;
        if(c.unknownPriceRefreshes>b.unknownPriceRefreshes) return false;
        if(c.dawnium<b.dawnium-1e-9) return true;
        if(c.dawnium>b.dawnium+1e-9) return false;
        if(c.realmPacks<b.realmPacks) return true;
        if(c.realmPacks>b.realmPacks) return false;
      }else{
        if(c.remainingAfterMax<b.remainingAfterMax-0.5) return true;
        if(c.remainingAfterMax>b.remainingAfterMax+0.5) return false;
        if(c.realmOverflow<b.realmOverflow) return true;
        if(c.realmOverflow>b.realmOverflow) return false;
        if(c.rawShortfall<b.rawShortfall-0.5) return true;
        if(c.rawShortfall>b.rawShortfall+0.5) return false;
      }
      if(c.bankedToolsUsed<b.bankedToolsUsed) return true;
      if(c.bankedToolsUsed>b.bankedToolsUsed) return false;
      // Stable tie-break: bank surplus Stamina as Ore, then Essence, then Sand.
      if(c.allocation.ore>b.allocation.ore) return true;
      if(c.allocation.ore<b.allocation.ore) return false;
      if(c.allocation.essence>b.allocation.essence) return true;
      return false;
    };
    let best=null;
    for(const key of keys){
      if((Number(map[key])||0)<=0) continue;
      const candidate=metricFor(key);
      if(better(candidate,best)) best=candidate;
    }
    return best?.allocation||{...empty,ore:(Number(map.ore)||0)>0?total:0,unassigned:(Number(map.ore)||0)>0?0:total};
  }

function realmTopupForMoment(key,cost,resources,targetMs,pAt,cfg=activeCalcConfig()){
    const ids={ore:'hammerCurrent',essence:'knucklesCurrent',sand:'shovelCurrent'};
    const futureDays=futureRealmPurchaseDaysUntil(targetMs,cfg);
    const baseline=realmDailyValue(key);
    const manual=Math.max(0,Math.floor(n(ids[key],0)));
    const planned=futureDays*baseline*REALM_RUNS_PER_REFRESH;
    let perRun=realmYieldFor(resources,key);
    if(cfg.key==='s2' && Math.floor((pAt?.decimal??pAt?.level??n('charLevel',100)))<cfg.realmMaxLevel) perRun=0;
    return realmTopup(Math.max(0,Number(cost)||0),Math.max(0,Number(resources?.[key])||0),perRun,1+futureDays,manual+planned,baseline);
  }

function fixedTargetRouteFundableAt(plan,requestedDesired,targetMs,pEnd,cfg=activeCalcConfig()){
    if(!plan) return false;
    const pAt=projectCharacterTo(targetMs,cfg);
    const nonCharacterScore=Math.max(0,(Number(plan.score)||0)-characterScore(pEnd,cfg));
    if(nonCharacterScore+characterScore(pAt,cfg)<requestedDesired-1e-9) return false;
    if(cfg.key==='s1'){
      const caps=categoryCapsForCharacter(pAt.level,cfg);
      if((plan.skillLevels||[]).some(x=>x>caps.skill)) return false;
      if((plan.relicLevels||[]).some(x=>x>caps.relic)) return false;
      if((plan.fantoLevels||[]).some(x=>x>caps.fanto)) return false;
    }
    const base=projectedResourcesTo(targetMs,cfg);
    const total=Math.max(0,Math.floor(base.staminaNodes||0));
    const empty={ore:0,essence:0,sand:0,rolla:0,unassigned:0};
    const map=base.yields?.map||{};
    const allocationCandidates=[];
    if(!base.yields?.mapReady || total<=0){
      allocationCandidates.push({...empty,unassigned:total});
    }else if(staminaMode()==='auto'){
      for(const key of ['ore','essence','sand']) if((Number(map[key])||0)>0) allocationCandidates.push({...empty,[key]:total});
    }else{
      const key=staminaMode();
      allocationCandidates.push((Number(map[key])||0)>0?{...empty,[key]:total}:{...empty,unassigned:total});
    }
    if(!allocationCandidates.length) allocationCandidates.push({...empty,unassigned:total});
    for(const allocation of allocationCandidates){
      const resources=applyStaminaAllocation(base,allocation,cfg);
      if((Number(plan.treatCost)||0)>(Number(resources.treat)||0)+0.5) continue;
      if(resources.refinedTracked && (Number(plan.refinedCost)||0)>(Number(resources.refined)||0)+0.5) continue;
      const ore=realmTopupForMoment('ore',plan.oreCost,resources,targetMs,pAt,cfg);
      const essence=realmTopupForMoment('essence',plan.essenceCost,resources,targetMs,pAt,cfg);
      const sand=realmTopupForMoment('sand',plan.sandCost,resources,targetMs,pAt,cfg);
      if(ore.feasible&&essence.feasible&&sand.feasible) return true;
    }
    return false;
  }

function estimateTargetReachMoment(plan,resourceBlocked,requestedDesired,pEnd,cfg=activeCalcConfig()){
    if(!plan||resourceBlocked) return null;
    const now=Date.now(),end=cfg.end.getTime();
    if(end<=now) return null;
    if(fixedTargetRouteFundableAt(plan,requestedDesired,now,pEnd,cfg)) return now;
    if(!fixedTargetRouteFundableAt(plan,requestedDesired,end,pEnd,cfg)) return null;
    let lo=now,hi=end;
    for(let i=0;i<18 && hi-lo>60_000;i++){
      const mid=Math.floor((lo+hi)/2);
      if(fixedTargetRouteFundableAt(plan,requestedDesired,mid,pEnd,cfg)) hi=mid;
      else lo=mid+1;
    }
    return hi;
  }

let postTargetLastReachMs=NaN;

let postTargetLastCfg=null;

let postTargetLastPlan=null;

let postTargetLastPEnd=null;

function selectedPostTargetToolState(){
    const checked=document.querySelector('input[name="postTargetToolMode"]:checked');
    const staminaChecked=document.querySelector('input[name="postTargetStaminaMode"]:checked');
    const state={mode:checked?.value||'current',stamina:staminaChecked?.value||'current',ore:0,essence:0,sand:0};
    state.ore=clamp(Math.floor(Number($('postTargetOreDaily')?.value)||0),0,20);
    state.essence=clamp(Math.floor(Number($('postTargetEssenceDaily')?.value)||0),0,20);
    state.sand=clamp(Math.floor(Number($('postTargetSandDaily')?.value)||0),0,20);
    return state;
  }

function ensurePostTargetControls(){
    const host=$('postTargetGains');
    if(!host || host.dataset.controlsBound==='1') return;
    host.dataset.controlsBound='1';
    const saved=postTargetToolState();
    const mode=document.querySelector(`input[name="postTargetToolMode"][value="${saved.mode}"]`) || document.querySelector('input[name="postTargetToolMode"][value="current"]');
    if(mode) mode.checked=true;
    const staminaMode=document.querySelector(`input[name="postTargetStaminaMode"][value="${saved.stamina}"]`) || document.querySelector('input[name="postTargetStaminaMode"][value="current"]');
    if(staminaMode) staminaMode.checked=true;
    if($('postTargetOreDaily')) $('postTargetOreDaily').value=String(saved.ore);
    if($('postTargetEssenceDaily')) $('postTargetEssenceDaily').value=String(saved.essence);
    if($('postTargetSandDaily')) $('postTargetSandDaily').value=String(saved.sand);
    const refresh=()=>{
      const state=selectedPostTargetToolState();
      savePostTargetToolState(state);
      if($('postTargetCustom')) $('postTargetCustom').hidden=state.mode!=='custom';
      if(Number.isFinite(postTargetLastReachMs) && postTargetLastCfg && postTargetLastPlan && postTargetLastPEnd) renderPostTargetGains(postTargetLastReachMs,postTargetLastPlan,postTargetLastPEnd,postTargetLastCfg);
    };
    host.querySelectorAll('input[name="postTargetToolMode"]').forEach(el=>el.addEventListener('change',refresh));
    host.querySelectorAll('input[name="postTargetStaminaMode"]').forEach(el=>el.addEventListener('change',refresh));
    ['postTargetOreDaily','postTargetEssenceDaily','postTargetSandDaily'].forEach(id=>$(id)?.addEventListener('input',refresh));
    if($('postTargetCustom')) $('postTargetCustom').hidden=saved.mode!=='custom';
  }

function hidePostTargetGains(){
    const host=$('postTargetGains');
    if(host) host.hidden=true;
    postTargetLastReachMs=NaN;
    postTargetLastCfg=null;
    postTargetLastPlan=null;
    postTargetLastPEnd=null;
  }

function postTargetCarryAt(reached,plan,pEnd,cfg=activeCalcConfig()){
    const emptyCarry={ore:0,essence:0,sand:0,treat:0,hammers:0,knuckles:0,shovels:0,staminaUnused:0,valid:false,resourceSnapshot:null,oreTop:null,essenceTop:null,sandTop:null};
    if(!plan || !Number.isFinite(Number(reached))) return emptyCarry;
    const pAt=projectCharacterTo(reached,cfg);
    const base=projectedResourcesTo(reached,cfg);
    const total=Math.max(0,Math.floor(base.staminaNodes||0));
    const empty={ore:0,essence:0,sand:0,rolla:0,unassigned:0};
    const map=base.yields?.map||{};
    const allocationCandidates=[];
    if(!base.yields?.mapReady || total<=0){
      allocationCandidates.push({...empty,unassigned:total});
    }else if(staminaMode()==='auto'){
      for(const key of ['ore','essence','sand']) if((Number(map[key])||0)>0) allocationCandidates.push({...empty,[key]:total});
    }else{
      const key=staminaMode();
      allocationCandidates.push((Number(map[key])||0)>0?{...empty,[key]:total}:{...empty,unassigned:total});
    }
    if(!allocationCandidates.length) allocationCandidates.push({...empty,unassigned:total});
    for(const allocation of allocationCandidates){
      const resources=applyStaminaAllocation(base,allocation,cfg);
      if((Number(plan.treatCost)||0)>(Number(resources.treat)||0)+0.5) continue;
      if(resources.refinedTracked && (Number(plan.refinedCost)||0)>(Number(resources.refined)||0)+0.5) continue;
      const oreTop=realmTopupForMoment('ore',plan.oreCost,resources,reached,pAt,cfg);
      const essenceTop=realmTopupForMoment('essence',plan.essenceCost,resources,reached,pAt,cfg);
      const sandTop=realmTopupForMoment('sand',plan.sandCost,resources,reached,pAt,cfg);
      if(!(oreTop.feasible&&essenceTop.feasible&&sandTop.feasible)) continue;
      return {
        ore:Math.max(0,(Number(resources.ore)||0)-(Number(plan.oreCost)||0)),
        essence:Math.max(0,(Number(resources.essence)||0)-(Number(plan.essenceCost)||0)),
        sand:Math.max(0,(Number(resources.sand)||0)-(Number(plan.sandCost)||0)),
        treat:Math.max(0,(Number(resources.treat)||0)-(Number(plan.treatCost)||0)),
        hammers:Math.max(0,Math.floor(Number(oreTop.bankedRemaining)||0)+Math.floor(Number(oreTop.sparePurchasedRuns)||0)),
        knuckles:Math.max(0,Math.floor(Number(essenceTop.bankedRemaining)||0)+Math.floor(Number(essenceTop.sparePurchasedRuns)||0)),
        shovels:Math.max(0,Math.floor(Number(sandTop.bankedRemaining)||0)+Math.floor(Number(sandTop.sparePurchasedRuns)||0)),
        staminaUnused:Math.max(0,Number(resources.staminaUnused)||0),
        valid:true,
        resourceSnapshot:resources,
        oreTop,essenceTop,sandTop
      };
    }
    return emptyCarry;
  }

function postTargetRawGains(reached,cfg,state=selectedPostTargetToolState(),staminaCarry=0){
    const end=cfg.end.getTime();
    const now=Date.now();
    const start=Math.max(now,Math.min(Number(reached)||end,end));
    if(!(end>start)) return {ore:0,essence:0,sand:0,treat:0,resets:0,resourceHours:0};
    const wallHours=(end-start)/3_600_000;
    const resets=countFuturePacificResets(start,end);
    const resourceHours=wallHours+(2*resets);
    const shop=dailyShopMaterialEstimate(cfg,resets);
    const gains={
      ore:Math.max(0,n('oreRate',0))*resourceHours+Math.max(0,Number(shop?.total?.ore)||0),
      essence:Math.max(0,n('essenceRate',0))*resourceHours+Math.max(0,Number(shop?.total?.essence)||0),
      sand:Math.max(0,n('sandRate',0))*resourceHours+Math.max(0,Number(shop?.total?.sand)||0),
      treat:Math.max(0,n('treatRate',0))*resourceHours+Math.max(0,Number(shop?.total?.treat)||0),
      resets,resourceHours
    };
    // Keep post-target Stamina behavior consistent with the live planner. Auto banks surplus in Ore.
    const yields=automaticResourceYields(n('charLevel',cfg.key==='s2'?100:122),cfg);
    // Stamina regenerates from real elapsed time; daily 2h idle boosts do not create Stamina.
    const staminaPerNode=Math.max(1,Number(yields.staminaPerNode)||5);
    const regenPerHour=5;
    const preWallHours=Math.max(0,(start-now)/3_600_000);
    const fullWallHours=Math.max(0,(end-now)/3_600_000);
    const preGenerated=Math.max(0,Math.floor(preWallHours*regenPerHour));
    const fullGenerated=Math.max(0,Math.floor(fullWallHours*regenPerHour));
    const preNodes=Math.floor(preGenerated/staminaPerNode);
    const fullNodes=Math.floor(fullGenerated/staminaPerNode);
    const staminaNodes=Math.max(0,fullNodes-preNodes);
    const currentMode=$('staminaMode')?.value||'auto';
    const requested=state?.stamina||'current';
    const destination=requested==='current'
      ? (currentMode==='auto'?'ore':currentMode)
      : requested;
    const map=yields.map||{};
    if(['ore','essence','sand'].includes(destination)) gains[destination]+=staminaNodes*Math.max(0,Number(map[destination])||0);
    gains.staminaNodes=staminaNodes;
    gains.staminaDestination=destination;
    return gains;
  }

let optimizerJobSequence=0;

let optimizerUpdateGeneration=0;

// COOPERATIVE_OPTIMIZER_GENERATION_V1
let activeOptimizerJob=null;

let queuedGoalOptimizerJob=null;

// REGULAR_GOAL_PROGRESS_V1

  /* CALC_SETTLE_PROBE_V1
     Exposes a deterministic "calculator fully settled" signal for automation and tests,
     so they can await a completed render instead of guessing from DOM quiet windows that
     can resolve while a cooperative optimizer search is still in flight. Every scheduled
     or direct updateCalculator() run is counted; the probe reports settled only after all
     of them have completed (superseded pending timers count as settled). */
let calculatorRunsScheduled=0;

let calculatorRunsSettled=0;

if(typeof window!=='undefined') window.__sxsCalculatorSettledV1=()=>calculatorRunsScheduled===calculatorRunsSettled;

function runCalculatorUpdateSettled(){
    calculatorRunsScheduled++;
    return Promise.resolve(updateCalculator())
      .catch(err=>{ if(!(err instanceof OptimizerCancelledError)) console.error('CALC_SETTLE_PROBE_V1: update failed',err); })
      .finally(()=>{ calculatorRunsSettled++; });
  }

function queueRegularGoalOptimizerProgress(){
    const cfg=activeCalcConfig();
    const historical=Math.max(0,Math.floor(n('historicalStars',0)));
    const target=Math.max(cfg.starBase+historical,Math.floor(n('targetStars',cfg.key==='s2'?680:200)));
    const job=beginOptimizerJob(target);
    queuedGoalOptimizerJob=job;
    const detail=$('optimizerProgressDetail');
    if(detail) detail.textContent='Preparing goal calculation';
    return job;
  }

function ensureOptimizerProgressPanel(){
    let panel=$('optimizerProgressPanel');
    if(panel) return panel;
    panel=document.createElement('div');
    panel.id='optimizerProgressPanel';
    panel.className='optimizerProgressPanel';
    panel.hidden=true;
    panel.setAttribute('role','status');
    panel.setAttribute('aria-live','polite');
    panel.innerHTML=`
      <div class="optimizerProgressSpinner" aria-hidden="true"></div>
      <div class="optimizerProgressCopy">
        <strong id="optimizerProgressTitle">Calculating…</strong>
        <span id="optimizerProgressDetail">Searching upgrade combinations</span>
        <small id="optimizerProgressElapsed">0.0s elapsed</small>
      </div>
      <button id="optimizerCancelButton" type="button">Cancel</button>`;
    document.body.appendChild(panel);
    $('optimizerCancelButton')?.addEventListener('click',()=>{
      const job=activeOptimizerJob;
      if(!job||job.cancelled) return;
      job.cancelled=true;
      const title=$('optimizerProgressTitle');
      const detail=$('optimizerProgressDetail');
      if(title) title.textContent='Cancelling…';
      if(detail) detail.textContent='Stopping at the next optimizer checkpoint';
      const btn=$('optimizerCancelButton');
      if(btn){btn.disabled=true;btn.textContent='Cancelling';}
    });
    return panel;
  }

function beginOptimizerJob(targetStars){
    if(activeOptimizerJob) activeOptimizerJob.cancelled=true;
    const panel=ensureOptimizerProgressPanel();
    const job={id:++optimizerJobSequence,cancelled:false,started:performance.now(),timer:0,targetStars:Number(targetStars)||0};
    activeOptimizerJob=job;
    panel.dataset.jobId=String(job.id);
    panel.hidden=false;
    panel.classList.remove('optimizerCancelled','optimizerError');
    const days=finishEarlyDaysValue();
    const title=$('optimizerProgressTitle'),detail=$('optimizerProgressDetail'),elapsed=$('optimizerProgressElapsed'),btn=$('optimizerCancelButton');
    if(title) title.textContent=`Calculating ${fmt(job.targetStars)} Primostars…`;
    if(detail) detail.textContent=days>0?`Finish Early: ${days} day${days===1?'':'s'} · searching upgrade combinations`:'Searching upgrade combinations';
    if(elapsed) elapsed.textContent='0.0s elapsed';
    if(btn){btn.disabled=false;btn.textContent='Cancel';}
    job.timer=setInterval(()=>{
      if(activeOptimizerJob!==job) return;
      const seconds=(performance.now()-job.started)/1000;
      if(elapsed) elapsed.textContent=`${seconds.toFixed(seconds<10?1:0)}s elapsed`;
    },100);
    return job;
  }

function finishOptimizerJob(job,state='done'){
    if(!job) return;
    if(job.timer) clearInterval(job.timer);
    if(activeOptimizerJob!==job) return;
    activeOptimizerJob=null;
    const panel=ensureOptimizerProgressPanel();
    const title=$('optimizerProgressTitle'),detail=$('optimizerProgressDetail'),btn=$('optimizerCancelButton');
    if(state==='cancelled'){
      panel.classList.add('optimizerCancelled');
      if(title) title.textContent='Calculation cancelled';
      if(detail) detail.textContent='Previous completed result kept.';
      if(btn){btn.disabled=true;btn.textContent='Cancelled';}
      const id=String(job.id);
      setTimeout(()=>{ if(panel.dataset.jobId===id) panel.hidden=true; },1200);
      return;
    }
    if(state==='error'){
      panel.classList.add('optimizerError');
      if(title) title.textContent='Calculation stopped';
      if(detail) detail.textContent='The optimizer hit an unexpected error.';
      if(btn){btn.disabled=true;btn.textContent='Close';}
      const id=String(job.id);
      setTimeout(()=>{ if(panel.dataset.jobId===id) panel.hidden=true; },1800);
      return;
    }
    panel.hidden=true;
  }

// Most checkpoints only inspect the clock/cancellation flag. Return a promise only
  // when yielding: awaiting an already-resolved promise in each hot-loop iteration
  // needlessly allocates promises and drains the microtask queue without painting.
function createOptimizerCheckpoint(job){
    let lastYield=performance.now();
    return (force=false)=>{
      if(!job) return;
      if(job.cancelled) throw new OptimizerCancelledError();
      const now=performance.now();
      if(force || now-lastYield>=8){
        // OPTIMIZER_CANCEL_TIMER_V3: refresh elapsed time at the same cooperative checkpoints
        // that service click/input events. This keeps the timer honest and gives Cancel a
        // browser turn even when the setInterval callback was delayed by optimizer work.
        const elapsed=$('optimizerProgressElapsed');
        const seconds=(performance.now()-job.started)/1000;
        if(elapsed) elapsed.textContent=`${seconds.toFixed(seconds<10?1:0)}s elapsed`;
        return new Promise(resolve=>setTimeout(resolve,0)).then(()=>{
          lastYield=performance.now();
          if(job.cancelled) throw new OptimizerCancelledError();
        });
      }
    };
  }

// Find the lowest-shortfall score-capable route for the ORIGINAL requested target.
function diagnoseTarget(baseScore,desired,p,resources,cfg=activeCalcConfig(),ctx=null){
    return searchPlans(baseScore,desired,p,resources,cfg,ctx).diagnostic;
  }

function setEssenceBalance(id,cost,resources){ setRawRemaining(id,cost,resources.essence); }

function confirmCurrentSeasonSnapshot(){
    const cfg=activeCalcConfig();
    // A persisted 200-ish S1 target is not useful in S2. Change it only at explicit rollover confirmation;
    // preserve any target the user already raised for S2.
    if(cfg.key==='s2' && $('targetStars')){
      const target=Number($('targetStars').value);
      if(!Number.isFinite(target) || target<=480) $('targetStars').value=String(S2_SCORING_START_DEFAULTS.targetStars);
    }
    snapshotSeason=cfg.key; snapshotAtMs=Date.now(); snapshotCarry={ore:0,essence:0,sand:0,treat:0,exp:0}; snapshotStateLoaded=true;
    saveState(); renderCalculatorSeasonChrome(cfg); runCalculatorUpdateSettled();
  }

function updateGearLockUI(){
    const btn=$('gearLockButton');
    if(!btn) return;
    btn.classList.toggle('locked',gearLocked);
    btn.setAttribute('aria-pressed', String(gearLocked));
    btn.textContent = gearLocked ? '🔒 Gear Locked' : '🔓 Lock Gear';
    $('gearLockNote').textContent = gearLocked
      ? 'Gear is locked at the current five slot levels. The optimizer cannot recommend any Gear increase; it must solve the target through other available progression.'
      : 'Gear is unlocked. The optimizer can raise Gear when it is the most resource-efficient path.';
  }

let maxAchievableState={fingerprint:'',routine:null,hard:null};

function maxAchievableFingerprint(){
    return JSON.stringify({
      inputs:INPUT_IDS.filter(id=>id!=='targetStars').map(id=>$(id)?.value??''),
      checks:CHECK_IDS.map(id=>!!$(id)?.checked),
      gearLocked,snapshotSeason
    });
  }

function resetMaxAchievableUi(){
    maxAchievableState={fingerprint:'',routine:null,hard:null};
    const btn=$('findMaxStars'),status=$('maxAchievableStatus');
    if(btn){btn.disabled=false;btn.textContent='Find max achievable';}
    if(status) status.textContent='Shows the maximum with your selected daily Realm plan and the hard maximum using all remaining Realm capacity.';
    const finishBtn=$('finishEarlyMax'),finishHint=$('finishEarlyMaxHint');
    if(finishBtn?.dataset.maxLocked==='true'){
      delete finishBtn.dataset.maxLocked;
      finishBtn.disabled=false;
      finishBtn.title='Find the maximum half-day finish-early value that still reaches the selected Primostar target';
    }
    if(finishHint) finishHint.hidden=true;
  }

function lockFinishEarlyMaxForPurchasePlan(){
    const btn=$('finishEarlyMax'),hint=$('finishEarlyMaxHint');
    if(!btn) return;
    btn.dataset.maxLocked='true';
    btn.disabled=true;
    btn.textContent='Max';
    btn.title='Current purchase plan sets this Max. Increase Material Realm purchases/day to finish earlier.';
    btn.removeAttribute('aria-busy');
    if(hint){
      hint.textContent='Current purchase plan sets this Max. Increase Material Realm purchases/day to finish earlier.';
      hint.hidden=false;
    }
  }

function buildMaxAchievableSnapshot(){
    const cfg=activeCalcConfig();
    if(snapshotSeason!==cfg.key) return null;
    const p=projectCharacter(cfg);
    const upgradeP=projectCharacterTo(upgradeFinishCutoffMs(cfg),cfg);
    p.upgradeCapLevel=upgradeP.level;p.upgradeCapPct=upgradeP.pct;
    const currentCharacter=p.current||characterSnapshot(cfg);
    if(cfg.key==='s2' && currentCharacter.level<S2_PLANNER_START_LEVEL) return null;
    const projectedResourceTotals=projectedResources(p.hours,cfg);
    const baseResources=projectedResourceTotals;
    const currentCaps=categoryInputCapsForCharacter(currentCharacter.level,cfg);
    const normalInputFloor=100;
    const relicInputFloor=10;
    const gearState=gearStateFromUser(cfg,currentCaps.gear,cfg.key==='s2'?130:143);
    const gear=gearState.levels;
    const skillState=categoryStateFromUser('skillLevel','exactSkillLevels',8,normalInputFloor,currentCaps.skill,cfg.scoreFloor,cfg.weights.skill,cfg.key==='s2'?130:122);
    const relicState=categoryStateFromUser('relicLevel','exactRelicLevels',20,relicInputFloor,currentCaps.relic,cfg.relicFloor,cfg.weights.relic,cfg.key==='s2'?13:13);
    const fantoState=categoryStateFromUser('fantomonLevel','exactFantoLevels',4,normalInputFloor,currentCaps.fanto,cfg.scoreFloor,cfg.weights.fanto,cfg.key==='s2'?130:130);
    const baselineScore=characterScore(p,cfg)+gearScore(gear,cfg)+skillState.score+relicState.score+fantoState.score;
    const historical=Math.max(0,Math.floor(n('historicalStars',0)));
    return {cfg,p,baseResources,baselineScore,historical,baselineStars:historical+cfg.starBase+Math.floor(baselineScore/cfg.scorePerStar)};
  }

function findMaxAchievableStars(){
    const btn=$('findMaxStars'),status=$('maxAchievableStatus');
    if(!btn||!status) return;
    const fingerprint=maxAchievableFingerprint();
    if(maxAchievableState.fingerprint===fingerprint && Number.isFinite(maxAchievableState.hard)){
      const hardTarget=maxAchievableState.hard;
      resetFinishEarlyForGoalChange();
      $('targetStars').value=String(hardTarget);
      resetMaxAchievableUi();
      saveState();
      if($('optimizerSummary')) $('optimizerSummary').textContent='Updating goal…';
      queueRegularGoalOptimizerProgress();
      requestAnimationFrame(()=>scheduleCalculatorUpdate(0));
      return;
    }
    const snap=buildMaxAchievableSnapshot();
    if(!snap){ status.textContent='Confirm the current-season snapshot first.'; return; }
    btn.disabled=true;btn.textContent='Calculating…';status.textContent='Searching reachable Primostar breakpoints…';
    setTimeout(()=>{
      try{
        const solveCache=new Map();
        const solveStars=stars=>{
          const key=Math.max(snap.baselineStars,Math.floor(stars));
          if(solveCache.has(key)) return solveCache.get(key);
          const desired=Math.max(0,(key-snap.historical-snap.cfg.starBase)*snap.cfg.scorePerStar);
          const result=solveTargetWithAutoStamina(snap.baselineScore,desired,snap.p,snap.baseResources,snap.cfg);
          solveCache.set(key,result);
          return result;
        };
        const hardFundable=stars=>!!solveStars(stars).plan;
        const routineFundable=stars=>{
          const plan=solveStars(stars).plan;
          return !!plan && candidateRealmStage(plan)<=1;
        };
        const upperLimit=snap.cfg.key==='s1'?1200:5000;
        let hardLo=snap.baselineStars,hardHi=Math.max(hardLo+1,Math.floor(n('targetStars',hardLo))+1),step=Math.max(8,hardHi-hardLo);
        while(hardHi<upperLimit && hardFundable(hardHi)){
          hardLo=hardHi;step*=2;hardHi=Math.min(upperLimit,hardHi+step);
        }
        if(hardHi===upperLimit && hardFundable(hardHi)) hardLo=hardHi;
        else{
          let lo=hardLo+1,hi=hardHi-1;
          while(lo<=hi){const mid=(lo+hi)>>1;if(hardFundable(mid)){hardLo=mid;lo=mid+1;}else hi=mid-1;}
        }
        const hard=hardLo;
        let routineLo=snap.baselineStars,routineHi=hard;
        while(routineLo<routineHi){
          const mid=Math.ceil((routineLo+routineHi)/2);
          if(routineFundable(mid)) routineLo=mid; else routineHi=mid-1;
        }
        const routine=routineLo;
        maxAchievableState={fingerprint,routine,hard};
        status.innerHTML=`Selected daily plan max: <strong>${fmt(routine)}</strong> · Hard Realm-cap max: <strong>${fmt(hard)}</strong>`;
        btn.disabled=false;btn.textContent=`Use ${fmt(hard)} target`;
      }catch(err){
        console.error(err);resetMaxAchievableUi();status.textContent='Could not calculate the ceiling from the current inputs.';
      }
    },0);
  }

/* FINISH_EARLY_MAX_FAST_NOEXTRA_V3
     Max answers: how early can the selected target be secured WITHOUT any additional
     Realm purchases beyond the user's already-configured daily Realm plan. Configured
     Shop Buyouts/day and configured daily Realm purchases remain part of the user's normal
     projection; candidate-invented extra Realm refreshes are not allowed.

     This uses the same exact owned/projected-pool feasibility proof already used inside
     searchPlans(), but skips the expensive nested optimizer scan. Each half-day probe only
     builds the reachable option lists and checks the independently affordable maxima for
     Gear / Skills / Relics / Fantomons across the calculator's legal Stamina strategies.
     After binary search finds the final half-day value, the full optimizer runs ONCE to
     render the normal result card. */
function finishEarlyNoExtraPossible(){
    const cfg=activeCalcConfig();
    if(snapshotSeason!==cfg.key) return false;
    if(cfg.key==='s2'){
      const required=s2RequiredPlannerInputs();
      if(!required.hasBed||!required.hasAllCart) return false;
    }
    const p=projectCharacterTo(upgradeFinishCutoffMs(cfg),cfg);
    if(cfg.key==='s2' && p.level<=cfg.scoreFloor) return false;
    p.upgradeCapLevel=p.level;
    p.upgradeCapPct=p.pct;
    const currentCharacter=p.current||characterSnapshot(cfg);
    const currentCaps=categoryInputCapsForCharacter(currentCharacter.level,cfg);
    const gearState=gearStateFromUser(cfg,currentCaps.gear,cfg.key==='s2'?130:143);
    const skillState=categoryStateFromUser('skillLevel','exactSkillLevels',8,100,currentCaps.skill,cfg.scoreFloor,cfg.weights.skill,cfg.key==='s2'?130:122);
    const relicState=categoryStateFromUser('relicLevel','exactRelicLevels',20,10,currentCaps.relic,cfg.relicFloor,cfg.weights.relic,cfg.key==='s2'?13:13);
    const fantoState=categoryStateFromUser('fantomonLevel','exactFantoLevels',4,100,currentCaps.fanto,cfg.scoreFloor,cfg.weights.fanto,cfg.key==='s2'?130:130);
    const baselineScore=characterScore(p,cfg)+gearScore(gearState.levels,cfg)+skillState.score+relicState.score+fantoState.score;
    const historical=Math.max(0,Math.floor(n('historicalStars',0)));
    const targetStars=Math.max(cfg.starBase+historical,Math.floor(n('targetStars',cfg.key==='s2'?680:200)));
    const desired=Math.max(0,(targetStars-historical-cfg.starBase)*cfg.scorePerStar);
    if(baselineScore>=desired-1e-9) return true;
    const ctx=createPlanningContext(baselineScore,desired,p,cfg);
    const baseResources=projectedResources(p.hours,cfg);
    const total=Math.max(0,Math.floor(baseResources.staminaNodes||0));
    const map=baseResources.yields?.map||{};
    const empty={ore:0,essence:0,sand:0,rolla:0,unassigned:0};
    const allocations=[];
    if(!baseResources.yields?.mapReady||total<=0){
      allocations.push({...empty,unassigned:total});
    }else if(staminaMode()==='auto'){
      for(const key of ['ore','essence','sand']){
        if((Number(map[key])||0)>0) allocations.push({...empty,[key]:total});
      }
    }else{
      const key=staminaMode();
      allocations.push((Number(map[key])||0)>0?{...empty,[key]:total}:{...empty,unassigned:total});
    }
    if(!allocations.length) allocations.push({...empty,unassigned:total});
    const highestAffordable=(options,budget,costKey='cost',secondaryBudget=Infinity,secondaryKey='')=>{
      let best=Array.isArray(options)&&options.length?options[0]:null;
      for(const option of (options||[])){
        const primary=Math.max(0,Number(option?.[costKey])||0);
        const secondary=secondaryKey?Math.max(0,Number(option?.[secondaryKey])||0):0;
        if(primary<=budget+0.5 && secondary<=secondaryBudget+0.5) best=option;
        else if(primary>budget+0.5) break;
      }
      return best;
    };
    for(const allocation of allocations){
      const resources=applyStaminaAllocation(baseResources,allocation,cfg);
      const refinedBudget=resources.refinedTracked?Math.max(0,Number(resources.refined)||0):Infinity;
      const go=highestAffordable(ctx.gearOptions,plannedToolAcquisitionSupply('ore',resources,cfg),'oreCost',refinedBudget,'refinedCost');
      const so=highestAffordable(ctx.cats.skillOptions,plannedToolAcquisitionSupply('essence',resources,cfg));
      const ro=highestAffordable(ctx.cats.relicOptions,plannedToolAcquisitionSupply('sand',resources,cfg));
      const fo=highestAffordable(ctx.cats.fantoOptions,Math.max(0,Number(resources.treat)||0));
      if(!go||!so||!ro||!fo) continue;
      const maxScore=ctx.charScore+(Number(go.score)||0)+(Number(so.score)||0)+(Number(ro.score)||0)+(Number(fo.score)||0);
      if(maxScore>=desired-1e-9) return true;
    }
    return false;
  }

async function findMaxFinishEarly(){
    const btn=$('finishEarlyMax'),input=$('finishEarlyDays');
    if(!btn||!input||btn.disabled) return;
    const cfg=activeCalcConfig();
    const original=String(input.value||'0');
    const halfDayMs=12*60*60*1000;
    const maxHalfSteps=Math.max(0,Math.floor((cfg.end.getTime()-Date.now())/halfDayMs));
    const targetStars=Math.max(0,Math.floor(n('targetStars',cfg.key==='s2'?680:200)));
    btn.disabled=true;
    btn.textContent='…';
    btn.setAttribute('aria-busy','true');
    clearTimeout(calculatorUpdateTimer);
    calculatorUpdateTimer=null;
    // COOPERATIVE_FINISH_EARLY_MAX_V4: Max participates in the same visible,
    // cancellable job system as the full optimizer. The previous binary search ran all
    // feasibility probes synchronously, which could prevent the progress panel from ever
    // painting and trigger Chrome's Page Unresponsive dialog on demanding targets.
    const optimizerJob=beginOptimizerJob(targetStars);
    const checkpoint=createOptimizerCheckpoint(optimizerJob);
    const title=$('optimizerProgressTitle');
    const detail=$('optimizerProgressDetail');
    if(title) title.textContent=`Finding max Finish Early for ${fmt(targetStars)} Primostars…`;
    if(detail) detail.textContent='Checking the full-season no-extra-purchase route';
    try{
      // Force a browser turn before the very first feasibility probe so the panel paints.
      await checkpoint(true);
      input.value='0';
      const fullSeasonPossible=finishEarlyNoExtraPossible();
      await checkpoint(true);
      if(!fullSeasonPossible){
        input.value=original;
        finishOptimizerJob(optimizerJob,'done');
        await runCalculatorUpdateSettled();
        lockFinishEarlyMaxForPurchasePlan();
        return;
      }
      let lo=0,hi=maxHalfSteps,probe=0;
      const estimatedProbes=Math.max(1,Math.ceil(Math.log2(Math.max(2,maxHalfSteps+1))));
      while(lo<hi){
        if(optimizerJob.cancelled) throw new OptimizerCancelledError();
        const mid=Math.ceil((lo+hi)/2);
        const days=mid/2;
        input.value=String(days);
        probe++;
        if(detail) detail.textContent=`Testing ${days} days early · probe ${probe}/${estimatedProbes}`;
        // Paint the current candidate before evaluating it, then yield again afterward so
        // Cancel/input events are serviced between every binary-search probe.
        await checkpoint(true);
        const possible=finishEarlyNoExtraPossible();
        await checkpoint(true);
        if(possible) lo=mid;
        else hi=mid-1;
      }
      if(optimizerJob.cancelled) throw new OptimizerCancelledError();
      input.value=String(lo/2);
      resetMaxAchievableUi();
      saveState();
      if(detail) detail.textContent=`Max found: ${lo/2} days early · running final plan`;
      await checkpoint(true);
      finishOptimizerJob(optimizerJob,'done');
      // One full cooperative solve only, after the cheap binary search finds the cutoff.
      await runCalculatorUpdateSettled();
      btn.title=lo>0
        ? `Maximum no-extra-purchase finish-early value: ${lo/2} days. Uses your configured Realm/Shop routine but no additional recommended Realm purchases.`
        : 'The current target needs the full remaining season without extra Realm purchases.';
    }catch(err){
      input.value=original;
      if(err instanceof OptimizerCancelledError || optimizerJob.cancelled){
        finishOptimizerJob(optimizerJob,'cancelled');
        // Keep the previously completed result. Do not immediately launch another heavy solve.
        saveState();
      }else{
        console.error('COOPERATIVE_FINISH_EARLY_MAX_V4',err);
        finishOptimizerJob(optimizerJob,'error');
        btn.title='Could not calculate the no-extra-purchase maximum from the current inputs.';
      }
    }finally{
      if(btn.dataset.maxLocked!=='true') btn.disabled=false;
      btn.textContent='Max';
      btn.removeAttribute('aria-busy');
    }
  }

function smartBalanceRawCeiling(baseScore,p,baseResources,cfg,historical){
    // Large structural target only expands Gear options; actual affordability below is
    // still limited strictly by projected raw resources and verified progression gates.
    const ctx=createPlanningContext(baseScore,1_000_000,p,cfg);
    const total=Math.max(0,Math.floor(baseResources?.staminaNodes||0));
    const empty={ore:0,essence:0,sand:0,rolla:0,unassigned:0};
    const map=baseResources?.yields?.map||{};
    const allocations=[];
    if(total<=0 || !baseResources?.yields?.mapReady){
      allocations.push({...empty,unassigned:total});
    }else if(staminaMode()==='auto'){
      for(const key of ['ore','essence','sand']) if((Number(map[key])||0)>0) allocations.push({...empty,[key]:total});
      if(!allocations.length) allocations.push({...empty,unassigned:total});
    }else{
      allocations.push(allocateStaminaForPlan(null,baseResources,cfg,p));
    }
    let best=null;
    for(const allocation of allocations){
      const resources=applyStaminaAllocation(baseResources,allocation,cfg);
      const refinedBudget=resources.refinedTracked?Math.max(0,Number(resources.refined)||0):Infinity;
      const go=smartBalanceHighestAffordable(ctx.gearOptions,Math.max(0,Number(resources.ore)||0),'oreCost',refinedBudget,'refinedCost');
      const so=smartBalanceHighestAffordable(ctx.cats.skillOptions,Math.max(0,Number(resources.essence)||0));
      const ro=smartBalanceHighestAffordable(ctx.cats.relicOptions,Math.max(0,Number(resources.sand)||0));
      const fo=smartBalanceHighestAffordable(ctx.cats.fantoOptions,Math.max(0,Number(resources.treat)||0));
      if(!go||!so||!ro||!fo) continue;
      const score=ctx.charScore+go.score+so.score+ro.score+fo.score;
      const stars=Math.max(0,Math.floor(historical))+cfg.starBase+Math.floor(score/cfg.scorePerStar);
      const candidate={stars,score,allocation,resources};
      if(!best || candidate.stars>best.stars || (candidate.stars===best.stars && candidate.score>best.score)) best=candidate;
    }
    return best||{stars:Math.max(0,Math.floor(historical))+cfg.starBase+Math.floor(baseScore/cfg.scorePerStar),score:baseScore,allocation:{...empty,unassigned:total},resources:baseResources};
  }

let lastRequestedTargetStars=null;

let lastEffectiveTargetStars=null;

/* GOAL_SWITCH_CACHE_V3 · RESPONSIVE_GOAL_PREP_V1
     Changing Target Primostars does not change the account snapshot. Reuse exact target
     solutions while every non-target input remains identical. The old path eagerly built an
     informational raw-only ceiling with a synthetic 1,000,000-score target before the real
     solve; that synchronous structural expansion could freeze the main thread, leaving Cancel
     and the elapsed timer stuck during "Preparing goal calculation". Ceiling discovery now
     stays behind the explicit Find max achievable control instead of blocking normal goals. */
let goalSwitchCache={fingerprint:'',rawCeiling:null,solutions:new Map()};

function goalSwitchFingerprint(cfg,baseScore){
    return JSON.stringify({
      season:cfg.key,
      snapshotAtMs,
      gearLocked,
      baseScore:Math.round((Number(baseScore)||0)*1000)/1000,
      inputs:INPUT_IDS.filter(id=>id!=='targetStars').map(id=>$(id)?.value??''),
      checks:CHECK_IDS.map(id=>!!$(id)?.checked)
    });
  }

function goalSwitchPlanningState(baseScore,p,baseResources,cfg,historical){
    const fingerprint=goalSwitchFingerprint(cfg,baseScore);
    if(goalSwitchCache.fingerprint===fingerprint) return goalSwitchCache;
    // RESPONSIVE_GOAL_PREP_V1: rawCeiling is informational only. Do not synchronously
    // expand a synthetic million-score planning context before the requested goal solve.
    goalSwitchCache={fingerprint,rawCeiling:null,solutions:new Map()};
    return goalSwitchCache;
  }

/* S2_REQUIRED_INPUT_GUARD_V1
     Avoid launching the expensive target search from an empty production snapshot.
     Saved materials and Material Realm purchases are allowed to remain zero, but the
     S2 optimizer needs real Bed EXP plus all four Cart/hr production rates. */
function s2RequiredPlannerInputs(){
    const bed=Math.max(0,parseCompactNumber($('bedExp')?.value,0));
    const cartInputs=[['oreRate','Raw Ore Cart/hr'],['essenceRate','Skill Essence Cart/hr'],['sandRate','Chrono Sand Cart/hr'],['treatRate','Fantomon Treats Cart/hr']];
    const cartRates=cartInputs.map(([id])=>Math.max(0,parseCompactNumber($(id)?.value,0)));
    const missingCart=cartInputs.filter((_,i)=>cartRates[i]<=0).map(([,label])=>label);
    return {bed,cartRates,missingCart,hasBed:bed>0,hasAllCart:missingCart.length===0};
  }

async function updateCalculator(){
    if($('resultStamina')) $('resultStamina').hidden=true;
    // Clamp impossible manual values before any expensive solve starts.
    syncFinishEarlyInputLimit(activeCalcConfig(),true);
    const updateGeneration=++optimizerUpdateGeneration;
    const queuedGoalJob=queuedGoalOptimizerJob;
    if(queuedGoalJob===queuedGoalOptimizerJob) queuedGoalOptimizerJob=null;
    // Any newer edit supersedes an older in-flight solve, except the goal job intentionally
    // queued by the target control so its already-painted progress panel can be reused.
    if(activeOptimizerJob && activeOptimizerJob!==queuedGoalJob) activeOptimizerJob.cancelled=true;
    const perfStarted=performance.now();
    {const _tm=$('targetMessage');if(_tm){_tm.hidden=true;_tm.classList.remove('warning','danger','caution');}}
    const cfg=activeCalcConfig();
    if(queuedGoalJob){
      // REGULAR_GOAL_PROGRESS_V1: target-button handlers create the job before scheduling
      // this update, giving the browser a full paint turn before any calculator work begins.
      await new Promise(resolve=>setTimeout(resolve,0));
      if(queuedGoalJob.cancelled){ finishOptimizerJob(queuedGoalJob,'cancelled'); return; }
    }
    if(renderCalculatorSeasonChrome(cfg)){
      if(queuedGoalJob) finishOptimizerJob(queuedGoalJob,'done');
      clearCalcForRollover(cfg); return;
    }
    let p=null;
    if(cfg.key==='s2'){
      const required=s2RequiredPlannerInputs();
      // Bed EXP is the only production input required for Character level projection.
      if(!required.hasBed){ if(queuedGoalJob) finishOptimizerJob(queuedGoalJob,'done'); clearS2ForRequiredPlannerInputs(cfg,required); return; }
      p=projectCharacter(cfg);
      // Do not run the full Primostar/material optimizer until every Cart rate exists.
      if(!required.hasAllCart){ if(queuedGoalJob) finishOptimizerJob(queuedGoalJob,'done'); clearS2ForRequiredPlannerInputs(cfg,required,p); return; }
    }
    if(!p) p=projectCharacter(cfg);
    const seasonEndP=p;
    p=projectCharacterTo(upgradeFinishCutoffMs(cfg),cfg);
    if(cfg.key==='s2' && p.level<=cfg.scoreFloor){ clearS2ProjectedAtFloor(cfg,p); return; }
    const upgradeP=p;
    // Upgrade availability and score projection stop at the optional finish-early cutoff.
    p.upgradeCapLevel=upgradeP.level;
    p.upgradeCapPct=upgradeP.pct;
    const currentCharacter=p.current||characterSnapshot(cfg);
    const projectedResourceTotals=projectedResources(p.hours,cfg);
    renderRealmToolProjection(cfg);
    const baseResources=projectedResourceTotals;
    let resources=baseResources;
    const currentCaps=categoryInputCapsForCharacter(currentCharacter.level,cfg);
    // EXACT_LEVEL_AVERAGE_SYNC_V1: loaded/saved exact distributions also refresh the compact
    // averages and keep the exact editor visible before planner state is read.
    syncExactProgressionUi(cfg,currentCaps);
    const projectedCaps=optimizerCategoryCaps(p,cfg);
    const normalInputFloor=100;
    const relicInputFloor=10;
    const gearState=gearStateFromUser(cfg,currentCaps.gear,cfg.key==='s2'?130:143);
    const gear=gearState.levels;
    const skillState=categoryStateFromUser('skillLevel','exactSkillLevels',8,normalInputFloor,currentCaps.skill,cfg.scoreFloor,cfg.weights.skill,cfg.key==='s2'?130:122);
    const relicState=categoryStateFromUser('relicLevel','exactRelicLevels',20,relicInputFloor,currentCaps.relic,cfg.relicFloor,cfg.weights.relic,cfg.key==='s2'?13:13);
    const fantoState=categoryStateFromUser('fantomonLevel','exactFantoLevels',4,normalInputFloor,currentCaps.fanto,cfg.scoreFloor,cfg.weights.fanto,cfg.key==='s2'?130:130);
    const skill=skillState.avg,relic=relicState.avg,fanto=fantoState.avg;
    const exactChecks=[
      ['exactSkillLevels',8,normalInputFloor,currentCaps.skill,'Skills'],
      ['exactRelicLevels',20,relicInputFloor,currentCaps.relic,'Relics'],
      ['exactFantoLevels',4,normalInputFloor,currentCaps.fanto,'Fantomons'],
      ['exactGearLevels',5,normalInputFloor,currentCaps.gear,'Gear']
    ].map(([id,count,min,max,label])=>({label,...parseExactLevelInput(id,count,min,max)}));
    const exactStatus=$('exactProgressStatus');
    if(exactStatus){
      const invalid=exactChecks.filter(x=>x.active&&!x.valid),active=exactChecks.filter(x=>x.active&&x.valid);
      exactStatus.classList.toggle('inputWarning',invalid.length>0);exactStatus.classList.toggle('inputGood',invalid.length===0&&active.length>0);
      exactStatus.textContent=invalid.length?`Invalid exact input: ${invalid.map(x=>`${x.label} (${x.reason})`).join(' · ')}. Falling back to the averages above.`:active.length?`Using exact slot levels for: ${active.map(x=>x.label).join(', ')}.`:'Leave blank to keep using the balanced average model.';
    }
    const sharedParts={gear:gearScore(gear,cfg),skills:skillState.score,relics:relicState.score,fantomons:fantoState.score};
    const currentParts={character:characterScore(currentCharacter,cfg),...sharedParts};
    const projectedParts={character:characterScore(p,cfg),...sharedParts};
    const currentScoreNow=Object.values(currentParts).reduce((a,b)=>a+b,0);
    const baselineScore=Object.values(projectedParts).reduce((a,b)=>a+b,0);
    const historical=Math.max(0,Math.floor(n('historicalStars',0)));
    const targetStars=Math.max(cfg.starBase+historical,Math.floor(n('targetStars',cfg.key==='s2'?680:200)));
    const currentStarsNow=historical+cfg.starBase+Math.floor(currentScoreNow/cfg.scorePerStar);
    const baselineStars=historical+cfg.starBase+Math.floor(baselineScore/cfg.scorePerStar);
    const requestedDesired=Math.max(0,(targetStars-historical-cfg.starBase)*cfg.scorePerStar);
    // SMART_BALANCE_GOAL_STOP_V2: calculate raw-only upside for INFORMATION only.
    // The recommendation itself stops at the entered goal instead of spending surplus raw
    // materials merely because a higher raw-only ceiling exists.
    if(queuedGoalJob){
      const detail=$('optimizerProgressDetail');
      if(detail) detail.textContent=`Preparing ${fmt(targetStars)} Primostar goal`;
      await new Promise(resolve=>setTimeout(resolve,0));
      if(queuedGoalJob.cancelled){ finishOptimizerJob(queuedGoalJob,'cancelled'); return; }
    }
    const goalState=goalSwitchPlanningState(baselineScore,p,baseResources,cfg,historical);
    if(queuedGoalJob){
      await new Promise(resolve=>setTimeout(resolve,0));
      if(queuedGoalJob.cancelled){ finishOptimizerJob(queuedGoalJob,'cancelled'); return; }
    }
    const rawCeiling=goalState.rawCeiling;
    const projectedRawCeilingStars=Math.max(baselineStars,Math.floor(Number(rawCeiling?.stars)||baselineStars));
    const desired=requestedDesired;
    let solution=goalState.solutions.get(desired);
    if(!solution){
      const optimizerJob=(queuedGoalJob && !queuedGoalJob.cancelled)?queuedGoalJob:beginOptimizerJob(targetStars);
      const detail=$('optimizerProgressDetail');
      if(detail) detail.textContent=`Searching ${fmt(targetStars)} Primostar upgrade combinations`;
      try{
        solution=await solveTargetWithAutoStaminaCooperative(baselineScore,desired,p,baseResources,cfg,optimizerJob);
        if(updateGeneration!==optimizerUpdateGeneration || optimizerJob.cancelled) throw new OptimizerCancelledError();
        goalState.solutions.set(desired,solution);
        finishOptimizerJob(optimizerJob,'done');
      }catch(err){
        if(err instanceof OptimizerCancelledError){
          finishOptimizerJob(optimizerJob,'cancelled');
          return;
        }
        finishOptimizerJob(optimizerJob,'error');
        console.error('COOPERATIVE_OPTIMIZER_V1',err);
        return;
      }
    }else if(queuedGoalJob && activeOptimizerJob===queuedGoalJob){
      finishOptimizerJob(queuedGoalJob,'done');
    }
    let plan=solution.plan;
    const diagnosticPlan=solution.diagnostic||null;
    let resourceBlocked=false;
    resources=solution.resources;
    const staminaPlan=solution.allocation;
    // Strict sourcing still applies inside solveTargetWithAutoStamina/searchPlans:
    // raw first -> saved/already-planned Realm tools if needed -> extra purchases last.
    if(!plan&&diagnosticPlan){plan=diagnosticPlan;resourceBlocked=!diagnosticPlan.realmFeasible;}
    lastRequestedTargetStars=targetStars; lastEffectiveTargetStars=targetStars;
    $('seasonRemaining').textContent=formatRemaining(seasonEndP.hours);
    const pc=`Lv.${seasonEndP.level} · ${(seasonEndP.pct*100).toFixed(1)}%`;
    $('projectedCharacter').value=pc;
    const expEstimated=cfg.key==='s1'&&s1ProjectionUsesEstimatedExp(currentCharacter.level,seasonEndP.level);
    $('resultProjectedCharacter').textContent=`Lv.${p.level} (${(p.pct*100).toFixed(1)}%)`;
    $('projectionNote').textContent=expEstimated?`Exact reset timing (${nextResetLocalLabel()} locally) · late-S1 EXP uses the exact mined 1,833,196/level plateau.`:`Uses exact server resets (${nextResetLocalLabel()} on this device); the free 2-hour speed-up is counted only when its checkbox is enabled and an actual reset occurs.`;
    if($('levelSummary')) $('levelSummary').textContent=`Skills ${formatAverage(skill)} · Relics +${formatAverage(relic)} · Fantomons ${formatAverage(fanto)} · Gear avg ${(gear.reduce((a,b)=>a+b,0)/5).toFixed(0)}`;
    const allocation=staminaPlan||resources.staminaAllocation||{ore:0,essence:0,sand:0,rolla:0,unassigned:resources.staminaNodes||0};
    const added=resources.staminaAdded||{ore:0,essence:0,sand:0,rolla:0};
    renderStaminaCurrentPlan(allocation,added,resources);
    const oreStam=added.ore?` · Stamina +${fmtCompact(added.ore)}`:'';
    const essStam=added.essence?` · Stamina +${fmtCompact(added.essence)}`:'';
    const sandStam=added.sand?` · Stamina +${fmtCompact(added.sand)}`:'';
    $('oreProjected').textContent=`Projected: ${fmtCompact(resources.ore)}${oreStam}`;
    const displayedEssence=Number(resources.essence)||0;
    $('essenceProjected').textContent=`Projected: ${fmtCompact(displayedEssence)}${essStam}`;
    const displayedSand=Number(resources.sand)||0;
    $('sandProjected').textContent=`Projected: ${fmtCompact(displayedSand)}${sandStam}`;
    const savedSandEq=savedSandEquivalent();
    /* BLUE_SAND_LABEL_CLEANUP_V1: the planner still applies the canonical Blue Sand conversion internally; the UI no longer repeats the x5 note. */
    if($('sandEquivalentNow')) $('sandEquivalentNow').textContent=`Saved total: ${fmtCompact(savedSandEq)} basic-equivalent`;
    const savedTreatEq=savedTreatEquivalent();
    if($('treatEquivalentNow')) $('treatEquivalentNow').textContent=`Saved total: ${fmtCompact(savedTreatEq)} basic-equivalent · ≈${fmtCompact(savedTreatEq*TREAT_BASIC_EXP)} Fantomon EXP`;
    const displayedTreats=Number(resources.treat)||0;
    $('treatProjected').textContent=`Projected: ${fmtCompact(displayedTreats)} basic-eq.`;
    if($('shopRefreshEstimate')){
      const shop=resources.shopEstimate||dailyShopMaterialEstimate(cfg);
      const gain=(id,value)=>{const el=$(id);if(el)el.textContent=shop.refreshes?`+${fmtCompact(value)}/day`:'Off';};
      gain('shopGainOre',shop.perDay.ore);
      gain('shopGainEssence',shop.perDay.essence);
      gain('shopGainSand',shop.perDay.sand);
      gain('shopGainTreat',shop.perDay.treat);
      $('shopRefreshEstimate').textContent=shop.refreshes
        ? `+${fmtCompact(shop.perDay.ore)} Ore · +${fmtCompact(shop.perDay.essence)} Essence · +${fmtCompact(shop.perDay.sand)} Sand-eq · +${fmtCompact(shop.perDay.treat)} Treats / day`
        : 'Off';
      if($('shopRefreshEstimateNote')){
        const observed=shop.sampleCount>0;
        const perPage=shop.perBuyout||{};
        $('shopRefreshEstimateNote').textContent=shop.refreshes
          ? observed
            ? `Observed Charming Glance S2 average from ${shop.sampleCount} untouched shop pages · ${shop.days} future reset day${shop.days===1?'':'s'} counted · Sand-eq includes ${fmtCompact(shop.perDay.sandRegular)} regular + ${fmtCompact(shop.perDay.sandRare)} Rare Chrono Sand/day (Rare ×${SAND_BLUE_EQ}).`
            : `${shop.days} future reset day${shop.days===1?'':'s'} counted · current day excluded to avoid double-counting materials already entered under Saved.`
          : observed
            ? `Observed CG S2 sample n=${shop.sampleCount}: ${fmtCompact(perPage.ore)} Ore · ${fmtCompact(perPage.essence)} Essence · ${fmtCompact(perPage.sandRegular)} regular Sand + ${fmtCompact(perPage.sandRare)} Rare Sand · ${fmtCompact(perPage.treat)} Treats per page. Rare Sand counts ×${SAND_BLUE_EQ} toward Sand-equivalent.`
            : 'Set Shop Buyouts/day: 1 counts the base page with no refresh; 2 counts the base page plus one restock and a second full-page buyout.';
      }
    }
    $('currentStars').textContent=fmt(baselineStars);
    $('currentScoreNow').textContent=fmt(currentScoreNow);
    $('desiredScore').textContent=fmt(requestedDesired);
    $('targetMessage').hidden=true;
    $('targetMessage').classList.remove('warning');
    $('currentBreakCharacter').textContent=fmt(currentParts.character);
    $('currentBreakGear').textContent=fmt(currentParts.gear);
    $('currentBreakSkills').textContent=fmt(currentParts.skills);
    $('currentBreakRelics').textContent=fmt(currentParts.relics);
    $('currentBreakFantomons').textContent=fmt(currentParts.fantomons);
    $('currentCharacterLabel').textContent=`Character · Lv.${currentCharacter.level} + ${Math.floor(currentCharacter.pct*100)}%`;
    $('currentGearLabel').textContent=`Gear · ${gear.join(' / ')}`;
    $('currentSkillsLabel').textContent=`Skills · ${formatLevelMix(skillState.levels)}`;
    $('currentRelicsLabel').textContent=`Relics · ${formatLevelMix(relicState.levels,{plus:true})}`;
    $('currentFantomonsLabel').textContent=`Fantomons · ${formatLevelMix(fantoState.levels)}`;
    $('currentBreakdownExplain').textContent=currentCharacter.decimal<cfg.scoreFloor
      ? `${cfg.name} Season Power begins at Lv.${cfg.scoreFloor}; your current below-floor progression contributes 0 Season Power. Because you are Lv.${S2_PLANNER_START_LEVEL}+, the optimizer uses a Lv.${optimizerPlanningLevel(p.upgradeCapLevel??p.level,cfg)} full-seasonal unlock preview for upgrade availability while keeping Character score tied to your real projection. This lets stockpiled resources produce a useful Primostar estimate before the live scoring gate opens.`
      : `Character is Lv.${currentCharacter.level} at ${(currentCharacter.pct*100).toFixed(1)}% EXP. ${cfg.name} awards 1 point per completed 1% above the Lv.${cfg.scoreFloor} floor, so this contributes ${fmt(currentParts.character)} points.`;
    const recommendedSection=$('recommendedBreakdownSection');
    if(!plan){
      if($('resultEyebrow')) $('resultEyebrow').textContent='Requested target';
      $('currentStars').textContent=fmt(targetStars);
      if(recommendedSection) recommendedSection.hidden=true;
      $('targetSkills').textContent=formatLevelMix(skillState.levels); $('targetRelics').textContent=formatLevelMix(relicState.levels,{plus:true}); $('targetFantomons').textContent=formatLevelMix(fantoState.levels);
      GEAR_OUTPUT_IDS.forEach((id,i)=>$(id).textContent=gear[i]);
      $('optimizerSummary').textContent=gearLocked?'The requested score cannot be reached while Gear is locked under the current season caps.':'The requested score exceeds the currently supported progression caps/level gates; this is a score-cap issue, not a Material Realm shortage.';
      $('optimizedScore').textContent=`${fmt(baselineScore)} / ${fmt(desired)} score · target stays ${fmt(targetStars)} Primostars`;
      $('summaryOptimizedScore').textContent='—'; if($('targetStatus')){$('targetStatus').textContent='cap';$('targetStatus').classList.add('notMet');}
      $('targetMessage').hidden=false;$('targetMessage').classList.add('warning');
      $('targetMessage').textContent=`⚠ Target remains ${fmt(targetStars)} Primostars. No upgrade combination under the current lock/season caps reaches ${fmt(desired)} score, even with unlimited Ore/Essence/Sand.`;
      ['oreCost','essenceCost','sandCost','treatCost'].forEach(id=>$(id).textContent='0');
      setRawRemaining('oreBalance',0,resources.ore);
      setEssenceBalance('essenceBalance',0,resources);
      setSandBalance('sandBalance',0,resources);
      setTreatBalance('treatBalance',0,resources);
      ['oreToolBalance','essenceToolBalance','sandToolBalance'].forEach(hidePlanBalance);
      $('materialRealmRecommendation').hidden=true;$('materialRealmRecommendation').textContent='';
      $('secondaryCostNote').hidden=true;$('secondaryCostNote').textContent='';
      $('milestoneNote').hidden=true;$('milestoneNote').textContent='';
      renderAstralPact(baselineStars);
      renderPrimostarRewardReference(currentStarsNow,baselineStars);
      saveState();return;
    }
    $('targetSkills').textContent=formatLevelMix(plan.skillLevels||levelsFromAverage(plan.skill,8,100,projectedCaps.skill)); $('targetRelics').textContent=formatLevelMix(plan.relicLevels||levelsFromAverage(plan.relic,20,10,projectedCaps.relic),{plus:true}); $('targetFantomons').textContent=formatLevelMix(plan.fantoLevels||levelsFromAverage(plan.fanto,4,100,projectedCaps.fanto));
    ['targetGearWeapon','targetGearOffhand','targetGearHelmet','targetGearArmor','targetGearBoots'].forEach((id,i)=>$(id).textContent=plan.gear[i]);
    if(recommendedSection) recommendedSection.hidden=false;
    const planSkillLevels=plan.skillLevels||levelsFromAverage(plan.skill,8,100,projectedCaps.skill);
    const planRelicLevels=plan.relicLevels||levelsFromAverage(plan.relic,20,10,projectedCaps.relic);
    const planFantoLevels=plan.fantoLevels||levelsFromAverage(plan.fanto,4,100,projectedCaps.fanto);
    const recommendedParts={character:characterScore(p,cfg),gear:gearScore(plan.gear,cfg),skills:categoryScoreFromLevels(planSkillLevels,cfg.scoreFloor,cfg.weights.skill),relics:categoryScoreFromLevels(planRelicLevels,cfg.relicFloor,cfg.weights.relic),fantomons:categoryScoreFromLevels(planFantoLevels,cfg.scoreFloor,cfg.weights.fanto)};
    $('recommendedBreakCharacter').textContent=fmt(recommendedParts.character); $('recommendedBreakGear').textContent=fmt(recommendedParts.gear); $('recommendedBreakSkills').textContent=fmt(recommendedParts.skills); $('recommendedBreakRelics').textContent=fmt(recommendedParts.relics); $('recommendedBreakFantomons').textContent=fmt(recommendedParts.fantomons);
    $('recommendedCharacterLabel').textContent=`Character · Lv.${p.level} + ${Math.floor(p.pct*100)}%`; $('recommendedGearLabel').textContent=`Gear · ${plan.gear.join(' / ')}`; $('recommendedSkillsLabel').textContent=`Skills · ${formatLevelMix(planSkillLevels)} recommended`; $('recommendedRelicsLabel').textContent=`Relics · ${formatLevelMix(planRelicLevels,{plus:true})} recommended`; $('recommendedFantomonsLabel').textContent=`Fantomons · ${formatLevelMix(planFantoLevels)} recommended`;
    const recommendationDelta=plan.score-baselineScore;
    const planStars=historical+cfg.starBase+Math.floor(plan.score/cfg.scorePerStar);
    const projectedAboveGoal=!resourceBlocked && planStars>targetStars;
    const rawPotentialAboveGoal=!resourceBlocked && projectedRawCeilingStars>targetStars;
    const planSourceStage=candidateRealmStage(plan);
    $('recommendedBreakdownExplain').textContent=resourceBlocked?`This is the score-capable upgrade route for your ORIGINAL ${fmt(targetStars)}-Primostar target. It is not being downgraded; the resource cards below show what still needs funding.`:rawPotentialAboveGoal?`Smart Balance stops the recommended spend once the ${fmt(targetStars)}-Primostar goal is funded. Projected raw materials alone could reach about ${fmt(projectedRawCeilingStars)} Primostars if you intentionally spend farther, but that upside is informational and does not raise the recommendation above your entered goal.`:`Actual ${cfg.name} season-end score used by the recommendation: projected Character plus every suggested upgrade, adding ${fmt(Math.max(0,recommendationDelta))} progression points over the no-upgrade baseline.`;
    const lockedText=gearLocked?' Gear is locked at the five current levels.':'';
    const previewText=cfg.key==='s2'&&currentCharacter.level<S2_FULL_SEASONAL_PREVIEW_LEVEL
      ? ` Fantomon planning uses a conservative Lv.${optimizerPlanningLevel(p.upgradeCapLevel??p.level,cfg)} availability preview; Gear, Skills and Relic ranks are not Character-level capped.`
      : (cfg.key==='s2'?' Gear, Skills and Relic ranks are not Character-level capped; recommendations are limited by resources and the supported S2 blessing tables.':'');
    const capText=cfg.key==='s1'?` S1 safe-upgrade cap uses projected Lv.${p.upgradeCapLevel??p.level} at season reset: Skills ${projectedCaps.skill}, Fantomons ${projectedCaps.fanto} (next 10-level band), Relics +${projectedCaps.relic}; Gear is not Character-level capped.`:` S2 score model: floor Lv.130 / Relics above +13, +45 fixed Primostars, 27 score per Primostar, weights Character 100 / Gear 18 / Skill 7 / Relic 33 / Fantomon 8. Max Realm bracket is Lv.120.${previewText}`;
    const achievableRewardStars=resourceBlocked?baselineStars:planStars;
    renderAstralPact(achievableRewardStars);
    renderPrimostarRewardReference(currentStarsNow,achievableRewardStars);
    if($('resultEyebrow')) $('resultEyebrow').textContent=resourceBlocked?'Target plan · resource shortfall':'Smart Balance goal plan';
    // TARGET_PLAN_HEADER_COMPLETE_V1: reward-reference rendering must never prevent the target-plan score/status from populating.
    $('currentStars').textContent=fmt(resourceBlocked?targetStars:planStars);$('summaryOptimizedScore').textContent=fmt(plan.score);
    if($('targetStatus')){$('targetStatus').textContent=resourceBlocked?'shortfall':'✓';$('targetStatus').classList.toggle('notMet',resourceBlocked);}
    $('optimizedScore').textContent=resourceBlocked?`${fmt(plan.score)} / ${fmt(requestedDesired)} score · ${fmt(targetStars)} Primostars target plan`:`${fmt(plan.score)} / ${fmt(requestedDesired)} score · ${fmt(planStars)} Primostars · goal ${fmt(targetStars)} ✓`;
    renderTargetTiming(plan,resourceBlocked,requestedDesired,p,cfg);
    $('oreCost').textContent=fmt(plan.oreCost);$('essenceCost').textContent=fmt(plan.essenceCost);$('sandCost').textContent=fmt(plan.sandCost);$('treatCost').textContent=fmt(plan.treatCost);
    const secondary=$('secondaryCostNote');
    const refinedShort=resources.refinedTracked?Math.max(0,(plan.refinedCost||0)-resources.refined):0;
    const secondaryBits=[];
    if((plan.refinedCost||0)>0){
      if(resources.refinedTracked) secondaryBits.push(`<b>Refined Ore:</b> ${fmt(plan.refinedCost)} required · ${refinedShort>0.5?`${fmt(Math.ceil(refinedShort))} short`:`${fmt(Math.max(0,resources.refined-plan.refinedCost))} left`}`);
      else secondaryBits.push(`<b>Refined Ore:</b> ${fmt(plan.refinedCost)} needed at +5 milestones`);
    }
    if((plan.gearAdds||0)>0) secondaryBits.push(`<b>Rolla:</b> ${fmt((Number(plan.oreCost)||0)*S2_EXACT_UPGRADE_RULES.rollaPerOre)} required · inventory not tracked`);
    secondary.hidden=secondaryBits.length===0;secondary.innerHTML=secondaryBits.join(' · ');
    // Two shortage views are intentional:
    // 1) Normal Resource-card Remaining = RAW material only after the recommended spend.
    //    Realm tools enter the card only once raw material is exhausted and a shortage must be bridged.
    // 2) Top warning = hard residual after EVERY remaining extra Realm refresh slot is also exhausted.
    //    This is the true physical season-end impossibility amount.
    const oreYield=Math.max(0,Number(resources.yields.orePerHammer)||0);
    const essenceYield=Math.max(0,Number(resources.yields.essencePerKnuckles)||0);
    const sandYield=Math.max(0,Number(resources.yields.sandPerShovel)||0);
    const oreCommittedRealm=(Math.max(0,Number(plan.realm?.ore?.bankedUsed)||0))*oreYield;
    const essenceCommittedRealm=(Math.max(0,Number(plan.realm?.essence?.bankedUsed)||0))*essenceYield;
    const sandCommittedRealm=(Math.max(0,Number(plan.realm?.sand?.bankedUsed)||0))*sandYield;
    const oreCommittedBudget=resources.ore+oreCommittedRealm;
    const essenceCommittedBudget=resources.essence+essenceCommittedRealm;
    const sandCommittedBudget=resources.sand+sandCommittedRealm;
    const orePlanShort=Math.max(0,plan.oreCost-oreCommittedBudget),essPlanShort=Math.max(0,plan.essenceCost-essenceCommittedBudget),sandPlanShort=Math.max(0,plan.sandCost-sandCommittedBudget),treatShort=Math.max(0,plan.treatCost-resources.treat);
    const oreMaxRealm=Math.max(0,Number(plan.realm?.ore?.provided)||0);
    const essenceMaxRealm=Math.max(0,Number(plan.realm?.essence?.provided)||0);
    const sandMaxRealm=Math.max(0,Number(plan.realm?.sand?.provided)||0);
    const oreHardShort=Math.max(0,plan.oreCost-(resources.ore+oreMaxRealm));
    const essHardShort=Math.max(0,plan.essenceCost-(resources.essence+essenceMaxRealm));
    const sandHardShort=Math.max(0,plan.sandCost-(resources.sand+sandMaxRealm));
    if(resourceBlocked){
      /* PARTIAL_SHORTFALL_SHOW_REMAINING_V1
         A target can be impossible because ONE resource is exhausted while the other cards
         still have plenty left. Only show a shortage breakdown on resources that are actually
         short under the selected daily plan; otherwise keep the normal Remaining display. */
      if(orePlanShort>0.5) setRealmShortfallBreakdown('oreBalance',orePlanShort,oreYield,'Hammers',plan.realm?.ore?.maxPurchasedRuns,oreHardShort,'Ore');
      else setRawRemaining('oreBalance',plan.oreCost,resources.ore);
      if(essPlanShort>0.5) setRealmShortfallBreakdown('essenceBalance',essPlanShort,essenceYield,'Knuckles',plan.realm?.essence?.maxPurchasedRuns,essHardShort,'Essence',(resources.s2SkillReserve?.rawEssence||0)>0?` · S2 raw reserve: ${fmt(resources.s2SkillReserve.rawEssence)} Essence`:'');
      else setEssenceBalance('essenceBalance',plan.essenceCost,{...resources,planRealmProvided:plan.realm?.essence?.planProvided||0});
      if(sandPlanShort>0.5) setRealmShortfallBreakdown('sandBalance',sandPlanShort,sandYield,'Shovels',plan.realm?.sand?.maxPurchasedRuns,sandHardShort,'Sand',(resources.s2RelicSandReserve?.rawSand||0)>0?` · S2 raw reserve: ${fmt(resources.s2RelicSandReserve.rawSand)} Sand`:'');
      else setSandBalance('sandBalance',plan.sandCost,{...resources,planRealmProvided:plan.realm?.sand?.planProvided||0});
      setTreatBalance('treatBalance',plan.treatCost,resources);
      const shortageBits=[];if(oreHardShort>0.5)shortageBits.push(`${fmt(Math.ceil(oreHardShort))} Ore`);if(essHardShort>0.5)shortageBits.push(`${fmt(Math.ceil(essHardShort))} Essence`);if(sandHardShort>0.5)shortageBits.push(`${fmt(Math.ceil(sandHardShort))} Sand`);if(treatShort>0.5)shortageBits.push(`${fmt(Math.ceil(treatShort))} Treats`);if(refinedShort>0.5)shortageBits.push(`${fmt(Math.ceil(refinedShort))} Refined Ore`);
      const dailyShortBits=[];if(orePlanShort>0.5)dailyShortBits.push(`${fmt(Math.ceil(orePlanShort))} Ore`);if(essPlanShort>0.5)dailyShortBits.push(`${fmt(Math.ceil(essPlanShort))} Essence`);if(sandPlanShort>0.5)dailyShortBits.push(`${fmt(Math.ceil(sandPlanShort))} Sand`);
      $('targetMessage').hidden=false;$('targetMessage').classList.add('warning','danger');
      $('targetMessage').innerHTML=`⚠ Goal exceeds remaining Realm capacity.<span class="targetMessageDetail">Still short after maxing Realm purchases: ${shortageBits.join(' · ')||'resources'}.</span>`;
      const brief=[];
      /* TOOL_ONLY_RESOURCE_GAPS_V4: reserve math intentionally hidden from result summary */
      if((resources.s2SkillReserve?.target||0)>0) brief.push(`${fmt(resources.s2SkillReserve.target)} S2 skill reserve`);
      if(gearLocked) brief.push('Gear locked');
      brief.push('Resource totals include the selected daily Realm plan');
      $('optimizerSummary').textContent=brief.join(' · ');
    }else{
      const brief=[];
      /* TOOL_ONLY_RESOURCE_GAPS_V4: reserve math intentionally hidden from result summary */
      brief.push(`Goal ${fmt(targetStars)} ✓`);
      if(rawPotentialAboveGoal) brief.push(`projected raw-only potential ${fmt(projectedRawCeilingStars)}`);
      if(planSourceStage===0) brief.push('goal plan happened to use raw only');
      else if(planSourceStage===1) brief.push('raw + saved/planned Realm tools optimized as one pool · raw consumed first');
      else if(planSourceStage===2) brief.push('extra Realm purchases required as final fallback');
      if((resources.s2SkillReserve?.target||0)>0) brief.push(`${fmt(resources.s2SkillReserve.target)} S2 skill reserve`);
      if(gearLocked) brief.push('Gear locked');
      $('optimizerSummary').hidden=true;
      $('optimizerSummary').textContent='';
      setRawRemaining('oreBalance',plan.oreCost,resources.ore);
      setEssenceBalance('essenceBalance',plan.essenceCost,{...resources,planRealmProvided:plan.realm?.essence?.planProvided||0});
      setSandBalance('sandBalance',plan.sandCost,{...resources,planRealmProvided:plan.realm?.sand?.planProvided||0});
      setTreatBalance('treatBalance',plan.treatCost,resources);
    }
    const rawOreRemaining=Math.max(0,(Number(resources.ore)||0)-(Number(plan.oreCost)||0));
    const rawEssenceRemaining=Math.max(0,(Number(resources.essenceTotal??resources.essence)||0)-(Number(plan.essenceCost)||0));
    const rawSandRemaining=Math.max(0,(Number(resources.sandTotal??resources.sand)||0)-(Number(plan.sandCost)||0));
    setToolBalance('oreToolBalance',plan.realm?.ore,oreHardShort,oreYield,'Hammers',0,rawOreRemaining);
    setToolBalance('essenceToolBalance',plan.realm?.essence,essHardShort,essenceYield,'Knuckles',resources.s2SkillReserve?.knucklesReserved||0,rawEssenceRemaining);
    setToolBalance('sandToolBalance',plan.realm?.sand,sandHardShort,sandYield,'Shovels',resources.s2RelicSandReserve?.shovelsReserved||0,rawSandRemaining);
    appendStaminaProjection('oreToolBalance',allocation.ore,added.ore,'Ore');
    appendStaminaProjection('essenceToolBalance',allocation.essence,added.essence,'Essence');
    appendStaminaProjection('sandToolBalance',allocation.sand,added.sand,'Sand');
    // TARGET_SNAPSHOT_SPLIT_V1: once target timing is known, the upper resource cards stop
    // at that exact target moment. The lower post-target section alone continues to season end.
    if(Number.isFinite(postTargetLastReachMs) && !resourceBlocked){
      renderTargetResourceSnapshot(postTargetLastReachMs,plan,p,cfg);
    }
    renderRealmDailyRecommendations(plan,resources,cfg);
    const realmRec=$('materialRealmRecommendation'),realmDetailParts=[];
    const realmEntries=[
      {key:'ore',label:'Hammers',top:plan.realm?.ore},
      {key:'essence',label:'Knuckles',top:plan.realm?.essence},
      {key:'sand',label:'Shovels',top:plan.realm?.sand}
    ];
    const extraRealmBits=[];
    let hasRealmNeed=false;
    for(const entry of realmEntries){
      const top=entry.top;
      if(!top) continue;
      const detail=formatRealmSchedule(top,entry.label); if(detail) realmDetailParts.push(detail);
      if(Number.isFinite(top.packs)&&top.packs>0){
        hasRealmNeed=true;
        const extraTools=Math.max(0,Math.floor(Number(top.purchasedRuns)||0));
        if(extraTools>0) extraRealmBits.push(`${entry.label} +${fmt(extraTools)}`);
      }
    }
    const protectedKnuckles=Math.max(0,Math.floor(Number(plan.realm?.essence?.reserveRuns)||0));
    const protectedShovels=Math.max(0,Math.floor(Number(plan.realm?.sand?.reserveRuns)||0));
    const afterPlanTools={
      ore:Math.max(0,(plan.realm?.ore?.bankedRemaining||0)+(plan.realm?.ore?.sparePurchasedRuns||0)),
      essence:Math.max(0,(plan.realm?.essence?.bankedRemaining||0)+(plan.realm?.essence?.sparePurchasedRuns||0)),
      sand:Math.max(0,(plan.realm?.sand?.bankedRemaining||0)+(plan.realm?.sand?.sparePurchasedRuns||0))
    };
    // COMPACT_REALM_AFTER_PLAN_V1: keep the useful post-plan balance without repeating context.
    const toolLeftEls=[['hammerAfterPlan',afterPlanTools.ore,0],['knucklesAfterPlan',afterPlanTools.essence,protectedKnuckles],['shovelAfterPlan',afterPlanTools.sand,protectedShovels]];
    toolLeftEls.forEach(([id,value,protectedCount])=>{const el=$(id);if(el){el.textContent=`After plan: ${fmt(value)} left${protectedCount?` · ${fmt(protectedCount)} reserved`:''}`;el.classList.toggle('toolLow',value<=10);}});
    if(hasRealmNeed||resourceBlocked){
      realmRec.hidden=false;
      const hardNotes=[];
      if(treatShort>0.5) hardNotes.push(`Treats short ${fmt(Math.ceil(treatShort))}`);
      if(refinedShort>0.5) hardNotes.push(`Refined Ore short ${fmt(Math.ceil(refinedShort))}`);
      const realmCan=!resourceBlocked||!!plan.realmFeasible;
      realmRec.classList.toggle('realmFeasible',realmCan);
      realmRec.classList.toggle('realmImpossible',!realmCan);
      const extraText=extraRealmBits.length?`Goal achievable with extra Realm entries · ${extraRealmBits.join(' · ')} beyond daily plan`:(realmCan?'Goal achievable · selected daily Realm plan covers it':'Goal not achievable through remaining Realm capacity');
      const dailyPreset={ore:realmDailyValue('ore'),essence:realmDailyValue('essence'),sand:realmDailyValue('sand')};
      const dailySuggested=suggestedRealmDailyPlan(plan,cfg);
      // RECOVERABLE_SHORTFALL_REFRESH_PLAN_V1: put the resource-specific action directly
      // on each recoverable shortage card. dailySuggested values are refreshes/day, while
      // the first line keeps the exact number of additional Realm tools needed overall.
      const applyShortfallRefreshPlan=(id,key,realmLabel)=>{
        const el=$(id);
        if(!el || !el.classList.contains('shortfallBreakdown') || el.querySelector('.hardShort')) return;
        const bridge=el.querySelector('.realmBridge');
        if(!bridge) return;
        const recommended=Math.max(0,Math.floor(Number(dailySuggested?.[key])||0));
        const current=Math.max(0,Math.floor(Number(dailyPreset?.[key])||0));
        const tools=Math.max(0,Math.ceil(Number(el.dataset.shortfallTools)||0));
        const item=el.dataset.shortfallItem||'tools';
        if(recommended>current){
          bridge.textContent=`Recommended: ${fmt(recommended)} ${realmLabel} Realm purchase${recommended===1?'':'s'}/day`;
        }else if(tools>0){
          bridge.textContent=`${fmt(tools)} ${item} can cover`;
        }
      };
      applyShortfallRefreshPlan('oreBalance','ore','Ore');
      applyShortfallRefreshPlan('essenceBalance','essence','Essence');
      applyShortfallRefreshPlan('sandBalance','sand','Sand');
      const unknownTierCount=realmEntries.reduce((sum,e)=>sum+Math.max(0,Number(e.top?.unknownPriceRefreshes)||0),0);
      const priceNote=unknownTierCount>0?` · ${fmt(unknownTierCount)} extra purchase${unknownTierCount===1?'':'s'} use unverified 11–20 pricing`:'';
      const suggestionLine=realmCan&&dailySuggested.changed&&dailySuggested.needsExtra
        ? `<div class="realmBuyRoute"><b>Suggested daily plan:</b> ${dailySuggested.ore} H / ${dailySuggested.essence} K / ${dailySuggested.sand} S for ${fmt(dailySuggested.futureDays)} remaining reset${dailySuggested.futureDays===1?'':'s'}</div>`
        : (!realmCan&&dailySuggested.changed&&dailySuggested.impossible
          ? `<div class="realmBuyRoute"><b>Best available daily plan:</b> ${dailySuggested.ore} H / ${dailySuggested.essence} K / ${dailySuggested.sand} S · target still has a hard shortfall</div>`
          : '');
      realmRec.innerHTML=`<b>Material Realm:</b> ${extraText} · daily ${dailyPreset.ore}/${dailyPreset.essence}/${dailyPreset.sand} already included${priceNote}${hardNotes.length?` · ${hardNotes.join(' · ')}`:''}${suggestionLine}`;
      if(!resourceBlocked && hasRealmNeed){
        $('targetMessage').hidden=false;
        $('targetMessage').classList.add('warning','caution');
        // APPLY_RECOMMENDED_REALM_REFRESHES_V1: recommendation and one-click apply live inside the caution box.
        const route=dailySuggested.changed
          ? `<span class="targetMessageDetail">Recommended purchases/day: Ore ${dailySuggested.ore} · Essence ${dailySuggested.essence} · Sand ${dailySuggested.sand}.</span>`
          : '';
        const action=dailySuggested.changed
          ? `<button type="button" class="applyRealmRecommendation" data-ore="${dailySuggested.ore}" data-essence="${dailySuggested.essence}" data-sand="${dailySuggested.sand}">Apply purchases</button>`
          : '';
        // Resource cards now carry the exact deficit + resource-specific refresh action.
        // Keep this banner focused on the combined plan and its one-click Apply control.
        $('targetMessage').innerHTML=`<span class="targetMessageCopy">⚠ Goal is achievable with the recommended Material Realm purchase plan.${route}</span>${action}`;
      }
      realmRec.title=realmDetailParts.join(' · ');
    }else{realmRec.hidden=true;realmRec.textContent='';realmRec.classList.remove('realmFeasible','realmImpossible');realmRec.removeAttribute('title');}
    $('milestoneNote').hidden=true;$('milestoneNote').textContent='';
    saveState();
    const perfMs=performance.now()-perfStarted;
    const calcSection=$('calculatorSection');
    if(calcSection) calcSection.dataset.lastSolveMs=perfMs.toFixed(1);
    if(perfMs>750) console.warn(`Primostar solve took ${perfMs.toFixed(0)} ms`,{season:cfg.key,target:targetStars});
  }

async function copyPlan(){
    await runCalculatorUpdateSettled();
    const text=[
      `Charming Glance ${activeCalcConfig().name} plan`,
      `Current score now: ${$('currentScoreNow').textContent}`,
      `After recommended upgrades: ${$('optimizedScore').textContent}`,
      `Projected character: ${$('resultProjectedCharacter').textContent}`,
      `Target: ${$('targetStars').value} Primostars`,
      `Skills: ${$('targetSkills').textContent}`,
      `Relics: ${$('targetRelics').textContent}`,
      `Fantomons: ${$('targetFantomons').textContent}`,
      `Gear: W ${$('targetGearWeapon').textContent} / OH ${$('targetGearOffhand').textContent} / H ${$('targetGearHelmet').textContent} / A ${$('targetGearArmor').textContent} / B ${$('targetGearBoots').textContent}`,
      `Projected Stamina focus: ${staminaModeLabel(staminaMode())}${staminaMode()==='auto'&&$('staminaCurrentPlan')?` · ${$('staminaCurrentPlan').innerText.replace(/\n+/g,' · ')}`:''}`,
      `Ore: ${$('oreCost').textContent} (${ $('oreBalance').textContent })`,
      `Essence: ${$('essenceCost').textContent} (${ $('essenceBalance').textContent })`,
      `Sand: ${$('sandCost').textContent} (${ $('sandBalance').textContent })`,
      `Treats: ${$('treatCost').textContent} (${ $('treatBalance').textContent })`,
      ...(!$('secondaryCostNote').hidden?[`Other costs: ${$('secondaryCostNote').textContent}`]:[]),
      ...(!$('materialRealmRecommendation').hidden?[`Material Realm: ${$('materialRealmRecommendation').innerText.replace(/^Material Realm today:\s*/,'Today: ').replace(/^Material Realm:\s*/,'').replace(/\n+/g,' · ')}`]:[]),
    ].join('\n');
    navigator.clipboard?.writeText(text).then(()=>{
      $('saveStatus').textContent='Plan copied.'; $('saveStatus').classList.add('copyFlash');
      setTimeout(()=>{$('saveStatus').textContent='Saved snapshot auto-ages Cart + character EXP; future Stamina regen is projected automatically.';$('saveStatus').classList.remove('copyFlash');},1400);
    }).catch(()=>{});
  }

function resetCalculator(){
    const cfg=activeCalcConfig();
    if(cfg.key==='s1'){
      INPUT_IDS.forEach(id=>{if($(id)) $(id).value=defaults[id];});
      CHECK_IDS.forEach(id=>{if($(id)) $(id).checked=defaults[id];});
    } else {
      applyS2ScoringStartDefaults();
    }
    gearLocked=false; snapshotAtMs=Date.now(); snapshotSeason=cfg.key; snapshotCarry={ore:0,essence:0,sand:0,treat:0,exp:0}; snapshotStateLoaded=true;
    updateGearLockUI(); clearSavedState(); saveState(); runCalculatorUpdateSettled();
  }
// ---------- Navigation/theme ----------
let calculatorInitialized=false;

let calculatorUpdateTimer=null;

function initializeCalculatorIfNeeded(){
    if(calculatorInitialized) return;
    // Paint the lightweight season-specific chrome immediately on refresh before
    // the optimizer starts. This prevents stale S1 fallback text from flashing
    // while a saved S2 plan is being restored and solved.
    renderCalculatorSeasonChrome(activeCalcConfig());
    const status=$('optimizerSummary');
    if(status) status.textContent='Calculating your saved season plan…';
    // Let the Calculator tab paint before the expensive optimizer starts.
    requestAnimationFrame(()=>setTimeout(()=>{
      if(calculatorInitialized) return;
      calculatorInitialized=true;
      runCalculatorUpdateSettled();
    },0));
  }

function scheduleCalculatorUpdate(delay=120){
    if(!calculatorInitialized) return;
    if(calculatorUpdateTimer){
      clearTimeout(calculatorUpdateTimer);
      calculatorUpdateTimer=null;
      calculatorRunsSettled++; // superseded pending run settles trivially
    }
    calculatorRunsScheduled++;
    calculatorUpdateTimer=setTimeout(async()=>{
      calculatorUpdateTimer=null;
      try{ await updateCalculator(); }
      catch(err){ if(!(err instanceof OptimizerCancelledError)) console.error('CALC_SETTLE_PROBE_V1: update failed',err); }
      finally{ calculatorRunsSettled++; }
    },delay);
  }

function setupCalculator(){
    document.getElementById('calculatorSection')?.addEventListener('focusin',e=>{
      if(e.target?.matches?.('input') && e.target.id!=='targetStars' && e.target.id!=='finishEarlyDays'){
        // PERFORMANCE_STABILIZATION_V1: age under the pre-edit rates, but do not run the
        // expensive optimizer just for tabbing/clicking between account-state fields.
        // Target Primostars is only a goal selector and must not mutate the snapshot clock.
        rollSnapshotForward(Date.now(),true);
      }
    });
    // Heavy optimizer work only commits after the user finishes editing a field.
    // Clicking/Tabbing out fires `change`; Enter deliberately blurs the field so it commits too.
    // Discrete selectors/toggles still update immediately.
    INPUT_IDS.forEach(id=>{
      const el=$(id);
      if(!el) return;
      if(id==='finishEarlyDays'){
        /* FINISH_EARLY_COMMIT_ON_BLUR_V1
           Finish Early can trigger an expensive optimizer solve, so never recalculate while
           the user is still typing or clicking the number spinner. Commit only when editing
           is explicitly finished: Enter blurs the field; Tab and clicking/tapping elsewhere
           naturally fire blur. This is a planning preference and never moves snapshot time. */
        const commitFinishEarly=()=>{
          // FINISH_EARLY_CANCEL_CLAMP_V1: normalize visibly before starting any heavy solve.
          syncFinishEarlyInputLimit(activeCalcConfig(),true);
          const value=finishEarlyDaysValue();
          el.value=String(value);
          resetMaxAchievableUi();
          saveState();
          // FINISH_EARLY_PROGRESS_V1: Finish Early launches the same heavy optimizer as a goal change,
          // so show the cancellable calculating panel instead of making the UI appear frozen.
          queueRegularGoalOptimizerProgress();
          requestAnimationFrame(()=>scheduleCalculatorUpdate(0));
        };
        // Do not let a manually typed value sit above the physical season-time ceiling.
        el.addEventListener('input',()=>{
          const raw=Number(el.value),max=maxFinishEarlyDays(activeCalcConfig());
          if(Number.isFinite(raw)&&raw>max) el.value=String(max);
        });
        el.addEventListener('blur',commitFinishEarly);
        el.addEventListener('keydown',ev=>{
          if(ev.key==='Enter'){
            ev.preventDefault();
            el.blur();
          }
        });
        return;
      }
      if(id==='staminaMode'){
        el.addEventListener('change',()=>{resetMaxAchievableUi();markManualSnapshot(id);scheduleCalculatorUpdate(0);});
        return;
      }
      el.addEventListener('change',()=>{
        normalizeCompactNumberInput(id);
        if(id==='targetStars'){
          // GOAL_CHANGE_FINISH_EARLY_RESET_V1: always evaluate a newly entered goal with
          // the full remaining season. A previous Max cutoff is only valid for its old goal.
          if(resetFinishEarlyForGoalChange()) resetMaxAchievableUi();
          saveState();
          if($('optimizerSummary')) $('optimizerSummary').textContent='Updating goal…';
          queueRegularGoalOptimizerProgress();
          requestAnimationFrame(()=>scheduleCalculatorUpdate(0));
          return;
        }
        resetMaxAchievableUi();
        markManualSnapshot(id);
        scheduleCalculatorUpdate(0);
      });
      el.addEventListener('keydown',e=>{
        if(e.key==='Enter'){
          e.preventDefault();
          el.blur();
        }
      });
    });
    /* MAIN_RUNTIME_REPAIR_V1
       Restore the calculator setup tail and startup sequence. A build-role patch had
       accidentally replaced this block, preventing navigation/timeline initialization. */
    CHECK_IDS.forEach(id=>$(id)?.addEventListener('change',()=>{
      resetMaxAchievableUi();
      markManualSnapshot(id);
      saveState();
      if(calculatorInitialized) scheduleCalculatorUpdate(0);
      else initializeCalculatorIfNeeded();
    }));
    PANEL_OPEN_IDS.forEach(id=>$(id)?.addEventListener('toggle',saveState));
    $('s2TargetPresets')?.addEventListener('click',e=>{
      const btn=e.target.closest?.('[data-s2-target]');
      if(!btn || activeCalcConfig().key!=='s2') return;
      $('targetStars').value=btn.dataset.s2Target;
      resetFinishEarlyForGoalChange();
      resetMaxAchievableUi();
      saveState();
      $('s2TargetPresets')?.querySelectorAll('[data-s2-target]').forEach(x=>x.classList.toggle('active',x===btn));
      if($('optimizerSummary')) $('optimizerSummary').textContent='Updating goal…';
      queueRegularGoalOptimizerProgress();
      requestAnimationFrame(()=>scheduleCalculatorUpdate(0));
    });
    /* S2_ROLLOVER_HEADER_RESET_V1 */
    $('confirmSeasonSnapshot')?.addEventListener('click',()=>{resetMaxAchievableUi();confirmCurrentSeasonSnapshot();});
    $('resetSeasonSnapshot')?.addEventListener('click',()=>{resetMaxAchievableUi();resetCalculator();});
    $('findMaxStars')?.addEventListener('click',findMaxAchievableStars);
    $('finishEarlyMax')?.addEventListener('click',findMaxFinishEarly);
    $('targetMessage')?.addEventListener('click',e=>{
      const btn=e.target.closest?.('.applyRealmRecommendation');
      if(btn) applyRecommendedRealmRefreshes(btn);
    });
    $('copyPlan')?.addEventListener('click',copyPlan);
    $('resetCalc')?.addEventListener('click',()=>{resetMaxAchievableUi();resetCalculator();});
    setInterval(()=>{
      if(document.hidden||!calculatorInitialized) return;
      rollSnapshotForward(Date.now(),true);
      if(!document.getElementById('calculatorSection')?.hidden) scheduleCalculatorUpdate(0);
    },60_000);
  }
const {solveTargetWithAutoStamina, materialRealmDaysAvailable, realmInventoryFor, realmTopupFor, buildGearOptions, planningCategoryState, createPlanningContext, plannedToolAcquisitionSupply, jointReacquisitionHours, acquisitionEffortFor, makePlanCandidate, searchPlans, searchPlansCooperative, solveTargetWithAutoStaminaCooperative, optimizer}=createPlannerEngine({get staminaMode(){return staminaMode;},
get allocateStaminaForPlan(){return allocateStaminaForPlan;},
get upgradeFinishCutoffMs(){return upgradeFinishCutoffMs;},
get futureRealmPurchaseDays(){return futureRealmPurchaseDays;},
get n(){return n;},
get plannedRealmRunsFor(){return plannedRealmRunsFor;},
get realmDailyValue(){return realmDailyValue;},
get gearLocked(){return gearLocked;},set gearLocked(value){gearLocked=value;},
get categoryStateFromUser(){return categoryStateFromUser;},
get characterSnapshot(){return characterSnapshot;},
get optimizerCategoryCaps(){return optimizerCategoryCaps;},
get gearStateFromUser(){return gearStateFromUser;},
get createOptimizerCheckpoint(){return createOptimizerCheckpoint;}});
const {postTargetToolState,savePostTargetToolState,clearSavedState,advanceCharacterSnapshot, rollSnapshotForward, markManualSnapshot, saveState, loadState}=createSavedState({get snapshotSeason(){return snapshotSeason;},set snapshotSeason(value){snapshotSeason=value;},
get n(){return n;},
get $(){return $;},
get snapshotStateLoaded(){return snapshotStateLoaded;},set snapshotStateLoaded(value){snapshotStateLoaded=value;},
get snapshotAtMs(){return snapshotAtMs;},set snapshotAtMs(value){snapshotAtMs=value;},
get projectionResourceHoursAt(){return projectionResourceHoursAt;},
get finishScoreCutoffMs(){return finishScoreCutoffMs;},
get realmDailyValue(){return realmDailyValue;},
get snapshotCarry(){return snapshotCarry;},set snapshotCarry(value){snapshotCarry=value;},
get gearLocked(){return gearLocked;},set gearLocked(value){gearLocked=value;},
get applyS2ScoringStartDefaults(){return applyS2ScoringStartDefaults;},
get updateGearLockUI(){return updateGearLockUI;}});
const {renderRealmToolProjection, renderRealmDailyRecommendations, renderLocalTimeLabels, renderTargetResourceSnapshot, renderPostTargetGains, renderTargetTiming, renderStaminaCurrentPlan, hidePlanBalance, setRawRemaining, setSandBalance, setTreatBalance, setBalance, setToolBalance, appendStaminaProjection, setRealmShortfallBreakdown, renderAstralPact, renderPrimostarRewardReference, renderCalculatorSeasonChrome, clearS2PreScoring, clearS2ProjectedAtFloor, clearCalcForRollover, clearS2ForRequiredPlannerInputs}=createCalculatorRenderer({get futureRealmPurchaseDays(){return futureRealmPurchaseDays;},
get realmDailyValue(){return realmDailyValue;},
get n(){return n;},
get $(){return $;},
get suggestedRealmDailyPlan(){return suggestedRealmDailyPlan;},
get postTargetCarryAt(){return postTargetCarryAt;},
get ensurePostTargetControls(){return ensurePostTargetControls;},
get hidePostTargetGains(){return hidePostTargetGains;},
get postTargetLastReachMs(){return postTargetLastReachMs;},set postTargetLastReachMs(value){postTargetLastReachMs=value;},
get postTargetLastCfg(){return postTargetLastCfg;},set postTargetLastCfg(value){postTargetLastCfg=value;},
get postTargetLastPlan(){return postTargetLastPlan;},set postTargetLastPlan(value){postTargetLastPlan=value;},
get postTargetLastPEnd(){return postTargetLastPEnd;},set postTargetLastPEnd(value){postTargetLastPEnd=value;},
get selectedPostTargetToolState(){return selectedPostTargetToolState;},
get postTargetRawGains(){return postTargetRawGains;},
get estimateTargetReachMoment(){return estimateTargetReachMoment;},
get projectCharacterTo(){return projectCharacterTo;},
get projectCharacter(){return projectCharacter;},
get staminaMode(){return staminaMode;},
get characterSnapshot(){return characterSnapshot;},
get snapshotSeason(){return snapshotSeason;},set snapshotSeason(value){snapshotSeason=value;},
get applyS2ScoringStartDefaults(){return applyS2ScoringStartDefaults;},
get snapshotAtMs(){return snapshotAtMs;},set snapshotAtMs(value){snapshotAtMs=value;},
get snapshotCarry(){return snapshotCarry;},set snapshotCarry(value){snapshotCarry=value;},
get snapshotStateLoaded(){return snapshotStateLoaded;},set snapshotStateLoaded(value){snapshotStateLoaded=value;},
get saveState(){return saveState;}});

let mounted=false;
export function initialize(){if(mounted)return;loadState();setupCalculator();mounted=true;}
export function activate(){initializeCalculatorIfNeeded();}
