from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

if 'RAW_IMPOSSIBILITY_FASTPATH_V3' in s:
    print('Raw impossibility fast path v3 already applied.')
    raise SystemExit(0)

anchor="""    const acquisitionFor=(go,so,ro,fo)=>({hours:jointHoursFast(go.__acqOreV1,so.__acqEssenceV1,ro.__acqSandV1,fo.__acqTreatV1)});
    let best=null,bestDiagnostic=null;

    /* TREAT_FUNDED_SEARCH_FAST_V1"""
replacement="""    const acquisitionFor=(go,so,ro,fo)=>({hours:jointHoursFast(go.__acqOreV1,so.__acqEssenceV1,ro.__acqSandV1,fo.__acqTreatV1)});
    let best=null,bestDiagnostic=null;

    /* RAW_IMPOSSIBILITY_FASTPATH_V3
       Prove whether ANY raw-only plan can reach the target before deciding whether a
       tool-backed exact fast-path result needs the expensive general scan. Resource pools
       are independent here, so the maximum raw-only score is simply the sum of the highest
       individually raw-affordable option in each category (respecting Refined Ore too).
       If that maximum is below desired, a stage-0 route is mathematically impossible. */
    const highestAffordable=(options,budget,costKey='cost',secondaryBudget=Infinity,secondaryKey='')=>{
      let bestOption=Array.isArray(options)&&options.length?options[0]:null;
      for(const option of (options||[])){
        const primary=Math.max(0,Number(option?.[costKey])||0);
        const secondary=secondaryKey?Math.max(0,Number(option?.[secondaryKey])||0):0;
        if(primary<=budget+0.5 && secondary<=secondaryBudget+0.5) bestOption=option;
        else if(primary>budget+0.5) break;
      }
      return bestOption;
    };
    const rawRefinedBudget=resources.refinedTracked?Math.max(0,Number(resources.refined)||0):Infinity;
    const rawMaxGear=highestAffordable(gearOptions,Math.max(0,Number(resources.ore)||0),'oreCost',rawRefinedBudget,'refinedCost');
    const rawMaxSkill=highestAffordable(cats.skillOptions,Math.max(0,Number(resources.essence)||0));
    const rawMaxRelic=highestAffordable(cats.relicOptions,Math.max(0,Number(resources.sand)||0));
    const rawMaxFanto=highestAffordable(cats.fantoOptions,Math.max(0,Number(resources.treat)||0));
    const rawOnlyMaxScore=charScore+(rawMaxGear?.score||0)+(rawMaxSkill?.score||0)+(rawMaxRelic?.score||0)+(rawMaxFanto?.score||0);
    const rawOnlyRoutePossible=rawOnlyMaxScore>=desired-1e-9;

    /* TREAT_FUNDED_SEARCH_FAST_V1"""
if anchor not in s: raise SystemExit('acquisition fastpath anchor not found')
s=s.replace(anchor,replacement,1)

old="""      if(fastBest && candidateRealmStage(fastBest)===0) return {plan:fastBest,diagnostic:fastBest};
      // Under strict raw-first sourcing, a tool-using fast-path result cannot short-circuit
      // the general scan because a raw-only route may still exist elsewhere in the search space."""
new="""      if(fastBest && (candidateRealmStage(fastBest)===0 || !rawOnlyRoutePossible)) return {plan:fastBest,diagnostic:fastBest};
      // If raw-only maximum score can still reach the target, keep scanning because the
      // hard source hierarchy requires stage 0 to beat this tool-backed fast-path result."""
if old not in s: raise SystemExit('treat fastpath return anchor not found')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('Applied raw-impossibility fast path v3.')
