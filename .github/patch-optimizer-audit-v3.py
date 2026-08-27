from pathlib import Path
import re

PATH=Path('index.html')
text=PATH.read_text(encoding='utf-8')
MARKER='OPTIMIZER_AUDIT_V3'
if MARKER in text:
    print('Optimizer audit v3 already applied.')
    raise SystemExit(0)


def sub_once(pattern,repl,label,flags=re.S):
    global text
    text2,count=re.subn(pattern,repl,text,count=1,flags=flags)
    if count!=1:
        raise SystemExit(f'{label}: expected 1 match, got {count}')
    text=text2

# 1) Reserve-aware acquisition supply. This is the maximum CURRENT-season-equivalent
# material that can be spent while still satisfying the enabled S2 reserve with some
# combination of remaining raw + carried tools. It does not pre-lock raw unnecessarily.
anchor="  const ORE_PRESERVE_PREMIUM=0.50;\n\n  function dynamicAcquisitionWeights(resources){"
if text.count(anchor)!=1:
    raise SystemExit(f'optimizer constants anchor count={text.count(anchor)}')
helper=r'''  const ORE_PRESERVE_PREMIUM=0.50;

  /* OPTIMIZER_AUDIT_V3
     Resource scarcity is evaluated against supply that is genuinely safe to spend after
     enabled S2 reserves. Raw and carried tools can trade off: whichever combination leaves
     the most current-season material available while still funding the reserve is used. */
  function reserveAdjustedAcquisitionSupply(key,resources,cfg=activeCalcConfig()){
    const raw=Math.max(0,Number(resources?.[key])||0);
    const reserve=Math.max(0,reserveTargetFor(key,resources,cfg));
    if(key==='treat') return Math.max(0,raw-reserve);
    if(key!=='essence'&&key!=='sand') return raw;

    const inv=realmInventoryFor(key,cfg);
    const tools=Math.max(0,Math.floor(Number(inv?.banked)||0));
    const currentPer=Math.max(0,realmYieldFor(resources,key));
    if(reserve<=0) return raw+tools*currentPer;

    const reservePer=Math.max(0,reserveYieldFor(key,cfg));
    if(reservePer<=0) return Math.max(0,raw-reserve)+tools*currentPer;

    // The objective is piecewise linear in reserved tool count, so only the boundary
    // choices can win. Include the minimum feasible reserve-tool count and the floor/ceil
    // around the all-tool reserve point to handle the final partial tool exactly.
    const minTools=Math.max(0,Math.min(tools,Math.ceil(Math.max(0,reserve-raw)/reservePer)));
    const floorTools=Math.max(0,Math.min(tools,Math.floor(reserve/reservePer)));
    const ceilTools=Math.max(0,Math.min(tools,Math.ceil(reserve/reservePer)));
    let best=0,feasible=false;
    for(const held of new Set([minTools,floorTools,ceilTools,tools])){
      const rawHeld=Math.max(0,reserve-held*reservePer);
      if(rawHeld>raw+1e-9) continue;
      feasible=true;
      const spendable=Math.max(0,raw-rawHeld)+Math.max(0,tools-held)*currentPer;
      if(spendable>best) best=spendable;
    }
    return feasible?best:0;
  }

  function dynamicAcquisitionWeights(resources){'''
text=text.replace(anchor,helper,1)

# 2) Moving-headroom marginal pricing. Spending a category resource both reduces supply
# AND buys the upgrades that reduce the remaining useful cap demand. The old curve only
# reduced supply, which made large legitimate category spends become scarce too quickly.
sub_once(
    r"  function marginalWeightedSpend\(amount,key,resources\)\{.*?\n  \}\n\n  function marginalWeightedCosts",
    r'''  function marginalWeightedSpend(amount,key,resources){
    const amountTotal=Math.max(0,Number(amount)||0);
    if(amountTotal<=0) return 0;
    if(key==='ore') return amountTotal;

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
  }

  function marginalWeightedCosts''',
    'moving-headroom marginal pricing'
)

# 3) Use reserve-adjusted supply in the scarcity model rather than gross raw + every tool.
sub_once(
    r"    const essenceInv=realmInventoryFor\('essence',cfg\);\n    const sandInv=realmInventoryFor\('sand',cfg\);\n    resources\.acquisitionHeadroomCosts=headroomCosts\|\|\{\};\n    resources\.acquisitionSupplyEquiv=\{.*?\n    \};",
    r'''    resources.acquisitionHeadroomCosts=headroomCosts||{};
    resources.acquisitionSupplyEquiv={
      essence:reserveAdjustedAcquisitionSupply('essence',resources,cfg),
      sand:reserveAdjustedAcquisitionSupply('sand',resources,cfg),
      treat:reserveAdjustedAcquisitionSupply('treat',resources,cfg)
    };''',
    'reserve-adjusted acquisition supply'
)

# 4) Credit current-season Realm overage before calculating the S2 reserve gap. If the
# final Knuckle/Shovel used for the S1 plan produces more than the exact shortfall, that
# excess is real raw material and should reduce the reserve tool requirement.
sub_once(
    r"  function reserveAwareRealmTopupFor\(key,planCost,rawBudget,resources,cfg=activeCalcConfig\(\),p=null\)\{.*?\n  \}\n\n  function formatRealmSchedule",
    r'''  function reserveAwareRealmTopupFor(key,planCost,rawBudget,resources,cfg=activeCalcConfig(),p=null){
    if(cfg.key!=='s1' || (key!=='essence'&&key!=='sand')) return realmTopupFor(key,planCost,rawBudget,resources,cfg,p);
    const raw=Math.max(0,Number(rawBudget)||0);
    const cost=Math.max(0,Number(planCost)||0);
    const reserveTarget=reserveTargetFor(key,resources,cfg);
    const planPerRun=Math.max(0,realmYieldFor(resources,key));
    const reservePerRun=Math.max(0,reserveYieldFor(key,cfg));
    const rawPlanShortfall=Math.max(0,cost-raw);
    const planRuns=rawPlanShortfall>0&&planPerRun>0?Math.ceil(rawPlanShortfall/planPerRun):(rawPlanShortfall>0?Infinity:0);
    const planProvided=Number.isFinite(planRuns)?planRuns*planPerRun:0;
    const rawAfterPlan=Math.max(0,raw+planProvided-cost);
    const reserveGap=Math.max(0,reserveTarget-rawAfterPlan);
    const reserveRuns=reserveGap>0&&reservePerRun>0?Math.ceil(reserveGap/reservePerRun):(reserveGap>0?Infinity:0);
    if(!Number.isFinite(planRuns)||!Number.isFinite(reserveRuns)){
      const inv=realmInventoryFor(key,cfg);
      return {feasible:false,unsupported:true,shortfall:rawPlanShortfall+reserveGap,runsNeeded:Infinity,runsUsed:0,bankedUsed:0,bankedRemaining:inv.banked,packs:Infinity,attempts:Infinity,purchasedRuns:0,sparePurchasedRuns:0,dawnium:Infinity,days:Number.isFinite(resources?.realmDays)?resources.realmDays:materialRealmDaysAvailable(cfg),dailyCounts:[],provided:0,maxPacks:0,maxAttempts:0,maxRuns:inv.banked,maxProvided:0,remainingAfterMax:rawPlanShortfall+reserveGap,baselinePerDay:inv.baselineRefreshes,planRuns:0,reserveRuns:0,planProvided:0,reserveProvided:0,reserveGap,rawAfterPlan,reserveTarget};
    }
    const totalRuns=planRuns+reserveRuns;
    const inv=realmInventoryFor(key,cfg);
    const days=Number.isFinite(resources?.realmDays)?resources.realmDays:materialRealmDaysAvailable(cfg);
    const top=realmTopup(totalRuns,0,1,days,inv.banked,inv.baselineRefreshes);
    const reserveProvided=reserveRuns*reservePerRun;
    return {...top,
      shortfall:rawPlanShortfall+reserveGap,
      runsNeeded:totalRuns,runsUsed:totalRuns,
      provided:planProvided,
      planRuns,reserveRuns,planProvided,reserveProvided,
      planShortfall:rawPlanShortfall,reserveGap,rawAfterPlan,reserveTarget,
      reservePerRun,planPerRun,
      remainingRunsAfterMax:Math.max(0,Number(top.remainingAfterMax)||0)
    };
  }

  function formatRealmSchedule''',
    'Realm overage reserve credit'
)

# 5) Auto-Stamina's cycle/stability chooser must use the SAME feasible-plan objective as
# the main optimizer. Previously it put Realm pack count ahead of acquisition efficiency.
sub_once(
    r"    const betterState=\(state,best\)=>\{.*?\n    \};\n\n    for\(let pass=0;pass<5;pass\+\+\)\{",
    r'''    const betterState=(state,best)=>{
      if(!best) return true;
      const cp=state.result.plan, bp=best.result.plan;
      if(!!cp!==!!bp) return !!cp;
      if(cp&&bp){
        if(betterFeasibleCandidate(cp,bp)) return true;
        if(betterFeasibleCandidate(bp,cp)) return false;
        return false;
      }
      const cd=state.result.diagnostic, bd=best.result.diagnostic;
      if(cd&&bd) return betterDiagnosticCandidate(cd,bd);
      return !!cd;
    };

    for(let pass=0;pass<5;pass++){''',
    'Auto-Stamina objective alignment'
)

# 6) Documentation/comment cleanup. The implementation has been +50% for a while; a few
# old +75% strings and pre-lock reserve descriptions survived older patch layers.
text=text.replace('bounded +75% Ore premium','bounded +50% Ore premium')
text=text.replace('acquisition effort + 75% Ore premium','acquisition effort + 50% Ore premium')
text=text.replace('applies a 75% strategic premium to Ore/Hammers','applies a 50% strategic premium to Ore/Hammers')
text=text.replace(
    'Carried Knuckles satisfy this reserve first, with raw Essence protected only for any remainder. That protected amount is not spendable by the S1 optimizer.',
    'The S1 plan spends raw Essence normally; after the plan, leftover raw Essence covers the reserve first and Knuckles cover only any remaining reserve gap.'
)
text=text.replace(
    'Reserved Shovels are removed from the S1 spendable Realm pool.',
    'Sand follows the same post-plan raw-first rule: leftover raw Sand covers the reserve before Shovels are assigned to any gap.'
)

PATH.write_text(text,encoding='utf-8')
print('Applied optimizer audit v3: moving headroom, reserve-aware supply, Realm overage credit, and unified Auto-Stamina objective.')
