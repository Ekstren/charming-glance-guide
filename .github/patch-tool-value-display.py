from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')
marker = 'TOOL_VALUE_DISPLAY_V5'
if marker in text:
    print('Tool value display already applied.')
    raise SystemExit(0)

old = r'''    const gained=Math.max(0,planRuns*planPer+reserveRuns*reservePer);
    const left=Math.max(0,Math.floor(Number(top?.bankedRemaining)||0)+Math.floor(Number(top?.sparePurchasedRuns)||0));
    const leftPer=Math.max(0,Number(yieldVal)||0);
    const leftValue=left*leftPer;
    const required=Math.max(0,Math.floor(Number(top?.runsNeeded)||totalRuns));'''
new = r'''    const gained=Math.max(0,planRuns*planPer+reserveRuns*reservePer);
    const left=Math.max(0,Math.floor(Number(top?.bankedRemaining)||0)+Math.floor(Number(top?.sparePurchasedRuns)||0));
    // TOOL_VALUE_DISPLAY_V5: if tools are being carried/used for an S2 reserve, value the
    // leftover tools at that same S2 rate so the Used and Left rows do not mix seasons.
    const leftPer=reserveRuns>0&&reservePer>0
      ? reservePer
      : Math.max(0,Number(planPer||yieldVal)||0);
    const leftValue=left*leftPer;
    const required=Math.max(0,Math.floor(Number(top?.runsNeeded)||totalRuns));'''
if old not in text:
    raise SystemExit('tool value block not found')
text = text.replace(old, new, 1)

old_rows = r'''    if(totalRuns>0){
      lines.push(`<span class="toolUsageRow toolUsedLine"><i>Use</i><b>${fmt(totalRuns)} ${label}</b><em>${gained>0?`≈${fmtCompact(gained)} ${materialName}`:''}</em></span>`);
      lines.push(`<span class="toolUsageRow toolRemainingLine"><i>Left</i><b>${fmt(left)} ${label}</b><em>${leftValue>0?`≈${fmtCompact(leftValue)} ${materialName}`:'≈0'}</em></span>`);
    }'''
new_rows = r'''    if(totalRuns>0){
      lines.push(`<span class="toolUsageRow toolUsedLine"><i>Use</i><b>${fmt(totalRuns)} ${label}${gained>0?` ≈ ${fmtCompact(gained)} ${materialName}`:''}</b></span>`);
      lines.push(`<span class="toolUsageRow toolRemainingLine"><i>Left</i><b>${fmt(left)} ${label} ≈ ${leftValue>0?`${fmtCompact(leftValue)} ${materialName}`:'0'}</b></span>`);
    }'''
if old_rows not in text:
    raise SystemExit('tool row block not found')
text = text.replace(old_rows, new_rows, 1)

path.write_text(text, encoding='utf-8')
print('Updated tool rows and consistent value basis.')
