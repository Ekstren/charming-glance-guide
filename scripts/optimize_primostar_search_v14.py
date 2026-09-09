from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

MARKER='SG_SUBSET_LOWER_BOUND_V11'
if MARKER in s:
    print('Primostar v14 subset lower-bound optimizer already applied.')
    raise SystemExit(0)
if 'SKILL_GEAR_TWO_POINTER_V10' not in s or 'JOINT_HOURS_ACTIVE_SET_V9' not in s:
    raise SystemExit('Expected v13/v12 optimizer markers not found')

old_setup="""      const boundedFanto=cats.fantoOptions.slice(0,boundedFantoLast+1);
      const maxGearScore=Number(boundedGear[boundedGear.length-1]?.score)||0;
      const maxSkillScore=Number(boundedSkill[boundedSkill.length-1]?.score)||0;
      const maxFantoScore=Number(boundedFanto[boundedFanto.length-1]?.score)||0;
      const relicStart=firstScoreIndex(boundedRelic,desired-charScore-maxGearScore-maxSkillScore-maxFantoScore);
      let boundedBest=null;
"""
new_setup="""      const boundedFanto=cats.fantoOptions.slice(0,boundedFantoLast+1);
      const maxGearScore=Number(boundedGear[boundedGear.length-1]?.score)||0;
      const maxSkillScore=Number(boundedSkill[boundedSkill.length-1]?.score)||0;
      const maxFantoScore=Number(boundedFanto[boundedFanto.length-1]?.score)||0;

      /* BOUNDED_EAGER_REALM_V11
         The bounded search revisits the same Gear/Skill/Relic option objects thousands of
         times. Materialize their immutable Realm results once for this resource snapshot and
         keep the refined-funding bit on Gear. This removes the hot oreFor()/essFor() wrapper
         calls without changing any Realm math or candidate eligibility. */
      for(const go of boundedGear){ go.__realmOreV7=oreFor(go); go.__refinedFundedV11=refinedFunded(go); }
      for(const so of boundedSkill) so.__realmEssenceV7=essFor(so);
      for(const ro of boundedRelic) ro.__realmSandV7=sandFor(ro);

      /* SG_SUBSET_LOWER_BOUND_V11
         For any full candidate, acquisition hours must be at least the acquisition time of
         its Gear+Skill subset. Precompute the exact minimum Gear+Skill subset time for every
         reachable combined-score threshold. During Relic/Fantomon search this gives a cheap,
         mathematically safe lower bound that can reject an entire Skill/Gear frontier before
         visiting it. It cannot remove a winner: max(subset roots) is always <= the full joint
         acquisition root used by the primary comparator. */
      const sgPairs=[];
      for(const go of boundedGear){
        if(!go.__refinedFundedV11) continue;
        const ore=go.__acqOreV1;
        for(const so of boundedSkill){
          sgPairs.push([go.score+so.score,jointHoursFast(ore,so.__acqEssenceV1,0,0)]);
        }
      }
      sgPairs.sort((a,b)=>b[0]-a[0]);
      const sgScores=[],sgHours=[];
      let sgBestHours=Infinity;
      for(let i=0;i<sgPairs.length;){
        const score=sgPairs[i][0];
        do{ sgBestHours=Math.min(sgBestHours,sgPairs[i][1]); i++; }
        while(i<sgPairs.length&&Math.abs(sgPairs[i][0]-score)<1e-9);
        sgScores.push(score); sgHours.push(sgBestHours);
      }
      const sgSubsetLowerBound=(needRaw)=>{
        const need=Math.max(0,Number(needRaw)||0);
        let lo=0,hi=sgScores.length-1,ans=-1;
        while(lo<=hi){
          const mid=(lo+hi)>>1;
          if(sgScores[mid]>=need-1e-9){ans=mid;lo=mid+1;}else hi=mid-1;
        }
        return ans>=0?sgHours[ans]:Infinity;
      };

      const relicStart=firstScoreIndex(boundedRelic,desired-charScore-maxGearScore-maxSkillScore-maxFantoScore);
      let boundedBest=null;
"""
if old_setup not in s:
    raise SystemExit('v14 bounded setup anchor not found')
s=s.replace(old_setup,new_setup,1)

# Seed: use eager option properties and cached refined bit.
s=s.replace("const ro=boundedRelic[ri],sandRealm=sandFor(ro);","const ro=boundedRelic[ri],sandRealm=ro.__realmSandV7;",1)
s=s.replace("if(score>=desired&&refinedFunded(go)){\n              const oreRealm=oreFor(go),essenceRealm=essFor(so);","if(score>=desired&&go.__refinedFundedV11){\n              const oreRealm=go.__realmOreV7,essenceRealm=so.__realmEssenceV7;",1)

old_outer="""      const relicEnd=firstWorseIndex(boundedRelic,relicStart,ro=>jointHoursFast(0,0,ro.__acqSandV1,0));
      for(let ri=relicStart;ri<relicEnd;ri++){
        const ro=boundedRelic[ri];
        const sandRealm=sandFor(ro);
        const fantoStart=firstScoreIndex(boundedFanto,desired-charScore-ro.score-maxGearScore-maxSkillScore);
        const fantoEnd=firstWorseIndex(boundedFanto,fantoStart,fo=>jointHoursFast(0,0,ro.__acqSandV1,fo.__acqTreatV1));
        for(let fi=fantoStart;fi<fantoEnd;fi++){
          const fo=boundedFanto[fi];
          const fixedBeforeSkill=charScore+ro.score+fo.score;
          const skillStart=firstScoreIndex(boundedSkill,desired-fixedBeforeSkill-maxGearScore);
          if(skillStart>=boundedSkill.length) continue;
          const skillEnd=firstWorseIndex(boundedSkill,skillStart,so=>jointHoursFast(0,so.__acqEssenceV1,ro.__acqSandV1,fo.__acqTreatV1));
          if(skillStart>=skillEnd) continue;
"""
new_outer="""      const relicEnd=firstWorseIndex(boundedRelic,relicStart,ro=>jointHoursFast(0,0,ro.__acqSandV1,0));
      for(let ri=relicStart;ri<relicEnd;ri++){
        const ro=boundedRelic[ri];
        // boundedBest usually improves after relicEnd was computed. Sand-only acquisition is
        // monotone in Relic level, so a newly-worse Relic means every later Relic is also worse.
        if(noPaidRoutePossible&&boundedBest&&
           jointHoursFast(0,0,ro.__acqSandV1,0)>boundedBest.acquisitionHours+1e-9) break;
        const sandRealm=ro.__realmSandV7;
        const fantoStart=firstScoreIndex(boundedFanto,desired-charScore-ro.score-maxGearScore-maxSkillScore);
        const fantoEnd=firstWorseIndex(boundedFanto,fantoStart,fo=>jointHoursFast(0,0,ro.__acqSandV1,fo.__acqTreatV1));
        for(let fi=fantoStart;fi<fantoEnd;fi++){
          const fo=boundedFanto[fi];
          const rfLower=jointHoursFast(0,0,ro.__acqSandV1,fo.__acqTreatV1);
          // For fixed Relic, this lower bound is monotone in Fantomon cost. If the current
          // improved winner beats it, the remaining Fantomon suffix cannot recover.
          if(noPaidRoutePossible&&boundedBest&&rfLower>boundedBest.acquisitionHours+1e-9) break;
          const fixedBeforeSkill=charScore+ro.score+fo.score;
          const sgLower=sgSubsetLowerBound(desired-fixedBeforeSkill);
          if(noPaidRoutePossible&&boundedBest&&
             Math.max(rfLower,sgLower)>boundedBest.acquisitionHours+1e-9) continue;
          const skillStart=firstScoreIndex(boundedSkill,desired-fixedBeforeSkill-maxGearScore);
          if(skillStart>=boundedSkill.length) continue;
          const skillEnd=firstWorseIndex(boundedSkill,skillStart,so=>jointHoursFast(0,so.__acqEssenceV1,ro.__acqSandV1,fo.__acqTreatV1));
          if(skillStart>=skillEnd) continue;
"""
if old_outer not in s:
    raise SystemExit('v14 exact outer-loop anchor not found')
s=s.replace(old_outer,new_outer,1)

old_inner="""            const score=fixedBeforeSkill+so.score+go.score;
            if(score>=desired&&refinedFunded(go)){
              const oreRealm=oreFor(go),essenceRealm=essFor(so);
"""
new_inner="""            const score=fixedBeforeSkill+so.score+go.score;
            if(score>=desired&&go.__refinedFundedV11){
              const oreRealm=go.__realmOreV7,essenceRealm=so.__realmEssenceV7;
"""
if old_inner not in s:
    raise SystemExit('v14 exact inner-loop anchor not found')
s=s.replace(old_inner,new_inner,1)

p.write_text(s,encoding='utf-8')
print('Applied Primostar v14 eager Realm cache plus Gear/Skill subset lower-bound pruning.')
