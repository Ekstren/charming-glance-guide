from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
marker='/* CALC_HEADER_CLEANUP_V1 */'
if marker in s:
    raise SystemExit('calculator cleanup already applied')

# Put the projected season-end level directly beneath the XP/input grid.
old='''          <label>Current character level<input id="charLevel" type="number" value="100"></label>\n          <label>Current EXP into level<input id="charExp" type="number" value="0"></label>\n          <label>Bed EXP per hour<input id="bedExp" type="number" value="0"></label>\n          <label class="freeSpeedToggle">Daily free speed-up<span class="freeSpeedCheck"><input id="freeSpeed" type="checkbox" checked> Use free 2-hour boost every reset</span></label>\n        </div>\n        <div class="seasonDeadline">'''
new='''          <label>Current character level<input id="charLevel" type="number" value="100"></label>\n          <label>Current EXP into level<input id="charExp" type="number" value="0"></label>\n          <label>Bed EXP per hour<input id="bedExp" type="number" value="0"></label>\n          <label class="freeSpeedToggle">Daily free speed-up<span class="freeSpeedCheck"><input id="freeSpeed" type="checkbox" checked> Use free 2-hour boost every reset</span></label>\n        </div>\n        <div class="projectionCallout projectionInline"><span>Projected season-end level</span><strong id="projectedCharacter">—</strong><small id="projectionNote" hidden></small></div>\n        <div class="seasonDeadline">'''
if old not in s:
    raise SystemExit('character input grid anchor not found')
s=s.replace(old,new,1)

# Keep elements needed by existing JS/calculation state, but remove the noisy UI called out by the user.
old_hint='<div class="seasonDeadline"><span id="seasonDeadlineLabel">Season 1 ends</span><b id="seasonDeadlineDate">—</b><small id="seasonRemaining">—</small></div><div class="seasonRulesHint" id="seasonRulesHint">Season 2 data is preloaded: <b>Material Realm reaches its S2 max at Lv.120</b>; Season Power scoring starts at Lv.130.</div>'
new_hint='<div class="seasonDeadline"><span id="seasonDeadlineLabel">Season 1 ends</span><b id="seasonDeadlineDate">—</b><small id="seasonRemaining">—</small></div><div class="seasonRulesHint" id="seasonRulesHint" hidden></div>'
if old_hint not in s:
    raise SystemExit('season rules hint anchor not found')
s=s.replace(old_hint,new_hint,1)

old_reserve='<label class="reserveHoursControl"><input id="reserveHours" min="0" max="36" type="number" value="36"> hours Bed EXP reserved</label>'
new_reserve='<input id="reserveHours" min="0" max="36" type="number" value="36" hidden>'
if old_reserve not in s:
    raise SystemExit('reserve hours control not found')
s=s.replace(old_reserve,new_reserve,1)

old_projection='<div class="projectionCallout"><span>Projected final character</span><strong id="projectedCharacter">—</strong><small id="projectionNote">Uses exact server resets, displayed in this device\'s local timezone; the free 2-hour speed-up is discrete, not prorated.</small></div>'
if old_projection not in s:
    raise SystemExit('old projected character callout not found')
s=s.replace(old_projection,'',1)

old_optimizer='<p class="optimizerSummary" id="optimizerSummary">—</p>'
new_optimizer='<p class="optimizerSummary" id="optimizerSummary" hidden></p>'
if old_optimizer not in s:
    raise SystemExit('optimizer summary not found')
s=s.replace(old_optimizer,new_optimizer,1)

# The projected character belongs by the XP inputs now, so remove the duplicate result-header display while retaining its JS target.
old_result='<p class="finalLevelLine">Projected <b id="resultProjectedCharacter">—</b></p>'
new_result='<p class="finalLevelLine" hidden>Projected <b id="resultProjectedCharacter">—</b></p>'
if old_result not in s:
    raise SystemExit('result projected character line not found')
s=s.replace(old_result,new_result,1)

css='''\n\n/* CALC_HEADER_CLEANUP_V1 */\n.projectionCallout.projectionInline{\n  grid-template-columns:1fr auto;\n  align-items:center;\n  gap:12px;\n  margin-top:10px;\n  padding:9px 12px;\n  background:var(--ui-accent-soft)!important;\n  border-color:var(--ui-accent-border)!important;\n}\n.projectionCallout.projectionInline span{font-size:8px}\n.projectionCallout.projectionInline strong{grid-area:auto;font-size:15px}\n@media (max-width:520px){\n  .projectionCallout.projectionInline{grid-template-columns:1fr}\n  .projectionCallout.projectionInline strong{font-size:16px}\n}\n'''
if '</style>' not in s:
    raise SystemExit('style closing tag not found')
s=s.replace('</style>',css+'\n</style>',1)

p.write_text(s,encoding='utf-8')
print('Cleaned calculator planning chrome and moved projected level under XP inputs.')
