from pathlib import Path

runtime_path = Path('assets/runtime.js')
runtime = runtime_path.read_text(encoding='utf-8')

# Default target: 680 everywhere S2 initializes.
old = '    targetStars:800,'
new = '    targetStars:680,'
count = runtime.count(old)
if count == 1:
    runtime = runtime.replace(old, new, 1)
elif '    targetStars:680,' not in runtime:
    raise SystemExit(f'Unexpected S2 target default state; 800 count={count}')

# Auto-reset any stale pre-S2 calculator snapshot instead of showing the rollover prompt.
needle = "    const mismatch=snapshotSeason!==cfg.key;\n    $('calcSeasonNotice').hidden=!mismatch;"
replacement = "    // S2_AUTO_RESET_STALE_SNAPSHOT_V1: stale pre-S2 calculator state is never offered for reuse.\n    // Load clean S2 defaults immediately so old seasonal levels/resources cannot leak into the new season.\n    if(cfg.key==='s2' && snapshotSeason!==cfg.key){\n      applyS2ScoringStartDefaults();\n      snapshotSeason=cfg.key;\n      snapshotAtMs=Date.now();\n      snapshotCarry={ore:0,essence:0,sand:0,treat:0,exp:0};\n      snapshotStateLoaded=true;\n      saveState();\n    }\n    const mismatch=snapshotSeason!==cfg.key;\n    $('calcSeasonNotice').hidden=!mismatch;"
if runtime.count(needle) != 1:
    raise SystemExit(f'Expected exactly one rollover mismatch marker, found {runtime.count(needle)}')
runtime = runtime.replace(needle, replacement, 1)

runtime_path.write_text(runtime, encoding='utf-8')

index_path = Path('index.html')
index = index_path.read_text(encoding='utf-8')
old_html = '<label>Target Primostars<input id="targetStars" type="number" value="200"></label>'
new_html = '<label>Target Primostars<input id="targetStars" type="number" value="680"></label>'
count = index.count(old_html)
if count == 1:
    index = index.replace(old_html, new_html, 1)
elif new_html not in index:
    raise SystemExit(f'Unexpected HTML target default state; 200 count={count}')
index_path.write_text(index, encoding='utf-8')

check = runtime_path.read_text(encoding='utf-8')
assert '    targetStars:680,' in check
assert "if(cfg.key==='s2' && snapshotSeason!==cfg.key){" in check
assert 'applyS2ScoringStartDefaults();' in check
assert 'snapshotSeason=cfg.key;' in check
print('S2 auto-reset and 680 default patched successfully.')
