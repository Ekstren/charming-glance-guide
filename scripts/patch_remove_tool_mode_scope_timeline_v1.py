from pathlib import Path
import re

p=Path('index.html')
s=p.read_text(encoding='utf-8')
MARK='REMOVE_TOOL_MODE_SCOPE_TIMELINE_V1'
if MARK in s:
    print('optimizer/timeline cleanup already applied')
    raise SystemExit(0)

def replace_once(old,new,label):
    global s
    if old not in s:
        raise SystemExit(f'missing anchor: {label}')
    s=s.replace(old,new,1)

def remove_js_function(name):
    global s
    needle=f'  function {name}('
    start=s.find(needle)
    if start<0:
        raise SystemExit(f'missing JS function: {name}')
    brace=s.find('{',start)
    depth=0
    i=brace
    quote=None
    esc=False
    line_comment=False
    block_comment=False
    while i<len(s):
        c=s[i]
        n=s[i+1] if i+1<len(s) else ''
        if line_comment:
            if c=='\n': line_comment=False
        elif block_comment:
            if c=='*' and n=='/': block_comment=False; i+=1
        elif quote:
            if esc: esc=False
            elif c=='\\': esc=True
            elif c==quote: quote=None
        else:
            if c=='/' and n=='/': line_comment=True; i+=1
            elif c=='/' and n=='*': block_comment=True; i+=1
            elif c in ('\"',"'",'`'): quote=c
            elif c=='{': depth+=1
            elif c=='}':
                depth-=1
                if depth==0:
                    end=i+1
                    if end<len(s) and s[end]=='\n': end+=1
                    s=s[:start]+s[end:]
                    return
        i+=1
    raise SystemExit(f'unclosed JS function: {name}')

# 1) Remove the user-facing toggle and every state hook for it.
s,n=re.subn(r'\n<style id="realm-tool-preserve-policy-v4">.*?</style>\n','\n',s,count=1,flags=re.S)
if n!=1: raise SystemExit('tool-toggle CSS block not found')
s,n=re.subn(r'\n\s*<div class="rolloverHold seasonPlanningControls">\s*<label class="realmToolPreserveOption realmToolPreserveTop"><input id="preserveRealmTools"[^>]*>.*?</label>\s*</div>','',s,count=1,flags=re.S)
if n!=1: raise SystemExit('tool-toggle markup not found')
replace_once("  const CHECK_IDS = ['preserveRealmTools'];","  const CHECK_IDS = [];",'CHECK_IDS')
s,n=re.subn(r"  const S2_SCORING_START_CHECKS=Object\.freeze\(\{\s*preserveRealmTools:true\s*\}\);","  const S2_SCORING_START_CHECKS=Object.freeze({});",s,count=1)
if n!=1: raise SystemExit('S2 scoring-start checkbox defaults not found')
s=s.replace("      if(hadState && state.preserveRealmTools===undefined) state.preserveRealmTools=true;\n",'',1)

# 2) Remove the 10%/20% hurdle policy itself, not merely the checkbox.
# Pure acquisition efficiency is now always primary; existing Realm burden remains an
# exact-tie sourcing tiebreaker in betterFeasibleCandidate/betterDiagnosticCandidate.
s,n=re.subn(r'  /\* REALM_TOOL_EFFICIENCY_V4.*?\*/\n','',s,count=1,flags=re.S)
if n!=1: raise SystemExit('Realm tool policy comment not found')
for line in [
    '  const REALM_SAVED_TOOL_EFFICIENCY_HURDLE=0.10;\n',
    '  const REALM_PAID_REFRESH_EFFICIENCY_HURDLE=0.20;\n',
]:
    if line not in s: raise SystemExit(f'missing policy constant: {line.strip()}')
    s=s.replace(line,'',1)
for fn in ['preserveRealmToolsEnabled','acquisitionImprovementFraction','realmToolHurdleForMoreEfficientRoute','acquisitionEffortWinsAfterToolHurdle']:
    remove_js_function(fn)
s=s.replace('acquisitionEffortWinsAfterToolHurdle(candidate,best)','compareAcquisitionEffort(candidate,best)')
s=s.replace('Diagnostics follow the same saved-tool / paid-refresh hurdles as funded plans.','Diagnostics follow the same acquisition-effort ranking as funded plans.')

# 3) Rewrite optimizer explanation so UI matches the now-single policy.
replace_once(
    '<summary><span>How the optimizer decides</span><small>Best efficiency · minimize tools</small></summary>',
    '<summary><span>How the optimizer decides</span><small>Best overall acquisition efficiency</small></summary>',
    'optimizer summary wording')
old_steps='''            <p><b>3 · Minimize Realm tools unless they materially improve the route.</b> With <i>Minimize tools</i> enabled, spending saved Realm tools must improve acquisition effort by more than 10%. A route that requires additional Realm purchases must improve it by more than 20%. Turn the toggle off for strict pure-efficiency ranking.</p>\n            <p><b>4 · Realm purchases face the higher hurdle.</b> Premium-currency Realm purchases only win when their route is more than 20% better on modeled acquisition effort. If even maximum Realm capacity cannot fund the requested target, the planner reports the actual shortfall instead of lowering the target.</p>'''
new_steps='''            <p><b>3 · Rank by overall acquisition efficiency.</b> Raw materials, saved Realm tools and paid Realm purchases are all sourcing options for the same progression route. The optimizer chooses the route with the lowest modeled acquisition burden instead of applying a separate tool-preservation mode.</p>\n            <p><b>4 · Use Realm burden only to break true efficiency ties.</b> If two routes have effectively identical acquisition effort, the planner prefers the one with the lighter Realm/tool sourcing burden. If even maximum Realm capacity cannot fund the requested target, it reports the actual shortfall instead of lowering the target.</p>'''
replace_once(old_steps,new_steps,'optimizer steps 3-4')
s=s.replace('The active planning control is the single soft Realm-tool preservation toggle, while Season 2 uses live inventory directly.','Season 2 uses live inventory directly; Realm tools and paid purchases are treated as sourcing options rather than a separate optimizer mode.')

# 4) Clean reward-table headings; the chapter names already identify the seasons.
s=s.replace("const groups=[{title:'Season 1 · Witching Hours',nodes:s1Nodes,offset:0}];","const groups=[{title:'Witching Hours',nodes:s1Nodes,offset:0}];",1)
s=s.replace("groups.push({title:'Season 2 · Crossed Paths',nodes:ASTRAL_PACT_NODES.slice(40),offset:40});","groups.push({title:'Crossed Paths',nodes:ASTRAL_PACT_NODES.slice(40),offset:40});",1)

# 5) Scope Timeline audit/source footer to Timeline instead of the global page shell.
footer_match=re.search(r'<footer><p>Timeline refreshed.*?</footer>',s,flags=re.S)
if not footer_match: raise SystemExit('global Timeline footer not found')
footer=footer_match.group(0).replace('<footer>','<footer class="timelineSources">',1)
s=s[:footer_match.start()]+s[footer_match.end():]
timeline_tail='  <button class="todayButton" id="todayButton">Jump to current</button>\n</section>'
if timeline_tail not in s: raise SystemExit('timeline section tail not found')
s=s.replace(timeline_tail,'  <button class="todayButton" id="todayButton">Jump to current</button>\n  '+footer+'\n</section>',1)

# Source card styling follows the same content rail/card language as the other tabs.
style=f'''\n<style id="timeline-source-scope-v1">\n/* {MARK}: Timeline audit + sources belong to Timeline only, not the global shell. */\n#timelineSection>.timelineSources{{max-width:940px;margin:0 auto 34px;padding:16px 18px;border:1px solid var(--line);border-radius:14px;background:var(--surface);color:var(--muted);display:flex;align-items:flex-start;justify-content:space-between;gap:18px;font-size:10px;line-height:1.5}}\n#timelineSection>.timelineSources p{{margin:0;max-width:760px}}\n#timelineSection>.timelineSources .footerLinks{{display:flex;gap:10px;flex-wrap:wrap;flex:0 0 auto}}\n#timelineSection>.timelineSources a{{color:var(--green);font-weight:800;text-decoration:none;white-space:nowrap}}\n@media(max-width:720px){{#timelineSection>.timelineSources{{margin:0 10px 24px;padding:14px;flex-direction:column;gap:10px}}}}\n</style>\n'''
if '</head>' not in s: raise SystemExit('head close missing')
s=s.replace('</head>',style+'</head>',1)

# Strong invariants: none of the removed mode can survive in active page code.
for token in ['id="preserveRealmTools"','preserveRealmToolsEnabled','REALM_SAVED_TOOL_EFFICIENCY_HURDLE','REALM_PAID_REFRESH_EFFICIENCY_HURDLE','acquisitionEffortWinsAfterToolHurdle','Minimize tools']:
    if token in s: raise SystemExit(f'removed optimizer mode token still present: {token}')
if s.count('class="timelineSources"')!=1: raise SystemExit('Timeline source footer is not uniquely scoped')

p.write_text(s,encoding='utf-8')
print('removed Minimize tools mode completely, switched to one efficiency policy, cleaned reward headings, and scoped sources to Timeline')
