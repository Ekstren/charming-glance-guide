from pathlib import Path

PATH = Path('index.html')
text = PATH.read_text(encoding='utf-8')
MARKER = 'MARGINAL_HEADROOM_COST_V2'
if MARKER in text:
    print('Marginal headroom pricing already applied.')
    raise SystemExit(0)

anchor = "  function jointReacquisitionHours(costs,resources,cfg=activeCalcConfig(),weights=null){"
if text.count(anchor) != 1:
    raise SystemExit(f'joint solver anchor count={text.count(anchor)}')

marginal = r'''  /* MARGINAL_HEADROOM_COST_V2
     Candidate resource cost is priced along the funded-cap curve, not at one static
     pre-spend weight. When a capped category is already overfunded, the first units are
     cheap to spend; as spending consumes that cushion and approaches an unfunded safe cap,
     each additional unit becomes progressively more valuable. */
  const UNIT_ACQUISITION_WEIGHTS={ore:1,essence:1,sand:1,treat:1};

  function marginalWeightedSpend(amount,key,resources){
    let remaining=Math.max(0,Number(amount)||0);
    if(remaining<=0) return 0;
    if(key==='ore') return remaining;

    const floor=Math.max(0,Math.min(1,Number(SURPLUS_ACQUISITION_FLOORS[key])||0));
    const usefulNeed=Math.max(0,Number(resources?.acquisitionHeadroomCosts?.[key])||0);
    let available=Math.max(0,Number(resources?.acquisitionSupplyEquiv?.[key])||0);
    if(usefulNeed<=0) return remaining*floor;

    let effective=0;

    // Supply above the full reachable-cap requirement is pure cushion and carries only
    // the deferred-use floor value.
    const excess=Math.max(0,available-usefulNeed);
    if(excess>0){
      const cheap=Math.min(remaining,excess);
      effective+=cheap*floor;
      remaining-=cheap;
      available-=cheap;
    }

    // Within the funded-cap band, marginal value rises linearly from the floor at 100%
    // funded to 1.00 at 0% funded. Integrate that curve exactly over this candidate spend.
    if(remaining>0 && available>0){
      const band=Math.min(remaining,available);
      const start=Math.min(usefulNeed,available);
      const end=Math.max(0,start-band);
      effective+=band-((1-floor)/(2*usefulNeed))*((start*start)-(end*end));
      remaining-=band;
      available-=band;
    }

    // Any spend beyond current usable supply represents fully scarce replacement demand.
    if(remaining>0) effective+=remaining;
    return effective;
  }

  function marginalWeightedCosts(costs,resources,preserveOre=false){
    return {
      ore:Math.max(0,Number(costs?.ore)||0)*(preserveOre?1+ORE_PRESERVE_PREMIUM:1),
      essence:marginalWeightedSpend(costs?.essence,'essence',resources),
      sand:marginalWeightedSpend(costs?.sand,'sand',resources),
      treat:marginalWeightedSpend(costs?.treat,'treat',resources)
    };
  }

'''
text=text.replace(anchor,marginal+anchor,1)

start=text.find('  function acquisitionEffortFor(costs,resources,cfg=activeCalcConfig()){')
end=text.find('  function candidateResourceMetric(candidate){',start)
if start<0 or end<0:
    raise SystemExit('acquisitionEffortFor block not found')
old=text[start:end]
new=r'''  function acquisitionEffortFor(costs,resources,cfg=activeCalcConfig()){
    const weights=dynamicAcquisitionWeights(resources); // diagnostic snapshot at zero spend
    const marginalCosts=marginalWeightedCosts(costs,resources,false);
    const preserveCosts=marginalWeightedCosts(costs,resources,true);
    const hours=jointReacquisitionHours(marginalCosts,resources,cfg,UNIT_ACQUISITION_WEIGHTS);
    const preserveHours=jointReacquisitionHours(preserveCosts,resources,cfg,UNIT_ACQUISITION_WEIGHTS);
    const map=resources?.yields?.map||cfg.map||{};
    const single=(effective,key)=>{
      const target=Math.max(0,Number(effective)||0);
      if(target<=0) return 0;
      const rate=Math.max(0,n(key==='ore'?'oreRate':key==='essence'?'essenceRate':'sandRate'))+Math.max(0,Number(map[key])||0);
      return rate>0?target/rate:1e9;
    };
    return {
      hours,preserveHours,weights,marginalCosts,
      oreHours:single(marginalCosts.ore,'ore'),
      essenceHours:single(marginalCosts.essence,'essence'),
      sandHours:single(marginalCosts.sand,'sand'),
      treatHours:0,
      treatFallback:Math.max(0,n('treatRate'))<=0
    };
  }
'''
text=text[:start]+new+text[end:]

text=text.replace(
"      ? 'Joint Cart + shared-Stamina efficiency with funded-cap coverage, plus a +50% Ore premium for Gear runway.'\n      : 'Joint Cart + shared-Stamina efficiency, capped resources get cheaper as their reachable cap becomes funded.';",
"      ? 'Joint Cart + shared-Stamina efficiency with marginal funded-cap pricing, plus a +50% Ore premium for Gear runway.'\n      : 'Joint Cart + shared-Stamina efficiency with marginal pricing as capped-resource cushion is consumed.';",
1)

PATH.write_text(text,encoding='utf-8')
print('Applied marginal funded-cap resource pricing.')
