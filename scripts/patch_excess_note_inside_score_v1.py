from pathlib import Path

index = Path('index.html')
css = Path('assets/site.css')

html = index.read_text(encoding='utf-8')
old = '''      <div class="resultScoreLine">
        <span><small>Score</small><b id="currentScoreNow">—</b><i>→</i><b id="summaryOptimizedScore">—</b><b id="seasonEndExcessScore" class="seasonEndExcess seasonEndExcessScore" hidden>(+0)</b></span>
        <span><small>Target</small><b id="desiredScore">—</b><em id="targetStatus">—</em></span>
      </div>
      <!-- SEASON_END_EXCESS_V1 -->
      <small id="seasonEndExcessNote" class="seasonEndExcessNote" hidden>Parentheses show projected gains after reaching the target.</small>'''
new = '''      <div class="resultScoreLine">
        <span><small>Score</small><b id="currentScoreNow">—</b><i>→</i><b id="summaryOptimizedScore">—</b><b id="seasonEndExcessScore" class="seasonEndExcess seasonEndExcessScore" hidden>(+0)</b></span>
        <span><small>Target</small><b id="desiredScore">—</b><em id="targetStatus">—</em></span>
        <!-- SEASON_END_EXCESS_V1 -->
        <small id="seasonEndExcessNote" class="seasonEndExcessNote" hidden>Parentheses show projected gains after reaching the target.</small>
      </div>'''
if old not in html:
    raise SystemExit('expected score/excess markup not found')
html = html.replace(old, new, 1)
index.write_text(html, encoding='utf-8')

style = css.read_text(encoding='utf-8')
marker = '/* SEASON_END_EXCESS_NOTE_IN_CARD_V1 */'
if marker not in style:
    style += '''\n\n/* SEASON_END_EXCESS_NOTE_IN_CARD_V1 */
.resultScoreLine{flex-wrap:wrap}
.resultScoreLine>.seasonEndExcessNote{order:3;flex:0 0 100%;width:100%;display:block;margin:1px 0 0;padding-top:5px;border-top:1px solid color-mix(in srgb,var(--line) 65%,transparent);color:var(--muted);font-size:8px!important;line-height:1.35;text-align:left;text-transform:none!important;letter-spacing:0!important;font-weight:650!important}
@media(max-width:700px){.resultScoreLine>.seasonEndExcessNote{margin-top:2px;padding-top:5px;font-size:8px!important}}
'''
css.write_text(style, encoding='utf-8')

print('Moved season-end excess explanation inside the score card.')
