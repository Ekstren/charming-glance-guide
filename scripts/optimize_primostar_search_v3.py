from pathlib import Path

path=Path('index.html')
s=path.read_text(encoding='utf-8')

old="""      for(let ri=relicStart;ri<boundedRelic.length;ri++){
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
"""
new="""      /* ACQUISITION_LOWER_BOUND_PRUNE_V1
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

count=s.count(old)
if count!=1:
    raise SystemExit(f'expected one bounded-loop block, found {count}')
s=s.replace(old,new,1)
path.write_text(s,encoding='utf-8')
print('Added exact acquisition lower-bound branch pruning to Primostar optimizer.')
