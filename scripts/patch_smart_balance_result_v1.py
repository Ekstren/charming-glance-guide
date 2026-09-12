from pathlib import Path


def replace_once(text, old, new, label):
    if old not in text:
        raise SystemExit(f"{label} pattern not found")
    return text.replace(old, new, 1)

# --- index.html ---
p = Path("index.html")
s = p.read_text()

old = '''      <div class="targetTiming" id="targetTiming" title="Estimate based on current production inputs and the recommended target route.">
        <span><small>Projected target</small><b id="targetReachedDate">—</b></span>
        <span><small>Season left after target</small><b id="targetSeasonLeft">—</b></span>
      </div>'''
new = '''      <div class="targetTiming" id="targetTiming" title="Estimate based on current production inputs and the recommended target route.">
        <span><small>Projected target</small><b id="targetReachedDate">—</b></span>
        <span><small>Season left after target</small><b id="targetSeasonLeft">—</b></span>
        <span class="targetCharacterCard"><small>Character used for target</small><b id="targetCharacterAtGoal">—</b><em>Used in score calculation</em></span>
        <span><small>Season-end character</small><b id="seasonEndCharacterResult">—</b><em>Projected final season level</em></span>
      </div>'''
s = replace_once(s, old, new, "target timing cards")

s = replace_once(
    s,
    '<div><span>Estimated post-target totals</span><small id="postTargetWindow">—</small></div>',
    '<div><span>Estimated next-season inventory</span><small id="postTargetWindow">—</small></div>',
    "next-season inventory heading",
)
s = replace_once(
    s,
    '<small>Bed EXP is claimed normally until 34h before season end; the final 36h stays banked for next season.</small>',
    '<small>What you will have at season end after reaching the target. Bed EXP still banks the final 36h for next season.</small>',
    "next-season inventory helper",
)

# Keep post-target controls, but move them behind one optional disclosure so the result is level/carry focused.
s = replace_once(
    s,
    '        <div class="postTargetToolPlan">',
    '        <details class="postTargetOptions"><summary>Post-target plan options</summary><div class="postTargetOptionsBody">\n        <div class="postTargetToolPlan">',
    "post-target options open",
)
old = '''            <label><input type="radio" name="postTargetStaminaMode" value="sand"> Sand</label>
          </div>
        </div>
        <div class="postTargetGainGrid">'''
new = '''            <label><input type="radio" name="postTargetStaminaMode" value="sand"> Sand</label>
          </div>
        </div>
        </div></details>
        <div class="postTargetGainGrid">'''
s = replace_once(s, old, new, "post-target options close")

p.write_text(s)

# --- assets/runtime.js ---
p = Path("assets/runtime.js")
s = p.read_text()
old = '''  function renderTargetTiming(plan,resourceBlocked,requestedDesired,pEnd,cfg=activeCalcConfig()){
    const host=$('targetTiming'),dateEl=$('targetReachedDate'),leftEl=$('targetSeasonLeft');
    if(!host||!dateEl||!leftEl) return;
    const reached=estimateTargetReachMoment(plan,resourceBlocked,requestedDesired,pEnd,cfg);
    host.classList.toggle('isUnreachable',!Number.isFinite(reached));
    if(!Number.isFinite(reached)){
      dateEl.textContent='Not projected';
      leftEl.textContent='—';
      hidePostTargetGains();
      return;
    }
    const now=Date.now();
    dateEl.textContent=reached<=now+60_000?'Now':targetMomentLabel(reached);
    leftEl.textContent=compactDurationMs(Math.max(0,cfg.end.getTime()-reached));
    renderPostTargetGains(reached,plan,pEnd,cfg);
  }'''
new = '''  function renderTargetTiming(plan,resourceBlocked,requestedDesired,pEnd,cfg=activeCalcConfig()){
    const host=$('targetTiming'),dateEl=$('targetReachedDate'),leftEl=$('targetSeasonLeft');
    const targetCharEl=$('targetCharacterAtGoal'),seasonCharEl=$('seasonEndCharacterResult');
    if(!host||!dateEl||!leftEl) return;
    const reached=estimateTargetReachMoment(plan,resourceBlocked,requestedDesired,pEnd,cfg);
    host.classList.toggle('isUnreachable',!Number.isFinite(reached));
    if(!Number.isFinite(reached)){
      dateEl.textContent='Not projected';
      leftEl.textContent='—';
      if(targetCharEl) targetCharEl.textContent='—';
      if(seasonCharEl) seasonCharEl.textContent='—';
      hidePostTargetGains();
      return;
    }
    const now=Date.now();
    const targetP=projectCharacterTo(reached,cfg);
    const seasonP=projectCharacter(cfg);
    dateEl.textContent=reached<=now+60_000?'Now':targetMomentLabel(reached);
    leftEl.textContent=compactDurationMs(Math.max(0,cfg.end.getTime()-reached));
    if(targetCharEl) targetCharEl.textContent=`Lv.${targetP.level} · ${(targetP.pct*100).toFixed(1)}%`;
    if(seasonCharEl) seasonCharEl.textContent=`Lv.${seasonP.level} · ${(seasonP.pct*100).toFixed(1)}%`;
    renderPostTargetGains(reached,plan,pEnd,cfg);
  }'''
s = replace_once(s, old, new, "target character timing renderer")

old = "if($('postTargetWindow')) $('postTargetWindow').textContent=`${compactDurationMs(Math.max(0,end-reached))} after target · season-end totals`;"
new = "if($('postTargetWindow')) $('postTargetWindow').textContent=`${compactDurationMs(Math.max(0,end-reached))} of post-target gathering · season-end carry`;"
s = replace_once(s, old, new, "post-target window label")
p.write_text(s)

# --- assets/site.css ---
p = Path("assets/site.css")
s = p.read_text()
marker = "/* SMART_BALANCE_RESULT_V1 */"
if marker in s:
    raise SystemExit("SMART_BALANCE_RESULT_V1 already applied")
s += r'''

/* SMART_BALANCE_RESULT_V1
   Main result = target timing + target Character + recommended levels + next-season carry.
   Detailed material spend remains available in the Materials input panel / score details, but
   is intentionally removed from the primary Smart Balance result. */
.calcResults .planCosts{display:none!important}
.targetTiming>span em{display:block;color:var(--muted);font-size:8px;font-style:normal;line-height:1.35;margin-top:4px}
.targetTiming .targetCharacterCard{border-color:color-mix(in srgb,var(--purple) 76%,var(--line));background:color-mix(in srgb,var(--surface) 84%,var(--purple));box-shadow:inset 0 0 0 1px color-mix(in srgb,var(--purple) 18%,transparent)}
.targetTiming .targetCharacterCard small{color:color-mix(in srgb,var(--purple) 72%,var(--ink))}
.postTargetHeader>div>span{color:color-mix(in srgb,var(--purple) 72%,var(--ink))}
.postTargetOptions{border-top:1px solid var(--line);border-bottom:1px solid var(--line);margin:10px 0;padding:0}
.postTargetOptions>summary{cursor:pointer;color:var(--body-text);font-size:9px;font-weight:850;letter-spacing:.03em;padding:9px 2px;list-style:none}
.postTargetOptions>summary::-webkit-details-marker{display:none}
.postTargetOptions>summary:after{content:'+';float:right;color:var(--muted);font-size:14px;line-height:1}
.postTargetOptions[open]>summary:after{content:'−'}
.postTargetOptionsBody{padding:0 0 10px}
.postTargetOptions .postTargetToolPlan{border-top:0;padding-top:0}
.postTargetGainGrid{margin-top:10px}
@media (max-width:430px){
  .targetTiming{grid-template-columns:1fr}
  .targetTiming>span em{font-size:7.5px}
}
'''
p.write_text(s)
print("Patched Smart Balance result layout")
