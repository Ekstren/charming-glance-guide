from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

if 'MONOTONE_BOUND_BINARY_PRUNE_V2' in s:
    print('Primostar optimizer hot-loop v5 already applied.')
    raise SystemExit(0)

# 1) Treat-funded dimensional collapse is still exact when Refined Ore is tracked but
# the projected Refined pool already covers every reachable Gear option.
old="""    const treatFullyFunded=!resources.refinedTracked &&
      (Number(resources.treat)||0)>=Math.max(0,Number(headroomCosts?.treat)||0)-0.5;
"""
new="""    /* FULLY_FUNDED_TREAT_REFINED_V2
       Refined tracking only blocks the Treat-funded dimensional collapse when Refined Ore
       can actually constrain Gear. If the projected Refined pool covers the maximum reachable
       Gear option, the constraint is inactive and the same exact Relic x Skill collapse applies. */
    const maxReachableRefined=Math.max(0,Number(gearOptions[gearOptions.length-1]?.refinedCost)||0);
    const refinedFullyFunded=!resources.refinedTracked || (Number(resources.refined)||0)>=maxReachableRefined-0.5;
    const treatFullyFunded=refinedFullyFunded &&
      (Number(resources.treat)||0)>=Math.max(0,Number(headroomCosts?.treat)||0)-0.5;
"""
if old not in s:
    raise SystemExit('Treat-funded anchor not found')
s=s.replace(old,new,1)

# 2) Remove one closure allocation from every hot joint-hours evaluation. The math/order
# stays identical; only the helper lifetime changes from per-call to per-search.
old="""    const acqNodeOre=Math.max(0,Number(acqMap.ore)||0);
    const acqNodeEssence=Math.max(0,Number(acqMap.essence)||0);
    const acqNodeSand=Math.max(0,Number(acqMap.sand)||0);
    const jointHoursFast=(oreRaw,essRaw,sandRaw,treatRaw)=>{
"""
new="""    const acqNodeOre=Math.max(0,Number(acqMap.ore)||0);
    const acqNodeEssence=Math.max(0,Number(acqMap.essence)||0);
    const acqNodeSand=Math.max(0,Number(acqMap.sand)||0);
    /* JOINT_HOURS_NO_CLOSURE_V2
       This helper used to be allocated inside every jointHoursFast() call. Keeping it once
       per optimizer search removes hot-loop closure churn without changing arithmetic. */
    const nodesAtFast=(hours,ore,essence,sand)=>{
      let total=0,rem=0;
      rem=Math.max(0,ore-acqCartOre*hours);if(rem>0){if(acqNodeOre<=0)return Infinity;total+=rem/acqNodeOre;}
      rem=Math.max(0,essence-acqCartEssence*hours);if(rem>0){if(acqNodeEssence<=0)return Infinity;total+=rem/acqNodeEssence;}
      rem=Math.max(0,sand-acqCartSand*hours);if(rem>0){if(acqNodeSand<=0)return Infinity;total+=rem/acqNodeSand;}
      return total;
    };
    const jointHoursFast=(oreRaw,essRaw,sandRaw,treatRaw)=>{
"""
if old not in s:
    raise SystemExit('joint-hours helper insertion anchor not found')
s=s.replace(old,new,1)

old="""      const nodesAt=hours=>{
        let total=0,rem=0;
        rem=Math.max(0,ore-acqCartOre*hours);if(rem>0){if(acqNodeOre<=0)return Infinity;total+=rem/acqNodeOre;}
        rem=Math.max(0,essence-acqCartEssence*hours);if(rem>0){if(acqNodeEssence<=0)return Infinity;total+=rem/acqNodeEssence;}
        rem=Math.max(0,sand-acqCartSand*hours);if(rem>0){if(acqNodeSand<=0)return Infinity;total+=rem/acqNodeSand;}
        return total;
      };
      if(nodesAt(floor)<=floor+1e-9) return floor;
"""
new="""      if(nodesAtFast(floor,ore,essence,sand)<=floor+1e-9) return floor;
"""
if old not in s:
    raise SystemExit('per-call nodesAt closure anchor not found')
s=s.replace(old,new,1)
s=s.replace('if(nodesAt(hours)<=hours+1e-7) return hours;','if(nodesAtFast(hours,ore,essence,sand)<=hours+1e-7) return hours;',1)
s=s.replace('while(nodesAt(hi)>hi+1e-9&&hi<1e9) hi*=2;','while(nodesAtFast(hi,ore,essence,sand)>hi+1e-9&&hi<1e9) hi*=2;',1)
s=s.replace('if(hi>=1e9&&nodesAt(hi)>hi+1e-9) return 1e9;','if(hi>=1e9&&nodesAtFast(hi,ore,essence,sand)>hi+1e-9) return 1e9;',1)
s=s.replace('if(nodesAt(mid)<=mid) hi=mid; else lo=mid;','if(nodesAtFast(mid,ore,essence,sand)<=mid) hi=mid; else lo=mid;',1)

# 3) The acquisition lower-bound inputs are monotone by Relic/Fantomon/Skill option index.
# Replace a lower-bound solve on every loop iteration with binary-searched end indices.
old="""      /* ACQUISITION_LOWER_BOUND_PRUNE_V1
         jointHoursFast() is monotone in every resource demand. Therefore a branch's
         acquisition time with one or more remaining categories set to ZERO is a strict
         lower bound on every real plan in that branch. Once that optimistic bound is
         already worse than the best exact candidate, the whole monotone suffix can be
         skipped without changing the winner. */
      const effortWorseThanBest=hours=>boundedBest && hours>boundedBest.acquisitionHours+1e-9;

      for(let ri=relicStart;ri<boundedRelic.length;ri++){
        const ro=boundedRelic[ri];
        if(effortWorseThanBest(jointHoursFast(0,0,ro.__acqSandV1,0))) break;
        const sandRealm=sandFor(ro);
        const fantoStart=firstScoreIndex(boundedFanto,desired-charScore-ro.score-maxGearScore-maxSkillScore);
        for(let fi=fantoStart;fi<boundedFanto.length;fi++){
          const fo=boundedFanto[fi];
          if(effortWorseThanBest(jointHoursFast(0,0,ro.__acqSandV1,fo.__acqTreatV1))) break;
          const fixedBeforeSkill=charScore+ro.score+fo.score;
          const skillStart=firstScoreIndex(boundedSkill,desired-fixedBeforeSkill-maxGearScore);
          if(skillStart>=boundedSkill.length) continue;
          let lastGearAdds=null;

          for(let si=skillStart;si<boundedSkill.length;si++){
            const so=boundedSkill[si];
            if(effortWorseThanBest(jointHoursFast(0,so.__acqEssenceV1,ro.__acqSandV1,fo.__acqTreatV1))) break;
            const fixedScore=fixedBeforeSkill+so.score;
"""
new="""      /* ACQUISITION_LOWER_BOUND_PRUNE_V1 · MONOTONE_BOUND_BINARY_PRUNE_V2
         jointHoursFast() is monotone in every resource demand. Instead of evaluating the
         same lower-bound equation once for every Relic/Fantomon/Skill iteration, binary-search
         the first option that is already worse than the current exact seed. This preserves the
         identical candidate set: only a monotone suffix that the old loop would immediately
         break on is skipped. A later/improved best can only make these precomputed ends loose,
         never incorrectly exclude a winner. */
      const firstWorseIndex=(options,start,hoursFor)=>{
        if(!boundedBest) return options.length;
        const limit=boundedBest.acquisitionHours+1e-9;
        let lo=Math.max(0,start),hi=options.length-1,ans=options.length;
        while(lo<=hi){
          const mid=(lo+hi)>>1;
          if(hoursFor(options[mid])>limit){ans=mid;hi=mid-1;}else lo=mid+1;
        }
        return ans;
      };

      const relicEnd=firstWorseIndex(boundedRelic,relicStart,ro=>jointHoursFast(0,0,ro.__acqSandV1,0));
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
          let lastGearAdds=null;

          for(let si=skillStart;si<skillEnd;si++){
            const so=boundedSkill[si];
            const fixedScore=fixedBeforeSkill+so.score;
"""
if old not in s:
    raise SystemExit('bounded acquisition-prune loop anchor not found')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('Applied Primostar optimizer hot-loop v5: funded Refined collapse, closure-free acquisition kernel, monotone binary pruning.')
