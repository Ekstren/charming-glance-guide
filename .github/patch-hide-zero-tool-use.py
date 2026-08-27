from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')
marker = 'HIDE_ZERO_TOOL_USE_V12'
if marker in text:
    print('Zero-use Realm tool display already fixed.')
    raise SystemExit(0)

old = r'''    if(totalRuns<=0 && missing<=0){ el.innerHTML=''; el.hidden=true; return; }
    // SIMPLE_TOOL_COUNTS_V11: keep this deliberately boring and readable.
    // Used = tools actually consumed now for the current-season target.
    // Remaining includes the S2-reserved subset, shown in parentheses.
    const remainingTools=Math.max(0,left+reserveRuns);
    const lines=[];
    if(totalRuns>0){
      lines.push(`<div class="toolSimpleLine"><i>Use:</i><b>${fmt(planRuns)}${planRuns>0&&planGained>0?` <em>≈ ${fmtCompact(planGained)} ${materialName}</em>`:''}</b></div>`);
      lines.push(`<div class="toolSimpleLine"><i>Remaining:</i><b>${fmt(remainingTools)}${reserveRuns>0?` <em>(${fmt(reserveRuns)} reserved)</em>`:''}</b></div>`);
    }
    if(missing>0){
      lines.push(`<div class="toolSimpleLine toolNeedLine"><i>Still short:</i><b>${fmt(missing)}</b></div>`);
    }
    el.hidden=false;
    el.innerHTML=lines.join('');
    el.classList.add(missing?'toolNeed':'toolLeft');
'''

new = r'''    // HIDE_ZERO_TOOL_USE_V12: shared by Hammers, Knuckles and Shovels.
    // Reserve-only tools affect optimizer math but stay hidden in the result card.
    // Show Use/Remaining only when the current-season recommendation actually spends tools.
    if(planRuns<=0 && missing<=0){ el.innerHTML=''; el.hidden=true; return; }
    const remainingTools=Math.max(0,left+reserveRuns);
    const lines=[];
    if(planRuns>0){
      lines.push(`<div class="toolSimpleLine"><i>Use:</i><b>${fmt(planRuns)}${planGained>0?` <em>≈ ${fmtCompact(planGained)} ${materialName}</em>`:''}</b></div>`);
      lines.push(`<div class="toolSimpleLine"><i>Remaining:</i><b>${fmt(remainingTools)}${reserveRuns>0?` <em>(${fmt(reserveRuns)} reserved)</em>`:''}</b></div>`);
    }
    if(missing>0){
      lines.push(`<div class="toolSimpleLine toolNeedLine"><i>Still short:</i><b>${fmt(missing)}</b></div>`);
    }
    el.hidden=false;
    el.innerHTML=lines.join('');
    el.classList.add(missing?'toolNeed':'toolLeft');
'''

if text.count(old) != 1:
    raise SystemExit(f'Expected exactly one simple tool display block, found {text.count(old)}')
text = text.replace(old, new, 1)
path.write_text(text, encoding='utf-8')
print('Fixed zero-use Realm tool display.')
