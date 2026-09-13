from pathlib import Path

path = Path('assets/runtime.js')
text = path.read_text(encoding='utf-8')

old = """  function finishEarlyDaysValue(){
    const raw=Number($('finishEarlyDays')?.value);
    // FINISH_EARLY_HALF_DAY_V1: planner cutoff supports 0.5-day increments.
    return Number.isFinite(raw)?Math.max(0,Math.round(raw*2)/2):0;
  }
"""
new = """  function maxFinishEarlyDays(cfg=activeCalcConfig()){
    const remainingDays=Math.max(0,(cfg.end.getTime()-Date.now())/86_400_000);
    // Never allow the planning cutoff to move before the present moment.
    return Math.floor((remainingDays+1e-9)*2)/2;
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
"""
if old not in text:
    raise SystemExit('finishEarlyDaysValue block not found')
text = text.replace(old, new, 1)

old_update = """  async function updateCalculator(){
    const updateGeneration=++optimizerUpdateGeneration;
"""
new_update = """  async function updateCalculator(){
    // Clamp impossible manual values before any expensive solve starts.
    syncFinishEarlyInputLimit(activeCalcConfig(),true);
    const updateGeneration=++optimizerUpdateGeneration;
"""
if old_update not in text:
    raise SystemExit('updateCalculator start not found')
text = text.replace(old_update, new_update, 1)

path.write_text(text, encoding='utf-8')
print('Added dynamic Finish Early cap based on actual season time remaining.')
