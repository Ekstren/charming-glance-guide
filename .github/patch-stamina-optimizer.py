from pathlib import Path
import re

path = Path('index.html')
html = path.read_text(encoding='utf-8')

old_allocator = re.compile(r'''  // For a fixed upgrade plan, spend each projected node where it saves the most paid Realm cost\.\n  // Once all supported current-season score-material shortages are covered, every remaining verified node goes to Raw Ore for future Gear growth\.\n  function allocateStaminaForPlan\(plan,base,cfg=activeCalcConfig\(\),p=null\)\{.*?\n  \}\n\n  function staminaAllocationSignature''', re.S)

new_allocator = r'''  // For a FIXED upgrade plan, solve the complete Ore / Essence / Sand split instead of
  // greedily assigning one Stamina node at a time. Realm pricing is stepwise: several nodes
  // may need to land on one material before an entire paid refresh disappears, so a locally
  // best next node is not always the globally cheapest split for that plan.
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

    // If there is no score plan yet, preserve the existing policy: bank projected surplus as Ore.
    if(!plan){
      if((Number(map.ore)||0)>0) return {...empty,ore:total};
      return {...empty,unassigned:total};
    }

    const keys=['ore','essence','sand'];
    const costs={ore:staminaPlanCost(plan,'ore'),essence:staminaPlanCost(plan,'essence'),sand:staminaPlanCost(plan,'sand')};
    const yields={ore:Number(map.ore)||0,essence:Number(map.essence)||0,sand:Number(map.sand)||0};
    const realmPerRun={ore:staminaRealmYield(base,'ore'),essence:staminaRealmYield(base,'essence'),sand:staminaRealmYield(base,'sand')};
    const days=Number.isFinite(base?.realmDays)?base.realmDays:materialRealmDaysAvailable(cfg);
    const inventories=Object.fromEntries(keys.map(key=>[key,realmInventoryFor(key,cfg)]));

    // Precompute each resource's Realm result for every possible node count. The expensive Realm
    // logic is therefore O(nodes), while the complete split scan below is only cheap array lookups.
    const tables={};
    for(const key of keys){
      tables[key]=new Array(total+1);
      const inv=inventories[key];
      const perRun=realmPerRun[key];
      const baseBudget=Number(base[key])||0;
      for(let nodes=0;nodes<=total;nodes++){
        const budget=baseBudget+nodes*yields[key];
        tables[key][nodes]=realmTopup(costs[key],budget,perRun,days,inv.banked,inv.baselineRefreshes);
      }
    }

    const finiteOr=(v,fallback)=>Number.isFinite(Number(v))?Number(v):fallback;
    const metricFor=(oreNodes,essenceNodes,sandNodes)=>{
      const allocation={ore:oreNodes,essence:essenceNodes,sand:sandNodes,rolla:0,unassigned:0};
      const tops=[tables.ore[oreNodes],tables.essence[essenceNodes],tables.sand[sandNodes]];
      const feasible=tops.every(x=>!!x?.feasible);
      const remainingAfterMax=tops.reduce((sum,x)=>sum+Math.max(0,finiteOr(x?.remainingAfterMax,1e15)),0);
      const realmOverflow=tops.reduce((sum,x)=>sum+Math.max(0,finiteOr(x?.packs,1e9)-finiteOr(x?.maxPacks,0)),0);
      const dawnium=feasible?tops.reduce((sum,x)=>sum+finiteOr(x?.dawnium,1e15),0):Infinity;
      const realmPacks=tops.reduce((sum,x)=>sum+finiteOr(x?.packs,1e9),0);
      const bankedToolsUsed=tops.reduce((sum,x)=>sum+Math.max(0,finiteOr(x?.bankedUsed,0)),0);
      const bankedHammersUsed=Math.max(0,finiteOr(tops[0]?.bankedUsed,0));
      const rawShortfall=Math.max(0,costs.ore-((Number(base.ore)||0)+oreNodes*yields.ore))+
        Math.max(0,costs.essence-((Number(base.essence)||0)+essenceNodes*yields.essence))+
        Math.max(0,costs.sand-((Number(base.sand)||0)+sandNodes*yields.sand));
      return {allocation,feasible,remainingAfterMax,realmOverflow,dawnium,realmPacks,bankedToolsUsed,bankedHammersUsed,rawShortfall};
    };

    const better=(c,b)=>{
      if(!b) return true;
      if(c.feasible!==b.feasible) return c.feasible;
      if(c.feasible){
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
      // Equal paid-Realm outcome: avoid consuming banked tools. Preserve-Ore mode gives Hammers
      // the first tool tie-break; both modes still bank otherwise-unused projected nodes as Ore.
      if(optimizerMode()==='preserve'){
        if(c.bankedHammersUsed<b.bankedHammersUsed) return true;
        if(c.bankedHammersUsed>b.bankedHammersUsed) return false;
      }
      if(c.bankedToolsUsed<b.bankedToolsUsed) return true;
      if(c.bankedToolsUsed>b.bankedToolsUsed) return false;
      if(c.allocation.ore>b.allocation.ore) return true;
      if(c.allocation.ore<b.allocation.ore) return false;
      if(c.allocation.essence>b.allocation.essence) return true;
      return false;
    };

    let best=null;
    // Full integer split. At a fresh long season this is ~1.3M cheap comparisons for ~1,600 nodes;
    // all Realm topups were precomputed above, so this remains much cheaper than rerunning searchPlans.
    for(let essenceNodes=0;essenceNodes<=total;essenceNodes++){
      for(let sandNodes=0;sandNodes<=total-essenceNodes;sandNodes++){
        const oreNodes=total-essenceNodes-sandNodes;
        const candidate=metricFor(oreNodes,essenceNodes,sandNodes);
        if(better(candidate,best)) best=candidate;
      }
    }
    return best?.allocation||{...empty,ore:(Number(map.ore)||0)>0?total:0,unassigned:(Number(map.ore)||0)>0?0:total};
  }

  function staminaAllocationSignature'''

html, count = old_allocator.subn(new_allocator, html, count=1)
if count != 1:
    raise SystemExit(f'allocator replacement count={count}')

old_solver = re.compile(r'''  function solveTargetWithAutoStamina\(baseScore,desired,p,baseResources,cfg=activeCalcConfig\(\)\)\{.*?\n  \}\n\n  // Live-server correction:''', re.S)
new_solver = r'''  function solveTargetWithAutoStamina(baseScore,desired,p,baseResources,cfg=activeCalcConfig()){
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

    // Auto mode alternates between two exact subproblems:
    //   1) global score-plan search for the current resource mix;
    //   2) complete Stamina split search for that fixed plan.
    // Iterate until the split stabilizes (or a short cycle is detected) instead of stopping after one retarget pass.
    const initial=searchPlans(baseScore,desired,p,baseResources,cfg,ctx);
    let guidance=initial.plan||initial.diagnostic;
    if(!guidance){
      const allocation=allocateStaminaForPlan(null,baseResources,cfg,p);
      const resources=applyStaminaAllocation(baseResources,allocation,cfg);
      return {plan:null,diagnostic:null,resources,allocation};
    }

    const seen=new Set();
    let bestState=null;
    const betterState=(state,best)=>{
      if(!best) return true;
      const cp=state.result.plan, bp=best.result.plan;
      if(!!cp!==!!bp) return !!cp;
      if(cp&&bp){
        if(cp.dawniumCost<bp.dawniumCost-1e-9) return true;
        if(cp.dawniumCost>bp.dawniumCost+1e-9) return false;
        if(cp.realmPacks<bp.realmPacks) return true;
        if(cp.realmPacks>bp.realmPacks) return false;
        if(optimizerMode()==='preserve'){
          const cOre=(Number(state.resources.ore)||0)-(Number(cp.oreCost)||0);
          const bOre=(Number(best.resources.ore)||0)-(Number(bp.oreCost)||0);
          if(cOre>bOre+0.5) return true;
          if(cOre<bOre-0.5) return false;
        }
        if(cp.overshoot<bp.overshoot-1e-9) return true;
        if(cp.overshoot>bp.overshoot+1e-9) return false;
        return (cp.bankedToolsUsed||0)<(bp.bankedToolsUsed||0);
      }
      const cd=state.result.diagnostic, bd=best.result.diagnostic;
      if(cd&&bd) return betterDiagnosticCandidate(cd,bd);
      return !!cd;
    };

    for(let pass=0;pass<5;pass++){
      const allocation=allocateStaminaForPlan(guidance,baseResources,cfg,p);
      const signature=staminaAllocationSignature(allocation);
      if(seen.has(signature)) break;
      seen.add(signature);
      const resources=applyStaminaAllocation(baseResources,allocation,cfg);
      const result=searchPlans(baseScore,desired,p,resources,cfg,ctx);
      const state={plan:result.plan,diagnostic:result.plan||result.diagnostic,resources,allocation,result};
      if(betterState(state,bestState)) bestState=state;
      const nextGuidance=result.plan||result.diagnostic;
      if(!nextGuidance) break;
      guidance=nextGuidance;
    }

    if(bestState) return {plan:bestState.result.plan,diagnostic:bestState.result.plan||bestState.result.diagnostic,resources:bestState.resources,allocation:bestState.allocation};
    const allocation=allocateStaminaForPlan(guidance,baseResources,cfg,p);
    const resources=applyStaminaAllocation(baseResources,allocation,cfg);
    const result=searchPlans(baseScore,desired,p,resources,cfg,ctx);
    return {plan:result.plan,diagnostic:result.plan||result.diagnostic,resources,allocation};
  }

  // Live-server correction:'''

html, count = old_solver.subn(new_solver, html, count=1)
if count != 1:
    raise SystemExit(f'solver replacement count={count}')

old_method = 'Current-season score shortages are covered first; surplus verified nodes default to Raw Ore because Gear has the broadest practical upgrade runway while Skill Essence is constrained by Character level.'
new_method = 'In Auto mode, the planner now tests the complete Ore / Essence / Sand Stamina split for each chosen score plan, minimizing total paid Material Realm cost instead of greedily choosing one node at a time. It then re-solves the score plan until the Stamina split stabilizes. Once the requested current-season target is protected, otherwise-unused verified nodes default to Raw Ore because Gear has the broadest practical upgrade runway while Skill Essence is constrained by Character level.'
if old_method not in html:
    raise SystemExit('method text marker not found')
html = html.replace(old_method, new_method, 1)

path.write_text(html, encoding='utf-8')
print('Applied exact fixed-plan Stamina split optimizer and iterative convergence.')
