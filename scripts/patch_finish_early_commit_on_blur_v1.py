from pathlib import Path

path = Path('assets/runtime.js')
text = path.read_text(encoding='utf-8')

old_focus = """      if(e.target?.matches?.('input') && e.target.id!=='targetStars'){
"""
new_focus = """      if(e.target?.matches?.('input') && e.target.id!=='targetStars' && e.target.id!=='finishEarlyDays'){
"""
if old_focus not in text:
    raise SystemExit('focusin anchor not found')
text = text.replace(old_focus, new_focus, 1)

old = """      if(id==='finishEarlyDays'){
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
"""
new = """      if(id==='finishEarlyDays'){
        /* FINISH_EARLY_COMMIT_ON_BLUR_V1
           Finish Early can trigger an expensive optimizer solve, so never recalculate while
           the user is still typing or clicking the number spinner. Commit only when editing
           is explicitly finished: Enter blurs the field; Tab and clicking/tapping elsewhere
           naturally fire blur. This is a planning preference and never moves snapshot time. */
        const commitFinishEarly=()=>{
          const value=finishEarlyDaysValue();
          el.value=String(value);
          resetMaxAchievableUi();
          saveState();
          scheduleCalculatorUpdate(0);
        };
        el.addEventListener('blur',commitFinishEarly);
        el.addEventListener('keydown',ev=>{
          if(ev.key==='Enter'){
            ev.preventDefault();
            el.blur();
          }
        });
        return;
      }
"""
if old not in text:
    raise SystemExit('finishEarlyDays listener anchor not found')
text = text.replace(old, new, 1)

path.write_text(text, encoding='utf-8')
print('patched Finish Early to commit only on blur/Enter/Tab/outside click')
