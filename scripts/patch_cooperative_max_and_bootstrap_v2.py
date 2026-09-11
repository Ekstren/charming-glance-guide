from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
runtime_path = ROOT / 'assets' / 'runtime.js'
runtime = runtime_path.read_text(encoding='utf-8')

# 1) The normal cooperative solver must yield BEFORE building the planning context.
old_solve = """async function solveTargetWithAutoStaminaCooperative(baseScore,desired,p,baseResources,cfg=activeCalcConfig(),job=null){\n    const ctx=createPlanningContext(baseScore,desired,p,cfg);\n"""
new_solve = """async function solveTargetWithAutoStaminaCooperative(baseScore,desired,p,baseResources,cfg=activeCalcConfig(),job=null){\n    // COOPERATIVE_OPTIMIZER_BOOTSTRAP_V2: paint the progress panel and honor a queued\n    // cancellation before any structural option-building work can occupy the main thread.\n    const bootstrapCheckpoint=createOptimizerCheckpoint(job);\n    await bootstrapCheckpoint(true);\n    const ctx=createPlanningContext(baseScore,desired,p,cfg);\n    await bootstrapCheckpoint(true);\n"""
if 'COOPERATIVE_OPTIMIZER_BOOTSTRAP_V2' not in runtime:
    if old_solve not in runtime:
        raise SystemExit('cooperative solver bootstrap anchor not found')
    runtime = runtime.replace(old_solve, new_solve, 1)

# 2) Finish Early Max used synchronous binary-search probes. Make the search itself a
# cooperative/cancellable optimizer job, yielding before and after every probe.
start = runtime.find('  function findMaxFinishEarly(){')
if start < 0:
    start = runtime.find('  async function findMaxFinishEarly(){')
end = runtime.find('\n\n  /* SMART_BALANCE_RAW_CEILING_V1', start)
if start < 0 or end < 0:
    raise SystemExit('Finish Early Max function anchors not found')

new_max = r'''  async function findMaxFinishEarly(){
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
        btn.title='The selected target is not reachable without extra Realm purchases beyond your configured routine.';
        await updateCalculator();
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
      await updateCalculator();
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
      btn.disabled=false;
      btn.textContent='Max';
      btn.removeAttribute('aria-busy');
    }
  }'''

runtime = runtime[:start] + new_max + runtime[end:]
runtime_path.write_text(runtime, encoding='utf-8')
