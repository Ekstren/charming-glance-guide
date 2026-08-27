from pathlib import Path

p=Path('index.html')
text=p.read_text(encoding='utf-8')
marker='TOOL_ACTION_LABELS_V8'
if marker in text:
    print('Tool action labels already current.')
    raise SystemExit(0)

old='''    if(planRuns>0){\n      lines.push(`<span class="toolUsageRow toolUsedLine"><i>Use</i><b>${fmt(planRuns)} ${label}${planGained>0?` ≈ ${fmtCompact(planGained)} ${materialName}`:''}</b></span>`);\n    }\n    if(reserveRuns>0){\n      lines.push(`<span class="toolUsageRow toolReserveLine"><i>S2 reserve</i><b>Hold ${fmt(reserveRuns)} ${label}${reserveValue>0?` ≈ ${fmtCompact(reserveValue)} ${materialName}`:''}</b></span>`);\n    }'''
new='''    // TOOL_ACTION_LABELS_V8: short action labels. Spend = consume now for S1;\n    // Hold = keep banked to satisfy the enabled S2 reserve.\n    if(planRuns>0){\n      lines.push(`<span class="toolUsageRow toolUsedLine"><i>Spend</i><b>${fmt(planRuns)} ${label}${planGained>0?` ≈ ${fmtCompact(planGained)} ${materialName}`:''}</b></span>`);\n    }\n    if(reserveRuns>0){\n      lines.push(`<span class="toolUsageRow toolReserveLine"><i>Hold</i><b>${fmt(reserveRuns)} ${label}${reserveValue>0?` ≈ ${fmtCompact(reserveValue)} ${materialName}`:''}</b></span>`);\n    }'''
if text.count(old)!=1:
    raise SystemExit(f'action-label block count={text.count(old)}')
text=text.replace(old,new,1)
p.write_text(text,encoding='utf-8')
print('Changed tool actions to Spend / Hold / Left.')
