from pathlib import Path

runtime = Path('assets/runtime.js')
js = runtime.read_text(encoding='utf-8')

# 1) Main calculator: Stamina regenerates from real wall-clock time only.
old = "    const staminaGenerated=Math.max(0,Math.floor(resourceHours*5));\n"
new = "    // Stamina regenerates from real wall-clock time only; idle/2h speed-ups do not create Stamina.\n    const staminaGenerated=Math.max(0,Math.floor(wallResourceHours*5));\n"
if old not in js:
    raise SystemExit('projectedResourcesTo stamina line not found')
js = js.replace(old, new, 1)

# 2) Preserve leftover stamina across the target boundary so splitting the season at the target
#    does not drop partial-node stamina.
old = "    const emptyCarry={ore:0,essence:0,sand:0,treat:0,hammers:0,knuckles:0,shovels:0};\n"
new = "    const emptyCarry={ore:0,essence:0,sand:0,treat:0,hammers:0,knuckles:0,shovels:0,staminaUnused:0};\n"
if old not in js:
    raise SystemExit('emptyCarry anchor not found')
js = js.replace(old, new, 1)

old = "        shovels:Math.max(0,Math.floor(Number(sandTop.bankedRemaining)||0)+Math.floor(Number(sandTop.sparePurchasedRuns)||0))\n      };\n"
new = "        shovels:Math.max(0,Math.floor(Number(sandTop.bankedRemaining)||0)+Math.floor(Number(sandTop.sparePurchasedRuns)||0)),\n        staminaUnused:Math.max(0,Number(resources.staminaUnused)||0)\n      };\n"
if old not in js:
    raise SystemExit('carry return anchor not found')
js = js.replace(old, new, 1)

# 3) Post-target calculation starts with the stamina remainder carried from the pre-target segment.
old = "  function postTargetRawGains(reached,cfg,state=selectedPostTargetToolState()){\n"
new = "  function postTargetRawGains(reached,cfg,state=selectedPostTargetToolState(),staminaCarry=0){\n"
if old not in js:
    raise SystemExit('postTargetRawGains signature not found')
js = js.replace(old, new, 1)

old = "    const staminaGenerated=Math.max(0,Math.floor(wallHours*5));\n"
new = "    const staminaGenerated=Math.max(0,Math.floor(Math.max(0,Number(staminaCarry)||0)+(wallHours*5)));\n"
if old not in js:
    raise SystemExit('post-target stamina line not found')
js = js.replace(old, new, 1)

old = "    const gains=postTargetRawGains(reached,cfg,state);\n"
new = "    const gains=postTargetRawGains(reached,cfg,state,carry.staminaUnused);\n"
if old not in js:
    raise SystemExit('post-target gains call not found')
js = js.replace(old, new, 1)

runtime.write_text(js, encoding='utf-8')

# Regression guards.
text = runtime.read_text(encoding='utf-8')
if "Math.floor(wallResourceHours*5)" not in text:
    raise SystemExit('wall-clock stamina fix missing')
if "carry.staminaUnused" not in text:
    raise SystemExit('stamina carry fix missing')
