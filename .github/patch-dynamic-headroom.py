from pathlib import Path

PATH = Path('index.html')
text = PATH.read_text(encoding='utf-8')
MARKER = 'DYNAMIC_HEADROOM_WEIGHTS_V1'
if MARKER in text:
    print('Dynamic headroom weighting already applied.')
    raise SystemExit(0)

start = text.find('  /* SURPLUS_AWARE_OPTIMIZER_V2 · JOINT_REACQUISITION_V1')
end = text.find('  function candidateResourceMetric(candidate){', start)
if start < 0 or end < 0:
    raise SystemExit('joint acquisition helper block not found')

helper = r'''  /* SURPLUS_AWARE_OPTIMIZER_V2 · JOINT_REACQUISITION_V1 · DYNAMIC_HEADROOM_WEIGHTS_V1
     Enabled S2 hard reserves are removed before this S1 tie-breaker runs. Reacquisition is
     solved jointly: Ore / Essence / Sand carts accrue simultaneously while one natural
     Stamina stream is optimally shared between map nodes. Capped-resource future value is
     now dynamic: if the current spendable raw + usable Realm-tool supply cannot fund the
     remaining safe-cap upgrades, that material stays near full value; once the reachable
     category is already comfortably funded, its value falls toward a deferred-use floor.
     Ore remains the 1.00 baseline because Gear has the broadest runway. Preserve Ore applies
     a bounded +50% Ore premium on top of the same joint model. */
  const SURPLUS_ACQUISITION_FLOORS={ore:1.00,essence:0.10,sand:0.35,treat:0.35};
  const ORE_PRESERVE_PREMIUM=0.50;

  function dynamicAcquisitionWeights(resources){
    const headroom=resources?.acquisitionHeadroomCosts||{};
    const supply=resources?.acquisitionSupplyEquiv||{};
    const result={ore:1.00,essence:SURPLUS_ACQUISITION_FLOORS.essence,sand:SURPLUS_ACQUISITION_FLOORS.sand,treat:SURPLUS_ACQUISITION_FLOORS.treat};
    for(const key of ['essence','sand','treat']){
      const floor=Math.max(0,Math.min(1,Number(SURPLUS_ACQUISITION_FLOORS[key])||0));
      const usefulNeed=Math.max(0,Number(headroom[key])||0);
      const available=Math.max(0,Number(supply[key])||0);
      // usefulShare=1 means all current supply can still be productively spent before the
      // safe cap. If supply already exceeds that headroom, only the excess is discounted.
      const usefulShare=usefulNeed<=0?0:(available>0?Math.min(1,usefulNeed/available):1);
      result[key]=floor+(1-floor)*usefulShare;
    }
    return result;
  }

  function jointReacquisitionHours(costs,resources,cfg=activeCalcConfig(),weights=null){
    weights=weights||dynamicAcquisitionWeights(resources);
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
    const weights=dynamicAcquisitionWeights(resources);
    const preserveWeights={...weights,ore:weights.ore*(1+ORE_PRESERVE_PREMIUM)};
    const hours=jointReacquisitionHours(costs,resources,cfg,weights);
    const preserveHours=jointReacquisitionHours(costs,resources,cfg,preserveWeights);
    const map=resources?.yields?.map||cfg.map||{};
    const single=(amount,key,weight)=>{
      const target=Math.max(0,Number(amount)||0)*Math.max(0,Number(weight)||0);
      if(target<=0) return 0;
      const rate=Math.max(0,n(key==='ore'?'oreRate':key==='essence'?'essenceRate':'sandRate'))+Math.max(0,Number(map[key])||0);
      return rate>0?target/rate:1e9;
    };
    return {
      hours,preserveHours,weights,
      oreHours:single(costs?.ore,'ore',weights.ore),
      essenceHours:single(costs?.essence,'essence',weights.essence),
      sandHours:single(costs?.sand,'sand',weights.sand),
      treatHours:0,
      treatFallback:Math.max(0,n('treatRate'))<=0
    };
  }
'''
text = text[:start] + helper + text[end:]

old_context = """    const cats=planningCategoryState(cfg,currentCaps,projectedCaps);\n    const gearOptions=buildGearOptions(baseGear,cfg,desired,projectedCaps.gear);\n    return {baseScore,desired,p,cfg,current,currentCaps,projectedCaps,baseGear,cats,gearOptions,charScore:characterScore(p,cfg)};\n"""
new_context = """    const cats=planningCategoryState(cfg,currentCaps,projectedCaps);\n    const gearOptions=buildGearOptions(baseGear,cfg,desired,projectedCaps.gear);\n    const lastOptionCost=options=>{\n      const last=Array.isArray(options)&&options.length?options[options.length-1]:null;\n      return Math.max(0,Number(last?.cost)||0);\n    };\n    // Total material still productively spendable from the CURRENT category levels up to\n    // the safe projected cap. This is independent of whichever candidate plan wins.\n    const headroomCosts={\n      essence:lastOptionCost(cats.skillOptions),\n      sand:lastOptionCost(cats.relicOptions),\n      treat:lastOptionCost(cats.fantoOptions)\n    };\n    return {baseScore,desired,p,cfg,current,currentCaps,projectedCaps,baseGear,cats,gearOptions,headroomCosts,charScore:characterScore(p,cfg)};\n"""
if text.count(old_context)!=1:
    raise SystemExit(f'planning context match count={text.count(old_context)}')
text=text.replace(old_context,new_context,1)

old_search = """    const context=ctx||createPlanningContext(baseScore,desired,p,cfg);\n    const {baseGear,cats,gearOptions,charScore}=context;\n    const realmDays=Number.isFinite(resources?.realmDays)?resources.realmDays:materialRealmDaysAvailable(cfg);\n"""
new_search = """    const context=ctx||createPlanningContext(baseScore,desired,p,cfg);\n    const {baseGear,cats,gearOptions,charScore,headroomCosts}=context;\n    const realmDays=Number.isFinite(resources?.realmDays)?resources.realmDays:materialRealmDaysAvailable(cfg);\n\n    // Dynamic usability compares remaining safe-cap demand with everything already available\n    // for that category. Spendable Realm tools count as material-equivalent supply; protected\n    // S2 tools do not, because realmInventoryFor() has already removed protected runs.\n    const essenceInv=realmInventoryFor('essence',cfg);\n    const sandInv=realmInventoryFor('sand',cfg);\n    resources.acquisitionHeadroomCosts=headroomCosts||{};\n    resources.acquisitionSupplyEquiv={\n      essence:Math.max(0,Number(resources?.essence)||0)+Math.max(0,Number(essenceInv?.banked)||0)*Math.max(0,realmYieldFor(resources,'essence')),\n      sand:Math.max(0,Number(resources?.sand)||0)+Math.max(0,Number(sandInv?.banked)||0)*Math.max(0,realmYieldFor(resources,'sand')),\n      treat:Math.max(0,Number(resources?.treat)||0)\n    };\n"""
if text.count(old_search)!=1:
    raise SystemExit(f'searchPlans header match count={text.count(old_search)}')
text=text.replace(old_search,new_search,1)

text=text.replace(
"      ? 'Minimize joint Cart + shared-Stamina reacquisition effort with a +50% Ore value premium for Gear runway.'\n      : 'Minimize joint Cart + shared-Stamina reacquisition effort, weighted by future usability.';",
"      ? 'Joint Cart + shared-Stamina efficiency with dynamic safe-cap headroom, plus a +50% Ore premium for Gear runway.'\n      : 'Joint Cart + shared-Stamina efficiency with dynamic safe-cap headroom for Essence, Sand and Treats.';",
1)
text=text.replace("const policy=optimizerMode()==='preserve'?'joint reacquisition + Ore premium':'joint reacquisition efficiency';",
                  "const policy=optimizerMode()==='preserve'?'dynamic headroom + Ore premium':'dynamic headroom acquisition efficiency';",1)

PATH.write_text(text,encoding='utf-8')
print('Applied dynamic safe-cap resource headroom weighting.')
