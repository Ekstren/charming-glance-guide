from pathlib import Path

index = Path('index.html')
css = Path('assets/site.css')
runtime = Path('assets/runtime.js')

html = index.read_text(encoding='utf-8')
style = css.read_text(encoding='utf-8')
js = runtime.read_text(encoding='utf-8')

# Add a preview-only post-target Stamina destination control. It must never feed back into
# Smart Balance, target timing, Finish Early, or the pre-target scoring/resource solve.
HTML_MARK = 'name="postTargetStaminaMode"'
if HTML_MARK not in html:
    anchor = '''        </div>
        <div class="postTargetGainGrid">'''
    if html.count(anchor) != 1:
        raise SystemExit(f'Expected one post-target gain-grid anchor, found {html.count(anchor)}')
    block = '''        </div>
        <div class="postTargetStaminaPlan">
          <div class="postTargetPlanHead"><b>Post-target Stamina plan</b><small>Preview only · does not affect score planning or target timing.</small></div>
          <div class="postTargetPlanControls">
            <label><input type="radio" name="postTargetStaminaMode" value="current" checked> Use current plan</label>
            <label><input type="radio" name="postTargetStaminaMode" value="ore"> Ore</label>
            <label><input type="radio" name="postTargetStaminaMode" value="essence"> Essence</label>
            <label><input type="radio" name="postTargetStaminaMode" value="sand"> Sand</label>
            <label><input type="radio" name="postTargetStaminaMode" value="save"> Save Stamina</label>
          </div>
        </div>
        <div class="postTargetGainGrid">'''
    html = html.replace(anchor, block, 1)

CSS_MARK = '/* POST_TARGET_STAMINA_V1 */'
if CSS_MARK not in style:
    style += '''\n\n/* POST_TARGET_STAMINA_V1 */\n.postTargetStaminaPlan{border-top:1px solid var(--line);margin-top:9px;padding-top:9px}\n'''

if "stamina:'current'" not in js:
    old = "    let out={mode:'current',ore:0,essence:0,sand:0};"
    new = "    let out={mode:'current',stamina:'current',ore:0,essence:0,sand:0};"
    if js.count(old) != 1:
        raise SystemExit(f'Expected one post-target state initializer, found {js.count(old)}')
    js = js.replace(old, new, 1)

    old = "      if(['current','stop','custom'].includes(saved.mode)) out.mode=saved.mode;\n      for(const k of ['ore','essence','sand']) if(Number.isFinite(Number(saved[k]))) out[k]=clamp(Math.floor(Number(saved[k])),0,20);"
    new = "      if(['current','stop','custom'].includes(saved.mode)) out.mode=saved.mode;\n      if(['current','ore','essence','sand','save'].includes(saved.stamina)) out.stamina=saved.stamina;\n      for(const k of ['ore','essence','sand']) if(Number.isFinite(Number(saved[k]))) out[k]=clamp(Math.floor(Number(saved[k])),0,20);"
    if js.count(old) != 1:
        raise SystemExit(f'Expected one post-target saved-state loader, found {js.count(old)}')
    js = js.replace(old, new, 1)

    old = "    const state={mode:checked?.value||'current',ore:0,essence:0,sand:0};"
    new = "    const staminaChecked=document.querySelector('input[name=\"postTargetStaminaMode\"]:checked');\n    const state={mode:checked?.value||'current',stamina:staminaChecked?.value||'current',ore:0,essence:0,sand:0};"
    if js.count(old) != 1:
        raise SystemExit(f'Expected one selected post-target state initializer, found {js.count(old)}')
    js = js.replace(old, new, 1)

    old = "    if(mode) mode.checked=true;\n    if($('postTargetOreDaily')) $('postTargetOreDaily').value=String(saved.ore);"
    new = "    if(mode) mode.checked=true;\n    const staminaMode=document.querySelector(`input[name=\"postTargetStaminaMode\"][value=\"${saved.stamina}\"]`) || document.querySelector('input[name=\"postTargetStaminaMode\"][value=\"current\"]');\n    if(staminaMode) staminaMode.checked=true;\n    if($('postTargetOreDaily')) $('postTargetOreDaily').value=String(saved.ore);"
    if js.count(old) != 1:
        raise SystemExit(f'Expected one post-target control restore anchor, found {js.count(old)}')
    js = js.replace(old, new, 1)

    old = "    host.querySelectorAll('input[name=\"postTargetToolMode\"]').forEach(el=>el.addEventListener('change',refresh));\n    ['postTargetOreDaily','postTargetEssenceDaily','postTargetSandDaily'].forEach(id=>$(id)?.addEventListener('input',refresh));"
    new = "    host.querySelectorAll('input[name=\"postTargetToolMode\"]').forEach(el=>el.addEventListener('change',refresh));\n    host.querySelectorAll('input[name=\"postTargetStaminaMode\"]').forEach(el=>el.addEventListener('change',refresh));\n    ['postTargetOreDaily','postTargetEssenceDaily','postTargetSandDaily'].forEach(id=>$(id)?.addEventListener('input',refresh));"
    if js.count(old) != 1:
        raise SystemExit(f'Expected one post-target control binding anchor, found {js.count(old)}')
    js = js.replace(old, new, 1)

    old = "  function postTargetRawGains(reached,cfg){"
    new = "  function postTargetRawGains(reached,cfg,state=selectedPostTargetToolState()){"
    if js.count(old) != 1:
        raise SystemExit(f'Expected one postTargetRawGains signature, found {js.count(old)}')
    js = js.replace(old, new, 1)

    old = "    const mode=$('staminaMode')?.value||'auto';\n    const destination=mode==='auto'?'ore':mode;\n    if(['ore','essence','sand'].includes(destination)) gains[destination]+=staminaNodes*Math.max(0,Number(yields[destination])||0);"
    new = "    const currentMode=$('staminaMode')?.value||'auto';\n    const requested=state?.stamina||'current';\n    const destination=requested==='current'\n      ? (currentMode==='auto'?'ore':currentMode)\n      : (requested==='save'?null:requested);\n    if(['ore','essence','sand'].includes(destination)) gains[destination]+=staminaNodes*Math.max(0,Number(yields[destination])||0);"
    if js.count(old) != 1:
        raise SystemExit(f'Expected one post-target Stamina destination block, found {js.count(old)}')
    js = js.replace(old, new, 1)

    old = "    const gains=postTargetRawGains(reached,cfg);"
    new = "    const gains=postTargetRawGains(reached,cfg,state);"
    if js.count(old) != 1:
        raise SystemExit(f'Expected one postTargetRawGains call, found {js.count(old)}')
    js = js.replace(old, new, 1)

# Hide the successful-plan optimizer narration the user asked to remove. Keep warning/status
# summaries available in exceptional states; only the normal success line is suppressed.
old = "      if(gearLocked) brief.push('Gear locked');\n      $('optimizerSummary').hidden=false;\n      $('optimizerSummary').textContent=brief.join(' · ');\n      setRawRemaining('oreBalance',plan.oreCost,resources.ore);"
new = "      if(gearLocked) brief.push('Gear locked');\n      $('optimizerSummary').hidden=true;\n      $('optimizerSummary').textContent='';\n      setRawRemaining('oreBalance',plan.oreCost,resources.ore);"
if old in js:
    js = js.replace(old, new, 1)
elif "$('optimizerSummary').hidden=true;\n      $('optimizerSummary').textContent='';\n      setRawRemaining('oreBalance',plan.oreCost,resources.ore);" not in js:
    raise SystemExit('Could not find normal successful optimizer summary block')

index.write_text(html, encoding='utf-8')
css.write_text(style, encoding='utf-8')
runtime.write_text(js, encoding='utf-8')

# Verification guards.
assert 'name="postTargetStaminaMode"' in html
assert 'POST_TARGET_STAMINA_V1' in style
assert "stamina:'current'" in js
assert "requested==='save'?null:requested" in js
assert "postTargetRawGains(reached,cfg,state)" in js
assert "$('optimizerSummary').hidden=true" in js
