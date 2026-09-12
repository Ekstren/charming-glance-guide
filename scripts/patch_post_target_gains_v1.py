from pathlib import Path

index = Path('index.html')
css = Path('assets/site.css')
runtime = Path('assets/runtime.js')

html = index.read_text(encoding='utf-8')
style = css.read_text(encoding='utf-8')
js = runtime.read_text(encoding='utf-8')

HTML_MARK = '<!-- POST_TARGET_GAINS_V1 -->'
if HTML_MARK not in html:
    anchor = '      <div class="secondaryCostNote" id="secondaryCostNote" hidden></div>'
    if html.count(anchor) != 1:
        raise SystemExit(f'Expected one secondaryCostNote anchor, found {html.count(anchor)}')
    block = '''      <!-- POST_TARGET_GAINS_V1 -->
      <section class="postTargetGains" id="postTargetGains" hidden>
        <div class="postTargetHeader">
          <div><span>Estimated gains after target</span><small id="postTargetWindow">—</small></div>
          <small>Bed EXP is claimed normally until 34h before season end; the final 36h stays banked for next season.</small>
        </div>
        <div class="postTargetToolPlan">
          <div class="postTargetPlanHead"><b>Post-target tool plan</b><small>Applies only after the target is reached · does not affect score planning.</small></div>
          <div class="postTargetPlanControls">
            <label><input type="radio" name="postTargetToolMode" value="current" checked> Use current plan</label>
            <label><input type="radio" name="postTargetToolMode" value="stop"> Stop tool purchases</label>
            <label><input type="radio" name="postTargetToolMode" value="custom"> Custom</label>
          </div>
          <div class="postTargetCustom" id="postTargetCustom" hidden>
            <label>Ore Realm/day<input id="postTargetOreDaily" type="number" min="0" max="20" step="1" value="0"></label>
            <label>Essence Realm/day<input id="postTargetEssenceDaily" type="number" min="0" max="20" step="1" value="0"></label>
            <label>Sand Realm/day<input id="postTargetSandDaily" type="number" min="0" max="20" step="1" value="0"></label>
          </div>
        </div>
        <div class="postTargetGainGrid">
          <div><span>Raw Ore</span><b id="postTargetOreGain">—</b><small id="postTargetHammerGain">—</small></div>
          <div><span>Skill Essence</span><b id="postTargetEssenceGain">—</b><small id="postTargetKnuckleGain">—</small></div>
          <div><span>Chrono Sand</span><b id="postTargetSandGain">—</b><small id="postTargetShovelGain">—</small></div>
          <div><span>Fantomon Treats</span><b id="postTargetTreatGain">—</b><small>Basic-equivalent gained</small></div>
        </div>
      </section>
'''
    html = html.replace(anchor, block + anchor, 1)

# Remove stale help text left over from before the universal Bed hold was implemented.
old_help = "For now, Bed storage/hold automation is disabled; the planner uses the entered <b>Bed EXP per hour</b> directly through the season reset and includes the free 2-hour speed-up at each future reset."
new_help = "Character projection assumes the recommended rollover strategy automatically: Bed EXP is claimed normally until <b>34 hours before season end</b>, then left unclaimed; the final reset's free 2-hour speed-up also stays in the Bed, leaving <b>36 hours of EXP banked</b> for the next season."
if old_help in html:
    html = html.replace(old_help, new_help, 1)

CSS_MARK = '/* POST_TARGET_GAINS_V1 */'
if CSS_MARK not in style:
    style += r'''

/* POST_TARGET_GAINS_V1 */
.postTargetGains{border:1px solid color-mix(in srgb,var(--purple) 72%,var(--line));background:color-mix(in srgb,var(--surface) 94%,var(--purple));border-radius:14px;margin-top:12px;padding:12px;box-shadow:0 0 0 1px color-mix(in srgb,var(--purple) 12%,transparent)}
.postTargetHeader{display:flex;justify-content:space-between;align-items:flex-start;gap:12px;margin-bottom:10px}
.postTargetHeader>div>span{display:block;color:var(--green);font-size:10px;font-weight:900;letter-spacing:.08em;text-transform:uppercase}
.postTargetHeader>div>small{display:block;color:var(--muted);margin-top:3px;font-size:9px}
.postTargetHeader>small{max-width:330px;color:var(--muted);font-size:8px;line-height:1.45;text-align:right}
.postTargetToolPlan{border-top:1px solid var(--line);padding-top:9px}
.postTargetPlanHead{display:flex;justify-content:space-between;gap:10px;align-items:center;margin-bottom:7px}
.postTargetPlanHead b{font-size:9px}
.postTargetPlanHead small{color:var(--muted);font-size:8px;text-align:right}
.postTargetPlanControls{display:flex;flex-wrap:wrap;gap:8px 16px;align-items:center}
.postTargetPlanControls label{display:flex;align-items:center;gap:5px;color:var(--body-text);font-size:9px;font-weight:700;cursor:pointer}
.postTargetPlanControls input[type=radio]{accent-color:var(--green)}
.postTargetCustom{grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin-top:9px;display:grid}
.postTargetCustom label{color:var(--muted);font-size:8px;font-weight:800;text-transform:uppercase;letter-spacing:.04em}
.postTargetCustom input{display:block;width:100%;height:34px;margin-top:4px;border:1px solid var(--line);border-radius:9px;background:var(--filter-bg);padding:0 9px;color:var(--ink);font-size:10px;font-weight:800}
.postTargetGainGrid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px;margin-top:10px}
.postTargetGainGrid>div{min-width:0;border:1px solid var(--line);background:color-mix(in srgb,var(--surface) 84%,var(--green-soft));border-radius:11px;padding:10px}
.postTargetGainGrid span{display:block;color:var(--muted);font-size:8px;font-weight:850;text-transform:uppercase;letter-spacing:.045em}
.postTargetGainGrid b{display:block;color:var(--ink);font-size:16px;line-height:1.2;margin-top:4px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.postTargetGainGrid small{display:block;color:var(--green);font-size:8px;font-weight:800;margin-top:5px}
@media (max-width:760px){.postTargetHeader,.postTargetPlanHead{display:block}.postTargetHeader>small,.postTargetPlanHead small{text-align:left;display:block;margin-top:4px}.postTargetGainGrid{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media (max-width:430px){.postTargetCustom{grid-template-columns:1fr}.postTargetGainGrid{grid-template-columns:1fr 1fr}.postTargetGainGrid b{font-size:13px}}
'''

JS_MARK = '/* POST_TARGET_GAINS_V1 */'
if JS_MARK not in js:
    anchor = '  function renderTargetTiming(plan,resourceBlocked,requestedDesired,pEnd,cfg=activeCalcConfig()){' 
    if js.count(anchor) != 1:
        raise SystemExit(f'Expected one renderTargetTiming anchor, found {js.count(anchor)}')
    logic = r'''  /* POST_TARGET_GAINS_V1
     Preview only: once the requested Primostar target is projected to be reached, show the
     resources expected to accumulate from that moment through season end. Post-target Realm
     purchase overrides affect this preview only and never feed back into Smart Balance scoring. */
  const POST_TARGET_TOOL_STORAGE_KEY='sxsPostTargetToolPlanV1';
  let postTargetLastReachMs=NaN;
  let postTargetLastCfg=null;
  function postTargetToolState(){
    let out={mode:'current',ore:0,essence:0,sand:0};
    try{
      const saved=JSON.parse(localStorage.getItem(POST_TARGET_TOOL_STORAGE_KEY)||'{}');
      if(['current','stop','custom'].includes(saved.mode)) out.mode=saved.mode;
      for(const k of ['ore','essence','sand']) if(Number.isFinite(Number(saved[k]))) out[k]=clamp(Math.floor(Number(saved[k])),0,20);
    }catch(_){}
    return out;
  }
  function savePostTargetToolState(state){
    try{localStorage.setItem(POST_TARGET_TOOL_STORAGE_KEY,JSON.stringify(state));}catch(_){}
  }
  function selectedPostTargetToolState(){
    const checked=document.querySelector('input[name="postTargetToolMode"]:checked');
    const state={mode:checked?.value||'current',ore:0,essence:0,sand:0};
    state.ore=clamp(Math.floor(Number($('postTargetOreDaily')?.value)||0),0,20);
    state.essence=clamp(Math.floor(Number($('postTargetEssenceDaily')?.value)||0),0,20);
    state.sand=clamp(Math.floor(Number($('postTargetSandDaily')?.value)||0),0,20);
    return state;
  }
  function ensurePostTargetControls(){
    const host=$('postTargetGains');
    if(!host || host.dataset.controlsBound==='1') return;
    host.dataset.controlsBound='1';
    const saved=postTargetToolState();
    const mode=document.querySelector(`input[name="postTargetToolMode"][value="${saved.mode}"]`) || document.querySelector('input[name="postTargetToolMode"][value="current"]');
    if(mode) mode.checked=true;
    if($('postTargetOreDaily')) $('postTargetOreDaily').value=String(saved.ore);
    if($('postTargetEssenceDaily')) $('postTargetEssenceDaily').value=String(saved.essence);
    if($('postTargetSandDaily')) $('postTargetSandDaily').value=String(saved.sand);
    const refresh=()=>{
      const state=selectedPostTargetToolState();
      savePostTargetToolState(state);
      if($('postTargetCustom')) $('postTargetCustom').hidden=state.mode!=='custom';
      if(Number.isFinite(postTargetLastReachMs) && postTargetLastCfg) renderPostTargetGains(postTargetLastReachMs,postTargetLastCfg);
    };
    host.querySelectorAll('input[name="postTargetToolMode"]').forEach(el=>el.addEventListener('change',refresh));
    ['postTargetOreDaily','postTargetEssenceDaily','postTargetSandDaily'].forEach(id=>$(id)?.addEventListener('input',refresh));
    if($('postTargetCustom')) $('postTargetCustom').hidden=saved.mode!=='custom';
  }
  function hidePostTargetGains(){
    const host=$('postTargetGains');
    if(host) host.hidden=true;
    postTargetLastReachMs=NaN;
    postTargetLastCfg=null;
  }
  function postTargetRawGains(reached,cfg){
    const end=cfg.end.getTime();
    const start=Math.max(Date.now(),Math.min(Number(reached)||end,end));
    if(!(end>start)) return {ore:0,essence:0,sand:0,treat:0,resets:0,resourceHours:0};
    const wallHours=(end-start)/3_600_000;
    const resets=countFuturePacificResets(start,end);
    const resourceHours=wallHours+(2*resets);
    const shop=dailyShopMaterialEstimate(cfg,resets);
    const gains={
      ore:Math.max(0,n('oreRate',0))*resourceHours+Math.max(0,Number(shop?.total?.ore)||0),
      essence:Math.max(0,n('essenceRate',0))*resourceHours+Math.max(0,Number(shop?.total?.essence)||0),
      sand:Math.max(0,n('sandRate',0))*resourceHours+Math.max(0,Number(shop?.total?.sand)||0),
      treat:Math.max(0,n('treatRate',0))*resourceHours+Math.max(0,Number(shop?.total?.treat)||0),
      resets,resourceHours
    };
    // Keep post-target Stamina behavior consistent with the live planner. Auto banks surplus in Ore.
    const yields=automaticResourceYields(n('charLevel',cfg.key==='s2'?100:122),cfg);
    const staminaGenerated=Math.max(0,Math.floor(resourceHours*5));
    const staminaNodes=Math.floor(staminaGenerated/Math.max(1,Number(yields.staminaPerNode)||5));
    const mode=$('staminaMode')?.value||'auto';
    const destination=mode==='auto'?'ore':mode;
    if(['ore','essence','sand'].includes(destination)) gains[destination]+=staminaNodes*Math.max(0,Number(yields[destination])||0);
    gains.staminaNodes=staminaNodes;
    gains.staminaDestination=destination;
    return gains;
  }
  function renderPostTargetGains(reached,cfg=activeCalcConfig()){
    const host=$('postTargetGains');
    if(!host) return;
    ensurePostTargetControls();
    const end=cfg.end.getTime();
    if(!Number.isFinite(reached) || reached>=end){ hidePostTargetGains(); return; }
    postTargetLastReachMs=reached;
    postTargetLastCfg=cfg;
    host.hidden=false;
    const state=selectedPostTargetToolState();
    if($('postTargetCustom')) $('postTargetCustom').hidden=state.mode!=='custom';
    const gains=postTargetRawGains(reached,cfg);
    const daily=state.mode==='stop'
      ? {ore:0,essence:0,sand:0}
      : state.mode==='custom'
        ? {ore:state.ore,essence:state.essence,sand:state.sand}
        : {ore:realmDailyValue('ore'),essence:realmDailyValue('essence'),sand:realmDailyValue('sand')};
    const toolMultiplier=Math.max(0,Math.floor(Number(REALM_RUNS_PER_REFRESH)||5))*gains.resets;
    const tools={ore:daily.ore*toolMultiplier,essence:daily.essence*toolMultiplier,sand:daily.sand*toolMultiplier};
    if($('postTargetWindow')) $('postTargetWindow').textContent=`${compactDurationMs(Math.max(0,end-reached))} from target to season end`;
    if($('postTargetOreGain')) $('postTargetOreGain').textContent=`+${fmt(Math.floor(gains.ore))}`;
    if($('postTargetEssenceGain')) $('postTargetEssenceGain').textContent=`+${fmt(Math.floor(gains.essence))}`;
    if($('postTargetSandGain')) $('postTargetSandGain').textContent=`+${fmt(Math.floor(gains.sand))}`;
    if($('postTargetTreatGain')) $('postTargetTreatGain').textContent=`+${fmt(Math.floor(gains.treat))}`;
    if($('postTargetHammerGain')) $('postTargetHammerGain').textContent=`+${fmt(tools.ore)} Hammers`;
    if($('postTargetKnuckleGain')) $('postTargetKnuckleGain').textContent=`+${fmt(tools.essence)} Knuckles`;
    if($('postTargetShovelGain')) $('postTargetShovelGain').textContent=`+${fmt(tools.sand)} Shovels`;
  }

'''
    js = js.replace(anchor, logic + anchor, 1)

    unreachable = "      leftEl.textContent='—';\n      return;"
    if js.count(unreachable) != 1:
        raise SystemExit(f'Expected one unreachable target branch, found {js.count(unreachable)}')
    js = js.replace(unreachable, "      leftEl.textContent='—';\n      hidePostTargetGains();\n      return;", 1)

    reached_line = "    leftEl.textContent=compactDurationMs(Math.max(0,cfg.end.getTime()-reached));"
    if js.count(reached_line) != 1:
        raise SystemExit(f'Expected one target-left render line, found {js.count(reached_line)}')
    js = js.replace(reached_line, reached_line + "\n    renderPostTargetGains(reached,cfg);", 1)

index.write_text(html, encoding='utf-8')
css.write_text(style, encoding='utf-8')
runtime.write_text(js, encoding='utf-8')

# Safety checks: the removed mockup-only green Finish Early Mode card must never be added.
assert 'FINISH EARLY MODE' not in html
assert 'postTargetGains' in html
assert 'Post-target tool plan' in html
assert 'renderPostTargetGains(reached,cfg)' in js
assert "value=\"stop\"" in html and "value=\"custom\"" in html
assert 'POST_TARGET_GAINS_V1' in style
print('Post-target gains planner patch applied.')
