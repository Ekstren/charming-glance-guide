from pathlib import Path

index_path = Path('index.html')
runtime_path = Path('assets/runtime.js')
css_path = Path('assets/site.css')

index = index_path.read_text()
runtime = runtime_path.read_text()
css = css_path.read_text()

# Headline: target Primostars + projected excess Primostars by season end.
old = '''        <strong class="starTotal"><span id="currentStars">—</span><small> Primostars</small></strong>'''
new = '''        <strong class="starTotal"><span id="currentStars">—</span><span id="seasonEndExcessStars" class="seasonEndExcess seasonEndExcessStars" hidden>(+0)</span><small> Primostars</small></strong>'''
if old in index:
    index = index.replace(old, new, 1)
elif 'id="seasonEndExcessStars"' not in index:
    raise SystemExit('starTotal pattern not found')

# Score: target-route score + projected score gained afterward.
old = '''        <span><small>Score</small><b id="currentScoreNow">—</b><i>→</i><b id="summaryOptimizedScore">—</b></span>'''
new = '''        <span><small>Score</small><b id="currentScoreNow">—</b><i>→</i><b id="summaryOptimizedScore">—</b><b id="seasonEndExcessScore" class="seasonEndExcess seasonEndExcessScore" hidden>(+0)</b></span>'''
if old in index:
    index = index.replace(old, new, 1)
elif 'id="seasonEndExcessScore"' not in index:
    raise SystemExit('summary score pattern not found')

# Small dynamic explanation immediately below the score/target row.
old = '''      </div>\n      <div class="targetTiming" id="targetTiming" title="Estimate based on current production inputs and the recommended target route.">'''
new = '''      </div>\n      <!-- SEASON_END_EXCESS_V1 -->\n      <small id="seasonEndExcessNote" class="seasonEndExcessNote" hidden>Parentheses show projected gains after reaching the target.</small>\n      <div class="targetTiming" id="targetTiming" title="Estimate based on current production inputs and the recommended target route.">'''
if old in index:
    index = index.replace(old, new, 1)
elif 'id="seasonEndExcessNote"' not in index:
    raise SystemExit('targetTiming insertion pattern not found')

# Runtime refs.
old = '''    const targetCharEl=$('targetCharacterAtGoal'),seasonCharEl=$('seasonEndCharacterResult');'''
new = '''    const targetCharEl=$('targetCharacterAtGoal'),seasonCharEl=$('seasonEndCharacterResult');\n    const excessStarsEl=$('seasonEndExcessStars'),excessScoreEl=$('seasonEndExcessScore'),excessNoteEl=$('seasonEndExcessNote');'''
if old in runtime:
    runtime = runtime.replace(old, new, 1)
elif "const excessStarsEl=$('seasonEndExcessStars')" not in runtime:
    raise SystemExit('renderTargetTiming refs pattern not found')

# Clear the projected excess when target timing is unavailable.
old = '''      if(targetCharEl) targetCharEl.textContent='—';\n      if(seasonCharEl) seasonCharEl.textContent='—';\n      hidePostTargetGains();'''
new = '''      if(targetCharEl) targetCharEl.textContent='—';\n      if(seasonCharEl) seasonCharEl.textContent='—';\n      if(excessStarsEl){excessStarsEl.hidden=true;excessStarsEl.textContent='';}\n      if(excessScoreEl){excessScoreEl.hidden=true;excessScoreEl.textContent='';}\n      if(excessNoteEl){excessNoteEl.hidden=true;excessNoteEl.textContent='';}\n      hidePostTargetGains();'''
if old in runtime:
    runtime = runtime.replace(old, new, 1)
elif 'excessStarsEl.hidden=true' not in runtime:
    raise SystemExit('unreachable clear pattern not found')

# Calculate excess from the SAME recommended non-character build, allowing only Character
# EXP to continue from the target route to the normal season-end claim cutoff.
old = '''    if(targetCharEl) targetCharEl.textContent=`Lv.${targetP.level} · ${(targetP.pct*100).toFixed(1)}%`;\n    if(seasonCharEl) seasonCharEl.textContent=`Lv.${seasonP.level} · ${(seasonP.pct*100).toFixed(1)}%`;\n    renderPostTargetGains(reached,plan,pEnd,cfg);'''
new = '''    if(targetCharEl) targetCharEl.textContent=`Lv.${targetP.level} · ${(targetP.pct*100).toFixed(1)}%`;\n    if(seasonCharEl) seasonCharEl.textContent=`Lv.${seasonP.level} · ${(seasonP.pct*100).toFixed(1)}%`;\n\n    /* SEASON_END_EXCESS_V1\n       Keep the requested plan/build fixed. Parenthetical values show what Character EXP alone\n       adds AFTER the displayed target-route score, through the normal season-end EXP projection.\n       Primostar excess is recomputed from the actual floor conversion, not excessScore/scorePerStar. */\n    const planScore=Math.max(0,Number(plan?.score)||0);\n    const nonCharacterScore=Math.max(0,planScore-characterScore(pEnd,cfg));\n    const seasonEndScore=Math.max(planScore,nonCharacterScore+characterScore(seasonP,cfg));\n    const excessScore=Math.max(0,Math.floor(seasonEndScore-planScore+1e-9));\n    const historical=Math.max(0,Math.floor(n('historicalStars',0)));\n    const planStars=historical+cfg.starBase+Math.floor(planScore/cfg.scorePerStar);\n    const seasonEndStars=historical+cfg.starBase+Math.floor(seasonEndScore/cfg.scorePerStar);\n    const excessStars=Math.max(0,seasonEndStars-planStars);\n    const timeAfterTargetMs=Math.max(0,cfg.end.getTime()-reached);\n    const timeAfterTarget=compactDurationMs(timeAfterTargetMs);\n    if(excessStarsEl){\n      excessStarsEl.textContent=`(+${fmt(excessStars)})`;\n      excessStarsEl.hidden=excessStars<=0;\n    }\n    if(excessScoreEl){\n      excessScoreEl.textContent=`(+${fmt(excessScore)})`;\n      excessScoreEl.hidden=excessScore<=0;\n    }\n    if(excessNoteEl){\n      const hasExcess=excessStars>0||excessScore>0;\n      excessNoteEl.textContent=`( ) = projected extra gained after reaching the target ${timeAfterTarget} before season end`;\n      excessNoteEl.hidden=!hasExcess||timeAfterTargetMs<=0;\n    }\n    renderPostTargetGains(reached,plan,pEnd,cfg);'''
if old in runtime:
    runtime = runtime.replace(old, new, 1)
elif 'SEASON_END_EXCESS_V1' not in runtime:
    raise SystemExit('target excess calculation pattern not found')

css_marker = '''\n/* SEASON_END_EXCESS_V1 */\n.starTotal .seasonEndExcessStars{display:inline-block;margin-left:8px;color:var(--green);font-size:.34em;font-weight:850;letter-spacing:0;vertical-align:middle}\n.resultScoreLine .seasonEndExcessScore{display:inline-block;margin-left:6px;color:var(--green);font-size:10px;font-weight:850;white-space:nowrap}\n.seasonEndExcessNote{display:block;color:var(--muted);font-size:8px;line-height:1.35;margin:-7px 2px 8px;text-align:right}\n@media (max-width:430px){.starTotal .seasonEndExcessStars{margin-left:5px;font-size:.3em}.resultScoreLine .seasonEndExcessScore{font-size:9px;margin-left:4px}.seasonEndExcessNote{font-size:7px;text-align:left;margin-top:-5px}}\n'''
if '/* SEASON_END_EXCESS_V1 */' not in css:
    css += css_marker

index_path.write_text(index)
runtime_path.write_text(runtime)
css_path.write_text(css)
