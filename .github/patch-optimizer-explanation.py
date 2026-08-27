from pathlib import Path

PATH=Path('index.html')
text=PATH.read_text(encoding='utf-8')
MARKER='OPTIMIZER_EXPLANATION_V1'
if MARKER in text:
    print('Optimizer explanation already applied.')
    raise SystemExit(0)

anchor='''        <div class="optimizerModeRow" id="optimizerModeRow">
          <div class="optimizerModeCopy"><b>Resource strategy</b><small id="optimizerModeNote">Efficient raw-first planning using normal replacement effort across resources.</small></div>
          <label class="favorOreToggle"><input id="favorOre" type="checkbox"> Favor saving Ore</label>
        </div>'''
if text.count(anchor)!=1:
    raise SystemExit(f'optimizer row anchor count={text.count(anchor)}')

explain='''        <details class="optimizerExplain" id="optimizerExplain">
          <summary><span>How the optimizer decides</span><small>Raw first → saved Realm tools → extra Realm purchases</small></summary>
          <div class="optimizerExplainBody">
            <p><b>1 · Protect enabled Season 2 reserves.</b> Skill Essence and Chrono Sand reserves assign carried/projected Realm tools first, then hold raw material only for any reserve amount those tools cannot cover. Fantomon Treats have no Realm-tool conversion, so an enabled Treat reserve stays raw.</p>
            <p><b>2 · Find the best raw-only score route.</b> The planner searches Gear, Skills, Relics and Fantomons together for a combination that reaches the requested Primostar score. It prefers resources that are already sufficient to fund their reachable Season 1 cap, so surplus Sand, Essence or Treats can replace Ore instead of being stranded. It also avoids paying for meaningless overscore when otherwise-equivalent routes exist.</p>
            <p><b>3 · Use saved Realm tools only if raw cannot reach the target.</b> Reserved tools stay protected. Unreserved Hammers, Knuckles and Shovels become available only after every feasible raw-only route has been considered.</p>
            <p><b>4 · Buy more Realm refreshes only as the final fallback.</b> If the target still cannot be funded, the planner minimizes additional Realm purchases within the remaining daily capacity. If even the maximum remaining capacity is insufficient, it reports the actual material shortfall instead of lowering the target.</p>
            <p><b>Auto Stamina</b> tests Ore, Essence and Sand gathering against the selected upgrade route and uses the split that reduces required paid Realm farming. <b>Gear Lock</b> removes new Gear levels from consideration. <b>Favor saving Ore</b> keeps the same optimizer and gate order, but applies a +50% strategic cost premium to Ore/Hammers so close alternatives lean away from Gear.</p>
          </div>
        </details>'''
text=text.replace(anchor,anchor+'\n'+explain,1)

css='''
<style id="optimizer-explanation-v1">
/* OPTIMIZER_EXPLANATION_V1 */
.optimizerExplain{border:1px solid var(--line);background:var(--ui-subpanel,var(--bg));border-radius:11px;margin:0 0 10px;overflow:hidden}
.optimizerExplain>summary{cursor:pointer;display:flex;align-items:center;justify-content:space-between;gap:16px;padding:10px 12px;list-style:none;color:var(--ink)}
.optimizerExplain>summary::-webkit-details-marker{display:none}
.optimizerExplain>summary span{font-size:10px;font-weight:850}
.optimizerExplain>summary small{color:var(--muted);font-size:9px;text-align:right}
.optimizerExplain>summary:after{content:'+';color:var(--muted);font-weight:900;font-size:14px;line-height:1}
.optimizerExplain[open]>summary:after{content:'−'}
.optimizerExplainBody{border-top:1px solid var(--line);padding:10px 12px 11px;display:grid;gap:8px}
.optimizerExplainBody p{margin:0;color:var(--secondary-text);font-size:9px;line-height:1.55}
.optimizerExplainBody b{color:var(--ink)}
@media(max-width:700px){.optimizerExplain>summary{align-items:flex-start}.optimizerExplain>summary small{display:none}.optimizerExplainBody p{font-size:10px}}
</style>
'''
insert=text.rfind('</head>')
if insert<0:
    raise SystemExit('</head> not found')
text=text[:insert]+css+'\n'+text[insert:]

PATH.write_text(text,encoding='utf-8')
print('Applied OPTIMIZER_EXPLANATION_V1')
