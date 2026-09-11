from pathlib import Path

p=Path('assets/runtime.js')
s=p.read_text(encoding='utf-8')
marker='COOPERATIVE_OPTIMIZER_GENERATION_V1'
if marker in s:
    print('Generation guard already present.')
    raise SystemExit(0)

old="""  let optimizerJobSequence=0;\n  let activeOptimizerJob=null;"""
new="""  let optimizerJobSequence=0;\n  let optimizerUpdateGeneration=0; // COOPERATIVE_OPTIMIZER_GENERATION_V1\n  let activeOptimizerJob=null;"""
if old not in s:
    raise SystemExit('optimizer job state block not found')
s=s.replace(old,new,1)

old="""  async function updateCalculator(){\n    const perfStarted=performance.now();"""
new="""  async function updateCalculator(){\n    const updateGeneration=++optimizerUpdateGeneration;\n    // Any newer edit supersedes an older in-flight solve, even if the new state is cached.\n    if(activeOptimizerJob) activeOptimizerJob.cancelled=true;\n    const perfStarted=performance.now();"""
if old not in s:
    raise SystemExit('updateCalculator header not found')
s=s.replace(old,new,1)

old="""        solution=await solveTargetWithAutoStaminaCooperative(baselineScore,desired,p,baseResources,cfg,optimizerJob);\n        if(optimizerJob.cancelled) throw new OptimizerCancelledError();"""
new="""        solution=await solveTargetWithAutoStaminaCooperative(baselineScore,desired,p,baseResources,cfg,optimizerJob);\n        if(updateGeneration!==optimizerUpdateGeneration || optimizerJob.cancelled) throw new OptimizerCancelledError();"""
if old not in s:
    raise SystemExit('cooperative solve await block not found')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('Applied optimizer generation guard.')
