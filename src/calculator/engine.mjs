
import { activeCalcConfig, gearScore, characterScore, buildCategoryOptionsFromLevels, categoryInputCapsForCharacter, gearStepCost, gearStepRefined, skillStepCost, relicStepSand, fantoStepTreatCost, applyStaminaAllocation, realmYieldFor, realmTopup, firstGearOptionAtLeast, TOOL_SCARCITY_CREDIT, rawOnlyAcquisitionSupply, marginalWeightedSpend, marginalWeightedCosts, candidateRealmStage, betterFeasibleCandidate, betterDiagnosticCandidate } from './model.mjs';
export function createPlannerEngine(__calculatorDeps){
/* AUTO_STAMINA_EXACT_THREE_V1
     Auto Stamina has exactly three legal strategies: all Ore, all Essence, or all Sand.
     Solve each legal resource state directly and compare the globally optimal score plan
     from each state. This is both more exact and cheaper than the old alternating solver,
     which could run the full optimizer up to six times while chasing a fixed point.

     If safe raw inventory already funds every reachable Ore/Essence/Sand upgrade through
     the projected cap, Stamina cannot change feasibility or marginal scarcity. In that
     common surplus case solve once and bank the otherwise-unused nodes as Ore. */
function solveTargetWithAutoStamina(baseScore,desired,p,baseResources,cfg=activeCalcConfig()){
    const ctx=createPlanningContext(baseScore,desired,p,cfg);
    // Below the verified S2 Lv.120 map bracket, keep Stamina out of the numeric budget rather than guessing yields.
    if(!baseResources.yields?.mapReady){
      const allocation={ore:0,essence:0,sand:0,rolla:0,unassigned:baseResources.staminaNodes||0};
      const resources=applyStaminaAllocation(baseResources,allocation,cfg);
      const result=searchPlans(baseScore,desired,p,resources,cfg,ctx);
      return {plan:result.plan,diagnostic:result.plan||result.diagnostic,resources,allocation};
    }
    // Manual Stamina destinations do not depend on a score plan; apply them once and solve normally.
    if(__calculatorDeps.staminaMode()!=='auto'){
      const allocation=__calculatorDeps.allocateStaminaForPlan(null,baseResources,cfg,p);
      const resources=applyStaminaAllocation(baseResources,allocation,cfg);
      const result=searchPlans(baseScore,desired,p,resources,cfg,ctx);
      return {plan:result.plan,diagnostic:result.plan||result.diagnostic,resources,allocation};
    }
    const total=Math.max(0,Math.floor(baseResources.staminaNodes||0));
    const map=baseResources.yields?.map||{};
    const empty={ore:0,essence:0,sand:0,rolla:0,unassigned:0};
    const resultState=(allocation)=>{
      const resources=applyStaminaAllocation(baseResources,allocation,cfg);
      const result=searchPlans(baseScore,desired,p,resources,cfg,ctx);
      return {plan:result.plan,diagnostic:result.plan||result.diagnostic,resources,allocation,result};
    };
    const betterState=(state,best)=>{
      if(!best) return true;
      const cp=state.result.plan,bp=best.result.plan;
      if(!!cp!==!!bp) return !!cp;
      if(cp&&bp){
        if(betterFeasibleCandidate(cp,bp)) return true;
        if(betterFeasibleCandidate(bp,cp)) return false;
        return false;
      }
      const cd=state.result.diagnostic,bd=best.result.diagnostic;
      if(cd&&bd){
        if(betterDiagnosticCandidate(cd,bd)) return true;
        if(betterDiagnosticCandidate(bd,cd)) return false;
      }
      return !!cd&&!bd;
    };
    // Surplus fast path: every reachable raw-material category is already fully funded.
    // Extra Stamina cannot alter candidate feasibility or the marginal scarcity weights.
    const maxGearOre=Math.max(0,Number(ctx.gearOptions?.[ctx.gearOptions.length-1]?.oreCost)||0);
    const fullyRawFunded=
      (Number(baseResources.ore)||0)>=maxGearOre-0.5 &&
      (Number(baseResources.essence)||0)>=Math.max(0,Number(ctx.headroomCosts?.essence)||0)-0.5 &&
      (Number(baseResources.sand)||0)>=Math.max(0,Number(ctx.headroomCosts?.sand)||0)-0.5;
    if(fullyRawFunded){
      const allocation=(Number(map.ore)||0)>0?{...empty,ore:total}:{...empty,unassigned:total};
      const state=resultState(allocation);
      return {plan:state.result.plan,diagnostic:state.result.plan||state.result.diagnostic,resources:state.resources,allocation:state.allocation};
    }
    // Evaluate the complete legal Auto-Stamina state space directly: at most three searches.
    let bestState=null;
    for(const key of ['ore','essence','sand']){
      if((Number(map[key])||0)<=0) continue;
      const state=resultState({...empty,[key]:total});
      if(betterState(state,bestState)) bestState=state;
    }
    if(bestState){
      return {plan:bestState.result.plan,diagnostic:bestState.result.plan||bestState.result.diagnostic,resources:bestState.resources,allocation:bestState.allocation};
    }
    const allocation={...empty,unassigned:total};
    const state=resultState(allocation);
    return {plan:state.result.plan,diagnostic:state.result.plan||state.result.diagnostic,resources:state.resources,allocation};
  }

function materialRealmDaysAvailable(cfg=activeCalcConfig()){
    if(__calculatorDeps.upgradeFinishCutoffMs(cfg)<=Date.now()) return 0;
    // Current server-day window + each future 6 AM reset strictly before the planner cutoff.
    return 1+__calculatorDeps.futureRealmPurchaseDays(cfg);
  }

function realmInventoryFor(key,cfg=activeCalcConfig()){
    const ids={ore:'hammerCurrent',essence:'knucklesCurrent',sand:'shovelCurrent'};
    const id=ids[key];
    const manualBanked=id?Math.max(0,Math.floor(__calculatorDeps.n(id,0))):0;
    const plannedRuns=__calculatorDeps.plannedRealmRunsFor(key,cfg);
    return {banked:Math.max(0,manualBanked+plannedRuns),manualBanked,plannedRuns,protectedRuns:0,baselineRefreshes:__calculatorDeps.realmDailyValue(key)};
  }

function realmTopupFor(key,resourceCost,projectedBudget,resources,cfg=activeCalcConfig(),p=null){
    const inv=realmInventoryFor(key,cfg);
    let perRun=realmYieldFor(resources,key);
    // S2 tools can be bought/banked before Lv.120 and spent once the max bracket is reached.
    // If the projection never reaches Lv.120, do not invent a lower-bracket yield.
    if(cfg.key==='s2' && Math.floor((p?.decimal??p?.level??__calculatorDeps.n('charLevel',100)))<cfg.realmMaxLevel) perRun=0;
    return realmTopup(resourceCost,projectedBudget,perRun,Number.isFinite(resources?.realmDays)?resources.realmDays:materialRealmDaysAvailable(cfg),inv.banked,inv.baselineRefreshes);
  }

function buildGearOptions(baseGear,cfg,scoreTarget=0,hardCap=cfg.gearCap){
    const out=[{adds:0,target:baseGear.slice(),score:gearScore(baseGear,cfg),oreCost:0,refinedCost:0}];
    if(__calculatorDeps.gearLocked) return out;
    const t=baseGear.slice();
    let oreCost=0,refinedCost=0,adds=0;
    const effectiveCap=Number.isFinite(hardCap)?Math.floor(hardCap):Infinity;
    const scoreGap=Math.max(0,(Number(scoreTarget)||0)-gearScore(baseGear,cfg));
    const targetLimited=Math.min(2500,Math.max(40,Math.ceil(scoreGap/Math.max(1,cfg.weights.gear))+80));
    const maxAdds=Number.isFinite(effectiveCap)
      ? t.reduce((sum,l)=>sum+Math.max(0,effectiveCap-l),0)
      : targetLimited;
    for(let k=0;k<maxAdds;k++){
      let idx=0;
      for(let i=1;i<t.length;i++) if(t[i]<t[idx]) idx=i;
      if(Number.isFinite(effectiveCap) && t[idx]>=effectiveCap) break;
      oreCost+=gearStepCost(t[idx],cfg);
      refinedCost+=gearStepRefined(t[idx]);
      t[idx]++; adds++;
      out.push({adds,target:t.slice(),score:gearScore(t,cfg),oreCost,refinedCost});
    }
    return out;
  }

function planningCategoryState(cfg,currentCaps,projectedCaps){
    const skill=__calculatorDeps.categoryStateFromUser('skillLevel','exactSkillLevels',8,100,currentCaps.skill,cfg.scoreFloor,cfg.weights.skill,cfg.key==='s2'?100:122);
    const relic=__calculatorDeps.categoryStateFromUser('relicLevel','exactRelicLevels',20,10,currentCaps.relic,cfg.relicFloor,cfg.weights.relic,cfg.key==='s2'?10:13);
    const fanto=__calculatorDeps.categoryStateFromUser('fantomonLevel','exactFantoLevels',4,100,currentCaps.fanto,cfg.scoreFloor,cfg.weights.fanto,cfg.key==='s2'?100:130);
    return {
      skill,relic,fanto,
      skillOptions:buildCategoryOptionsFromLevels(skill.levels,Math.max(Math.ceil(skill.avg),projectedCaps.skill),cfg.scoreFloor,cfg.weights.skill,l=>skillStepCost(l,cfg)),
      relicOptions:cfg.optimizeRelic?buildCategoryOptionsFromLevels(relic.levels,Math.max(Math.ceil(relic.avg),projectedCaps.relic),cfg.relicFloor,cfg.weights.relic,l=>relicStepSand(l,cfg),1):[{...relic,cost:0,adds:0}],
      fantoOptions:cfg.optimizeFanto?buildCategoryOptionsFromLevels(fanto.levels,Math.max(Math.ceil(fanto.avg),projectedCaps.fanto),cfg.scoreFloor,cfg.weights.fanto,l=>fantoStepTreatCost(l,cfg),10):[{...fanto,cost:0,adds:0}]
    };
  }

// Structural upgrade options do not depend on the projected resource mix. Build them once
  // and reuse them across the auto-Stamina passes instead of rebuilding thousands of arrays.
function createPlanningContext(baseScore,desired,p,cfg=activeCalcConfig()){
    const current=__calculatorDeps.characterSnapshot(cfg);
    const currentCaps=categoryInputCapsForCharacter(current.level,cfg);
    const projectedCaps=__calculatorDeps.optimizerCategoryCaps(p,cfg);
    const baseGear=__calculatorDeps.gearStateFromUser(cfg,currentCaps.gear,cfg.key==='s2'?130:143).levels.slice();
    const cats=planningCategoryState(cfg,currentCaps,projectedCaps);
    const gearOptions=buildGearOptions(baseGear,cfg,desired,projectedCaps.gear);
    const lastOptionCost=options=>{
      const last=Array.isArray(options)&&options.length?options[options.length-1]:null;
      return Math.max(0,Number(last?.cost)||0);
    };
    // Total material still productively spendable from the CURRENT category levels up to
    // the safe projected cap. This is independent of whichever candidate plan wins.
    const headroomCosts={
      ore:Math.max(0,Number(gearOptions?.[gearOptions.length-1]?.oreCost)||0),
      essence:lastOptionCost(cats.skillOptions),
      sand:lastOptionCost(cats.relicOptions),
      treat:lastOptionCost(cats.fantoOptions)
    };
    return {baseScore,desired,p,cfg,current,currentCaps,projectedCaps,baseGear,cats,gearOptions,headroomCosts,charScore:characterScore(p,cfg)};
  }

function plannedToolAcquisitionSupply(key,resources,cfg=activeCalcConfig()){
    if(key==='treat') return rawOnlyAcquisitionSupply(key,resources,cfg);
    const inv=realmInventoryFor(key,cfg);
    const perRun=Math.max(0,realmYieldFor(resources,key));
    const bankedMaterial=Math.max(0,Number(inv?.banked)||0)*perRun;
    // Saved + already-configured future tools are real owned/projected capacity, so they
    // enter scarcity at full material equivalent. Candidate-invented extra purchases are
    // intentionally absent from realmInventoryFor() and therefore cannot inflate this pool.
    return rawOnlyAcquisitionSupply(key,resources,cfg)+bankedMaterial*TOOL_SCARCITY_CREDIT;
  }

function jointReacquisitionHours(costs,resources,cfg=activeCalcConfig()){
    const map=resources?.yields?.map||cfg.map||{};
    const enteredTreatRate=Math.max(0,__calculatorDeps.n('treatRate'));
    const cart={
      ore:Math.max(0,__calculatorDeps.n('oreRate')),
      essence:Math.max(0,__calculatorDeps.n('essenceRate')),
      sand:Math.max(0,__calculatorDeps.n('sandRate')),
      treat:enteredTreatRate
    };
    const nodeYield={
      ore:Math.max(0,Number(map.ore)||0),
      essence:Math.max(0,Number(map.essence)||0),
      sand:Math.max(0,Number(map.sand)||0)
    };
    const demand={
      ore:Math.max(0,Number(costs?.ore)||0),
      essence:Math.max(0,Number(costs?.essence)||0),
      sand:Math.max(0,Number(costs?.sand)||0),
      treat:Math.max(0,Number(costs?.treat)||0)
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
    const marginalCosts=marginalWeightedCosts(costs,resources,cfg);
    return {hours:jointReacquisitionHours(marginalCosts,resources,cfg)};
  }

function makePlanCandidate(go,so,ro,fo,score,desired,resources,realms,acquisitionResult=null){
    const oreRealm=realms[0],essenceRealm=realms[1],sandRealm=realms[2];
    const dawniumCost=oreRealm.dawnium+essenceRealm.dawnium+sandRealm.dawnium;
    const realmPacks=oreRealm.packs+essenceRealm.packs+sandRealm.packs;
    const oreShare=resources.ore>0?go.oreCost/resources.ore:(go.oreCost>0?go.oreCost/100000:0);
    const essenceShare=resources.essence>0?so.cost/resources.essence:(so.cost>0?so.cost/100000:0);
    const sandShare=resources.sand>0?ro.cost/resources.sand:(ro.cost>0?ro.cost/100000:0);
    const treatShare=resources.treat>0?fo.cost/resources.treat:(fo.cost>0?fo.cost/10000:0);
    const refinedShare=resources.refinedTracked&&resources.refined>0?go.refinedCost/resources.refined:0;
    const maxShare=Math.max(oreShare,essenceShare,sandShare,treatShare,refinedShare);
    const sumShare=oreShare+essenceShare+sandShare+treatShare+refinedShare;
    /* ACQUISITION_KERNEL_V2 · TOTAL_POOL_SMART_BALANCE_V1 · CANDIDATE_SCALAR_FASTPATH_V5
       Candidate creation is in the hottest optimizer path. Keep the exact same economics and
       public result fields, but avoid per-candidate temporary share/Realm arrays, reduce()
       callbacks and repeated activeCalcConfig() lookups. */
    const cfg=activeCalcConfig();
    const acquisition=acquisitionResult||acquisitionEffortFor({ore:go.oreCost,essence:so.cost,sand:ro.cost,treat:fo.cost},resources,cfg);
    const unknownPriceRefreshes=
      Math.max(0,Number(oreRealm?.unknownPriceRefreshes)||0)+
      Math.max(0,Number(essenceRealm?.unknownPriceRefreshes)||0)+
      Math.max(0,Number(sandRealm?.unknownPriceRefreshes)||0);
    const bankedHammersUsed=oreRealm.bankedUsed||0;
    const bankedKnucklesUsed=essenceRealm.bankedUsed||0;
    const bankedShovelsUsed=sandRealm.bankedUsed||0;
    return {
      gear:go.target,skill:so.avg,relic:ro.avg,fanto:fo.avg,
      skillLevels:so.levels,relicLevels:ro.levels,fantoLevels:fo.levels,
      oreCost:go.oreCost,essenceCost:so.cost,sandCost:ro.cost,treatCost:fo.cost,refinedCost:go.refinedCost,
      score,gearAdds:go.adds,skillAdds:so.adds,relicAdds:ro.adds,fantoAdds:fo.adds,
      oreShare,essenceShare,sandShare,treatShare,refinedShare,
      acquisitionHours:acquisition.hours,unknownPriceRefreshes,
      maxShare,sumShare,overshoot:score-desired,
      dawniumCost,realmAttempts:realmPacks,realmPacks,
      bankedHammersUsed,bankedKnucklesUsed,bankedShovelsUsed,
      bankedToolsUsed:bankedHammersUsed+bankedKnucklesUsed+bankedShovelsUsed,seasonKey:cfg.key,
      realm:{days:Number.isFinite(resources?.realmDays)?resources.realmDays:materialRealmDaysAvailable(cfg),ore:oreRealm,essence:essenceRealm,sand:sandRealm}
    };
  }

// Find both the cheapest fundable plan and the best score-capable shortfall plan in ONE scan.
  // v22/v23 performed almost the same triple-nested search separately, sometimes many times per refresh.
function searchPlans(baseScore,desired,p,resources,cfg=activeCalcConfig(),ctx=null){
    const context=ctx||createPlanningContext(baseScore,desired,p,cfg);
    const {baseGear,cats,gearOptions,charScore,headroomCosts}=context;
    const realmDays=Number.isFinite(resources?.realmDays)?resources.realmDays:materialRealmDaysAvailable(cfg);
    // TOTAL_POOL_SMART_BALANCE_V1: scarcity/efficiency sees projected raw + saved/already-
    // planned tools at full material equivalent. realmTopupFor() separately preserves the
    // physical consumption order (raw first). Extra candidate purchases never enter this pool.
    resources.acquisitionHeadroomCosts=headroomCosts||{};
    resources.acquisitionSupplyEquiv={
      ore:plannedToolAcquisitionSupply('ore',resources,cfg),
      essence:plannedToolAcquisitionSupply('essence',resources,cfg),
      sand:plannedToolAcquisitionSupply('sand',resources,cfg),
      treat:rawOnlyAcquisitionSupply('treat',resources,cfg)
    };
    if(baseScore>=desired){
      const zero={gear:baseGear,skill:cats.skill.avg,relic:cats.relic.avg,fanto:cats.fanto.avg,skillLevels:cats.skill.levels,relicLevels:cats.relic.levels,fantoLevels:cats.fanto.levels,oreCost:0,essenceCost:0,sandCost:0,treatCost:0,refinedCost:0,score:baseScore,gearAdds:0,skillAdds:0,relicAdds:0,fantoAdds:0,dawniumCost:0,realmAttempts:0,realmPacks:0,seasonKey:cfg.key,realmFeasible:true,realm:{days:realmDays,ore:realmTopupFor('ore',0,resources.ore,resources,cfg,p),essence:realmTopupFor('essence',0,resources.essence,resources,cfg,p),sand:realmTopupFor('sand',0,resources.sand,resources,cfg,p)}};
      return {plan:zero,diagnostic:zero};
    }
    /* RAW_FUNDED_SEARCH_FAST_V1 is intentionally disabled under
       SCARCITY_ADJUSTED_ACQUISITION_V1. Its dimensional collapse was exact only when fully
       funded non-Ore material had zero marginal value and Ore was always fixed at 1.00.
       With continuous nonzero scarcity floors, different Gear/Skill/Relic mixes retain
       different economic costs and must stay in the general exact search. */
    const nonOreRawFunded=false;
    if(nonOreRawFunded){
      const skillMax=cats.skillOptions[cats.skillOptions.length-1];
      const relicMax=cats.relicOptions[cats.relicOptions.length-1];
      const fantoMax=cats.fantoOptions[cats.fantoOptions.length-1];
      const maxNonGearScore=(skillMax?.score||0)+(relicMax?.score||0)+(fantoMax?.score||0);
      const go=__calculatorDeps.gearLocked
        ? (gearOptions[0].score>=Math.max(0,desired-charScore-maxNonGearScore)?gearOptions[0]:null)
        : firstGearOptionAtLeast(gearOptions,Math.max(0,desired-charScore-maxNonGearScore));
      if(go){
        const firstSkillAtLeast=scoreNeeded=>{
          let lo=0,hi=cats.skillOptions.length-1,ans=null;
          while(lo<=hi){
            const mid=(lo+hi)>>1;
            if(cats.skillOptions[mid].score>=scoreNeeded){ans=cats.skillOptions[mid];hi=mid-1;}else lo=mid+1;
          }
          return ans;
        };
        const oreRealm=realmTopupFor('ore',go.oreCost,resources.ore,resources,cfg,p);
        const zeroEssence=realmTopupFor('essence',0,resources.essence,resources,cfg,p);
        const zeroSand=realmTopupFor('sand',0,resources.sand,resources,cfg,p);
        const sharedAcquisition=acquisitionEffortFor({ore:go.oreCost,essence:0,sand:0,treat:0},resources,cfg);
        let fastBest=null;
        for(const ro of cats.relicOptions){
          for(const fo of cats.fantoOptions){
            const neededSkill=Math.max(0,desired-charScore-go.score-ro.score-fo.score);
            const so=firstSkillAtLeast(neededSkill);
            if(!so) continue;
            const score=charScore+go.score+so.score+ro.score+fo.score;
            if(score<desired) continue;
            const candidate=makePlanCandidate(go,so,ro,fo,score,desired,resources,[oreRealm,zeroEssence,zeroSand],sharedAcquisition);
            candidate.realm.days=realmDays;
            candidate.realmFeasible=oreRealm.feasible;
            if(!oreRealm.feasible) continue;
            if(betterFeasibleCandidate(candidate,fastBest)) fastBest=candidate;
          }
        }
        if(fastBest && candidateRealmStage(fastBest)<2) return {plan:fastBest,diagnostic:fastBest};
      }
    }
    /* REALM_OPTION_PROPERTY_CACHE_V7
       Realm top-up results are immutable for one resource allocation, but Auto-Stamina
       reuses option objects across allocations. Reset cached Realm costs in the acquisition
       prepass below so each search sees its own raw/tool budget. Hot-loop reads remain direct
       property accesses and unused Realm options are still evaluated lazily. */
    const oreFor=go=>go.__realmOreV7||(go.__realmOreV7=realmTopupFor('ore',go.oreCost,resources.ore,resources,cfg,p));
    const essFor=so=>so.__realmEssenceV7||(so.__realmEssenceV7=realmTopupFor('essence',so.cost,resources.essence,resources,cfg,p));
    const sandFor=ro=>ro.__realmSandV7||(ro.__realmSandV7=realmTopupFor('sand',ro.cost,resources.sand,resources,cfg,p));
    /* ACQUISITION_KERNEL_V2 · TOTAL_POOL_SMART_BALANCE_V1
       This metric is evaluated in the hottest optimizer loop. Precompute each category's
       scarcity-adjusted spend ONCE against the full owned/projected resource-family pool,
       read Cart/map rates once, and run the joint-reacquisition equation with scalar locals.
       Raw-funded and tool-backed candidates therefore use the same economic kernel. */
    for(const go of gearOptions){
      go.__realmOreV7=null;
      go.__acqOreV1=marginalWeightedSpend(go.oreCost,'ore',resources);
    }
    for(const so of cats.skillOptions){
      so.__realmEssenceV7=null;
      so.__acqEssenceV1=marginalWeightedSpend(so.cost,'essence',resources);
    }
    for(const ro of cats.relicOptions){
      ro.__realmSandV7=null;
      ro.__acqSandV1=marginalWeightedSpend(ro.cost,'sand',resources);
    }
    for(const fo of cats.fantoOptions) fo.__acqTreatV1=marginalWeightedSpend(fo.cost,'treat',resources);
    const acqMap=resources?.yields?.map||cfg.map||{};
    const acqCartOre=Math.max(0,__calculatorDeps.n('oreRate'));
    const acqCartEssence=Math.max(0,__calculatorDeps.n('essenceRate'));
    const acqCartSand=Math.max(0,__calculatorDeps.n('sandRate'));
    const acqCartTreat=Math.max(0,__calculatorDeps.n('treatRate'));
    const acqNodeOre=Math.max(0,Number(acqMap.ore)||0);
    const acqNodeEssence=Math.max(0,Number(acqMap.essence)||0);
    const acqNodeSand=Math.max(0,Number(acqMap.sand)||0);
    /* JOINT_HOURS_NO_CLOSURE_V2 · JOINT_HOURS_ACTIVE_SET_V9
       The acquisition equation is a three-term piecewise-linear fixed point:
         sum(max(0, demand - CartRate * hours) / nodeYield) <= hours.
       Active resources can only DROP OUT as hours rises. Precompute reciprocal node yields,
       fold the floor residual check into active-set construction, then solve each active set
       directly. With only Ore/Essence/Sand, at most three active-set solves are possible.
       This removes repeated division, the stable-set verification pass and the 48-step binary
       fallback while preserving the same mathematical root and tolerance boundaries. */
    const acqInvNodeOre=acqNodeOre>0?1/acqNodeOre:0;
    const acqInvNodeEssence=acqNodeEssence>0?1/acqNodeEssence:0;
    const acqInvNodeSand=acqNodeSand>0?1/acqNodeSand:0;
    const acqCartNodeOre=acqCartOre*acqInvNodeOre;
    const acqCartNodeEssence=acqCartEssence*acqInvNodeEssence;
    const acqCartNodeSand=acqCartSand*acqInvNodeSand;
    const nodesAtFast=(hours,ore,essence,sand)=>{
      let total=0,rem=0;
      rem=ore-acqCartOre*hours;if(rem>0){if(acqInvNodeOre<=0)return Infinity;total+=rem*acqInvNodeOre;}
      rem=essence-acqCartEssence*hours;if(rem>0){if(acqInvNodeEssence<=0)return Infinity;total+=rem*acqInvNodeEssence;}
      rem=sand-acqCartSand*hours;if(rem>0){if(acqInvNodeSand<=0)return Infinity;total+=rem*acqInvNodeSand;}
      return total;
    };
    const jointHoursFast=(oreRaw,essRaw,sandRaw,treatRaw)=>{
      const ore=oreRaw>0?oreRaw:0;
      const essence=essRaw>0?essRaw:0;
      const sand=sandRaw>0?sandRaw:0;
      const treat=treatRaw>0?treatRaw:0;
      let floor=0;
      if(treat>0){
        if(acqCartTreat<=0) return 1e9;
        floor=treat/acqCartTreat;
      }
      if(ore>0&&acqInvNodeOre<=0){if(acqCartOre<=0)return 1e9;floor=Math.max(floor,ore/acqCartOre);}
      if(essence>0&&acqInvNodeEssence<=0){if(acqCartEssence<=0)return 1e9;floor=Math.max(floor,essence/acqCartEssence);}
      if(sand>0&&acqInvNodeSand<=0){if(acqCartSand<=0)return 1e9;floor=Math.max(floor,sand/acqCartSand);}
      let mask=0,floorNodes=0,rem=0;
      rem=ore-acqCartOre*floor;
      if(rem>1e-9&&acqInvNodeOre>0){mask|=1;floorNodes+=rem*acqInvNodeOre;}
      rem=essence-acqCartEssence*floor;
      if(rem>1e-9&&acqInvNodeEssence>0){mask|=2;floorNodes+=rem*acqInvNodeEssence;}
      rem=sand-acqCartSand*floor;
      if(rem>1e-9&&acqInvNodeSand>0){mask|=4;floorNodes+=rem*acqInvNodeSand;}
      if(!mask||floorNodes<=floor+1e-9) return floor;
      let hours=floor;
      for(let pass=0;pass<3;pass++){
        let numerator=0,denominator=1;
        if(mask&1){numerator+=ore*acqInvNodeOre;denominator+=acqCartNodeOre;}
        if(mask&2){numerator+=essence*acqInvNodeEssence;denominator+=acqCartNodeEssence;}
        if(mask&4){numerator+=sand*acqInvNodeSand;denominator+=acqCartNodeSand;}
        hours=Math.max(floor,numerator/denominator);
        let next=0;
        if((mask&1)&&ore>acqCartOre*hours+1e-9) next|=1;
        if((mask&2)&&essence>acqCartEssence*hours+1e-9) next|=2;
        if((mask&4)&&sand>acqCartSand*hours+1e-9) next|=4;
        if(next===mask) return hours;
        mask=next;
        if(!mask) return floor;
      }
      // Three resources means a non-empty active set must stabilize within three passes.
      return hours;
    };
    const acquisitionFor=(go,so,ro,fo)=>({hours:jointHoursFast(go.__acqOreV1,so.__acqEssenceV1,ro.__acqSandV1,fo.__acqTreatV1)});
    /* ACQUISITION_LIMIT_PRECHECK_V8
       For the no-paid bounded search acquisition hours are the primary comparator. Before
       solving the piecewise joint-hours equation, test the current winner's time directly:
       if Treat Cart production cannot cover Treat demand by that time, or the map-node work
       still exceeds the same time budget, the candidate's exact joint root must be later and
       it cannot win. This is a necessary-condition rejection only; surviving candidates still
       run the original exact jointHoursFast() and the normal tie-break chain. */
    const acquisitionCannotBeat=(bestHours,go,so,ro,fo)=>{
      if(!Number.isFinite(bestHours)||bestHours>=1e9) return false;
      const limit=bestHours+1e-9;
      const treat=fo.__acqTreatV1;
      if(treat>0){
        if(acqCartTreat<=0) return true;
        if(treat>acqCartTreat*limit+1e-7) return true;
      }
      return nodesAtFast(limit,go.__acqOreV1,so.__acqEssenceV1,ro.__acqSandV1)>limit+1e-7;
    };
    let best=null,bestDiagnostic=null;
    /* OWNED_POOL_IMPOSSIBILITY_FASTPATH_V4 · TOTAL_POOL_SMART_BALANCE_V1
       Prove whether ANY route using projected raw + saved/already-planned tools can reach the
       target before deciding whether a paid-refresh fast-path result needs the expensive scan.
       Extra candidate purchases are excluded from these budgets. */
    const highestAffordable=(options,budget,costKey='cost',secondaryBudget=Infinity,secondaryKey='')=>{
      let bestOption=Array.isArray(options)&&options.length?options[0]:null;
      for(const option of (options||[])){
        const primary=Math.max(0,Number(option?.[costKey])||0);
        const secondary=secondaryKey?Math.max(0,Number(option?.[secondaryKey])||0):0;
        if(primary<=budget+0.5 && secondary<=secondaryBudget+0.5) bestOption=option;
        else if(primary>budget+0.5) break;
      }
      return bestOption;
    };
    const poolRefinedBudget=resources.refinedTracked?Math.max(0,Number(resources.refined)||0):Infinity;
    const poolMaxGear=highestAffordable(gearOptions,plannedToolAcquisitionSupply('ore',resources,cfg),'oreCost',poolRefinedBudget,'refinedCost');
    const poolMaxSkill=highestAffordable(cats.skillOptions,plannedToolAcquisitionSupply('essence',resources,cfg));
    const poolMaxRelic=highestAffordable(cats.relicOptions,plannedToolAcquisitionSupply('sand',resources,cfg));
    const poolMaxFanto=highestAffordable(cats.fantoOptions,Math.max(0,Number(resources.treat)||0));
    const ownedPoolMaxScore=charScore+(poolMaxGear?.score||0)+(poolMaxSkill?.score||0)+(poolMaxRelic?.score||0)+(poolMaxFanto?.score||0);
    const ownedPoolRoutePossible=ownedPoolMaxScore>=desired-1e-9;
    /* TREAT_FUNDED_SEARCH_FAST_V1
       Exact dimensional collapse when raw Treats already fund every reachable Fantomon
       upgrade. In that state the configured fully-funded Treat acquisition floor is zero,
       so Fantomon score is free in the PRIMARY acquisition metric.
       For each Skill+Relic choice, the best acquisition route therefore uses enough free
       Fantomon score to force Gear to its lowest possible option. Once that Gear option is
       fixed, extra Fantomon upgrades cannot improve acquisition and only worsen/equal the
       normal overscore/share tie-breaks, so select the first Fantomon option that reaches
       target. This replaces Relic x Fantomon x Skill with Relic x Skill while preserving
       the exact candidate comparator. */
    /* REFINED_FASTPATH_GUARD_V3
       Keep the Treat-funded dimensional collapse disabled whenever Refined Ore tracking is
       active. Even a numerically funded Refined pool still participates in downstream share/
       tie-break semantics, so collapsing that dimension changes the exact chosen plan. */
    const treatFullyFunded=!resources.refinedTracked &&
      (Number(resources.treat)||0)>=Math.max(0,Number(headroomCosts?.treat)||0)-0.5;
    if(treatFullyFunded && cats.fantoOptions.length>1){
      const fantoMax=cats.fantoOptions[cats.fantoOptions.length-1];
      const firstFantoAtLeast=scoreNeeded=>{
        let lo=0,hi=cats.fantoOptions.length-1,ans=null;
        while(lo<=hi){
          const mid=(lo+hi)>>1;
          if(cats.fantoOptions[mid].score>=scoreNeeded){ans=cats.fantoOptions[mid];hi=mid-1;}else lo=mid+1;
        }
        return ans;
      };
      let fastBest=null,fastDiagnostic=null;
      for(const ro of cats.relicOptions){
        const sandRealm=sandFor(ro);
        for(const so of cats.skillOptions){
          const fixedScore=charScore+ro.score+so.score;
          const go=__calculatorDeps.gearLocked
            ? (gearOptions[0].score+fantoMax.score>=Math.max(0,desired-fixedScore)?gearOptions[0]:null)
            : firstGearOptionAtLeast(gearOptions,Math.max(0,desired-fixedScore-fantoMax.score));
          if(!go) continue;
          const neededFanto=Math.max(0,desired-fixedScore-go.score);
          const fo=firstFantoAtLeast(neededFanto);
          if(!fo) continue;
          const score=fixedScore+go.score+fo.score;
          if(score<desired) continue;
          const oreRealm=oreFor(go),essenceRealm=essFor(so);
          const refinedShortfall=0;
          const hardShortfall=0;
          const realms=[oreRealm,essenceRealm,sandRealm];
          const realmOverflow=realms.reduce((sum,x)=>sum+Math.max(0,(Number.isFinite(x.packs)?x.packs:1e9)-(x.maxPacks||0)),0);
          const remainingAfterMax=realms.reduce((sum,x)=>sum+Math.max(0,x.remainingAfterMax||0),0);
          const realmPacks=realms.reduce((sum,x)=>sum+(Number.isFinite(x.packs)?x.packs:1e9),0);
          const allFeasible=realms.every(x=>x.feasible);
          const dawniumCost=allFeasible?realms.reduce((sum,x)=>sum+x.dawnium,0):Infinity;
          const unknownPriceRefreshes=realms.reduce((sum,x)=>sum+Math.max(0,Number(x?.unknownPriceRefreshes)||0),0);
          const acquisition=acquisitionFor(go,so,ro,fo);
          if(allFeasible){
            const candidate=makePlanCandidate(go,so,ro,fo,score,desired,resources,realms,acquisition);
            candidate.realm.days=realmDays;
            candidate.realmFeasible=true;
            if(betterFeasibleCandidate(candidate,fastBest)) fastBest=candidate;
            continue;
          }
          const treatShortfall=0;
          const diagOreShare=resources.ore>0?go.oreCost/resources.ore:(go.oreCost>0?go.oreCost/100000:0);
          const diagEssenceShare=resources.essence>0?so.cost/resources.essence:(so.cost>0?so.cost/100000:0);
          const diagSandShare=resources.sand>0?ro.cost/resources.sand:(ro.cost>0?ro.cost/100000:0);
          const diagTreatShare=resources.treat>0?fo.cost/resources.treat:0;
          const diagnostic={gear:go.target,skill:so.avg,relic:ro.avg,fanto:fo.avg,skillLevels:so.levels,relicLevels:ro.levels,fantoLevels:fo.levels,oreCost:go.oreCost,essenceCost:so.cost,sandCost:ro.cost,treatCost:fo.cost,refinedCost:go.refinedCost,score,gearAdds:go.adds,skillAdds:so.adds,relicAdds:ro.adds,fantoAdds:fo.adds,overshoot:score-desired,dawniumCost,realmAttempts:realmPacks,realmPacks,oreShare:diagOreShare,essenceShare:diagEssenceShare,sandShare:diagSandShare,treatShare:diagTreatShare,acquisitionHours:acquisition.hours,unknownPriceRefreshes,bankedHammersUsed:(oreRealm.bankedUsed||0),bankedKnucklesUsed:(essenceRealm.bankedUsed||0),bankedShovelsUsed:(sandRealm.bankedUsed||0),bankedToolsUsed:(oreRealm.bankedUsed||0)+(essenceRealm.bankedUsed||0)+(sandRealm.bankedUsed||0),realmOverflow,remainingAfterMax,treatShortfall,refinedShortfall,hardShortfall,seasonKey:cfg.key,realmFeasible:false,realm:{days:realmDays,ore:oreRealm,essence:essenceRealm,sand:sandRealm}};
          if(betterDiagnosticCandidate(diagnostic,fastDiagnostic)) fastDiagnostic=diagnostic;
        }
      }
      if(fastBest && (candidateRealmStage(fastBest)<2 || !ownedPoolRoutePossible)) return {plan:fastBest,diagnostic:fastBest};
      // If the owned/projected pool can still reach the target without extra purchases, keep
      // scanning before accepting a paid-refresh route because extra purchases are last resort.
    }
    /* BOUNDED_FEASIBLE_SEARCH_V1
       Before the expensive diagnostic scan, prove the largest independently fundable
       option in each resource family. Because Gear/Ore, Skills/Essence, Relics/Sand and
       Fantomons/Treats use separate budgets in this model, the sum of those maxima proves
       whether at least one fully fundable target route exists.
       If a route exists without EXTRA Realm purchases, paid-refresh candidates are
       categorically worse under betterFeasibleCandidate(), so search only the owned/raw+
       banked-tool prefixes. Otherwise, if a route exists within maximum legal Realm
       capacity, search only the individually feasible prefixes. This cannot change the
       winner: every excluded option is either physically impossible or belongs to a
       sourcing tier that loses before acquisition-effort tie-breaks are considered.
       The bounded scan also starts each monotone category at the first score that could
       possibly reach the target even with all remaining categories maxed. That removes
       millions of low-score combinations that previously called the Gear binary search
       only to discover that no Gear option could make them reach target. */
    const lastTrueIndex=(options,predicate)=>{
      let lo=0,hi=(options?.length||0)-1,ans=-1;
      while(lo<=hi){
        const mid=(lo+hi)>>1;
        if(predicate(options[mid],mid)){ans=mid;lo=mid+1;}else hi=mid-1;
      }
      return ans;
    };
    const firstScoreIndex=(options,scoreNeeded)=>{
      const need=Math.max(0,Number(scoreNeeded)||0);
      let lo=0,hi=(options?.length||0)-1,ans=options?.length||0;
      while(lo<=hi){
        const mid=(lo+hi)>>1;
        if((Number(options[mid]?.score)||0)>=need){ans=mid;hi=mid-1;}else lo=mid+1;
      }
      return ans;
    };
    const refinedFunded=go=>!resources.refinedTracked || (Number(go?.refinedCost)||0)<=(Number(resources.refined)||0)+0.5;
    const noPaidRealm=x=>!!x?.feasible && Math.max(0,Number(x?.packs)||0)<=0;
    const feasibleLast={
      gear:lastTrueIndex(gearOptions,go=>refinedFunded(go)&&!!oreFor(go)?.feasible),
      skill:lastTrueIndex(cats.skillOptions,so=>!!essFor(so)?.feasible),
      relic:lastTrueIndex(cats.relicOptions,ro=>!!sandFor(ro)?.feasible),
      fanto:lastTrueIndex(cats.fantoOptions,fo=>(Number(fo?.cost)||0)<=(Number(resources.treat)||0)+0.5)
    };
    const noPaidLast={
      gear:lastTrueIndex(gearOptions,go=>refinedFunded(go)&&noPaidRealm(oreFor(go))),
      skill:lastTrueIndex(cats.skillOptions,so=>noPaidRealm(essFor(so))),
      relic:lastTrueIndex(cats.relicOptions,ro=>noPaidRealm(sandFor(ro))),
      fanto:feasibleLast.fanto
    };
    const scoreAt=(options,index)=>index>=0?(Number(options[index]?.score)||0):-Infinity;
    const maxRouteScore=last=>charScore+
      scoreAt(gearOptions,last.gear)+scoreAt(cats.skillOptions,last.skill)+
      scoreAt(cats.relicOptions,last.relic)+scoreAt(cats.fantoOptions,last.fanto);
    const noPaidRoutePossible=Object.values(noPaidLast).every(i=>i>=0) && maxRouteScore(noPaidLast)>=desired-1e-9;
    const feasibleRoutePossible=Object.values(feasibleLast).every(i=>i>=0) && maxRouteScore(feasibleLast)>=desired-1e-9;
    const boundedLast=noPaidRoutePossible?noPaidLast:(feasibleRoutePossible?feasibleLast:null);
    if(boundedLast){
      const boundedGear=gearOptions.slice(0,boundedLast.gear+1);
      const boundedSkill=cats.skillOptions.slice(0,boundedLast.skill+1);
      const boundedRelic=cats.relicOptions.slice(0,boundedLast.relic+1);
      /* ZERO_RATE_FANTO_PRUNE_V1
         Treats have no map/Realm reacquisition path. If Treat Cart income is zero, any
         Fantomon upgrade has the optimizer's 1e9 acquisition penalty. When the target is
         already reachable in the same preferred no-paid sourcing tier with the current
         Fantomon level, every positive-Treat Fantomon option is strictly worse before
         overscore/share tie-breaks are consulted. Keep only the zero-cost base option.
         This is especially important for well-funded accounts: the old exact scan still
         walked hundreds of Fantomon states even though none could beat a finite-acquisition
         base-Fantomon route. */
      let boundedFantoLast=boundedLast.fanto;
      if(noPaidRoutePossible && acqCartTreat<=0 && (Number(cats.fantoOptions[0]?.__acqTreatV1)||0)<=1e-9){
        const baseFantoScore=Number(cats.fantoOptions[0]?.score)||0;
        const noPaidBaseFantoMax=charScore+
          scoreAt(gearOptions,noPaidLast.gear)+scoreAt(cats.skillOptions,noPaidLast.skill)+
          scoreAt(cats.relicOptions,noPaidLast.relic)+baseFantoScore;
        if(noPaidBaseFantoMax>=desired-1e-9) boundedFantoLast=0;
      }
      const boundedFanto=cats.fantoOptions.slice(0,boundedFantoLast+1);
      const maxGearScore=Number(boundedGear[boundedGear.length-1]?.score)||0;
      const maxSkillScore=Number(boundedSkill[boundedSkill.length-1]?.score)||0;
      const maxFantoScore=Number(boundedFanto[boundedFanto.length-1]?.score)||0;
      /* BOUNDED_EAGER_REALM_V12
         The exact bounded scan revisits the same Gear/Skill/Relic options thousands of times.
         Materialize each immutable Realm result once for this search snapshot and store the
         refined-funding bit on Gear. The hot loops then use direct property reads instead of
         repeatedly entering oreFor()/essFor()/sandFor()/refinedFunded() wrappers. */
      for(const go of boundedGear){ go.__realmOreV7=oreFor(go); go.__refinedFundedV12=refinedFunded(go); }
      for(const so of boundedSkill) so.__realmEssenceV7=essFor(so);
      for(const ro of boundedRelic) ro.__realmSandV7=sandFor(ro);
      const relicStart=firstScoreIndex(boundedRelic,desired-charScore-maxGearScore-maxSkillScore-maxFantoScore);
      let boundedBest=null;
      /* COARSE_EXACT_SEED_V1
         Give branch-and-bound a strong VALID upper bound before the exhaustive scan.
         Sample a small evenly-spaced set of Relic/Fantomon states, but search the complete
         monotone Skill->minimum-Gear frontier inside each sampled state. Every seed is a
         normal exact candidate scored by the same comparator; it can only make later
         lower-bound pruning stronger, never alter correctness. */
      const sampledIndices=(start,length,count=10)=>{
        const out=new Set();
        const first=Math.max(0,Math.min(length-1,start));
        const last=Math.max(first,length-1);
        if(length<=0) return [];
        if(last===first) return [first];
        for(let i=0;i<count;i++) out.add(Math.round(first+(last-first)*(i/(count-1))));
        return [...out].sort((a,b)=>a-b);
      };
      for(const ri of sampledIndices(relicStart,boundedRelic.length,10)){
        const ro=boundedRelic[ri],sandRealm=ro.__realmSandV7;
        const fantoStart=firstScoreIndex(boundedFanto,desired-charScore-ro.score-maxGearScore-maxSkillScore);
        for(const fi of sampledIndices(fantoStart,boundedFanto.length,10)){
          const fo=boundedFanto[fi];
          const fixedBeforeSkill=charScore+ro.score+fo.score;
          const skillStart=firstScoreIndex(boundedSkill,desired-fixedBeforeSkill-maxGearScore);
          if(skillStart>=boundedSkill.length) continue;
          /* SKILL_GEAR_TWO_POINTER_V10
             The old loop walked every Skill option and binary-searched Gear each time, then
             discarded all but the FIRST Skill state mapping to each minimum Gear step. Keep
             that exact candidate frontier/order, but walk it with monotone Skill/Gear cursors:
             one Gear binary search to enter the frontier, then a linear scan only until the
             next lower Gear step becomes sufficient. No per-Skill Gear binary searches. */
          let si=skillStart;
          let gi=__calculatorDeps.gearLocked?0:firstScoreIndex(boundedGear,desired-fixedBeforeSkill-boundedSkill[si].score);
          while(si<boundedSkill.length&&gi<boundedGear.length){
            const so=boundedSkill[si],go=boundedGear[gi];
            const score=fixedBeforeSkill+so.score+go.score;
            if(score>=desired&&go.__refinedFundedV12){
              const oreRealm=go.__realmOreV7,essenceRealm=so.__realmEssenceV7;
              if(oreRealm.feasible&&essenceRealm.feasible&&sandRealm.feasible &&
                 !(noPaidRoutePossible&&boundedBest&&acquisitionCannotBeat(boundedBest.acquisitionHours,go,so,ro,fo))){
                const acquisition=acquisitionFor(go,so,ro,fo);
                if(!(noPaidRoutePossible&&boundedBest&&acquisition.hours>boundedBest.acquisitionHours+1e-9)){
                  const candidate=makePlanCandidate(go,so,ro,fo,score,desired,resources,[oreRealm,essenceRealm,sandRealm],acquisition);
                  candidate.realm.days=realmDays;
                  candidate.realmFeasible=true;
                  if(noPaidRoutePossible&&boundedBest&&acquisition.hours<boundedBest.acquisitionHours-1e-9){
                    boundedBest=candidate;
                  }else if(betterFeasibleCandidate(candidate,boundedBest)) boundedBest=candidate;
                }
              }
            }
            if(__calculatorDeps.gearLocked||gi===0) break;
            const nextGearScore=Number(boundedGear[gi-1]?.score)||0;
            do{si++;}while(si<boundedSkill.length &&
              fixedBeforeSkill+(Number(boundedSkill[si]?.score)||0)+nextGearScore<desired-1e-9);
            if(si>=boundedSkill.length) break;
            const need=desired-fixedBeforeSkill-(Number(boundedSkill[si]?.score)||0);
            while(gi>0&&(Number(boundedGear[gi-1]?.score)||0)>=need-1e-9) gi--;
          }
        }
      }
      /* ACQUISITION_LOWER_BOUND_PRUNE_V1 · MONOTONE_BOUND_BINARY_PRUNE_V2
         jointHoursFast() is monotone in every resource demand. Instead of evaluating the
         same lower-bound equation once for every Relic/Fantomon/Skill iteration, binary-search
         the first option that is already worse than the current exact seed. This preserves the
         identical candidate set: only a monotone suffix that the old loop would immediately
         break on is skipped. A later/improved best can only make these precomputed ends loose,
         never incorrectly exclude a winner. */
      const firstWorseIndex=(options,start,hoursFor)=>{
        if(!boundedBest) return options.length;
        const limit=boundedBest.acquisitionHours+1e-9;
        let lo=Math.max(0,start),hi=options.length-1,ans=options.length;
        while(lo<=hi){
          const mid=(lo+hi)>>1;
          if(hoursFor(options[mid])>limit){ans=mid;hi=mid-1;}else lo=mid+1;
        }
        return ans;
      };
      const relicEnd=firstWorseIndex(boundedRelic,relicStart,ro=>jointHoursFast(0,0,ro.__acqSandV1,0));
      for(let ri=relicStart;ri<relicEnd;ri++){
        const ro=boundedRelic[ri];
        /* DYNAMIC_OUTER_BOUND_V12
           relicEnd/fantoEnd are based on the seed winner. If the exact scan finds a faster
           winner, refresh the cheap monotone subset bound inline so we can stop the now-dead
           Relic/Fantomon suffix immediately. */
        if(noPaidRoutePossible&&boundedBest&&
           jointHoursFast(0,0,ro.__acqSandV1,0)>boundedBest.acquisitionHours+1e-9) break;
        const sandRealm=ro.__realmSandV7;
        const fantoStart=firstScoreIndex(boundedFanto,desired-charScore-ro.score-maxGearScore-maxSkillScore);
        const fantoEnd=firstWorseIndex(boundedFanto,fantoStart,fo=>jointHoursFast(0,0,ro.__acqSandV1,fo.__acqTreatV1));
        for(let fi=fantoStart;fi<fantoEnd;fi++){
          const fo=boundedFanto[fi];
          if(noPaidRoutePossible&&boundedBest&&
             jointHoursFast(0,0,ro.__acqSandV1,fo.__acqTreatV1)>boundedBest.acquisitionHours+1e-9) break;
          const fixedBeforeSkill=charScore+ro.score+fo.score;
          const skillStart=firstScoreIndex(boundedSkill,desired-fixedBeforeSkill-maxGearScore);
          if(skillStart>=boundedSkill.length) continue;
          const skillEnd=firstWorseIndex(boundedSkill,skillStart,so=>jointHoursFast(0,so.__acqEssenceV1,ro.__acqSandV1,fo.__acqTreatV1));
          if(skillStart>=skillEnd) continue;
          /* SKILL_GEAR_TWO_POINTER_V10
             Same exact frontier as the legacy duplicate-skip loop, but without a Gear binary
             search for every skipped Skill state. Skill only rises and required Gear only
             falls, so a pair of monotone cursors visits the first Skill state of each Gear
             step in identical order. */
          let si=skillStart;
          let gi=__calculatorDeps.gearLocked?0:firstScoreIndex(boundedGear,desired-fixedBeforeSkill-boundedSkill[si].score);
          while(si<skillEnd&&gi<boundedGear.length){
            const so=boundedSkill[si],go=boundedGear[gi];
            const score=fixedBeforeSkill+so.score+go.score;
            if(score>=desired&&go.__refinedFundedV12){
              const oreRealm=go.__realmOreV7,essenceRealm=so.__realmEssenceV7;
              if(oreRealm.feasible&&essenceRealm.feasible&&sandRealm.feasible){
                const dominated=boundedBest && go.oreCost>=boundedBest.oreCost &&
                  so.cost>=boundedBest.essenceCost && ro.cost>=boundedBest.sandCost &&
                  fo.cost>=boundedBest.treatCost && go.refinedCost>=boundedBest.refinedCost;
                if(!dominated &&
                   !(noPaidRoutePossible&&boundedBest&&acquisitionCannotBeat(boundedBest.acquisitionHours,go,so,ro,fo))){
                  const acquisition=acquisitionFor(go,so,ro,fo);
                  if(!(noPaidRoutePossible&&boundedBest&&acquisition.hours>boundedBest.acquisitionHours+1e-9)){
                    const candidate=makePlanCandidate(go,so,ro,fo,score,desired,resources,[oreRealm,essenceRealm,sandRealm],acquisition);
                    candidate.realm.days=realmDays;
                    candidate.realmFeasible=true;
                    if(noPaidRoutePossible&&boundedBest&&acquisition.hours<boundedBest.acquisitionHours-1e-9){
                      boundedBest=candidate;
                    }else if(betterFeasibleCandidate(candidate,boundedBest)) boundedBest=candidate;
                  }
                }
              }
            }
            if(__calculatorDeps.gearLocked||gi===0) break;
            const nextGearScore=Number(boundedGear[gi-1]?.score)||0;
            do{si++;}while(si<skillEnd &&
              fixedBeforeSkill+(Number(boundedSkill[si]?.score)||0)+nextGearScore<desired-1e-9);
            if(si>=skillEnd) break;
            const need=desired-fixedBeforeSkill-(Number(boundedSkill[si]?.score)||0);
            while(gi>0&&(Number(boundedGear[gi-1]?.score)||0)>=need-1e-9) gi--;
          }
        }
      }
      if(boundedBest) return {plan:boundedBest,diagnostic:boundedBest};
      // Defensive fall-through: if future rule changes violate one of the monotonic
      // assumptions above, the legacy full scan below still preserves correctness.
    }
    /* AFFORDABLE_TREAT_FEASIBLE_V1
       Treats have no Material-Realm top-up path. Any actually FUNDABLE plan must therefore
       choose a Fantomon option whose Treat cost is already covered by projected Treat
       inventory. When that affordable slice is much smaller than the full Fantomon search
       range, do a cheap feasible-only pass first. If it finds a plan, every excluded
       Fantomon option is provably infeasible and the expensive diagnostic scan is unnecessary.
       If it finds nothing, fall through to the complete scan so shortfall diagnostics remain exact. */
    const affordableFantoOptions=cats.fantoOptions.filter(fo=>fo.cost<=(Number(resources.treat)||0)+0.5);
    if(affordableFantoOptions.length>0 && affordableFantoOptions.length*1.25<cats.fantoOptions.length){
      let affordableBest=null;
      for(const ro of cats.relicOptions){
        const sandRealm=sandFor(ro);
        for(const fo of affordableFantoOptions){
          const fixedBeforeSkill=charScore+ro.score+fo.score;
          let lastGearAdds=null;
          for(const so of cats.skillOptions){
            const fixedScore=fixedBeforeSkill+so.score;
            const go=__calculatorDeps.gearLocked?(gearOptions[0].score>=Math.max(0,desired-fixedScore)?gearOptions[0]:null):firstGearOptionAtLeast(gearOptions,Math.max(0,desired-fixedScore));
            if(!go) continue;
            if(lastGearAdds===go.adds) continue;
            lastGearAdds=go.adds;
            const score=fixedScore+go.score;
            if(score<desired) continue;
            const refinedShortfall=resources.refinedTracked?Math.max(0,go.refinedCost-resources.refined):0;
            if(refinedShortfall>0.5) continue;
            const oreRealm=oreFor(go),essenceRealm=essFor(so);
            const realms=[oreRealm,essenceRealm,sandRealm];
            if(!realms.every(x=>x.feasible)) continue;
            if(affordableBest && go.oreCost>=affordableBest.oreCost && so.cost>=affordableBest.essenceCost && ro.cost>=affordableBest.sandCost && fo.cost>=affordableBest.treatCost && go.refinedCost>=affordableBest.refinedCost) continue;
            const acquisition=acquisitionFor(go,so,ro,fo);
            const candidate=makePlanCandidate(go,so,ro,fo,score,desired,resources,realms,acquisition);
            candidate.realm.days=realmDays;
            candidate.realmFeasible=true;
            if(betterFeasibleCandidate(candidate,affordableBest)) affordableBest=candidate;
          }
        }
      }
      if(affordableBest) return {plan:affordableBest,diagnostic:affordableBest};
    }
    for(const ro of cats.relicOptions){
      const sandRealm=sandFor(ro);
      for(const fo of cats.fantoOptions){
        const treatShortfall=Math.max(0,fo.cost-resources.treat);
        const fixedBeforeSkill=charScore+ro.score+fo.score;
        let lastGearAdds=null;
        for(const so of cats.skillOptions){
          const fixedScore=fixedBeforeSkill+so.score;
          const go=__calculatorDeps.gearLocked?(gearOptions[0].score>=Math.max(0,desired-fixedScore)?gearOptions[0]:null):firstGearOptionAtLeast(gearOptions,Math.max(0,desired-fixedScore));
          if(!go)continue;
          // PERFORMANCE_STABILIZATION_V1: if Gear did not step down, this later Skill
          // option spends more Essence for the same required Gear and cannot win.
          if(lastGearAdds===go.adds) continue;
          lastGearAdds=go.adds;
          const score=fixedScore+go.score;if(score<desired)continue;
          const oreRealm=oreFor(go),essenceRealm=essFor(so);
          const refinedShortfall=resources.refinedTracked?Math.max(0,go.refinedCost-resources.refined):0;
          const hardShortfall=treatShortfall+refinedShortfall;
          const realms=[oreRealm,essenceRealm,sandRealm];
          const realmOverflow=realms.reduce((sum,x)=>sum+Math.max(0,(Number.isFinite(x.packs)?x.packs:1e9)-(x.maxPacks||0)),0);
          const remainingAfterMax=realms.reduce((sum,x)=>sum+Math.max(0,x.remainingAfterMax||0),0);
          const realmPacks=realms.reduce((sum,x)=>sum+(Number.isFinite(x.packs)?x.packs:1e9),0);
          const allFeasible=realms.every(x=>x.feasible)&&hardShortfall<=0.5;
          const dawniumCost=allFeasible?realms.reduce((sum,x)=>sum+x.dawnium,0):Infinity;
          const unknownPriceRefreshes=realms.reduce((sum,x)=>sum+Math.max(0,Number(x?.unknownPriceRefreshes)||0),0);
          if(allFeasible){
            // A route that costs at least as much as the current winner in every tracked
            // resource (and Refined Ore) is strictly dominated and cannot win later tie-breaks.
            if(best && go.oreCost>=best.oreCost && so.cost>=best.essenceCost && ro.cost>=best.sandCost && fo.cost>=best.treatCost && go.refinedCost>=best.refinedCost) continue;
            const acquisition=acquisitionFor(go,so,ro,fo);
            const candidate=makePlanCandidate(go,so,ro,fo,score,desired,resources,[oreRealm,essenceRealm,sandRealm],acquisition);
            candidate.realm.days=realmDays;
            candidate.realmFeasible=true;
            if(betterFeasibleCandidate(candidate,best)) best=candidate;
            continue;
          }
          // betterDiagnosticCandidate always compares these three fields first. If this route
          // already loses there, the expensive acquisition metric cannot rescue it.
          if(bestDiagnostic){
            if(hardShortfall>bestDiagnostic.hardShortfall+0.5) continue;
            if(Math.abs(hardShortfall-bestDiagnostic.hardShortfall)<=0.5){
              if(realmOverflow>bestDiagnostic.realmOverflow) continue;
              if(realmOverflow===bestDiagnostic.realmOverflow && remainingAfterMax>bestDiagnostic.remainingAfterMax+0.5) continue;
            }
          }
          const diagOreShare=resources.ore>0?go.oreCost/resources.ore:(go.oreCost>0?go.oreCost/100000:0),diagEssenceShare=resources.essence>0?so.cost/resources.essence:(so.cost>0?so.cost/100000:0),diagSandShare=resources.sand>0?ro.cost/resources.sand:(ro.cost>0?ro.cost/100000:0),diagTreatShare=resources.treat>0?fo.cost/resources.treat:(fo.cost>0?fo.cost/10000:0);
          const diagAcquisition=acquisitionFor(go,so,ro,fo);
          const diagnostic={gear:go.target,skill:so.avg,relic:ro.avg,fanto:fo.avg,skillLevels:so.levels,relicLevels:ro.levels,fantoLevels:fo.levels,oreCost:go.oreCost,essenceCost:so.cost,sandCost:ro.cost,treatCost:fo.cost,refinedCost:go.refinedCost,score,gearAdds:go.adds,skillAdds:so.adds,relicAdds:ro.adds,fantoAdds:fo.adds,overshoot:score-desired,dawniumCost,realmAttempts:realmPacks,realmPacks,oreShare:diagOreShare,essenceShare:diagEssenceShare,sandShare:diagSandShare,treatShare:diagTreatShare,acquisitionHours:diagAcquisition.hours,unknownPriceRefreshes,bankedHammersUsed:(oreRealm.bankedUsed||0),bankedKnucklesUsed:(essenceRealm.bankedUsed||0),bankedShovelsUsed:(sandRealm.bankedUsed||0),bankedToolsUsed:(oreRealm.bankedUsed||0)+(essenceRealm.bankedUsed||0)+(sandRealm.bankedUsed||0),realmOverflow,remainingAfterMax,treatShortfall,refinedShortfall,hardShortfall,seasonKey:cfg.key,realmFeasible:false,realm:{days:realmDays,ore:oreRealm,essence:essenceRealm,sand:sandRealm}};
          if(betterDiagnosticCandidate(diagnostic,bestDiagnostic)) bestDiagnostic=diagnostic;
        }
      }
    }
    return {plan:best,diagnostic:best||bestDiagnostic};
  }

async function searchPlansCooperative(baseScore,desired,p,resources,cfg=activeCalcConfig(),ctx=null,job=null){
    const checkpoint=__calculatorDeps.createOptimizerCheckpoint(job);
    await checkpoint(true);
    const context=ctx||createPlanningContext(baseScore,desired,p,cfg);
    const {baseGear,cats,gearOptions,charScore,headroomCosts}=context;
    const realmDays=Number.isFinite(resources?.realmDays)?resources.realmDays:materialRealmDaysAvailable(cfg);
    // TOTAL_POOL_SMART_BALANCE_V1: scarcity/efficiency sees projected raw + saved/already-
    // planned tools at full material equivalent. realmTopupFor() separately preserves the
    // physical consumption order (raw first). Extra candidate purchases never enter this pool.
    resources.acquisitionHeadroomCosts=headroomCosts||{};
    resources.acquisitionSupplyEquiv={
      ore:plannedToolAcquisitionSupply('ore',resources,cfg),
      essence:plannedToolAcquisitionSupply('essence',resources,cfg),
      sand:plannedToolAcquisitionSupply('sand',resources,cfg),
      treat:rawOnlyAcquisitionSupply('treat',resources,cfg)
    };
    if(baseScore>=desired){
      const zero={gear:baseGear,skill:cats.skill.avg,relic:cats.relic.avg,fanto:cats.fanto.avg,skillLevels:cats.skill.levels,relicLevels:cats.relic.levels,fantoLevels:cats.fanto.levels,oreCost:0,essenceCost:0,sandCost:0,treatCost:0,refinedCost:0,score:baseScore,gearAdds:0,skillAdds:0,relicAdds:0,fantoAdds:0,dawniumCost:0,realmAttempts:0,realmPacks:0,seasonKey:cfg.key,realmFeasible:true,realm:{days:realmDays,ore:realmTopupFor('ore',0,resources.ore,resources,cfg,p),essence:realmTopupFor('essence',0,resources.essence,resources,cfg,p),sand:realmTopupFor('sand',0,resources.sand,resources,cfg,p)}};
      return {plan:zero,diagnostic:zero};
    }
    /* RAW_FUNDED_SEARCH_FAST_V1 is intentionally disabled under
       SCARCITY_ADJUSTED_ACQUISITION_V1. Its dimensional collapse was exact only when fully
       funded non-Ore material had zero marginal value and Ore was always fixed at 1.00.
       With continuous nonzero scarcity floors, different Gear/Skill/Relic mixes retain
       different economic costs and must stay in the general exact search. */
    const nonOreRawFunded=false;
    if(nonOreRawFunded){
      const skillMax=cats.skillOptions[cats.skillOptions.length-1];
      const relicMax=cats.relicOptions[cats.relicOptions.length-1];
      const fantoMax=cats.fantoOptions[cats.fantoOptions.length-1];
      const maxNonGearScore=(skillMax?.score||0)+(relicMax?.score||0)+(fantoMax?.score||0);
      const go=__calculatorDeps.gearLocked
        ? (gearOptions[0].score>=Math.max(0,desired-charScore-maxNonGearScore)?gearOptions[0]:null)
        : firstGearOptionAtLeast(gearOptions,Math.max(0,desired-charScore-maxNonGearScore));
      if(go){
        const firstSkillAtLeast=scoreNeeded=>{
          let lo=0,hi=cats.skillOptions.length-1,ans=null;
          while(lo<=hi){
            const mid=(lo+hi)>>1;
            if(cats.skillOptions[mid].score>=scoreNeeded){ans=cats.skillOptions[mid];hi=mid-1;}else lo=mid+1;
          }
          return ans;
        };
        const oreRealm=realmTopupFor('ore',go.oreCost,resources.ore,resources,cfg,p);
        const zeroEssence=realmTopupFor('essence',0,resources.essence,resources,cfg,p);
        const zeroSand=realmTopupFor('sand',0,resources.sand,resources,cfg,p);
        const sharedAcquisition=acquisitionEffortFor({ore:go.oreCost,essence:0,sand:0,treat:0},resources,cfg);
        let fastBest=null;
        for(const ro of cats.relicOptions){
        { const pending=checkpoint(); if(pending) await pending; }
          for(const fo of cats.fantoOptions){
        { const pending=checkpoint(); if(pending) await pending; }
            const neededSkill=Math.max(0,desired-charScore-go.score-ro.score-fo.score);
            const so=firstSkillAtLeast(neededSkill);
            if(!so) continue;
            const score=charScore+go.score+so.score+ro.score+fo.score;
            if(score<desired) continue;
            const candidate=makePlanCandidate(go,so,ro,fo,score,desired,resources,[oreRealm,zeroEssence,zeroSand],sharedAcquisition);
            candidate.realm.days=realmDays;
            candidate.realmFeasible=oreRealm.feasible;
            if(!oreRealm.feasible) continue;
            if(betterFeasibleCandidate(candidate,fastBest)) fastBest=candidate;
          }
        }
        if(fastBest && candidateRealmStage(fastBest)<2) return {plan:fastBest,diagnostic:fastBest};
      }
    }
    /* REALM_OPTION_PROPERTY_CACHE_V7
       Realm top-up results are immutable for one resource allocation, but Auto-Stamina
       reuses option objects across allocations. Reset cached Realm costs in the acquisition
       prepass below so each search sees its own raw/tool budget. Hot-loop reads remain direct
       property accesses and unused Realm options are still evaluated lazily. */
    const oreFor=go=>go.__realmOreV7||(go.__realmOreV7=realmTopupFor('ore',go.oreCost,resources.ore,resources,cfg,p));
    const essFor=so=>so.__realmEssenceV7||(so.__realmEssenceV7=realmTopupFor('essence',so.cost,resources.essence,resources,cfg,p));
    const sandFor=ro=>ro.__realmSandV7||(ro.__realmSandV7=realmTopupFor('sand',ro.cost,resources.sand,resources,cfg,p));
    /* ACQUISITION_KERNEL_V2 · TOTAL_POOL_SMART_BALANCE_V1
       This metric is evaluated in the hottest optimizer loop. Precompute each category's
       scarcity-adjusted spend ONCE against the full owned/projected resource-family pool,
       read Cart/map rates once, and run the joint-reacquisition equation with scalar locals.
       Raw-funded and tool-backed candidates therefore use the same economic kernel. */
    for(const go of gearOptions){
      go.__realmOreV7=null;
      go.__acqOreV1=marginalWeightedSpend(go.oreCost,'ore',resources);
    }
    for(const so of cats.skillOptions){
      so.__realmEssenceV7=null;
      so.__acqEssenceV1=marginalWeightedSpend(so.cost,'essence',resources);
    }
    for(const ro of cats.relicOptions){
      ro.__realmSandV7=null;
      ro.__acqSandV1=marginalWeightedSpend(ro.cost,'sand',resources);
    }
    for(const fo of cats.fantoOptions) fo.__acqTreatV1=marginalWeightedSpend(fo.cost,'treat',resources);
    const acqMap=resources?.yields?.map||cfg.map||{};
    const acqCartOre=Math.max(0,__calculatorDeps.n('oreRate'));
    const acqCartEssence=Math.max(0,__calculatorDeps.n('essenceRate'));
    const acqCartSand=Math.max(0,__calculatorDeps.n('sandRate'));
    const acqCartTreat=Math.max(0,__calculatorDeps.n('treatRate'));
    const acqNodeOre=Math.max(0,Number(acqMap.ore)||0);
    const acqNodeEssence=Math.max(0,Number(acqMap.essence)||0);
    const acqNodeSand=Math.max(0,Number(acqMap.sand)||0);
    /* JOINT_HOURS_NO_CLOSURE_V2 · JOINT_HOURS_ACTIVE_SET_V9
       The acquisition equation is a three-term piecewise-linear fixed point:
         sum(max(0, demand - CartRate * hours) / nodeYield) <= hours.
       Active resources can only DROP OUT as hours rises. Precompute reciprocal node yields,
       fold the floor residual check into active-set construction, then solve each active set
       directly. With only Ore/Essence/Sand, at most three active-set solves are possible.
       This removes repeated division, the stable-set verification pass and the 48-step binary
       fallback while preserving the same mathematical root and tolerance boundaries. */
    const acqInvNodeOre=acqNodeOre>0?1/acqNodeOre:0;
    const acqInvNodeEssence=acqNodeEssence>0?1/acqNodeEssence:0;
    const acqInvNodeSand=acqNodeSand>0?1/acqNodeSand:0;
    const acqCartNodeOre=acqCartOre*acqInvNodeOre;
    const acqCartNodeEssence=acqCartEssence*acqInvNodeEssence;
    const acqCartNodeSand=acqCartSand*acqInvNodeSand;
    const nodesAtFast=(hours,ore,essence,sand)=>{
      let total=0,rem=0;
      rem=ore-acqCartOre*hours;if(rem>0){if(acqInvNodeOre<=0)return Infinity;total+=rem*acqInvNodeOre;}
      rem=essence-acqCartEssence*hours;if(rem>0){if(acqInvNodeEssence<=0)return Infinity;total+=rem*acqInvNodeEssence;}
      rem=sand-acqCartSand*hours;if(rem>0){if(acqInvNodeSand<=0)return Infinity;total+=rem*acqInvNodeSand;}
      return total;
    };
    const jointHoursFast=(oreRaw,essRaw,sandRaw,treatRaw)=>{
      const ore=oreRaw>0?oreRaw:0;
      const essence=essRaw>0?essRaw:0;
      const sand=sandRaw>0?sandRaw:0;
      const treat=treatRaw>0?treatRaw:0;
      let floor=0;
      if(treat>0){
        if(acqCartTreat<=0) return 1e9;
        floor=treat/acqCartTreat;
      }
      if(ore>0&&acqInvNodeOre<=0){if(acqCartOre<=0)return 1e9;floor=Math.max(floor,ore/acqCartOre);}
      if(essence>0&&acqInvNodeEssence<=0){if(acqCartEssence<=0)return 1e9;floor=Math.max(floor,essence/acqCartEssence);}
      if(sand>0&&acqInvNodeSand<=0){if(acqCartSand<=0)return 1e9;floor=Math.max(floor,sand/acqCartSand);}
      let mask=0,floorNodes=0,rem=0;
      rem=ore-acqCartOre*floor;
      if(rem>1e-9&&acqInvNodeOre>0){mask|=1;floorNodes+=rem*acqInvNodeOre;}
      rem=essence-acqCartEssence*floor;
      if(rem>1e-9&&acqInvNodeEssence>0){mask|=2;floorNodes+=rem*acqInvNodeEssence;}
      rem=sand-acqCartSand*floor;
      if(rem>1e-9&&acqInvNodeSand>0){mask|=4;floorNodes+=rem*acqInvNodeSand;}
      if(!mask||floorNodes<=floor+1e-9) return floor;
      let hours=floor;
      for(let pass=0;pass<3;pass++){
        let numerator=0,denominator=1;
        if(mask&1){numerator+=ore*acqInvNodeOre;denominator+=acqCartNodeOre;}
        if(mask&2){numerator+=essence*acqInvNodeEssence;denominator+=acqCartNodeEssence;}
        if(mask&4){numerator+=sand*acqInvNodeSand;denominator+=acqCartNodeSand;}
        hours=Math.max(floor,numerator/denominator);
        let next=0;
        if((mask&1)&&ore>acqCartOre*hours+1e-9) next|=1;
        if((mask&2)&&essence>acqCartEssence*hours+1e-9) next|=2;
        if((mask&4)&&sand>acqCartSand*hours+1e-9) next|=4;
        if(next===mask) return hours;
        mask=next;
        if(!mask) return floor;
      }
      // Three resources means a non-empty active set must stabilize within three passes.
      return hours;
    };
    const acquisitionFor=(go,so,ro,fo)=>({hours:jointHoursFast(go.__acqOreV1,so.__acqEssenceV1,ro.__acqSandV1,fo.__acqTreatV1)});
    /* ACQUISITION_LIMIT_PRECHECK_V8
       For the no-paid bounded search acquisition hours are the primary comparator. Before
       solving the piecewise joint-hours equation, test the current winner's time directly:
       if Treat Cart production cannot cover Treat demand by that time, or the map-node work
       still exceeds the same time budget, the candidate's exact joint root must be later and
       it cannot win. This is a necessary-condition rejection only; surviving candidates still
       run the original exact jointHoursFast() and the normal tie-break chain. */
    const acquisitionCannotBeat=(bestHours,go,so,ro,fo)=>{
      if(!Number.isFinite(bestHours)||bestHours>=1e9) return false;
      const limit=bestHours+1e-9;
      const treat=fo.__acqTreatV1;
      if(treat>0){
        if(acqCartTreat<=0) return true;
        if(treat>acqCartTreat*limit+1e-7) return true;
      }
      return nodesAtFast(limit,go.__acqOreV1,so.__acqEssenceV1,ro.__acqSandV1)>limit+1e-7;
    };
    let best=null,bestDiagnostic=null;
    /* OWNED_POOL_IMPOSSIBILITY_FASTPATH_V4 · TOTAL_POOL_SMART_BALANCE_V1
       Prove whether ANY route using projected raw + saved/already-planned tools can reach the
       target before deciding whether a paid-refresh fast-path result needs the expensive scan.
       Extra candidate purchases are excluded from these budgets. */
    const highestAffordable=(options,budget,costKey='cost',secondaryBudget=Infinity,secondaryKey='')=>{
      let bestOption=Array.isArray(options)&&options.length?options[0]:null;
      for(const option of (options||[])){
        const primary=Math.max(0,Number(option?.[costKey])||0);
        const secondary=secondaryKey?Math.max(0,Number(option?.[secondaryKey])||0):0;
        if(primary<=budget+0.5 && secondary<=secondaryBudget+0.5) bestOption=option;
        else if(primary>budget+0.5) break;
      }
      return bestOption;
    };
    const poolRefinedBudget=resources.refinedTracked?Math.max(0,Number(resources.refined)||0):Infinity;
    const poolMaxGear=highestAffordable(gearOptions,plannedToolAcquisitionSupply('ore',resources,cfg),'oreCost',poolRefinedBudget,'refinedCost');
    const poolMaxSkill=highestAffordable(cats.skillOptions,plannedToolAcquisitionSupply('essence',resources,cfg));
    const poolMaxRelic=highestAffordable(cats.relicOptions,plannedToolAcquisitionSupply('sand',resources,cfg));
    const poolMaxFanto=highestAffordable(cats.fantoOptions,Math.max(0,Number(resources.treat)||0));
    const ownedPoolMaxScore=charScore+(poolMaxGear?.score||0)+(poolMaxSkill?.score||0)+(poolMaxRelic?.score||0)+(poolMaxFanto?.score||0);
    const ownedPoolRoutePossible=ownedPoolMaxScore>=desired-1e-9;
    /* TREAT_FUNDED_SEARCH_FAST_V1
       Exact dimensional collapse when raw Treats already fund every reachable Fantomon
       upgrade. In that state the configured fully-funded Treat acquisition floor is zero,
       so Fantomon score is free in the PRIMARY acquisition metric.
       For each Skill+Relic choice, the best acquisition route therefore uses enough free
       Fantomon score to force Gear to its lowest possible option. Once that Gear option is
       fixed, extra Fantomon upgrades cannot improve acquisition and only worsen/equal the
       normal overscore/share tie-breaks, so select the first Fantomon option that reaches
       target. This replaces Relic x Fantomon x Skill with Relic x Skill while preserving
       the exact candidate comparator. */
    /* REFINED_FASTPATH_GUARD_V3
       Keep the Treat-funded dimensional collapse disabled whenever Refined Ore tracking is
       active. Even a numerically funded Refined pool still participates in downstream share/
       tie-break semantics, so collapsing that dimension changes the exact chosen plan. */
    const treatFullyFunded=!resources.refinedTracked &&
      (Number(resources.treat)||0)>=Math.max(0,Number(headroomCosts?.treat)||0)-0.5;
    if(treatFullyFunded && cats.fantoOptions.length>1){
      const fantoMax=cats.fantoOptions[cats.fantoOptions.length-1];
      const firstFantoAtLeast=scoreNeeded=>{
        let lo=0,hi=cats.fantoOptions.length-1,ans=null;
        while(lo<=hi){
          const mid=(lo+hi)>>1;
          if(cats.fantoOptions[mid].score>=scoreNeeded){ans=cats.fantoOptions[mid];hi=mid-1;}else lo=mid+1;
        }
        return ans;
      };
      let fastBest=null,fastDiagnostic=null;
      for(const ro of cats.relicOptions){
        { const pending=checkpoint(); if(pending) await pending; }
        const sandRealm=sandFor(ro);
        for(const so of cats.skillOptions){
          const fixedScore=charScore+ro.score+so.score;
          const go=__calculatorDeps.gearLocked
            ? (gearOptions[0].score+fantoMax.score>=Math.max(0,desired-fixedScore)?gearOptions[0]:null)
            : firstGearOptionAtLeast(gearOptions,Math.max(0,desired-fixedScore-fantoMax.score));
          if(!go) continue;
          const neededFanto=Math.max(0,desired-fixedScore-go.score);
          const fo=firstFantoAtLeast(neededFanto);
          if(!fo) continue;
          const score=fixedScore+go.score+fo.score;
          if(score<desired) continue;
          const oreRealm=oreFor(go),essenceRealm=essFor(so);
          const refinedShortfall=0;
          const hardShortfall=0;
          const realms=[oreRealm,essenceRealm,sandRealm];
          const realmOverflow=realms.reduce((sum,x)=>sum+Math.max(0,(Number.isFinite(x.packs)?x.packs:1e9)-(x.maxPacks||0)),0);
          const remainingAfterMax=realms.reduce((sum,x)=>sum+Math.max(0,x.remainingAfterMax||0),0);
          const realmPacks=realms.reduce((sum,x)=>sum+(Number.isFinite(x.packs)?x.packs:1e9),0);
          const allFeasible=realms.every(x=>x.feasible);
          const dawniumCost=allFeasible?realms.reduce((sum,x)=>sum+x.dawnium,0):Infinity;
          const unknownPriceRefreshes=realms.reduce((sum,x)=>sum+Math.max(0,Number(x?.unknownPriceRefreshes)||0),0);
          const acquisition=acquisitionFor(go,so,ro,fo);
          if(allFeasible){
            const candidate=makePlanCandidate(go,so,ro,fo,score,desired,resources,realms,acquisition);
            candidate.realm.days=realmDays;
            candidate.realmFeasible=true;
            if(betterFeasibleCandidate(candidate,fastBest)) fastBest=candidate;
            continue;
          }
          const treatShortfall=0;
          const diagOreShare=resources.ore>0?go.oreCost/resources.ore:(go.oreCost>0?go.oreCost/100000:0);
          const diagEssenceShare=resources.essence>0?so.cost/resources.essence:(so.cost>0?so.cost/100000:0);
          const diagSandShare=resources.sand>0?ro.cost/resources.sand:(ro.cost>0?ro.cost/100000:0);
          const diagTreatShare=resources.treat>0?fo.cost/resources.treat:0;
          const diagnostic={gear:go.target,skill:so.avg,relic:ro.avg,fanto:fo.avg,skillLevels:so.levels,relicLevels:ro.levels,fantoLevels:fo.levels,oreCost:go.oreCost,essenceCost:so.cost,sandCost:ro.cost,treatCost:fo.cost,refinedCost:go.refinedCost,score,gearAdds:go.adds,skillAdds:so.adds,relicAdds:ro.adds,fantoAdds:fo.adds,overshoot:score-desired,dawniumCost,realmAttempts:realmPacks,realmPacks,oreShare:diagOreShare,essenceShare:diagEssenceShare,sandShare:diagSandShare,treatShare:diagTreatShare,acquisitionHours:acquisition.hours,unknownPriceRefreshes,bankedHammersUsed:(oreRealm.bankedUsed||0),bankedKnucklesUsed:(essenceRealm.bankedUsed||0),bankedShovelsUsed:(sandRealm.bankedUsed||0),bankedToolsUsed:(oreRealm.bankedUsed||0)+(essenceRealm.bankedUsed||0)+(sandRealm.bankedUsed||0),realmOverflow,remainingAfterMax,treatShortfall,refinedShortfall,hardShortfall,seasonKey:cfg.key,realmFeasible:false,realm:{days:realmDays,ore:oreRealm,essence:essenceRealm,sand:sandRealm}};
          if(betterDiagnosticCandidate(diagnostic,fastDiagnostic)) fastDiagnostic=diagnostic;
        }
      }
      if(fastBest && (candidateRealmStage(fastBest)<2 || !ownedPoolRoutePossible)) return {plan:fastBest,diagnostic:fastBest};
      // If the owned/projected pool can still reach the target without extra purchases, keep
      // scanning before accepting a paid-refresh route because extra purchases are last resort.
    }
    /* BOUNDED_FEASIBLE_SEARCH_V1
       Before the expensive diagnostic scan, prove the largest independently fundable
       option in each resource family. Because Gear/Ore, Skills/Essence, Relics/Sand and
       Fantomons/Treats use separate budgets in this model, the sum of those maxima proves
       whether at least one fully fundable target route exists.
       If a route exists without EXTRA Realm purchases, paid-refresh candidates are
       categorically worse under betterFeasibleCandidate(), so search only the owned/raw+
       banked-tool prefixes. Otherwise, if a route exists within maximum legal Realm
       capacity, search only the individually feasible prefixes. This cannot change the
       winner: every excluded option is either physically impossible or belongs to a
       sourcing tier that loses before acquisition-effort tie-breaks are considered.
       The bounded scan also starts each monotone category at the first score that could
       possibly reach the target even with all remaining categories maxed. That removes
       millions of low-score combinations that previously called the Gear binary search
       only to discover that no Gear option could make them reach target. */
    const lastTrueIndex=(options,predicate)=>{
      let lo=0,hi=(options?.length||0)-1,ans=-1;
      while(lo<=hi){
        const mid=(lo+hi)>>1;
        if(predicate(options[mid],mid)){ans=mid;lo=mid+1;}else hi=mid-1;
      }
      return ans;
    };
    const firstScoreIndex=(options,scoreNeeded)=>{
      const need=Math.max(0,Number(scoreNeeded)||0);
      let lo=0,hi=(options?.length||0)-1,ans=options?.length||0;
      while(lo<=hi){
        const mid=(lo+hi)>>1;
        if((Number(options[mid]?.score)||0)>=need){ans=mid;hi=mid-1;}else lo=mid+1;
      }
      return ans;
    };
    const refinedFunded=go=>!resources.refinedTracked || (Number(go?.refinedCost)||0)<=(Number(resources.refined)||0)+0.5;
    const noPaidRealm=x=>!!x?.feasible && Math.max(0,Number(x?.packs)||0)<=0;
    const feasibleLast={
      gear:lastTrueIndex(gearOptions,go=>refinedFunded(go)&&!!oreFor(go)?.feasible),
      skill:lastTrueIndex(cats.skillOptions,so=>!!essFor(so)?.feasible),
      relic:lastTrueIndex(cats.relicOptions,ro=>!!sandFor(ro)?.feasible),
      fanto:lastTrueIndex(cats.fantoOptions,fo=>(Number(fo?.cost)||0)<=(Number(resources.treat)||0)+0.5)
    };
    const noPaidLast={
      gear:lastTrueIndex(gearOptions,go=>refinedFunded(go)&&noPaidRealm(oreFor(go))),
      skill:lastTrueIndex(cats.skillOptions,so=>noPaidRealm(essFor(so))),
      relic:lastTrueIndex(cats.relicOptions,ro=>noPaidRealm(sandFor(ro))),
      fanto:feasibleLast.fanto
    };
    const scoreAt=(options,index)=>index>=0?(Number(options[index]?.score)||0):-Infinity;
    const maxRouteScore=last=>charScore+
      scoreAt(gearOptions,last.gear)+scoreAt(cats.skillOptions,last.skill)+
      scoreAt(cats.relicOptions,last.relic)+scoreAt(cats.fantoOptions,last.fanto);
    const noPaidRoutePossible=Object.values(noPaidLast).every(i=>i>=0) && maxRouteScore(noPaidLast)>=desired-1e-9;
    const feasibleRoutePossible=Object.values(feasibleLast).every(i=>i>=0) && maxRouteScore(feasibleLast)>=desired-1e-9;
    const boundedLast=noPaidRoutePossible?noPaidLast:(feasibleRoutePossible?feasibleLast:null);
    if(boundedLast){
      const boundedGear=gearOptions.slice(0,boundedLast.gear+1);
      const boundedSkill=cats.skillOptions.slice(0,boundedLast.skill+1);
      const boundedRelic=cats.relicOptions.slice(0,boundedLast.relic+1);
      /* ZERO_RATE_FANTO_PRUNE_V1
         Treats have no map/Realm reacquisition path. If Treat Cart income is zero, any
         Fantomon upgrade has the optimizer's 1e9 acquisition penalty. When the target is
         already reachable in the same preferred no-paid sourcing tier with the current
         Fantomon level, every positive-Treat Fantomon option is strictly worse before
         overscore/share tie-breaks are consulted. Keep only the zero-cost base option.
         This is especially important for well-funded accounts: the old exact scan still
         walked hundreds of Fantomon states even though none could beat a finite-acquisition
         base-Fantomon route. */
      let boundedFantoLast=boundedLast.fanto;
      if(noPaidRoutePossible && acqCartTreat<=0 && (Number(cats.fantoOptions[0]?.__acqTreatV1)||0)<=1e-9){
        const baseFantoScore=Number(cats.fantoOptions[0]?.score)||0;
        const noPaidBaseFantoMax=charScore+
          scoreAt(gearOptions,noPaidLast.gear)+scoreAt(cats.skillOptions,noPaidLast.skill)+
          scoreAt(cats.relicOptions,noPaidLast.relic)+baseFantoScore;
        if(noPaidBaseFantoMax>=desired-1e-9) boundedFantoLast=0;
      }
      const boundedFanto=cats.fantoOptions.slice(0,boundedFantoLast+1);
      const maxGearScore=Number(boundedGear[boundedGear.length-1]?.score)||0;
      const maxSkillScore=Number(boundedSkill[boundedSkill.length-1]?.score)||0;
      const maxFantoScore=Number(boundedFanto[boundedFanto.length-1]?.score)||0;
      /* BOUNDED_EAGER_REALM_V12
         The exact bounded scan revisits the same Gear/Skill/Relic options thousands of times.
         Materialize each immutable Realm result once for this search snapshot and store the
         refined-funding bit on Gear. The hot loops then use direct property reads instead of
         repeatedly entering oreFor()/essFor()/sandFor()/refinedFunded() wrappers. */
      for(const go of boundedGear){ go.__realmOreV7=oreFor(go); go.__refinedFundedV12=refinedFunded(go); }
      for(const so of boundedSkill) so.__realmEssenceV7=essFor(so);
      for(const ro of boundedRelic) ro.__realmSandV7=sandFor(ro);
      const relicStart=firstScoreIndex(boundedRelic,desired-charScore-maxGearScore-maxSkillScore-maxFantoScore);
      let boundedBest=null;
      /* COARSE_EXACT_SEED_V1
         Give branch-and-bound a strong VALID upper bound before the exhaustive scan.
         Sample a small evenly-spaced set of Relic/Fantomon states, but search the complete
         monotone Skill->minimum-Gear frontier inside each sampled state. Every seed is a
         normal exact candidate scored by the same comparator; it can only make later
         lower-bound pruning stronger, never alter correctness. */
      const sampledIndices=(start,length,count=10)=>{
        const out=new Set();
        const first=Math.max(0,Math.min(length-1,start));
        const last=Math.max(first,length-1);
        if(length<=0) return [];
        if(last===first) return [first];
        for(let i=0;i<count;i++) out.add(Math.round(first+(last-first)*(i/(count-1))));
        return [...out].sort((a,b)=>a-b);
      };
      for(const ri of sampledIndices(relicStart,boundedRelic.length,10)){
        { const pending=checkpoint(); if(pending) await pending; }
        const ro=boundedRelic[ri],sandRealm=ro.__realmSandV7;
        const fantoStart=firstScoreIndex(boundedFanto,desired-charScore-ro.score-maxGearScore-maxSkillScore);
        for(const fi of sampledIndices(fantoStart,boundedFanto.length,10)){
        { const pending=checkpoint(); if(pending) await pending; }
          const fo=boundedFanto[fi];
          const fixedBeforeSkill=charScore+ro.score+fo.score;
          const skillStart=firstScoreIndex(boundedSkill,desired-fixedBeforeSkill-maxGearScore);
          if(skillStart>=boundedSkill.length) continue;
          /* SKILL_GEAR_TWO_POINTER_V10
             The old loop walked every Skill option and binary-searched Gear each time, then
             discarded all but the FIRST Skill state mapping to each minimum Gear step. Keep
             that exact candidate frontier/order, but walk it with monotone Skill/Gear cursors:
             one Gear binary search to enter the frontier, then a linear scan only until the
             next lower Gear step becomes sufficient. No per-Skill Gear binary searches. */
          let si=skillStart;
          let gi=__calculatorDeps.gearLocked?0:firstScoreIndex(boundedGear,desired-fixedBeforeSkill-boundedSkill[si].score);
          while(si<boundedSkill.length&&gi<boundedGear.length){
        { const pending=checkpoint(); if(pending) await pending; }
            const so=boundedSkill[si],go=boundedGear[gi];
            const score=fixedBeforeSkill+so.score+go.score;
            if(score>=desired&&go.__refinedFundedV12){
              const oreRealm=go.__realmOreV7,essenceRealm=so.__realmEssenceV7;
              if(oreRealm.feasible&&essenceRealm.feasible&&sandRealm.feasible &&
                 !(noPaidRoutePossible&&boundedBest&&acquisitionCannotBeat(boundedBest.acquisitionHours,go,so,ro,fo))){
                const acquisition=acquisitionFor(go,so,ro,fo);
                if(!(noPaidRoutePossible&&boundedBest&&acquisition.hours>boundedBest.acquisitionHours+1e-9)){
                  const candidate=makePlanCandidate(go,so,ro,fo,score,desired,resources,[oreRealm,essenceRealm,sandRealm],acquisition);
                  candidate.realm.days=realmDays;
                  candidate.realmFeasible=true;
                  if(noPaidRoutePossible&&boundedBest&&acquisition.hours<boundedBest.acquisitionHours-1e-9){
                    boundedBest=candidate;
                  }else if(betterFeasibleCandidate(candidate,boundedBest)) boundedBest=candidate;
                }
              }
            }
            if(__calculatorDeps.gearLocked||gi===0) break;
            const nextGearScore=Number(boundedGear[gi-1]?.score)||0;
            do{si++;}while(si<boundedSkill.length &&
              fixedBeforeSkill+(Number(boundedSkill[si]?.score)||0)+nextGearScore<desired-1e-9);
            if(si>=boundedSkill.length) break;
            const need=desired-fixedBeforeSkill-(Number(boundedSkill[si]?.score)||0);
            while(gi>0&&(Number(boundedGear[gi-1]?.score)||0)>=need-1e-9) gi--;
          }
        }
      }
      /* ACQUISITION_LOWER_BOUND_PRUNE_V1 · MONOTONE_BOUND_BINARY_PRUNE_V2
         jointHoursFast() is monotone in every resource demand. Instead of evaluating the
         same lower-bound equation once for every Relic/Fantomon/Skill iteration, binary-search
         the first option that is already worse than the current exact seed. This preserves the
         identical candidate set: only a monotone suffix that the old loop would immediately
         break on is skipped. A later/improved best can only make these precomputed ends loose,
         never incorrectly exclude a winner. */
      const firstWorseIndex=(options,start,hoursFor)=>{
        if(!boundedBest) return options.length;
        const limit=boundedBest.acquisitionHours+1e-9;
        let lo=Math.max(0,start),hi=options.length-1,ans=options.length;
        while(lo<=hi){
          const mid=(lo+hi)>>1;
          if(hoursFor(options[mid])>limit){ans=mid;hi=mid-1;}else lo=mid+1;
        }
        return ans;
      };
      const relicEnd=firstWorseIndex(boundedRelic,relicStart,ro=>jointHoursFast(0,0,ro.__acqSandV1,0));
      for(let ri=relicStart;ri<relicEnd;ri++){
        { const pending=checkpoint(); if(pending) await pending; }
        const ro=boundedRelic[ri];
        /* DYNAMIC_OUTER_BOUND_V12
           relicEnd/fantoEnd are based on the seed winner. If the exact scan finds a faster
           winner, refresh the cheap monotone subset bound inline so we can stop the now-dead
           Relic/Fantomon suffix immediately. */
        if(noPaidRoutePossible&&boundedBest&&
           jointHoursFast(0,0,ro.__acqSandV1,0)>boundedBest.acquisitionHours+1e-9) break;
        const sandRealm=ro.__realmSandV7;
        const fantoStart=firstScoreIndex(boundedFanto,desired-charScore-ro.score-maxGearScore-maxSkillScore);
        const fantoEnd=firstWorseIndex(boundedFanto,fantoStart,fo=>jointHoursFast(0,0,ro.__acqSandV1,fo.__acqTreatV1));
        for(let fi=fantoStart;fi<fantoEnd;fi++){
        { const pending=checkpoint(); if(pending) await pending; }
          const fo=boundedFanto[fi];
          if(noPaidRoutePossible&&boundedBest&&
             jointHoursFast(0,0,ro.__acqSandV1,fo.__acqTreatV1)>boundedBest.acquisitionHours+1e-9) break;
          const fixedBeforeSkill=charScore+ro.score+fo.score;
          const skillStart=firstScoreIndex(boundedSkill,desired-fixedBeforeSkill-maxGearScore);
          if(skillStart>=boundedSkill.length) continue;
          const skillEnd=firstWorseIndex(boundedSkill,skillStart,so=>jointHoursFast(0,so.__acqEssenceV1,ro.__acqSandV1,fo.__acqTreatV1));
          if(skillStart>=skillEnd) continue;
          /* SKILL_GEAR_TWO_POINTER_V10
             Same exact frontier as the legacy duplicate-skip loop, but without a Gear binary
             search for every skipped Skill state. Skill only rises and required Gear only
             falls, so a pair of monotone cursors visits the first Skill state of each Gear
             step in identical order. */
          let si=skillStart;
          let gi=__calculatorDeps.gearLocked?0:firstScoreIndex(boundedGear,desired-fixedBeforeSkill-boundedSkill[si].score);
          while(si<skillEnd&&gi<boundedGear.length){
            const so=boundedSkill[si],go=boundedGear[gi];
            const score=fixedBeforeSkill+so.score+go.score;
            if(score>=desired&&go.__refinedFundedV12){
              const oreRealm=go.__realmOreV7,essenceRealm=so.__realmEssenceV7;
              if(oreRealm.feasible&&essenceRealm.feasible&&sandRealm.feasible){
                const dominated=boundedBest && go.oreCost>=boundedBest.oreCost &&
                  so.cost>=boundedBest.essenceCost && ro.cost>=boundedBest.sandCost &&
                  fo.cost>=boundedBest.treatCost && go.refinedCost>=boundedBest.refinedCost;
                if(!dominated &&
                   !(noPaidRoutePossible&&boundedBest&&acquisitionCannotBeat(boundedBest.acquisitionHours,go,so,ro,fo))){
                  const acquisition=acquisitionFor(go,so,ro,fo);
                  if(!(noPaidRoutePossible&&boundedBest&&acquisition.hours>boundedBest.acquisitionHours+1e-9)){
                    const candidate=makePlanCandidate(go,so,ro,fo,score,desired,resources,[oreRealm,essenceRealm,sandRealm],acquisition);
                    candidate.realm.days=realmDays;
                    candidate.realmFeasible=true;
                    if(noPaidRoutePossible&&boundedBest&&acquisition.hours<boundedBest.acquisitionHours-1e-9){
                      boundedBest=candidate;
                    }else if(betterFeasibleCandidate(candidate,boundedBest)) boundedBest=candidate;
                  }
                }
              }
            }
            if(__calculatorDeps.gearLocked||gi===0) break;
            const nextGearScore=Number(boundedGear[gi-1]?.score)||0;
            do{si++;}while(si<skillEnd &&
              fixedBeforeSkill+(Number(boundedSkill[si]?.score)||0)+nextGearScore<desired-1e-9);
            if(si>=skillEnd) break;
            const need=desired-fixedBeforeSkill-(Number(boundedSkill[si]?.score)||0);
            while(gi>0&&(Number(boundedGear[gi-1]?.score)||0)>=need-1e-9) gi--;
          }
        }
      }
      if(boundedBest) return {plan:boundedBest,diagnostic:boundedBest};
      // Defensive fall-through: if future rule changes violate one of the monotonic
      // assumptions above, the legacy full scan below still preserves correctness.
    }
    /* AFFORDABLE_TREAT_FEASIBLE_V1
       Treats have no Material-Realm top-up path. Any actually FUNDABLE plan must therefore
       choose a Fantomon option whose Treat cost is already covered by projected Treat
       inventory. When that affordable slice is much smaller than the full Fantomon search
       range, do a cheap feasible-only pass first. If it finds a plan, every excluded
       Fantomon option is provably infeasible and the expensive diagnostic scan is unnecessary.
       If it finds nothing, fall through to the complete scan so shortfall diagnostics remain exact. */
    const affordableFantoOptions=cats.fantoOptions.filter(fo=>fo.cost<=(Number(resources.treat)||0)+0.5);
    if(affordableFantoOptions.length>0 && affordableFantoOptions.length*1.25<cats.fantoOptions.length){
      let affordableBest=null;
      for(const ro of cats.relicOptions){
        { const pending=checkpoint(); if(pending) await pending; }
        const sandRealm=sandFor(ro);
        for(const fo of affordableFantoOptions){
          const fixedBeforeSkill=charScore+ro.score+fo.score;
          let lastGearAdds=null;
          for(const so of cats.skillOptions){
            const fixedScore=fixedBeforeSkill+so.score;
            const go=__calculatorDeps.gearLocked?(gearOptions[0].score>=Math.max(0,desired-fixedScore)?gearOptions[0]:null):firstGearOptionAtLeast(gearOptions,Math.max(0,desired-fixedScore));
            if(!go) continue;
            if(lastGearAdds===go.adds) continue;
            lastGearAdds=go.adds;
            const score=fixedScore+go.score;
            if(score<desired) continue;
            const refinedShortfall=resources.refinedTracked?Math.max(0,go.refinedCost-resources.refined):0;
            if(refinedShortfall>0.5) continue;
            const oreRealm=oreFor(go),essenceRealm=essFor(so);
            const realms=[oreRealm,essenceRealm,sandRealm];
            if(!realms.every(x=>x.feasible)) continue;
            if(affordableBest && go.oreCost>=affordableBest.oreCost && so.cost>=affordableBest.essenceCost && ro.cost>=affordableBest.sandCost && fo.cost>=affordableBest.treatCost && go.refinedCost>=affordableBest.refinedCost) continue;
            const acquisition=acquisitionFor(go,so,ro,fo);
            const candidate=makePlanCandidate(go,so,ro,fo,score,desired,resources,realms,acquisition);
            candidate.realm.days=realmDays;
            candidate.realmFeasible=true;
            if(betterFeasibleCandidate(candidate,affordableBest)) affordableBest=candidate;
          }
        }
      }
      if(affordableBest) return {plan:affordableBest,diagnostic:affordableBest};
    }
    for(const ro of cats.relicOptions){
        { const pending=checkpoint(); if(pending) await pending; }
      const sandRealm=sandFor(ro);
      for(const fo of cats.fantoOptions){
        { const pending=checkpoint(); if(pending) await pending; }
        const treatShortfall=Math.max(0,fo.cost-resources.treat);
        const fixedBeforeSkill=charScore+ro.score+fo.score;
        let lastGearAdds=null;
        for(const so of cats.skillOptions){
          const fixedScore=fixedBeforeSkill+so.score;
          const go=__calculatorDeps.gearLocked?(gearOptions[0].score>=Math.max(0,desired-fixedScore)?gearOptions[0]:null):firstGearOptionAtLeast(gearOptions,Math.max(0,desired-fixedScore));
          if(!go)continue;
          // PERFORMANCE_STABILIZATION_V1: if Gear did not step down, this later Skill
          // option spends more Essence for the same required Gear and cannot win.
          if(lastGearAdds===go.adds) continue;
          lastGearAdds=go.adds;
          const score=fixedScore+go.score;if(score<desired)continue;
          const oreRealm=oreFor(go),essenceRealm=essFor(so);
          const refinedShortfall=resources.refinedTracked?Math.max(0,go.refinedCost-resources.refined):0;
          const hardShortfall=treatShortfall+refinedShortfall;
          const realms=[oreRealm,essenceRealm,sandRealm];
          const realmOverflow=realms.reduce((sum,x)=>sum+Math.max(0,(Number.isFinite(x.packs)?x.packs:1e9)-(x.maxPacks||0)),0);
          const remainingAfterMax=realms.reduce((sum,x)=>sum+Math.max(0,x.remainingAfterMax||0),0);
          const realmPacks=realms.reduce((sum,x)=>sum+(Number.isFinite(x.packs)?x.packs:1e9),0);
          const allFeasible=realms.every(x=>x.feasible)&&hardShortfall<=0.5;
          const dawniumCost=allFeasible?realms.reduce((sum,x)=>sum+x.dawnium,0):Infinity;
          const unknownPriceRefreshes=realms.reduce((sum,x)=>sum+Math.max(0,Number(x?.unknownPriceRefreshes)||0),0);
          if(allFeasible){
            // A route that costs at least as much as the current winner in every tracked
            // resource (and Refined Ore) is strictly dominated and cannot win later tie-breaks.
            if(best && go.oreCost>=best.oreCost && so.cost>=best.essenceCost && ro.cost>=best.sandCost && fo.cost>=best.treatCost && go.refinedCost>=best.refinedCost) continue;
            const acquisition=acquisitionFor(go,so,ro,fo);
            const candidate=makePlanCandidate(go,so,ro,fo,score,desired,resources,[oreRealm,essenceRealm,sandRealm],acquisition);
            candidate.realm.days=realmDays;
            candidate.realmFeasible=true;
            if(betterFeasibleCandidate(candidate,best)) best=candidate;
            continue;
          }
          // betterDiagnosticCandidate always compares these three fields first. If this route
          // already loses there, the expensive acquisition metric cannot rescue it.
          if(bestDiagnostic){
            if(hardShortfall>bestDiagnostic.hardShortfall+0.5) continue;
            if(Math.abs(hardShortfall-bestDiagnostic.hardShortfall)<=0.5){
              if(realmOverflow>bestDiagnostic.realmOverflow) continue;
              if(realmOverflow===bestDiagnostic.realmOverflow && remainingAfterMax>bestDiagnostic.remainingAfterMax+0.5) continue;
            }
          }
          const diagOreShare=resources.ore>0?go.oreCost/resources.ore:(go.oreCost>0?go.oreCost/100000:0),diagEssenceShare=resources.essence>0?so.cost/resources.essence:(so.cost>0?so.cost/100000:0),diagSandShare=resources.sand>0?ro.cost/resources.sand:(ro.cost>0?ro.cost/100000:0),diagTreatShare=resources.treat>0?fo.cost/resources.treat:(fo.cost>0?fo.cost/10000:0);
          const diagAcquisition=acquisitionFor(go,so,ro,fo);
          const diagnostic={gear:go.target,skill:so.avg,relic:ro.avg,fanto:fo.avg,skillLevels:so.levels,relicLevels:ro.levels,fantoLevels:fo.levels,oreCost:go.oreCost,essenceCost:so.cost,sandCost:ro.cost,treatCost:fo.cost,refinedCost:go.refinedCost,score,gearAdds:go.adds,skillAdds:so.adds,relicAdds:ro.adds,fantoAdds:fo.adds,overshoot:score-desired,dawniumCost,realmAttempts:realmPacks,realmPacks,oreShare:diagOreShare,essenceShare:diagEssenceShare,sandShare:diagSandShare,treatShare:diagTreatShare,acquisitionHours:diagAcquisition.hours,unknownPriceRefreshes,bankedHammersUsed:(oreRealm.bankedUsed||0),bankedKnucklesUsed:(essenceRealm.bankedUsed||0),bankedShovelsUsed:(sandRealm.bankedUsed||0),bankedToolsUsed:(oreRealm.bankedUsed||0)+(essenceRealm.bankedUsed||0)+(sandRealm.bankedUsed||0),realmOverflow,remainingAfterMax,treatShortfall,refinedShortfall,hardShortfall,seasonKey:cfg.key,realmFeasible:false,realm:{days:realmDays,ore:oreRealm,essence:essenceRealm,sand:sandRealm}};
          if(betterDiagnosticCandidate(diagnostic,bestDiagnostic)) bestDiagnostic=diagnostic;
        }
      }
    }
    return {plan:best,diagnostic:best||bestDiagnostic};
  }

async function solveTargetWithAutoStaminaCooperative(baseScore,desired,p,baseResources,cfg=activeCalcConfig(),job=null){
    // COOPERATIVE_OPTIMIZER_BOOTSTRAP_V2: paint the progress panel and honor a queued
    // cancellation before any structural option-building work can occupy the main thread.
    const bootstrapCheckpoint=__calculatorDeps.createOptimizerCheckpoint(job);
    await bootstrapCheckpoint(true);
    const ctx=createPlanningContext(baseScore,desired,p,cfg);
    await bootstrapCheckpoint(true);
    // Below the verified S2 Lv.120 map bracket, keep Stamina out of the numeric budget rather than guessing yields.
    if(!baseResources.yields?.mapReady){
      const allocation={ore:0,essence:0,sand:0,rolla:0,unassigned:baseResources.staminaNodes||0};
      const resources=applyStaminaAllocation(baseResources,allocation,cfg);
      const result=await searchPlansCooperative(baseScore,desired,p,resources,cfg,ctx,job);
      return {plan:result.plan,diagnostic:result.plan||result.diagnostic,resources,allocation};
    }
    // Manual Stamina destinations do not depend on a score plan; apply them once and solve normally.
    if(__calculatorDeps.staminaMode()!=='auto'){
      const allocation=__calculatorDeps.allocateStaminaForPlan(null,baseResources,cfg,p);
      const resources=applyStaminaAllocation(baseResources,allocation,cfg);
      const result=await searchPlansCooperative(baseScore,desired,p,resources,cfg,ctx,job);
      return {plan:result.plan,diagnostic:result.plan||result.diagnostic,resources,allocation};
    }
    const total=Math.max(0,Math.floor(baseResources.staminaNodes||0));
    const map=baseResources.yields?.map||{};
    const empty={ore:0,essence:0,sand:0,rolla:0,unassigned:0};
    const resultState=async (allocation)=>{
      const resources=applyStaminaAllocation(baseResources,allocation,cfg);
      const result=await searchPlansCooperative(baseScore,desired,p,resources,cfg,ctx,job);
      return {plan:result.plan,diagnostic:result.plan||result.diagnostic,resources,allocation,result};
    };
    const betterState=(state,best)=>{
      if(!best) return true;
      const cp=state.result.plan,bp=best.result.plan;
      if(!!cp!==!!bp) return !!cp;
      if(cp&&bp){
        if(betterFeasibleCandidate(cp,bp)) return true;
        if(betterFeasibleCandidate(bp,cp)) return false;
        return false;
      }
      const cd=state.result.diagnostic,bd=best.result.diagnostic;
      if(cd&&bd){
        if(betterDiagnosticCandidate(cd,bd)) return true;
        if(betterDiagnosticCandidate(bd,cd)) return false;
      }
      return !!cd&&!bd;
    };
    // Surplus fast path: every reachable raw-material category is already fully funded.
    // Extra Stamina cannot alter candidate feasibility or the marginal scarcity weights.
    const maxGearOre=Math.max(0,Number(ctx.gearOptions?.[ctx.gearOptions.length-1]?.oreCost)||0);
    const fullyRawFunded=
      (Number(baseResources.ore)||0)>=maxGearOre-0.5 &&
      (Number(baseResources.essence)||0)>=Math.max(0,Number(ctx.headroomCosts?.essence)||0)-0.5 &&
      (Number(baseResources.sand)||0)>=Math.max(0,Number(ctx.headroomCosts?.sand)||0)-0.5;
    if(fullyRawFunded){
      const allocation=(Number(map.ore)||0)>0?{...empty,ore:total}:{...empty,unassigned:total};
      const state=await resultState(allocation);
      return {plan:state.result.plan,diagnostic:state.result.plan||state.result.diagnostic,resources:state.resources,allocation:state.allocation};
    }
    // Evaluate the complete legal Auto-Stamina state space directly: at most three searches.
    let bestState=null;
    for(const key of ['ore','essence','sand']){
      if((Number(map[key])||0)<=0) continue;
      const state=await resultState({...empty,[key]:total});
      if(betterState(state,bestState)) bestState=state;
    }
    if(bestState){
      return {plan:bestState.result.plan,diagnostic:bestState.result.plan||bestState.result.diagnostic,resources:bestState.resources,allocation:bestState.allocation};
    }
    const allocation={...empty,unassigned:total};
    const state=await resultState(allocation);
    return {plan:state.result.plan,diagnostic:state.result.plan||state.result.diagnostic,resources:state.resources,allocation};
  }

function optimizer(baseScore,desired,p,resources,cfg=activeCalcConfig(),ctx=null){
    return searchPlans(baseScore,desired,p,resources,cfg,ctx).plan;
  }
return {solveTargetWithAutoStamina, materialRealmDaysAvailable, realmInventoryFor, realmTopupFor, buildGearOptions, planningCategoryState, createPlanningContext, plannedToolAcquisitionSupply, jointReacquisitionHours, acquisitionEffortFor, makePlanCandidate, searchPlans, searchPlansCooperative, solveTargetWithAutoStaminaCooperative, optimizer};
}
