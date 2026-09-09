from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

MARKER='BOUNDED_EAGER_REALM_V12'
if MARKER in s:
    print('Primostar v15 eager bounded cache already applied.')
    raise SystemExit(0)
if 'SKILL_GEAR_TWO_POINTER_V10' not in s or 'JOINT_HOURS_ACTIVE_SET_V9' not in s:
    raise SystemExit('Expected v13/v12 optimizer markers not found')
if 'SG_SUBSET_LOWER_BOUND_V11' in s:
    raise SystemExit('Rejected v14 subset-table experiment is present; refusing to stack v15')

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

      /* BOUNDED_EAGER_REALM_V12
         The exact bounded scan revisits the same Gear/Skill/Relic options thousands of times.
         Materialize each immutable Realm result once for this search snapshot and store the
         refined-funding bit on Gear. The hot loops then use direct property reads instead of
         repeatedly entering oreFor()/essFor()/sandFor()/refinedFunded() wrappers. */
      for(const go of boundedGear){ go.__realmOreV7=oreFor(go); go.__refinedFundedV12=refinedFunded(go); }
      for(const so of boundedSkill) so.__realmEssenceV7=essFor(so);
      for(const ro of boundedRelic) ro.__realmSandV7=sandFor(ro);

      const relicStart=firstScoreIndex(boundedRelic,desired-charScore-maxGearScore-maxSkillScore-maxFantoScore);
      let boundedBest=null;
"""
if old_setup not in s:
    raise SystemExit('v15 bounded setup anchor not found')
s=s.replace(old_setup,new_setup,1)

# Coarse seed uses direct cached reads.
s=s.replace("const ro=boundedRelic[ri],sandRealm=sandFor(ro);","const ro=boundedRelic[ri],sandRealm=ro.__realmSandV7;",1)
s=s.replace("if(score>=desired&&refinedFunded(go)){\n              const oreRealm=oreFor(go),essenceRealm=essFor(so);","if(score>=desired&&go.__refinedFundedV12){\n              const oreRealm=go.__realmOreV7,essenceRealm=so.__realmEssenceV7;",1)

old_outer="""      const relicEnd=firstWorseIndex(boundedRelic,relicStart,ro=>jointHoursFast(0,0,ro.__acqSandV1,0));
      for(let ri=relicStart;ri<relicEnd;ri++){
        const ro=boundedRelic[ri];
        const sandRealm=sandFor(ro);
        const fantoStart=firstScoreIndex(boundedFanto,desired-charScore-ro.score-maxGearScore-maxSkillScore);
        const fantoEnd=firstWorseIndex(boundedFanto,fantoStart,fo=>jointHoursFast(0,0,ro.__acqSandV1,fo.__acqTreatV1));
        for(let fi=fantoStart;fi<fantoEnd;fi++){
          const fo=boundedFanto[fi];
          const fixedBeforeSkill=charScore+ro.score+fo.score;
"""
new_outer="""      const relicEnd=firstWorseIndex(boundedRelic,relicStart,ro=>jointHoursFast(0,0,ro.__acqSandV1,0));
      for(let ri=relicStart;ri<relicEnd;ri++){
        const ro=boundedRelic[ri];
        /* DYNAMIC_OUTER_BOUND_V12
           relicEnd/fantoEnd are based on the seed winner. If the exact scan finds a faster
           winner, refresh the cheap monotone subset bound inline so we can stop the now-dead
           Relic/Fantomon suffix immediately. */
        if(noPaidRoutePossible&&boundedBest&&
           jointHoursFast(0,0,ro.__acqSandV1,0)>boundedBest.acquisitionHours+1e-9) break;
        const sandRealm=ro.__realmSandV7;
        const fantoStart=firstScoreIndex(boundedFanto,desired-charScore-ro.score-maxGearScore-maxSkillScore);
        const fantoEnd=firstWorseIndex(boundedFanto,fantoStart,fo=>jointHoursFast(0,0,ro.__acqSandV1,fo.__acqTreatV1));
        for(let fi=fantoStart;fi<fantoEnd;fi++){
          const fo=boundedFanto[fi];
          if(noPaidRoutePossible&&boundedBest&&
             jointHoursFast(0,0,ro.__acqSandV1,fo.__acqTreatV1)>boundedBest.acquisitionHours+1e-9) break;
          const fixedBeforeSkill=charScore+ro.score+fo.score;
"""
if old_outer not in s:
    raise SystemExit('v15 exact outer-loop anchor not found')
s=s.replace(old_outer,new_outer,1)

old_inner="""            const score=fixedBeforeSkill+so.score+go.score;
            if(score>=desired&&refinedFunded(go)){
              const oreRealm=oreFor(go),essenceRealm=essFor(so);
"""
new_inner="""            const score=fixedBeforeSkill+so.score+go.score;
            if(score>=desired&&go.__refinedFundedV12){
              const oreRealm=go.__realmOreV7,essenceRealm=so.__realmEssenceV7;
"""
if old_inner not in s:
    raise SystemExit('v15 exact inner-loop anchor not found')
s=s.replace(old_inner,new_inner,1)

p.write_text(s,encoding='utf-8')
print('Applied Primostar v15 eager bounded Realm/refined cache and dynamic outer bounds.')
