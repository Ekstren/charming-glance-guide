from pathlib import Path

path = Path('index.html')
s = path.read_text(encoding='utf-8')

marker = """    /* AFFORDABLE_TREAT_FEASIBLE_V1
"""
if marker not in s:
    raise SystemExit('optimizer insertion marker not found')
if 'BOUNDED_FEASIBLE_SEARCH_V1' in s:
    print('Bounded feasible optimizer search already present.')
    raise SystemExit(0)

block = r'''    /* BOUNDED_FEASIBLE_SEARCH_V1
       Before the expensive diagnostic scan, prove the largest independently fundable
       option in each resource family. Because Gear/Ore, Skills/Essence, Relics/Sand and
       Fantomons/Treats use separate budgets in this model, the sum of those maxima proves
       whether at least one fully fundable target route exists.

       If a route exists without EXTRA Realm purchases, paid-refresh candidates are
       categorically worse under betterFeasibleCandidate(), so search only the owned/raw+
       banked-tool prefixes. Otherwise, if a route exists within maximum legal Realm
       capacity, search only the individually feasible prefixes. This cannot change the
       winner: every excluded option is either physically impossible or belongs to a
       sourcing tier that loses before acquisition-effort tie-breaks are considered.

       The bounded scan also starts each monotone category at the first score that could
       possibly reach the target even with all remaining categories maxed. That removes
       millions of low-score combinations that previously called the Gear binary search
       only to discover that no Gear option could make them reach target. */
    const lastTrueIndex=(options,predicate)=>{
      let lo=0,hi=(options?.length||0)-1,ans=-1;
      while(lo<=hi){
        const mid=(lo+hi)>>1;
        if(predicate(options[mid],mid)){ans=mid;lo=mid+1;}else hi=mid-1;
      }
      return ans;
    };
    const firstScoreIndex=(options,scoreNeeded)=>{
      const need=Math.max(0,Number(scoreNeeded)||0);
      let lo=0,hi=(options?.length||0)-1,ans=options?.length||0;
      while(lo<=hi){
        const mid=(lo+hi)>>1;
        if((Number(options[mid]?.score)||0)>=need){ans=mid;hi=mid-1;}else lo=mid+1;
      }
      return ans;
    };
    const refinedFunded=go=>!resources.refinedTracked || (Number(go?.refinedCost)||0)<=(Number(resources.refined)||0)+0.5;
    const noPaidRealm=x=>!!x?.feasible && Math.max(0,Number(x?.packs)||0)<=0;

    const feasibleLast={
      gear:lastTrueIndex(gearOptions,go=>refinedFunded(go)&&!!oreFor(go)?.feasible),
      skill:lastTrueIndex(cats.skillOptions,so=>!!essFor(so)?.feasible),
      relic:lastTrueIndex(cats.relicOptions,ro=>!!sandFor(ro)?.feasible),
      fanto:lastTrueIndex(cats.fantoOptions,fo=>(Number(fo?.cost)||0)<=(Number(resources.treat)||0)+0.5)
    };
    const noPaidLast={
      gear:lastTrueIndex(gearOptions,go=>refinedFunded(go)&&noPaidRealm(oreFor(go))),
      skill:lastTrueIndex(cats.skillOptions,so=>noPaidRealm(essFor(so))),
      relic:lastTrueIndex(cats.relicOptions,ro=>noPaidRealm(sandFor(ro))),
      fanto:feasibleLast.fanto
    };
    const scoreAt=(options,index)=>index>=0?(Number(options[index]?.score)||0):-Infinity;
    const maxRouteScore=last=>charScore+
      scoreAt(gearOptions,last.gear)+scoreAt(cats.skillOptions,last.skill)+
      scoreAt(cats.relicOptions,last.relic)+scoreAt(cats.fantoOptions,last.fanto);
    const noPaidRoutePossible=Object.values(noPaidLast).every(i=>i>=0) && maxRouteScore(noPaidLast)>=desired-1e-9;
    const feasibleRoutePossible=Object.values(feasibleLast).every(i=>i>=0) && maxRouteScore(feasibleLast)>=desired-1e-9;
    const boundedLast=noPaidRoutePossible?noPaidLast:(feasibleRoutePossible?feasibleLast:null);

    if(boundedLast){
      const boundedGear=gearOptions.slice(0,boundedLast.gear+1);
      const boundedSkill=cats.skillOptions.slice(0,boundedLast.skill+1);
      const boundedRelic=cats.relicOptions.slice(0,boundedLast.relic+1);
      const boundedFanto=cats.fantoOptions.slice(0,boundedLast.fanto+1);
      const maxGearScore=Number(boundedGear[boundedGear.length-1]?.score)||0;
      const maxSkillScore=Number(boundedSkill[boundedSkill.length-1]?.score)||0;
      const maxFantoScore=Number(boundedFanto[boundedFanto.length-1]?.score)||0;
      const relicStart=firstScoreIndex(boundedRelic,desired-charScore-maxGearScore-maxSkillScore-maxFantoScore);
      let boundedBest=null;

      for(let ri=relicStart;ri<boundedRelic.length;ri++){
        const ro=boundedRelic[ri];
        const sandRealm=sandFor(ro);
        const fantoStart=firstScoreIndex(boundedFanto,desired-charScore-ro.score-maxGearScore-maxSkillScore);
        for(let fi=fantoStart;fi<boundedFanto.length;fi++){
          const fo=boundedFanto[fi];
          const fixedBeforeSkill=charScore+ro.score+fo.score;
          const skillStart=firstScoreIndex(boundedSkill,desired-fixedBeforeSkill-maxGearScore);
          if(skillStart>=boundedSkill.length) continue;
          let lastGearAdds=null;

          for(let si=skillStart;si<boundedSkill.length;si++){
            const so=boundedSkill[si];
            const fixedScore=fixedBeforeSkill+so.score;
            const needGear=Math.max(0,desired-fixedScore);
            const go=gearLocked
              ? (boundedGear[0].score>=needGear?boundedGear[0]:null)
              : firstGearOptionAtLeast(boundedGear,needGear);
            if(!go) continue;

            // For fixed Relic+Fantomon, Skill rises monotonically while the minimum Gear
            // required falls monotonically. Only the first Skill option for each Gear step
            // can survive the cost/overscore comparator. Once Gear is already at its base,
            // all later Skill options are strictly dominated.
            if(lastGearAdds===go.adds){
              if(go.adds===0) break;
              continue;
            }
            lastGearAdds=go.adds;

            const score=fixedScore+go.score;
            if(score<desired) continue;
            if(!refinedFunded(go)) continue;
            const oreRealm=oreFor(go),essenceRealm=essFor(so);
            if(!oreRealm.feasible||!essenceRealm.feasible||!sandRealm.feasible) continue;

            // Same exact dominance rule used by the legacy full scan, but before the
            // expensive joint acquisition equation.
            if(boundedBest && go.oreCost>=boundedBest.oreCost && so.cost>=boundedBest.essenceCost &&
               ro.cost>=boundedBest.sandCost && fo.cost>=boundedBest.treatCost &&
               go.refinedCost>=boundedBest.refinedCost) continue;

            const acquisition=acquisitionFor(go,so,ro,fo);
            const candidate=makePlanCandidate(go,so,ro,fo,score,desired,resources,[oreRealm,essenceRealm,sandRealm],acquisition);
            candidate.realm.days=realmDays;
            candidate.realmFeasible=true;
            if(betterFeasibleCandidate(candidate,boundedBest)) boundedBest=candidate;
          }
        }
      }
      if(boundedBest) return {plan:boundedBest,diagnostic:boundedBest};
      // Defensive fall-through: if future rule changes violate one of the monotonic
      // assumptions above, the legacy full scan below still preserves correctness.
    }

'''

s = s.replace(marker, block + marker, 1)
path.write_text(s, encoding='utf-8')
print('Added exact bounded feasible-search fast path to Primostar optimizer.')
