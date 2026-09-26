import { countFuturePacificResets } from '../time.mjs';
import { seasonKeyAt } from '../season-clock.mjs';
import { STORAGE_KEY, PANEL_OPEN_IDS, CALC_SEASONS, LEGACY_GEAR_IDS, INPUT_IDS, CHECK_IDS, clamp, activeCalcConfig, projectionBedClaimableHoursAt, expRequiredForLevel, POST_TARGET_TOOL_STORAGE_KEY, REALM_RUNS_PER_REFRESH } from './model.mjs';
export function createSavedState(__calculatorDeps){
function advanceCharacterSnapshot(deltaExp,cfg=CALC_SEASONS[__calculatorDeps.snapshotSeason] || activeCalcConfig()){
    let lvl = Math.max(1, Math.floor(__calculatorDeps.n('charLevel',cfg.key==='s2'?100:122)));
    let exp = Math.max(0,__calculatorDeps.n('charExp',0)) + Math.max(0,deltaExp);
    let safety=0;
    while(safety++ < 400){
      const req = expRequiredForLevel(lvl,cfg);
      if(exp < req) break;
      exp -= req;
      lvl++;
    }
    if(__calculatorDeps.$('charLevel')) __calculatorDeps.$('charLevel').value = String(lvl);
    if(__calculatorDeps.$('charExp')) __calculatorDeps.$('charExp').value = String(Math.max(0,Math.floor(exp)));
  }
function rollSnapshotForward(nowMs=Date.now(), persist=true){
    if(!__calculatorDeps.snapshotStateLoaded) return false;
    if(!Number.isFinite(__calculatorDeps.snapshotAtMs) || __calculatorDeps.snapshotAtMs <= 0){ __calculatorDeps.snapshotAtMs=nowMs; return false; }
    const cfg=CALC_SEASONS[__calculatorDeps.snapshotSeason] || activeCalcConfig();
    const cappedNow=Math.min(nowMs,cfg.end.getTime());
    if(cappedNow <= __calculatorDeps.snapshotAtMs + 1000) return false;
    // Deterministic values age only inside the season that produced this snapshot.
    // This prevents a stale S1 state from silently becoming an S2 state after reset.
    const oldResourceHours = __calculatorDeps.projectionResourceHoursAt(__calculatorDeps.snapshotAtMs,cfg);
    const newResourceHours = __calculatorDeps.projectionResourceHoursAt(cappedNow,cfg);
    const elapsedResourceHours = Math.max(0, oldResourceHours-newResourceHours);
    const oldBedClaimableHours = projectionBedClaimableHoursAt(__calculatorDeps.snapshotAtMs,cfg);
    const newBedClaimableHours = projectionBedClaimableHoursAt(cappedNow,cfg);
    const elapsedBedClaimableHours = Math.max(0,oldBedClaimableHours-newBedClaimableHours);
    /* AUTO_AGE_REALM_TOOLS_V1
       Treat the saved Daily purchase plan like Cart production: once a planned 6 AM
       reset has actually passed, move those purchased entries into the on-hand tool counts.
       Future projection then loses that reset at the same time, so season-end tool totals stay
       stable instead of requiring the user to manually add Hammers/Knuckles/Shovels each day.
       Match futureRealmPurchaseDays(): purchases stop at the optional finishing-window cutoff. */
    const realmCutoffMs=__calculatorDeps.finishScoreCutoffMs(cfg);
    const realmAgeEnd=Math.min(cappedNow,realmCutoffMs);
    const elapsedRealmResets=realmAgeEnd>__calculatorDeps.snapshotAtMs
      ? countFuturePacificResets(__calculatorDeps.snapshotAtMs,realmAgeEnd)
      : 0;
    if(elapsedRealmResets>0){
      const toolDefs=[
        ['hammerCurrent','ore'],
        ['knucklesCurrent','essence'],
        ['shovelCurrent','sand']
      ];
      toolDefs.forEach(([currentId,key])=>{
        const gained=elapsedRealmResets*__calculatorDeps.realmDailyValue(key)*REALM_RUNS_PER_REFRESH;
        if(gained>0 && __calculatorDeps.$(currentId)) __calculatorDeps.$(currentId).value=String(Math.max(0,Math.floor(__calculatorDeps.n(currentId,0)))+gained);
      });
    }
    const resourceDefs = [
      ['oreCurrent','oreRate','ore'],
      ['essenceCurrent','essenceRate','essence'],
      ['sandCurrent','sandRate','sand'],
      ['treatCurrent','treatRate','treat']
    ];
    resourceDefs.forEach(([currentId,rateId,key])=>{
      const produced = Math.max(0,__calculatorDeps.n(rateId,0))*elapsedResourceHours + Math.max(0,Number(__calculatorDeps.snapshotCarry[key])||0);
      const whole = Math.floor(produced + 1e-9);
      __calculatorDeps.snapshotCarry[key] = Math.max(0, produced-whole);
      if(whole>0 && __calculatorDeps.$(currentId)) __calculatorDeps.$(currentId).value = String(Math.max(0,__calculatorDeps.n(currentId,0))+whole);
    });
    const bedRate=Math.max(0,__calculatorDeps.n('bedExp',0));
    const producedExp=bedRate*elapsedBedClaimableHours + Math.max(0,Number(__calculatorDeps.snapshotCarry.exp)||0);
    const wholeExp=Math.floor(producedExp+1e-9);
    __calculatorDeps.snapshotCarry.exp=Math.max(0,producedExp-wholeExp);
    if(wholeExp>0) advanceCharacterSnapshot(wholeExp,cfg);
    // Already-held Stamina is intentionally not snapshot-aged because the calculator tracks only future regenerated Stamina.
    __calculatorDeps.snapshotAtMs = cappedNow;
    if(persist) saveState();
    return elapsedResourceHours>0 || elapsedBedClaimableHours>0 || elapsedRealmResets>0;
  }
function markManualSnapshot(id){
    // Do not silently approve a season rollover just because one field was edited.
    // The dedicated rollover button confirms that the whole snapshot has been refreshed.
    if(__calculatorDeps.snapshotSeason===seasonKeyAt(Date.now())) __calculatorDeps.snapshotAtMs = Date.now();
    if(id==='oreCurrent') __calculatorDeps.snapshotCarry.ore=0;
    if(id==='essenceCurrent') __calculatorDeps.snapshotCarry.essence=0;
    if(id==='sandCurrent' || id==='sandBlueCurrent' || id==='sandEpicCurrent') __calculatorDeps.snapshotCarry.sand=0;
    if(id==='treatCurrent' || id==='treatPremiumCurrent' || id==='treatDeluxeCurrent') __calculatorDeps.snapshotCarry.treat=0;
    if(id==='charLevel' || id==='charExp') __calculatorDeps.snapshotCarry.exp=0;
  }
function saveState(){
    const state = {
      gearLocked: __calculatorDeps.gearLocked,
      theme: document.documentElement.dataset.theme || 'dark',
      snapshotSchema: 8,
      snapshotAt: __calculatorDeps.snapshotAtMs,
      snapshotSeason: __calculatorDeps.snapshotSeason,
      snapshotCarry: {...__calculatorDeps.snapshotCarry},
      panelOpen: Object.fromEntries(PANEL_OPEN_IDS.map(id => [id, !!__calculatorDeps.$(id)?.open]))
    };
    INPUT_IDS.forEach(id => state[id] = __calculatorDeps.$(id)?.value ?? '');
    CHECK_IDS.forEach(id => state[id] = !!__calculatorDeps.$(id)?.checked);
    try{localStorage.setItem(STORAGE_KEY, JSON.stringify(state));}catch(_){}
  }
function loadState(){
    let hadState=false;
    try{
      const state = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
      hadState = Object.keys(state).length>0;
      // SHOP_REFRESH_DEFAULT_ZERO_V1: the shop estimator is opt-in. Migrate the old inherited 3/day once.
      if(hadState && localStorage.getItem('sxs-shop-refresh-default-zero-v1')!=='1'){
        if(Number(state.shopRefreshesDaily)===3) state.shopRefreshesDaily=0;
        localStorage.setItem('sxs-shop-refresh-default-zero-v1','1');
      }
      // v39 replaces the old single Realm preset with independent per-resource daily inputs.
      // Preserve the user's prior shared preset when migrating; otherwise default each Realm to 4/day.
      if(hadState && (Number(state.snapshotSchema)||0)<5){
        const oldDaily = /^\d+$/.test(String(state.realmDailyPreset??'')) ? clamp(parseInt(state.realmDailyPreset,10),0,20) : 4;
        if(state.realmDailyOre===undefined) state.realmDailyOre=String(oldDaily);
        if(state.realmDailyEssence===undefined) state.realmDailyEssence=String(oldDaily);
        if(state.realmDailySand===undefined) state.realmDailySand=String(oldDaily);
      }
      if(hadState && state.gearLevel===undefined){
        const legacy=LEGACY_GEAR_IDS.map(id=>Number(state[id])).filter(Number.isFinite);
        if(legacy.length===5){
          state.gearLevel=String(legacy.reduce((a,b)=>a+b,0)/legacy.length);
          if(state.exactGearLevels===undefined && new Set(legacy).size>1) state.exactGearLevels=legacy.join(', ');
        }
      }
      // Preserve existing early-finish plans as the new automatic preference.
      if(state.finishEarlyAuto===undefined) state.finishEarlyAuto=Number(state.finishEarlyDays)>0;
      INPUT_IDS.forEach(id => { if (state[id] !== undefined && __calculatorDeps.$(id)) __calculatorDeps.$(id).value = state[id]; });
      CHECK_IDS.forEach(id => { if (state[id] !== undefined && __calculatorDeps.$(id)) __calculatorDeps.$(id).checked = !!state[id]; });
      if(!hadState && activeCalcConfig().key==='s2') __calculatorDeps.applyS2ScoringStartDefaults();
      __calculatorDeps.gearLocked = false; // gear lock UI removed; optimizer always considers Gear
      // Main calculator editors default closed, then remember the user's last open/collapsed state.
      PANEL_OPEN_IDS.forEach(id => {
        const panel=__calculatorDeps.$(id);
        if(!panel) return;
        const hasSavedPanelState=state.panelOpen && typeof state.panelOpen==='object' && Object.prototype.hasOwnProperty.call(state.panelOpen,id);
        panel.open = hasSavedPanelState ? state.panelOpen[id]===true : id==='characterDetails';
      });
      if(Number.isFinite(Number(state.snapshotAt)) && Number(state.snapshotAt)>0){
        __calculatorDeps.snapshotAtMs = Number(state.snapshotAt);
      } else {
        // v10 and earlier did not store a timestamp, so their values cannot be safely
        // back-filled. Treat first v11 load as the baseline rather than guessing.
        __calculatorDeps.snapshotAtMs = Date.now();
      }
      __calculatorDeps.snapshotSeason = (state.snapshotSeason && CALC_SEASONS[state.snapshotSeason]) ? state.snapshotSeason : seasonKeyAt(__calculatorDeps.snapshotAtMs);
      if(state.snapshotCarry && typeof state.snapshotCarry==='object'){
        for(const k of Object.keys(__calculatorDeps.snapshotCarry)){
          const v=Number(state.snapshotCarry[k]);
          __calculatorDeps.snapshotCarry[k]=Number.isFinite(v) && v>=0 ? v : 0;
        }
      }
    } catch (_) {
      __calculatorDeps.snapshotAtMs=Date.now();
      __calculatorDeps.snapshotSeason=seasonKeyAt(__calculatorDeps.snapshotAtMs);
      __calculatorDeps.snapshotCarry={ore:0, essence:0, sand:0, treat:0, exp:0};
    }
    __calculatorDeps.snapshotStateLoaded=true;
    if(hadState) rollSnapshotForward(Date.now(),false);
    __calculatorDeps.updateGearLockUI();
    saveState();
  }
function postTargetToolState(){
    let out={mode:'current',stamina:'current',ore:0,essence:0,sand:0};
    try{
      const saved=JSON.parse(localStorage.getItem(POST_TARGET_TOOL_STORAGE_KEY)||'{}');
      if(['current','stop','custom'].includes(saved.mode)) out.mode=saved.mode;
      if(['current','ore','essence','sand'].includes(saved.stamina)) out.stamina=saved.stamina;
      for(const k of ['ore','essence','sand']) if(Number.isFinite(Number(saved[k]))) out[k]=clamp(Math.floor(Number(saved[k])),0,20);
    }catch(_){}
    return out;
  }

function savePostTargetToolState(state){
    try{localStorage.setItem(POST_TARGET_TOOL_STORAGE_KEY,JSON.stringify(state));}catch(_){}
  }
function clearSavedState(){try{localStorage.removeItem(STORAGE_KEY);}catch(_){}}
return {postTargetToolState,savePostTargetToolState,clearSavedState,advanceCharacterSnapshot, rollSnapshotForward, markManualSnapshot, saveState, loadState};
}
