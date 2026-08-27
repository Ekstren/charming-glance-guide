from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')
marker = 'TOOL_NEED_COLOR_V15'
if marker in text:
    print('Realm Need/Remaining color polish already applied.')
    raise SystemExit(0)

# Keep the material estimate on the Need row red with the rest of that row,
# and give Remaining its own positive/green row styling.
old_remaining = r'''        lines.push(`<div class="toolSimpleLine"><i>Remaining:</i><b>${fmt(remainingTools)}${reserveRuns>0?` <em>(${fmt(reserveRuns)} reserved)</em>`:''}</b></div>`);
'''
new_remaining = r'''        lines.push(`<div class="toolSimpleLine toolRemainingLine"><i>Remaining:</i><b>${fmt(remainingTools)}${reserveRuns>0?` <em>(${fmt(reserveRuns)} reserved)</em>`:''}</b></div>`);
'''
if text.count(old_remaining) != 1:
    raise SystemExit(f'Expected one Realm Remaining display line, found {text.count(old_remaining)}')
text = text.replace(old_remaining, new_remaining, 1)

old_css = r'''.planCosts small.toolBalance .toolNeedLine,
.planCosts small.toolBalance .toolNeedLine i,
.planCosts small.toolBalance .toolNeedLine b{color:var(--status-negative,var(--red))!important}'''
new_css = r'''/* TOOL_NEED_COLOR_V15: keep the entire Need row red, including the ≈ resource estimate;
   render the entire Remaining row green, including its reserve note. */
.planCosts small.toolBalance .toolNeedLine,
.planCosts small.toolBalance .toolNeedLine i,
.planCosts small.toolBalance .toolNeedLine b,
.planCosts small.toolBalance .toolNeedLine em{color:var(--status-negative,var(--red))!important}
.planCosts small.toolBalance .toolRemainingLine,
.planCosts small.toolBalance .toolRemainingLine i,
.planCosts small.toolBalance .toolRemainingLine b,
.planCosts small.toolBalance .toolRemainingLine em{color:var(--status-positive,var(--green))!important}'''
if text.count(old_css) != 1:
    raise SystemExit(f'Expected one Realm Need color rule, found {text.count(old_css)}')
text = text.replace(old_css, new_css, 1)

path.write_text(text, encoding='utf-8')
print('Kept Realm Need fully red and made Remaining fully green.')
