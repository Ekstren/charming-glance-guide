from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')
original = text

marker = 'REALM_TOOL_PRESERVE_POLICY_V3'
if marker in text:
    print(f'{marker} already applied')
    raise SystemExit(0)

# Remove the four user-facing S1->S2 reserve toggles, but keep hidden compatibility
# inputs until the Season-2-only cleanup removes the old rollover code entirely.
old_controls = '''          <label><input id="reserveS2Ore" checked type="checkbox"> Reserve S2 Ore</label>\n          <label><input id="reserveS2Essence" checked type="checkbox"> Reserve S2 Essence</label>\n          <label><input id="reserveS2Sand" checked type="checkbox"> Reserve S2 Sand</label>\n          <label><input id="reserveS2Treats" checked type="checkbox"> Reserve S2 Treats</label>'''
new_controls = '''          <input id="reserveS2Ore" checked type="checkbox" hidden>\n          <input id="reserveS2Essence" checked type="checkbox" hidden>\n          <input id="reserveS2Sand" checked type="checkbox" hidden>\n          <input id="reserveS2Treats" checked type="checkbox" hidden>'''
assert old_controls in text, 'visible reserve-toggle block missing'
text = text.replace(old_controls, new_controls, 1)

# Add one simple, always-visible policy control next to the Material Realm daily plan.
realm_title = '                <span class="realmDailyTitle">Daily Realm refresh plan <small>Each refresh = 5 tools · max 20/day per Realm</small></span>\n'
assert realm_title in text, 'realm daily title anchor missing'
realm_toggle = realm_title + '''                <label class="realmToolPreserveOption"><input id="preserveRealmTools" checked type="checkbox"><span>Preserve Realm tools if possible</span><small>When two target routes are within 5% acquisition efficiency, prefer the one that uses fewer saved tools / paid refreshes. Turn this off for pure efficiency.</small></label>\n'''
text = text.replace(realm_title, realm_toggle, 1)

# Lightweight styling that fits the existing Realm controls.
head_anchor = '</head>'
assert head_anchor in text
style = '''<style id="realm-tool-preserve-policy-v3">\n.realmToolPreserveOption{display:flex;align-items:flex-start;gap:8px;margin:9px 0 12px;color:var(--body-text);font-size:11px;font-weight:750;line-height:1.35}.realmToolPreserveOption input{margin-top:2px;flex:0 0 auto}.realmToolPreserveOption span{white-space:nowrap}.realmToolPreserveOption small{color:var(--muted);font-size:9px;font-weight:600;line-height:1.4}\n@media(max-width:680px){.realmToolPreserveOption{flex-wrap:wrap}.realmToolPreserveOption small{flex-basis:100%;padding-left:22px}}\n</style>\n'''
text = text.replace(head_anchor, style + head_anchor, 1)

# Persist only the new policy toggle plus Bed EXP hold. The hidden legacy reserve inputs
# deliberately reset to their conservative checked defaults until S1 is retired.
old_checks = """  const S2_SCORING_START_CHECKS=Object.freeze({\n    holdExp:true,reserveS2Ore:false,reserveS2Essence:false,reserveS2Sand:false,reserveS2Treats:false\n  });"""
new_checks = """  const S2_SCORING_START_CHECKS=Object.freeze({\n    holdExp:true,preserveRealmTools:true\n  });"""
assert old_checks in text, 'S2 scoring-start checks anchor missing'
text = text.replace(old_checks, new_checks, 1)

old_check_ids = "  const CHECK_IDS = ['holdExp','reserveS2Ore','reserveS2Essence','reserveS2Sand','reserveS2Treats'];"
new_check_ids = "  const CHECK_IDS = ['holdExp','preserveRealmTools'];"
assert old_check_ids in text, 'CHECK_IDS anchor missing'
text = text.replace(old_check_ids, new_check_ids, 1)

migration_anchor = "      if(hadState && state.reserveS2Ore===undefined) state.reserveS2Ore=true;"
assert migration_anchor in text, 'state migration anchor missing'
text = text.replace(migration_anchor, migration_anchor + "\n      if(hadState && state.preserveRealmTools===undefined) state.preserveRealmTools=true;", 1)

# Add a soft 5% efficiency window. With the policy enabled, tiny acquisition-efficiency
# improvements are not allowed to burn tools. Outside the window, pure efficiency still wins.
helper_old = """  function compareAcquisitionEffort(candidate,best){\n    const cm=candidateResourceMetric(candidate),bm=candidateResourceMetric(best);\n    if(cm<bm-1e-9) return true;\n    if(cm>bm+1e-9) return false;\n    return null;\n  }\n"""
helper_new = helper_old + """  /* REALM_TOOL_PRESERVE_POLICY_V3\n     A saved Realm tool is strategically scarce even when its material yield is known.\n     With preservation enabled, routes within 5% acquisition effort are treated as close\n     enough that lower tool/Dawnium burden wins. A route that is >5% more efficient still\n     wins outright, so preservation cannot trap the planner in a materially worse path. */\n  const REALM_TOOL_PRESERVE_EFFICIENCY_WINDOW=0.05;\n  function preserveRealmToolsEnabled(){\n    return $('preserveRealmTools')?.checked!==false;\n  }\n  function acquisitionEffortWithinRealmPreserveWindow(candidate,best){\n    const cm=candidateResourceMetric(candidate),bm=candidateResourceMetric(best);\n    if(!Number.isFinite(cm)||!Number.isFinite(bm)) return false;\n    if(Math.abs(cm-bm)<=1e-9) return true;\n    const low=Math.min(cm,bm),high=Math.max(cm,bm);\n    if(low<=1e-9) return false;\n    return high<=low*(1+REALM_TOOL_PRESERVE_EFFICIENCY_WINDOW)+1e-9;\n  }\n"""
assert helper_old in text, 'compareAcquisitionEffort helper anchor missing'
text = text.replace(helper_old, helper_new, 1)

feasible_old = """    const effortFirst=compareAcquisitionEffort(candidate,best);\n    if(effortFirst!==null) return effortFirst;\n\n    // With acquisition effort tied, prefer the less expensive sourcing method so we do not\n    // burn saved tools or Dawnium for no progression-efficiency gain.\n"""
feasible_new = """    const effortFirst=compareAcquisitionEffort(candidate,best);\n    const preserveWindow=preserveRealmToolsEnabled()&&acquisitionEffortWithinRealmPreserveWindow(candidate,best);\n    if(effortFirst!==null&&!preserveWindow) return effortFirst;\n\n    // With preservation enabled, acquisition routes inside the 5% efficiency window are\n    // deliberately compared by sourcing burden first. This stops a 0.1-4.9% paper gain\n    // from consuming a pile of saved tools or Dawnium. If sourcing burden also ties, the\n    // lower acquisition effort still wins below.\n"""
assert feasible_old in text, 'main optimizer acquisition-first anchor missing'
text = text.replace(feasible_old, feasible_new, 1)

diagnostic_old = """    // Among equally fundable diagnostics, show the lowest acquisition burden first. Realm\n    // stage is only a tie-breaker after efficiency, matching the main plan comparator.\n    const diagnosticEffortFirst=compareAcquisitionEffort(candidate,best);\n    if(diagnosticEffortFirst!==null) return diagnosticEffortFirst;\n\n"""
diagnostic_new = """    // Diagnostics follow the same soft-preservation policy as the funded plan so the\n    // displayed near-miss route does not recommend needless Realm-tool consumption.\n    const diagnosticEffortFirst=compareAcquisitionEffort(candidate,best);\n    const diagnosticPreserveWindow=preserveRealmToolsEnabled()&&acquisitionEffortWithinRealmPreserveWindow(candidate,best);\n    if(diagnosticEffortFirst!==null&&!diagnosticPreserveWindow) return diagnosticEffortFirst;\n\n"""
assert diagnostic_old in text, 'diagnostic optimizer acquisition-first anchor missing'
text = text.replace(diagnostic_old, diagnostic_new, 1)

# Update user-facing optimizer explanation so it matches the actual policy.
text = text.replace(
    '<summary><span>How the optimizer decides</span><small>Raw first → saved Realm tools → extra Realm purchases</small></summary>',
    '<summary><span>How the optimizer decides</span><small>Best efficiency · preserve tools when close</small></summary>',
    1,
)
text = text.replace(
    '<p><b>2 · Find the best raw-only score route.</b> The planner searches Gear, Skills, Relics and Fantomons together for a combination that reaches the requested Primostar score. It prefers resources that are already sufficient to fund their reachable Season 1 cap, so surplus Sand, Essence or Treats can replace Ore instead of being stranded. It also avoids paying for meaningless overscore when otherwise-equivalent routes exist. If Treat Cart/hr is left at 0, non-surplus Treats are treated as scarce rather than inventing a replacement rate from your saved stock.</p>',
    '<p><b>2 · Find the most acquisition-efficient score route.</b> The planner searches Gear, Skills, Relics and Fantomons together for a combination that reaches the requested Primostar score, using the active season\'s real cost curves and resource yields. It avoids meaningless overscore and does not force a fixed Gear/Skill/Relic/Fantomon order.</p>',
    1,
)
text = text.replace(
    '<p><b>3 · Use saved Realm tools only if raw cannot reach the target.</b> Reserved tools stay protected. Unreserved Hammers, Knuckles and Shovels become available only after every feasible raw-only route has been considered.</p>',
    '<p><b>3 · Preserve Realm tools when the efficiency difference is small.</b> With <i>Preserve Realm tools if possible</i> enabled, routes within 5% acquisition efficiency prefer fewer saved tools, fewer paid runs and less Dawnium. If a tool-using route is more than 5% better, the optimizer uses it.</p>',
    1,
)
text = text.replace(
    '<p><b>4 · Buy more Realm refreshes only as the final fallback.</b> If the target still cannot be funded, the planner minimizes additional Realm purchases within the remaining daily capacity. If even the maximum remaining capacity is insufficient, it reports the actual material shortfall instead of lowering the target.</p>',
    '<p><b>4 · Paid refreshes compete on the same economics.</b> They can be recommended when they materially improve the route, but the preservation toggle keeps them from winning on trivial efficiency differences. If even maximum Realm capacity cannot fund the requested target, the planner reports the actual shortfall instead of lowering the target.</p>',
    1,
)
text = text.replace(
    'The optimizer uses one consistent acquisition-efficient, raw-first policy and always considers Gear alongside Skills, Relics and Fantomons.',
    'The optimizer uses one consistent acquisition-efficiency policy and always considers Gear alongside Skills, Relics and Fantomons.',
    1,
)

old_s2_opt = '<p><b>S2 target optimization:</b> once the Realm/tool stage is tied, target plans are ranked by marginal acquisition effort using the active season resource model. For S2 that means the verified Lv.120 Realm values (1,200 Ore / 1,500 Essence / 1,000 Sand per tool), max-bracket open-map yields, entered Cart production and Treat income, and the actual S2 upgrade-cost curves. The optimizer can therefore move between Gear, individual Skills, individual Relics and individual Fantomons as their marginal score efficiency changes. Raw inventory, existing Realm tools and paid refreshes are compared in one global efficiency ranking; sourcing method only breaks ties, so a paid refresh can be recommended when it materially lowers the total acquisition burden.</p>'
new_s2_opt = '<p><b>S2 target optimization:</b> target plans are ranked by marginal acquisition effort using the verified Lv.120 Realm values (1,200 Ore / 1,500 Essence / 1,000 Sand per tool), max-bracket open-map yields, entered Cart production and Treat income, and the actual S2 upgrade-cost curves. The optimizer can move between Gear, individual Skills, individual Relics and individual Fantomons as their marginal score efficiency changes. With <i>Preserve Realm tools if possible</i> enabled, any routes within 5% acquisition effort are treated as close enough that lower saved-tool / paid-refresh / Dawnium burden wins; a route more than 5% better still wins on efficiency. Turn the toggle off for strict pure-efficiency ranking.</p>'
assert old_s2_opt in text, 'S2 target optimization method note missing'
text = text.replace(old_s2_opt, new_s2_opt, 1)

# Remove stale wording that says the old reserve toggles are the user control.
text = text.replace(
    'With the separate S2 reserve toggles enabled, the planner can independently protect the startup Skill Essence reserve and/or exactly one full first S2 Relic round (+10→+11 across all 20 relics). Projected Shovels count toward that Sand reserve at the S2 Realm yield first; only the remaining raw Sand is protected. Surplus Essence/Treats/Sand can then be spent in S1 while Ore/Hammers are preserved for the much longer Gear progression runway.',
    'During the final S1 rollover window the startup reserves remain protected automatically; the four old manual reserve switches are no longer shown. The active planning control is the single soft Realm-tool preservation toggle, while Season 2 uses live inventory directly.',
    1,
)

text = text.replace(
    'Existing plus routine-purchased Hammers/Knuckles/Shovels are treated as a reserve and, among otherwise equal routes, the optimizer preserves the route with more tools left.',
    'With Realm-tool preservation enabled, existing plus routine-purchased Hammers/Knuckles/Shovels are preferred to remain banked whenever an alternative target route is within 5% acquisition efficiency.',
    1,
)

# Protected invariants.
required = [
    marker,
    'id="preserveRealmTools" checked type="checkbox"',
    'REALM_TOOL_PRESERVE_EFFICIENCY_WINDOW=0.05',
    "const CHECK_IDS = ['holdExp','preserveRealmTools'];",
    'reserveHours:34',
    'realmMaxLevel:120,realm:{ore:1200,essence:1500,sand:1000,rolla:11800}',
    'scoreFloor:130,relicFloor:13,starBase:45,scorePerStar:27,weights:{character:100,gear:18,skill:7,relic:33,fanto:8}',
    'S2_PRIMO_BENCHMARK_V2',
]
for needle in required:
    assert needle in text, f'missing protected marker/constant: {needle}'
for old_label in ['Reserve S2 Ore</label>','Reserve S2 Essence</label>','Reserve S2 Sand</label>','Reserve S2 Treats</label>']:
    assert old_label not in text, f'visible legacy reserve label remains: {old_label}'
assert text != original, 'patch made no changes'

path.write_text(text, encoding='utf-8')
print('Applied', marker)
