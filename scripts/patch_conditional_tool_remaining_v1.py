from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
MARK='CONDITIONAL_TOOL_REMAINING_V1'
if MARK in s:
    print('conditional tool remainder already applied')
    raise SystemExit(0)

old='''    // TOOL_SAVED_LEFT_LABEL_V1: this is the user's saved Realm-tool inventory left
    // after the plan, not an additional requirement. Avoid a confusing \"Need\" then
    // \"Remaining\" sequence when extra Realm entries are also required.
    // REMOVE_SAVED_TOOL_LEFT_V1: do not show unused saved-tool remainder in result cards.
    // The card should only tell the user what the plan uses and what additional tools it needs.'''

new='''    // CONDITIONAL_TOOL_REMAINING_V1:
    // Show a remainder only when no additional Realm tools are required. If the plan
    // still has a Need line, suppress the tiny remainder created by whole-tool purchase
    // rounding so the result does not read as Need -> Remaining.
    if(dailyGapRuns<=0 && remainingTools>0){
      lines.push(`<div class="toolSimpleLine toolRemainingLine"><i>Remaining:</i><b>${fmt(remainingTools)} ${remainingToolLabel}${reserveRuns>0?` <em>(${fmt(reserveRuns)} reserved)</em>`:''}</b></div>`);
    }'''

count=s.count(old)
if count<1:
    raise SystemExit('removed remainder marker block not found')
s=s.replace(old,new)
p.write_text(s,encoding='utf-8')
print(f'applied conditional Realm-tool remainder to {count} render block(s)')
