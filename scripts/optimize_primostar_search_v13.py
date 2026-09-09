from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

MARKER='SKILL_GEAR_TWO_POINTER_V10'
if MARKER in s:
    print('Primostar v13 two-pointer frontier already applied.')
    raise SystemExit(0)
if 'JOINT_HOURS_ACTIVE_SET_V9' not in s or 'ACQUISITION_LIMIT_PRECHECK_V8' not in s:
    raise SystemExit('Expected v12 optimizer markers not found')
if 'SKILL_GEAR_BREAKPOINT_JUMP_V4' in s:
    raise SystemExit('Rejected binary-search breakpoint jump is present; refusing to stack v13')

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
            if(noPaidRoutePossible&&boundedBest&&acquisitionCannotBeat(boundedBest.acquisitionHours,go,so,ro,fo)) continue;
            const acquisition=acquisitionFor(go,so,ro,fo);
            /* NO_PAID_PRIMARY_FAST_COMPARE_V5 · ACQUISITION_LIMIT_PRECHECK_V8
               The cheap current-winner feasibility test above rejects obvious losers before
               the full joint solve; this exact comparison remains the final numeric guard. */
            if(noPaidRoutePossible&&boundedBest&&acquisition.hours>boundedBest.acquisitionHours+1e-9) continue;
            const candidate=makePlanCandidate(go,so,ro,fo,score,desired,resources,[oreRealm,essenceRealm,sandRealm],acquisition);
            candidate.realm.days=realmDays;
            candidate.realmFeasible=true;
            if(noPaidRoutePossible&&boundedBest&&acquisition.hours<boundedBest.acquisitionHours-1e-9){
              boundedBest=candidate;
            }else if(betterFeasibleCandidate(candidate,boundedBest)) boundedBest=candidate;
          }
"""
new_seed="""          /* SKILL_GEAR_TWO_POINTER_V10
             The old loop walked every Skill option and binary-searched Gear each time, then
             discarded all but the FIRST Skill state mapping to each minimum Gear step. Keep
             that exact candidate frontier/order, but walk it with monotone Skill/Gear cursors:
             one Gear binary search to enter the frontier, then a linear scan only until the
             next lower Gear step becomes sufficient. No per-Skill Gear binary searches. */
          let si=skillStart;
          let gi=gearLocked?0:firstScoreIndex(boundedGear,desired-fixedBeforeSkill-boundedSkill[si].score);
          while(si<boundedSkill.length&&gi<boundedGear.length){
            const so=boundedSkill[si],go=boundedGear[gi];
            const score=fixedBeforeSkill+so.score+go.score;
            if(score>=desired&&refinedFunded(go)){
              const oreRealm=oreFor(go),essenceRealm=essFor(so);
              if(oreRealm.feasible&&essenceRealm.feasible&&sandRealm.feasible &&
                 !(noPaidRoutePossible&&boundedBest&&acquisitionCannotBeat(boundedBest.acquisitionHours,go,so,ro,fo))){
                const acquisition=acquisitionFor(go,so,ro,fo);
                if(!(noPaidRoutePossible&&boundedBest&&acquisition.hours>boundedBest.acquisitionHours+1e-9)){
                  const candidate=makePlanCandidate(go,so,ro,fo,score,desired,resources,[oreRealm,essenceRealm,sandRealm],acquisition);
                  candidate.realm.days=realmDays;
                  candidate.realmFeasible=true;
                  if(noPaidRoutePossible&&boundedBest&&acquisition.hours<boundedBest.acquisitionHours-1e-9){
                    boundedBest=candidate;
                  }else if(betterFeasibleCandidate(candidate,boundedBest)) boundedBest=candidate;
                }
              }
            }
            if(gearLocked||gi===0) break;
            const nextGearScore=Number(boundedGear[gi-1]?.score)||0;
            do{si++;}while(si<boundedSkill.length &&
              fixedBeforeSkill+(Number(boundedSkill[si]?.score)||0)+nextGearScore<desired-1e-9);
            if(si>=boundedSkill.length) break;
            const need=desired-fixedBeforeSkill-(Number(boundedSkill[si]?.score)||0);
            while(gi>0&&(Number(boundedGear[gi-1]?.score)||0)>=need-1e-9) gi--;
          }
"""
if old_seed not in s:
    raise SystemExit('v13 coarse seed anchor not found')
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

            if(noPaidRoutePossible&&boundedBest&&acquisitionCannotBeat(boundedBest.acquisitionHours,go,so,ro,fo)) continue;
            const acquisition=acquisitionFor(go,so,ro,fo);
            /* NO_PAID_PRIMARY_FAST_COMPARE_V5 · ACQUISITION_LIMIT_PRECHECK_V8
               The cheap current-winner feasibility test above rejects obvious losers before
               the full joint solve; this exact comparison remains the final numeric guard. */
            if(noPaidRoutePossible&&boundedBest&&acquisition.hours>boundedBest.acquisitionHours+1e-9) continue;
            const candidate=makePlanCandidate(go,so,ro,fo,score,desired,resources,[oreRealm,essenceRealm,sandRealm],acquisition);
            candidate.realm.days=realmDays;
            candidate.realmFeasible=true;
            if(noPaidRoutePossible&&boundedBest&&acquisition.hours<boundedBest.acquisitionHours-1e-9){
              boundedBest=candidate;
            }else if(betterFeasibleCandidate(candidate,boundedBest)) boundedBest=candidate;
          }
"""
new_exact="""          if(skillStart>=skillEnd) continue;

          /* SKILL_GEAR_TWO_POINTER_V10
             Same exact frontier as the legacy duplicate-skip loop, but without a Gear binary
             search for every skipped Skill state. Skill only rises and required Gear only
             falls, so a pair of monotone cursors visits the first Skill state of each Gear
             step in identical order. */
          let si=skillStart;
          let gi=gearLocked?0:firstScoreIndex(boundedGear,desired-fixedBeforeSkill-boundedSkill[si].score);
          while(si<skillEnd&&gi<boundedGear.length){
            const so=boundedSkill[si],go=boundedGear[gi];
            const score=fixedBeforeSkill+so.score+go.score;
            if(score>=desired&&refinedFunded(go)){
              const oreRealm=oreFor(go),essenceRealm=essFor(so);
              if(oreRealm.feasible&&essenceRealm.feasible&&sandRealm.feasible){
                const dominated=boundedBest && go.oreCost>=boundedBest.oreCost &&
                  so.cost>=boundedBest.essenceCost && ro.cost>=boundedBest.sandCost &&
                  fo.cost>=boundedBest.treatCost && go.refinedCost>=boundedBest.refinedCost;
                if(!dominated &&
                   !(noPaidRoutePossible&&boundedBest&&acquisitionCannotBeat(boundedBest.acquisitionHours,go,so,ro,fo))){
                  const acquisition=acquisitionFor(go,so,ro,fo);
                  if(!(noPaidRoutePossible&&boundedBest&&acquisition.hours>boundedBest.acquisitionHours+1e-9)){
                    const candidate=makePlanCandidate(go,so,ro,fo,score,desired,resources,[oreRealm,essenceRealm,sandRealm],acquisition);
                    candidate.realm.days=realmDays;
                    candidate.realmFeasible=true;
                    if(noPaidRoutePossible&&boundedBest&&acquisition.hours<boundedBest.acquisitionHours-1e-9){
                      boundedBest=candidate;
                    }else if(betterFeasibleCandidate(candidate,boundedBest)) boundedBest=candidate;
                  }
                }
              }
            }
            if(gearLocked||gi===0) break;
            const nextGearScore=Number(boundedGear[gi-1]?.score)||0;
            do{si++;}while(si<skillEnd &&
              fixedBeforeSkill+(Number(boundedSkill[si]?.score)||0)+nextGearScore<desired-1e-9);
            if(si>=skillEnd) break;
            const need=desired-fixedBeforeSkill-(Number(boundedSkill[si]?.score)||0);
            while(gi>0&&(Number(boundedGear[gi-1]?.score)||0)>=need-1e-9) gi--;
          }
"""
if old_exact not in s:
    raise SystemExit('v13 bounded exact anchor not found')
s=s.replace(old_exact,new_exact,1)

p.write_text(s,encoding='utf-8')
print('Applied Primostar v13 monotone Skill/Gear two-pointer frontier.')
