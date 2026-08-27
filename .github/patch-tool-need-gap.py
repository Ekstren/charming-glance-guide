from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')
marker = 'TOOL_NEED_VALUE_V14'
if marker in text:
    print('Realm tool Need resource estimate already applied.')
    raise SystemExit(0)

old_setup = r'''    const dailyGapRuns=Math.max(0,Math.floor(Number(top?.paidRunsUsed)||0));
    const toolSingular=label==='Hammers'?'Hammer':label==='Knuckles'?'Knuckle':label==='Shovels'?'Shovel':'tool';
    const toolNeedLabel=dailyGapRuns===1?toolSingular:label;
    const lines=[];
'''
new_setup = r'''    const dailyGapRuns=Math.max(0,Math.floor(Number(top?.paidRunsUsed)||0));
    const toolSingular=label==='Hammers'?'Hammer':label==='Knuckles'?'Knuckle':label==='Shovels'?'Shovel':'tool';
    const toolNeedLabel=dailyGapRuns===1?toolSingular:label;
    // TOOL_NEED_VALUE_V14: show the material-equivalent value beside Need, matching Use.
    // If the gap exists to preserve an enabled rollover reserve, value those tools at the
    // reserve yield; otherwise use the current-season Material Realm yield.
    const dailyGapDisplayPer=reserveRuns>0&&reserveDisplayPer>0?reserveDisplayPer:planDisplayPer;
    const dailyGapValue=dailyGapRuns*dailyGapDisplayPer;
    const lines=[];
'''
if text.count(old_setup) != 1:
    raise SystemExit(f'Expected one Realm Need setup block, found {text.count(old_setup)}')
text = text.replace(old_setup, new_setup, 1)

old_need = r'''        lines.push(`<div class="toolSimpleLine toolNeedLine"><i>Need:</i><b>${fmt(dailyGapRuns)} ${toolNeedLabel}</b></div>`);
'''
new_need = r'''        lines.push(`<div class="toolSimpleLine toolNeedLine"><i>Need:</i><b>${fmt(dailyGapRuns)} ${toolNeedLabel}${dailyGapValue>0?` <em>≈ ${fmtCompact(dailyGapValue)} ${materialName}</em>`:''}</b></div>`);
'''
if text.count(old_need) != 1:
    raise SystemExit(f'Expected one Realm Need display line, found {text.count(old_need)}')
text = text.replace(old_need, new_need, 1)

path.write_text(text, encoding='utf-8')
print('Added material-equivalent value to Realm Need display.')
