from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

if 'POST_PLAN_SCARCITY_V4' in s:
    print('Post-plan scarcity v4 already applied.')
    raise SystemExit(0)

old="""  /* SCARCITY_ADJUSTED_ACQUISITION_V1 · TOOL_SCARCITY_CREDIT_V2
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
new="""  /* SCARCITY_ADJUSTED_ACQUISITION_V1 · TOOL_SCARCITY_CREDIT_V2 · POST_PLAN_SCARCITY_V4
     Acquisition difficulty and projected scarcity are ONE economic metric, not competing
     ranking rules. Saved + already-planned Realm tools count toward the pool at 80% of their
     material-equivalent value, preserving a 20% option-value premium. Extra purchases never
     count as surplus. The v4 balance pressure is based on how much of that usable pool a
     CANDIDATE PLAN would leave after spending: abundant pools are cheap to consume, while
     plans that drain a pool toward zero become progressively expensive instead of all
     collapsing to the same flat surplus floor. Strict source tiers remain
     raw -> saved/planned tools -> extra purchases. */
  const SURPLUS_ACQUISITION_FLOORS={ore:0.25,essence:0.25,sand:0.25,treat:0.00};
  const TOOL_SCARCITY_CREDIT=0.80;
  const POST_PLAN_SCARCITY_MAX=2.50;
  const POST_PLAN_SCARCITY_EXPONENT=2.20;"""
if old not in s: raise SystemExit('scarcity header anchor not found')
s=s.replace(old,new,1)

old="""  /* MARGINAL_HEADROOM_COST_V2
     Candidate resource cost is priced along the funded-cap curve, not at one static
     pre-spend weight. When a capped category is already overfunded, the first units are
     cheap to spend; as spending consumes that cushion and approaches an unfunded safe cap,
     each additional unit becomes progressively more valuable. */
  function marginalWeightedSpend(amount,key,resources){
    const amountTotal=Math.max(0,Number(amount)||0);
    if(amountTotal<=0) return 0;

    const floor=Math.max(0,Math.min(1,Number(SURPLUS_ACQUISITION_FLOORS[key])||0));
    const usefulNeed=Math.max(0,Number(resources?.acquisitionHeadroomCosts?.[key])||0);
    const available=Math.max(0,Number(resources?.acquisitionSupplyEquiv?.[key])||0);
    if(usefulNeed<=0) return amountTotal*floor;

    // Candidate costs should never exceed productive headroom, but keep any impossible
    // excess fully scarce rather than silently discounting it.
    const productive=Math.min(amountTotal,usefulNeed);
    let effective=0;

    if(available>=usefulNeed-1e-9){
      // Fully funded cap: as this resource is spent on its OWN upgrades, supply and
      // remaining demand fall together, so coverage stays full through the useful band.
      effective+=productive*floor;
    }else if(available<=1e-9){
      effective+=productive;
    }else{
      // With an initial deficit D=N-A, after spending t on this same category the deficit
      // remains D while remaining demand becomes N-t. Marginal scarcity is therefore
      // floor + (1-floor)*D/(N-t). Integrate exactly until usable supply is exhausted.
      const covered=Math.min(productive,available);
      const deficit=Math.max(0,usefulNeed-available);
      const denomEnd=Math.max(1e-12,usefulNeed-covered);
      effective+=floor*covered+(1-floor)*deficit*Math.log(usefulNeed/denomEnd);
      if(productive>covered) effective+=productive-covered;
    }

    if(amountTotal>productive) effective+=amountTotal-productive;
    return effective;
  }"""
new="""  /* POST_PLAN_SCARCITY_V4
     Rank plans by the reserve they LEAVE, not just whether a category was technically
     funded before spending. For Ore / Essence / Sand, the economic multiplier rises
     smoothly with the fraction of the projected usable pool consumed by the candidate.
     This is monotone in spend, so dominated-plan pruning remains valid. Saved/planned Realm
     tools are already represented in acquisitionSupplyEquiv at 80% credit; when a candidate
     crosses from raw into those tools, only 80% of that material spend reduces scarcity
     supply, preserving their option-value premium. Extra purchased tools contribute no
     starting supply and therefore hit maximum scarcity pressure.

     Treats intentionally keep the prior headroom integral because the exact Treat-funded
     fast path relies on a fully funded Treat cap having zero marginal acquisition cost. */
  function marginalWeightedSpend(amount,key,resources){
    const amountTotal=Math.max(0,Number(amount)||0);
    if(amountTotal<=0) return 0;

    const floor=Math.max(0,Math.min(1,Number(SURPLUS_ACQUISITION_FLOORS[key])||0));
    const usefulNeed=Math.max(0,Number(resources?.acquisitionHeadroomCosts?.[key])||0);
    const available=Math.max(0,Number(resources?.acquisitionSupplyEquiv?.[key])||0);
    if(usefulNeed<=0) return amountTotal*floor;

    const productive=Math.min(amountTotal,usefulNeed);

    if(key==='treat'){
      let effective=0;
      if(available>=usefulNeed-1e-9){
        effective+=productive*floor;
      }else if(available<=1e-9){
        effective+=productive;
      }else{
        const covered=Math.min(productive,available);
        const deficit=Math.max(0,usefulNeed-available);
        const denomEnd=Math.max(1e-12,usefulNeed-covered);
        effective+=floor*covered+(1-floor)*deficit*Math.log(usefulNeed/denomEnd);
        if(productive>covered) effective+=productive-covered;
      }
      if(amountTotal>productive) effective+=amountTotal-productive;
      return effective;
    }

    const rawAvailable=Math.max(0,Number(resources?.[key])||0);
    const toolCreditAvailable=Math.max(0,available-rawAvailable);
    const rawSpend=Math.min(productive,rawAvailable);
    const toolMaterialSpend=Math.max(0,productive-rawAvailable);
    const creditedToolSpend=Math.min(toolCreditAvailable,toolMaterialSpend*TOOL_SCARCITY_CREDIT);
    const creditedSpend=Math.min(available,rawSpend+creditedToolSpend);

    // Fraction of the existing projected usable pool consumed by THIS candidate. Because
    // creditedSpend is monotone, this multiplier only rises as a plan spends more of a pool.
    const spentFraction=available>1e-9
      ? Math.max(0,Math.min(1,creditedSpend/available))
      : (productive>0?1:0);
    const multiplier=floor+(POST_PLAN_SCARCITY_MAX-floor)*Math.pow(spentFraction,POST_PLAN_SCARCITY_EXPONENT);
    let effective=productive*multiplier;

    // Any progression beyond productive headroom or beyond the credited existing pool is
    // intentionally expensive. Source-tier rules still decide whether such a route is legal.
    if(amountTotal>productive) effective+=(amountTotal-productive)*POST_PLAN_SCARCITY_MAX;
    return effective;
  }"""
if old not in s: raise SystemExit('marginalWeightedSpend anchor not found')
s=s.replace(old,new,1)

old="""Within each sourcing tier, Gear, individual Skills, individual Relics and individual Fantomons are balanced by <b>scarcity-adjusted acquisition efficiency</b>: replacement difficulty is the base cost, then projected coverage makes abundant Ore/Hammers, Essence/Knuckles or Sand/Shovels cheaper to consume while nearly exhausted pools become more valuable. Saved + already-planned Realm tools contribute <b>80%</b> of their material-equivalent value to scarcity coverage, preserving a 20% option-value premium; extra recommended purchases never count as surplus. Raw feasibility still comes first, so tools remain untouched whenever a raw-only goal plan exists. Surplus has a nonzero floor, so excess is cheap rather than literally worthless. Actual S2 upgrade-cost curves still determine every marginal step."""
new="""Within each sourcing tier, Gear, individual Skills, individual Relics and individual Fantomons are balanced by <b>post-plan scarcity-adjusted acquisition efficiency</b>: replacement difficulty is still the base cost, but the optimizer now prices each candidate by how much of the projected usable Ore/Hammer, Essence/Knuckle or Sand/Shovel pool it would consume. A plan that leaves a healthy reserve is cheaper; a plan that would scrape a pool toward zero becomes progressively more expensive. Saved + already-planned Realm tools contribute <b>80%</b> of their material-equivalent value to that pool, preserving a 20% option-value premium; extra recommended purchases never count as surplus. Raw feasibility still comes first, so tools remain untouched whenever a raw-only goal plan exists. Actual S2 upgrade-cost curves still determine every marginal step."""
if old not in s: raise SystemExit('method text anchor not found')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('Applied post-plan scarcity v4.')
