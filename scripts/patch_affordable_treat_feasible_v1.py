from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
MARK='AFFORDABLE_TREAT_FEASIBLE_V1'
if MARK in s:
    print('affordable-Treat feasible presearch already applied')
    raise SystemExit(0)

anchor='''      if(fastBest) return {plan:fastBest,diagnostic:fastBest};
      if(fastDiagnostic) return {plan:null,diagnostic:fastDiagnostic};
    }

    for(const ro of cats.relicOptions){
'''
if anchor not in s:
    raise SystemExit('Treat fast-path/general-loop boundary not found')

insert=r'''      if(fastBest) return {plan:fastBest,diagnostic:fastBest};
      if(fastDiagnostic) return {plan:null,diagnostic:fastDiagnostic};
    }

    /* AFFORDABLE_TREAT_FEASIBLE_V1
       Treats have no Material-Realm top-up path. Any actually FUNDABLE plan must therefore
       choose a Fantomon option whose Treat cost is already covered by projected Treat
       inventory. When that affordable slice is much smaller than the full Fantomon search
       range, do a cheap feasible-only pass first. If it finds a plan, every excluded
       Fantomon option is provably infeasible and the expensive diagnostic scan is unnecessary.
       If it finds nothing, fall through to the complete scan so shortfall diagnostics remain exact. */
    const affordableFantoOptions=cats.fantoOptions.filter(fo=>fo.cost<=(Number(resources.treat)||0)+0.5);
    if(affordableFantoOptions.length>0 && affordableFantoOptions.length*1.25<cats.fantoOptions.length){
      let affordableBest=null;
      for(const ro of cats.relicOptions){
        const sandRealm=sandFor(ro);
        for(const fo of affordableFantoOptions){
          const fixedBeforeSkill=charScore+ro.score+fo.score;
          let lastGearAdds=null;
          for(const so of cats.skillOptions){
            const fixedScore=fixedBeforeSkill+so.score;
            const go=gearLocked?(gearOptions[0].score>=Math.max(0,desired-fixedScore)?gearOptions[0]:null):firstGearOptionAtLeast(gearOptions,Math.max(0,desired-fixedScore));
            if(!go) continue;
            if(lastGearAdds===go.adds) continue;
            lastGearAdds=go.adds;
            const score=fixedScore+go.score;
            if(score<desired) continue;
            const refinedShortfall=resources.refinedTracked?Math.max(0,go.refinedCost-resources.refined):0;
            if(refinedShortfall>0.5) continue;
            const oreRealm=oreFor(go),essenceRealm=essFor(so);
            const realms=[oreRealm,essenceRealm,sandRealm];
            if(!realms.every(x=>x.feasible)) continue;
            if(affordableBest && go.oreCost>=affordableBest.oreCost && so.cost>=affordableBest.essenceCost && ro.cost>=affordableBest.sandCost && fo.cost>=affordableBest.treatCost && go.refinedCost>=affordableBest.refinedCost) continue;
            const acquisition=acquisitionFor(go,so,ro,fo);
            const candidate=makePlanCandidate(go,so,ro,fo,score,desired,resources,realms,acquisition);
            candidate.realm.days=realmDays;
            candidate.realmFeasible=true;
            if(betterFeasibleCandidate(candidate,affordableBest)) affordableBest=candidate;
          }
        }
      }
      if(affordableBest) return {plan:affordableBest,diagnostic:affordableBest};
    }

    for(const ro of cats.relicOptions){
'''
s=s.replace(anchor,insert,1)
p.write_text(s,encoding='utf-8')
print('added exact affordable-Treat feasible presearch')
