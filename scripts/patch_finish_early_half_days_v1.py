from pathlib import Path

root = Path('.')
index_path = root / 'index.html'
runtime_path = root / 'assets' / 'runtime.js'
css_path = root / 'assets' / 'site.css'

index = index_path.read_text(encoding='utf-8')
runtime = runtime_path.read_text(encoding='utf-8')
css = css_path.read_text(encoding='utf-8')

old_input = 'id="finishEarlyDays" type="number" min="0" step="1" value="0" inputmode="numeric"'
new_input = 'id="finishEarlyDays" type="number" min="0" step="0.5" value="0" inputmode="decimal"'
if old_input not in index and new_input not in index:
    raise SystemExit('finishEarlyDays input signature not found')
index = index.replace(old_input, new_input, 1)

old_value = """  function finishEarlyDaysValue(){
    const raw=Number($('finishEarlyDays')?.value);
    return Number.isFinite(raw)?Math.max(0,Math.floor(raw)):0;
  }
"""
new_value = """  function finishEarlyDaysValue(){
    const raw=Number($('finishEarlyDays')?.value);
    // FINISH_EARLY_HALF_DAY_V1: planner cutoff supports 0.5-day increments.
    return Number.isFinite(raw)?Math.max(0,Math.round(raw*2)/2):0;
  }
"""
if old_value in runtime:
    runtime = runtime.replace(old_value, new_value, 1)
elif 'Math.round(raw*2)/2' not in runtime:
    raise SystemExit('finishEarlyDaysValue block not found')

old_cutoff = """  function finishScoreCutoffMs(cfg=activeCalcConfig()){
    const days=finishEarlyDaysValue();
    if(days<=0) return cfg.end.getTime();
    const endIso=pacificIsoAt(cfg.end.getTime());
    const cutoff=pacificLocalMs(isoAddDays(endIso,-days),6,0);
    return Math.min(cfg.end.getTime(),cutoff);
  }
"""
new_cutoff = """  function finishScoreCutoffMs(cfg=activeCalcConfig()){
    const days=finishEarlyDaysValue();
    if(days<=0) return cfg.end.getTime();
    const endIso=pacificIsoAt(cfg.end.getTime());
    const wholeDays=Math.floor(days);
    const hasHalf=days-wholeDays>=0.5;
    // Preserve reset-day semantics across DST. A half day lands at 6 PM Pacific on
    // the preceding local date instead of subtracting a blind 12h from a UTC timestamp.
    const cutoffIso=isoAddDays(endIso,-(wholeDays+(hasHalf?1:0)));
    const cutoff=pacificLocalMs(cutoffIso,hasHalf?18:6,0);
    return Math.min(cfg.end.getTime(),cutoff);
  }
"""
if old_cutoff in runtime:
    runtime = runtime.replace(old_cutoff, new_cutoff, 1)
elif 'const hasHalf=days-wholeDays>=0.5;' not in runtime:
    raise SystemExit('finishScoreCutoffMs block not found')

marker_start = '/* FINISH_EARLY_HALF_DAY_SIZE_V1_START */'
marker_end = '/* FINISH_EARLY_HALF_DAY_SIZE_V1_END */'
block = r'''
/* FINISH_EARLY_HALF_DAY_SIZE_V1_START */
/* Slightly larger than the compact v2 control while staying intentionally small. */
.finishEarlyCard{
  min-height:46px!important;
  padding:8px 11px!important;
  gap:6px!important;
  font-size:9px!important;
}
.finishEarlyCard input{
  width:46px!important;
  min-width:46px!important;
  max-width:46px!important;
  flex-basis:46px!important;
  height:30px!important;
  min-height:30px!important;
  font-size:11px!important;
}
.finishEarlyCard em{font-size:9px!important}
@media(max-width:760px){
  .finishEarlyCard{min-height:48px!important;padding:9px 12px!important}
  .finishEarlyCard input{width:48px!important;min-width:48px!important;max-width:48px!important;flex-basis:48px!important;height:32px!important;min-height:32px!important;font-size:12px!important}
}
/* FINISH_EARLY_HALF_DAY_SIZE_V1_END */
'''.strip()

if marker_start in css and marker_end in css:
    before = css.split(marker_start, 1)[0]
    after = css.split(marker_end, 1)[1]
    css = before + block + after
else:
    css = css.rstrip() + '\n\n' + block + '\n'

index_path.write_text(index, encoding='utf-8')
runtime_path.write_text(runtime, encoding='utf-8')
css_path.write_text(css, encoding='utf-8')

# Sanity checks
assert 'step="0.5"' in index
assert 'inputmode="decimal"' in index
assert 'Math.round(raw*2)/2' in runtime
assert 'hasHalf?18:6' in runtime
assert marker_start in css
print('Applied finish-early half-day + sizing patch.')
