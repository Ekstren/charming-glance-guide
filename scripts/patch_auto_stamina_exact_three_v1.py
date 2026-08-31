from pathlib import Path
import re

p=Path('index.html')
s=p.read_text(encoding='utf-8')
MARK='AUTO_STAMINA_EXACT_THREE_V1'
if MARK in s:
    print('Auto Stamina exact-three patch already applied')
    raise SystemExit(0)

start=s.find('  function solveTargetWithAutoStamina(')
end=s.find('  // REALM_20_REFRESH_TOOL_COUNT_V1',start)
if start<0 or end<0:
    raise SystemExit('solveTargetWithAutoStamina block not found')

new=r'''  /* AUTO_STAMINA_EXACT_THREE_V1
     Auto Stamina has exactly three legal strategies: all Ore, all Essence, or all Sand.
     Solve each legal resource state directly and compare the globally optimal score plan
     from each state. This is both more exact and cheaper than the old alternating solver,
     which could run the full optimizer up to six times while chasing a fixed point.

     If safe raw inventory already funds every reachable Ore/Essence/Sand upgrade through
     the projected cap, Stamina cannot change feasibility or marginal scarcity. In that
     common surplus case solve once and bank the otherwise-unused nodes as Ore. */
  function solveTargetWithAutoStamina(baseScore,desired,p,baseResources,cfg=activeCalcConfig()){
    const ctx=createPlanningContext(baseScore,desired,p,cfg);

    // Below the verified S2 Lv.120 map bracket, keep Stamina out of the numeric budget rather than guessing yields.
    if(!baseResources.yields?.mapReady){
      const allocation={ore:0,essence:0,sand:0,rolla:0,unassigned:baseResources.staminaNodes||0};
      const resources=applyStaminaAllocation(baseResources,allocation,cfg);
      const result=searchPlans(baseScore,desired,p,resources,cfg,ctx);
      return {plan:result.plan,diagnostic:result.plan||result.diagnostic,resources,allocation};
    }

    // Manual Stamina destinations do not depend on a score plan; apply them once and solve normally.
    if(staminaMode()!=='auto'){
      const allocation=allocateStaminaForPlan(null,baseResources,cfg,p);
      const resources=applyStaminaAllocation(baseResources,allocation,cfg);
      const result=searchPlans(baseScore,desired,p,resources,cfg,ctx);
      return {plan:result.plan,diagnostic:result.plan||result.diagnostic,resources,allocation};
    }

    const total=Math.max(0,Math.floor(baseResources.staminaNodes||0));
    const map=baseResources.yields?.map||{};
    const empty={ore:0,essence:0,sand:0,rolla:0,unassigned:0};
    const resultState=(allocation)=>{
      const resources=applyStaminaAllocation(baseResources,allocation,cfg);
      const result=searchPlans(baseScore,desired,p,resources,cfg,ctx);
      return {plan:result.plan,diagnostic:result.plan||result.diagnostic,resources,allocation,result};
    };
    const betterState=(state,best)=>{
      if(!best) return true;
      const cp=state.result.plan,bp=best.result.plan;
      if(!!cp!==!!bp) return !!cp;
      if(cp&&bp){
        if(betterFeasibleCandidate(cp,bp)) return true;
        if(betterFeasibleCandidate(bp,cp)) return false;
        return false;
      }
      const cd=state.result.diagnostic,bd=best.result.diagnostic;
      if(cd&&bd){
        if(betterDiagnosticCandidate(cd,bd)) return true;
        if(betterDiagnosticCandidate(bd,cd)) return false;
      }
      return !!cd&&!bd;
    };

    // Surplus fast path: every reachable raw-material category is already fully funded.
    // Extra Stamina cannot alter candidate feasibility or the marginal scarcity weights.
    const maxGearOre=Math.max(0,Number(ctx.gearOptions?.[ctx.gearOptions.length-1]?.oreCost)||0);
    const fullyRawFunded=
      (Number(baseResources.ore)||0)>=maxGearOre-0.5 &&
      (Number(baseResources.essence)||0)>=Math.max(0,Number(ctx.headroomCosts?.essence)||0)-0.5 &&
      (Number(baseResources.sand)||0)>=Math.max(0,Number(ctx.headroomCosts?.sand)||0)-0.5;
    if(fullyRawFunded){
      const allocation=(Number(map.ore)||0)>0?{...empty,ore:total}:{...empty,unassigned:total};
      const state=resultState(allocation);
      return {plan:state.result.plan,diagnostic:state.result.plan||state.result.diagnostic,resources:state.resources,allocation:state.allocation};
    }

    // Evaluate the complete legal Auto-Stamina state space directly: at most three searches.
    let bestState=null;
    for(const key of ['ore','essence','sand']){
      if((Number(map[key])||0)<=0) continue;
      const state=resultState({...empty,[key]:total});
      if(betterState(state,bestState)) bestState=state;
    }
    if(bestState){
      return {plan:bestState.result.plan,diagnostic:bestState.result.plan||bestState.result.diagnostic,resources:bestState.resources,allocation:bestState.allocation};
    }

    const allocation={...empty,unassigned:total};
    const state=resultState(allocation);
    return {plan:state.result.plan,diagnostic:state.result.plan||state.result.diagnostic,resources:state.resources,allocation};
  }

'''
s=s[:start]+new+s[end:]

s=s.replace(
'''  /* REMOVE_ORE_PRESERVATION_V1
     Ore now participates in the same acquisition-efficiency model as every other score
     resource. Tool preservation is handled only by the Minimize-tools 10%/20% hurdles. */''',
'''  /* REMOVE_ORE_PRESERVATION_V1
     Ore participates in the same acquisition-efficiency model as every other score
     resource. Realm/tool burden is now only a true-efficiency tie-breaker. */''',1)

s=s.replace(
'''  /* RAW_BEFORE_REALM_TOOLS_V1
     Upgrade selection is efficient WITHIN the cheapest Realm-tool tier, but raw materials
     that are safely spendable should be brute-forced before the planner consumes more Realm
     entries. Paid Realm purchases remain the strongest penalty; after that, fewer actual
     tool entries needed/consumed beats modeled reacquisition efficiency. This lets surplus
     Treats/Essence/Sand/Ore replace a tool-funded upgrade whenever the score math allows it. */''',
'''  /* REALM_TOOL_TIEBREAK_V1
     Acquisition effort is the primary route metric. Realm stage, Dawnium and actual tool
     burden are consulted only when acquisition effort is effectively tied, so sourcing
     details cannot override a materially better progression route. */''',1)

if 'Minimize-tools 10%/20% hurdles' in s:
    raise SystemExit('stale Minimize-tools optimizer comment remains')
if s.count(MARK)!=1:
    raise SystemExit('Auto Stamina exact-three marker missing or duplicated')

p.write_text(s,encoding='utf-8')
print('replaced iterative Auto Stamina solver with exact three-state search plus surplus fast path')
