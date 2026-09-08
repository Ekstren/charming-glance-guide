from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
MARK='TREAT_MARGINAL_SCARCITY_V1'
if MARK in s:
    print('Treat marginal scarcity v1 already applied.')
    raise SystemExit(0)

old_consts="""  const SURPLUS_ACQUISITION_FLOORS={ore:0.25,essence:0.25,sand:0.25,treat:0.00};
  const TOOL_SCARCITY_CREDIT=1.00;
  // MARGINAL_INTEGRATED_SCARCITY_V5: these shape the price of the NEXT unit consumed.
"""
new_consts="""  // TREAT_MARGINAL_SCARCITY_V1: Treats use the same marginal depletion curve as the
  // other score-material families; their only economic difference is no Realm-tool supply.
  const SURPLUS_ACQUISITION_FLOORS={ore:0.25,essence:0.25,sand:0.25,treat:0.25};
  const TOOL_SCARCITY_CREDIT=1.00;
  // MARGINAL_INTEGRATED_SCARCITY_V5: these shape the price of the NEXT unit consumed.
"""
if old_consts not in s:
    raise SystemExit('scarcity constants anchor not found')
s=s.replace(old_consts,new_consts,1)

old_comment="""     V5 prices Ore / Essence / Sand MARGINALLY as the pool is consumed. The scarcity multiplier
     for the next unit is floor + (max-floor) * consumedFraction^exponent, and candidate cost is
     the analytic integral of that curve from the pre-plan state through the candidate spend.
     Therefore early surplus units stay cheap and only later units become strongly scarce; the
     last unit no longer retroactively reprices every earlier unit. Any spend beyond the projected
     owned/planned pool is priced at the maximum scarcity multiplier.

     Treats intentionally keep the prior headroom integral because they have no Realm-tool pool. */
"""
new_comment="""     V5 prices Ore / Essence / Sand / Treats MARGINALLY as each pool is consumed. The scarcity
     multiplier for the next unit is floor + (max-floor) * consumedFraction^exponent, and candidate
     cost is the analytic integral of that curve from the pre-plan state through the candidate spend.
     Therefore early surplus units stay cheap and only later units become strongly scarce; the last
     unit no longer retroactively reprices every earlier unit. Any spend beyond the projected
     owned/planned pool is priced at the maximum scarcity multiplier. Treats use projected raw/
     acquired Treat-equivalent supply only; unlike Ore/Essence/Sand they have no Realm-tool credit. */
"""
if old_comment not in s:
    raise SystemExit('scarcity comment anchor not found')
s=s.replace(old_comment,new_comment,1)

old_treat="""    if(key==='treat'){
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

    let effective=0;
"""
new_treat="""    // TREAT_MARGINAL_SCARCITY_V1: all four score-material families now use this same
    // integrated depletion curve. Treats differ only in acquisitionSupplyEquiv construction:
    // they have no Hammer/Knuckle/Shovel-style Realm-tool capacity added to their pool.
    let effective=0;
"""
if old_treat not in s:
    raise SystemExit('legacy Treat branch anchor not found')
s=s.replace(old_treat,new_treat,1)

old_method="""Smart Balance chooses the Gear / Skill / Relic / Fantomon mix by <b>marginal integrated scarcity-adjusted acquisition efficiency</b>: each additional unit is priced along the depletion curve, so early surplus spend stays cheap while later units rise progressively as a pool drains."""
new_method="""Smart Balance chooses the Gear / Skill / Relic / Fantomon mix by <b>marginal integrated scarcity-adjusted acquisition efficiency</b>: Ore, Essence, Sand and Treats all price each additional unit along the same depletion curve, so early surplus spend stays cheap while later units rise progressively as a pool drains. Treats simply have no Realm-tool capacity added to their supply."""
if old_method not in s:
    raise SystemExit('Smart Balance method text anchor not found')
s=s.replace(old_method,new_method,1)

p.write_text(s,encoding='utf-8')
print('Applied Treat marginal scarcity v1.')
