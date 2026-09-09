from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

if 'BOUNDED_COMPACT_BEST_V6' in s:
    print('Primostar compact bounded-candidate optimizer already applied.')
    raise SystemExit(0)

if 'NO_PAID_PRIMARY_FAST_COMPARE_V5' not in s:
    raise SystemExit('v8 optimizer marker not found; refusing to patch unknown baseline')
if 'SKILL_GEAR_BREAKPOINT_JUMP_V4' in s:
    raise SystemExit('rejected v7 breakpoint-jump optimizer is present; refusing to stack v9')

anchor="""      const relicStart=firstScoreIndex(boundedRelic,desired-charScore-maxGearScore-maxSkillScore-maxFantoScore);
      let boundedBest=null;

      /* COARSE_EXACT_SEED_V1
"""
insert="""      const relicStart=firstScoreIndex(boundedRelic,desired-charScore-maxGearScore-maxSkillScore-maxFantoScore);
      let boundedBest=null;

      /* NO_PAID_PRIMARY_FAST_COMPARE_V5 · BOUNDED_COMPACT_BEST_V6
         The bounded feasible scan used to materialize a full public plan object every time a
         candidate improved (or tied) the acquisition metric. CPU profiling showed candidate
         construction/comparison dominating the hot case. Keep only the exact comparator key
         plus option/Realm references while searching, then materialize ONE normal candidate at
         the end. The comparison order below mirrors betterFeasibleCandidate() exactly. */
      const boundedCommit=(go,so,ro,fo,score,oreRealm,essenceRealm,sandRealm,acquisition)=>{
        const acquisition0=Number(acquisition?.hours);
        const acquisitionHours=Number.isFinite(acquisition0)?acquisition0:1e18;
        const realmPacks=(Number(oreRealm?.packs)||0)+(Number(essenceRealm?.packs)||0)+(Number(sandRealm?.packs)||0);
        const paid=(Number(realmPacks)||0)>0;
        const unknownPriceRefreshes=
          Math.max(0,Number(oreRealm?.unknownPriceRefreshes)||0)+
          Math.max(0,Number(essenceRealm?.unknownPriceRefreshes)||0)+
          Math.max(0,Number(sandRealm?.unknownPriceRefreshes)||0);
        const dawniumCost=(Number(oreRealm?.dawnium)||0)+(Number(essenceRealm?.dawnium)||0)+(Number(sandRealm?.dawnium)||0);
        const paidRuns=
          Math.max(0,Number(oreRealm?.paidRunsUsed)||0)+
          Math.max(0,Number(essenceRealm?.paidRunsUsed)||0)+
          Math.max(0,Number(sandRealm?.paidRunsUsed)||0);
        const totalRuns=
          Math.max(0,Number(oreRealm?.runsNeeded)||0)+
          Math.max(0,Number(essenceRealm?.runsNeeded)||0)+
          Math.max(0,Number(sandRealm?.runsNeeded)||0);
        const bankedUsed=
          Math.max(0,Number(oreRealm?.bankedUsed)||0)+
          Math.max(0,Number(essenceRealm?.bankedUsed)||0)+
          Math.max(0,Number(sandRealm?.bankedUsed)||0);
        const oreShare=resources.ore>0?go.oreCost/resources.ore:(go.oreCost>0?go.oreCost/100000:0);
        const essenceShare=resources.essence>0?so.cost/resources.essence:(so.cost>0?so.cost/100000:0);
        const sandShare=resources.sand>0?ro.cost/resources.sand:(ro.cost>0?ro.cost/100000:0);
        const treatShare=resources.treat>0?fo.cost/resources.treat:(fo.cost>0?fo.cost/10000:0);
        const refinedShare=resources.refinedTracked&&resources.refined>0?go.refinedCost/resources.refined:0;
        boundedBest={
          go,so,ro,fo,score,oreRealm,essenceRealm,sandRealm,
          acquisitionHours,realmPacks,paid,unknownPriceRefreshes,dawniumCost,paidRuns,totalRuns,bankedUsed,
          overshoot:score-desired,
          maxShare:Math.max(oreShare,essenceShare,sandShare,treatShare,refinedShare),
          sumShare:oreShare+essenceShare+sandShare+treatShare+refinedShare,
          oreCost:go.oreCost,essenceCost:so.cost,sandCost:ro.cost,treatCost:fo.cost,refinedCost:go.refinedCost
        };
      };
      const considerBounded=(go,so,ro,fo,score,oreRealm,essenceRealm,sandRealm,acquisition)=>{
        const a0=Number(acquisition?.hours);
        const acquisitionHours=Number.isFinite(a0)?a0:1e18;
        if(!boundedBest){boundedCommit(go,so,ro,fo,score,oreRealm,essenceRealm,sandRealm,acquisition);return true;}

        const realmPacks=(Number(oreRealm?.packs)||0)+(Number(essenceRealm?.packs)||0)+(Number(sandRealm?.packs)||0);
        const paid=(Number(realmPacks)||0)>0;
        if(paid!==boundedBest.paid){
          if(paid) return false;
          boundedCommit(go,so,ro,fo,score,oreRealm,essenceRealm,sandRealm,acquisition);return true;
        }

        if(paid){
          const unknownPriceRefreshes=
            Math.max(0,Number(oreRealm?.unknownPriceRefreshes)||0)+
            Math.max(0,Number(essenceRealm?.unknownPriceRefreshes)||0)+
            Math.max(0,Number(sandRealm?.unknownPriceRefreshes)||0);
          if(unknownPriceRefreshes>boundedBest.unknownPriceRefreshes) return false;
          if(unknownPriceRefreshes<boundedBest.unknownPriceRefreshes){boundedCommit(go,so,ro,fo,score,oreRealm,essenceRealm,sandRealm,acquisition);return true;}
          const dawniumCost=(Number(oreRealm?.dawnium)||0)+(Number(essenceRealm?.dawnium)||0)+(Number(sandRealm?.dawnium)||0);
          if(dawniumCost>boundedBest.dawniumCost+1e-9) return false;
          if(dawniumCost<boundedBest.dawniumCost-1e-9){boundedCommit(go,so,ro,fo,score,oreRealm,essenceRealm,sandRealm,acquisition);return true;}
        }

        if(acquisitionHours>boundedBest.acquisitionHours+1e-9) return false;
        if(acquisitionHours<boundedBest.acquisitionHours-1e-9){boundedCommit(go,so,ro,fo,score,oreRealm,essenceRealm,sandRealm,acquisition);return true;}

        const paidRuns=
          Math.max(0,Number(oreRealm?.paidRunsUsed)||0)+Math.max(0,Number(essenceRealm?.paidRunsUsed)||0)+Math.max(0,Number(sandRealm?.paidRunsUsed)||0);
        if(paidRuns>boundedBest.paidRuns) return false;
        if(paidRuns<boundedBest.paidRuns){boundedCommit(go,so,ro,fo,score,oreRealm,essenceRealm,sandRealm,acquisition);return true;}
        const totalRuns=
          Math.max(0,Number(oreRealm?.runsNeeded)||0)+Math.max(0,Number(essenceRealm?.runsNeeded)||0)+Math.max(0,Number(sandRealm?.runsNeeded)||0);
        if(totalRuns>boundedBest.totalRuns) return false;
        if(totalRuns<boundedBest.totalRuns){boundedCommit(go,so,ro,fo,score,oreRealm,essenceRealm,sandRealm,acquisition);return true;}
        const bankedUsed=
          Math.max(0,Number(oreRealm?.bankedUsed)||0)+Math.max(0,Number(essenceRealm?.bankedUsed)||0)+Math.max(0,Number(sandRealm?.bankedUsed)||0);
        if(bankedUsed>boundedBest.bankedUsed) return false;
        if(bankedUsed<boundedBest.bankedUsed){boundedCommit(go,so,ro,fo,score,oreRealm,essenceRealm,sandRealm,acquisition);return true;}

        const overshoot=score-desired;
        if(overshoot>boundedBest.overshoot+1e-9) return false;
        if(overshoot<boundedBest.overshoot-1e-9){boundedCommit(go,so,ro,fo,score,oreRealm,essenceRealm,sandRealm,acquisition);return true;}
        const oreShare=resources.ore>0?go.oreCost/resources.ore:(go.oreCost>0?go.oreCost/100000:0);
        const essenceShare=resources.essence>0?so.cost/resources.essence:(so.cost>0?so.cost/100000:0);
        const sandShare=resources.sand>0?ro.cost/resources.sand:(ro.cost>0?ro.cost/100000:0);
        const treatShare=resources.treat>0?fo.cost/resources.treat:(fo.cost>0?fo.cost/10000:0);
        const refinedShare=resources.refinedTracked&&resources.refined>0?go.refinedCost/resources.refined:0;
        const maxShare=Math.max(oreShare,essenceShare,sandShare,treatShare,refinedShare);
        if(maxShare>boundedBest.maxShare+1e-9) return false;
        if(maxShare<boundedBest.maxShare-1e-9){boundedCommit(go,so,ro,fo,score,oreRealm,essenceRealm,sandRealm,acquisition);return true;}
        const sumShare=oreShare+essenceShare+sandShare+treatShare+refinedShare;
        if(sumShare<boundedBest.sumShare-1e-9){boundedCommit(go,so,ro,fo,score,oreRealm,essenceRealm,sandRealm,acquisition);return true;}
        return false;
      };
      const materializeBounded=()=>{
        if(!boundedBest) return null;
        const b=boundedBest;
        const candidate=makePlanCandidate(b.go,b.so,b.ro,b.fo,b.score,desired,resources,[b.oreRealm,b.essenceRealm,b.sandRealm],{hours:b.acquisitionHours});
        candidate.realm.days=realmDays;
        candidate.realmFeasible=true;
        return candidate;
      };

      /* COARSE_EXACT_SEED_V1
"""
if anchor not in s:
    raise SystemExit('bounded-search insertion anchor not found')
s=s.replace(anchor,insert,1)

old="""            const acquisition=acquisitionFor(go,so,ro,fo);
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
new="""            const acquisition=acquisitionFor(go,so,ro,fo);
            considerBounded(go,so,ro,fo,score,oreRealm,essenceRealm,sandRealm,acquisition);
"""
count=s.count(old)
if count != 2:
    raise SystemExit(f'expected exactly two v8 bounded candidate blocks, found {count}')
s=s.replace(old,new,2)

old_return="""      if(boundedBest) return {plan:boundedBest,diagnostic:boundedBest};
      // Defensive fall-through: if future rule changes violate one of the monotonic
"""
new_return="""      if(boundedBest){
        const boundedPlan=materializeBounded();
        return {plan:boundedPlan,diagnostic:boundedPlan};
      }
      // Defensive fall-through: if future rule changes violate one of the monotonic
"""
if old_return not in s:
    raise SystemExit('bounded return anchor not found')
s=s.replace(old_return,new_return,1)

p.write_text(s,encoding='utf-8')
print('Applied Primostar v9 compact bounded-candidate search with single final materialization.')
