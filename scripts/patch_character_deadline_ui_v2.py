from pathlib import Path

index = Path('index.html')
runtime = Path('assets/runtime.js')
css = Path('assets/site.css')

html = index.read_text()
old_bed = '<label>Bed EXP per hour<input id="bedExp" type="number" min="0" value="0"><small>Required for projection</small></label>'
new_bed = '<label>Bed EXP per hour<input id="bedExp" type="number" min="0" value="0"></label>'
if old_bed not in html:
    raise SystemExit('Bed EXP helper marker not found')
html = html.replace(old_bed, new_bed, 1)

old_deadline = '<div class="seasonDeadline"><span id="seasonDeadlineLabel">Season ends</span><b id="seasonDeadlineDate">—</b><label class="finishEarlyControl" title="Stop counting Character score and projected resources this many reset-days before season end"><span>Finish early</span><input id="finishEarlyDays" type="number" min="0" step="1" value="0" inputmode="numeric"><em>days</em></label><small id="seasonRemaining">—</small></div><div class="seasonRulesHint" id="seasonRulesHint" hidden></div>'
new_deadline = '<div class="seasonPlanningRow"><div class="seasonDeadline"><span id="seasonDeadlineLabel">Season ends</span><b id="seasonDeadlineDate">—</b><small id="seasonRemaining">—</small></div><label class="finishEarlyCard" title="Stop counting Character score and projected resources this many reset-days before season end"><span>Finish early</span><input id="finishEarlyDays" type="number" min="0" step="1" value="0" inputmode="numeric"><em>days</em></label></div><div class="seasonRulesHint" id="seasonRulesHint" hidden></div>'
if old_deadline not in html:
    raise SystemExit('Old finish-early deadline row not found')
html = html.replace(old_deadline, new_deadline, 1)
index.write_text(html)

js = runtime.read_text()
old_label = "$('historicalStarsLabel').textContent='Season 1 Primostars (carried)';"
new_label = "$('historicalStarsLabel').textContent='Season 1 Primostars';"
if old_label not in js:
    raise SystemExit('Historical stars carried label not found')
js = js.replace(old_label, new_label, 1)

old_listener = """      if(id==='staminaMode'){
        el.addEventListener('change',()=>{resetMaxAchievableUi();markManualSnapshot(id);scheduleCalculatorUpdate(0);});
        return;
      }
"""
new_listener = """      if(id==='finishEarlyDays'){
        // Finish-early is a planning preference, not account-state data. Recalculate on a
        // short debounce so the cutoff visibly responds while typing without hammering the
        // optimizer once per keystroke or moving the user's snapshot clock.
        let finishEarlyTimer=0;
        const commitFinishEarly=()=>{
          const value=finishEarlyDaysValue();
          el.value=String(value);
          resetMaxAchievableUi();
          saveState();
          scheduleCalculatorUpdate(0);
        };
        el.addEventListener('input',()=>{
          clearTimeout(finishEarlyTimer);
          finishEarlyTimer=setTimeout(commitFinishEarly,250);
        });
        el.addEventListener('change',()=>{
          clearTimeout(finishEarlyTimer);
          commitFinishEarly();
        });
        el.addEventListener('keydown',ev=>{if(ev.key==='Enter') el.blur();});
        return;
      }
      if(id==='staminaMode'){
        el.addEventListener('change',()=>{resetMaxAchievableUi();markManualSnapshot(id);scheduleCalculatorUpdate(0);});
        return;
      }
"""
if old_listener not in js:
    raise SystemExit('Input listener insertion marker not found')
js = js.replace(old_listener, new_listener, 1)
runtime.write_text(js)

style = css.read_text()
marker = '/* FINISH_EARLY_SCORE_UI_V2 */'
if marker not in style:
    style += r'''

/* FINISH_EARLY_SCORE_UI_V2 */
.seasonPlanningRow{
  display:grid;
  grid-template-columns:minmax(0,1fr) max-content;
  gap:8px;
  align-items:stretch;
  margin-top:14px;
}
.seasonPlanningRow .seasonDeadline{
  margin-top:0!important;
  min-width:0;
  height:100%;
}
.finishEarlyCard{
  border:1px solid var(--line);
  background:var(--bg);
  border-radius:10px;
  min-height:42px;
  padding:7px 9px;
  display:flex;
  align-items:center;
  justify-content:flex-end;
  gap:5px;
  color:var(--muted);
  text-align:right;
  white-space:nowrap;
  letter-spacing:.05em;
  text-transform:uppercase;
  font-size:8px;
  font-weight:850;
}
.finishEarlyCard span{color:var(--muted);font:inherit;letter-spacing:inherit;text-transform:inherit}
.finishEarlyCard input{
  width:34px!important;
  min-width:34px!important;
  max-width:34px!important;
  flex:0 0 34px!important;
  height:26px!important;
  min-height:26px!important;
  padding:3px 4px!important;
  margin:0!important;
  border:1px solid var(--line)!important;
  border-radius:7px!important;
  background:var(--input-bg)!important;
  color:var(--ink)!important;
  text-align:center!important;
  font-size:10px!important;
  font-weight:850!important;
  line-height:1!important;
  outline:0!important;
}
.finishEarlyCard input:focus{
  border-color:var(--green)!important;
  box-shadow:0 0 0 2px color-mix(in srgb,var(--green) 15%,transparent)!important;
}
.finishEarlyCard em{color:var(--muted);font-style:normal;font-size:8px;font-weight:850;text-transform:none}
@media(max-width:700px){
  .seasonPlanningRow{grid-template-columns:1fr}
  .finishEarlyCard{justify-content:flex-end}
}
'''
css.write_text(style)
