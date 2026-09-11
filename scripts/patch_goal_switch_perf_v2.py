from pathlib import Path
import re

runtime=Path('assets/runtime.js')
s=runtime.read_text()
index=Path('index.html')
h=index.read_text()

# New/reset S2 states start from a realistic Bed EXP rate.
assert 'charLevel:130,charExp:0,bedExp:0,' in s
s=s.replace('charLevel:130,charExp:0,bedExp:0,','charLevel:130,charExp:0,bedExp:400000,',1)
assert '<label>Bed EXP per hour<input id="bedExp" type="number" value="0"></label>' in h
h=h.replace('<label>Bed EXP per hour<input id="bedExp" type="number" value="0"></label>','<label>Bed EXP per hour<input id="bedExp" type="number" value="400000"></label>',1)

# One structural option context can serve the raw ceiling and every preparation-goal target.
old='function smartBalanceRawCeiling(baseScore,p,baseResources,cfg,historical){\n    // Large structural target only expands Gear options; actual affordability below is\n    // still limited strictly by projected raw resources and verified progression gates.\n    const ctx=createPlanningContext(baseScore,1_000_000,p,cfg);'
new='function smartBalanceRawCeiling(baseScore,p,baseResources,cfg,historical,sharedCtx=null){\n    // Large structural target only expands Gear options; actual affordability below is\n    // still limited strictly by projected raw resources and verified progression gates.\n    const ctx=sharedCtx||createPlanningContext(baseScore,1_000_000,p,cfg);'
assert old in s
s=s.replace(old,new,1)

pat=r"function solveTargetWithAutoStamina\(baseScore,desired,p,baseResources,cfg=activeCalcConfig\(\)\)\{\n    const ctx=createPlanningContext\(baseScore,desired,p,cfg\);"
s,n=re.subn(pat,"function solveTargetWithAutoStamina(baseScore,desired,p,baseResources,cfg=activeCalcConfig(),sharedCtx=null){\n    const ctx=sharedCtx||createPlanningContext(baseScore,desired,p,cfg);",s,count=1)
assert n==1

anchor='  let lastRequestedTargetStars=null;\n  let lastEffectiveTargetStars=null;\n\n  function updateCalculator(){'
insert='''  let lastRequestedTargetStars=null;
  let lastEffectiveTargetStars=null;

  /* GOAL_SWITCH_CACHE_V2
     Preparation-goal changes do not alter the player's snapshot. Reuse the expensive option
     tables and their lazy Realm/acquisition caches across goal changes, and memoize targets
     already solved during this unchanged snapshot. */
  let goalSwitchCache={fingerprint:'',ctx:null,rawCeiling:null,solutions:new Map()};
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
    if(goalSwitchCache.fingerprint===fingerprint && goalSwitchCache.ctx) return goalSwitchCache;
    const ctx=createPlanningContext(baseScore,1_000_000,p,cfg);
    const rawCeiling=smartBalanceRawCeiling(baseScore,p,baseResources,cfg,historical,ctx);
    goalSwitchCache={fingerprint,ctx,rawCeiling,solutions:new Map()};
    return goalSwitchCache;
  }

  function updateCalculator(){'''
assert anchor in s
s=s.replace(anchor,insert,1)

# Scope the projected-level fast path specifically to updateCalculator (not max-achievable helpers).
pat=r"(function updateCalculator\(\)\{.*?if\(cfg\.key==='s2' && characterSnapshot\(cfg\)\.level<S2_PLANNER_START_LEVEL\)\{ clearS2PreScoring\(cfg\); return; \}\n    const p=projectCharacter\(cfg\);)\n    const upgradeP="
m=re.search(pat,s,flags=re.S)
assert m, 'updateCalculator projected gate anchor missing'
replacement=m.group(1)+"\n    if(cfg.key==='s2' && p.level<=cfg.scoreFloor){ clearS2ProjectedAtFloor(cfg,p); return; }\n    const upgradeP="
s=s[:m.start()]+re.sub(pat,lambda _:replacement,s[m.start():],count=1,flags=re.S)

old='''    const rawCeiling=smartBalanceRawCeiling(baselineScore,p,baseResources,cfg,historical);
    const projectedRawCeilingStars=Math.max(baselineStars,Math.floor(Number(rawCeiling?.stars)||baselineStars));
    const desired=requestedDesired;
    const solution=solveTargetWithAutoStamina(baselineScore,desired,p,baseResources,cfg);'''
new='''    const goalState=goalSwitchPlanningState(baselineScore,p,baseResources,cfg,historical);
    const rawCeiling=goalState.rawCeiling;
    const projectedRawCeilingStars=Math.max(baselineStars,Math.floor(Number(rawCeiling?.stars)||baselineStars));
    const desired=requestedDesired;
    let solution=goalState.solutions.get(desired);
    if(!solution){
      solution=solveTargetWithAutoStamina(baselineScore,desired,p,baseResources,cfg,goalState.ctx);
      goalState.solutions.set(desired,solution);
    }'''
assert old in s
s=s.replace(old,new,1)

anchor='  function clearCalcForRollover(cfg){'
helper='''  function clearS2ProjectedAtFloor(cfg,p=projectCharacter(cfg)){
    const historical=Math.max(0,Math.floor(n('historicalStars',0)));
    const carried=historical+cfg.starBase;
    $('seasonRemaining').textContent=formatRemaining(p.hours);
    $('projectedCharacter').value=`Lv.${p.level} · ${(p.pct*100).toFixed(1)}%`;
    $('resultProjectedCharacter').textContent=`Lv.${p.level} (${(p.pct*100).toFixed(1)}%)`;
    $('currentStars').textContent=fmt(carried);
    $('currentScoreNow').textContent='0';
    $('summaryOptimizedScore').textContent='—';
    $('desiredScore').textContent='—';
    if($('recommendedBreakdownSection')) $('recommendedBreakdownSection').hidden=true;
    $('targetMessage').hidden=false;
    $('targetMessage').classList.remove('danger');
    $('targetMessage').classList.add('warning','caution');
    $('targetMessage').textContent=`Projected season-end Character is Lv.${p.level}. The S2 preparation optimizer stays paused until the projection reaches Lv.131, so goal changes do not run the heavy upgrade search at Lv.130 or lower.`;
    if($('targetStatus')){$('targetStatus').textContent='waiting for Lv.131';$('targetStatus').classList.remove('notMet');}
    $('optimizerSummary').textContent='Preparation optimizer paused: projected season-end Character must reach Lv.131 before Gear / Skill / Relic / Fantomon target planning runs.';
    $('optimizedScore').textContent='—';
    ['targetSkills','targetRelics','targetFantomons'].forEach(id=>{if($(id))$(id).textContent='—';});
    GEAR_OUTPUT_IDS.forEach(id=>{if($(id))$(id).textContent='—';});
    ['oreCost','essenceCost','sandCost','treatCost'].forEach(id=>{if($(id))$(id).textContent='0';});
    ['oreBalance','essenceBalance','sandBalance','treatBalance','oreToolBalance','essenceToolBalance','sandToolBalance'].forEach(hidePlanBalance);
    $('materialRealmRecommendation').hidden=true;$('materialRealmRecommendation').textContent='';
    $('secondaryCostNote').hidden=true;$('secondaryCostNote').textContent='';
    $('milestoneNote').hidden=true;$('milestoneNote').textContent='';
    renderAstralPact(carried);
    renderPrimostarRewardReference(carried,carried);
    saveState();
    const calcSection=$('calculatorSection');
    if(calcSection) calcSection.dataset.lastSolveMs='0.0';
  }

  function clearCalcForRollover(cfg){'''
assert anchor in s
s=s.replace(anchor,helper,1)

# Goal changes are planning preferences, not progression snapshots. Do not advance snapshotAtMs.
old='''      el.addEventListener('change',()=>{
        normalizeCompactNumberInput(id);
        if(id!=='targetStars') resetMaxAchievableUi();
        markManualSnapshot(id);
        scheduleCalculatorUpdate(0);
      });'''
new='''      el.addEventListener('change',()=>{
        normalizeCompactNumberInput(id);
        if(id!=='targetStars'){
          resetMaxAchievableUi();
          markManualSnapshot(id);
          scheduleCalculatorUpdate(0);
        }else{
          saveState();
          if($('optimizerSummary')) $('optimizerSummary').textContent='Updating goal…';
          requestAnimationFrame(()=>scheduleCalculatorUpdate(0));
        }
      });'''
assert old in s
s=s.replace(old,new,1)

old='''      $('targetStars').value=btn.dataset.s2Target;
      resetMaxAchievableUi();
      markManualSnapshot('targetStars');
      saveState();
      scheduleCalculatorUpdate(0);'''
new='''      $('targetStars').value=btn.dataset.s2Target;
      resetMaxAchievableUi();
      saveState();
      $('s2TargetPresets')?.querySelectorAll('[data-s2-target]').forEach(x=>x.classList.toggle('active',x===btn));
      if($('optimizerSummary')) $('optimizerSummary').textContent='Updating goal…';
      requestAnimationFrame(()=>scheduleCalculatorUpdate(0));'''
assert old in s
s=s.replace(old,new,1)

# Find-max changing only the target should not invalidate the physical snapshot either.
s=s.replace("      markManualSnapshot('targetStars');\n      scheduleCalculatorUpdate(0);","      saveState();\n      scheduleCalculatorUpdate(0);",1)

# Keep the explanatory source text aligned with the new Lv.131 projected-end gate.
h=h.replace('<b>Lv.120 maximum S2 Realm/open-map material bracket and planner start</b>, <b>Lv.130 Season Power scoring baseline / second-dungeon milestone</b>, and a <b>Lv.131 full-seasonal unlock preview</b> used only for pre-gate planning.', '<b>Lv.120 maximum S2 Realm/open-map material bracket</b>, <b>Lv.130 Season Power scoring baseline / second-dungeon milestone</b>, and <b>Lv.131 projected season-end level</b> as the point where the preparation optimizer begins running.')
h=h.replace('At the Lv.120 max bracket, one Realm attempt yields', 'The optimizer stays paused when projected season-end Character is Lv.130 or lower; once the projection reaches Lv.131, it evaluates the progression families below. At the Lv.120 max bracket, one Realm attempt yields')

runtime.write_text(s)
index.write_text(h)
print('Applied GOAL_SWITCH_CACHE_V2 + Lv131 projected gate + 400k Bed EXP default')
