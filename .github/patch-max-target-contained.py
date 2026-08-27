from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')
marker = 'MAX_TARGET_CONTAINED_V1'
if marker in s:
    print('already applied')
    raise SystemExit(0)

old = '<div class="findMaxCell"><span>Maximum target</span><button id="findMaxStars" type="button">Find max achievable</button><small id="maxAchievableStatus"></small></div>'
new = '<div class="findMaxCell"><span>Maximum target</span><div class="maxTargetControl"><button id="findMaxStars" type="button">Find max achievable</button><small id="maxAchievableStatus"></small></div></div>'
if old not in s:
    raise SystemExit('max target cell HTML not found')
s = s.replace(old, new, 1)

css = '''\n<style id="max-target-contained-v1">\n/* MAX_TARGET_CONTAINED_V1 */\n.calcGrid .findMaxCell .maxTargetControl{border:1px solid var(--today-border);background:var(--today-bg);border-radius:10px;min-height:38px;padding:6px 10px;display:grid;align-content:center;gap:2px;min-width:0}\n.calcGrid .findMaxCell .maxTargetControl button{border:0!important;background:transparent!important;border-radius:0!important;min-height:0!important;padding:0!important;text-align:left;color:var(--ink);font-size:10px;font-weight:850}\n.calcGrid .findMaxCell .maxTargetControl:hover{border-color:var(--green)}\n.calcGrid .findMaxCell .maxTargetControl:hover button{color:var(--green)}\n.calcGrid .findMaxCell .maxTargetControl small{margin:0;color:var(--muted);font-size:8px;line-height:1.25;white-space:normal}\n.calcGrid .findMaxCell .maxTargetControl small strong{color:var(--green)}\n@media(max-width:700px){.calcGrid .findMaxCell .maxTargetControl button{text-align:center}}\n</style>\n'''
if '</head>' not in s:
    raise SystemExit('head close not found')
s = s.replace('</head>', css + '</head>', 1)
p.write_text(s, encoding='utf-8')
print('applied')
