from pathlib import Path
import re

p=Path('index.html')
s=p.read_text(encoding='utf-8')
marker='/* CALCULATOR_COMPACT_LAYOUT_V1 */'
if marker in s:
    raise SystemExit('compact calculator layout already applied')

# Remove the visible Refined Ore expander but keep a hidden field so existing math/state code stays safe.
pat=re.compile(r'''\s*<details class=\\?"accuracyInputs\\?">\s*<summary><span>Optional Refined Ore tracking</span><small>Only needed for the \+5 milestone hard check</small></summary>\s*<div class=\\?"accuracyInputsBody\\?">\s*<div class=\\?"accuracyGrid refinedOnlyGrid\\?">\s*<label>Refined Ore on hand <small>\(optional hard check\)</small><input id=\\?"refinedOreCurrent\\?" type=\\?"number\\?" min=\\?"0\\?" step=\\?"1\\?" placeholder=\\?"Leave blank if not tracking\\?"></label>\s*</div>\s*</div>\s*</details>''', re.S)
m=pat.search(s)
if not m:
    raise SystemExit('refined ore UI block not found')
s=s[:m.start()]+'\n          <input id="refinedOreCurrent" type="hidden" value="">'+s[m.end():]

css=r'''
<style id="calculator-compact-layout">
/* CALCULATOR_COMPACT_LAYOUT_V1
   Reduce dead space in the main calculator editor and Material Realm sections. */
@media (min-width:701px){
  .calcInputs{gap:8px!important}
  .calcPanel{padding:16px!important}
  .calcPanel h3{margin-bottom:11px!important}
  .calcGrid{gap:8px 10px!important}
  .calcGrid label{gap:4px!important}
  .calcGrid input,.calcGrid select{min-height:38px!important;padding:7px 10px!important}

  .projectionCallout.projectionInline{margin-top:8px!important;padding:7px 10px!important;min-height:0!important}
  .seasonDeadline{margin-top:8px!important;padding:8px 10px!important}
  .seasonPlanningControls{margin-top:8px!important;padding:8px 10px!important;gap:10px!important}

  .currentLevelsBody{padding:14px 16px 16px!important}
  .resourceCards{gap:7px!important}
  .resourceCards>.resourceCard{padding:9px 10px!important;gap:7px!important}
  .resourceCardFields{gap:6px!important}
  .resourceCardFields input{min-height:38px!important;padding:7px 9px!important}
  .treatEquivalent{margin-top:0!important}

  .realmInventory{margin-top:9px!important;padding:11px 13px!important}
  .realmInventoryTop{margin-bottom:7px!important}
  .realmInventoryGrid{gap:8px!important}
  .realmInventoryGrid input{min-height:40px!important;margin-top:4px!important;padding:8px 10px!important}
  .realmInventoryGrid label>small{margin-top:4px!important;line-height:1.3!important}

  .realmDailyPlanRow{gap:10px!important;margin-top:10px!important;padding-top:10px!important;align-items:start!important}
  .realmDailyTitle{margin-bottom:6px!important}
  .realmDailyInputs{gap:6px!important}
  .realmDailyInputs input{min-height:40px!important;margin-top:4px!important;padding:8px 10px!important}
  .realmDailyInputs small{margin-top:4px!important}
  .realmPlanSummary{min-height:58px!important;padding:8px 10px!important;align-self:end!important}
}
</style>
'''
if '</head>' not in s:
    raise SystemExit('head closing tag not found')
s=s.replace('</head>',css+'\n</head>',1)
p.write_text(s,encoding='utf-8')
print('Removed visible Refined Ore tracking and compacted calculator spacing.')
# trigger
