from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')
base_marker = 'MAX_TARGET_CONTAINED_V1'
line_marker = 'MAX_TARGET_ONE_LINE_V2'
size_marker = 'MAX_TARGET_PLAN_TEXT_SIZE_V1'

# Preserve the original contained control migration for older copies of the page.
if base_marker not in s:
    old = '<div class="findMaxCell"><span>Maximum target</span><button id="findMaxStars" type="button">Find max achievable</button><small id="maxAchievableStatus"></small></div>'
    new = '<div class="findMaxCell"><span>Maximum target</span><div class="maxTargetControl"><button id="findMaxStars" type="button">Find max achievable</button><small id="maxAchievableStatus"></small></div></div>'
    if old not in s:
        raise SystemExit('max target cell HTML not found')
    s = s.replace(old, new, 1)

    base_css = '''\n<style id="max-target-contained-v1">\n/* MAX_TARGET_CONTAINED_V1 */\n.calcGrid .findMaxCell .maxTargetControl{border:1px solid var(--today-border);background:var(--today-bg);border-radius:10px;min-height:38px;padding:6px 10px;display:grid;align-content:center;gap:2px;min-width:0}\n.calcGrid .findMaxCell .maxTargetControl button{border:0!important;background:transparent!important;border-radius:0!important;min-height:0!important;padding:0!important;text-align:left;color:var(--ink);font-size:10px;font-weight:850}\n.calcGrid .findMaxCell .maxTargetControl:hover{border-color:var(--green)}\n.calcGrid .findMaxCell .maxTargetControl:hover button{color:var(--green)}\n.calcGrid .findMaxCell .maxTargetControl small{margin:0;color:var(--muted);font-size:8px;line-height:1.25;white-space:normal}\n.calcGrid .findMaxCell .maxTargetControl small strong{color:var(--green)}\n@media(max-width:700px){.calcGrid .findMaxCell .maxTargetControl button{text-align:center}}\n</style>\n'''
    if '</head>' not in s:
        raise SystemExit('head close not found')
    s = s.replace('</head>', base_css + '</head>', 1)

# Keep the action and the calculated limits together on one readable row.
if line_marker not in s:
    line_css = '''\n<style id="max-target-one-line-v2">\n/* MAX_TARGET_ONE_LINE_V2 */\n.calcGrid .findMaxCell .maxTargetControl{display:flex!important;align-items:center;gap:8px;white-space:nowrap;overflow:hidden}\n.calcGrid .findMaxCell .maxTargetControl button{flex:0 0 auto;white-space:nowrap}\n.calcGrid .findMaxCell .maxTargetControl small{flex:1 1 auto;min-width:0;white-space:nowrap!important;line-height:1.2}\n@media(max-width:700px){\n  .calcGrid .findMaxCell .maxTargetControl{gap:6px}\n  .calcGrid .findMaxCell .maxTargetControl button{text-align:left!important;font-size:9px}\n  .calcGrid .findMaxCell .maxTargetControl small{font-size:7px}\n}\n</style>\n'''
    if '</head>' not in s:
        raise SystemExit('head close not found')
    s = s.replace('</head>', line_css + '</head>', 1)

# Make the selected-plan / hard-cap summary easier to read without allowing it to wrap.
if size_marker not in s:
    size_css = '''\n<style id="max-target-plan-text-size-v1">\n/* MAX_TARGET_PLAN_TEXT_SIZE_V1 */\n.calcGrid .findMaxCell .maxTargetControl small{font-size:10px!important;font-weight:600;color:var(--secondary-text);line-height:1.2}\n@media(max-width:700px){.calcGrid .findMaxCell .maxTargetControl small{font-size:8.5px!important}}\n</style>\n'''
    if '</head>' not in s:
        raise SystemExit('head close not found')
    s = s.replace('</head>', size_css + '</head>', 1)

p.write_text(s, encoding='utf-8')
print('applied max target contained, one-line, and readable plan text styles')
