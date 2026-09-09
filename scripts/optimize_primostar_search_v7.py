from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

if 'SKILL_GEAR_BREAKPOINT_JUMP_V4' in s:
    print('Primostar skill/gear breakpoint optimizer already applied.')
    raise SystemExit(0)

# The bounded optimizer already evaluates only the FIRST Skill state that maps to each
# minimum required Gear state. It still reached those states by linearly walking every
# intervening Skill option and discarding duplicates. Skill score rises monotonically and
# minimum required Gear falls monotonically, so we can jump directly to the next exact
# Skill/Gear breakpoint with the existing binary-search helper.

old_seed="""          let lastGearAdds=null;
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
"""
new_seed="""          /* SKILL_GEAR_BREAKPOINT_JUMP_V4
             The old seed loop incremented through every Skill option, but after the first
             option selecting a given minimum Gear state it discarded every later Skill
             option selecting that same Gear state. Jump straight to the first Skill score
             at which the previous Gear option can satisfy the target. This visits the exact
             same candidate frontier in the exact same order. */
          for(let si=skillStart;si<boundedSkill.length;){
            const so=boundedSkill[si];
            const go=gearLocked
              ? (boundedGear[0].score>=Math.max(0,desired-fixedBeforeSkill-so.score)?boundedGear[0]:null)
              : firstGearOptionAtLeast(boundedGear,Math.max(0,desired-fixedBeforeSkill-so.score));
            if(!go){ si++; continue; }

            let nextSi=si+1;
            if(go.adds===0){
              nextSi=boundedSkill.length;
            }else{
              // buildGearOptions() appends exactly one level per option, so adds === index.
              const previousGear=boundedGear[Math.max(0,go.adds-1)];
              if(previousGear){
                nextSi=Math.max(nextSi,firstScoreIndex(
                  boundedSkill,
                  desired-fixedBeforeSkill-(Number(previousGear.score)||0)
                ));
              }
            }

            const score=fixedBeforeSkill+so.score+go.score;
            if(score>=desired&&refinedFunded(go)){
              const oreRealm=oreFor(go),essenceRealm=essFor(so);
              if(oreRealm.feasible&&essenceRealm.feasible&&sandRealm.feasible){
                const acquisition=acquisitionFor(go,so,ro,fo);
                const candidate=makePlanCandidate(go,so,ro,fo,score,desired,resources,[oreRealm,essenceRealm,sandRealm],acquisition);
                candidate.realm.days=realmDays;
                candidate.realmFeasible=true;
                if(betterFeasibleCandidate(candidate,boundedBest)) boundedBest=candidate;
              }
            }
            if(go.adds===0) break;
            si=nextSi;
          }
"""
if old_seed not in s:
    raise SystemExit('coarse exact seed Skill loop anchor not found')
s=s.replace(old_seed,new_seed,1)

old_exact="""          if(skillStart>=skillEnd) continue;
          let lastGearAdds=null;

          for(let si=skillStart;si<skillEnd;si++){
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
"""
new_exact="""          if(skillStart>=skillEnd) continue;

          /* SKILL_GEAR_BREAKPOINT_JUMP_V4
             For fixed Relic+Fantomon, Skill rises monotonically while the minimum Gear
             required falls monotonically. The previous loop already rejected every Skill
             option after the first one for each Gear step. Instead of walking those rejected
             states one-by-one, binary-search the first Skill option where the NEXT lower
             Gear step becomes sufficient. Candidate order and comparator inputs are unchanged. */
          for(let si=skillStart;si<skillEnd;){
            const so=boundedSkill[si];
            const fixedScore=fixedBeforeSkill+so.score;
            const needGear=Math.max(0,desired-fixedScore);
            const go=gearLocked
              ? (boundedGear[0].score>=needGear?boundedGear[0]:null)
              : firstGearOptionAtLeast(boundedGear,needGear);
            if(!go){ si++; continue; }

            let nextSi=si+1;
            if(go.adds===0){
              nextSi=skillEnd;
            }else{
              // buildGearOptions() guarantees one sequential adds value per array index.
              const previousGear=boundedGear[Math.max(0,go.adds-1)];
              if(previousGear){
                nextSi=Math.max(nextSi,firstScoreIndex(
                  boundedSkill,
                  desired-fixedBeforeSkill-(Number(previousGear.score)||0)
                ));
              }
            }

            const score=fixedScore+go.score;
            if(score>=desired&&refinedFunded(go)){
              const oreRealm=oreFor(go),essenceRealm=essFor(so);
              if(oreRealm.feasible&&essenceRealm.feasible&&sandRealm.feasible){
                // Same exact dominance rule used by the legacy full scan, but before the
                // expensive joint acquisition equation.
                const dominated=boundedBest && go.oreCost>=boundedBest.oreCost &&
                  so.cost>=boundedBest.essenceCost && ro.cost>=boundedBest.sandCost &&
                  fo.cost>=boundedBest.treatCost && go.refinedCost>=boundedBest.refinedCost;
                if(!dominated){
                  const acquisition=acquisitionFor(go,so,ro,fo);
                  const candidate=makePlanCandidate(go,so,ro,fo,score,desired,resources,[oreRealm,essenceRealm,sandRealm],acquisition);
                  candidate.realm.days=realmDays;
                  candidate.realmFeasible=true;
                  if(betterFeasibleCandidate(candidate,boundedBest)) boundedBest=candidate;
                }
              }
            }
            if(go.adds===0) break;
            si=nextSi;
          }
"""
if old_exact not in s:
    raise SystemExit('bounded exact Skill loop anchor not found')
s=s.replace(old_exact,new_exact,1)

p.write_text(s,encoding='utf-8')
print('Applied Primostar v7 exact Skill/Gear breakpoint jumps to seed and bounded scans.')
