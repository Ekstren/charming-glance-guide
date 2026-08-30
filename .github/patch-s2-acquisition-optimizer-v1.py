from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')
original = text

marker = 'S2_ACQUISITION_OPTIMIZER_V1'
if marker in text:
    print(f'{marker} already applied')
    raise SystemExit(0)

metric_old = """  function candidateResourceMetric(candidate){
    const base=Number(candidate?.acquisitionHours);
    return Number.isFinite(base)?base:1e18;
  }
"""
metric_new = """  function candidateResourceMetric(candidate){
    const base=Number(candidate?.acquisitionHours);
    return Number.isFinite(base)?base:1e18;
  }
  /* S2_ACQUISITION_OPTIMIZER_V1
     Compare same-stage target plans by the time-equivalent burden of reacquiring the
     marginal resources they consume. This is season-agnostic: S2 uses its Lv.120
     Realm/open-map yields and its own scoring/cost curves instead of falling back to
     minimum overscore after the Realm-stage gates are satisfied. */
  function compareAcquisitionEffort(candidate,best){
    const cm=candidateResourceMetric(candidate),bm=candidateResourceMetric(best);
    if(cm<bm-1e-9) return true;
    if(cm>bm+1e-9) return false;
    return null;
  }
"""
assert metric_old in text, 'candidateResourceMetric anchor missing'
text = text.replace(metric_old, metric_new, 1)

s1_only = """    if(candidate.seasonKey==='s1' || best.seasonKey==='s1'){
      const cm=candidateResourceMetric(candidate),bm=candidateResourceMetric(best);
      if(cm<bm-1e-9) return true;
      if(cm>bm+1e-9) return false;
    }
"""
count = text.count(s1_only)
assert count == 2, f'expected 2 S1-only acquisition gates, found {count}'
text = text.replace(s1_only, """    const effortCmp=compareAcquisitionEffort(candidate,best);
    if(effortCmp!==null) return effortCmp;
""")

text = text.replace(
"""    // STRICT GATES: raw-only beats existing Realm-tool use; existing Realm-tool use beats
    // buying additional refreshes. Reserved banked tools are not counted as S1 tool usage.
""",
"""    // STRICT GATES: raw-only beats existing Realm-tool use; existing Realm-tool use beats
    // buying additional refreshes. Reserved/banked tools remain a distinct strategic stage.
""",
1)
text = text.replace(
"""    // Within a tool-using stage, consume the fewest actual S1 Realm entries before comparing
    // raw economics. This never unlocks a reserved tool: reserveAwareRealmTopupFor already
    // allocates those entries to S2 before exposing any S1 plan runs.
""",
"""    // Within a tool-using stage, consume the fewest actual Realm entries before comparing
    // acquisition economics. Reserve-aware topups still enforce any protected carry reserve.
""",
1)

assert 'usesS1Tools' in text, 'usesS1Tools anchor missing'
text = text.replace('usesS1Tools', 'usesRealmTools')

text = text.replace(
"""    // Raw-stage economics: fully funded capped raw (Skills / Relics / Fantomons) is allowed
    // to replace open-ended Gear/Ore when that lowers reacquisition effort.
""",
"""    // Same-stage economics: compare the marginal time-equivalent burden of the resources
    // consumed by each score-capable route. This now applies to both S1 and S2.
""",
1)

# Generalize the surplus/headroom comment if the historical wording is still present.
text = text.replace('remaining S1 headroom', 'remaining productive category headroom')

method_anchor = '<p><b>Time projection:</b>'
assert method_anchor in text, 'method-panel Time projection anchor missing'
method_note = (
    '<p><b>S2 target optimization:</b> once the Realm/tool stage is tied, target plans are ranked by marginal acquisition effort using the active season resource model. '
    'For S2 that means the verified Lv.120 Realm values (1,200 Ore / 1,500 Essence / 1,000 Sand per tool), max-bracket open-map yields, entered Cart production and Treat income, and the actual S2 upgrade-cost curves. '
    'The optimizer can therefore move between Gear, individual Skills, individual Relics and individual Fantomons as their marginal score efficiency changes, while still preferring raw-only routes over consuming saved tools and avoiding paid Realm refreshes when a cheaper same-stage route exists.</p>\n'
)
text = text.replace(method_anchor, method_note + method_anchor, 1)

# Hard guards: this refactor must not drift any verified S2 constants or explicit starter rules.
required = [
    "scoreFloor:130,relicFloor:13,starBase:45,scorePerStar:27,weights:{character:100,gear:18,skill:7,relic:33,fanto:8}",
    "realmMaxLevel:120,realm:{ore:1200,essence:1500,sand:1000,rolla:11800}",
    "map:{ore:1400,essence:1770,sand:1180,rolla:14000,bigRate:0.0932}",
    'S2_PRIMO_BENCHMARK_V2',
    'S2_SCORING_START_DEFAULTS',
    'relicLevel:13',
]
for needle in required:
    assert needle in text, f'protected S2 constant/marker missing: {needle}'

assert "candidate.seasonKey==='s1' || best.seasonKey==='s1'" not in text, 'S1-only acquisition comparator remains'
assert text.count('compareAcquisitionEffort(candidate,best)') >= 3, 'comparison helper not used in both plan comparators'
assert 'usesS1Tools' not in text
assert 'usesRealmTools' in text
assert marker in text
assert text != original, 'patch made no changes'

path.write_text(text, encoding='utf-8')
print('Applied', marker)
