from pathlib import Path

path = Path('assets/runtime.js')
text = path.read_text(encoding='utf-8')

# Propagate the optimizer job into every cooperative inner search so Cancel can
# actually be observed while the expensive plan scan is running.
old_call = "searchPlansCooperative(baseScore,desired,p,resources,cfg,ctx);"
count = text.count(old_call)
if count < 3:
    raise SystemExit(f'Expected at least 3 cooperative search calls without job, found {count}')
text = text.replace(old_call, "searchPlansCooperative(baseScore,desired,p,resources,cfg,ctx,job);")

# Make the Finish Early field visibly clamp before the progress job begins.
old_commit = """        const commitFinishEarly=()=>{
          const value=finishEarlyDaysValue();
          el.value=String(value);
          resetMaxAchievableUi();
          saveState();
          // FINISH_EARLY_PROGRESS_V1: Finish Early launches the same heavy optimizer as a goal change,
          // so show the cancellable calculating panel instead of making the UI appear frozen.
          queueRegularGoalOptimizerProgress();
          requestAnimationFrame(()=>scheduleCalculatorUpdate(0));
        };
        el.addEventListener('blur',commitFinishEarly);
"""
new_commit = """        const commitFinishEarly=()=>{
          // FINISH_EARLY_CANCEL_CLAMP_V1: normalize visibly before starting any heavy solve.
          syncFinishEarlyInputLimit(activeCalcConfig(),true);
          const value=finishEarlyDaysValue();
          el.value=String(value);
          resetMaxAchievableUi();
          saveState();
          // FINISH_EARLY_PROGRESS_V1: Finish Early launches the same heavy optimizer as a goal change,
          // so show the cancellable calculating panel instead of making the UI appear frozen.
          queueRegularGoalOptimizerProgress();
          requestAnimationFrame(()=>scheduleCalculatorUpdate(0));
        };
        // Do not let a manually typed value sit above the physical season-time ceiling.
        el.addEventListener('input',()=>{
          const raw=Number(el.value),max=maxFinishEarlyDays(activeCalcConfig());
          if(Number.isFinite(raw)&&raw>max) el.value=String(max);
        });
        el.addEventListener('blur',commitFinishEarly);
"""
if old_commit not in text:
    raise SystemExit('Finish Early commit block not found')
text = text.replace(old_commit, new_commit, 1)

path.write_text(text, encoding='utf-8')
print(f'Patched {count} cooperative search calls and hardened Finish Early clamp/cancel behavior.')
