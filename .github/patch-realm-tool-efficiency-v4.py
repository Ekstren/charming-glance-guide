from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')
original = text

marker = 'REALM_TOOL_EFFICIENCY_V4'
if marker in text:
    print(f'{marker} already applied')
    raise SystemExit(0)

# Rename the user-facing policy to the shorter intent-based label.
old_toggle = '''                <label class="realmToolPreserveOption"><input id="preserveRealmTools" checked type="checkbox"><span>Preserve Realm tools if possible</span><small>When two target routes are within 5% acquisition efficiency, prefer the one that uses fewer saved tools / paid refreshes. Turn this off for pure efficiency.</small></label>'''
new_toggle = '''                <label class="realmToolPreserveOption"><input id="preserveRealmTools" checked type="checkbox"><span>Minimize tools</span><small>Saved Realm tools need >10% acquisition improvement to justify spending; paid refreshes need >20%. Turn off for pure efficiency.</small></label>'''
assert old_toggle in text, 'v3 tool toggle anchor missing'
text = text.replace(old_toggle, new_toggle, 1)

# Replace the single 5% window with separate saved-tool and paid-refresh hurdles.
old_helper = '''  /* REALM_TOOL_PRESERVE_POLICY_V3
     A saved Realm tool is strategically scarce even when its material yield is known.
     With preservation enabled, routes within 5% acquisition effort are treated as close
     enough that lower tool/Dawnium burden wins. A route that is >5% more efficient still
     wins outright, so preservation cannot trap the planner in a materially worse path. */
  const REALM_TOOL_PRESERVE_EFFICIENCY_WINDOW=0.05;
  function preserveRealmToolsEnabled(){
    return $('preserveRealmTools')?.checked!==false;
  }
  function acquisitionEffortWithinRealmPreserveWindow(candidate,best){
    const cm=candidateResourceMetric(candidate),bm=candidateResourceMetric(best);
    if(!Number.isFinite(cm)||!Number.isFinite(bm)) return false;
    if(Math.abs(cm-bm)<=1e-9) return true;
    const low=Math.min(cm,bm),high=Math.max(cm,bm);
    if(low<=1e-9) return false;
    return high<=low*(1+REALM_TOOL_PRESERVE_EFFICIENCY_WINDOW)+1e-9;
  }
'''
new_helper = '''  /* REALM_TOOL_EFFICIENCY_V4
     "Minimize tools" is a soft economic hurdle, not a hard reserve. Spending already-banked
     Realm tools must improve modeled acquisition effort by more than 10%; introducing paid
     Realm refreshes must improve it by more than 20%. This intentionally uses percentage
     reduction from the slower route (e.g. 88h vs 100h = 12% better), which matches the
     user-facing meaning of "10% better". Disable the toggle for strict pure efficiency. */
  const REALM_SAVED_TOOL_EFFICIENCY_HURDLE=0.10;
  const REALM_PAID_REFRESH_EFFICIENCY_HURDLE=0.20;
  function preserveRealmToolsEnabled(){
    return $('preserveRealmTools')?.checked!==false;
  }
  function acquisitionImprovementFraction(faster,slower){
    const f=candidateResourceMetric(faster),s=candidateResourceMetric(slower);
    if(!Number.isFinite(f)||!Number.isFinite(s)||s<=1e-9||f>=s-1e-9) return 0;
    return Math.max(0,(s-f)/s);
  }
  function realmToolHurdleForMoreEfficientRoute(faster,slower){
    const f=candidateRealmToolBurden(faster),s=candidateRealmToolBurden(slower);
    // Any increase in paid runs carries the premium-currency hurdle.
    if(f.paidRuns>s.paidRuns) return REALM_PAID_REFRESH_EFFICIENCY_HURDLE;
    // Otherwise any increase in total/banked Realm-tool consumption carries the saved-tool hurdle.
    if(f.totalRuns>s.totalRuns || f.bankedUsed>s.bankedUsed) return REALM_SAVED_TOOL_EFFICIENCY_HURDLE;
    return 0;
  }
  function acquisitionEffortWinsAfterToolHurdle(candidate,best){
    const effortCmp=compareAcquisitionEffort(candidate,best);
    if(effortCmp===null) return null;
    if(!preserveRealmToolsEnabled()) return effortCmp;
    const faster=effortCmp?candidate:best;
    const slower=effortCmp?best:candidate;
    const hurdle=realmToolHurdleForMoreEfficientRoute(faster,slower);
    if(hurdle<=0) return effortCmp;
    const improvement=acquisitionImprovementFraction(faster,slower);
    if(improvement>hurdle+1e-9) return effortCmp;
    // The faster route did not clear the tool-spending hurdle. Prefer the lower sourcing burden.
    const toolCmp=betterToolBurden(candidate,best);
    if(toolCmp!==null) return toolCmp;
    const cStage=candidateRealmStage(candidate),bStage=candidateRealmStage(best);
    if(cStage<bStage) return true;
    if(cStage>bStage) return false;
    return effortCmp;
  }
'''
assert old_helper in text, 'v3 preservation helper block missing'
text = text.replace(old_helper, new_helper, 1)

old_main = '''    const effortFirst=compareAcquisitionEffort(candidate,best);
    const preserveWindow=preserveRealmToolsEnabled()&&acquisitionEffortWithinRealmPreserveWindow(candidate,best);
    if(effortFirst!==null&&!preserveWindow) return effortFirst;

    // With preservation enabled, acquisition routes inside the 5% efficiency window are
    // deliberately compared by sourcing burden first. This stops a 0.1-4.9% paper gain
    // from consuming a pile of saved tools or Dawnium. If sourcing burden also ties, the
    // lower acquisition effort still wins below.
'''
new_main = '''    const effortFirst=acquisitionEffortWinsAfterToolHurdle(candidate,best);
    if(effortFirst!==null) return effortFirst;

    // Exact acquisition ties fall through to sourcing burden and overscore tie-breakers.
'''
assert old_main in text, 'v3 main comparator block missing'
text = text.replace(old_main, new_main, 1)

old_diag = '''    // Diagnostics follow the same soft-preservation policy as the funded plan so the
    // displayed near-miss route does not recommend needless Realm-tool consumption.
    const diagnosticEffortFirst=compareAcquisitionEffort(candidate,best);
    const diagnosticPreserveWindow=preserveRealmToolsEnabled()&&acquisitionEffortWithinRealmPreserveWindow(candidate,best);
    if(diagnosticEffortFirst!==null&&!diagnosticPreserveWindow) return diagnosticEffortFirst;

'''
new_diag = '''    // Diagnostics follow the same saved-tool / paid-refresh hurdles as funded plans.
    const diagnosticEffortFirst=acquisitionEffortWinsAfterToolHurdle(candidate,best);
    if(diagnosticEffortFirst!==null) return diagnosticEffortFirst;

'''
assert old_diag in text, 'v3 diagnostic comparator block missing'
text = text.replace(old_diag, new_diag, 1)

# User-facing explainer and method notes.
text = text.replace(
    '<summary><span>How the optimizer decides</span><small>Best efficiency · preserve tools when close</small></summary>',
    '<summary><span>How the optimizer decides</span><small>Best efficiency · minimize tools</small></summary>',
    1,
)
text = text.replace(
    '<p><b>3 · Preserve Realm tools when the efficiency difference is small.</b> With <i>Preserve Realm tools if possible</i> enabled, routes within 5% acquisition efficiency prefer fewer saved tools, fewer paid runs and less Dawnium. If a tool-using route is more than 5% better, the optimizer uses it.</p>',
    '<p><b>3 · Minimize Realm tools unless they materially improve the route.</b> With <i>Minimize tools</i> enabled, spending saved Realm tools must improve acquisition effort by more than 10%. A route that requires additional paid Realm refreshes must improve it by more than 20%. Turn the toggle off for strict pure-efficiency ranking.</p>',
    1,
)
text = text.replace(
    '<p><b>4 · Paid refreshes compete on the same economics.</b> They can be recommended when they materially improve the route, but the preservation toggle keeps them from winning on trivial efficiency differences. If even maximum Realm capacity cannot fund the requested target, the planner reports the actual shortfall instead of lowering the target.</p>',
    '<p><b>4 · Paid refreshes face the higher hurdle.</b> Premium-currency Realm purchases only win when their route is more than 20% better on modeled acquisition effort. If even maximum Realm capacity cannot fund the requested target, the planner reports the actual shortfall instead of lowering the target.</p>',
    1,
)
old_s2_note = '<p><b>S2 target optimization:</b> target plans are ranked by marginal acquisition effort using the verified Lv.120 Realm values (1,200 Ore / 1,500 Essence / 1,000 Sand per tool), max-bracket open-map yields, entered Cart production and Treat income, and the actual S2 upgrade-cost curves. The optimizer can move between Gear, individual Skills, individual Relics and individual Fantomons as their marginal score efficiency changes. With <i>Preserve Realm tools if possible</i> enabled, any routes within 5% acquisition effort are treated as close enough that lower saved-tool / paid-refresh / Dawnium burden wins; a route more than 5% better still wins on efficiency. Turn the toggle off for strict pure-efficiency ranking.</p>'
new_s2_note = '<p><b>S2 target optimization:</b> target plans are ranked by marginal acquisition effort using the verified Lv.120 Realm values (1,200 Ore / 1,500 Essence / 1,000 Sand per tool), max-bracket open-map yields, entered Cart production and Treat income, and the actual S2 upgrade-cost curves. The optimizer can move between Gear, individual Skills, individual Relics and individual Fantomons as their marginal score efficiency changes. With <i>Minimize tools</i> enabled, saved Realm tools are spent only when their route is more than 10% better; routes requiring additional paid refreshes must be more than 20% better. Turn the toggle off for strict pure-efficiency ranking.</p>'
assert old_s2_note in text, 'v3 S2 optimization note missing'
text = text.replace(old_s2_note, new_s2_note, 1)
text = text.replace(
    'With Realm-tool preservation enabled, existing plus routine-purchased Hammers/Knuckles/Shovels are preferred to remain banked whenever an alternative target route is within 5% acquisition efficiency.',
    'With Minimize tools enabled, existing Hammers/Knuckles/Shovels stay banked unless consuming them improves modeled acquisition effort by more than 10%; additional paid refreshes require more than a 20% improvement.',
    1,
)

# Keep the input id stable for saved-state compatibility, but ensure all visible wording is new.
required = [
    marker,
    '<span>Minimize tools</span>',
    'REALM_SAVED_TOOL_EFFICIENCY_HURDLE=0.10',
    'REALM_PAID_REFRESH_EFFICIENCY_HURDLE=0.20',
    'function acquisitionImprovementFraction(faster,slower)',
    'function acquisitionEffortWinsAfterToolHurdle(candidate,best)',
    "const CHECK_IDS = ['holdExp','preserveRealmTools'];",
    'reserveHours:34',
    'realmMaxLevel:120,realm:{ore:1200,essence:1500,sand:1000,rolla:11800}',
    'scoreFloor:130,relicFloor:13,starBase:45,scorePerStar:27,weights:{character:100,gear:18,skill:7,relic:33,fanto:8}',
    'S2_PRIMO_BENCHMARK_V2',
]
for needle in required:
    assert needle in text, f'missing protected marker/constant: {needle}'
for stale in [
    'REALM_TOOL_PRESERVE_EFFICIENCY_WINDOW=0.05',
    'acquisitionEffortWithinRealmPreserveWindow',
    '<span>Preserve Realm tools if possible</span>',
    'routes within 5% acquisition effort',
]:
    assert stale not in text, f'stale v3 policy remains: {stale}'
assert text != original, 'patch made no changes'

path.write_text(text, encoding='utf-8')
print('Applied', marker)
