from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')
marker = 'SIMPLE_TOOL_COUNTS_V11'
if marker in text:
    print('Simple tool counts already applied.')
    raise SystemExit(0)

start = text.find('    const lines=[];\n    // COMPACT_TOOL_SUMMARY_V9:')
if start < 0:
    raise SystemExit('Compact tool summary block start not found')
end_needle = "    el.classList.add(missing?'toolNeed':'toolLeft');\n"
end = text.find(end_needle, start)
if end < 0:
    raise SystemExit('Compact tool summary block end not found')
end += len(end_needle)

new = r'''    // SIMPLE_TOOL_COUNTS_V11: keep this deliberately boring and readable.
    // Used = tools actually consumed now for the current-season target.
    // Remaining includes the S2-reserved subset, shown in parentheses.
    const remainingTools=Math.max(0,left+reserveRuns);
    const lines=[];
    if(totalRuns>0){
      lines.push(`<div class="toolSimpleLine"><i>Used:</i><b>${fmt(planRuns)}${planRuns>0&&planGained>0?` <em>≈ ${fmtCompact(planGained)} ${materialName}</em>`:''}</b></div>`);
      lines.push(`<div class="toolSimpleLine"><i>Remaining:</i><b>${fmt(remainingTools)}${reserveRuns>0?` <em>(${fmt(reserveRuns)} reserved)</em>`:''}</b></div>`);
    }
    if(missing>0){
      lines.push(`<div class="toolSimpleLine toolNeedLine"><i>Still short:</i><b>${fmt(missing)}</b></div>`);
    }
    el.hidden=false;
    el.innerHTML=lines.join('');
    el.classList.add(missing?'toolNeed':'toolLeft');
'''
text = text[:start] + new + text[end:]

anchor = '</head>'
css = r'''
<style id="simple-tool-counts-v11">
/* SIMPLE_TOOL_COUNTS_V11 */
.planCosts small.toolBalance{
  display:grid!important;
  gap:3px!important;
  margin-top:7px!important;
  padding:7px 0 0!important;
  border-top:1px solid var(--line)!important;
  background:transparent!important;
  border-radius:0!important;
  box-shadow:none!important;
  font-size:9px!important;
  line-height:1.35!important;
}
.planCosts small.toolBalance .toolSimpleLine{
  display:grid!important;
  grid-template-columns:auto minmax(0,1fr)!important;
  gap:8px!important;
  align-items:baseline!important;
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
.planCosts small.toolBalance .toolSimpleLine i{
  color:var(--secondary-text)!important;
  font-style:normal!important;
  font-weight:700!important;
}
.planCosts small.toolBalance .toolSimpleLine b{
  margin:0!important;
  padding:0!important;
  border:0!important;
  background:transparent!important;
  color:var(--status-positive,var(--green))!important;
  font-size:9px!important;
  line-height:1.35!important;
  font-weight:850!important;
  white-space:normal!important;
}
.planCosts small.toolBalance .toolSimpleLine b em{
  color:var(--secondary-text)!important;
  font-size:inherit!important;
  font-style:normal!important;
  font-weight:750!important;
}
.planCosts small.toolBalance .toolNeedLine b{color:var(--status-negative,var(--red))!important}
@media(max-width:720px){
  .planCosts small.toolBalance,
  .planCosts small.toolBalance .toolSimpleLine,
  .planCosts small.toolBalance .toolSimpleLine b{font-size:10px!important}
}
</style>
'''
if anchor not in text:
    raise SystemExit('head close not found')
text = text.replace(anchor, css + '\n' + anchor, 1)
path.write_text(text, encoding='utf-8')
print('Applied simple Realm tool counts.')
