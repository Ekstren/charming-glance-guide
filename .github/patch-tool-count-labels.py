from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')
marker = 'TOOL_COUNT_LABELS_V15'
if marker in text:
    print('Material Realm tool-count labels already applied.')
    raise SystemExit(0)

old = r'''    const lines=[];
    if(planRuns>0){
      lines.push(`<div class="toolSimpleLine toolUseLine"><i>Use:</i><b>${fmt(planRuns)}${planGained>0?` <em>≈ ${fmtCompact(planGained)} ${materialName}</em>`:''}</b></div>`);
      if(dailyGapRuns>0){
        lines.push(`<div class="toolSimpleLine toolNeedLine"><i>Need:</i><b>${fmt(dailyGapRuns)} ${toolNeedLabel}${dailyGapValue>0?` <em>≈ ${fmtCompact(dailyGapValue)} ${materialName}</em>`:''}</b></div>`);
      }
      if(remainingTools>0){
        lines.push(`<div class="toolSimpleLine toolRemainingLine"><i>Remaining:</i><b>${fmt(remainingTools)}${reserveRuns>0?` <em>(${fmt(reserveRuns)} reserved)</em>`:''}</b></div>`);
      }
    }
    if(missing>0){
      lines.push(`<div class="toolSimpleLine toolNeedLine"><i>Still short:</i><b>${fmt(missing)}</b></div>`);
    }
'''

new = r'''    // TOOL_COUNT_LABELS_V15: these rows are Material Realm TOOL counts, not raw materials.
    // Always name the tool on Use / Need / Remaining / Still short so the resource card cannot
    // be misread as mixing another raw-material balance into the lower helper section.
    const lines=[];
    const planToolLabel=planRuns===1?toolSingular:label;
    const remainingToolLabel=remainingTools===1?toolSingular:label;
    const missingToolLabel=missing===1?toolSingular:label;
    if(planRuns>0){
      lines.push(`<div class="toolSimpleLine toolUseLine"><i>Use:</i><b>${fmt(planRuns)} ${planToolLabel}${planGained>0?` <em>≈ ${fmtCompact(planGained)} ${materialName}</em>`:''}</b></div>`);
      if(dailyGapRuns>0){
        lines.push(`<div class="toolSimpleLine toolNeedLine"><i>Need:</i><b>${fmt(dailyGapRuns)} ${toolNeedLabel}${dailyGapValue>0?` <em>≈ ${fmtCompact(dailyGapValue)} ${materialName}</em>`:''}</b></div>`);
      }
      if(remainingTools>0){
        lines.push(`<div class="toolSimpleLine toolRemainingLine"><i>Remaining:</i><b>${fmt(remainingTools)} ${remainingToolLabel}${reserveRuns>0?` <em>(${fmt(reserveRuns)} reserved)</em>`:''}</b></div>`);
      }
    }
    if(missing>0){
      lines.push(`<div class="toolSimpleLine toolNeedLine"><i>Still short:</i><b>${fmt(missing)} ${missingToolLabel}</b></div>`);
    }
'''

if text.count(old) != 1:
    raise SystemExit(f'Expected one Material Realm tool-line block, found {text.count(old)}')

text = text.replace(old, new, 1)
path.write_text(text, encoding='utf-8')
print('Added explicit Hammer/Knuckle/Shovel labels to Material Realm tool rows.')
