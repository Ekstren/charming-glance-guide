from pathlib import Path

PATH = Path('index.html')
text = PATH.read_text(encoding='utf-8')
MARKER = 'POST_TARGET_SURPLUS_TOPUP_V1'

if MARKER in text:
    print('Post-target surplus top-up already applied.')
    raise SystemExit(0)


def replace_once(old: str, new: str, label: str):
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly 1 match, found {count}')
    text = text.replace(old, new, 1)

anchor = "  function solveTargetWithAutoStamina(baseScore,desired,p,baseResources,cfg=activeCalcConfig()){\n"
helper = r'''  /* POST_TARGET_SURPLUS_TOPUP_V1
     After the cheapest target-reaching plan is selected, use only leftover raw, spendable
     capped resources to advance their own category toward the safe season-end cap. Enabled
     S2 reserves have already been removed from resources before this runs. This pass never
     spends Ore, Realm tools, or Dawnium and therefore cannot make the target plan less safe. */
  function applyPostTargetSurplusTopups(plan,resources,desired,p,cfg=activeCalcConfig()){
    if(!plan || cfg.key!=='s1' || Number(plan.score)<Number(desired)) return plan;
    const caps=categoryCapsForCharacter(p.upgradeCapLevel??p.level,cfg);
    const out={
      ...plan,
      skillLevels:Array.isArray(plan.skillLevels)?plan.skillLevels.slice():[],
      relicLevels:Array.isArray(plan.relicLevels)?plan.relicLevels.slice():[],
      fantoLevels:Array.isArray(plan.fantoLevels)?plan.fantoLevels.slice():[]
    };
    const topups={skillAdds:0,relicAdds:0,fantoAdds:0,essence:0,sand:0,treat:0,score:0};

    const fill=(levelsField,costField,addsField,avgField,budgetKey,cap,stepCost,floor,weight,topupCostKey,topupAddsKey)=>{
      const levels=out[levelsField];
      if(!levels.length || !Number.isFinite(Number(cap))) return;
      let budget=Math.max(0,(Number(resources?.[budgetKey])||0)-(Number(out[costField])||0));
      let spent=0,adds=0,scoreGain=0,safety=0;
      while(safety++<10000){
        let bestIdx=-1,bestCost=Infinity,bestLevel=Infinity;
        for(let i=0;i<levels.length;i++){
          const level=Math.floor(Number(levels[i])||0);
          if(level>=cap) continue;
          const cost=Number(stepCost(level));
          if(!Number.isFinite(cost) || cost<0) continue;
          if(cost<bestCost-1e-9 || (Math.abs(cost-bestCost)<1e-9 && level<bestLevel)){
            bestIdx=i; bestCost=cost; bestLevel=level;
          }
        }
        if(bestIdx<0 || bestCost>budget+1e-9) break;
        const before=Math.floor(Number(levels[bestIdx])||0);
        levels[bestIdx]=before+1;
        budget-=bestCost; spent+=bestCost; adds++;
        if(before>=floor) scoreGain+=weight;
      }
      if(!adds) return;
      out[costField]=(Number(out[costField])||0)+spent;
      out[addsField]=(Number(out[addsField])||0)+adds;
      out[avgField]=averageLevels(levels);
      out.score=(Number(out.score)||0)+scoreGain;
      topups[topupCostKey]+=spent;
      topups[topupAddsKey]+=adds;
      topups.score+=scoreGain;
    };

    fill('skillLevels','essenceCost','skillAdds','skill','essence',caps.skill,l=>skillStepCost(l,cfg),cfg.scoreFloor,cfg.weights.skill,'essence','skillAdds');
    fill('relicLevels','sandCost','relicAdds','relic','sand',caps.relic,l=>relicStepSand(l,cfg),cfg.relicFloor,cfg.weights.relic,'sand','relicAdds');
    fill('fantoLevels','treatCost','fantoAdds','fanto','treat',caps.fanto,l=>fantoStepTreatCost(l,cfg),cfg.scoreFloor,cfg.weights.fanto,'treat','fantoAdds');

    if(!(topups.skillAdds||topups.relicAdds||topups.fantoAdds)) return plan;
    out.overshoot=(Number(out.score)||0)-Number(desired||0);
    const acquisition=acquisitionEffortFor({ore:out.oreCost,essence:out.essenceCost,sand:out.sandCost,treat:out.treatCost},resources,cfg);
    out.acquisitionHours=acquisition.hours;
    out.oreAcquisitionHours=acquisition.oreHours;
    out.preserveAcquisitionScore=acquisition.hours+acquisition.oreHours*ORE_PRESERVE_PREMIUM;
    out.postTargetTopups=topups;
    return out;
  }

'''
replace_once(anchor, helper + anchor, 'surplus top-up helper insertion')

old_solution = """    const solution=solveTargetWithAutoStamina(baselineScore,desired,p,baseResources,cfg);\n    let plan=solution.plan;\n    const diagnosticPlan=solution.diagnostic||null;\n"""
new_solution = """    const solution=solveTargetWithAutoStamina(baselineScore,desired,p,baseResources,cfg);\n    let plan=solution.plan;\n    if(plan) plan=applyPostTargetSurplusTopups(plan,solution.resources,desired,p,cfg);\n    const diagnosticPlan=solution.diagnostic||null;\n"""
replace_once(old_solution, new_solution, 'final plan surplus top-up call')

old_explain = """    const recommendationDelta=plan.score-baselineScore;\n    $('recommendedBreakdownExplain').textContent=resourceBlocked?`This is the score-capable upgrade route for your ORIGINAL ${fmt(targetStars)}-Primostar target. It is not being downgraded; the resource cards below show what still needs funding.`:`Actual ${cfg.name} season-end score used by the recommendation: projected Character plus every suggested upgrade, adding ${fmt(Math.max(0,recommendationDelta))} progression points over the no-upgrade baseline.`;\n"""
new_explain = """    const recommendationDelta=plan.score-baselineScore;\n    const surplusTopupCount=(plan.postTargetTopups?.skillAdds||0)+(plan.postTargetTopups?.relicAdds||0)+(plan.postTargetTopups?.fantoAdds||0);\n    $('recommendedBreakdownExplain').textContent=resourceBlocked?`This is the score-capable upgrade route for your ORIGINAL ${fmt(targetStars)}-Primostar target. It is not being downgraded; the resource cards below show what still needs funding.`:`Actual ${cfg.name} season-end score used by the recommendation: projected Character plus every suggested upgrade, adding ${fmt(Math.max(0,recommendationDelta))} progression points over the no-upgrade baseline.${surplusTopupCount?` ${fmt(surplusTopupCount)} capped upgrade${surplusTopupCount===1?'':'s'} use leftover spendable Essence/Sand/Treats after the target is already secured.`:''}`;\n"""
replace_once(old_explain, new_explain, 'surplus top-up explanation')

PATH.write_text(text, encoding='utf-8')
print('Applied post-target surplus top-up.')
