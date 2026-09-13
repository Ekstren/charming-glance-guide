from pathlib import Path

path = Path('assets/runtime.js')
text = path.read_text(encoding='utf-8')
old = """        const commitFinishEarly=()=>{
          const value=finishEarlyDaysValue();
          el.value=String(value);
          resetMaxAchievableUi();
          saveState();
          scheduleCalculatorUpdate(0);
        };
"""
new = """        const commitFinishEarly=()=>{
          const value=finishEarlyDaysValue();
          el.value=String(value);
          resetMaxAchievableUi();
          saveState();
          // FINISH_EARLY_PROGRESS_V1: Finish Early launches the same heavy optimizer as a goal change,
          // so show the cancellable calculating panel instead of making the UI appear frozen.
          queueRegularGoalOptimizerProgress();
          requestAnimationFrame(()=>scheduleCalculatorUpdate(0));
        };
"""
if old not in text:
    raise SystemExit('Finish Early commit block not found')
text = text.replace(old, new, 1)
path.write_text(text, encoding='utf-8')
print('Restored optimizer progress panel for Finish Early recalculations.')
