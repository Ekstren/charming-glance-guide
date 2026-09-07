from pathlib import Path
import re

p=Path('index.html')
s=p.read_text(encoding='utf-8')
MARK='TOTAL_POOL_SMART_BALANCE_V1'
if MARK in s:
    print('Total-pool Smart Balance v1 already applied.')
    raise SystemExit(0)

old_header="""  /* SCARCITY_ADJUSTED_ACQUISITION_V1 · TOOL_SCARCITY_CREDIT_V2 · POST_PLAN_SCARCITY_V4
     Acquisition difficulty and projected scarcity are ONE economic metric, not competing
     ranking rules. Saved + already-planned Realm tools count toward the pool at 80% of their
     material-equivalent value, preserving a 20% option-value premium. Extra purchases never
     count as surplus. The v4 balance pressure is based on how much of that usable pool a
     CANDIDATE PLAN would leave after spending: abundant pools are cheap to consume, while
     plans that drain a pool toward zero become progressively expensive instead of all
     collapsing to the same flat surplus floor. Strict source tiers remain
     raw -> saved/planned tools -> extra purchases. */
  const SURPLUS_ACQUISITION_FLOORS={ore:0.25,essence:0.25,sand:0.25,treat:0.00};
  const TOOL_SCARCITY_CREDIT=0.80;
  const POST_PLAN_SCARCITY_MAX=2.50;
  const POST_PLAN_SCARCITY_EXPONENT=2.20;
"""
new_header="""  /* SCARCITY_ADJUSTED_ACQUISITION_V1 · POST_PLAN_SCARCITY_V4 · TOTAL_POOL_SMART_BALANCE_V1
     Smart Balance now treats each owned/projected progression family as ONE economic pool:
       Ore = projected raw Ore + saved/already-planned Hammers at full material value;
       Essence = projected raw Essence + saved/already-planned Knuckles at full material value;
       Sand = projected raw Sand + saved/already-planned Shovels at full material value.
     This pool decides which category mix is healthiest. Actual funding still spends raw material
     first inside each family and consumes tools only for the remaining shortfall. Tool preservation
     is a tie-breaker, not a hard preference. Extra Realm purchases are NOT included in starting
     abundance and remain the last-resort sourcing tier. */
  const SURPLUS_ACQUISITION_FLOORS={ore:0.25,essence:0.25,sand:0.25,treat:0.00};
  const TOOL_SCARCITY_CREDIT=1.00;
  const POST_PLAN_SCARCITY_MAX=2.50;
  const POST_PLAN_SCARCITY_EXPONENT=2.20;
"""
if old_header not in s: raise SystemExit('scarcity header anchor not found')
s=s.replace(old_header,new_header,1)

old_supply="""  function plannedToolAcquisitionSupply(key,resources,cfg=activeCalcConfig()){
    if(key==='treat') return rawOnlyAcquisitionSupply(key,resources,cfg);
    const inv=realmInventoryFor(key,cfg);
    const perRun=Math.max(0,realmYieldFor(resources,key));
    const bankedMaterial=Math.max(0,Number(inv?.banked)||0)*perRun;
    return rawOnlyAcquisitionSupply(key,resources,cfg)+bankedMaterial*TOOL_SCARCITY_CREDIT;
  }
"""
new_supply="""  function plannedToolAcquisitionSupply(key,resources,cfg=activeCalcConfig()){
    if(key==='treat') return rawOnlyAcquisitionSupply(key,resources,cfg);
    const inv=realmInventoryFor(key,cfg);
    const perRun=Math.max(0,realmYieldFor(resources,key));
    const bankedMaterial=Math.max(0,Number(inv?.banked)||0)*perRun;
    // Saved + already-configured future tools are real owned/projected capacity, so they
    // enter scarcity at full material equivalent. Candidate-invented extra purchases are
    // intentionally absent from realmInventoryFor() and therefore cannot inflate this pool.
    return rawOnlyAcquisitionSupply(key,resources,cfg)+bankedMaterial*TOOL_SCARCITY_CREDIT;
  }
"""
if old_supply not in s: raise SystemExit('planned tool supply anchor not found')
s=s.replace(old_supply,new_supply,1)

pat=re.compile(r"  /\* POST_PLAN_SCARCITY_V4\n.*?\n  function marginalWeightedCosts\(costs,resources,cfg=activeCalcConfig\(\)\)\{",re.S)
m=pat.search(s)
if not m: raise SystemExit('post-plan scarcity block not found')
new_scarcity="""  /* POST_PLAN_SCARCITY_V4 · TOTAL_POOL_SMART_BALANCE_V1
     Rank plans by the reserve they leave in the TOTAL owned/projected resource family.
     Raw and saved/already-planned tools are economically interchangeable for scarcity, while
     realmTopupFor() still enforces the physical spend order: raw first, then banked/planned tools.
     Extra candidate purchases never add starting supply, so a paid route cannot make itself look
     abundant by counting tools it has not bought yet.

     Treats intentionally keep the prior headroom integral because they have no Realm-tool pool. */
  function marginalWeightedSpend(amount,key,resources){
    const amountTotal=Math.max(0,Number(amount)||0);
    if(amountTotal<=0) return 0;

    const floor=Math.max(0,Math.min(1,Number(SURPLUS_ACQUISITION_FLOORS[key])||0));
    const usefulNeed=Math.max(0,Number(resources?.acquisitionHeadroomCosts?.[key])||0);
    const available=Math.max(0,Number(resources?.acquisitionSupplyEquiv?.[key])||0);
    if(usefulNeed<=0) return amountTotal*floor;

    const productive=Math.min(amountTotal,usefulNeed);

    if(key==='treat'){
      let effective=0;
      if(available>=usefulNeed-1e-9){
        effective+=productive*floor;
      }else if(available<=1e-9){
        effective+=productive;
      }else{
        const covered=Math.min(productive,available);
        const deficit=Math.max(0,usefulNeed-available);
        const denomEnd=Math.max(1e-12,usefulNeed-covered);
        effective+=floor*covered+(1-floor)*deficit*Math.log(usefulNeed/denomEnd);
        if(productive>covered) effective+=productive-covered;
      }
      if(amountTotal>productive) effective+=amountTotal-productive;
      return effective;
    }

    // Scarcity sees the WHOLE existing/projected family. Whether a unit is physically raw
    // material or a saved/planned tool does not change its economic coverage. Spending order
    // is handled later by realmTopupFor(), which always drains projected raw first.
    const poolSpend=Math.min(productive,available);
    const spentFraction=available>1e-9
      ? Math.max(0,Math.min(1,poolSpend/available))
      : (productive>0?1:0);
    const multiplier=floor+(POST_PLAN_SCARCITY_MAX-floor)*Math.pow(spentFraction,POST_PLAN_SCARCITY_EXPONENT);
    let effective=productive*multiplier;

    // Material beyond the owned/projected pool is maximally scarce. Such a candidate is legal
    // only if the final fallback can buy extra Realm entries; those purchases never count as surplus.
    if(productive>available+1e-9){
      const over=productive-available;
      effective+=over*(POST_PLAN_SCARCITY_MAX-multiplier);
    }
    if(amountTotal>productive) effective+=(amountTotal-productive)*POST_PLAN_SCARCITY_MAX;
    return effective;
  }

  function marginalWeightedCosts(costs,resources,cfg=activeCalcConfig()){"
s=s[:m.start()]+new_scarcity+s[m.end():]

old_search_supply="""    // Scarcity RANKING can see saved + already-planned Realm tools at 80% material credit;
    // Realm FEASIBILITY remains strictly raw-first because realmTopupFor still compares each
    // candidate cost against the raw projected budget before consuming any tools. Extra tool
    // purchases are not included here, avoiding circular 'buy it because it is abundant' logic.
    resources.acquisitionHeadroomCosts=headroomCosts||{};
    resources.acquisitionSupplyEquiv={
      ore:plannedToolAcquisitionSupply('ore',resources,cfg),
      essence:plannedToolAcquisitionSupply('essence',resources,cfg),
      sand:plannedToolAcquisitionSupply('sand',resources,cfg),
      treat:rawOnlyAcquisitionSupply('treat',resources,cfg)
    };
"""
new_search_supply="""    // TOTAL_POOL_SMART_BALANCE_V1: scarcity/efficiency sees projected raw + saved/already-
    // planned tools at full material equivalent. realmTopupFor() separately preserves the
    // physical consumption order (raw first). Extra candidate purchases never enter this pool.
    resources.acquisitionHeadroomCosts=headroomCosts||{};
    resources.acquisitionSupplyEquiv={
      ore:plannedToolAcquisitionSupply('ore',resources,cfg),
      essence:plannedToolAcquisitionSupply('essence',resources,cfg),
      sand:plannedToolAcquisitionSupply('sand',resources,cfg),
      treat:rawOnlyAcquisitionSupply('treat',resources,cfg)
    };
"""
if old_search_supply not in s: raise SystemExit('search supply anchor not found')
s=s.replace(old_search_supply,new_search_supply,1)

old_kernel_comment="""    /* ACQUISITION_KERNEL_V2
       This metric is evaluated in the hottest optimizer loop. Precompute each category's
       scarcity-adjusted spend ONCE per resource snapshot (including 80%-credited saved/
       planned tools), read Cart/map rates once, and run the joint-reacquisition equation
       with scalar locals. Tool-backed candidates reuse this same exact kernel instead of
       rebuilding scarcity objects and rerunning logarithms in makePlanCandidate(). */
"""
new_kernel_comment="""    /* ACQUISITION_KERNEL_V2 · TOTAL_POOL_SMART_BALANCE_V1
       This metric is evaluated in the hottest optimizer loop. Precompute each category's
       scarcity-adjusted spend ONCE against the full owned/projected resource-family pool,
       read Cart/map rates once, and run the joint-reacquisition equation with scalar locals.
       Raw-funded and tool-backed candidates therefore use the same economic kernel. */
"""
if old_kernel_comment not in s: raise SystemExit('kernel comment anchor not found')
s=s.replace(old_kernel_comment,new_kernel_comment,1)

old_make_comment="""    /* ACQUISITION_KERNEL_V2
       Scarcity coverage is fixed for one resource snapshot, including the 80% credit for
       saved/planned tools. Feasibility/source stage is still decided separately by Realm
       top-up math. Therefore the hot search can reuse its precomputed acquisition result
       for raw AND tool-backed candidates instead of recalculating logarithms/DOM rates for
       every candidate combination. */
"""
new_make_comment="""    /* ACQUISITION_KERNEL_V2 · TOTAL_POOL_SMART_BALANCE_V1
       Scarcity coverage is fixed for one resource snapshot using projected raw + saved/planned
       tools at full material equivalent. Feasibility and the raw-before-tools consumption order
       are decided separately by Realm top-up math, so the hot search can reuse this kernel. */
"""
if old_make_comment not in s: raise SystemExit('make candidate comment anchor not found')
s=s.replace(old_make_comment,new_make_comment,1)

old_better="""  function betterFeasibleCandidate(candidate,best){
    if(!best) return true;

    /* SMART_BALANCE_RAW_FIRST_V1
       Strict sourcing priority for the default planner:
       0 = projected raw materials only;
       1 = saved + already-planned Realm tools;
       2 = extra Realm purchases beyond the selected daily plan.
       Never spend tools just because a tool-assisted route has a nicer acquisition metric. */
    const cStage=candidateRealmStage(candidate),bStage=candidateRealmStage(best);
    if(cStage<bStage) return true;
    if(cStage>bStage) return false;

    // Paid Realm purchases are the final fallback. Inside that stage, Dawnium cost wins.
    if(cStage===2){
      const cu=Math.max(0,Number(candidate.unknownPriceRefreshes)||0),bu=Math.max(0,Number(best.unknownPriceRefreshes)||0);
      if(cu<bu) return true;
      if(cu>bu) return false;
      if(candidate.dawniumCost<best.dawniumCost-1e-9) return true;
      if(candidate.dawniumCost>best.dawniumCost+1e-9) return false;
    }

    /* TOOL_MATERIAL_WEIGHTS_V1
       Once both candidates are in the SAME sourcing tier, value Realm-tool-backed
       progression with the SAME material acquisition weights used for raw Ore/Essence/Sand.
       This prevents an unweighted 'fewest tools' rule from exhausting scarce Hammers/Ore
       while abundant Knuckles/Essence are left idle. Source priority remains strict:
       raw-only still beats any tool route, and projected tools still beat extra purchases. */
    const effortCmp=compareAcquisitionEffort(candidate,best);
    if(effortCmp!==null) return effortCmp;

    // If the weighted material burden is genuinely tied, preserve the route that consumes
    // fewer actual Realm entries. Reserve-aware topups still enforce protected carry reserve.
    if(cStage>=1){
      const toolCmp=betterToolBurden(candidate,best);
      if(toolCmp!==null) return toolCmp;
    }

    // Do not spend material just for meaningless overscore once strategic cost is tied.
    return candidate.overshoot<best.overshoot-1e-9||
      (Math.abs(candidate.overshoot-best.overshoot)<1e-9&&candidate.maxShare<best.maxShare-1e-9)||
      (Math.abs(candidate.overshoot-best.overshoot)<1e-9&&Math.abs(candidate.maxShare-best.maxShare)<1e-9&&candidate.sumShare<best.sumShare-1e-9);
  }
"""
new_better="""  function betterFeasibleCandidate(candidate,best){
    if(!best) return true;

    /* TOTAL_POOL_SMART_BALANCE_V1
       Raw material and saved/already-planned Realm tools belong to the SAME owned/projected
       economic tier. Do not force a raw-only candidate to beat a healthier pooled candidate.
       The only hard sourcing boundary is EXTRA Realm purchases, which remain last resort. */
    const cStage=candidateRealmStage(candidate),bStage=candidateRealmStage(best);
    const cPaid=cStage>=2,bPaid=bStage>=2;
    if(cPaid!==bPaid) return !cPaid;

    // If extra purchases are unavoidable for both routes, minimize unknown-price refreshes
    // and verified Dawnium before choosing among their economic mixes.
    if(cPaid&&bPaid){
      const cu=Math.max(0,Number(candidate.unknownPriceRefreshes)||0),bu=Math.max(0,Number(best.unknownPriceRefreshes)||0);
      if(cu<bu) return true;
      if(cu>bu) return false;
      if(candidate.dawniumCost<best.dawniumCost-1e-9) return true;
      if(candidate.dawniumCost>best.dawniumCost+1e-9) return false;
    }

    // Primary choice inside the owned/projected tier: total-pool scarcity-adjusted acquisition.
    const effortCmp=compareAcquisitionEffort(candidate,best);
    if(effortCmp!==null) return effortCmp;

    // Tool preservation is deliberately ONLY a tie-breaker. realmTopupFor() has already spent
    // raw first, so this chooses fewer Hammers/Knuckles/Shovels only when economics are tied.
    const toolCmp=betterToolBurden(candidate,best);
    if(toolCmp!==null) return toolCmp;

    // Do not spend material just for meaningless overscore once strategic cost is tied.
    return candidate.overshoot<best.overshoot-1e-9||
      (Math.abs(candidate.overshoot-best.overshoot)<1e-9&&candidate.maxShare<best.maxShare-1e-9)||
      (Math.abs(candidate.overshoot-best.overshoot)<1e-9&&Math.abs(candidate.maxShare-best.maxShare)<1e-9&&candidate.sumShare<best.sumShare-1e-9);
  }
"""
if old_better not in s: raise SystemExit('better feasible candidate anchor not found')
s=s.replace(old_better,new_better,1)

old_diag="""    // Diagnostics follow the same acquisition-effort ranking as funded plans.
    const diagnosticEffortFirst=compareAcquisitionEffort(candidate,best);
    if(diagnosticEffortFirst!==null) return diagnosticEffortFirst;

    const cStage=candidateRealmStage(candidate),bStage=candidateRealmStage(best);
    if(cStage<bStage) return true;
    if(cStage>bStage) return false;
    if(cStage===2){
      const cu=Math.max(0,Number(candidate.unknownPriceRefreshes)||0),bu=Math.max(0,Number(best.unknownPriceRefreshes)||0);
      if(cu<bu) return true;
      if(cu>bu) return false;
      if(candidate.dawniumCost<best.dawniumCost-1e-9) return true;
      if(candidate.dawniumCost>best.dawniumCost+1e-9) return false;
    }
    if(cStage>=1){
      const toolCmp=betterToolBurden(candidate,best);
      if(toolCmp!==null) return toolCmp;
    }

    const effortCmp=compareAcquisitionEffort(candidate,best);
    if(effortCmp!==null) return effortCmp;
    return candidate.overshoot<best.overshoot;
"""
new_diag="""    // Diagnostics use the same owned/projected-pool vs extra-purchase boundary as funded plans.
    const cStage=candidateRealmStage(candidate),bStage=candidateRealmStage(best);
    const cPaid=cStage>=2,bPaid=bStage>=2;
    if(cPaid!==bPaid) return !cPaid;
    if(cPaid&&bPaid){
      const cu=Math.max(0,Number(candidate.unknownPriceRefreshes)||0),bu=Math.max(0,Number(best.unknownPriceRefreshes)||0);
      if(cu<bu) return true;
      if(cu>bu) return false;
      if(candidate.dawniumCost<best.dawniumCost-1e-9) return true;
      if(candidate.dawniumCost>best.dawniumCost+1e-9) return false;
    }
    const effortCmp=compareAcquisitionEffort(candidate,best);
    if(effortCmp!==null) return effortCmp;
    const toolCmp=betterToolBurden(candidate,best);
    if(toolCmp!==null) return toolCmp;
    return candidate.overshoot<best.overshoot;
"""
if old_diag not in s: raise SystemExit('diagnostic comparator anchor not found')
s=s.replace(old_diag,new_diag,1)

old_rawproof="""    /* RAW_IMPOSSIBILITY_FASTPATH_V3
       Prove whether ANY raw-only plan can reach the target before deciding whether a
       tool-backed exact fast-path result needs the expensive general scan. Resource pools
       are independent here, so the maximum raw-only score is simply the sum of the highest
       individually raw-affordable option in each category (respecting Refined Ore too).
       If that maximum is below desired, a stage-0 route is mathematically impossible. */
"""
new_rawproof="""    /* OWNED_POOL_IMPOSSIBILITY_FASTPATH_V4 · TOTAL_POOL_SMART_BALANCE_V1
       Prove whether ANY route using projected raw + saved/already-planned tools can reach the
       target before deciding whether a paid-refresh fast-path result needs the expensive scan.
       Extra candidate purchases are excluded from these budgets. */
"""
if old_rawproof not in s: raise SystemExit('raw proof comment anchor not found')
s=s.replace(old_rawproof,new_rawproof,1)

old_rawvars="""    const rawRefinedBudget=resources.refinedTracked?Math.max(0,Number(resources.refined)||0):Infinity;
    const rawMaxGear=highestAffordable(gearOptions,Math.max(0,Number(resources.ore)||0),'oreCost',rawRefinedBudget,'refinedCost');
    const rawMaxSkill=highestAffordable(cats.skillOptions,Math.max(0,Number(resources.essence)||0));
    const rawMaxRelic=highestAffordable(cats.relicOptions,Math.max(0,Number(resources.sand)||0));
    const rawMaxFanto=highestAffordable(cats.fantoOptions,Math.max(0,Number(resources.treat)||0));
    const rawOnlyMaxScore=charScore+(rawMaxGear?.score||0)+(rawMaxSkill?.score||0)+(rawMaxRelic?.score||0)+(rawMaxFanto?.score||0);
    const rawOnlyRoutePossible=rawOnlyMaxScore>=desired-1e-9;
"""
new_rawvars="""    const poolRefinedBudget=resources.refinedTracked?Math.max(0,Number(resources.refined)||0):Infinity;
    const poolMaxGear=highestAffordable(gearOptions,plannedToolAcquisitionSupply('ore',resources,cfg),'oreCost',poolRefinedBudget,'refinedCost');
    const poolMaxSkill=highestAffordable(cats.skillOptions,plannedToolAcquisitionSupply('essence',resources,cfg));
    const poolMaxRelic=highestAffordable(cats.relicOptions,plannedToolAcquisitionSupply('sand',resources,cfg));
    const poolMaxFanto=highestAffordable(cats.fantoOptions,Math.max(0,Number(resources.treat)||0));
    const ownedPoolMaxScore=charScore+(poolMaxGear?.score||0)+(poolMaxSkill?.score||0)+(poolMaxRelic?.score||0)+(poolMaxFanto?.score||0);
    const ownedPoolRoutePossible=ownedPoolMaxScore>=desired-1e-9;
"""
if old_rawvars not in s: raise SystemExit('raw proof variables anchor not found')
s=s.replace(old_rawvars,new_rawvars,1)

old_fast="""      if(fastBest && (candidateRealmStage(fastBest)===0 || !rawOnlyRoutePossible)) return {plan:fastBest,diagnostic:fastBest};
      // If raw-only maximum score can still reach the target, keep scanning because the
      // hard source hierarchy requires stage 0 to beat this tool-backed fast-path result.
"""
new_fast="""      if(fastBest && (candidateRealmStage(fastBest)<2 || !ownedPoolRoutePossible)) return {plan:fastBest,diagnostic:fastBest};
      // If the owned/projected pool can still reach the target without extra purchases, keep
      // scanning before accepting a paid-refresh route because extra purchases are last resort.
"""
if old_fast not in s: raise SystemExit('fast-path return anchor not found')
s=s.replace(old_fast,new_fast,1)
# Disabled legacy branch: if ever re-enabled, an existing/planned-tool route is now equally legal.
s=s.replace('if(fastBest && candidateRealmStage(fastBest)===0) return {plan:fastBest,diagnostic:fastBest};','if(fastBest && candidateRealmStage(fastBest)<2) return {plan:fastBest,diagnostic:fastBest};',1)

old_explain="""`Smart Balance stops the recommended spend once the ${fmt(targetStars)}-Primostar goal is funded. Projected raw materials could reach about ${fmt(projectedRawCeilingStars)} Primostars if you intentionally spend farther, but that upside is informational and does not consume extra raw materials or Realm tools in this goal plan.`"""
new_explain="""`Smart Balance stops the recommended spend once the ${fmt(targetStars)}-Primostar goal is funded. Projected raw materials alone could reach about ${fmt(projectedRawCeilingStars)} Primostars if you intentionally spend farther, but that upside is informational and does not raise the recommendation above your entered goal.`"""
if old_explain not in s: raise SystemExit('raw potential explanation anchor not found')
s=s.replace(old_explain,new_explain,1)

old_summary="""      if(planSourceStage===0) brief.push('goal funded with raw projected materials only');
      else if(planSourceStage===1) brief.push('saved/planned Realm tools used only as needed');
      else if(planSourceStage===2) brief.push('extra Realm purchases required');
"""
new_summary="""      if(planSourceStage===0) brief.push('goal plan happened to use raw only');
      else if(planSourceStage===1) brief.push('raw + saved/planned Realm tools optimized as one pool · raw consumed first');
      else if(planSourceStage===2) brief.push('extra Realm purchases required as final fallback');
"""
if old_summary not in s: raise SystemExit('optimizer summary anchor not found')
s=s.replace(old_summary,new_summary,1)

old_method="""<p><b>S2 target optimization / Smart Balance:</b> the entered Primostar target is the <b>recommended stopping point</b>, not an instruction to spend every projected resource. The planner finds the best balanced route to that goal using projected <b>raw materials first</b> (Saved + Cart + Shop + projected Stamina). If raw alone cannot reach the goal, it unlocks saved tools plus tools already included by the selected daily Realm purchase plan; only if raw + those projected tools still cannot reach the goal may it recommend additional Realm purchases. Separately, the result shows the higher <b>projected raw-only potential</b> when surplus raw income could reach more Primostars, but that ceiling is informational and does not raise the recommended spend. Within each sourcing tier, Gear, individual Skills, individual Relics and individual Fantomons are balanced by <b>post-plan scarcity-adjusted acquisition efficiency</b>: replacement difficulty is still the base cost, but the optimizer now prices each candidate by how much of the projected usable Ore/Hammer, Essence/Knuckle or Sand/Shovel pool it would consume. A plan that leaves a healthy reserve is cheaper; a plan that would scrape a pool toward zero becomes progressively more expensive. Saved + already-planned Realm tools contribute <b>80%</b> of their material-equivalent value to that pool, preserving a 20% option-value premium; extra recommended purchases never count as surplus. Raw feasibility still comes first, so tools remain untouched whenever a raw-only goal plan exists. Actual S2 upgrade-cost curves still determine every marginal step.</p>"""
new_method="""<p><b>S2 target optimization / Smart Balance:</b> the entered Primostar target is the <b>recommended stopping point</b>, not an instruction to spend every projected resource. For economic balancing, each progression family is treated as one owned/projected pool: <b>Ore + saved/already-planned Hammers</b>, <b>Essence + saved/already-planned Knuckles</b>, and <b>Sand + saved/already-planned Shovels</b>, with tools valued at their full material equivalent. Smart Balance chooses the Gear / Skill / Relic / Fantomon mix by <b>post-plan scarcity-adjusted acquisition efficiency</b>, so abundant pools are cheaper to consume and near-empty pools become expensive. This pool selection is separate from physical consumption: within a chosen family the calculator always spends projected <b>raw material first</b>, then uses saved/planned Realm tools only for the remainder. Tool preservation is a tie-breaker when two plans are economically equivalent, not a hard rule that can force a worse balance. <b>Extra Realm purchases are never counted as existing abundance and remain the final fallback</b>; they are recommended only when the target cannot be funded from the owned/projected pools. Separately, the result may show a higher <b>projected raw-only potential</b>; that ceiling is informational and never raises the entered goal. Actual S2 upgrade-cost curves determine every marginal step.</p>"""
if old_method not in s: raise SystemExit('Smart Balance method paragraph anchor not found')
s=s.replace(old_method,new_method,1)

old_realm_method="""<p><b>Material Realm buys:</b> Each Realm purchase grants <b>5 actual Realm entries/tools</b>, and the planner allows up to <b>20 purchases per Realm per server day</b> (100 tools). The verified Dawnium curve currently covers purchases 1–10: 60, 60, 100, 100, 150, 150, 200, 200, 250, 300. Purchases 11–20 count fully toward tool capacity, but their Dawnium prices remain unknown and are not fabricated. Existing Hammers/Knuckles/Shovels and additional Realm purchases are evaluated as normal sourcing options under the same acquisition-efficiency ranking. Your recurring daily purchase plan is added after future server resets; extra purchases consume the same daily capacity. Resource-card shortfalls are shown after your selected recurring plan, while the top warning shows the hard remainder after every remaining extra slot is exhausted. The requested Primostar target is never lowered.</p>"""
new_realm_method="""<p><b>Material Realm buys:</b> Each Realm purchase grants <b>5 actual Realm entries/tools</b>, and the planner allows up to <b>20 purchases per Realm per server day</b> (100 tools). The verified Dawnium curve currently covers purchases 1–10: 60, 60, 100, 100, 150, 150, 200, 200, 250, 300. Purchases 11–20 count fully toward tool capacity, but their Dawnium prices remain unknown and are not fabricated. Saved tools and tools already produced by your configured recurring Realm plan count as owned/projected material capacity for Smart Balance. <b>Additional purchases beyond that plan do not count toward abundance and are a separate final-fallback tier.</b> When they are unavoidable, the planner minimizes unknown-price refreshes and verified Dawnium before normal economic tie-breaks. Your recurring daily purchase plan is added after future server resets; extra purchases consume the same daily capacity. Resource-card shortfalls are shown after your selected recurring plan, while the top warning shows the hard remainder after every remaining extra slot is exhausted. The requested Primostar target is never lowered.</p>"""
if old_realm_method not in s: raise SystemExit('Realm method paragraph anchor not found')
s=s.replace(old_realm_method,new_realm_method,1)

old_auto="""After those reserves are protected, the planner first searches every fundable raw-only Gear / Skill / Relic / Fantomon route. Existing unreserved Realm tools unlock only if raw cannot reach the target, and additional paid Realm refreshes are the final fallback."""
new_auto="""After those reserves are protected, projected raw materials plus existing/already-planned Realm tools are valued together as material-equivalent progression pools; actual funding still consumes raw before tools. Additional paid Realm refreshes remain the final fallback and never count toward starting abundance."""
if old_auto not in s: raise SystemExit('auto-stamina method anchor not found')
s=s.replace(old_auto,new_auto,1)

old_ore_preserve="""Existing optimizer stage rules remain stricter, so the preference will not burn Realm tools or Realm purchases merely to save Ore; it only favors comparable non-Ore upgrade routes."""
new_ore_preserve="""The preference participates inside the same pooled acquisition economics; saved/planned tools may be used when that creates a healthier goal plan, while extra Realm purchases remain the strict final fallback."""
if old_ore_preserve not in s: raise SystemExit('Ore preservation method anchor not found')
s=s.replace(old_ore_preserve,new_ore_preserve,1)

p.write_text(s,encoding='utf-8')
print('Applied total-pool Smart Balance v1.')
