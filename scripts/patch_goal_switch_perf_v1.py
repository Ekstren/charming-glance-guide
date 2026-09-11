from pathlib import Path
import re

runtime=Path('assets/runtime.js')
s=runtime.read_text()
index=Path('index.html')
h=index.read_text()

# 1) New/reset S2 states should start with a realistic Bed EXP rate.
old='charLevel:130,charExp:0,bedExp:0,'
new='charLevel:130,charExp:0,bedExp:400000,'
assert old in s, 'S2 bed default anchor missing'
s=s.replace(old,new,1)
old_html='<label>Bed EXP per hour<input id="bedExp" type="number" value="0"></label>'
new_html='<label>Bed EXP per hour<input id="bedExp" type="number" value="400000"></label>'
assert old_html in h, 'bedExp HTML anchor missing'
h=h.replace(old_html,new_html,1)

# 2) Share the expensive structural planning context between raw-ceiling and target solve.
old='function smartBalanceRawCeiling(baseScore,p,baseResources,cfg,historical){\n    // Large structural target only expands Gear options; actual affordability below is\n    // still limited strictly by projected raw resources and verified progression gates.\n    const ctx=createPlanningContext(baseScore,1_000_000,p,cfg);'
new='function smartBalanceRawCeiling(baseScore,p,baseResources,cfg,historical,sharedCtx=null){\n    // Large structural target only expands Gear options; actual affordability below is\n    // still limited strictly by projected raw resources and verified progression gates.\n    const ctx=sharedCtx||createPlanningContext(baseScore,1_000_000,p,cfg);'
assert old in s, 'raw ceiling anchor missing'
s=s.replace(old,new,1)

pattern=r"function solveTargetWithAutoStamina\(baseScore,desired,p,baseResources,cfg=activeCalcConfig\(\)\)\{\n    const ctx=createPlanningContext\(baseScore,desired,p,cfg\);"
repl="function solveTargetWithAutoStamina(baseScore,desired,p,baseResources,cfg=activeCalcConfig(),sharedCtx=null){\n    const ctx=sharedCtx||createPlanningContext(baseScore,desired,p,cfg);"
s,n=re.subn(pattern,repl,s,count=1)
assert n==1, 'solveTargetWithAutoStamina anchor missing'

# 3) Cache target-independent structural state and per-target solutions while inputs stay unchanged.
anchor='  let lastRequestedTargetStars=null;\n  let lastEffectiveTargetStars=null;\n\n  function updateCalculator(){'
insert='''  let lastRequestedTargetStars=null;
  let lastEffectiveTargetStars=null;

  /* GOAL_SWITCH_CACHE_V1
     Target Primostars is the only value that changes when the user taps a preparation goal.
     All expensive category option tables, the raw-only ceiling, and previously solved targets
     can therefore be reused until any other calculator input/snapshot changes. */
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
    if(goalSwitchCache.fingerprint===fingerprint && goalSwitchCache.ctx){
      return goalSwitchCache;
    }
    const ctx=createPlanningContext(baseScore,1_000_000,p,cfg);
    const rawCeiling=smartBalanceRawCeiling(baseScore,p,baseResources,cfg,historical,ctx);
    goalSwitchCache={fingerprint,ctx,rawCeiling,solutions:new Map()};
    return goalSwitchCache;
  }

  function updateCalculator(){'''
assert anchor in s, 'goal cache insertion anchor missing'
s=s.replace(anchor,insert,1)

# 4) When the projected season-end player level does not reach 131, do not run the optimizer at all.
old='''    const p=projectCharacter(cfg);
    const upgradeP=projectCharacterTo(upgradeFinishCutoffMs(cfg),cfg);'''
new='''    const p=projectCharacter(cfg);
    if(cfg.key==='s2' && p.level<=cfg.scoreFloor){ clearS2ProjectedAtFloor(cfg,p); return; }
    const upgradeP=projectCharacterTo(upgradeFinishCutoffMs(cfg),cfg);'''
assert old in s, 'projected-floor fast path anchor missing'
s=s.replace(old,new,1)

# 5) Reuse the shared context/raw ceiling and memoize exact target solutions.
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
assert old in s, 'goal solve replacement anchor missing'
s=s.replace(old,new,1)

# 6) Add the projected-floor paused-state renderer next to the existing pre-scoring renderer.
anchor='''  function clearCalcForRollover(cfg){'''
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
    $('targetMessage').textContent=`Projected season-end Character is Lv.${p.level}. The S2 preparation optimizer stays paused until the projection reaches Lv.131, so changing the Primostar goal does not run the heavy upgrade search at Lv.130 or lower.`;
    if($('targetStatus')){$('targetStatus').textContent='waiting for Lv.131';$('targetStatus').classList.remove('notMet');}
    $('optimizerSummary').textContent='No Gear / Skill / Relic / Fantomon optimization is run while projected season-end Character remains Lv.130 or lower.';
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
assert anchor in s, 'clear projected floor helper anchor missing'
s=s.replace(anchor,helper,1)

# 7) Let the selected goal paint before the heavy solve starts on slower phones.
old="""      markManualSnapshot('targetStars');
      saveState();
      scheduleCalculatorUpdate(0);
    });"""
new="""      markManualSnapshot('targetStars');
      saveState();
      $('s2TargetPresets')?.querySelectorAll('[data-s2-target]').forEach(x=>x.classList.toggle('active',x===btn));
      if($('optimizerSummary')) $('optimizerSummary').textContent='Updating goal…';
      requestAnimationFrame(()=>scheduleCalculatorUpdate(0));
    });"""
assert old in s, 'preset responsiveness anchor missing'
s=s.replace(old,new,1)

runtime.write_text(s)
index.write_text(h)
print('Applied goal-switch performance patch + S2 bed default + projected-Lv130 fast path')
