from pathlib import Path
import re

path = Path('index.html')
s = path.read_text(encoding='utf-8')

MARKER = 'OPTIMIZER_SYSTEM_AUDIT_V4'
if MARKER in s:
    print('optimizer audit already applied')
    raise SystemExit(0)

def replace_once(old, new, label):
    global s
    if old not in s:
        raise SystemExit(f'missing anchor: {label}')
    s = s.replace(old, new, 1)

def sub_once(pattern, repl, label, flags=re.S):
    global s
    ns, count = re.subn(pattern, lambda m: repl, s, count=1, flags=flags)
    if count != 1:
        raise SystemExit(f'expected one match for {label}, got {count}')
    s = ns

# ---------------------------------------------------------------------------
# UI: explicit on-demand ceiling finder, so maximizing rating does not require
# manually walking Target Primostars one point at a time.
# ---------------------------------------------------------------------------
style = r'''<style id="optimizer-system-audit-v4">
/* OPTIMIZER_SYSTEM_AUDIT_V4 */
.maxAchievableBar{border:1px solid var(--line);background:var(--bg);border-radius:10px;display:flex;align-items:center;gap:10px;margin-top:9px;padding:8px 10px}
.maxAchievableBar button{border:1px solid var(--today-border);background:var(--today-bg);color:var(--ink);border-radius:8px;cursor:pointer;flex:0 0 auto;padding:7px 10px;font-size:9px;font-weight:850}
.maxAchievableBar button:hover{border-color:var(--green);color:var(--green)}
.maxAchievableBar button:disabled{cursor:wait;opacity:.65}
.maxAchievableBar small{color:var(--muted);font-size:8px;line-height:1.4}
.maxAchievableBar small strong{color:var(--green)}
@media(max-width:700px){.maxAchievableBar{align-items:stretch;flex-direction:column}.maxAchievableBar button{width:100%}}
</style>
'''
replace_once('</head>', style + '</head>', 'head style insertion')

old_html = '''          <label class="freeSpeedToggle">Daily free speed-up<span class="freeSpeedCheck"><input id="freeSpeed" type="checkbox" checked> Use free 2-hour boost every reset</span></label>
        </div>
        <div class="projectionCallout projectionInline"><span>Projected season-end level</span><strong id="projectedCharacter">—</strong><small id="projectionNote" hidden></small></div>'''
new_html = '''          <label class="freeSpeedToggle">Daily free speed-up<span class="freeSpeedCheck"><input id="freeSpeed" type="checkbox" checked> Use free 2-hour boost every reset</span></label>
        </div>
        <div class="maxAchievableBar"><button id="findMaxStars" type="button">Find max achievable</button><small id="maxAchievableStatus">Shows the maximum with your selected daily Realm plan and the hard maximum using all remaining Realm capacity.</small></div>
        <div class="projectionCallout projectionInline"><span>Projected season-end level</span><strong id="projectedCharacter">—</strong><small id="projectionNote" hidden></small></div>'''
replace_once(old_html, new_html, 'max achievable UI')

# ---------------------------------------------------------------------------
# Explanations: make every visible description match the actual tools-first
# reserve gates and the intentionally single-target Auto Stamina behavior.
# ---------------------------------------------------------------------------
replace_once(
    '<p><b>Auto Stamina</b> tests Ore, Essence and Sand gathering against the selected upgrade route and uses the split that reduces required paid Realm farming. <b>Gear Lock</b> removes new Gear levels from consideration. The optimizer otherwise uses one consistent acquisition-efficient, raw-first policy so the same inputs always produce the same resource strategy.</p>',
    '<p><b>Auto Stamina</b> compares three simple all-in choices—every projected node to Ore, every node to Essence, or every node to Sand—and picks the destination that best reduces Realm farming for the selected score route. It never asks you to track a fiddly multi-resource split. <b>Gear Lock</b> removes new Gear levels from consideration. The optimizer otherwise uses one consistent acquisition-efficient, raw-first policy so the same inputs always produce the same resource strategy.</p>',
    'optimizer explanation stamina'
)

sub_once(
    r'<p><b>S2 Skill reserve / Automatic Stamina:</b>.*?</p>',
    '<p><b>S2 Skill reserve / Automatic Stamina:</b> During S1, an enabled rollover reserve is protected before S1 Realm tools become spendable. For Essence and Sand, carried/projected Knuckles or Shovels cover the reserve first; raw material is held only for any reserve amount those tools cannot cover. Treats have no Realm-tool conversion, so an enabled Treat reserve stays raw. After those reserves are protected, the planner first searches every fundable raw-only Gear / Skill / Relic / Fantomon route. Existing unreserved Realm tools unlock only if raw cannot reach the target, and additional paid Realm refreshes are the final fallback. In Auto mode, the planner compares exactly three easy-to-follow Stamina destinations—all Ore, all Essence or all Sand—for each candidate route, then re-solves until the selected destination stabilizes. Once the requested current-season target is funded, otherwise-unused verified nodes default to Raw Ore because Gear has the broadest practical progression runway. S2 Lv.120+ uses the current community table: 1,400 Ore, 1,770 Essence, 1,180 Sand or 14,000 Rolla per 5-Stamina node. Late-S1 uses 900 Ore/node; Essence/Sand are automatic estimates (~1,475 Essence / ~838 Sand per 5-Stamina node) derived from the verified S1 Ore-to-Realm scaling until direct late-S1 values are independently confirmed.</p>',
    'method stamina/reserve paragraph'
)

replace_once(
    'Public references currently publish the Dawnium curve only for purchases 1–10 (60, 60, 100, 100, 150, 150, 200, 200, 250, 300), so purchases 11–20 count toward real capacity and feasibility but their Dawnium price is intentionally not fabricated.',
    'Public references currently publish the Dawnium curve only for purchases 1–10 (60, 60, 100, 100, 150, 150, 200, 200, 250, 300), so purchases 11–20 count toward real capacity and feasibility but their Dawnium price is intentionally not fabricated. The optimizer ranks routes using fewer unknown-price 11–20 purchases ahead of routes using more, then compares only the Dawnium cost that is actually known.',
    'unknown realm pricing explanation'
)

# ---------------------------------------------------------------------------
# Remove the deleted Preserve-Ore model from the hot path. The visible mode was
# already removed; calculating a second +50% solution for every candidate was
# now pure wasted CPU.
# ---------------------------------------------------------------------------
replace_once(
    '''  /* GATED_RAW_FIRST_OPTIMIZER_V1: once a capped category's remaining S1 headroom is fully funded by SAFE RAW, spending that raw on its own score progression has zero additional S1 opportunity cost. */
  const SURPLUS_ACQUISITION_FLOORS={ore:1.00,essence:0.00,sand:0.00,treat:0.00};
  const ORE_PRESERVE_PREMIUM=0.50;''',
    '''  /* GATED_RAW_FIRST_OPTIMIZER_V2: once a capped category's remaining S1 headroom is fully funded by SAFE RAW, spending that raw on its own score progression has zero additional S1 opportunity cost. */
  const SURPLUS_ACQUISITION_FLOORS={ore:1.00,essence:0.00,sand:0.00,treat:0.00};''',
    'preserve ore constants'
)

# Dead helper left over from the pre-gated model.
sub_once(
    r'  function reserveAdjustedAcquisitionSupply\(key,resources,cfg=activeCalcConfig\(\)\)\{.*?\n  \}\n\n  function dynamicAcquisitionWeights',
    '  function dynamicAcquisitionWeights',
    'dead reserveAdjustedAcquisitionSupply'
)

sub_once(
    r'  function marginalWeightedCosts\(costs,resources,preserveOre=false\)\{.*?\n  \}',
    '''  function marginalWeightedCosts(costs,resources){
    return {
      ore:Math.max(0,Number(costs?.ore)||0),
      essence:marginalWeightedSpend(costs?.essence,'essence',resources),
      sand:marginalWeightedSpend(costs?.sand,'sand',resources),
      treat:marginalWeightedSpend(costs?.treat,'treat',resources)
    };
  }''',
    'marginal weighted costs'
)

# Treat stock is not an income rate. If Treat/hr is unknown, genuinely scarce
# Treats remain expensive; fully funded surplus still becomes zero-cost through
# marginalWeightedSpend before this solver sees it.
replace_once(
    '''    const horizon=Math.max(24,Number(resources?.cartHours)||24);
    const projectedTreat=Math.max(0,Number(resources?.treat)||0);
    const enteredTreatRate=Math.max(0,n('treatRate'));
    const fallbackTreatRate=projectedTreat>0?projectedTreat/horizon:0;
    const cart={
      ore:Math.max(0,n('oreRate')),
      essence:Math.max(0,n('essenceRate')),
      sand:Math.max(0,n('sandRate')),
      treat:enteredTreatRate>0?enteredTreatRate:fallbackTreatRate
    };''',
    '''    const enteredTreatRate=Math.max(0,n('treatRate'));
    const cart={
      ore:Math.max(0,n('oreRate')),
      essence:Math.max(0,n('essenceRate')),
      sand:Math.max(0,n('sandRate')),
      treat:enteredTreatRate
    };''',
    'treat reacquisition fallback'
)

sub_once(
    r'  function acquisitionEffortFor\(costs,resources,cfg=activeCalcConfig\(\)\)\{.*?\n  \}\n  function candidateResourceMetric\(candidate\)\{.*?\n  \}\n  function makePlanCandidate\(go,so,ro,fo,score,desired,resources,realms\)\{',
    '''  function acquisitionEffortFor(costs,resources,cfg=activeCalcConfig()){
    const weights=dynamicAcquisitionWeights(resources); // diagnostic snapshot at zero spend
    const marginalCosts=marginalWeightedCosts(costs,resources);
    const hours=jointReacquisitionHours(marginalCosts,resources,cfg,UNIT_ACQUISITION_WEIGHTS);
    const map=resources?.yields?.map||cfg.map||{};
    const single=(effective,key)=>{
      const target=Math.max(0,Number(effective)||0);
      if(target<=0) return 0;
      const rate=Math.max(0,n(key==='ore'?'oreRate':key==='essence'?'essenceRate':'sandRate'))+Math.max(0,Number(map[key])||0);
      return rate>0?target/rate:1e9;
    };
    return {
      hours,weights,marginalCosts,
      oreHours:single(marginalCosts.ore,'ore'),
      essenceHours:single(marginalCosts.essence,'essence'),
      sandHours:single(marginalCosts.sand,'sand'),
      treatHours:0
    };
  }
  function candidateResourceMetric(candidate){
    const base=Number(candidate?.acquisitionHours);
    return Number.isFinite(base)?base:1e18;
  }
  function makePlanCandidate(go,so,ro,fo,score,desired,resources,realms,acquisitionResult=null){''',
    'acquisition hot path'
)

replace_once(
    '''    const acquisition=acquisitionEffortFor({ore:go.oreCost,essence:so.cost,sand:ro.cost,treat:fo.cost},resources,activeCalcConfig());
    const preserveAcquisitionScore=acquisition.preserveHours;
    return {''',
    '''    const acquisition=acquisitionResult||acquisitionEffortFor({ore:go.oreCost,essence:so.cost,sand:ro.cost,treat:fo.cost},resources,activeCalcConfig());
    const unknownPriceRefreshes=realms.reduce((sum,x)=>sum+Math.max(0,Number(x?.unknownPriceRefreshes)||0),0);
    return {''',
    'make candidate acquisition reuse'
)
replace_once(
    '      acquisitionHours:acquisition.hours,oreAcquisitionHours:acquisition.oreHours,preserveAcquisitionScore,',
    '      acquisitionHours:acquisition.hours,oreAcquisitionHours:acquisition.oreHours,unknownPriceRefreshes,',
    'candidate preserve score field'
)

# ---------------------------------------------------------------------------
# Realm purchase pricing: do not invent a pseudo-Dawnium price for 11–20. Known
# tiers always sort first; unknown tiers are tracked as a separate lexicographic
# burden. This keeps feasibility accurate without pretending a price exists.
# ---------------------------------------------------------------------------
sub_once(
    r'  const MATERIAL_REALM_BUY_COSTS = \[60,60,100,100,150,150,200,200,250,300\];.*?\n  function materialRealmDaysAvailable',
    '''  const MATERIAL_REALM_BUY_COSTS = [60,60,100,100,150,150,200,200,250,300];
  const MAX_REALM_REFRESHES_PER_DAY=20;
  const REALM_RUNS_PER_REFRESH=5;
  const REALM_CHOICE_CACHE=new Map();
  function realmPurchaseChoices(days,baselinePerDay){
    const d=Math.max(0,Math.floor(days||0)),baseline=clamp(Math.floor(baselinePerDay||0),0,MAX_REALM_REFRESHES_PER_DAY);
    const key=`${d}|${baseline}`;
    if(REALM_CHOICE_CACHE.has(key)) return REALM_CHOICE_CACHE.get(key);
    const choices=[];
    for(let day=1;day<d;day++){
      for(let idx=baseline;idx<MAX_REALM_REFRESHES_PER_DAY;idx++){
        const known=idx<MATERIAL_REALM_BUY_COSTS.length;
        const knownCost=known?MATERIAL_REALM_BUY_COSTS[idx]:0;
        choices.push({knownCost,known,day,idx});
      }
    }
    // Never compare an invented price. Exhaust known-price opportunities first, then
    // minimize how deep into the unknown 11–20 band a route must go.
    choices.sort((a,b)=>{
      if(a.known!==b.known) return a.known?-1:1;
      if(a.known && a.knownCost!==b.knownCost) return a.knownCost-b.knownCost;
      if(!a.known && a.idx!==b.idx) return a.idx-b.idx;
      return a.day-b.day||a.idx-b.idx;
    });
    const knownPrefix=[0],unknownPrefix=[0];
    for(const x of choices){
      knownPrefix.push(knownPrefix[knownPrefix.length-1]+x.knownCost);
      unknownPrefix.push(unknownPrefix[unknownPrefix.length-1]+(x.known?0:1));
    }
    // prefix is retained for realmTopup compatibility, but now means VERIFIED Dawnium only.
    const out={choices,prefix:knownPrefix,knownPrefix,unknownPrefix}; REALM_CHOICE_CACHE.set(key,out); return out;
  }

  function materialRealmDaysAvailable''',
    'realm purchase ranking'
)

# The successful top-up result had already computed these values but did not expose
# them, which made the existing "unverified pricing" UI unable to count them.
replace_once(
    'return {feasible:true,shortfall,runsNeeded,runsUsed,bankedUsed,bankedRemaining,packs,attempts:packs,purchasedRuns,paidRunsUsed,sparePurchasedRuns,dawnium,days:d,',
    'return {feasible:true,shortfall,runsNeeded,runsUsed,bankedUsed,bankedRemaining,packs,attempts:packs,purchasedRuns,paidRunsUsed,sparePurchasedRuns,dawnium,knownDawnium,unknownPriceRefreshes,days:d,',
    'realm topup unknown-price return'
)

# ---------------------------------------------------------------------------
# Auto Stamina: the UI intentionally recommends one destination. The old code
# still precomputed Realm results for every node count as if it were scanning all
# 3-way splits. Evaluate only the three states the player can actually be told to
# follow, and use reserve-aware top-ups in that comparison.
# ---------------------------------------------------------------------------
sub_once(
    r'  // For a FIXED upgrade plan, solve the complete Ore / Essence / Sand split instead of.*?\n  function staminaAllocationSignature',
    '''  // AUTO_STAMINA_THREE_WAY_V2: Auto intentionally recommends ONE destination.
  // Evaluate exactly the three actionable states (all Ore / all Essence / all Sand),
  // including S2 reserve-aware tool usage, instead of building O(nodes) tables that are
  // never consulted by the single-target UI.
  function allocateStaminaForPlan(plan,base,cfg=activeCalcConfig(),p=null){
    const total=Math.max(0,Math.floor(base.staminaNodes||0));
    const empty={ore:0,essence:0,sand:0,rolla:0,unassigned:0};
    if(total<=0) return empty;
    const map=base.yields?.map||{};
    if(!base.yields?.mapReady) return {...empty,unassigned:total};

    const mode=staminaMode();
    if(mode!=='auto'){
      const allocation={...empty};
      if((Number(map[mode])||0)>0) allocation[mode]=total;
      else allocation.unassigned=total;
      return allocation;
    }

    if(!plan){
      if((Number(map.ore)||0)>0) return {...empty,ore:total};
      return {...empty,unassigned:total};
    }

    const keys=['ore','essence','sand'];
    const costs={ore:staminaPlanCost(plan,'ore'),essence:staminaPlanCost(plan,'essence'),sand:staminaPlanCost(plan,'sand')};
    const yields={ore:Number(map.ore)||0,essence:Number(map.essence)||0,sand:Number(map.sand)||0};
    const finiteOr=(v,fallback)=>Number.isFinite(Number(v))?Number(v):fallback;

    const topupFor=(key,nodes)=>{
      const budget=(Number(base[key])||0)+Math.max(0,nodes)*yields[key];
      const sim={...base,[key]:budget};
      return key==='ore'
        ? realmTopupFor(key,costs[key],budget,sim,cfg,p)
        : reserveAwareRealmTopupFor(key,costs[key],budget,sim,cfg,p);
    };

    const metricFor=targetKey=>{
      const allocation={...empty,[targetKey]:total};
      const tops=keys.map(key=>topupFor(key,key===targetKey?total:0));
      const feasible=tops.every(x=>!!x?.feasible);
      const remainingAfterMax=tops.reduce((sum,x)=>sum+Math.max(0,finiteOr(x?.remainingAfterMax,1e15)),0);
      const realmOverflow=tops.reduce((sum,x)=>sum+Math.max(0,finiteOr(x?.packs,1e9)-finiteOr(x?.maxPacks,0)),0);
      const unknownPriceRefreshes=tops.reduce((sum,x)=>sum+Math.max(0,finiteOr(x?.unknownPriceRefreshes,0)),0);
      const dawnium=feasible?tops.reduce((sum,x)=>sum+finiteOr(x?.dawnium,1e15),0):Infinity;
      const realmPacks=tops.reduce((sum,x)=>sum+finiteOr(x?.packs,1e9),0);
      const bankedToolsUsed=tops.reduce((sum,x)=>sum+Math.max(0,finiteOr(x?.bankedUsed,0)),0);
      const rawShortfall=tops.reduce((sum,x)=>sum+Math.max(0,finiteOr(x?.planShortfall,x?.shortfall||0)),0);
      return {allocation,feasible,remainingAfterMax,realmOverflow,unknownPriceRefreshes,dawnium,realmPacks,bankedToolsUsed,rawShortfall};
    };

    const better=(c,b)=>{
      if(!b) return true;
      if(c.feasible!==b.feasible) return c.feasible;
      if(c.feasible){
        if(c.unknownPriceRefreshes<b.unknownPriceRefreshes) return true;
        if(c.unknownPriceRefreshes>b.unknownPriceRefreshes) return false;
        if(c.dawnium<b.dawnium-1e-9) return true;
        if(c.dawnium>b.dawnium+1e-9) return false;
        if(c.realmPacks<b.realmPacks) return true;
        if(c.realmPacks>b.realmPacks) return false;
      }else{
        if(c.remainingAfterMax<b.remainingAfterMax-0.5) return true;
        if(c.remainingAfterMax>b.remainingAfterMax+0.5) return false;
        if(c.realmOverflow<b.realmOverflow) return true;
        if(c.realmOverflow>b.realmOverflow) return false;
        if(c.rawShortfall<b.rawShortfall-0.5) return true;
        if(c.rawShortfall>b.rawShortfall+0.5) return false;
      }
      if(c.bankedToolsUsed<b.bankedToolsUsed) return true;
      if(c.bankedToolsUsed>b.bankedToolsUsed) return false;
      // Stable tie-break: bank surplus Stamina as Ore, then Essence, then Sand.
      if(c.allocation.ore>b.allocation.ore) return true;
      if(c.allocation.ore<b.allocation.ore) return false;
      if(c.allocation.essence>b.allocation.essence) return true;
      return false;
    };

    let best=null;
    for(const key of keys){
      if((Number(map[key])||0)<=0) continue;
      const candidate=metricFor(key);
      if(better(candidate,best)) best=candidate;
    }
    return best?.allocation||{...empty,ore:(Number(map.ore)||0)>0?total:0,unassigned:(Number(map.ore)||0)>0?0:total};
  }

  function staminaAllocationSignature''',
    'auto stamina single-target optimization'
)

replace_once(
    '''    // Auto mode alternates between two exact subproblems:
    //   1) global score-plan search for the current resource mix;
    //   2) complete Stamina split search for that fixed plan.
    // Iterate until the split stabilizes (or a short cycle is detected) instead of stopping after one retarget pass.''',
    '''    // Auto mode alternates between two exact subproblems:
    //   1) global score-plan search for the current resource mix;
    //   2) three-way single-destination Stamina comparison for that fixed plan.
    // Iterate until the destination stabilizes (or a short cycle is detected) instead of stopping after one retarget pass.''',
    'auto stamina solve comment'
)

# ---------------------------------------------------------------------------
# Candidate comparison: unknown-price purchases are a real separate burden, and
# acquisition effort is computed once per unique cost tuple and reused by both
# diagnostic and feasible candidate objects.
# ---------------------------------------------------------------------------
replace_once(
    '''    if(cStage===2){
      if(candidate.dawniumCost<best.dawniumCost-1e-9) return true;
      if(candidate.dawniumCost>best.dawniumCost+1e-9) return false;
    }''',
    '''    if(cStage===2){
      const cu=Math.max(0,Number(candidate.unknownPriceRefreshes)||0),bu=Math.max(0,Number(best.unknownPriceRefreshes)||0);
      if(cu<bu) return true;
      if(cu>bu) return false;
      if(candidate.dawniumCost<best.dawniumCost-1e-9) return true;
      if(candidate.dawniumCost>best.dawniumCost+1e-9) return false;
    }''',
    'feasible unknown realm comparator'
)
# same block occurs once more in diagnostics after the first replacement
replace_once(
    '''    if(cStage===2){
      if(candidate.dawniumCost<best.dawniumCost-1e-9) return true;
      if(candidate.dawniumCost>best.dawniumCost+1e-9) return false;
    }''',
    '''    if(cStage===2){
      const cu=Math.max(0,Number(candidate.unknownPriceRefreshes)||0),bu=Math.max(0,Number(best.unknownPriceRefreshes)||0);
      if(cu<bu) return true;
      if(cu>bu) return false;
      if(candidate.dawniumCost<best.dawniumCost-1e-9) return true;
      if(candidate.dawniumCost>best.dawniumCost+1e-9) return false;
    }''',
    'diagnostic unknown realm comparator'
)

# Delete remaining unreachable preserve-mode tie-breaks.
s = re.sub(r"\n      if\(optimizerMode\(\)==='preserve'\)\{\n        if\(\(candidate\.oreCost\|\|0\)<\(best\.oreCost\|\|0\)\) return true;\n        if\(\(candidate\.oreCost\|\|0\)>\(best\.oreCost\|\|0\)\) return false;(?:\n        if\(\(candidate\.bankedHammersUsed\|\|0\)<\(best\.bankedHammersUsed\|\|0\)\) return true;\n        if\(\(candidate\.bankedHammersUsed\|\|0\)>\(best\.bankedHammersUsed\|\|0\)\) return false;)?\n      \}", '', s)
s = s.replace('    // Raw-stage economics: fully funded capped raw (Skills / Relics / Fantomons) is allowed\n    // to replace open-ended Gear/Ore. Preserve Ore applies the existing +50% Ore premium.\n', '    // Raw-stage economics: fully funded capped raw (Skills / Relics / Fantomons) is allowed\n    // to replace open-ended Gear/Ore when that lowers reacquisition effort.\n')

replace_once(
    '    const oreCache=new Map(),essCache=new Map(),sandCache=new Map();',
    '''    const oreCache=new Map(),essCache=new Map(),sandCache=new Map(),acquisitionCache=new Map();''',
    'search caches'
)
replace_once(
    '''    const sandFor=ro=>{const k=ro.cost;if(!sandCache.has(k))sandCache.set(k,reserveAwareRealmTopupFor('sand',k,resources.sand,resources,cfg,p));return sandCache.get(k);};
    let best=null,bestDiagnostic=null;''',
    '''    const sandFor=ro=>{const k=ro.cost;if(!sandCache.has(k))sandCache.set(k,reserveAwareRealmTopupFor('sand',k,resources.sand,resources,cfg,p));return sandCache.get(k);};
    const acquisitionFor=(go,so,ro,fo)=>{
      const k=`${go.oreCost}|${so.cost}|${ro.cost}|${fo.cost}`;
      if(!acquisitionCache.has(k)) acquisitionCache.set(k,acquisitionEffortFor({ore:go.oreCost,essence:so.cost,sand:ro.cost,treat:fo.cost},resources,cfg));
      return acquisitionCache.get(k);
    };
    let best=null,bestDiagnostic=null;''',
    'acquisition cache helper'
)
replace_once(
    '          const diagAcquisition=acquisitionEffortFor({ore:go.oreCost,essence:so.cost,sand:ro.cost,treat:fo.cost},resources,cfg);',
    '''          const diagAcquisition=acquisitionFor(go,so,ro,fo);
          const unknownPriceRefreshes=realms.reduce((sum,x)=>sum+Math.max(0,Number(x?.unknownPriceRefreshes)||0),0);''',
    'diagnostic acquisition reuse'
)
replace_once(
    'preserveAcquisitionScore:diagAcquisition.preserveHours,bankedHammersUsed:',
    'unknownPriceRefreshes,bankedHammersUsed:',
    'diagnostic preserve field'
)
replace_once(
    '          const candidate=makePlanCandidate(go,so,ro,fo,score,desired,resources,[oreRealm,essenceRealm,sandRealm]);',
    '          const candidate=makePlanCandidate(go,so,ro,fo,score,desired,resources,[oreRealm,essenceRealm,sandRealm],diagAcquisition);',
    'candidate acquisition pass-through'
)

# Policy summary no longer references a deleted mode.
sub_once(
    r"  function optimizerReserveSummary\(resources,cfg\)\{.*?\n  \}",
    '''  function optimizerReserveSummary(resources,cfg){
    if(cfg.key!=='s1') return '';
    const reserveKinds=[];
    if((resources?.s2SkillReserve?.target||0)>0) reserveKinds.push('Skill');
    if((resources?.s2RelicSandReserve?.target||0)>0) reserveKinds.push('Relic');
    if((resources?.s2FantomonTreatReserve?.target||0)>0) reserveKinds.push('Fantomon');
    return reserveKinds.length
      ? `Spend surplus first · minimize reacquisition effort · S2 ${reserveKinds.join(' + ')} reserve${reserveKinds.length>1?'s':''} protected`
      : 'Spend surplus first · minimize reacquisition effort · no S2 resource reserve';
  }''',
    'optimizer reserve summary'
)

# ---------------------------------------------------------------------------
# On-demand max finder. It caches solver calls inside one click and reports both
# the ceiling under the selected recurring Realm plan and the hard ceiling if all
# remaining extra Realm capacity is used. The second click can copy the hard max
# directly into Target Primostars.
# ---------------------------------------------------------------------------
max_code = r'''
  let maxAchievableState={fingerprint:'',routine:null,hard:null};
  function maxAchievableFingerprint(){
    return JSON.stringify({
      inputs:INPUT_IDS.filter(id=>id!=='targetStars').map(id=>$(id)?.value??''),
      checks:CHECK_IDS.map(id=>!!$(id)?.checked),
      gearLocked,snapshotSeason
    });
  }
  function resetMaxAchievableUi(){
    maxAchievableState={fingerprint:'',routine:null,hard:null};
    const btn=$('findMaxStars'),status=$('maxAchievableStatus');
    if(btn){btn.disabled=false;btn.textContent='Find max achievable';}
    if(status) status.textContent='Shows the maximum with your selected daily Realm plan and the hard maximum using all remaining Realm capacity.';
  }
  function buildMaxAchievableSnapshot(){
    const cfg=activeCalcConfig();
    if(snapshotSeason!==cfg.key) return null;
    const p=projectCharacter(cfg);
    const upgradeP=projectCharacterTo(upgradeFinishCutoffMs(cfg),cfg);
    p.upgradeCapLevel=upgradeP.level;p.upgradeCapPct=upgradeP.pct;
    const currentCharacter=p.current||characterSnapshot(cfg);
    const projectedResourceTotals=projectedResources(p.hours,cfg);
    const baseResources=applySeasonTransitionReserves(projectedResourceTotals,cfg);
    const currentCaps=categoryInputCapsForCharacter(currentCharacter.level,cfg);
    const gear=GEAR_IDS.map(id=>Math.max(100,Math.floor(n(id,143))));
    const skillState=categoryStateFromUser('skillLevel','exactSkillLevels',8,100,currentCaps.skill,cfg.scoreFloor,cfg.weights.skill,cfg.key==='s2'?100:122);
    const relicState=categoryStateFromUser('relicLevel','exactRelicLevels',20,10,currentCaps.relic,cfg.relicFloor,cfg.weights.relic,cfg.key==='s2'?10:13);
    const fantoState=categoryStateFromUser('fantomonLevel','exactFantoLevels',4,100,currentCaps.fanto,cfg.scoreFloor,cfg.weights.fanto,cfg.key==='s2'?100:130);
    const baselineScore=characterScore(p,cfg)+gearScore(gear,cfg)+skillState.score+relicState.score+fantoState.score;
    const historical=Math.max(0,Math.floor(n('historicalStars',0)));
    return {cfg,p,baseResources,baselineScore,historical,baselineStars:historical+cfg.starBase+Math.floor(baselineScore/cfg.scorePerStar)};
  }
  function findMaxAchievableStars(){
    const btn=$('findMaxStars'),status=$('maxAchievableStatus');
    if(!btn||!status) return;
    const fingerprint=maxAchievableFingerprint();
    if(maxAchievableState.fingerprint===fingerprint && Number.isFinite(maxAchievableState.hard)){
      $('targetStars').value=String(maxAchievableState.hard);
      markManualSnapshot('targetStars');
      scheduleCalculatorUpdate(0);
      return;
    }
    const snap=buildMaxAchievableSnapshot();
    if(!snap){ status.textContent='Confirm the current-season snapshot first.'; return; }
    btn.disabled=true;btn.textContent='Calculating…';status.textContent='Searching reachable Primostar breakpoints…';
    setTimeout(()=>{
      try{
        const solveCache=new Map();
        const solveStars=stars=>{
          const key=Math.max(snap.baselineStars,Math.floor(stars));
          if(solveCache.has(key)) return solveCache.get(key);
          const desired=Math.max(0,(key-snap.historical-snap.cfg.starBase)*snap.cfg.scorePerStar);
          const result=solveTargetWithAutoStamina(snap.baselineScore,desired,snap.p,snap.baseResources,snap.cfg);
          solveCache.set(key,result);
          return result;
        };
        const hardFundable=stars=>!!solveStars(stars).plan;
        const routineFundable=stars=>{
          const plan=solveStars(stars).plan;
          return !!plan && candidateRealmStage(plan)<=1;
        };
        const upperLimit=snap.cfg.key==='s1'?1200:5000;
        let hardLo=snap.baselineStars,hardHi=Math.max(hardLo+1,Math.floor(n('targetStars',hardLo))+1),step=Math.max(8,hardHi-hardLo);
        while(hardHi<upperLimit && hardFundable(hardHi)){
          hardLo=hardHi;step*=2;hardHi=Math.min(upperLimit,hardHi+step);
        }
        if(hardHi===upperLimit && hardFundable(hardHi)) hardLo=hardHi;
        else{
          let lo=hardLo+1,hi=hardHi-1;
          while(lo<=hi){const mid=(lo+hi)>>1;if(hardFundable(mid)){hardLo=mid;lo=mid+1;}else hi=mid-1;}
        }
        const hard=hardLo;
        let routineLo=snap.baselineStars,routineHi=hard;
        while(routineLo<routineHi){
          const mid=Math.ceil((routineLo+routineHi)/2);
          if(routineFundable(mid)) routineLo=mid; else routineHi=mid-1;
        }
        const routine=routineLo;
        const hardPlan=solveStars(hard).plan;
        const unknown=Math.max(0,Number(hardPlan?.unknownPriceRefreshes)||0);
        maxAchievableState={fingerprint,routine,hard};
        status.innerHTML=`Selected daily plan max: <strong>${fmt(routine)}</strong> · Hard Realm-cap max: <strong>${fmt(hard)}</strong>${unknown?` · ${fmt(unknown)} unpriced tier 11–20 purchase${unknown===1?'':'s'} at hard max`:''}`;
        btn.disabled=false;btn.textContent=`Use ${fmt(hard)} target`;
      }catch(err){
        console.error(err);resetMaxAchievableUi();status.textContent='Could not calculate the ceiling from the current inputs.';
      }
    },0);
  }
'''
replace_once('  let lastRequestedTargetStars=null;', max_code + '\n  let lastRequestedTargetStars=null;', 'max achievable functions')

replace_once(
    "    $('gearLockButton').addEventListener('click',()=>{gearLocked=!gearLocked;markManualSnapshot('gearLocked');updateGearLockUI();scheduleCalculatorUpdate(0);});",
    "    $('gearLockButton').addEventListener('click',()=>{gearLocked=!gearLocked;resetMaxAchievableUi();markManualSnapshot('gearLocked');updateGearLockUI();scheduleCalculatorUpdate(0);});",
    'gear lock max invalidation'
)
replace_once(
    "    $('confirmSeasonSnapshot')?.addEventListener('click',confirmCurrentSeasonSnapshot);",
    "    $('confirmSeasonSnapshot')?.addEventListener('click',()=>{resetMaxAchievableUi();confirmCurrentSeasonSnapshot();});\n    $('findMaxStars')?.addEventListener('click',findMaxAchievableStars);",
    'max button handler'
)
# Any non-target input changes the ceiling; targetStars itself does not.
replace_once(
    "        el.addEventListener('change',()=>{markManualSnapshot(id);scheduleCalculatorUpdate(0);});\n        return;",
    "        el.addEventListener('change',()=>{resetMaxAchievableUi();markManualSnapshot(id);scheduleCalculatorUpdate(0);});\n        return;",
    'stamina mode max invalidation'
)
replace_once(
    "      el.addEventListener('change',()=>{markManualSnapshot(id);scheduleCalculatorUpdate(0);});",
    "      el.addEventListener('change',()=>{if(id!=='targetStars')resetMaxAchievableUi();markManualSnapshot(id);scheduleCalculatorUpdate(0);});",
    'input max invalidation'
)
replace_once(
    "    CHECK_IDS.forEach(id=>$(id)?.addEventListener('change',()=>{\n      markManualSnapshot(id);",
    "    CHECK_IDS.forEach(id=>$(id)?.addEventListener('change',()=>{\n      resetMaxAchievableUi();\n      markManualSnapshot(id);",
    'checkbox max invalidation'
)

# Reset button should clear a computed ceiling too.
replace_once(
    "    $('resetCalc').addEventListener('click',resetCalculator);",
    "    $('resetCalc').addEventListener('click',()=>{resetMaxAchievableUi();resetCalculator();});",
    'reset max invalidation'
)

# Tidy comments that referenced the deleted mode.
s = s.replace('Ore remains the 1.00 baseline because Gear has the broadest runway. Preserve Ore applies\n     a bounded +50% Ore premium on top of the same joint model.', 'Ore remains the 1.00 baseline because Gear has the broadest runway.')
s = s.replace('// Equal paid-Realm outcome: avoid consuming banked tools. Preserve-Ore mode gives Hammers\n      // the first tool tie-break; both modes still bank otherwise-unused projected nodes as Ore.', '// Equal paid-Realm outcome: avoid consuming banked tools; otherwise-unused projected nodes bank as Ore.')
s = s.replace("      if(optimizerMode()==='preserve'){\n        if(c.bankedHammersUsed<b.bankedHammersUsed) return true;\n        if(c.bankedHammersUsed>b.bankedHammersUsed) return false;\n      }\n", '')

path.write_text(s, encoding='utf-8')
print('applied OPTIMIZER_SYSTEM_AUDIT_V4')
