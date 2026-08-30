from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')
original = text

marker = 'GLOBAL_ACQUISITION_PRIORITY_V2'
if marker in text:
    print(f'{marker} already applied')
    raise SystemExit(0)

old_feasible = """  function betterFeasibleCandidate(candidate,best){
    if(!best) return true;

    // STRICT GATES: raw-only beats existing Realm-tool use; existing Realm-tool use beats
    // buying additional refreshes. Reserved/banked tools remain a distinct strategic stage.
    const cStage=candidateRealmStage(candidate),bStage=candidateRealmStage(best);
    if(cStage<bStage) return true;
    if(cStage>bStage) return false;
"""
new_feasible = """  function betterFeasibleCandidate(candidate,best){
    if(!best) return true;

    /* GLOBAL_ACQUISITION_PRIORITY_V2
       Rank every fundable route by acquisition efficiency before considering how it is
       sourced. Raw inventory, existing Realm tools and paid refreshes are therefore not
       hard tiers anymore. Realm/tool/Dawnium burden only breaks an acquisition-effort tie,
       so a paid-refresh route may win when it is genuinely the cheaper progression path. */
    const effortFirst=compareAcquisitionEffort(candidate,best);
    if(effortFirst!==null) return effortFirst;

    // With acquisition effort tied, prefer the less expensive sourcing method so we do not
    // burn saved tools or Dawnium for no progression-efficiency gain.
    const cStage=candidateRealmStage(candidate),bStage=candidateRealmStage(best);
    if(cStage<bStage) return true;
    if(cStage>bStage) return false;
"""
assert text.count(old_feasible) == 1, 'betterFeasibleCandidate strict-stage anchor missing or duplicated'
text = text.replace(old_feasible, new_feasible, 1)

old_diag = """    if(candidate.remainingAfterMax<best.remainingAfterMax-0.5) return true;
    if(Math.abs(candidate.remainingAfterMax-best.remainingAfterMax)>0.5) return false;

    const cStage=candidateRealmStage(candidate),bStage=candidateRealmStage(best);
"""
new_diag = """    if(candidate.remainingAfterMax<best.remainingAfterMax-0.5) return true;
    if(Math.abs(candidate.remainingAfterMax-best.remainingAfterMax)>0.5) return false;

    // Among equally fundable diagnostics, show the lowest acquisition burden first. Realm
    // stage is only a tie-breaker after efficiency, matching the main plan comparator.
    const diagnosticEffortFirst=compareAcquisitionEffort(candidate,best);
    if(diagnosticEffortFirst!==null) return diagnosticEffortFirst;

    const cStage=candidateRealmStage(candidate),bStage=candidateRealmStage(best);
"""
assert text.count(old_diag) == 1, 'betterDiagnosticCandidate stage anchor missing or duplicated'
text = text.replace(old_diag, new_diag, 1)

text = text.replace(
"""  /* S2_ACQUISITION_OPTIMIZER_V1
     Compare same-stage target plans by the time-equivalent burden of reacquiring the
     marginal resources they consume. This is season-agnostic: S2 uses its Lv.120
     Realm/open-map yields and its own scoring/cost curves instead of falling back to
     minimum overscore after the Realm-stage gates are satisfied. */
""",
"""  /* S2_ACQUISITION_OPTIMIZER_V1
     Compare target plans by the time-equivalent burden of reacquiring the marginal
     resources they consume. This is season-agnostic: S2 uses its Lv.120 Realm/open-map
     yields and its own scoring/cost curves. GLOBAL_ACQUISITION_PRIORITY_V2 makes this
     metric primary across raw, existing-tool and paid-refresh sourcing instead of only
     comparing plans after Realm-stage gates are satisfied. */
""",
1)

old_method = """The optimizer can therefore move between Gear, individual Skills, individual Relics and individual Fantomons as their marginal score efficiency changes, while still preferring raw-only routes over consuming saved tools and avoiding paid Realm refreshes when a cheaper same-stage route exists."""
new_method = """The optimizer can therefore move between Gear, individual Skills, individual Relics and individual Fantomons as their marginal score efficiency changes. Raw inventory, existing Realm tools and paid refreshes are compared in one global efficiency ranking; sourcing method only breaks ties, so a paid refresh can be recommended when it materially lowers the total acquisition burden."""
assert old_method in text, 'S2 optimizer method note anchor missing'
text = text.replace(old_method, new_method, 1)

# Protected verified constants and explicit starter behavior must not drift.
required = [
    'S2_ACQUISITION_OPTIMIZER_V1',
    'GLOBAL_ACQUISITION_PRIORITY_V2',
    "scoreFloor:130,relicFloor:13,starBase:45,scorePerStar:27,weights:{character:100,gear:18,skill:7,relic:33,fanto:8}",
    "realmMaxLevel:120,realm:{ore:1200,essence:1500,sand:1000,rolla:11800}",
    "map:{ore:1400,essence:1770,sand:1180,rolla:14000,bigRate:0.0932}",
    'S2_PRIMO_BENCHMARK_V2',
    'S2_SCORING_START_DEFAULTS',
    'relicLevel:13',
    'reserveHours:34',
]
for needle in required:
    assert needle in text, f'protected constant/marker missing: {needle}'

assert 'STRICT GATES: raw-only beats existing Realm-tool use' not in text
assert 'const effortFirst=compareAcquisitionEffort(candidate,best);' in text
assert 'const diagnosticEffortFirst=compareAcquisitionEffort(candidate,best);' in text
assert text.count('compareAcquisitionEffort(candidate,best)') >= 5
assert text != original, 'patch made no changes'

path.write_text(text, encoding='utf-8')
print('Applied', marker)
