from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')
marker = 'TOOL_ACTION_COLORS_V16'
if marker in text:
    print('Realm Use/Need/Remaining colors already applied.')
    raise SystemExit(0)

# Semantic Realm action colors:
# Use = informational blue/cyan, Need = warning red, Remaining = positive green.
old_use = r'''      lines.push(`<div class="toolSimpleLine"><i>Use:</i><b>${fmt(planRuns)}${planGained>0?` <em>≈ ${fmtCompact(planGained)} ${materialName}</em>`:''}</b></div>`);
'''
new_use = r'''      lines.push(`<div class="toolSimpleLine toolUseLine"><i>Use:</i><b>${fmt(planRuns)}${planGained>0?` <em>≈ ${fmtCompact(planGained)} ${materialName}</em>`:''}</b></div>`);
'''
if text.count(old_use) != 1:
    raise SystemExit(f'Expected one Realm Use display line, found {text.count(old_use)}')
text = text.replace(old_use, new_use, 1)

old_css = r'''/* TOOL_NEED_COLOR_V15: keep the entire Need row red, including the ≈ resource estimate;
   render the entire Remaining row green, including its reserve note. */
.planCosts small.toolBalance .toolNeedLine,
.planCosts small.toolBalance .toolNeedLine i,
.planCosts small.toolBalance .toolNeedLine b,
.planCosts small.toolBalance .toolNeedLine em{color:var(--status-negative,var(--red))!important}
.planCosts small.toolBalance .toolRemainingLine,
.planCosts small.toolBalance .toolRemainingLine i,
.planCosts small.toolBalance .toolRemainingLine b,
.planCosts small.toolBalance .toolRemainingLine em{color:var(--status-positive,var(--green))!important}'''
new_css = r'''/* TOOL_ACTION_COLORS_V16: semantic Realm action colors.
   Use = informational blue/cyan; Need = red; Remaining = green. Keep the whole row consistent. */
.planCosts small.toolBalance .toolUseLine,
.planCosts small.toolBalance .toolUseLine i,
.planCosts small.toolBalance .toolUseLine b,
.planCosts small.toolBalance .toolUseLine em{color:var(--status-info,var(--blue))!important}
.planCosts small.toolBalance .toolNeedLine,
.planCosts small.toolBalance .toolNeedLine i,
.planCosts small.toolBalance .toolNeedLine b,
.planCosts small.toolBalance .toolNeedLine em{color:var(--status-negative,var(--red))!important}
.planCosts small.toolBalance .toolRemainingLine,
.planCosts small.toolBalance .toolRemainingLine i,
.planCosts small.toolBalance .toolRemainingLine b,
.planCosts small.toolBalance .toolRemainingLine em{color:var(--status-positive,var(--green))!important}'''
if text.count(old_css) != 1:
    raise SystemExit(f'Expected one Realm V15 color block, found {text.count(old_css)}')
text = text.replace(old_css, new_css, 1)

path.write_text(text, encoding='utf-8')
print('Applied blue Use, red Need, and green Remaining Realm colors.')
