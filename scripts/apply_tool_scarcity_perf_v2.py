from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

if 'TOOL_SCARCITY_CREDIT_V2' in s:
    print('Tool scarcity/performance v2 already applied.')
    raise SystemExit(0)

old="""  /* SCARCITY_ADJUSTED_ACQUISITION_V1
     Acquisition difficulty and projected scarcity are ONE economic metric, not competing
     ranking rules. Every score material is priced by replacement effort, then discounted
     continuously when projected usable supply comfortably covers remaining productive
     upgrade demand. Ore is no longer a permanent 1.00 exception. A 0.25 floor keeps large
     surpluses cheap-but-not-worthless; Treats retain the existing zero floor because they
     have no Realm-tool substitute and the exact funded-Treat fast path depends on it.
     Strict source tiers are unchanged: raw-only -> saved/planned tools -> extra purchases. */
  const SURPLUS_ACQUISITION_FLOORS={ore:0.25,essence:0.25,sand:0.25,treat:0.00};"""
new="""  /* SCARCITY_ADJUSTED_ACQUISITION_V1 · TOOL_SCARCITY_CREDIT_V2
     Acquisition difficulty and projected scarcity are ONE economic metric, not competing
     ranking rules. Every score material is priced by replacement effort, then discounted
     continuously when projected usable supply comfortably covers remaining productive
     upgrade demand. Saved + already-planned Realm tools count toward that COVERAGE at 80%
     of their material-equivalent value: enough to recognize a healthy bank, but with a 20%
     preservation premium for their bankable/flexible option value. Extra Realm purchases
     invented by the optimizer never count as surplus. A 0.25 floor keeps large surpluses
     cheap-but-not-worthless; Treats retain the existing zero floor because they have no
     Realm-tool substitute. Strict source tiers remain raw -> saved/planned tools -> extra. */
  const SURPLUS_ACQUISITION_FLOORS={ore:0.25,essence:0.25,sand:0.25,treat:0.00};
  const TOOL_SCARCITY_CREDIT=0.80;"""
if old not in s: raise SystemExit('scarcity header anchor not found')
s=s.replace(old,new,1)

old="""  function plannedToolAcquisitionSupply(key,resources,cfg=activeCalcConfig()){
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
  }"""
new="""  function plannedToolAcquisitionSupply(key,resources,cfg=activeCalcConfig()){
    if(key==='treat') return rawOnlyAcquisitionSupply(key,resources,cfg);
    const inv=realmInventoryFor(key,cfg);
    const perRun=Math.max(0,realmYieldFor(resources,key));
    const bankedMaterial=Math.max(0,Number(inv?.banked)||0)*perRun;
    return rawOnlyAcquisitionSupply(key,resources,cfg)+bankedMaterial*TOOL_SCARCITY_CREDIT;
  }"""
if old not in s: raise SystemExit('planned tool supply anchor not found')
s=s.replace(old,new,1)

old="""    const acquisitionResources=acquisitionResourcesForRealms(resources,realms,activeCalcConfig());
    const realmStageForAcquisition=candidateRealmStage({realm:{ore:oreRealm,essence:essenceRealm,sand:sandRealm}});
    const acquisition=(realmStageForAcquisition===0&&acquisitionResult)
      ? acquisitionResult
      : acquisitionEffortFor({ore:go.oreCost,essence:so.cost,sand:ro.cost,treat:fo.cost},acquisitionResources,activeCalcConfig());"""
new="""    /* ACQUISITION_KERNEL_V2
       Scarcity coverage is fixed for one resource snapshot, including the 80% credit for
       saved/planned tools. Feasibility/source stage is still decided separately by Realm
       top-up math. Therefore the hot search can reuse its precomputed acquisition result
       for raw AND tool-backed candidates instead of recalculating logarithms/DOM rates for
       every candidate combination. */
    const acquisition=acquisitionResult||acquisitionEffortFor({ore:go.oreCost,essence:so.cost,sand:ro.cost,treat:fo.cost},resources,activeCalcConfig());"""
if old not in s: raise SystemExit('makePlanCandidate acquisition anchor not found')
s=s.replace(old,new,1)

old="""    // Dynamic usability compares remaining safe-cap demand with everything already available
    // for that category. Spendable Realm tools count as material-equivalent supply; only tools needed
    // for a raw-material reserve gap are excluded by realmInventoryFor().
    resources.acquisitionHeadroomCosts=headroomCosts||{};
    // Gate 2 is RAW ONLY. Realm tools do not make a capped category look overfunded here;
    // they remain banked until no raw-only score plan can reach the requested target.
    resources.acquisitionSupplyEquiv={
      ore:rawOnlyAcquisitionSupply('ore',resources,cfg),
      essence:rawOnlyAcquisitionSupply('essence',resources,cfg),
      sand:rawOnlyAcquisitionSupply('sand',resources,cfg),
      treat:rawOnlyAcquisitionSupply('treat',resources,cfg)
    };"""
new="""    // Scarcity RANKING can see saved + already-planned Realm tools at 80% material credit;
    // Realm FEASIBILITY remains strictly raw-first because realmTopupFor still compares each
    // candidate cost against the raw projected budget before consuming any tools. Extra tool
    // purchases are not included here, avoiding circular 'buy it because it is abundant' logic.
    resources.acquisitionHeadroomCosts=headroomCosts||{};
    resources.acquisitionSupplyEquiv={
      ore:plannedToolAcquisitionSupply('ore',resources,cfg),
      essence:plannedToolAcquisitionSupply('essence',resources,cfg),
      sand:plannedToolAcquisitionSupply('sand',resources,cfg),
      treat:rawOnlyAcquisitionSupply('treat',resources,cfg)
    };"""
if old not in s: raise SystemExit('search supply anchor not found')
s=s.replace(old,new,1)

old="""    /* ACQUISITION_KERNEL_V1
       This metric is evaluated in the hottest optimizer loop. Precompute each category's
       marginal weighted spend once per resource state, read Cart/map rates once, and run
       the same joint-reacquisition equation with scalar locals. This removes repeated DOM
       reads, logarithms, temporary objects and arrays from millions of candidate comparisons
       without changing the acquisition formula or any tie-break rule. */"""
new="""    /* ACQUISITION_KERNEL_V2
       This metric is evaluated in the hottest optimizer loop. Precompute each category's
       scarcity-adjusted spend ONCE per resource snapshot (including 80%-credited saved/
       planned tools), read Cart/map rates once, and run the joint-reacquisition equation
       with scalar locals. Tool-backed candidates reuse this same exact kernel instead of
       rebuilding scarcity objects and rerunning logarithms in makePlanCandidate(). */"""
if old not in s: raise SystemExit('kernel comment anchor not found')
s=s.replace(old,new,1)

old="""Within each sourcing tier, Gear, individual Skills, individual Relics and individual Fantomons are balanced by <b>scarcity-adjusted acquisition efficiency</b>: replacement difficulty is the base cost, then projected coverage makes abundant Ore/Hammers, Essence/Knuckles or Sand/Shovels cheaper to consume while nearly exhausted pools become more valuable. Surplus has a nonzero floor, so excess is cheap rather than literally worthless. Actual S2 upgrade-cost curves still determine every marginal step."""
new="""Within each sourcing tier, Gear, individual Skills, individual Relics and individual Fantomons are balanced by <b>scarcity-adjusted acquisition efficiency</b>: replacement difficulty is the base cost, then projected coverage makes abundant Ore/Hammers, Essence/Knuckles or Sand/Shovels cheaper to consume while nearly exhausted pools become more valuable. Saved + already-planned Realm tools contribute <b>80%</b> of their material-equivalent value to scarcity coverage, preserving a 20% option-value premium; extra recommended purchases never count as surplus. Raw feasibility still comes first, so tools remain untouched whenever a raw-only goal plan exists. Surplus has a nonzero floor, so excess is cheap rather than literally worthless. Actual S2 upgrade-cost curves still determine every marginal step."""
if old not in s: raise SystemExit('method text anchor not found')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('Applied tool scarcity credit + acquisition hot-path v2.')
