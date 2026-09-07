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

# SMART_BALANCE_GOAL_STOP_V2
# The entered target remains the recommendation target. Raw-only maximum is informational.
old = """    const requestedDesired=Math.max(0,(targetStars-historical-cfg.starBase)*cfg.scorePerStar);
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
new = """    const requestedDesired=Math.max(0,(targetStars-historical-cfg.starBase)*cfg.scorePerStar);
    // SMART_BALANCE_GOAL_STOP_V2: calculate raw-only upside for INFORMATION only.
    // The recommendation itself stops at the entered goal instead of spending surplus raw
    // materials merely because a higher raw-only ceiling exists.
    const rawCeiling=smartBalanceRawCeiling(baselineScore,p,baseResources,cfg,historical);
    const projectedRawCeilingStars=Math.max(baselineStars,Math.floor(Number(rawCeiling?.stars)||baselineStars));
    const desired=requestedDesired;
    const solution=solveTargetWithAutoStamina(baselineScore,desired,p,baseResources,cfg);
    let plan=solution.plan;
    const diagnosticPlan=solution.diagnostic||null;
    let resourceBlocked=false;
    resources=solution.resources;
    const staminaPlan=solution.allocation;
    // Strict sourcing still applies inside solveTargetWithAutoStamina/searchPlans:
    // raw first -> saved/already-planned Realm tools if needed -> extra purchases last.
    if(!plan&&diagnosticPlan){plan=diagnosticPlan;resourceBlocked=!diagnosticPlan.realmFeasible;}
    lastRequestedTargetStars=targetStars; lastEffectiveTargetStars=targetStars;
"""
replace_once(old, new, 'target remains goal')

old = """    const recommendationDelta=plan.score-baselineScore;
    const planStars=historical+cfg.starBase+Math.floor(plan.score/cfg.scorePerStar);
    const smartAboveGoal=!resourceBlocked && effectiveTargetStars>targetStars;
    const projectedAboveGoal=!resourceBlocked && planStars>targetStars;
    const planSourceStage=candidateRealmStage(plan);
    $('recommendedBreakdownExplain').textContent=resourceBlocked?`This is the score-capable upgrade route for your ORIGINAL ${fmt(targetStars)}-Primostar target. It is not being downgraded; the resource cards below show what still needs funding.`:smartAboveGoal?`Smart Balance treats ${fmt(targetStars)} Primostars as the minimum goal, then raises the recommendation to the highest whole-Primostar tier funded by projected raw materials alone. Realm tools are not spent just to push above the goal.`:`Actual ${cfg.name} season-end score used by the recommendation: projected Character plus every suggested upgrade, adding ${fmt(Math.max(0,recommendationDelta))} progression points over the no-upgrade baseline.`;
"""
new = """    const recommendationDelta=plan.score-baselineScore;
    const planStars=historical+cfg.starBase+Math.floor(plan.score/cfg.scorePerStar);
    const projectedAboveGoal=!resourceBlocked && planStars>targetStars;
    const rawPotentialAboveGoal=!resourceBlocked && projectedRawCeilingStars>targetStars;
    const planSourceStage=candidateRealmStage(plan);
    $('recommendedBreakdownExplain').textContent=resourceBlocked?`This is the score-capable upgrade route for your ORIGINAL ${fmt(targetStars)}-Primostar target. It is not being downgraded; the resource cards below show what still needs funding.`:rawPotentialAboveGoal?`Smart Balance stops the recommended spend once the ${fmt(targetStars)}-Primostar goal is funded. Projected raw materials could reach about ${fmt(projectedRawCeilingStars)} Primostars if you intentionally spend farther, but that upside is informational and does not consume extra raw materials or Realm tools in this goal plan.`:`Actual ${cfg.name} season-end score used by the recommendation: projected Character plus every suggested upgrade, adding ${fmt(Math.max(0,recommendationDelta))} progression points over the no-upgrade baseline.`;
"""
replace_once(old, new, 'goal plan explanation')

replace_once(
    "    if($('resultEyebrow')) $('resultEyebrow').textContent=resourceBlocked?'Target plan · resource shortfall':projectedAboveGoal?'Smart Balance season-end result':'Recommended season-end result';\n",
    "    if($('resultEyebrow')) $('resultEyebrow').textContent=resourceBlocked?'Target plan · resource shortfall':'Smart Balance goal plan';\n",
    'result eyebrow'
)

replace_once(
    "    $('optimizedScore').textContent=resourceBlocked?`${fmt(plan.score)} / ${fmt(requestedDesired)} score · ${fmt(targetStars)} Primostars target plan`:projectedAboveGoal?`${fmt(plan.score)} score · Smart Balance ${fmt(planStars)} Primostars · goal ${fmt(targetStars)} ✓`:`${fmt(plan.score)} / ${fmt(requestedDesired)} score · ${fmt(planStars)} Primostars · goal ${fmt(targetStars)} ✓`;\n",
    "    $('optimizedScore').textContent=resourceBlocked?`${fmt(plan.score)} / ${fmt(requestedDesired)} score · ${fmt(targetStars)} Primostars target plan`:`${fmt(plan.score)} / ${fmt(requestedDesired)} score · ${fmt(planStars)} Primostars · goal ${fmt(targetStars)} ✓`;\n",
    'optimized score goal display'
)

old = """    }else{
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
new = """    }else{
      const brief=[];
      /* TOOL_ONLY_RESOURCE_GAPS_V4: reserve math intentionally hidden from result summary */
      brief.push(`Goal ${fmt(targetStars)} ✓`);
      if(rawPotentialAboveGoal) brief.push(`projected raw-only potential ${fmt(projectedRawCeilingStars)}`);
      if(planSourceStage===0) brief.push('goal funded with raw projected materials only');
      else if(planSourceStage===1) brief.push('saved/planned Realm tools used only as needed');
      else if(planSourceStage===2) brief.push('extra Realm purchases required');
      if((resources.s2SkillReserve?.target||0)>0) brief.push(`${fmt(resources.s2SkillReserve.target)} S2 skill reserve`);
      if(gearLocked) brief.push('Gear locked');
      $('optimizerSummary').hidden=false;
      $('optimizerSummary').textContent=brief.join(' · ');
"""
replace_once(old, new, 'visible projected potential summary')

old = """<p><b>S2 target optimization / Smart Balance:</b> the entered Primostar target is a minimum goal. The default planner first finds the highest whole-Primostar tier reachable from projected <b>raw materials only</b> (Saved + Cart + Shop + projected Stamina) and recommends the cheapest balanced route to that raw-only tier. If raw materials cannot reach the requested goal, it unlocks saved tools plus tools already included by the selected daily Realm purchase plan. Only if raw + those projected tools still cannot reach the goal may it recommend additional Realm purchases. Within each sourcing tier, Gear, individual Skills, individual Relics and individual Fantomons are still balanced by marginal acquisition efficiency and actual S2 upgrade-cost curves.</p>"""
new = """<p><b>S2 target optimization / Smart Balance:</b> the entered Primostar target is the <b>recommended stopping point</b>, not an instruction to spend every projected resource. The planner finds the best balanced route to that goal using projected <b>raw materials first</b> (Saved + Cart + Shop + projected Stamina). If raw alone cannot reach the goal, it unlocks saved tools plus tools already included by the selected daily Realm purchase plan; only if raw + those projected tools still cannot reach the goal may it recommend additional Realm purchases. Separately, the result shows the higher <b>projected raw-only potential</b> when surplus raw income could reach more Primostars, but that ceiling is informational and does not raise the recommended spend. Within each sourcing tier, Gear, individual Skills, individual Relics and individual Fantomons are balanced by marginal acquisition efficiency and the actual S2 upgrade-cost curves.</p>"""
replace_once(old, new, 'method text goal stop')

if changed:
    p.write_text(s, encoding='utf-8')
    print('Applied Smart Balance goal-stop v2 behavior.')
else:
    print('Smart Balance goal-stop v2 already current.')
