from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
index_path = ROOT / 'index.html'
runtime_path = ROOT / 'assets' / 'runtime.js'
css_path = ROOT / 'assets' / 'site.css'

index = index_path.read_text(encoding='utf-8')
runtime = runtime_path.read_text(encoding='utf-8')
css = css_path.read_text(encoding='utf-8')

old_control = '<label class="finishEarlyCard" title="Stop counting Character score and projected resources this many days before season end"><span>Finish early</span><input id="finishEarlyDays" type="number" min="0" step="0.5" value="0" inputmode="decimal"><em>days</em></label>'
new_control = '<div class="finishEarlyCard" title="Stop counting Character score and projected resources this many days before season end"><span>Finish early</span><input id="finishEarlyDays" type="number" min="0" step="0.5" value="0" inputmode="decimal" aria-label="Finish early days"><em>days</em><button id="finishEarlyMax" class="finishEarlyMax" type="button" title="Find the maximum half-day finish-early value that still reaches the selected Primostar target">Max</button></div>'
if old_control in index:
    index = index.replace(old_control, new_control, 1)
elif 'id="finishEarlyMax"' not in index:
    raise SystemExit('finish-early control pattern not found')

marker = '  /* SMART_BALANCE_RAW_CEILING_V1\n'
max_fn = r'''  /* FINISH_EARLY_MAX_V1
     Find the largest 0.5-day cutoff that still reaches the selected Primostar target.
     This intentionally reuses updateCalculator() so Max follows the exact same scoring,
     resource, Realm and cap rules as the visible result card. Binary search keeps the
     number of heavy optimizer passes small even with a long season remaining. */
  function finishEarlyTargetFundable(){
    return ($('targetStatus')?.textContent||'').trim()==='✓';
  }
  function findMaxFinishEarly(){
    const btn=$('finishEarlyMax'),input=$('finishEarlyDays');
    if(!btn||!input||btn.disabled) return;
    const cfg=activeCalcConfig();
    const original=String(input.value||'0');
    const halfDayMs=12*60*60*1000;
    const maxHalfSteps=Math.max(0,Math.floor((cfg.end.getTime()-Date.now())/halfDayMs));
    btn.disabled=true;
    btn.textContent='…';
    btn.setAttribute('aria-busy','true');
    clearTimeout(calculatorUpdateTimer);
    calculatorUpdateTimer=null;
    setTimeout(()=>{
      try{
        input.value='0';
        updateCalculator();
        if(!finishEarlyTargetFundable()){
          input.value=original;
          updateCalculator();
          btn.title='The selected target is not reachable with the full remaining season, or required inputs are still missing.';
          return;
        }

        let lo=0,hi=maxHalfSteps;
        while(lo<hi){
          const mid=Math.ceil((lo+hi)/2);
          input.value=String(mid/2);
          updateCalculator();
          if(finishEarlyTargetFundable()) lo=mid;
          else hi=mid-1;
        }

        input.value=String(lo/2);
        resetMaxAchievableUi();
        saveState();
        updateCalculator();
        btn.title=lo>0
          ? `Maximum finish-early value for the current target: ${lo/2} days.`
          : 'The current target needs the full remaining season.';
      }catch(err){
        console.error('FINISH_EARLY_MAX_V1',err);
        input.value=original;
        updateCalculator();
        btn.title='Could not calculate the maximum finish-early value from the current inputs.';
      }finally{
        btn.disabled=false;
        btn.textContent='Max';
        btn.removeAttribute('aria-busy');
      }
    },0);
  }

'''
if 'FINISH_EARLY_MAX_V1' not in runtime:
    if marker not in runtime:
        raise SystemExit('runtime insertion marker not found')
    runtime = runtime.replace(marker, max_fn + marker, 1)

listener = "    $('findMaxStars')?.addEventListener('click',findMaxAchievableStars);\n"
listener_new = listener + "    $('finishEarlyMax')?.addEventListener('click',findMaxFinishEarly);\n"
if "$('finishEarlyMax')?.addEventListener('click',findMaxFinishEarly);" not in runtime:
    if listener not in runtime:
        raise SystemExit('calculator listener marker not found')
    runtime = runtime.replace(listener, listener_new, 1)

css_marker = '/* FINISH_EARLY_MAX_V1_STYLE */'
css_add = r'''

/* FINISH_EARLY_MAX_V1_STYLE */
.finishEarlyCard{gap:8px!important}
.finishEarlyMax{
  flex:0 0 auto;
  min-width:42px;
  height:30px;
  border:1px solid var(--line);
  background:var(--surface);
  color:var(--green);
  border-radius:8px;
  padding:0 9px;
  font-size:9px;
  line-height:1;
  font-weight:900;
  letter-spacing:.03em;
  cursor:pointer;
}
.finishEarlyMax:hover{border-color:var(--green);background:var(--green-soft)}
.finishEarlyMax:disabled{opacity:.6;cursor:wait}
@media(max-width:700px){
  .finishEarlyCard{justify-content:flex-end!important}
  .finishEarlyMax{min-width:46px;height:32px;font-size:10px}
}
'''
if css_marker not in css:
    css = css.rstrip() + css_add + '\n'

index_path.write_text(index, encoding='utf-8')
runtime_path.write_text(runtime, encoding='utf-8')
css_path.write_text(css, encoding='utf-8')
