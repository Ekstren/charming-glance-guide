from pathlib import Path

PATH=Path('index.html')
text=PATH.read_text(encoding='utf-8')
MARKER='TOOL_RESERVE_HOLD_LABEL_V7'
if MARKER in text:
    print('Tool reserve wording already applied.')
    raise SystemExit(0)

old=r'''    const displayPer=reserveRuns>0&&reservePer>0
      ? reservePer
      : Math.max(0,Number(planPer||yieldVal)||0);
    const gained=totalRuns*displayPer;
    const leftValue=left*displayPer;
    const required=Math.max(0,Math.floor(Number(top?.runsNeeded)||totalRuns));
    const maxRuns=Math.max(0,Math.floor(Number(top?.maxRuns)||0));
    const missing=Math.max(0,required-maxRuns);

    if(totalRuns<=0 && missing<=0){ el.innerHTML=''; el.hidden=true; return; }
    const lines=[];
    if(totalRuns>0){
      lines.push(`<span class="toolUsageRow toolUsedLine"><i>Use</i><b>${fmt(totalRuns)} ${label}${gained>0?` ≈ ${fmtCompact(gained)} ${materialName}`:''}</b></span>`);
      lines.push(`<span class="toolUsageRow toolRemainingLine"><i>Left</i><b>${fmt(left)} ${label} ≈ ${leftValue>0?`${fmtCompact(leftValue)} ${materialName}`:'0'}</b></span>`);
    }
    if(missing>0) lines.push(`<span class="toolUsageRow toolNeedLine"><i>Still short</i><b>${fmt(missing)} ${label}</b><em></em></span>`);
    el.hidden=false; el.innerHTML=lines.join('');
    el.classList.add(missing?'toolNeed':'toolLeft');
'''

new=r'''    // TOOL_RESERVE_HOLD_LABEL_V7: distinguish tools actually consumed for the
    // current-season plan from tools merely allocated to the S2 reserve. This keeps the
    // card from telling the player to "Use" tools that should stay banked for rollover.
    const planDisplayPer=Math.max(0,Number(planPer||yieldVal)||0);
    const reserveDisplayPer=Math.max(0,Number(reservePer)||0);
    const leftDisplayPer=reserveRuns>0&&reserveDisplayPer>0
      ? reserveDisplayPer
      : planDisplayPer;
    const planGained=planRuns*planDisplayPer;
    const reserveValue=reserveRuns*reserveDisplayPer;
    const leftValue=left*leftDisplayPer;
    const required=Math.max(0,Math.floor(Number(top?.runsNeeded)||totalRuns));
    const maxRuns=Math.max(0,Math.floor(Number(top?.maxRuns)||0));
    const missing=Math.max(0,required-maxRuns);

    if(totalRuns<=0 && missing<=0){ el.innerHTML=''; el.hidden=true; return; }
    const lines=[];
    if(planRuns>0){
      lines.push(`<span class="toolUsageRow toolUsedLine"><i>Use</i><b>${fmt(planRuns)} ${label}${planGained>0?` ≈ ${fmtCompact(planGained)} ${materialName}`:''}</b></span>`);
    }
    if(reserveRuns>0){
      lines.push(`<span class="toolUsageRow toolReserveLine"><i>S2 reserve</i><b>Hold ${fmt(reserveRuns)} ${label}${reserveValue>0?` ≈ ${fmtCompact(reserveValue)} ${materialName}`:''}</b></span>`);
    }
    if(totalRuns>0){
      lines.push(`<span class="toolUsageRow toolRemainingLine"><i>Left</i><b>${fmt(left)} ${label} ≈ ${leftValue>0?`${fmtCompact(leftValue)} ${materialName}`:'0'}</b></span>`);
    }
    if(missing>0) lines.push(`<span class="toolUsageRow toolNeedLine"><i>Still short</i><b>${fmt(missing)} ${label}</b><em></em></span>`);
    el.hidden=false; el.innerHTML=lines.join('');
    el.classList.add(missing?'toolNeed':'toolLeft');
'''

if text.count(old)!=1:
    raise SystemExit(f'tool display block count={text.count(old)}')
text=text.replace(old,new,1)
PATH.write_text(text,encoding='utf-8')
print('Applied S1-use vs S2-reserve tool wording.')
