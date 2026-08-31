from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
MARK='TREAT_FUNDED_SEARCH_FAST_V1'
if MARK in s:
    print('Treat-funded optimizer fast path already applied')
    raise SystemExit(0)

anchor='''    const oreCache=new Map(),essCache=new Map(),sandCache=new Map();
    const oreFor=go=>{const k=go.oreCost;if(!oreCache.has(k))oreCache.set(k,realmTopupFor('ore',k,resources.ore,resources,cfg,p));return oreCache.get(k);};
    const essFor=so=>{const k=so.cost;if(!essCache.has(k))essCache.set(k,realmTopupFor('essence',k,resources.essence,resources,cfg,p));return essCache.get(k);};
    const sandFor=ro=>{const k=ro.cost;if(!sandCache.has(k))sandCache.set(k,realmTopupFor('sand',k,resources.sand,resources,cfg,p));return sandCache.get(k);};
    const acquisitionFor=(go,so,ro,fo)=>acquisitionEffortFor(
      {ore:go.oreCost,essence:so.cost,sand:ro.cost,treat:fo.cost},resources,cfg
    );
    let best=null,bestDiagnostic=null;

'''
if anchor not in s:
    raise SystemExit('searchPlans cache anchor not found')

insert=anchor+r'''    /* TREAT_FUNDED_SEARCH_FAST_V1
       Exact dimensional collapse when raw Treats already fund every reachable Fantomon
       upgrade. In that state the configured fully-funded Treat acquisition floor is zero,
       so Fantomon score is free in the PRIMARY acquisition metric.

       For each Skill+Relic choice, the best acquisition route therefore uses enough free
       Fantomon score to force Gear to its lowest possible option. Once that Gear option is
       fixed, extra Fantomon upgrades cannot improve acquisition and only worsen/equal the
       normal overscore/share tie-breaks, so select the first Fantomon option that reaches
       target. This replaces Relic x Fantomon x Skill with Relic x Skill while preserving
       the exact candidate comparator. */
    const treatFullyFunded=!resources.refinedTracked &&
      (Number(resources.treat)||0)>=Math.max(0,Number(headroomCosts?.treat)||0)-0.5;
    if(treatFullyFunded && cats.fantoOptions.length>1){
      const fantoMax=cats.fantoOptions[cats.fantoOptions.length-1];
      const firstFantoAtLeast=scoreNeeded=>{
        let lo=0,hi=cats.fantoOptions.length-1,ans=null;
        while(lo<=hi){
          const mid=(lo+hi)>>1;
          if(cats.fantoOptions[mid].score>=scoreNeeded){ans=cats.fantoOptions[mid];hi=mid-1;}else lo=mid+1;
        }
        return ans;
      };
      let fastBest=null,fastDiagnostic=null;
      for(const ro of cats.relicOptions){
        const sandRealm=sandFor(ro);
        for(const so of cats.skillOptions){
          const fixedScore=charScore+ro.score+so.score;
          const go=gearLocked
            ? (gearOptions[0].score+fantoMax.score>=Math.max(0,desired-fixedScore)?gearOptions[0]:null)
            : firstGearOptionAtLeast(gearOptions,Math.max(0,desired-fixedScore-fantoMax.score));
          if(!go) continue;
          const neededFanto=Math.max(0,desired-fixedScore-go.score);
          const fo=firstFantoAtLeast(neededFanto);
          if(!fo) continue;
          const score=fixedScore+go.score+fo.score;
          if(score<desired) continue;

          const oreRealm=oreFor(go),essenceRealm=essFor(so);
          const refinedShortfall=0;
          const hardShortfall=0;
          const realms=[oreRealm,essenceRealm,sandRealm];
          const realmOverflow=realms.reduce((sum,x)=>sum+Math.max(0,(Number.isFinite(x.packs)?x.packs:1e9)-(x.maxPacks||0)),0);
          const remainingAfterMax=realms.reduce((sum,x)=>sum+Math.max(0,x.remainingAfterMax||0),0);
          const realmPacks=realms.reduce((sum,x)=>sum+(Number.isFinite(x.packs)?x.packs:1e9),0);
          const allFeasible=realms.every(x=>x.feasible);
          const dawniumCost=allFeasible?realms.reduce((sum,x)=>sum+x.dawnium,0):Infinity;
          const unknownPriceRefreshes=realms.reduce((sum,x)=>sum+Math.max(0,Number(x?.unknownPriceRefreshes)||0),0);
          const acquisition=acquisitionFor(go,so,ro,fo);

          if(allFeasible){
            const candidate=makePlanCandidate(go,so,ro,fo,score,desired,resources,realms,acquisition);
            candidate.realm.days=realmDays;
            candidate.realmFeasible=true;
            if(betterFeasibleCandidate(candidate,fastBest)) fastBest=candidate;
            continue;
          }

          const treatShortfall=0;
          const diagOreShare=resources.ore>0?go.oreCost/resources.ore:(go.oreCost>0?go.oreCost/100000:0);
          const diagEssenceShare=resources.essence>0?so.cost/resources.essence:(so.cost>0?so.cost/100000:0);
          const diagSandShare=resources.sand>0?ro.cost/resources.sand:(ro.cost>0?ro.cost/100000:0);
          const diagTreatShare=resources.treat>0?fo.cost/resources.treat:0;
          const diagnostic={gear:go.target,skill:so.avg,relic:ro.avg,fanto:fo.avg,skillLevels:so.levels,relicLevels:ro.levels,fantoLevels:fo.levels,oreCost:go.oreCost,essenceCost:so.cost,sandCost:ro.cost,treatCost:fo.cost,refinedCost:go.refinedCost,score,gearAdds:go.adds,skillAdds:so.adds,relicAdds:ro.adds,fantoAdds:fo.adds,overshoot:score-desired,dawniumCost,realmAttempts:realmPacks,realmPacks,oreShare:diagOreShare,essenceShare:diagEssenceShare,sandShare:diagSandShare,treatShare:diagTreatShare,acquisitionHours:acquisition.hours,unknownPriceRefreshes,bankedHammersUsed:(oreRealm.bankedUsed||0),bankedKnucklesUsed:(essenceRealm.bankedUsed||0),bankedShovelsUsed:(sandRealm.bankedUsed||0),bankedToolsUsed:(oreRealm.bankedUsed||0)+(essenceRealm.bankedUsed||0)+(sandRealm.bankedUsed||0),realmOverflow,remainingAfterMax,treatShortfall,refinedShortfall,hardShortfall,seasonKey:cfg.key,realmFeasible:false,realm:{days:realmDays,ore:oreRealm,essence:essenceRealm,sand:sandRealm}};
          if(betterDiagnosticCandidate(diagnostic,fastDiagnostic)) fastDiagnostic=diagnostic;
        }
      }
      if(fastBest) return {plan:fastBest,diagnostic:fastBest};
      if(fastDiagnostic) return {plan:null,diagnostic:fastDiagnostic};
    }

'''
s=s.replace(anchor,insert,1)
p.write_text(s,encoding='utf-8')
print('added exact Treat-funded search dimensional collapse')
