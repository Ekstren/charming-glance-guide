from pathlib import Path

path = Path('assets/runtime.js')
text = path.read_text(encoding='utf-8')

# 1) Finish Early belongs to the goal for which it was calculated.  A stale Max value
# must never constrain a newly selected Primostar target.
needle = """  function finishEarlyDaysValue(){\n    const raw=Number($('finishEarlyDays')?.value);\n    // FINISH_EARLY_HALF_DAY_V1: planner cutoff supports 0.5-day increments.\n    return Number.isFinite(raw)?Math.max(0,Math.round(raw*2)/2):0;\n  }\n"""
insert = needle + """  /* GOAL_CHANGE_FINISH_EARLY_RESET_V1\n     Finish Early is target-specific. If the user changes the Primostar goal after Max\n     found (for example) 38 days early for a lower goal, do not let that stale cutoff make\n     the new goal look impossible. New goals always solve from the full remaining season;\n     Max can then be run again for the new target. */\n  function resetFinishEarlyForGoalChange(){\n    const input=$('finishEarlyDays');\n    if(!input || finishEarlyDaysValue()<=0) return false;\n    input.value='0';\n    return true;\n  }\n"""
if 'GOAL_CHANGE_FINISH_EARLY_RESET_V1' not in text:
    if needle not in text:
        raise SystemExit('finishEarlyDaysValue anchor not found')
    text = text.replace(needle, insert, 1)

# 2) Stop doing the giant informational raw-only ceiling calculation before every
# non-target state fingerprint. It used createPlanningContext(..., 1_000_000, ...)
# synchronously and could freeze the main thread while the visible job still read 0.0s.
old_cache = """  /* GOAL_SWITCH_CACHE_V2\n     Changing Target Primostars does not change the account snapshot. Reuse the expensive\n     raw-only ceiling and any exact target solution already computed while every non-target\n     input remains identical. New goals still build their normal target-specific context. */\n  let goalSwitchCache={fingerprint:'',rawCeiling:null,solutions:new Map()};\n"""
new_cache = """  /* GOAL_SWITCH_CACHE_V3 · RESPONSIVE_GOAL_PREP_V1\n     Changing Target Primostars does not change the account snapshot. Reuse exact target\n     solutions while every non-target input remains identical. The old path eagerly built an\n     informational raw-only ceiling with a synthetic 1,000,000-score target before the real\n     solve; that synchronous structural expansion could freeze the main thread, leaving Cancel\n     and the elapsed timer stuck during \"Preparing goal calculation\". Ceiling discovery now\n     stays behind the explicit Find max achievable control instead of blocking normal goals. */\n  let goalSwitchCache={fingerprint:'',rawCeiling:null,solutions:new Map()};\n"""
if 'RESPONSIVE_GOAL_PREP_V1' not in text:
    if old_cache not in text:
        raise SystemExit('GOAL_SWITCH_CACHE_V2 anchor not found')
    text = text.replace(old_cache, new_cache, 1)

old_state = """  function goalSwitchPlanningState(baseScore,p,baseResources,cfg,historical){\n    const fingerprint=goalSwitchFingerprint(cfg,baseScore);\n    if(goalSwitchCache.fingerprint===fingerprint) return goalSwitchCache;\n    const rawCeiling=smartBalanceRawCeiling(baseScore,p,baseResources,cfg,historical);\n    goalSwitchCache={fingerprint,rawCeiling,solutions:new Map()};\n    return goalSwitchCache;\n  }\n"""
new_state = """  function goalSwitchPlanningState(baseScore,p,baseResources,cfg,historical){\n    const fingerprint=goalSwitchFingerprint(cfg,baseScore);\n    if(goalSwitchCache.fingerprint===fingerprint) return goalSwitchCache;\n    // RESPONSIVE_GOAL_PREP_V1: rawCeiling is informational only. Do not synchronously\n    // expand a synthetic million-score planning context before the requested goal solve.\n    goalSwitchCache={fingerprint,rawCeiling:null,solutions:new Map()};\n    return goalSwitchCache;\n  }\n"""
if old_state in text:
    text = text.replace(old_state, new_state, 1)
elif 'rawCeiling:null,solutions:new Map()' not in text:
    raise SystemExit('goalSwitchPlanningState anchor not found')

# 3) Typed target changes reset Finish Early to 0 before queueing the solve.
old_target = """        if(id==='targetStars'){\n          saveState();\n          if($('optimizerSummary')) $('optimizerSummary').textContent='Updating goal…';\n          queueRegularGoalOptimizerProgress();\n          requestAnimationFrame(()=>scheduleCalculatorUpdate(0));\n          return;\n        }\n"""
new_target = """        if(id==='targetStars'){\n          // GOAL_CHANGE_FINISH_EARLY_RESET_V1: always evaluate a newly entered goal with\n          // the full remaining season. A previous Max cutoff is only valid for its old goal.\n          if(resetFinishEarlyForGoalChange()) resetMaxAchievableUi();\n          saveState();\n          if($('optimizerSummary')) $('optimizerSummary').textContent='Updating goal…';\n          queueRegularGoalOptimizerProgress();\n          requestAnimationFrame(()=>scheduleCalculatorUpdate(0));\n          return;\n        }\n"""
if 'A previous Max cutoff is only valid for its old goal.' not in text:
    if old_target not in text:
        raise SystemExit('typed target handler anchor not found')
    text = text.replace(old_target, new_target, 1)

# 4) Preset target buttons get the same reset behavior.
old_preset = """      $('targetStars').value=btn.dataset.s2Target;\n      resetMaxAchievableUi();\n      saveState();\n"""
new_preset = """      $('targetStars').value=btn.dataset.s2Target;\n      resetFinishEarlyForGoalChange();\n      resetMaxAchievableUi();\n      saveState();\n"""
if old_preset in text:
    text = text.replace(old_preset, new_preset, 1)
elif "$('targetStars').value=btn.dataset.s2Target;\n      resetFinishEarlyForGoalChange();" not in text:
    raise SystemExit('preset target handler anchor not found')

# 5) Applying the already-computed hard max is also a goal change.
old_max_apply = """    if(maxAchievableState.fingerprint===fingerprint && Number.isFinite(maxAchievableState.hard)){\n      $('targetStars').value=String(maxAchievableState.hard);\n      markManualSnapshot('targetStars');\n      scheduleCalculatorUpdate(0);\n      return;\n    }\n"""
new_max_apply = """    if(maxAchievableState.fingerprint===fingerprint && Number.isFinite(maxAchievableState.hard)){\n      const hardTarget=maxAchievableState.hard;\n      resetFinishEarlyForGoalChange();\n      $('targetStars').value=String(hardTarget);\n      resetMaxAchievableUi();\n      saveState();\n      if($('optimizerSummary')) $('optimizerSummary').textContent='Updating goal…';\n      queueRegularGoalOptimizerProgress();\n      requestAnimationFrame(()=>scheduleCalculatorUpdate(0));\n      return;\n    }\n"""
if 'const hardTarget=maxAchievableState.hard;' not in text:
    if old_max_apply not in text:
        raise SystemExit('max achievable apply anchor not found')
    text = text.replace(old_max_apply, new_max_apply, 1)

path.write_text(text, encoding='utf-8')
print('patched goal switch reset + responsive prep')
