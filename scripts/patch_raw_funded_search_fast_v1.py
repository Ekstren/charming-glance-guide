from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
MARK='RAW_FUNDED_SEARCH_FAST_V1'
if MARK in s:
    print('raw-funded optimizer fast path already applied')
    raise SystemExit(0)

anchor='''    if(baseScore>=desired){
      const zero={gear:baseGear,skill:cats.skill.avg,relic:cats.relic.avg,fanto:cats.fanto.avg,skillLevels:cats.skill.levels,relicLevels:cats.relic.levels,fantoLevels:cats.fanto.levels,oreCost:0,essenceCost:0,sandCost:0,treatCost:0,refinedCost:0,score:baseScore,gearAdds:0,skillAdds:0,relicAdds:0,fantoAdds:0,dawniumCost:0,realmAttempts:0,realmPacks:0,seasonKey:cfg.key,realmFeasible:true,realm:{days:realmDays,ore:realmTopupFor('ore',0,resources.ore,resources,cfg,p),essence:realmTopupFor('essence',0,resources.essence,resources,cfg,p),sand:realmTopupFor('sand',0,resources.sand,resources,cfg,p)}};
      return {plan:zero,diagnostic:zero};
    }

'''
if anchor not in s:
    raise SystemExit('searchPlans base-score anchor not found')

fast=r'''    if(baseScore>=desired){
      const zero={gear:baseGear,skill:cats.skill.avg,relic:cats.relic.avg,fanto:cats.fanto.avg,skillLevels:cats.skill.levels,relicLevels:cats.relic.levels,fantoLevels:cats.fanto.levels,oreCost:0,essenceCost:0,sandCost:0,treatCost:0,refinedCost:0,score:baseScore,gearAdds:0,skillAdds:0,relicAdds:0,fantoAdds:0,dawniumCost:0,realmAttempts:0,realmPacks:0,seasonKey:cfg.key,realmFeasible:true,realm:{days:realmDays,ore:realmTopupFor('ore',0,resources.ore,resources,cfg,p),essence:realmTopupFor('essence',0,resources.essence,resources,cfg,p),sand:realmTopupFor('sand',0,resources.sand,resources,cfg,p)}};
      return {plan:zero,diagnostic:zero};
    }

    /* RAW_FUNDED_SEARCH_FAST_V1
       Exact fast path for the expensive "everything is already funded" case.

       When raw Ore can fund every reachable Gear upgrade and raw Essence/Sand/Treats can
       fund every reachable upgrade in their categories, marginalWeightedSpend prices all
       productive non-Ore spend at zero (their configured fully-funded floor), while Ore
       remains the 1.00 baseline. Therefore acquisition effort is strictly determined by
       Gear Ore cost. The global winner must use the LOWEST Gear option that can still reach
       the requested score with the maximum non-Gear score available.

       With Gear fixed at that minimum, every remaining candidate has identical acquisition
       effort and Realm stage (raw-only). The normal comparator then reduces exactly to:
       minimum overscore -> minimum maxShare -> minimum sumShare. We can evaluate that exact
       tie-break space as Relic x Fantomon with a binary-search Skill lookup instead of the
       old Relic x Fantomon x Skill scan. This removes millions of equivalent candidates
       without changing scoring or the winner. Refined-Ore tracking stays on the general path. */
    const maxGearOption=gearOptions[gearOptions.length-1];
    const rawFundsAllReachable=!resources.refinedTracked &&
      (Number(resources.ore)||0)>=(Number(maxGearOption?.oreCost)||0)-0.5 &&
      (Number(resources.essence)||0)>=Math.max(0,Number(headroomCosts?.essence)||0)-0.5 &&
      (Number(resources.sand)||0)>=Math.max(0,Number(headroomCosts?.sand)||0)-0.5 &&
      (Number(resources.treat)||0)>=Math.max(0,Number(headroomCosts?.treat)||0)-0.5;
    if(rawFundsAllReachable){
      const skillMax=cats.skillOptions[cats.skillOptions.length-1];
      const relicMax=cats.relicOptions[cats.relicOptions.length-1];
      const fantoMax=cats.fantoOptions[cats.fantoOptions.length-1];
      const maxNonGearScore=(skillMax?.score||0)+(relicMax?.score||0)+(fantoMax?.score||0);
      const go=gearLocked
        ? (gearOptions[0].score>=Math.max(0,desired-charScore-maxNonGearScore)?gearOptions[0]:null)
        : firstGearOptionAtLeast(gearOptions,Math.max(0,desired-charScore-maxNonGearScore));
      if(go){
        const firstSkillAtLeast=scoreNeeded=>{
          let lo=0,hi=cats.skillOptions.length-1,ans=null;
          while(lo<=hi){
            const mid=(lo+hi)>>1;
            if(cats.skillOptions[mid].score>=scoreNeeded){ans=cats.skillOptions[mid];hi=mid-1;}else lo=mid+1;
          }
          return ans;
        };
        const zeroOre=realmTopupFor('ore',0,resources.ore,resources,cfg,p);
        const zeroEssence=realmTopupFor('essence',0,resources.essence,resources,cfg,p);
        const zeroSand=realmTopupFor('sand',0,resources.sand,resources,cfg,p);
        const sharedAcquisition=acquisitionEffortFor({ore:go.oreCost,essence:0,sand:0,treat:0},resources,cfg);
        let fastBest=null;
        for(const ro of cats.relicOptions){
          for(const fo of cats.fantoOptions){
            const neededSkill=Math.max(0,desired-charScore-go.score-ro.score-fo.score);
            const so=firstSkillAtLeast(neededSkill);
            if(!so) continue;
            const score=charScore+go.score+so.score+ro.score+fo.score;
            if(score<desired) continue;
            const candidate=makePlanCandidate(go,so,ro,fo,score,desired,resources,[zeroOre,zeroEssence,zeroSand],sharedAcquisition);
            candidate.realm.days=realmDays;
            candidate.realmFeasible=true;
            if(betterFeasibleCandidate(candidate,fastBest)) fastBest=candidate;
          }
        }
        if(fastBest) return {plan:fastBest,diagnostic:fastBest};
      }
    }

'''
s=s.replace(anchor,fast,1)

p.write_text(s,encoding='utf-8')
print('added exact raw-funded search fast path')
