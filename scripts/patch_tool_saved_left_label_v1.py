from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
mark='TOOL_SAVED_LEFT_LABEL_V1'
if mark in s:
    print('tool remainder label already clarified')
    raise SystemExit(0)

old='''    if(remainingTools>0){
      lines.push(`<div class="toolSimpleLine toolRemainingLine"><i>Remaining:</i><b>${fmt(remainingTools)} ${remainingToolLabel}${reserveRuns>0?` <em>(${fmt(reserveRuns)} reserved)</em>`:''}</b></div>`);
    }'''
new='''    // TOOL_SAVED_LEFT_LABEL_V1: this is the user's saved Realm-tool inventory left
    // after the plan, not an additional requirement. Avoid a confusing "Need" then
    // "Remaining" sequence when extra Realm entries are also required.
    if(remainingTools>0){
      lines.push(`<div class="toolSimpleLine toolRemainingLine"><i>Saved left:</i><b>${fmt(remainingTools)} ${remainingToolLabel}${reserveRuns>0?` <em>(${fmt(reserveRuns)} reserved)</em>`:''}</b></div>`);
    }'''
if old not in s:
    raise SystemExit('tool remainder render anchor not found')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')
print('renamed Realm tool Remaining to Saved left')
