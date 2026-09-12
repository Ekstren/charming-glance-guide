from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
index_path = ROOT / 'index.html'
runtime_path = ROOT / 'assets' / 'runtime.js'
css_path = ROOT / 'assets' / 'site.css'

index = index_path.read_text(encoding='utf-8')
runtime = runtime_path.read_text(encoding='utf-8')
css = css_path.read_text(encoding='utf-8')

# Add a persistent, non-actionable explanation directly below the Finish Early row.
old = '<button id="finishEarlyMax" class="finishEarlyMax" type="button" title="Find the maximum half-day finish-early value that still reaches the selected Primostar target">Max</button></div></div><div class="seasonRulesHint" id="seasonRulesHint" hidden></div>'
new = '<button id="finishEarlyMax" class="finishEarlyMax" type="button" title="Find the maximum half-day finish-early value that still reaches the selected Primostar target">Max</button></div></div><small id="finishEarlyMaxHint" class="finishEarlyMaxHint" hidden>Max reached for current purchase plan. To finish earlier, increase Material Realm purchases per day.</small><div class="seasonRulesHint" id="seasonRulesHint" hidden></div>'
if old not in index:
    raise SystemExit('Finish Early markup anchor not found')
index = index.replace(old, new, 1)

# Any real input change already calls resetMaxAchievableUi(). Extend that reset so a
# previously locked Max button immediately becomes available when the plan changes.
old = """  function resetMaxAchievableUi(){
    maxAchievableState={fingerprint:'',routine:null,hard:null};
    const btn=$('findMaxStars'),status=$('maxAchievableStatus');
    if(btn){btn.disabled=false;btn.textContent='Find max achievable';}
    if(status) status.textContent='Shows the maximum with your selected daily Realm plan and the hard maximum using all remaining Realm capacity.';
  }
"""
new = """  function resetMaxAchievableUi(){
    maxAchievableState={fingerprint:'',routine:null,hard:null};
    const btn=$('findMaxStars'),status=$('maxAchievableStatus');
    if(btn){btn.disabled=false;btn.textContent='Find max achievable';}
    if(status) status.textContent='Shows the maximum with your selected daily Realm plan and the hard maximum using all remaining Realm capacity.';
    const finishBtn=$('finishEarlyMax'),finishHint=$('finishEarlyMaxHint');
    if(finishBtn?.dataset.maxLocked==='true'){
      delete finishBtn.dataset.maxLocked;
      finishBtn.disabled=false;
      finishBtn.title='Find the maximum half-day finish-early value that still reaches the selected Primostar target';
    }
    if(finishHint) finishHint.hidden=true;
  }

  function lockFinishEarlyMaxForPurchasePlan(){
    const btn=$('finishEarlyMax'),hint=$('finishEarlyMaxHint');
    if(!btn) return;
    btn.dataset.maxLocked='true';
    btn.disabled=true;
    btn.textContent='Max';
    btn.title='Max reached for current purchase plan. To finish earlier, increase Material Realm purchases per day.';
    btn.removeAttribute('aria-busy');
    if(hint){
      hint.textContent='Max reached for current purchase plan. To finish earlier, increase Material Realm purchases per day.';
      hint.hidden=false;
    }
  }
"""
if old not in runtime:
    raise SystemExit('resetMaxAchievableUi anchor not found')
runtime = runtime.replace(old, new, 1)

# When even Finish Early = 0 cannot be funded by the configured routine, repeated Max
# clicks can never move the cutoff. Keep the button visibly locked until the user changes
# an input (especially Realm purchases), and explain why without silently changing anything.
old = """      if(!fullSeasonPossible){
        input.value=original;
        finishOptimizerJob(optimizerJob,'done');
        btn.title='The selected target is not reachable without extra Realm purchases beyond your configured routine.';
        await updateCalculator();
        return;
      }
"""
new = """      if(!fullSeasonPossible){
        input.value=original;
        finishOptimizerJob(optimizerJob,'done');
        await updateCalculator();
        lockFinishEarlyMaxForPurchasePlan();
        return;
      }
"""
if old not in runtime:
    raise SystemExit('fullSeasonPossible branch anchor not found')
runtime = runtime.replace(old, new, 1)

# Do not undo the intentional locked state in the function's unconditional cleanup.
old = """    }finally{
      btn.disabled=false;
      btn.textContent='Max';
      btn.removeAttribute('aria-busy');
"""
new = """    }finally{
      if(btn.dataset.maxLocked!=='true') btn.disabled=false;
      btn.textContent='Max';
      btn.removeAttribute('aria-busy');
"""
if old not in runtime:
    raise SystemExit('findMaxFinishEarly finally anchor not found')
runtime = runtime.replace(old, new, 1)

marker = '/* FINISH_EARLY_MAX_LOCKED_V1 */'
if marker not in css:
    css += r'''

/* FINISH_EARLY_MAX_LOCKED_V1
   A disabled Max here is explanatory, not a loading state: the current routine cannot
   support the selected target without additional Material Realm purchases. */
.finishEarlyMax:disabled[data-max-locked="true"]{
  opacity:.42!important;
  cursor:not-allowed!important;
  border-color:var(--line)!important;
  background:var(--surface)!important;
  color:var(--muted)!important;
}
.finishEarlyMaxHint{
  display:block;
  margin:-2px 4px 8px 0;
  color:var(--gold);
  font-size:8px;
  font-weight:750;
  line-height:1.35;
  text-align:right;
}
@media(max-width:700px){
  .finishEarlyMaxHint{margin:0 2px 8px;text-align:left;font-size:8px}
}
'''

index_path.write_text(index, encoding='utf-8')
runtime_path.write_text(runtime, encoding='utf-8')
css_path.write_text(css, encoding='utf-8')
print('Applied FINISH_EARLY_MAX_LOCKED_V1')
