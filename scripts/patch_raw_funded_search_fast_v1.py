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
       Exact fast path for the expensive case where every reachable NON-ORE category is
       already funded by raw inventory. marginalWeightedSpend then prices all productive
       Essence/Sand/Treat spend at zero (their configured fully-funded floors), while Ore
       remains the 1.00 acquisition baseline. Ore itself does NOT need to be fully funded:
       lower Gear Ore cost still has strictly lower acquisition effort before Realm sourcing
       is considered, even if that Gear route ultimately uses banked/paid Ore Realm entries.

       Therefore the global winner must use the LOWEST Gear option that can still reach the
       requested score with maximum non-Gear score. With Gear fixed, every candidate has the
       same acquisition effort and Ore Realm stage. The normal comparator then reduces to
       overscore -> maxShare -> sumShare. Evaluate that exact tie-break space as
       Relic x Fantomon with a binary-search Skill lookup instead of Relic x Fantomon x Skill.
       Refined-Ore tracking stays on the general path because it adds a separate hard constraint. */
    const nonOreRawFunded=!resources.refinedTracked &&
      (Number(resources.essence)||0)>=Math.max(0,Number(headroomCosts?.essence)||0)-0.5 &&
      (Number(resources.sand)||0)>=Math.max(0,Number(headroomCosts?.sand)||0)-0.5 &&
      (Number(resources.treat)||0)>=Math.max(0,Number(headroomCosts?.treat)||0)-0.5;
    if(nonOreRawFunded){
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
        const oreRealm=realmTopupFor('ore',go.oreCost,resources.ore,resources,cfg,p);
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
            const candidate=makePlanCandidate(go,so,ro,fo,score,desired,resources,[oreRealm,zeroEssence,zeroSand],sharedAcquisition);
            candidate.realm.days=realmDays;
            candidate.realmFeasible=oreRealm.feasible;
            if(!oreRealm.feasible) continue;
            if(betterFeasibleCandidate(candidate,fastBest)) fastBest=candidate;
          }
        }
        if(fastBest) return {plan:fastBest,diagnostic:fastBest};
      }
    }

'''
s=s.replace(anchor,fast,1)

p.write_text(s,encoding='utf-8')
print('added exact non-Ore-funded search fast path')
