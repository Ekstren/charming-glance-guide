from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

if 'SCARCITY_ADJUSTED_ACQUISITION_V1' in s:
    print('Scarcity-adjusted acquisition v1 already applied.')
    raise SystemExit(0)

old="""    const headroomCosts={
      essence:lastOptionCost(cats.skillOptions),
      sand:lastOptionCost(cats.relicOptions),
      treat:lastOptionCost(cats.fantoOptions)
    };"""
new="""    const headroomCosts={
      ore:Math.max(0,Number(gearOptions?.[gearOptions.length-1]?.oreCost)||0),
      essence:lastOptionCost(cats.skillOptions),
      sand:lastOptionCost(cats.relicOptions),
      treat:lastOptionCost(cats.fantoOptions)
    };"""
if old not in s: raise SystemExit('headroomCosts anchor not found')
s=s.replace(old,new,1)

old="""  /* SURPLUS_AWARE_OPTIMIZER_V2 · JOINT_REACQUISITION_V1 · DYNAMIC_HEADROOM_WEIGHTS_V1 · DYNAMIC_HEADROOM_WEIGHTS_V2
     Enabled S2 hard reserves are enforced after each S1 candidate plan. Reacquisition is
     solved jointly: Ore / Essence / Sand carts accrue simultaneously while one natural
     Stamina stream is optimally shared between map nodes. Capped-resource future value is
     now dynamic: if the current spendable raw + usable Realm-tool supply cannot fund the
     remaining safe-cap upgrades, that material stays near full value; once the reachable
     category is already comfortably funded, its value falls toward a deferred-use floor.
     Ore remains the 1.00 baseline because Gear has the broadest runway. */
  /* GATED_RAW_FIRST_OPTIMIZER_V2: once a capped category's remaining productive category headroom is fully funded by SAFE RAW, spending that raw on its own score progression has zero additional S1 opportunity cost. */
  const SURPLUS_ACQUISITION_FLOORS={ore:1.00,essence:0.00,sand:0.00,treat:0.00};"""
new="""  /* SCARCITY_ADJUSTED_ACQUISITION_V1
     Acquisition difficulty and projected scarcity are ONE economic metric, not competing
     ranking rules. Every score material is priced by replacement effort, then discounted
     continuously when projected usable supply comfortably covers remaining productive
     upgrade demand. Ore is no longer a permanent 1.00 exception. A 0.25 floor keeps large
     surpluses cheap-but-not-worthless; Treats retain the existing zero floor because they
     have no Realm-tool substitute and the exact funded-Treat fast path depends on it.
     Strict source tiers are unchanged: raw-only -> saved/planned tools -> extra purchases. */
  const SURPLUS_ACQUISITION_FLOORS={ore:0.25,essence:0.25,sand:0.25,treat:0.00};"""
if old not in s: raise SystemExit('surplus-floor anchor not found')
s=s.replace(old,new,1)

old="""  function rawOnlyAcquisitionSupply(key,resources,cfg=activeCalcConfig()){
    return Math.max(0,Number(resources?.[key])||0);
  }

  /* MARGINAL_HEADROOM_COST_V2"""
new="""  function rawOnlyAcquisitionSupply(key,resources,cfg=activeCalcConfig()){
    return Math.max(0,Number(resources?.[key])||0);
  }
  function plannedToolAcquisitionSupply(key,resources,cfg=activeCalcConfig()){
    if(key==='treat') return rawOnlyAcquisitionSupply(key,resources,cfg);
    const inv=realmInventoryFor(key,cfg);
    const perRun=Math.max(0,realmYieldFor(resources,key));
    return rawOnlyAcquisitionSupply(key,resources,cfg)+Math.max(0,Number(inv?.banked)||0)*perRun;
  }
  function acquisitionResourcesForRealms(resources,realms,cfg=activeCalcConfig()){
    const usesTools=(realms||[]).some(x=>{
      const planRuns=Number.isFinite(Number(x?.planRuns))?Number(x.planRuns):Number(x?.runsUsed)||0;
      return planRuns>0 || Math.max(0,Number(x?.packs)||0)>0 || Math.max(0,Number(x?.paidRunsUsed)||0)>0;
    });
    if(!usesTools) return resources;
    return {...resources,acquisitionSupplyEquiv:{
      ore:plannedToolAcquisitionSupply('ore',resources,cfg),
      essence:plannedToolAcquisitionSupply('essence',resources,cfg),
      sand:plannedToolAcquisitionSupply('sand',resources,cfg),
      treat:rawOnlyAcquisitionSupply('treat',resources,cfg)
    }};
  }

  /* MARGINAL_HEADROOM_COST_V2"""
if old not in s: raise SystemExit('raw supply helper anchor not found')
s=s.replace(old,new,1)

old="""    if(amountTotal<=0) return 0;
    if(key==='ore') return amountTotal;

    const floor="""
new="""    if(amountTotal<=0) return 0;

    const floor="""
if old not in s: raise SystemExit('ore bypass anchor not found')
s=s.replace(old,new,1)

old="""  /* REMOVE_ORE_PRESERVATION_V1
     Ore participates in the same acquisition-efficiency model as every other score
     resource. Realm/tool burden is now only a true-efficiency tie-breaker. */
  function marginalWeightedCosts(costs,resources,cfg=activeCalcConfig()){
    return {
      ore:Math.max(0,Number(costs?.ore)||0),
      essence:marginalWeightedSpend(costs?.essence,'essence',resources),"""
new="""  function marginalWeightedCosts(costs,resources,cfg=activeCalcConfig()){
    return {
      ore:marginalWeightedSpend(costs?.ore,'ore',resources),
      essence:marginalWeightedSpend(costs?.essence,'essence',resources),"""
if old not in s: raise SystemExit('marginalWeightedCosts anchor not found')
s=s.replace(old,new,1)

old="""    const acquisition=acquisitionResult||acquisitionEffortFor({ore:go.oreCost,essence:so.cost,sand:ro.cost,treat:fo.cost},resources,activeCalcConfig());"""
new="""    const acquisitionResources=acquisitionResourcesForRealms(resources,realms,activeCalcConfig());
    const realmStageForAcquisition=candidateRealmStage({realm:{ore:oreRealm,essence:essenceRealm,sand:sandRealm}});
    const acquisition=(realmStageForAcquisition===0&&acquisitionResult)
      ? acquisitionResult
      : acquisitionEffortFor({ore:go.oreCost,essence:so.cost,sand:ro.cost,treat:fo.cost},acquisitionResources,activeCalcConfig());"""
if old not in s: raise SystemExit('makePlanCandidate acquisition anchor not found')
s=s.replace(old,new,1)

old="""    resources.acquisitionSupplyEquiv={
      essence:rawOnlyAcquisitionSupply('essence',resources,cfg),
      sand:rawOnlyAcquisitionSupply('sand',resources,cfg),
      treat:rawOnlyAcquisitionSupply('treat',resources,cfg)
    };"""
new="""    resources.acquisitionSupplyEquiv={
      ore:rawOnlyAcquisitionSupply('ore',resources,cfg),
      essence:rawOnlyAcquisitionSupply('essence',resources,cfg),
      sand:rawOnlyAcquisitionSupply('sand',resources,cfg),
      treat:rawOnlyAcquisitionSupply('treat',resources,cfg)
    };"""
if old not in s: raise SystemExit('acquisitionSupplyEquiv anchor not found')
s=s.replace(old,new,1)

old="""    /* RAW_FUNDED_SEARCH_FAST_V1
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
      (Number(resources.treat)||0)>=Math.max(0,Number(headroomCosts?.treat)||0)-0.5;"""
new="""    /* RAW_FUNDED_SEARCH_FAST_V1 is intentionally disabled under
       SCARCITY_ADJUSTED_ACQUISITION_V1. Its dimensional collapse was exact only when fully
       funded non-Ore material had zero marginal value and Ore was always fixed at 1.00.
       With continuous nonzero scarcity floors, different Gear/Skill/Relic mixes retain
       different economic costs and must stay in the general exact search. */
    const nonOreRawFunded=false;"""
if old not in s: raise SystemExit('raw funded fast-path anchor not found')
s=s.replace(old,new,1)

old="""    for(const so of cats.skillOptions) so.__acqEssenceV1=marginalWeightedSpend(so.cost,'essence',resources);
    for(const ro of cats.relicOptions) ro.__acqSandV1=marginalWeightedSpend(ro.cost,'sand',resources);"""
new="""    for(const go of gearOptions) go.__acqOreV1=marginalWeightedSpend(go.oreCost,'ore',resources);
    for(const so of cats.skillOptions) so.__acqEssenceV1=marginalWeightedSpend(so.cost,'essence',resources);
    for(const ro of cats.relicOptions) ro.__acqSandV1=marginalWeightedSpend(ro.cost,'sand',resources);"""
if old not in s: raise SystemExit('acquisition precompute anchor not found')
s=s.replace(old,new,1)

old="""    const acquisitionFor=(go,so,ro,fo)=>({hours:jointHoursFast(go.oreCost,so.__acqEssenceV1,ro.__acqSandV1,fo.__acqTreatV1)});"""
new="""    const acquisitionFor=(go,so,ro,fo)=>({hours:jointHoursFast(go.__acqOreV1,so.__acqEssenceV1,ro.__acqSandV1,fo.__acqTreatV1)});"""
if old not in s: raise SystemExit('acquisitionFor anchor not found')
s=s.replace(old,new,1)

old="""Within each sourcing tier, Gear, individual Skills, individual Relics and individual Fantomons are balanced by marginal acquisition efficiency and the actual S2 upgrade-cost curves."""
new="""Within each sourcing tier, Gear, individual Skills, individual Relics and individual Fantomons are balanced by <b>scarcity-adjusted acquisition efficiency</b>: replacement difficulty is the base cost, then projected coverage makes abundant Ore/Hammers, Essence/Knuckles or Sand/Shovels cheaper to consume while nearly exhausted pools become more valuable. Surplus has a nonzero floor, so excess is cheap rather than literally worthless. Actual S2 upgrade-cost curves still determine every marginal step."""
if old not in s: raise SystemExit('method text anchor not found')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('Applied scarcity-adjusted acquisition v1.')
