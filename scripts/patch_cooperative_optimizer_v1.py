from pathlib import Path

RUNTIME = Path('assets/runtime.js')
CSS = Path('assets/site.css')
MARKER = 'COOPERATIVE_OPTIMIZER_V1'


def function_span(src: str, name: str):
    needle = f'function {name}('
    start = src.find(needle)
    if start < 0:
        raise RuntimeError(f'Could not find {needle}')
    brace = src.find('{', start)
    if brace < 0:
        raise RuntimeError(f'Could not find opening brace for {name}')
    depth = 0
    i = brace
    quote = None
    escape = False
    line_comment = False
    block_comment = False
    while i < len(src):
        ch = src[i]
        nxt = src[i + 1] if i + 1 < len(src) else ''
        if line_comment:
            if ch == '\n':
                line_comment = False
            i += 1
            continue
        if block_comment:
            if ch == '*' and nxt == '/':
                block_comment = False
                i += 2
                continue
            i += 1
            continue
        if quote:
            if escape:
                escape = False
            elif ch == '\\':
                escape = True
            elif ch == quote:
                quote = None
            i += 1
            continue
        if ch == '/' and nxt == '/':
            line_comment = True
            i += 2
            continue
        if ch == '/' and nxt == '*':
            block_comment = True
            i += 2
            continue
        if ch in ('\'', '"', '`'):
            quote = ch
            i += 1
            continue
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                return start, i + 1
        i += 1
    raise RuntimeError(f'Unterminated function {name}')


runtime = RUNTIME.read_text(encoding='utf-8')
css = CSS.read_text(encoding='utf-8')

if MARKER in runtime:
    print('Cooperative optimizer patch already present.')
    raise SystemExit(0)

# Clone the exact current search algorithm, changing only scheduling/cancellation behavior.
s0, s1 = function_span(runtime, 'searchPlans')
search_src = runtime[s0:s1]
coop_search = search_src.replace('function searchPlans(', 'async function searchPlansCooperative(', 1)
coop_search = coop_search.replace('ctx=null){', 'ctx=null,job=null){', 1)
first_body = coop_search.find('{')
coop_search = (
    coop_search[:first_body + 1]
    + "\n    const checkpoint=createOptimizerCheckpoint(job);\n    await checkpoint(true);"
    + coop_search[first_body + 1:]
)

# Checkpoints only go in the expensive top-level candidate scans. They are rate-limited,
# so calling checkpoint frequently does not materially slow normal solves.
loop_markers = [
    'for(const ro of cats.relicOptions){',
    'for(const fo of cats.fantoOptions){',
    'for(const ri of sampledIndices(relicStart,boundedRelic.length,10)){',
    'for(const fi of sampledIndices(fantoStart,boundedFanto.length,10)){',
    'while(si<boundedSkill.length&&gi<boundedGear.length){',
    'for(let ri=relicStart;ri<relicEnd;ri++){',
    'for(let fi=fantoStart;fi<fantoEnd;fi++){',
]
for marker in loop_markers:
    coop_search = coop_search.replace(marker, marker + '\n        await checkpoint();')

# Clone the Stamina dispatcher so ordinary legacy callers can remain synchronous.
t0, t1 = function_span(runtime, 'solveTargetWithAutoStamina')
solve_src = runtime[t0:t1]
coop_solve = solve_src.replace('function solveTargetWithAutoStamina(', 'async function solveTargetWithAutoStaminaCooperative(', 1)
coop_solve = coop_solve.replace('cfg=activeCalcConfig()){', 'cfg=activeCalcConfig(),job=null){', 1)
coop_solve = coop_solve.replace('const result=searchPlans(', 'const result=await searchPlansCooperative(')
coop_solve = coop_solve.replace('const resultState=(allocation)=>{', 'const resultState=async (allocation)=>{')
coop_solve = coop_solve.replace('const state=resultState(', 'const state=await resultState(')

helpers = r'''

  /* COOPERATIVE_OPTIMIZER_V1
     Heavy Primostar searches run in short main-thread slices rather than monopolizing one
     JavaScript task. The mathematical search remains identical to searchPlans(); this layer
     only yields to the browser between expensive candidate batches and supports cancellation. */
  class OptimizerCancelledError extends Error{
    constructor(){ super('Optimizer calculation cancelled'); this.name='OptimizerCancelledError'; }
  }
  let optimizerJobSequence=0;
  let activeOptimizerJob=null;

  function ensureOptimizerProgressPanel(){
    let panel=$('optimizerProgressPanel');
    if(panel) return panel;
    panel=document.createElement('div');
    panel.id='optimizerProgressPanel';
    panel.className='optimizerProgressPanel';
    panel.hidden=true;
    panel.setAttribute('role','status');
    panel.setAttribute('aria-live','polite');
    panel.innerHTML=`
      <div class="optimizerProgressSpinner" aria-hidden="true"></div>
      <div class="optimizerProgressCopy">
        <strong id="optimizerProgressTitle">Calculating…</strong>
        <span id="optimizerProgressDetail">Searching upgrade combinations</span>
        <small id="optimizerProgressElapsed">0.0s elapsed</small>
      </div>
      <button id="optimizerCancelButton" type="button">Cancel</button>`;
    document.body.appendChild(panel);
    $('optimizerCancelButton')?.addEventListener('click',()=>{
      const job=activeOptimizerJob;
      if(!job||job.cancelled) return;
      job.cancelled=true;
      const title=$('optimizerProgressTitle');
      const detail=$('optimizerProgressDetail');
      if(title) title.textContent='Cancelling…';
      if(detail) detail.textContent='Stopping at the next optimizer checkpoint';
      const btn=$('optimizerCancelButton');
      if(btn){btn.disabled=true;btn.textContent='Cancelling';}
    });
    return panel;
  }

  function beginOptimizerJob(targetStars){
    if(activeOptimizerJob) activeOptimizerJob.cancelled=true;
    const panel=ensureOptimizerProgressPanel();
    const job={id:++optimizerJobSequence,cancelled:false,started:performance.now(),timer:0,targetStars:Number(targetStars)||0};
    activeOptimizerJob=job;
    panel.dataset.jobId=String(job.id);
    panel.hidden=false;
    panel.classList.remove('optimizerCancelled','optimizerError');
    const days=finishEarlyDaysValue();
    const title=$('optimizerProgressTitle'),detail=$('optimizerProgressDetail'),elapsed=$('optimizerProgressElapsed'),btn=$('optimizerCancelButton');
    if(title) title.textContent=`Calculating ${fmt(job.targetStars)} Primostars…`;
    if(detail) detail.textContent=days>0?`Finish Early: ${days} day${days===1?'':'s'} · searching upgrade combinations`:'Searching upgrade combinations';
    if(elapsed) elapsed.textContent='0.0s elapsed';
    if(btn){btn.disabled=false;btn.textContent='Cancel';}
    job.timer=setInterval(()=>{
      if(activeOptimizerJob!==job) return;
      const seconds=(performance.now()-job.started)/1000;
      if(elapsed) elapsed.textContent=`${seconds.toFixed(seconds<10?1:0)}s elapsed`;
    },100);
    return job;
  }

  function finishOptimizerJob(job,state='done'){
    if(!job) return;
    if(job.timer) clearInterval(job.timer);
    if(activeOptimizerJob!==job) return;
    activeOptimizerJob=null;
    const panel=ensureOptimizerProgressPanel();
    const title=$('optimizerProgressTitle'),detail=$('optimizerProgressDetail'),btn=$('optimizerCancelButton');
    if(state==='cancelled'){
      panel.classList.add('optimizerCancelled');
      if(title) title.textContent='Calculation cancelled';
      if(detail) detail.textContent='Previous completed result kept.';
      if(btn){btn.disabled=true;btn.textContent='Cancelled';}
      const id=String(job.id);
      setTimeout(()=>{ if(panel.dataset.jobId===id) panel.hidden=true; },1200);
      return;
    }
    if(state==='error'){
      panel.classList.add('optimizerError');
      if(title) title.textContent='Calculation stopped';
      if(detail) detail.textContent='The optimizer hit an unexpected error.';
      if(btn){btn.disabled=true;btn.textContent='Close';}
      const id=String(job.id);
      setTimeout(()=>{ if(panel.dataset.jobId===id) panel.hidden=true; },1800);
      return;
    }
    panel.hidden=true;
  }

  function createOptimizerCheckpoint(job){
    let lastYield=performance.now();
    return async(force=false)=>{
      if(!job) return;
      if(job.cancelled) throw new OptimizerCancelledError();
      const now=performance.now();
      if(force || now-lastYield>=12){
        await new Promise(resolve=>setTimeout(resolve,0));
        lastYield=performance.now();
        if(job.cancelled) throw new OptimizerCancelledError();
      }
    };
  }
'''

insert_at = runtime.find('\n  function optimizer(', s1)
if insert_at < 0:
    raise RuntimeError('Could not locate optimizer insertion point')
runtime = runtime[:insert_at] + helpers + '\n\n' + coop_search + '\n\n' + coop_solve + '\n' + runtime[insert_at:]

# Only the normal visible calculator solve switches to the cooperative path. Existing helper
# probes / ceiling tools continue to use the legacy synchronous solver unless explicitly changed.
runtime = runtime.replace('  function updateCalculator(){', '  async function updateCalculator(){', 1)
old_solve = """    let solution=goalState.solutions.get(desired);\n    if(!solution){\n      solution=solveTargetWithAutoStamina(baselineScore,desired,p,baseResources,cfg);\n      goalState.solutions.set(desired,solution);\n    }"""
new_solve = """    let solution=goalState.solutions.get(desired);\n    if(!solution){\n      const optimizerJob=beginOptimizerJob(targetStars);\n      try{\n        solution=await solveTargetWithAutoStaminaCooperative(baselineScore,desired,p,baseResources,cfg,optimizerJob);\n        if(optimizerJob.cancelled) throw new OptimizerCancelledError();\n        goalState.solutions.set(desired,solution);\n        finishOptimizerJob(optimizerJob,'done');\n      }catch(err){\n        if(err instanceof OptimizerCancelledError){\n          finishOptimizerJob(optimizerJob,'cancelled');\n          return;\n        }\n        finishOptimizerJob(optimizerJob,'error');\n        console.error('COOPERATIVE_OPTIMIZER_V1',err);\n        return;\n      }\n    }"""
if old_solve not in runtime:
    raise RuntimeError('Could not locate updateCalculator solve block')
runtime = runtime.replace(old_solve, new_solve, 1)

# Copy Plan must wait for an in-flight solve before reading result text.
runtime = runtime.replace('  function copyPlan(){\n    updateCalculator();', '  async function copyPlan(){\n    await updateCalculator();', 1)

RUNTIME.write_text(runtime, encoding='utf-8')

if 'COOPERATIVE_OPTIMIZER_V1_STYLE' not in css:
    css += r'''

/* COOPERATIVE_OPTIMIZER_V1_STYLE */
.optimizerProgressPanel{
  position:fixed;
  right:18px;
  bottom:18px;
  z-index:9999;
  width:min(340px,calc(100vw - 36px));
  display:grid;
  grid-template-columns:28px minmax(0,1fr) auto;
  align-items:center;
  gap:11px;
  padding:12px 12px 12px 13px;
  border:1px solid var(--line);
  border-radius:12px;
  background:var(--surface);
  color:var(--text);
  box-shadow:0 14px 38px rgba(0,0,0,.28);
}
.optimizerProgressPanel[hidden]{display:none!important}
.optimizerProgressSpinner{
  width:22px;height:22px;border-radius:50%;
  border:3px solid var(--line);
  border-top-color:var(--green);
  animation:optimizerProgressSpin .8s linear infinite;
}
.optimizerProgressCopy{min-width:0;display:flex;flex-direction:column;gap:2px}
.optimizerProgressCopy strong{font-size:11px;line-height:1.25;color:var(--text);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.optimizerProgressCopy span{font-size:9px;line-height:1.3;color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.optimizerProgressCopy small{font-size:8px;line-height:1.2;color:var(--muted)}
#optimizerCancelButton{
  min-width:58px;height:32px;padding:0 10px;border-radius:8px;
  border:1px solid var(--line);background:var(--surface2,var(--surface));color:var(--pink,var(--green));
  font-size:9px;font-weight:900;cursor:pointer;
}
#optimizerCancelButton:hover{border-color:currentColor}
#optimizerCancelButton:disabled{opacity:.6;cursor:default}
.optimizerProgressPanel.optimizerCancelled .optimizerProgressSpinner{animation:none;border-top-color:var(--muted)}
.optimizerProgressPanel.optimizerError .optimizerProgressSpinner{animation:none;border-top-color:var(--danger,var(--pink))}
@keyframes optimizerProgressSpin{to{transform:rotate(360deg)}}
@media (prefers-reduced-motion:reduce){.optimizerProgressSpinner{animation:none}}
@media(max-width:700px){
  .optimizerProgressPanel{right:10px;bottom:10px;width:calc(100vw - 20px);padding:11px;grid-template-columns:26px minmax(0,1fr) auto}
  #optimizerCancelButton{min-width:64px;height:36px;font-size:10px}
}
'''
    CSS.write_text(css, encoding='utf-8')

print('Applied cooperative/cancellable optimizer patch.')
