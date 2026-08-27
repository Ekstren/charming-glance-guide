from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')
marker = 'PLAIN_TOOL_LINES_V10'
if marker in text:
    print('Plain tool lines already applied.')
    raise SystemExit(0)

old = r'''      toolParts.push(`<b class="toolFree">${fmt(left)} free${leftValue>0?` ≈ ${fmtCompact(leftValue)} ${materialName}`:''}</b>`);'''
new = r'''      toolParts.push(`<b class="toolFree">${fmt(left)} left${leftValue>0?` ≈ ${fmtCompact(leftValue)} ${materialName}`:''}</b>`);'''
if old not in text:
    raise SystemExit('toolFree line not found')
text = text.replace(old, new, 1)

anchor = '</head>'
css = r'''
<style id="plain-tool-lines-v10">
/* PLAIN_TOOL_LINES_V10
   Realm-tool actions are quiet helper text, not nested result cards. Specific !important
   overrides intentionally beat the older mobile .planCosts span/b rules. */
.planCosts small.toolBalance{
  display:block!important;
  margin-top:7px!important;
  padding:7px 0 0!important;
  border-top:1px solid var(--line)!important;
  background:transparent!important;
  border-radius:0!important;
  box-shadow:none!important;
  font-size:9px!important;
  line-height:1.35!important;
}
.planCosts small.toolBalance .toolCompactLine{
  display:grid!important;
  grid-template-columns:1fr!important;
  gap:3px!important;
  margin:0!important;
  padding:0!important;
  border:0!important;
  border-radius:0!important;
  background:transparent!important;
  box-shadow:none!important;
  color:var(--secondary-text)!important;
  font-size:9px!important;
  line-height:1.35!important;
}
.planCosts small.toolBalance .toolCompactLine b{
  display:block!important;
  margin:0!important;
  padding:0!important;
  border:0!important;
  border-radius:0!important;
  background:transparent!important;
  box-shadow:none!important;
  font-size:9px!important;
  line-height:1.35!important;
  font-weight:800!important;
  white-space:normal!important;
}
.planCosts small.toolBalance .toolCompactLine .toolSpend{color:var(--status-positive,var(--green))!important}
.planCosts small.toolBalance .toolCompactLine .toolHold{color:var(--status-info,var(--secondary-text))!important}
.planCosts small.toolBalance .toolCompactLine .toolFree{color:var(--secondary-text)!important;font-weight:750!important}
.planCosts small.toolBalance .toolCompactLine .toolSep{display:none!important}
.planCosts small.toolBalance .toolNeedLine{
  display:block!important;
  margin:3px 0 0!important;
  padding:0!important;
  border:0!important;
  background:transparent!important;
  font-size:9px!important;
  line-height:1.35!important;
}
@media(max-width:720px){
  .planCosts small.toolBalance,
  .planCosts small.toolBalance .toolCompactLine,
  .planCosts small.toolBalance .toolCompactLine b,
  .planCosts small.toolBalance .toolNeedLine{font-size:10px!important}
}
</style>
'''
if anchor not in text:
    raise SystemExit('head close not found')
text = text.replace(anchor, css + '\n' + anchor, 1)
path.write_text(text, encoding='utf-8')
print('Applied plain Realm tool helper lines.')
