from pathlib import Path
import re

p=Path('index.html')
s=p.read_text(encoding='utf-8')
MARK='STAGE_AWARE_TOOL_SCARCITY_V1'
if MARK in s:
    print('Stage-aware tool scarcity v1 already applied.')
    raise SystemExit(0)

old_header="""  /* SCARCITY_ADJUSTED_ACQUISITION_V1 · TOOL_SCARCITY_CREDIT_V2 · POST_PLAN_SCARCITY_V4
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
  const POST_PLAN_SCARCITY_EXPONENT=2.20;
"""
new_header="""  /* SCARCITY_ADJUSTED_ACQUISITION_V1 · POST_PLAN_SCARCITY_V4 · STAGE_AWARE_TOOL_SCARCITY_V1
     Acquisition difficulty and projected scarcity are ONE economic metric, but the supply
     visible to that metric now follows the SAME hard sourcing stage as the candidate plan.
     Stage 0 (raw-only) sees ONLY projected raw material: saved/planned Realm tools cannot make
     raw Essence, Ore or Sand look artificially abundant. Stage 1+ may count saved + already-
     planned Realm tools at their FULL material equivalent because those tools are genuinely
     available once the planner has had to enter the tool tier. Extra purchases never add to
     starting scarcity supply, so the optimizer cannot justify buying tools by first pretending
     those hypothetical purchases are surplus. Strict source tiers remain
     raw -> saved/planned tools -> extra purchases. */
  const SURPLUS_ACQUISITION_FLOORS={ore:0.25,essence:0.25,sand:0.25,treat:0.00};
  const POST_PLAN_SCARCITY_MAX=2.50;
  const POST_PLAN_SCARCITY_EXPONENT=2.20;
"""
if old_header not in s: raise SystemExit('scarcity header anchor not found')
s=s.replace(old_header,new_header,1)

old_plan_supply="""  function plannedToolAcquisitionSupply(key,resources,cfg=activeCalcConfig()){
    if(key==='treat') return rawOnlyAcquisitionSupply(key,resources,cfg);
    const inv=realmInventoryFor(key,cfg);
    const perRun=Math.max(0,realmYieldFor(resources,key));
    const bankedMaterial=Math.max(0,Number(inv?.banked)||0)*perRun;
    return rawOnlyAcquisitionSupply(key,resources,cfg)+bankedMaterial*TOOL_SCARCITY_CREDIT;
  }
"""
new_plan_supply="""  function plannedToolAcquisitionSupply(key,resources,cfg=activeCalcConfig()){
    if(key==='treat') return rawOnlyAcquisitionSupply(key,resources,cfg);
    const inv=realmInventoryFor(key,cfg);
    const perRun=Math.max(0,realmYieldFor(resources,key));
    const bankedMaterial=Math.max(0,Number(inv?.banked)||0)*perRun;
    return rawOnlyAcquisitionSupply(key,resources,cfg)+bankedMaterial;
  }
  function acquisitionSupplyForStage(key,resources,stage=0,cfg=activeCalcConfig()){
    if(key==='treat' || Math.max(0,Math.floor(Number(stage)||0))<1){
      return rawOnlyAcquisitionSupply(key,resources,cfg);
    }
    // Stage 1 and Stage 2 may see only SAVED + already-planned tools. realmInventoryFor()
    // intentionally excludes any extra purchases invented by the candidate itself.
    return plannedToolAcquisitionSupply(key,resources,cfg);
  }
"""
if old_plan_supply not in s: raise SystemExit('planned tool supply anchor not found')
s=s.replace(old_plan_supply,new_plan_supply,1)

pat=re.compile(r"  /\* POST_PLAN_SCARCITY_V4\n.*?\n  function marginalWeightedCosts\(costs,resources,cfg=activeCalcConfig\(\)\)\{",re.S)
m=pat.search(s)
if not m: raise SystemExit('post-plan scarcity function block not found')
new_block="""  /* POST_PLAN_SCARCITY_V4 · STAGE_AWARE_TOOL_SCARCITY_V1
     Rank plans by the reserve they LEAVE inside the candidate's legal sourcing stage.
     Stage 0 uses raw supply only. Stage 1/2 may include saved + configured-plan tools at
     100% material equivalent, but extra candidate purchases never inflate starting supply.
     This keeps tool option value in the HARD source hierarchy instead of encoding another
     arbitrary percentage inside scarcity itself.

     Treats intentionally keep the prior headroom integral because the exact Treat-funded
     fast path relies on a fully funded Treat cap having zero marginal acquisition cost. */
  function marginalWeightedSpend(amount,key,resources,stage=0,cfg=activeCalcConfig()){
    const amountTotal=Math.max(0,Number(amount)||0);
    if(amountTotal<=0) return 0;

    const floor=Math.max(0,Math.min(1,Number(SURPLUS_ACQUISITION_FLOORS[key])||0));
    const usefulNeed=Math.max(0,Number(resources?.acquisitionHeadroomCosts?.[key])||0);
    const available=Math.max(0,acquisitionSupplyForStage(key,resources,stage,cfg));
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

    const rawAvailable=Math.max(0,rawOnlyAcquisitionSupply(key,resources,cfg));
    const toolAvailable=Math.max(0,available-rawAvailable);
    const rawSpend=Math.min(productive,rawAvailable);
    const toolMaterialSpend=Math.max(0,productive-rawAvailable);
    const poolSpend=Math.min(available,rawSpend+Math.min(toolAvailable,toolMaterialSpend));

    // Fraction of the supply visible in THIS sourcing stage consumed by THIS candidate.
    // A raw-only plan is therefore completely invariant to saved tool counts.
    const spentFraction=available>1e-9
      ? Math.max(0,Math.min(1,poolSpend/available))
      : (productive>0?1:0);
    const multiplier=floor+(POST_PLAN_SCARCITY_MAX-floor)*Math.pow(spentFraction,POST_PLAN_SCARCITY_EXPONENT);
    let effective=productive*multiplier;

    // Material beyond the existing supply visible to this stage is maximally scarce.
    // Stage 2 can still be legal via extra Realm purchases; those purchases just cannot
    // retroactively make the pool look abundant.
    if(productive>available+1e-9){
      const over=productive-available;
      effective+=over*(POST_PLAN_SCARCITY_MAX-multiplier);
    }
    if(amountTotal>productive) effective+=(amountTotal-productive)*POST_PLAN_SCARCITY_MAX;
    return effective;
  }

  function marginalWeightedCosts(costs,resources,cfg=activeCalcConfig(),stage=0){"""
s=s[:m.start()]+new_block+s[m.end():]

old_cost_body="""    return {
      ore:marginalWeightedSpend(costs?.ore,'ore',resources),
      essence:marginalWeightedSpend(costs?.essence,'essence',resources),
      sand:marginalWeightedSpend(costs?.sand,'sand',resources),
      treat:marginalWeightedSpend(costs?.treat,'treat',resources)
    };
  }
"""
new_cost_body="""    return {
      ore:marginalWeightedSpend(costs?.ore,'ore',resources,stage,cfg),
      essence:marginalWeightedSpend(costs?.essence,'essence',resources,stage,cfg),
      sand:marginalWeightedSpend(costs?.sand,'sand',resources,stage,cfg),
      treat:marginalWeightedSpend(costs?.treat,'treat',resources,stage,cfg)
    };
  }
"""
if old_cost_body not in s: raise SystemExit('marginal cost body anchor not found')
s=s.replace(old_cost_body,new_cost_body,1)

old_effort="""  function acquisitionEffortFor(costs,resources,cfg=activeCalcConfig()){
    const marginalCosts=marginalWeightedCosts(costs,resources,cfg);
    return {hours:jointReacquisitionHours(marginalCosts,resources,cfg)};
  }
"""
new_effort="""  function acquisitionEffortFor(costs,resources,cfg=activeCalcConfig(),stage=0){
    const normalizedStage=Math.max(0,Math.min(2,Math.floor(Number(stage)||0)));
    const marginalCosts=marginalWeightedCosts(costs,resources,cfg,normalizedStage);
    return {hours:jointReacquisitionHours(marginalCosts,resources,cfg),stage:normalizedStage};
  }
"""
if old_effort not in s: raise SystemExit('acquisition effort anchor not found')
s=s.replace(old_effort,new_effort,1)

old_stage="""  function candidateRealmStage(candidate){
    const realms=['ore','essence','sand'].map(k=>candidate?.realm?.[k]).filter(Boolean);
    // A Treat shortage is a hard resource failure because there is no Fantomon-Treat
    // Material Realm tool. Diagnostics therefore rank it after all actually fundable stages.
    if(Math.max(0,Number(candidate?.treatShortfall)||0)>0.5) return 3;
    if(realms.some(x=>Math.max(0,Number(x?.packs)||0)>0 || Math.max(0,Number(x?.paidRunsUsed)||0)>0)) return 2;
    const usesRealmTools=realms.some(x=>{
      const planRuns=Number.isFinite(Number(x?.planRuns)) ? Number(x.planRuns) : Number(x?.runsUsed)||0;
      return planRuns>0;
    });
    return usesRealmTools?1:0;
  }
"""
new_stage="""  function realmStageForTopups(realms,treatShortfall=0){
    const list=(realms||[]).filter(Boolean);
    if(Math.max(0,Number(treatShortfall)||0)>0.5) return 3;
    if(list.some(x=>Math.max(0,Number(x?.packs)||0)>0 || Math.max(0,Number(x?.paidRunsUsed)||0)>0)) return 2;
    const usesRealmTools=list.some(x=>{
      const planRuns=Number.isFinite(Number(x?.planRuns)) ? Number(x.planRuns) : Number(x?.runsUsed)||0;
      return planRuns>0;
    });
    return usesRealmTools?1:0;
  }
  function candidateRealmStage(candidate){
    const realms=['ore','essence','sand'].map(k=>candidate?.realm?.[k]).filter(Boolean);
    return realmStageForTopups(realms,candidate?.treatShortfall);
  }
"""
if old_stage not in s: raise SystemExit('candidate stage anchor not found')
s=s.replace(old_stage,new_stage,1)

old_supply_block="""    // Scarcity RANKING can see saved + already-planned Realm tools at 80% material credit;
    // Realm FEASIBILITY remains strictly raw-first because realmTopupFor still compares each
    // candidate cost against the raw projected budget before consuming any tools. Extra tool
    // purchases are not included here, avoiding circular 'buy it because it is abundant' logic.
    resources.acquisitionHeadroomCosts=headroomCosts||{};
    resources.acquisitionSupplyEquiv={
      ore:plannedToolAcquisitionSupply('ore',resources,cfg),
      essence:plannedToolAcquisitionSupply('essence',resources,cfg),
      sand:plannedToolAcquisitionSupply('sand',resources,cfg),
      treat:rawOnlyAcquisitionSupply('treat',resources,cfg)
    };
"""
new_supply_block="""    // Keep a raw-only snapshot for diagnostics/legacy readers. The actual acquisition kernel
    // chooses its scarcity supply per candidate stage via acquisitionSupplyForStage().
    resources.acquisitionHeadroomCosts=headroomCosts||{};
    resources.acquisitionSupplyEquiv={
      ore:rawOnlyAcquisitionSupply('ore',resources,cfg),
      essence:rawOnlyAcquisitionSupply('essence',resources,cfg),
      sand:rawOnlyAcquisitionSupply('sand',resources,cfg),
      treat:rawOnlyAcquisitionSupply('treat',resources,cfg)
    };
"""
if old_supply_block not in s: raise SystemExit('search supply block anchor not found')
s=s.replace(old_supply_block,new_supply_block,1)

pat=re.compile(r"    /\* ACQUISITION_KERNEL_V2\n       This metric is evaluated in the hottest optimizer loop\..*?    const acquisitionFor=\(go,so,ro,fo\)=>\(\{hours:jointHoursFast\(go\.__acqOreV1,so\.__acqEssenceV1,ro\.__acqSandV1,fo\.__acqTreatV1\)\}\);",re.S)
m=pat.search(s)
if not m: raise SystemExit('acquisition kernel block anchor not found')
new_kernel="""    /* ACQUISITION_KERNEL_V3 · STAGE_AWARE_TOOL_SCARCITY_V1
       Precompute TWO scarcity prices per structural option: raw-stage and tool-stage.
       This keeps the hot combinational search fast while ensuring a raw-only candidate is
       completely blind to tool inventory. Stage 1/2 reuse the full saved/planned-tool pool;
       extra purchases never enter that pool. */
    for(const go of gearOptions){
      go.__acqOreRawV3=marginalWeightedSpend(go.oreCost,'ore',resources,0,cfg);
      go.__acqOreToolV3=marginalWeightedSpend(go.oreCost,'ore',resources,1,cfg);
    }
    for(const so of cats.skillOptions){
      so.__acqEssenceRawV3=marginalWeightedSpend(so.cost,'essence',resources,0,cfg);
      so.__acqEssenceToolV3=marginalWeightedSpend(so.cost,'essence',resources,1,cfg);
    }
    for(const ro of cats.relicOptions){
      ro.__acqSandRawV3=marginalWeightedSpend(ro.cost,'sand',resources,0,cfg);
      ro.__acqSandToolV3=marginalWeightedSpend(ro.cost,'sand',resources,1,cfg);
    }
    for(const fo of cats.fantoOptions){
      fo.__acqTreatRawV3=marginalWeightedSpend(fo.cost,'treat',resources,0,cfg);
      fo.__acqTreatToolV3=fo.__acqTreatRawV3;
    }
    const acqMap=resources?.yields?.map||cfg.map||{};
    const acqCartOre=Math.max(0,n('oreRate'));
    const acqCartEssence=Math.max(0,n('essenceRate'));
    const acqCartSand=Math.max(0,n('sandRate'));
    const acqCartTreat=Math.max(0,n('treatRate'));
    const acqNodeOre=Math.max(0,Number(acqMap.ore)||0);
    const acqNodeEssence=Math.max(0,Number(acqMap.essence)||0);
    const acqNodeSand=Math.max(0,Number(acqMap.sand)||0);
    const jointHoursFast=(oreRaw,essRaw,sandRaw,treatRaw)=>{
      const ore=Math.max(0,Number(oreRaw)||0);
      const essence=Math.max(0,Number(essRaw)||0);
      const sand=Math.max(0,Number(sandRaw)||0);
      const treat=Math.max(0,Number(treatRaw)||0);
      let floor=0;
      if(treat>0){
        if(acqCartTreat<=0) return 1e9;
        floor=Math.max(floor,treat/acqCartTreat);
      }
      if(ore>0&&acqNodeOre<=0){if(acqCartOre<=0)return 1e9;floor=Math.max(floor,ore/acqCartOre);}
      if(essence>0&&acqNodeEssence<=0){if(acqCartEssence<=0)return 1e9;floor=Math.max(floor,essence/acqCartEssence);}
      if(sand>0&&acqNodeSand<=0){if(acqCartSand<=0)return 1e9;floor=Math.max(floor,sand/acqCartSand);}
      const nodesAt=hours=>{
        let total=0,rem=0;
        rem=Math.max(0,ore-acqCartOre*hours);if(rem>0){if(acqNodeOre<=0)return Infinity;total+=rem/acqNodeOre;}
        rem=Math.max(0,essence-acqCartEssence*hours);if(rem>0){if(acqNodeEssence<=0)return Infinity;total+=rem/acqNodeEssence;}
        rem=Math.max(0,sand-acqCartSand*hours);if(rem>0){if(acqNodeSand<=0)return Infinity;total+=rem/acqNodeSand;}
        return total;
      };
      if(nodesAt(floor)<=floor+1e-9) return floor;
      let mask=0;
      if(ore>acqCartOre*floor+1e-9&&acqNodeOre>0) mask|=1;
      if(essence>acqCartEssence*floor+1e-9&&acqNodeEssence>0) mask|=2;
      if(sand>acqCartSand*floor+1e-9&&acqNodeSand>0) mask|=4;
      let hours=floor;
      for(let pass=0;pass<4;pass++){
        let numerator=0,denominator=1;
        if(mask&1){numerator+=ore/acqNodeOre;denominator+=acqCartOre/acqNodeOre;}
        if(mask&2){numerator+=essence/acqNodeEssence;denominator+=acqCartEssence/acqNodeEssence;}
        if(mask&4){numerator+=sand/acqNodeSand;denominator+=acqCartSand/acqNodeSand;}
        hours=Math.max(floor,numerator/denominator);
        let next=0;
        if((mask&1)&&ore>acqCartOre*hours+1e-9) next|=1;
        if((mask&2)&&essence>acqCartEssence*hours+1e-9) next|=2;
        if((mask&4)&&sand>acqCartSand*hours+1e-9) next|=4;
        if(next===mask){
          if(nodesAt(hours)<=hours+1e-7) return hours;
          break;
        }
        mask=next;
        if(!mask) return floor;
      }
      let lo=floor,hi=Math.max(1,hours,floor);
      while(nodesAt(hi)>hi+1e-9&&hi<1e9) hi*=2;
      if(hi>=1e9&&nodesAt(hi)>hi+1e-9) return 1e9;
      for(let i=0;i<48;i++){
        const mid=(lo+hi)/2;
        if(nodesAt(mid)<=mid) hi=mid; else lo=mid;
      }
      return hi;
    };
    const acquisitionFor=(go,so,ro,fo,stage=0)=>{
      const normalizedStage=Math.max(0,Math.min(2,Math.floor(Number(stage)||0)));
      const toolStage=normalizedStage>=1;
      return {
        hours:jointHoursFast(
          toolStage?go.__acqOreToolV3:go.__acqOreRawV3,
          toolStage?so.__acqEssenceToolV3:so.__acqEssenceRawV3,
          toolStage?ro.__acqSandToolV3:ro.__acqSandRawV3,
          fo.__acqTreatRawV3
        ),
        stage:normalizedStage
      };
    };"""
s=s[:m.start()]+new_kernel+s[m.end():]

# Every manual hot-loop acquisition calculation has a local `realms` array by construction.
old_call="const acquisition=acquisitionFor(go,so,ro,fo);"
call_count=s.count(old_call)
if call_count<1: raise SystemExit('no acquisitionFor hot-loop calls found')
s=s.replace(old_call,"const acquisition=acquisitionFor(go,so,ro,fo,realmStageForTopups(realms));")
print(f'Updated {call_count} hot-loop acquisition calls to stage-aware pricing.')

old_make_comment="""    /* ACQUISITION_KERNEL_V2
       Scarcity coverage is fixed for one resource snapshot, including the 80% credit for
       saved/planned tools. Feasibility/source stage is still decided separately by Realm
       top-up math. Therefore the hot search can reuse its precomputed acquisition result
       for raw AND tool-backed candidates instead of recalculating logarithms/DOM rates for
       every candidate combination. */
    const acquisition=acquisitionResult||acquisitionEffortFor({ore:go.oreCost,essence:so.cost,sand:ro.cost,treat:fo.cost},resources,activeCalcConfig());
"""
new_make_comment="""    /* ACQUISITION_KERNEL_V3
       Candidate acquisition economics must match the candidate's hard source stage.
       Hot-loop callers pass the matching precomputed raw/tool kernel. The fallback below
       self-corrects any caller that supplies an acquisition result for the wrong stage. */
    const candidateStage=realmStageForTopups(realms);
    const acquisition=(acquisitionResult&&Number(acquisitionResult.stage)===candidateStage)
      ? acquisitionResult
      : acquisitionEffortFor({ore:go.oreCost,essence:so.cost,sand:ro.cost,treat:fo.cost},resources,activeCalcConfig(),candidateStage);
"""
if old_make_comment not in s: raise SystemExit('makePlan acquisition anchor not found')
s=s.replace(old_make_comment,new_make_comment,1)

old_method="""Saved + already-planned Realm tools contribute <b>80%</b> of their material-equivalent value to that pool, preserving a 20% option-value premium; extra recommended purchases never count as surplus. Raw feasibility still comes first, so tools remain untouched whenever a raw-only goal plan exists."""
new_method="""Tool scarcity is <b>source-stage aware</b>: while the winning route is raw-only, Hammers/Knuckles/Shovels contribute <b>0%</b> to scarcity and cannot make a raw pool look artificially abundant. If raw cannot fund the goal and the planner enters the saved/planned-tool tier, those already-owned/already-configured tools count at their <b>full material equivalent</b>. Extra recommended purchases never count as starting surplus. Raw feasibility still comes first, so tools remain untouched whenever a raw-only goal plan exists."""
if old_method not in s: raise SystemExit('method text 80% anchor not found')
s=s.replace(old_method,new_method,1)

# Clean stale implementation comments that would otherwise contradict the new rule.
s=s.replace('including 80%-credited saved/\n       planned tools','with source-stage-aware saved/planned tools')
s=s.replace('including the 80% credit for\n       saved/planned tools','using the candidate source stage')

if 'TOOL_SCARCITY_CREDIT' in s:
    raise SystemExit('stale TOOL_SCARCITY_CREDIT reference remains after patch')
if MARK not in s:
    raise SystemExit('stage-aware marker missing after patch')

p.write_text(s,encoding='utf-8')
print('Applied stage-aware tool scarcity v1.')
