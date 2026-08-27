from pathlib import Path
import re

p=Path('index.html')
s=p.read_text(encoding='utf-8')
MARK='OPTIMIZER_CLEANUP_V5'
if MARK in s:
    print('optimizer cleanup already applied')
    raise SystemExit(0)

def one(old,new,label):
    global s
    if old not in s:
        raise SystemExit(f'missing anchor: {label}')
    s=s.replace(old,new,1)

def sub(pattern,repl,label):
    global s
    ns,n=re.subn(pattern,lambda m:repl,s,count=1,flags=re.S)
    if n!=1:
        raise SystemExit(f'expected one match for {label}, got {n}')
    s=ns

# Remove the final compatibility shim from the deleted strategy selector.
one("""  /* REMOVE_RESOURCE_STRATEGY_V1: one optimizer policy only — raw-first, acquisition-efficient. */
  const optimizerMode = () => 'acquisition';
  function updateOptimizerModeUI(){}
""","""  /* OPTIMIZER_CLEANUP_V5: one optimizer policy only — raw-first, acquisition-efficient. */
""",'optimizer mode shim')
one("""  function updateCalculator(){
    updateOptimizerModeUI();
""","""  function updateCalculator(){
""",'optimizer UI no-op call')

# marginalWeightedSpend already performs the useful dynamic headroom integration.
# The old snapshot-weight helper and unit multiplier layer became redundant after
# Preserve Ore was removed, so stop recomputing them for every candidate.
sub(r"  function dynamicAcquisitionWeights\(resources\)\{.*?\n  \}\n\n  /\* MARGINAL_HEADROOM_COST_V2", "  /* MARGINAL_HEADROOM_COST_V2", 'dead dynamic weights helper')
one("""  const UNIT_ACQUISITION_WEIGHTS={ore:1,essence:1,sand:1,treat:1};

""","",'unit weights constant')
one("""  function jointReacquisitionHours(costs,resources,cfg=activeCalcConfig(),weights=null){
    weights=weights||dynamicAcquisitionWeights(resources);
""","""  function jointReacquisitionHours(costs,resources,cfg=activeCalcConfig()){
""",'joint solver weights')
one("""    const demand={
      ore:Math.max(0,Number(costs?.ore)||0)*Math.max(0,Number(weights?.ore)||0),
      essence:Math.max(0,Number(costs?.essence)||0)*Math.max(0,Number(weights?.essence)||0),
      sand:Math.max(0,Number(costs?.sand)||0)*Math.max(0,Number(weights?.sand)||0),
      treat:Math.max(0,Number(costs?.treat)||0)*Math.max(0,Number(weights?.treat)||0)
    };
""","""    const demand={
      ore:Math.max(0,Number(costs?.ore)||0),
      essence:Math.max(0,Number(costs?.essence)||0),
      sand:Math.max(0,Number(costs?.sand)||0),
      treat:Math.max(0,Number(costs?.treat)||0)
    };
""",'joint solver demand')

# Only the joint hours metric is used by plan selection. Remove unused diagnostic
# sub-metrics and their extra map/rate arithmetic from every acquisition cache miss.
sub(r"  function acquisitionEffortFor\(costs,resources,cfg=activeCalcConfig\(\)\)\{.*?\n  \}\n  function candidateResourceMetric", """  function acquisitionEffortFor(costs,resources,cfg=activeCalcConfig()){
    const marginalCosts=marginalWeightedCosts(costs,resources);
    return {hours:jointReacquisitionHours(marginalCosts,resources,cfg)};
  }
  function candidateResourceMetric""", 'acquisition metric simplification')
s=s.replace(',oreAcquisitionHours:acquisition.oreHours','')
s=s.replace(',oreAcquisitionHours:diagAcquisition.oreHours','')

# Auto Stamina needs only two top-up states per resource: no Stamina there or all
# Stamina there. Cache those six states once instead of recomputing 3x3 = 9 calls.
one("""    const metricFor=targetKey=>{
      const allocation={...empty,[targetKey]:total};
      const tops=keys.map(key=>topupFor(key,key===targetKey?total:0));
""","""    const topupStates=Object.fromEntries(keys.map(key=>[key,{base:topupFor(key,0),full:topupFor(key,total)}]));
    const metricFor=targetKey=>{
      const allocation={...empty,[targetKey]:total};
      const tops=keys.map(key=>topupStates[key][key===targetKey?'full':'base']);
""",'auto stamina six-state cache')

# Make the zero Treat/hr behavior explicit rather than silently surprising users.
one("""<p><b>2 · Find the best raw-only score route.</b> The planner searches Gear, Skills, Relics and Fantomons together for a combination that reaches the requested Primostar score. It prefers resources that are already sufficient to fund their reachable Season 1 cap, so surplus Sand, Essence or Treats can replace Ore instead of being stranded. It also avoids paying for meaningless overscore when otherwise-equivalent routes exist.</p>""","""<p><b>2 · Find the best raw-only score route.</b> The planner searches Gear, Skills, Relics and Fantomons together for a combination that reaches the requested Primostar score. It prefers resources that are already sufficient to fund their reachable Season 1 cap, so surplus Sand, Essence or Treats can replace Ore instead of being stranded. It also avoids paying for meaningless overscore when otherwise-equivalent routes exist. If Treat Cart/hr is left at 0, non-surplus Treats are treated as scarce rather than inventing a replacement rate from your saved stock.</p>""",'treat rate explanation')

p.write_text(s,encoding='utf-8')
print('applied OPTIMIZER_CLEANUP_V5')
