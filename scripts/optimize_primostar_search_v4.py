from pathlib import Path

path=Path('index.html')
s=path.read_text(encoding='utf-8')

old="""      const maxGearScore=Number(boundedGear[boundedGear.length-1]?.score)||0;
      const maxSkillScore=Number(boundedSkill[boundedSkill.length-1]?.score)||0;
      const maxFantoScore=Number(boundedFanto[boundedFanto.length-1]?.score)||0;
      const relicStart=firstScoreIndex(boundedRelic,desired-charScore-maxGearScore-maxSkillScore-maxFantoScore);
      let boundedBest=null;

      /* ACQUISITION_LOWER_BOUND_PRUNE_V1
"""
new="""      const maxGearScore=Number(boundedGear[boundedGear.length-1]?.score)||0;
      const maxSkillScore=Number(boundedSkill[boundedSkill.length-1]?.score)||0;
      const maxFantoScore=Number(boundedFanto[boundedFanto.length-1]?.score)||0;
      const relicStart=firstScoreIndex(boundedRelic,desired-charScore-maxGearScore-maxSkillScore-maxFantoScore);
      let boundedBest=null;

      /* COARSE_EXACT_SEED_V1
         Give branch-and-bound a strong VALID upper bound before the exhaustive scan.
         Sample a small evenly-spaced set of Relic/Fantomon states, but search the complete
         monotone Skill->minimum-Gear frontier inside each sampled state. Every seed is a
         normal exact candidate scored by the same comparator; it can only make later
         lower-bound pruning stronger, never alter correctness. */
      const sampledIndices=(start,length,count=10)=>{
        const out=new Set();
        const first=Math.max(0,Math.min(length-1,start));
        const last=Math.max(first,length-1);
        if(length<=0) return [];
        if(last===first) return [first];
        for(let i=0;i<count;i++) out.add(Math.round(first+(last-first)*(i/(count-1))));
        return [...out].sort((a,b)=>a-b);
      };
      for(const ri of sampledIndices(relicStart,boundedRelic.length,10)){
        const ro=boundedRelic[ri],sandRealm=sandFor(ro);
        const fantoStart=firstScoreIndex(boundedFanto,desired-charScore-ro.score-maxGearScore-maxSkillScore);
        for(const fi of sampledIndices(fantoStart,boundedFanto.length,10)){
          const fo=boundedFanto[fi];
          const fixedBeforeSkill=charScore+ro.score+fo.score;
          const skillStart=firstScoreIndex(boundedSkill,desired-fixedBeforeSkill-maxGearScore);
          if(skillStart>=boundedSkill.length) continue;
          let lastGearAdds=null;
          for(let si=skillStart;si<boundedSkill.length;si++){
            const so=boundedSkill[si];
            const go=gearLocked
              ? (boundedGear[0].score>=Math.max(0,desired-fixedBeforeSkill-so.score)?boundedGear[0]:null)
              : firstGearOptionAtLeast(boundedGear,Math.max(0,desired-fixedBeforeSkill-so.score));
            if(!go) continue;
            if(lastGearAdds===go.adds){ if(go.adds===0) break; continue; }
            lastGearAdds=go.adds;
            const score=fixedBeforeSkill+so.score+go.score;
            if(score<desired||!refinedFunded(go)) continue;
            const oreRealm=oreFor(go),essenceRealm=essFor(so);
            if(!oreRealm.feasible||!essenceRealm.feasible||!sandRealm.feasible) continue;
            const acquisition=acquisitionFor(go,so,ro,fo);
            const candidate=makePlanCandidate(go,so,ro,fo,score,desired,resources,[oreRealm,essenceRealm,sandRealm],acquisition);
            candidate.realm.days=realmDays;
            candidate.realmFeasible=true;
            if(betterFeasibleCandidate(candidate,boundedBest)) boundedBest=candidate;
          }
        }
      }

      /* ACQUISITION_LOWER_BOUND_PRUNE_V1
"""

count=s.count(old)
if count!=1:
    raise SystemExit(f'expected one bounded seed insertion point, found {count}')
s=s.replace(old,new,1)
path.write_text(s,encoding='utf-8')
print('Added coarse exact seed pass for Primostar branch-and-bound search.')
