from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')
marker = 'COMPACT_TOOL_SUMMARY_V9'
if marker in text:
    print('Compact tool summary already applied.')
    raise SystemExit(0)

old = r'''    const lines=[];
    // TOOL_ACTION_LABELS_V8: short action labels. Spend = consume now for S1;
    // Hold = keep banked to satisfy the enabled S2 reserve.
    if(planRuns>0){
      lines.push(`<span class="toolUsageRow toolUsedLine"><i>Spend</i><b>${fmt(planRuns)} ${label}${planGained>0?` ≈ ${fmtCompact(planGained)} ${materialName}`:''}</b></span>`);
    }
    if(reserveRuns>0){
      lines.push(`<span class="toolUsageRow toolReserveLine"><i>Hold</i><b>${fmt(reserveRuns)} ${label}${reserveValue>0?` ≈ ${fmtCompact(reserveValue)} ${materialName}`:''}</b></span>`);
    }
    if(totalRuns>0){
      lines.push(`<span class="toolUsageRow toolRemainingLine"><i>Left</i><b>${fmt(left)} ${label} ≈ ${leftValue>0?`${fmtCompact(leftValue)} ${materialName}`:'0'}</b></span>`);
    }
    if(missing>0) lines.push(`<span class="toolUsageRow toolNeedLine"><i>Still short</i><b>${fmt(missing)} ${label}</b><em></em></span>`);
    el.hidden=false; el.innerHTML=lines.join('');
    el.classList.add(missing?'toolNeed':'toolLeft');
'''

new = r'''    const lines=[];
    // COMPACT_TOOL_SUMMARY_V9: keep Realm tool actions on one compact, wrapping helper line.
    // Spend = consume now for the S1 target. Hold = keep banked for the enabled S2 reserve.
    // Free = tools left after both commitments.
    const toolParts=[];
    if(planRuns>0){
      toolParts.push(`<b class="toolSpend">Spend ${fmt(planRuns)} ${label}${planGained>0?` ≈ ${fmtCompact(planGained)} ${materialName}`:''}</b>`);
    }
    if(reserveRuns>0){
      toolParts.push(`<b class="toolHold">Hold ${fmt(reserveRuns)} ${label}${reserveValue>0?` ≈ ${fmtCompact(reserveValue)} ${materialName}`:''}</b>`);
    }
    if(totalRuns>0){
      toolParts.push(`<b class="toolFree">${fmt(left)} free${leftValue>0?` ≈ ${fmtCompact(leftValue)} ${materialName}`:''}</b>`);
    }
    if(toolParts.length){
      lines.push(`<span class="toolCompactLine">${toolParts.join('<i class="toolSep">·</i>')}</span>`);
    }
    if(missing>0) lines.push(`<span class="toolUsageRow toolNeedLine"><i>Still short</i><b>${fmt(missing)} ${label}</b><em></em></span>`);
    el.hidden=false; el.innerHTML=lines.join('');
    el.classList.add(missing?'toolNeed':'toolLeft');
'''

if text.count(old) != 1:
    raise SystemExit(f'Expected one TOOL_ACTION_LABELS_V8 block, found {text.count(old)}')
text = text.replace(old, new, 1)

css_anchor = '''<style id="v59-treat-timezone-polish">'''
css = r'''<style id="compact-tool-summary-v9">
.planCosts small.toolBalance{display:block!important;line-height:1.35}
.planCosts small.toolBalance .toolCompactLine{display:flex;flex-wrap:wrap;align-items:baseline;gap:2px 5px;color:var(--secondary-text);font-size:8px;font-weight:750}
.planCosts small.toolBalance .toolCompactLine b{font-size:inherit;line-height:inherit;font-weight:800}
.planCosts small.toolBalance .toolCompactLine .toolSpend{color:var(--status-positive,var(--green))}
.planCosts small.toolBalance .toolCompactLine .toolHold{color:var(--status-info,var(--blue))}
.planCosts small.toolBalance .toolCompactLine .toolFree{color:var(--secondary-text)}
.planCosts small.toolBalance .toolCompactLine .toolSep{color:var(--muted);font-style:normal;font-weight:500}
.planCosts small.toolBalance .toolNeedLine{display:block;margin-top:3px}
@media(max-width:520px){.planCosts small.toolBalance .toolCompactLine{font-size:8px;gap:2px 4px}}
</style>

'''
if css_anchor not in text:
    raise SystemExit('CSS anchor not found')
text = text.replace(css_anchor, css + css_anchor, 1)

path.write_text(text, encoding='utf-8')
print('Applied compact Realm tool summary.')
