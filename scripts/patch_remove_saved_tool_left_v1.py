from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
MARK='REMOVE_SAVED_TOOL_LEFT_V1'
if MARK in s:
    print('saved-tool remainder line already removed')
    raise SystemExit(0)

old='''    if(remainingTools>0){\n      lines.push(`<div class="toolSimpleLine toolRemainingLine"><i>Saved left:</i><b>${fmt(remainingTools)} ${remainingToolLabel}${reserveRuns>0?` <em>(${fmt(reserveRuns)} reserved)</em>`:''}</b></div>`);\n    }'''
if old not in s:
    old='''    if(remainingTools>0){\n      lines.push(`<div class="toolSimpleLine toolRemainingLine"><i>Remaining:</i><b>${fmt(remainingTools)} ${remainingToolLabel}${reserveRuns>0?` <em>(${fmt(reserveRuns)} reserved)</em>`:''}</b></div>`);\n    }'''
if old not in s:
    raise SystemExit('saved-tool remainder render block not found')

new='''    // REMOVE_SAVED_TOOL_LEFT_V1: do not show unused saved-tool remainder in result cards.\n    // The card should only tell the user what the plan uses and what additional tools it needs.'''
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')
print('removed saved Realm-tool remainder line from result cards')
