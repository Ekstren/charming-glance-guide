#!/usr/bin/env python3
from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')

old = """  function relicCapForCharacter(characterLevel){
    const lvl=Math.max(1,Math.floor(Number(characterLevel)||1));
    // Community/live planner rule: Lv.100→+11, 110→+12, 120→+13, 130→+14, etc.
    return lvl<100 ? 10 : Math.max(10,Math.floor(lvl/10)+1);
  }
"""
new = """  function relicCapForCharacter(characterLevel,cfg=activeCalcConfig()){
    const lvl=Math.max(1,Math.floor(Number(characterLevel)||1));
    // S2_RELIC_14_LV131_DIRECT_V1: Charming Glance live evidence on Sep. 10 shows +13→+14 is locked through Lv.130 and unlocks at Character Lv.131.
    if(cfg.key==='s2' && lvl<=130) return 13;
    // Legacy/S1 rule retained outside the directly observed S2 Lv.130 gate.
    return lvl<100 ? 10 : Math.max(10,Math.floor(lvl/10)+1);
  }
"""

if 'S2_RELIC_14_LV131_DIRECT_V1' not in text:
    if old not in text:
        raise SystemExit('Expected relicCapForCharacter block not found; refusing to patch.')
    text = text.replace(old, new, 1)

# categoryCapsForCharacter may evaluate a season config that is not the currently
# selected UI config, so pass cfg explicitly instead of relying on the default.
needle = 'relic:relicCapForCharacter(lvl),'
count = text.count(needle)
if count:
    if count != 2:
        raise SystemExit(f'Expected exactly 2 category cap calls, found {count}; refusing to patch.')
    text = text.replace(needle, 'relic:relicCapForCharacter(lvl,cfg),')

required = [
    'S2_RELIC_14_LV131_DIRECT_V1',
    "if(cfg.key==='s2' && lvl<=130) return 13;",
    'relic:relicCapForCharacter(lvl,cfg),',
]
for marker in required:
    if marker not in text:
        raise SystemExit(f'Missing required post-patch marker: {marker}')

path.write_text(text, encoding='utf-8')
print('Applied direct Charming Glance S2 relic +14 Lv.131 gate correction.')
