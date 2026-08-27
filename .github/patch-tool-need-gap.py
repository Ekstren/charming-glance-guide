from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')
marker = 'TOOL_ACTION_COLORS_V17'
if marker in text:
    print('Realm action row colors already fully applied.')
    raise SystemExit(0)

old_css = r'''/* TOOL_ACTION_COLORS_V16: semantic Realm action colors.
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

new_css = r'''/* TOOL_ACTION_COLORS_V17: semantic Realm action colors with enough specificity to
   override the older per-element helper styles. Every character on each row shares its state color. */
:root{--realm-use:#2f87aa}
:root[data-theme="dark"]{--realm-use:#6ec8e8}
.planCosts small.toolBalance .toolSimpleLine.toolUseLine,
.planCosts small.toolBalance .toolSimpleLine.toolUseLine i,
.planCosts small.toolBalance .toolSimpleLine.toolUseLine b,
.planCosts small.toolBalance .toolSimpleLine.toolUseLine b em{color:var(--realm-use)!important}
.planCosts small.toolBalance .toolSimpleLine.toolNeedLine,
.planCosts small.toolBalance .toolSimpleLine.toolNeedLine i,
.planCosts small.toolBalance .toolSimpleLine.toolNeedLine b,
.planCosts small.toolBalance .toolSimpleLine.toolNeedLine b em{color:var(--status-negative,var(--red))!important}
.planCosts small.toolBalance .toolSimpleLine.toolRemainingLine,
.planCosts small.toolBalance .toolSimpleLine.toolRemainingLine i,
.planCosts small.toolBalance .toolSimpleLine.toolRemainingLine b,
.planCosts small.toolBalance .toolSimpleLine.toolRemainingLine b em{color:var(--status-positive,var(--green))!important}'''

if text.count(old_css) != 1:
    raise SystemExit(f'Expected one Realm V16 color block, found {text.count(old_css)}')
text = text.replace(old_css, new_css, 1)

path.write_text(text, encoding='utf-8')
print('Applied full-row cyan Use, red Need, and green Remaining colors.')
