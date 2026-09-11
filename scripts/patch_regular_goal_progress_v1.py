from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'assets'/'runtime.js'
s=path.read_text(encoding='utf-8')

if 'REGULAR_GOAL_PROGRESS_V1' in s:
    print('REGULAR_GOAL_PROGRESS_V1 already present')
    raise SystemExit(0)

old="""  let optimizerJobSequence=0;
  let optimizerUpdateGeneration=0; // COOPERATIVE_OPTIMIZER_GENERATION_V1
  let activeOptimizerJob=null;
"""
new="""  let optimizerJobSequence=0;
  let optimizerUpdateGeneration=0; // COOPERATIVE_OPTIMIZER_GENERATION_V1
  let activeOptimizerJob=null;
  let queuedGoalOptimizerJob=null; // REGULAR_GOAL_PROGRESS_V1

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
"""
if old not in s:
    raise SystemExit('optimizer globals anchor not found')
s=s.replace(old,new,1)

old="""  async function updateCalculator(){
    const updateGeneration=++optimizerUpdateGeneration;
    // Any newer edit supersedes an older in-flight solve, even if the new state is cached.
    if(activeOptimizerJob) activeOptimizerJob.cancelled=true;
    const perfStarted=performance.now();
"""
new="""  async function updateCalculator(){
    const updateGeneration=++optimizerUpdateGeneration;
    const queuedGoalJob=queuedGoalOptimizerJob;
    if(queuedGoalJob===queuedGoalOptimizerJob) queuedGoalOptimizerJob=null;
    // Any newer edit supersedes an older in-flight solve, except the goal job intentionally
    // queued by the target control so its already-painted progress panel can be reused.
    if(activeOptimizerJob && activeOptimizerJob!==queuedGoalJob) activeOptimizerJob.cancelled=true;
    const perfStarted=performance.now();
"""
if old not in s:
    raise SystemExit('updateCalculator start anchor not found')
s=s.replace(old,new,1)

old="""    const cfg=activeCalcConfig();
    if(renderCalculatorSeasonChrome(cfg)){ clearCalcForRollover(cfg); return; }
"""
new="""    const cfg=activeCalcConfig();
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
"""
if old not in s:
    raise SystemExit('calculator cfg anchor not found')
s=s.replace(old,new,1)

s=s.replace("if(!required.hasBed){ clearS2ForRequiredPlannerInputs(cfg,required); return; }",
            "if(!required.hasBed){ if(queuedGoalJob) finishOptimizerJob(queuedGoalJob,'done'); clearS2ForRequiredPlannerInputs(cfg,required); return; }",1)
s=s.replace("if(!required.hasAllCart){ clearS2ForRequiredPlannerInputs(cfg,required,p); return; }",
            "if(!required.hasAllCart){ if(queuedGoalJob) finishOptimizerJob(queuedGoalJob,'done'); clearS2ForRequiredPlannerInputs(cfg,required,p); return; }",1)

old="""    const goalState=goalSwitchPlanningState(baselineScore,p,baseResources,cfg,historical);
    const rawCeiling=goalState.rawCeiling;
"""
new="""    if(queuedGoalJob){
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
"""
if old not in s:
    raise SystemExit('goalState anchor not found')
s=s.replace(old,new,1)

old="""    let solution=goalState.solutions.get(desired);
    if(!solution){
      const optimizerJob=beginOptimizerJob(targetStars);
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
    }
"""
new="""    let solution=goalState.solutions.get(desired);
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
"""
if old not in s:
    raise SystemExit('solution block anchor not found')
s=s.replace(old,new,1)

old="""        if(id==='targetStars'){
          saveState();
          if($('optimizerSummary')) $('optimizerSummary').textContent='Updating goal…';
          requestAnimationFrame(()=>scheduleCalculatorUpdate(0));
          return;
        }
"""
new="""        if(id==='targetStars'){
          saveState();
          if($('optimizerSummary')) $('optimizerSummary').textContent='Updating goal…';
          queueRegularGoalOptimizerProgress();
          requestAnimationFrame(()=>scheduleCalculatorUpdate(0));
          return;
        }
"""
if old not in s:
    raise SystemExit('targetStars change handler anchor not found')
s=s.replace(old,new,1)

old="""      if($('optimizerSummary')) $('optimizerSummary').textContent='Updating goal…';
      requestAnimationFrame(()=>scheduleCalculatorUpdate(0));
    });
"""
new="""      if($('optimizerSummary')) $('optimizerSummary').textContent='Updating goal…';
      queueRegularGoalOptimizerProgress();
      requestAnimationFrame(()=>scheduleCalculatorUpdate(0));
    });
"""
if old not in s:
    raise SystemExit('preset target handler anchor not found')
s=s.replace(old,new,1)

path.write_text(s,encoding='utf-8')
print('patched REGULAR_GOAL_PROGRESS_V1')
