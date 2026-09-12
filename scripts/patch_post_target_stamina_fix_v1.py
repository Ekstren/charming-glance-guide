from pathlib import Path

runtime = Path('assets/runtime.js')
index = Path('index.html')

js = runtime.read_text(encoding='utf-8')
html = index.read_text(encoding='utf-8')

repls = [
    ("if(['current','ore','essence','sand','save'].includes(saved.stamina)) out.stamina=saved.stamina;",
     "if(['current','ore','essence','sand'].includes(saved.stamina)) out.stamina=saved.stamina;"),
    ("    const staminaGenerated=Math.max(0,Math.floor(resourceHours*5));\n    const staminaNodes=Math.floor(staminaGenerated/Math.max(1,Number(yields.staminaPerNode)||5));\n    const currentMode=$('staminaMode')?.value||'auto';\n    const requested=state?.stamina||'current';\n    const destination=requested==='current'\n      ? (currentMode==='auto'?'ore':currentMode)\n      : (requested==='save'?null:requested);\n    if(['ore','essence','sand'].includes(destination)) gains[destination]+=staminaNodes*Math.max(0,Number(yields[destination])||0);",
     "    // Stamina regenerates from real elapsed time; daily 2h idle boosts do not create Stamina.\n    const staminaGenerated=Math.max(0,Math.floor(wallHours*5));\n    const staminaNodes=Math.floor(staminaGenerated/Math.max(1,Number(yields.staminaPerNode)||5));\n    const currentMode=$('staminaMode')?.value||'auto';\n    const requested=state?.stamina||'current';\n    const destination=requested==='current'\n      ? (currentMode==='auto'?'ore':currentMode)\n      : requested;\n    const map=yields.map||{};\n    if(['ore','essence','sand'].includes(destination)) gains[destination]+=staminaNodes*Math.max(0,Number(map[destination])||0);"),
]
for old,new in repls:
    if old not in js:
        raise SystemExit('Expected runtime block not found: ' + old[:100])
    js = js.replace(old,new,1)

save_label = '            <label><input type="radio" name="postTargetStaminaMode" value="save"> Save Stamina</label>\n'
if save_label not in html:
    raise SystemExit('Save Stamina label not found')
html = html.replace(save_label,'',1)

runtime.write_text(js, encoding='utf-8')
index.write_text(html, encoding='utf-8')

# Verification
assert 'value="save"> Save Stamina' not in html
assert "['current','ore','essence','sand'].includes(saved.stamina)" in js
assert 'const staminaGenerated=Math.max(0,Math.floor(wallHours*5));' in js
assert 'const map=yields.map||{};' in js
assert 'Number(map[destination])' in js
