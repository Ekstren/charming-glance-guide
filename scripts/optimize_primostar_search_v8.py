from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

if 'NO_PAID_PRIMARY_FAST_COMPARE_V5' in s:
    print('Primostar candidate fast-compare v8 already applied.')
    raise SystemExit(0)

# 1) Remove hot-path temporary arrays/reduces and repeated config lookups from candidate
# materialization. Returned public fields and values remain identical.
old_make="""  function makePlanCandidate(go,so,ro,fo,score,desired,resources,realms,acquisitionResult=null){
    const [oreRealm,essenceRealm,sandRealm]=realms;
    const dawniumCost=oreRealm.dawnium+essenceRealm.dawnium+sandRealm.dawnium;
    const realmPacks=oreRealm.packs+essenceRealm.packs+sandRealm.packs;
    const oreShare=resources.ore>0?go.oreCost/resources.ore:(go.oreCost>0?go.oreCost/100000:0);
    const essenceShare=resources.essence>0?so.cost/resources.essence:(so.cost>0?so.cost/100000:0);
    const sandShare=resources.sand>0?ro.cost/resources.sand:(ro.cost>0?ro.cost/100000:0);
    const treatShare=resources.treat>0?fo.cost/resources.treat:(fo.cost>0?fo.cost/10000:0);
    const refinedShare=resources.refinedTracked&&resources.refined>0?go.refinedCost/resources.refined:0;
    const shares=[oreShare,essenceShare,sandShare,treatShare,refinedShare];
    /* ACQUISITION_KERNEL_V2 · TOTAL_POOL_SMART_BALANCE_V1
       Scarcity coverage is fixed for one resource snapshot using projected raw + saved/planned
       tools at full material equivalent. Feasibility and the raw-before-tools consumption order
       are decided separately by Realm top-up math, so the hot search can reuse this kernel. */
    const acquisition=acquisitionResult||acquisitionEffortFor({ore:go.oreCost,essence:so.cost,sand:ro.cost,treat:fo.cost},resources,activeCalcConfig());
    const unknownPriceRefreshes=realms.reduce((sum,x)=>sum+Math.max(0,Number(x?.unknownPriceRefreshes)||0),0);
    return {
      gear:go.target,skill:so.avg,relic:ro.avg,fanto:fo.avg,
      skillLevels:so.levels,relicLevels:ro.levels,fantoLevels:fo.levels,
      oreCost:go.oreCost,essenceCost:so.cost,sandCost:ro.cost,treatCost:fo.cost,refinedCost:go.refinedCost,
      score,gearAdds:go.adds,skillAdds:so.adds,relicAdds:ro.adds,fantoAdds:fo.adds,
      oreShare,essenceShare,sandShare,treatShare,refinedShare,
      acquisitionHours:acquisition.hours,unknownPriceRefreshes,
      maxShare:Math.max(...shares),sumShare:shares.reduce((a,b)=>a+b,0),overshoot:score-desired,
      dawniumCost,realmAttempts:realmPacks,realmPacks,
      bankedHammersUsed:(oreRealm.bankedUsed||0),bankedKnucklesUsed:(essenceRealm.bankedUsed||0),bankedShovelsUsed:(sandRealm.bankedUsed||0),
      bankedToolsUsed:(oreRealm.bankedUsed||0)+(essenceRealm.bankedUsed||0)+(sandRealm.bankedUsed||0),seasonKey:activeCalcConfig().key,
      realm:{days:Number.isFinite(resources?.realmDays)?resources.realmDays:materialRealmDaysAvailable(activeCalcConfig()),ore:oreRealm,essence:essenceRealm,sand:sandRealm}
    };
  }
"""
new_make="""  function makePlanCandidate(go,so,ro,fo,score,desired,resources,realms,acquisitionResult=null){
    const oreRealm=realms[0],essenceRealm=realms[1],sandRealm=realms[2];
    const dawniumCost=oreRealm.dawnium+essenceRealm.dawnium+sandRealm.dawnium;
    const realmPacks=oreRealm.packs+essenceRealm.packs+sandRealm.packs;
    const oreShare=resources.ore>0?go.oreCost/resources.ore:(go.oreCost>0?go.oreCost/100000:0);
    const essenceShare=resources.essence>0?so.cost/resources.essence:(so.cost>0?so.cost/100000:0);
    const sandShare=resources.sand>0?ro.cost/resources.sand:(ro.cost>0?ro.cost/100000:0);
    const treatShare=resources.treat>0?fo.cost/resources.treat:(fo.cost>0?fo.cost/10000:0);
    const refinedShare=resources.refinedTracked&&resources.refined>0?go.refinedCost/resources.refined:0;
    const maxShare=Math.max(oreShare,essenceShare,sandShare,treatShare,refinedShare);
    const sumShare=oreShare+essenceShare+sandShare+treatShare+refinedShare;
    /* ACQUISITION_KERNEL_V2 · TOTAL_POOL_SMART_BALANCE_V1 · CANDIDATE_SCALAR_FASTPATH_V5
       Candidate creation is in the hottest optimizer path. Keep the exact same economics and
       public result fields, but avoid per-candidate temporary share/Realm arrays, reduce()
       callbacks and repeated activeCalcConfig() lookups. */
    const cfg=activeCalcConfig();
    const acquisition=acquisitionResult||acquisitionEffortFor({ore:go.oreCost,essence:so.cost,sand:ro.cost,treat:fo.cost},resources,cfg);
    const unknownPriceRefreshes=
      Math.max(0,Number(oreRealm?.unknownPriceRefreshes)||0)+
      Math.max(0,Number(essenceRealm?.unknownPriceRefreshes)||0)+
      Math.max(0,Number(sandRealm?.unknownPriceRefreshes)||0);
    const bankedHammersUsed=oreRealm.bankedUsed||0;
    const bankedKnucklesUsed=essenceRealm.bankedUsed||0;
    const bankedShovelsUsed=sandRealm.bankedUsed||0;
    return {
      gear:go.target,skill:so.avg,relic:ro.avg,fanto:fo.avg,
      skillLevels:so.levels,relicLevels:ro.levels,fantoLevels:fo.levels,
      oreCost:go.oreCost,essenceCost:so.cost,sandCost:ro.cost,treatCost:fo.cost,refinedCost:go.refinedCost,
      score,gearAdds:go.adds,skillAdds:so.adds,relicAdds:ro.adds,fantoAdds:fo.adds,
      oreShare,essenceShare,sandShare,treatShare,refinedShare,
      acquisitionHours:acquisition.hours,unknownPriceRefreshes,
      maxShare,sumShare,overshoot:score-desired,
      dawniumCost,realmAttempts:realmPacks,realmPacks,
      bankedHammersUsed,bankedKnucklesUsed,bankedShovelsUsed,
      bankedToolsUsed:bankedHammersUsed+bankedKnucklesUsed+bankedShovelsUsed,seasonKey:cfg.key,
      realm:{days:Number.isFinite(resources?.realmDays)?resources.realmDays:materialRealmDaysAvailable(cfg),ore:oreRealm,essence:essenceRealm,sand:sandRealm}
    };
  }
"""
if old_make not in s:
    raise SystemExit('makePlanCandidate baseline anchor not found')
s=s.replace(old_make,new_make,1)

# 2) Feasible-plan comparison does not need diagnostic candidateRealmStage() machinery.
# Every caller passes a genuinely feasible makePlanCandidate() object, so paid-vs-owned tier
# is exactly represented by realmPacks. Inline the primary acquisition comparison as well.
old_better="""  function betterFeasibleCandidate(candidate,best){
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
new_better="""  function betterFeasibleCandidate(candidate,best){
    if(!best) return true;

    /* TOTAL_POOL_SMART_BALANCE_V1 · FEASIBLE_COMPARE_SCALAR_V5
       Feasible candidates never carry Treat/Realm-overflow diagnostics. Their paid-source
       tier is therefore exactly `realmPacks > 0`; avoid candidateRealmStage() array creation
       on every comparison. Inline the acquisition metric's two scalar reads as well. */
    const cPaid=(Number(candidate.realmPacks)||0)>0,bPaid=(Number(best.realmPacks)||0)>0;
    if(cPaid!==bPaid) return !cPaid;

    if(cPaid&&bPaid){
      const cu=Math.max(0,Number(candidate.unknownPriceRefreshes)||0),bu=Math.max(0,Number(best.unknownPriceRefreshes)||0);
      if(cu<bu) return true;
      if(cu>bu) return false;
      if(candidate.dawniumCost<best.dawniumCost-1e-9) return true;
      if(candidate.dawniumCost>best.dawniumCost+1e-9) return false;
    }

    const cm0=Number(candidate.acquisitionHours),bm0=Number(best.acquisitionHours);
    const cm=Number.isFinite(cm0)?cm0:1e18,bm=Number.isFinite(bm0)?bm0:1e18;
    if(cm<bm-1e-9) return true;
    if(cm>bm+1e-9) return false;

    // Tool preservation remains ONLY a tie-breaker after exact acquisition equality.
    const toolCmp=betterToolBurden(candidate,best);
    if(toolCmp!==null) return toolCmp;

    return candidate.overshoot<best.overshoot-1e-9||
      (Math.abs(candidate.overshoot-best.overshoot)<1e-9&&candidate.maxShare<best.maxShare-1e-9)||
      (Math.abs(candidate.overshoot-best.overshoot)<1e-9&&Math.abs(candidate.maxShare-best.maxShare)<1e-9&&candidate.sumShare<best.sumShare-1e-9);
  }
"""
if old_better not in s:
    raise SystemExit('betterFeasibleCandidate baseline anchor not found')
s=s.replace(old_better,new_better,1)

# 3) In the bounded no-paid search every candidate is guaranteed to be in the same owned
# sourcing tier. Acquisition hours are therefore the primary comparator. Reject a candidate
# before allocating the full result object when its exact acquisition value is already worse;
# when strictly better, materialize it and assign directly. Only true acquisition ties need
# the full tie-break comparator.
old_seed="""            const acquisition=acquisitionFor(go,so,ro,fo);
            const candidate=makePlanCandidate(go,so,ro,fo,score,desired,resources,[oreRealm,essenceRealm,sandRealm],acquisition);
            candidate.realm.days=realmDays;
            candidate.realmFeasible=true;
            if(betterFeasibleCandidate(candidate,boundedBest)) boundedBest=candidate;
"""
new_seed="""            const acquisition=acquisitionFor(go,so,ro,fo);
            /* NO_PAID_PRIMARY_FAST_COMPARE_V5
               boundedLast===noPaidLast means every candidate is in the same preferred owned
               tier. Acquisition is the exact primary comparator, so do not allocate a full
               candidate object for a value that is already strictly worse than boundedBest. */
            if(noPaidRoutePossible&&boundedBest&&acquisition.hours>boundedBest.acquisitionHours+1e-9) continue;
            const candidate=makePlanCandidate(go,so,ro,fo,score,desired,resources,[oreRealm,essenceRealm,sandRealm],acquisition);
            candidate.realm.days=realmDays;
            candidate.realmFeasible=true;
            if(noPaidRoutePossible&&boundedBest&&acquisition.hours<boundedBest.acquisitionHours-1e-9){
              boundedBest=candidate;
            }else if(betterFeasibleCandidate(candidate,boundedBest)) boundedBest=candidate;
"""
count=s.count(old_seed)
if count < 2:
    raise SystemExit(f'expected at least two bounded candidate materialization anchors, found {count}')
# Replace the coarse seed occurrence and the bounded exact occurrence only. They are the first
# two matching blocks in this section; later fallback passes deliberately retain generic logic.
s=s.replace(old_seed,new_seed,2)

p.write_text(s,encoding='utf-8')
print('Applied Primostar v8 scalar candidate/comparator fast path and no-paid pre-materialization pruning.')
