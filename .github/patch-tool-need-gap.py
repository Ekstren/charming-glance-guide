from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')
marker = 'TOOL_DAILY_GAP_V13'
if marker in text:
    print('Realm tool daily-gap display already applied.')
    raise SystemExit(0)

old = r'''    // HIDE_ZERO_TOOL_USE_V12: shared by Hammers, Knuckles and Shovels.
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

new = r'''    // TOOL_DAILY_GAP_V13: shared by Hammers, Knuckles and Shovels.
    // Reserve-only tools stay hidden unless the current-season plan actually uses this tool.
    // Need = additional tool entries required beyond the CURRENT daily refresh plan. It falls
    // as the user raises that daily setting and disappears once the configured plan covers it.
    if(planRuns<=0 && missing<=0){ el.innerHTML=''; el.hidden=true; return; }
    const remainingTools=Math.max(0,left+reserveRuns);
    const dailyGapRuns=Math.max(0,Math.floor(Number(top?.paidRunsUsed)||0));
    const toolSingular=label==='Hammers'?'Hammer':label==='Knuckles'?'Knuckle':label==='Shovels'?'Shovel':'tool';
    const toolNeedLabel=dailyGapRuns===1?toolSingular:label;
    const lines=[];
    if(planRuns>0){
      lines.push(`<div class="toolSimpleLine"><i>Use:</i><b>${fmt(planRuns)}${planGained>0?` <em>≈ ${fmtCompact(planGained)} ${materialName}</em>`:''}</b></div>`);
      if(dailyGapRuns>0){
        lines.push(`<div class="toolSimpleLine toolNeedLine"><i>Need:</i><b>${fmt(dailyGapRuns)} ${toolNeedLabel}</b></div>`);
      }
      if(remainingTools>0){
        lines.push(`<div class="toolSimpleLine"><i>Remaining:</i><b>${fmt(remainingTools)}${reserveRuns>0?` <em>(${fmt(reserveRuns)} reserved)</em>`:''}</b></div>`);
      }
    }
    if(missing>0){
      lines.push(`<div class="toolSimpleLine toolNeedLine"><i>Still short:</i><b>${fmt(missing)}</b></div>`);
    }
    el.hidden=false;
    el.innerHTML=lines.join('');
    el.classList.add((missing>0||dailyGapRuns>0)?'toolNeed':'toolLeft');
'''

if old not in text:
    raise SystemExit('Current Realm tool display block not found')
text = text.replace(old, new, 1)

css_old = '.planCosts small.toolBalance .toolNeedLine b{color:var(--status-negative,var(--red))!important}'
css_new = '.planCosts small.toolBalance .toolNeedLine,\n.planCosts small.toolBalance .toolNeedLine i,\n.planCosts small.toolBalance .toolNeedLine b{color:var(--status-negative,var(--red))!important}'
if css_old not in text:
    raise SystemExit('Realm tool need color rule not found')
text = text.replace(css_old, css_new, 1)

path.write_text(text, encoding='utf-8')
print('Applied Realm tool daily-gap display.')
