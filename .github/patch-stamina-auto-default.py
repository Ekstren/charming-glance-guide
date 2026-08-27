from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')
marker = 'STAMINA_AUTO_DEFAULT_V1'
if marker in s:
    print('already applied')
    raise SystemExit(0)

old_select = '<select id="staminaMode" title="Late-S1 Ore is verified; Essence/Sand use community-style estimates derived from the same S1 Ore-to-Realm scaling."><option value="ore" selected>Raw Ore</option><option value="auto">Auto</option><option value="essence">Skill Essence</option><option value="sand">Chrono Sand</option></select>'
new_select = '<select id="staminaMode" title="Late-S1 Ore is verified; Essence/Sand use community-style estimates derived from the same S1 Ore-to-Realm scaling."><option value="auto" selected>Auto</option><option value="ore">Raw Ore</option><option value="essence">Skill Essence</option><option value="sand">Chrono Sand</option></select>'
if old_select not in s:
    raise SystemExit('stamina select pattern not found')
s = s.replace(old_select, new_select, 1)

old_defaults = "if(!defaults.staminaMode) defaults.staminaMode = 'ore';"
new_defaults = "if(!defaults.staminaMode) defaults.staminaMode = 'auto'; // STAMINA_AUTO_DEFAULT_V1"
if old_defaults not in s:
    raise SystemExit('defaults stamina fallback not found')
s = s.replace(old_defaults, new_defaults, 1)

old_mode = "const raw = $('staminaMode')?.value || 'ore';\n    return ['ore','auto','essence','sand'].includes(raw) ? raw : 'ore';"
new_mode = "const raw = $('staminaMode')?.value || 'auto';\n    return ['auto','ore','essence','sand'].includes(raw) ? raw : 'auto';"
if old_mode not in s:
    raise SystemExit('staminaMode fallback pattern not found')
s = s.replace(old_mode, new_mode, 1)

old_s2 = "staminaMode:'ore',realmDailyOre:0"
new_s2 = "staminaMode:'auto',realmDailyOre:0"
if old_s2 not in s:
    raise SystemExit('S2 stamina default pattern not found')
s = s.replace(old_s2, new_s2, 1)

p.write_text(s, encoding='utf-8')
print('patched stamina selector: Auto first + default')
