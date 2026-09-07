from pathlib import Path
import re

p=Path('index.html')
s=p.read_text(encoding='utf-8')
MARK='MARGINAL_INTEGRATED_SCARCITY_V5'
if MARK in s:
    print('Marginal integrated scarcity v5 already applied.')
    raise SystemExit(0)

old_consts="""  const SURPLUS_ACQUISITION_FLOORS={ore:0.25,essence:0.25,sand:0.25,treat:0.00};
  const TOOL_SCARCITY_CREDIT=1.00;
  const POST_PLAN_SCARCITY_MAX=2.50;
  const POST_PLAN_SCARCITY_EXPONENT=2.20;
"""
new_consts="""  const SURPLUS_ACQUISITION_FLOORS={ore:0.25,essence:0.25,sand:0.25,treat:0.00};
  const TOOL_SCARCITY_CREDIT=1.00;
  // MARGINAL_INTEGRATED_SCARCITY_V5: these shape the price of the NEXT unit consumed.
  // The optimizer integrates this curve over the candidate spend instead of applying the
  // final depletion multiplier retroactively to the entire spend.
  const POST_PLAN_SCARCITY_MAX=3.50;
  const POST_PLAN_SCARCITY_EXPONENT=2.40;
"""
if old_consts not in s:
    raise SystemExit('scarcity constants anchor not found')
s=s.replace(old_consts,new_consts,1)

pat=re.compile(r"  /\* POST_PLAN_SCARCITY_V4 · TOTAL_POOL_SMART_BALANCE_V1\n.*?\n  function marginalWeightedCosts\(costs,resources,cfg=activeCalcConfig\(\)\)\{",re.S)
m=pat.search(s)
if not m:
    raise SystemExit('marginalWeightedSpend block not found')

new_block="""  /* POST_PLAN_SCARCITY_V4 · TOTAL_POOL_SMART_BALANCE_V1 · MARGINAL_INTEGRATED_SCARCITY_V5
     Rank plans by the reserve they leave in the TOTAL owned/projected resource family.
     Raw and saved/already-planned tools are economically interchangeable for scarcity, while
     realmTopupFor() still enforces the physical spend order: raw first, then banked/planned tools.
     Extra candidate purchases never add starting supply, so a paid route cannot make itself look
     abundant by counting tools it has not bought yet.

     V5 prices Ore / Essence / Sand MARGINALLY as the pool is consumed. The scarcity multiplier
     for the next unit is floor + (max-floor) * consumedFraction^exponent, and candidate cost is
     the analytic integral of that curve from the pre-plan state through the candidate spend.
     Therefore early surplus units stay cheap and only later units become strongly scarce; the
     last unit no longer retroactively reprices every earlier unit. Any spend beyond the projected
     owned/planned pool is priced at the maximum scarcity multiplier.

     Treats intentionally keep the prior headroom integral because they have no Realm-tool pool. */
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

    let effective=0;
    if(available<=1e-9){
      effective=productive*POST_PLAN_SCARCITY_MAX;
    }else{
      const withinPool=Math.min(productive,available);
      const fraction=Math.max(0,Math.min(1,withinPool/available));
      const power=POST_PLAN_SCARCITY_EXPONENT+1;
      // Integral from x=0 to x=fraction of:
      //   floor + (max-floor) * x^exponent
      // multiplied by the pool size to return material-equivalent weighted cost.
      effective=
        floor*withinPool+
        (POST_PLAN_SCARCITY_MAX-floor)*available/power*Math.pow(fraction,power);

      if(productive>available){
        effective+=(productive-available)*POST_PLAN_SCARCITY_MAX;
      }
    }

    // Progression beyond productive headroom is never treated as cheap surplus.
    if(amountTotal>productive) effective+=(amountTotal-productive)*POST_PLAN_SCARCITY_MAX;
    return effective;
  }

  function marginalWeightedCosts(costs,resources,cfg=activeCalcConfig()){"""
s=s[:m.start()]+new_block+s[m.end():]

old_method="""Smart Balance chooses the Gear / Skill / Relic / Fantomon mix by <b>post-plan scarcity-adjusted acquisition efficiency</b>, so abundant pools are cheaper to consume and near-empty pools become expensive."""
new_method="""Smart Balance chooses the Gear / Skill / Relic / Fantomon mix by <b>marginal integrated scarcity-adjusted acquisition efficiency</b>: each additional unit is priced along the depletion curve, so early surplus spend stays cheap while later units rise progressively as a pool drains."""
if old_method not in s:
    raise SystemExit('method text anchor not found')
s=s.replace(old_method,new_method,1)

p.write_text(s,encoding='utf-8')
print('Applied marginal integrated scarcity v5.')
