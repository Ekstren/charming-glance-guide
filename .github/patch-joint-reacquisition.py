from pathlib import Path

PATH=Path('index.html')
text=PATH.read_text(encoding='utf-8')
MARKER='JOINT_REACQUISITION_V1'
if MARKER in text:
    print('Joint reacquisition optimizer already applied.')
    raise SystemExit(0)

start=text.find('  /* SURPLUS_AWARE_OPTIMIZER_V2')
end=text.find('  function candidateResourceMetric(candidate){',start)
if start<0 or end<0:
    raise SystemExit('acquisition helper block not found')

helper=r'''  /* SURPLUS_AWARE_OPTIMIZER_V2 · JOINT_REACQUISITION_V1
     Enabled S2 hard reserves are removed before this S1 tie-breaker runs. The remaining
     costs are valued by future usability, then reacquisition is solved JOINTLY: Ore,
     Essence and Sand carts all accrue at the same time while one natural Stamina stream
     (5 Stamina/hour = one 5-Stamina map node/hour) is optimally shared between them.
     Treats accrue in parallel from their entered Cart rate / fallback scarcity rate.
     Preserve Ore uses the same joint model with a bounded Ore premium, not a separate
     additive Ore-hours penalty. */
  const SURPLUS_ACQUISITION_WEIGHTS={ore:1.00,essence:0.10,sand:0.35,treat:0.35};
  const ORE_PRESERVE_PREMIUM=0.50;

  function jointReacquisitionHours(costs,resources,cfg=activeCalcConfig(),weights=SURPLUS_ACQUISITION_WEIGHTS){
    const map=resources?.yields?.map||cfg.map||{};
    const horizon=Math.max(24,Number(resources?.cartHours)||24);
    const projectedTreat=Math.max(0,Number(resources?.treat)||0);
    const enteredTreatRate=Math.max(0,n('treatRate'));
    const fallbackTreatRate=projectedTreat>0?projectedTreat/horizon:0;
    const cart={
      ore:Math.max(0,n('oreRate')),
      essence:Math.max(0,n('essenceRate')),
      sand:Math.max(0,n('sandRate')),
      treat:enteredTreatRate>0?enteredTreatRate:fallbackTreatRate
    };
    const nodeYield={
      ore:Math.max(0,Number(map.ore)||0),
      essence:Math.max(0,Number(map.essence)||0),
      sand:Math.max(0,Number(map.sand)||0)
    };
    const demand={
      ore:Math.max(0,Number(costs?.ore)||0)*Math.max(0,Number(weights?.ore)||0),
      essence:Math.max(0,Number(costs?.essence)||0)*Math.max(0,Number(weights?.essence)||0),
      sand:Math.max(0,Number(costs?.sand)||0)*Math.max(0,Number(weights?.sand)||0),
      treat:Math.max(0,Number(costs?.treat)||0)*Math.max(0,Number(weights?.treat)||0)
    };

    let floor=0;
    if(demand.treat>0){
      if(cart.treat<=0) return 1e9;
      floor=Math.max(floor,demand.treat/cart.treat);
    }
    const keys=['ore','essence','sand'];
    for(const key of keys){
      if(demand[key]<=0) continue;
      if(nodeYield[key]<=0){
        if(cart[key]<=0) return 1e9;
        floor=Math.max(floor,demand[key]/cart[key]);
      }
    }

    const nodesNeededAt=hours=>{
      let total=0;
      for(const key of keys){
        const remaining=Math.max(0,demand[key]-cart[key]*hours);
        if(remaining<=0) continue;
        if(nodeYield[key]<=0) return Infinity;
        total+=remaining/nodeYield[key];
      }
      return total;
    };
    if(nodesNeededAt(floor)<=floor+1e-9) return floor;

    // f(T)=required shared Stamina nodes - T is piecewise linear. Start with every
    // resource still short at the Cart-only floor, solve that linear segment exactly,
    // and drop any resource whose Cart alone covers it by the resulting time.
    let active=keys.filter(key=>demand[key]>cart[key]*floor+1e-9 && nodeYield[key]>0);
    let hours=floor;
    for(let pass=0;pass<4;pass++){
      let numerator=0,denominator=1;
      for(const key of active){
        numerator+=demand[key]/nodeYield[key];
        denominator+=cart[key]/nodeYield[key];
      }
      hours=Math.max(floor,numerator/denominator);
      const next=active.filter(key=>demand[key]>cart[key]*hours+1e-9);
      if(next.length===active.length){
        if(nodesNeededAt(hours)<=hours+1e-7) return hours;
        break;
      }
      active=next;
      if(!active.length) return floor;
    }

    // Numerical fallback only; normal three-resource cases resolve in <=3 active-set passes.
    let lo=floor,hi=Math.max(1,hours,floor);
    while(nodesNeededAt(hi)>hi+1e-9 && hi<1e9) hi*=2;
    if(hi>=1e9 && nodesNeededAt(hi)>hi+1e-9) return 1e9;
    for(let i=0;i<48;i++){
      const mid=(lo+hi)/2;
      if(nodesNeededAt(mid)<=mid) hi=mid; else lo=mid;
    }
    return hi;
  }

  function acquisitionEffortFor(costs,resources,cfg=activeCalcConfig()){
    const preserveWeights={...SURPLUS_ACQUISITION_WEIGHTS,ore:SURPLUS_ACQUISITION_WEIGHTS.ore*(1+ORE_PRESERVE_PREMIUM)};
    const hours=jointReacquisitionHours(costs,resources,cfg,SURPLUS_ACQUISITION_WEIGHTS);
    const preserveHours=jointReacquisitionHours(costs,resources,cfg,preserveWeights);
    const map=resources?.yields?.map||cfg.map||{};
    const single=(amount,key,weight)=>{
      const target=Math.max(0,Number(amount)||0)*Math.max(0,Number(weight)||0);
      if(target<=0) return 0;
      const rate=Math.max(0,n(key==='ore'?'oreRate':key==='essence'?'essenceRate':'sandRate'))+Math.max(0,Number(map[key])||0);
      return rate>0?target/rate:1e9;
    };
    return {
      hours,preserveHours,
      oreHours:single(costs?.ore,'ore',SURPLUS_ACQUISITION_WEIGHTS.ore),
      essenceHours:single(costs?.essence,'essence',SURPLUS_ACQUISITION_WEIGHTS.essence),
      sandHours:single(costs?.sand,'sand',SURPLUS_ACQUISITION_WEIGHTS.sand),
      treatHours:0,
      treatFallback:Math.max(0,n('treatRate'))<=0
    };
  }
'''
text=text[:start]+helper+text[end:]

old='const preserveAcquisitionScore=acquisition.hours+acquisition.oreHours*ORE_PRESERVE_PREMIUM;'
if text.count(old)!=1:
    raise SystemExit(f'candidate preserve metric count={text.count(old)}')
text=text.replace(old,'const preserveAcquisitionScore=acquisition.preserveHours;',1)

old_diag='preserveAcquisitionScore:diagAcquisition.hours+diagAcquisition.oreHours*ORE_PRESERVE_PREMIUM'
if text.count(old_diag)!=1:
    raise SystemExit(f'diagnostic preserve metric count={text.count(old_diag)}')
text=text.replace(old_diag,'preserveAcquisitionScore:diagAcquisition.preserveHours',1)

text=text.replace("      ? 'Spend capped surplus first; replacement effort then gets a +50% Ore premium for Gear runway.'\n      : 'Spend capped surplus efficiently: reserves stay protected, then replacement effort is weighted by future usability.';",
                  "      ? 'Minimize joint Cart + shared-Stamina reacquisition effort with a +50% Ore value premium for Gear runway.'\n      : 'Minimize joint Cart + shared-Stamina reacquisition effort, weighted by future usability.';",1)
text=text.replace("const policy=optimizerMode()==='preserve'?'spend capped surplus + preserve Ore':'spend capped surplus by acquisition efficiency';",
                  "const policy=optimizerMode()==='preserve'?'joint reacquisition + Ore premium':'joint reacquisition efficiency';",1)

PATH.write_text(text,encoding='utf-8')
print('Applied joint Cart + shared-Stamina reacquisition model.')
