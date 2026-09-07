from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')
changed = False


def replace_once(old: str, new: str, label: str):
    global s, changed
    if new in s:
        return
    if old not in s:
        raise SystemExit(f'{label}: expected anchor not found')
    s = s.replace(old, new, 1)
    changed = True

# 1) Sourcing priority is strict: raw -> saved/planned tools -> extra purchases.
old = """    /* GLOBAL_ACQUISITION_PRIORITY_V2
       Rank every fundable route by acquisition efficiency before considering how it is
       sourced. Raw inventory, existing Realm tools and paid refreshes are therefore not
       hard tiers anymore. Realm/tool/Dawnium burden only breaks an acquisition-effort tie,
       so a paid-refresh route may win when it is genuinely the cheaper progression path. */
    const effortFirst=compareAcquisitionEffort(candidate,best);
    if(effortFirst!==null) return effortFirst;

    // Exact acquisition ties fall through to sourcing burden and overscore tie-breakers.
    const cStage=candidateRealmStage(candidate),bStage=candidateRealmStage(best);
    if(cStage<bStage) return true;
    if(cStage>bStage) return false;
"""
new = """    /* SMART_BALANCE_RAW_FIRST_V1
       Strict sourcing priority for the default planner:
       0 = projected raw materials only;
       1 = saved + already-planned Realm tools;
       2 = extra Realm purchases beyond the selected daily plan.
       Never spend tools just because a tool-assisted route has a nicer acquisition metric. */
    const cStage=candidateRealmStage(candidate),bStage=candidateRealmStage(best);
    if(cStage<bStage) return true;
    if(cStage>bStage) return false;
"""
replace_once(old, new, 'strict sourcing comparator')

# 2) Fast paths may only early-return a raw-only winner. Otherwise the full scan must be
# allowed to find a stage-0 route before any stage-1/2 route can win.
replace_once(
    "        if(fastBest) return {plan:fastBest,diagnostic:fastBest};\n",
    "        if(fastBest && candidateRealmStage(fastBest)===0) return {plan:fastBest,diagnostic:fastBest};\n",
    'non-ore funded fast path'
)
replace_once(
    "      if(fastBest) return {plan:fastBest,diagnostic:fastBest};\n      if(fastDiagnostic) return {plan:null,diagnostic:fastDiagnostic};\n",
    "      if(fastBest && candidateRealmStage(fastBest)===0) return {plan:fastBest,diagnostic:fastBest};\n      // Under strict raw-first sourcing, a tool-using fast-path result cannot short-circuit\n      // the general scan because a raw-only route may still exist elsewhere in the search space.\n",
    'treat funded fast path'
)

# 3) Add a cheap exact raw-only ceiling. Resources do not cross between Gear/Skill/Relic/Fanto,
# so the maximum raw-only score is simply the highest affordable option in each category,
# evaluated across the legal Stamina destinations. The normal optimizer then solves the
# cheapest combination for that whole-Primostar ceiling.
helper = r'''  /* SMART_BALANCE_RAW_CEILING_V1
     The requested Primostar value is a minimum goal. If projected RAW income alone can
     reach a higher whole-Primostar breakpoint, recommend that higher breakpoint without
     touching Realm tools. Tools are only unlocked when raw cannot reach the requested goal. */
  function smartBalanceHighestAffordable(options,budget,costKey='cost',secondaryBudget=Infinity,secondaryKey=''){
    let best=Array.isArray(options)&&options.length?options[0]:null;
    for(const option of (options||[])){
      const primary=Math.max(0,Number(option?.[costKey])||0);
      const secondary=secondaryKey?Math.max(0,Number(option?.[secondaryKey])||0):0;
      if(primary<=budget+0.5 && secondary<=secondaryBudget+0.5) best=option;
      else if(primary>budget+0.5) break;
    }
    return best;
  }
  function smartBalanceRawCeiling(baseScore,p,baseResources,cfg,historical){
    // Large structural target only expands Gear options; actual affordability below is
    // still limited strictly by projected raw resources and verified progression gates.
    const ctx=createPlanningContext(baseScore,1_000_000,p,cfg);
    const total=Math.max(0,Math.floor(baseResources?.staminaNodes||0));
    const empty={ore:0,essence:0,sand:0,rolla:0,unassigned:0};
    const map=baseResources?.yields?.map||{};
    const allocations=[];
    if(total<=0 || !baseResources?.yields?.mapReady){
      allocations.push({...empty,unassigned:total});
    }else if(staminaMode()==='auto'){
      for(const key of ['ore','essence','sand']) if((Number(map[key])||0)>0) allocations.push({...empty,[key]:total});
      if(!allocations.length) allocations.push({...empty,unassigned:total});
    }else{
      allocations.push(allocateStaminaForPlan(null,baseResources,cfg,p));
    }

    let best=null;
    for(const allocation of allocations){
      const resources=applyStaminaAllocation(baseResources,allocation,cfg);
      const refinedBudget=resources.refinedTracked?Math.max(0,Number(resources.refined)||0):Infinity;
      const go=smartBalanceHighestAffordable(ctx.gearOptions,Math.max(0,Number(resources.ore)||0),'oreCost',refinedBudget,'refinedCost');
      const so=smartBalanceHighestAffordable(ctx.cats.skillOptions,Math.max(0,Number(resources.essence)||0));
      const ro=smartBalanceHighestAffordable(ctx.cats.relicOptions,Math.max(0,Number(resources.sand)||0));
      const fo=smartBalanceHighestAffordable(ctx.cats.fantoOptions,Math.max(0,Number(resources.treat)||0));
      if(!go||!so||!ro||!fo) continue;
      const score=ctx.charScore+go.score+so.score+ro.score+fo.score;
      const stars=Math.max(0,Math.floor(historical))+cfg.starBase+Math.floor(score/cfg.scorePerStar);
      const candidate={stars,score,allocation,resources};
      if(!best || candidate.stars>best.stars || (candidate.stars===best.stars && candidate.score>best.score)) best=candidate;
    }
    return best||{stars:Math.max(0,Math.floor(historical))+cfg.starBase+Math.floor(baseScore/cfg.scorePerStar),score:baseScore,allocation:{...empty,unassigned:total},resources:baseResources};
  }

'''
anchor = "  let lastRequestedTargetStars=null;\n"
if 'SMART_BALANCE_RAW_CEILING_V1' not in s:
    if anchor not in s:
        raise SystemExit('smart balance helper insertion anchor missing')
    s = s.replace(anchor, helper + anchor, 1)
    changed = True

# 4) Requested target becomes a minimum. If raw-only projected income reaches higher,
# solve that higher whole-star breakpoint. Otherwise solve the requested target and let
# strict stage priority unlock planned tools, then extra purchases only if required.
old = """    const targetStars=Math.max(cfg.starBase+historical,Math.floor(n('targetStars',cfg.key==='s2'?680:200)));
    const currentStarsNow=historical+cfg.starBase+Math.floor(currentScoreNow/cfg.scorePerStar);
    const baselineStars=historical+cfg.starBase+Math.floor(baselineScore/cfg.scorePerStar);
    const desired=Math.max(0,(targetStars-historical-cfg.starBase)*cfg.scorePerStar);
    const solution=solveTargetWithAutoStamina(baselineScore,desired,p,baseResources,cfg);
    let plan=solution.plan;
    const diagnosticPlan=solution.diagnostic||null;
    let resourceBlocked=false;
    resources=solution.resources;
    const staminaPlan=solution.allocation;
    // Never step down to a lower Primostar goal. If the requested score is structurally reachable but the
    // remaining resource/Realm budget cannot fund it, keep that ORIGINAL target and render its shortages.
    if(!plan&&diagnosticPlan){plan=diagnosticPlan;resourceBlocked=!diagnosticPlan.realmFeasible;}
    lastRequestedTargetStars=targetStars; lastEffectiveTargetStars=targetStars;
"""
new = """    const targetStars=Math.max(cfg.starBase+historical,Math.floor(n('targetStars',cfg.key==='s2'?680:200)));
    const currentStarsNow=historical+cfg.starBase+Math.floor(currentScoreNow/cfg.scorePerStar);
    const baselineStars=historical+cfg.starBase+Math.floor(baselineScore/cfg.scorePerStar);
    const requestedDesired=Math.max(0,(targetStars-historical-cfg.starBase)*cfg.scorePerStar);
    const rawCeiling=smartBalanceRawCeiling(baselineScore,p,baseResources,cfg,historical);
    const effectiveTargetStars=Math.max(targetStars,Math.floor(Number(rawCeiling?.stars)||baselineStars));
    const desired=Math.max(0,(effectiveTargetStars-historical-cfg.starBase)*cfg.scorePerStar);
    const solution=solveTargetWithAutoStamina(baselineScore,desired,p,baseResources,cfg);
    let plan=solution.plan;
    const diagnosticPlan=solution.diagnostic||null;
    let resourceBlocked=false;
    resources=solution.resources;
    const staminaPlan=solution.allocation;
    // Never step down below the user's requested Primostar goal. Above-goal Smart Balance
    // is allowed only when projected RAW resources already fund that higher whole-star tier.
    if(!plan&&diagnosticPlan){plan=diagnosticPlan;resourceBlocked=!diagnosticPlan.realmFeasible;}
    lastRequestedTargetStars=targetStars; lastEffectiveTargetStars=effectiveTargetStars;
"""
replace_once(old, new, 'smart target selection')

replace_once("    $('desiredScore').textContent=fmt(desired);\n", "    $('desiredScore').textContent=fmt(requestedDesired);\n", 'requested score display')

# 5) Promote the projected Smart Balance number in the result and explain the source stage.
replace_once(
    "    const recommendationDelta=plan.score-baselineScore;\n",
    "    const recommendationDelta=plan.score-baselineScore;\n    const planStars=historical+cfg.starBase+Math.floor(plan.score/cfg.scorePerStar);\n    const smartAboveGoal=!resourceBlocked && effectiveTargetStars>targetStars;\n    const projectedAboveGoal=!resourceBlocked && planStars>targetStars;\n    const planSourceStage=candidateRealmStage(plan);\n",
    'smart result variables'
)
replace_once(
    "    const planStars=historical+cfg.starBase+Math.floor(plan.score/cfg.scorePerStar);\n",
    "",
    'remove duplicate planStars'
)
replace_once(
    "    $('recommendedBreakdownExplain').textContent=resourceBlocked?`This is the score-capable upgrade route for your ORIGINAL ${fmt(targetStars)}-Primostar target. It is not being downgraded; the resource cards below show what still needs funding.`:`Actual ${cfg.name} season-end score used by the recommendation: projected Character plus every suggested upgrade, adding ${fmt(Math.max(0,recommendationDelta))} progression points over the no-upgrade baseline.`;\n",
    "    $('recommendedBreakdownExplain').textContent=resourceBlocked?`This is the score-capable upgrade route for your ORIGINAL ${fmt(targetStars)}-Primostar target. It is not being downgraded; the resource cards below show what still needs funding.`:smartAboveGoal?`Smart Balance treats ${fmt(targetStars)} Primostars as the minimum goal, then raises the recommendation to the highest whole-Primostar tier funded by projected raw materials alone. Realm tools are not spent just to push above the goal.`:`Actual ${cfg.name} season-end score used by the recommendation: projected Character plus every suggested upgrade, adding ${fmt(Math.max(0,recommendationDelta))} progression points over the no-upgrade baseline.`;\n",
    'smart breakdown explanation'
)
replace_once(
    "    if($('resultEyebrow')) $('resultEyebrow').textContent=resourceBlocked?'Target plan · resource shortfall':'Recommended season-end result';\n",
    "    if($('resultEyebrow')) $('resultEyebrow').textContent=resourceBlocked?'Target plan · resource shortfall':projectedAboveGoal?'Smart Balance season-end result':'Recommended season-end result';\n",
    'smart result eyebrow'
)
replace_once(
    "    $('optimizedScore').textContent=resourceBlocked?`${fmt(plan.score)} / ${fmt(desired)} score · ${fmt(targetStars)} Primostars target plan`:`${fmt(plan.score)} / ${fmt(desired)} score · ${fmt(planStars)} Primostars`;\n",
    "    $('optimizedScore').textContent=resourceBlocked?`${fmt(plan.score)} / ${fmt(requestedDesired)} score · ${fmt(targetStars)} Primostars target plan`:projectedAboveGoal?`${fmt(plan.score)} score · Smart Balance ${fmt(planStars)} Primostars · goal ${fmt(targetStars)} ✓`:`${fmt(plan.score)} / ${fmt(requestedDesired)} score · ${fmt(planStars)} Primostars · goal ${fmt(targetStars)} ✓`;\n",
    'smart optimized score display'
)

# Add concise sourcing status to the normal optimizer summary.
old = """    }else{
      const brief=[];
      /* TOOL_ONLY_RESOURCE_GAPS_V4: reserve math intentionally hidden from result summary */
      if((resources.s2SkillReserve?.target||0)>0) brief.push(`${fmt(resources.s2SkillReserve.target)} S2 skill reserve`);
      if(gearLocked) brief.push('Gear locked');
      $('optimizerSummary').textContent=brief.join(' · ');
"""
new = """    }else{
      const brief=[];
      /* TOOL_ONLY_RESOURCE_GAPS_V4: reserve math intentionally hidden from result summary */
      if(projectedAboveGoal) brief.push(`Goal ${fmt(targetStars)} ✓ · projected ${fmt(planStars)}`);
      else brief.push(`Goal ${fmt(targetStars)} ✓`);
      if(planSourceStage===0) brief.push('raw projected materials only');
      else if(planSourceStage===1) brief.push('saved/planned Realm tools only as needed');
      else if(planSourceStage===2) brief.push('extra Realm purchases required');
      if((resources.s2SkillReserve?.target||0)>0) brief.push(`${fmt(resources.s2SkillReserve.target)} S2 skill reserve`);
      if(gearLocked) brief.push('Gear locked');
      $('optimizerSummary').textContent=brief.join(' · ');
"""
replace_once(old, new, 'smart optimizer summary')

# Keep the on-page method text aligned with the actual strict sourcing behavior.
old = """<p><b>S2 target optimization:</b> target plans are ranked by marginal acquisition effort using the verified Lv.120 Realm values (1,200 Ore / 1,500 Essence / 1,000 Sand per tool), max-bracket open-map yields, entered Cart production and Treat income, and the actual S2 upgrade-cost curves. The optimizer can move between Gear, individual Skills, individual Relics and individual Fantomons as their marginal score efficiency changes. Raw materials, saved Realm tools and paid Realm purchases share one acquisition-efficiency ranking; Realm/tool burden is used only to break effectively equal routes.</p>"""
new = """<p><b>S2 target optimization / Smart Balance:</b> the entered Primostar target is a minimum goal. The default planner first finds the highest whole-Primostar tier reachable from projected <b>raw materials only</b> (Saved + Cart + Shop + projected Stamina) and recommends the cheapest balanced route to that raw-only tier. If raw materials cannot reach the requested goal, it unlocks saved tools plus tools already included by the selected daily Realm purchase plan. Only if raw + those projected tools still cannot reach the goal may it recommend additional Realm purchases. Within each sourcing tier, Gear, individual Skills, individual Relics and individual Fantomons are still balanced by marginal acquisition efficiency and actual S2 upgrade-cost curves.</p>"""
replace_once(old, new, 'method text')

if changed:
    p.write_text(s, encoding='utf-8')
    print('Applied Smart Balance raw-first default behavior.')
else:
    print('Smart Balance raw-first behavior already current.')
