from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
runtime_path = ROOT / 'assets' / 'runtime.js'
index_path = ROOT / 'index.html'
runtime = runtime_path.read_text(encoding='utf-8')
index = index_path.read_text(encoding='utf-8')

start = runtime.find('  /* FINISH_EARLY_MAX_V2')
end = runtime.find('  /* SMART_BALANCE_RAW_CEILING_V1', start)
if start < 0 or end < 0:
    raise SystemExit('Finish Early Max block anchors not found')

new_block = r'''  /* FINISH_EARLY_MAX_FAST_NOEXTRA_V3
     Max answers: how early can the selected target be secured WITHOUT any additional
     Realm purchases beyond the user's already-configured daily Realm plan. Configured
     Shop Buyouts/day and configured daily Realm purchases remain part of the user's normal
     projection; candidate-invented extra Realm refreshes are not allowed.

     This uses the same exact owned/projected-pool feasibility proof already used inside
     searchPlans(), but skips the expensive nested optimizer scan. Each half-day probe only
     builds the reachable option lists and checks the independently affordable maxima for
     Gear / Skills / Relics / Fantomons across the calculator's legal Stamina strategies.
     After binary search finds the final half-day value, the full optimizer runs ONCE to
     render the normal result card. */
  function finishEarlyNoExtraPossible(){
    const cfg=activeCalcConfig();
    if(snapshotSeason!==cfg.key) return false;
    if(cfg.key==='s2'){
      const required=s2RequiredPlannerInputs();
      if(!required.hasBed||!required.hasAllCart) return false;
    }

    const p=projectCharacterTo(upgradeFinishCutoffMs(cfg),cfg);
    if(cfg.key==='s2' && p.level<=cfg.scoreFloor) return false;
    p.upgradeCapLevel=p.level;
    p.upgradeCapPct=p.pct;

    const currentCharacter=p.current||characterSnapshot(cfg);
    const currentCaps=categoryInputCapsForCharacter(currentCharacter.level,cfg);
    const gearState=gearStateFromUser(cfg,currentCaps.gear,cfg.key==='s2'?130:143);
    const skillState=categoryStateFromUser('skillLevel','exactSkillLevels',8,100,currentCaps.skill,cfg.scoreFloor,cfg.weights.skill,cfg.key==='s2'?130:122);
    const relicState=categoryStateFromUser('relicLevel','exactRelicLevels',20,10,currentCaps.relic,cfg.relicFloor,cfg.weights.relic,cfg.key==='s2'?13:13);
    const fantoState=categoryStateFromUser('fantomonLevel','exactFantoLevels',4,100,currentCaps.fanto,cfg.scoreFloor,cfg.weights.fanto,cfg.key==='s2'?130:130);
    const baselineScore=characterScore(p,cfg)+gearScore(gearState.levels,cfg)+skillState.score+relicState.score+fantoState.score;
    const historical=Math.max(0,Math.floor(n('historicalStars',0)));
    const targetStars=Math.max(cfg.starBase+historical,Math.floor(n('targetStars',cfg.key==='s2'?680:200)));
    const desired=Math.max(0,(targetStars-historical-cfg.starBase)*cfg.scorePerStar);
    if(baselineScore>=desired-1e-9) return true;

    const ctx=createPlanningContext(baselineScore,desired,p,cfg);
    const baseResources=projectedResources(p.hours,cfg);
    const total=Math.max(0,Math.floor(baseResources.staminaNodes||0));
    const map=baseResources.yields?.map||{};
    const empty={ore:0,essence:0,sand:0,rolla:0,unassigned:0};
    const allocations=[];
    if(!baseResources.yields?.mapReady||total<=0){
      allocations.push({...empty,unassigned:total});
    }else if(staminaMode()==='auto'){
      for(const key of ['ore','essence','sand']){
        if((Number(map[key])||0)>0) allocations.push({...empty,[key]:total});
      }
    }else{
      const key=staminaMode();
      allocations.push((Number(map[key])||0)>0?{...empty,[key]:total}:{...empty,unassigned:total});
    }
    if(!allocations.length) allocations.push({...empty,unassigned:total});

    const highestAffordable=(options,budget,costKey='cost',secondaryBudget=Infinity,secondaryKey='')=>{
      let best=Array.isArray(options)&&options.length?options[0]:null;
      for(const option of (options||[])){
        const primary=Math.max(0,Number(option?.[costKey])||0);
        const secondary=secondaryKey?Math.max(0,Number(option?.[secondaryKey])||0):0;
        if(primary<=budget+0.5 && secondary<=secondaryBudget+0.5) best=option;
        else if(primary>budget+0.5) break;
      }
      return best;
    };

    for(const allocation of allocations){
      const resources=applyStaminaAllocation(baseResources,allocation,cfg);
      const refinedBudget=resources.refinedTracked?Math.max(0,Number(resources.refined)||0):Infinity;
      const go=highestAffordable(ctx.gearOptions,plannedToolAcquisitionSupply('ore',resources,cfg),'oreCost',refinedBudget,'refinedCost');
      const so=highestAffordable(ctx.cats.skillOptions,plannedToolAcquisitionSupply('essence',resources,cfg));
      const ro=highestAffordable(ctx.cats.relicOptions,plannedToolAcquisitionSupply('sand',resources,cfg));
      const fo=highestAffordable(ctx.cats.fantoOptions,Math.max(0,Number(resources.treat)||0));
      if(!go||!so||!ro||!fo) continue;
      const maxScore=ctx.charScore+(Number(go.score)||0)+(Number(so.score)||0)+(Number(ro.score)||0)+(Number(fo.score)||0);
      if(maxScore>=desired-1e-9) return true;
    }
    return false;
  }

  function findMaxFinishEarly(){
    const btn=$('finishEarlyMax'),input=$('finishEarlyDays');
    if(!btn||!input||btn.disabled) return;
    const cfg=activeCalcConfig();
    const original=String(input.value||'0');
    const halfDayMs=12*60*60*1000;
    const maxHalfSteps=Math.max(0,Math.floor((cfg.end.getTime()-Date.now())/halfDayMs));
    btn.disabled=true;
    btn.textContent='…';
    btn.setAttribute('aria-busy','true');
    clearTimeout(calculatorUpdateTimer);
    calculatorUpdateTimer=null;
    setTimeout(()=>{
      try{
        input.value='0';
        if(!finishEarlyNoExtraPossible()){
          input.value=original;
          updateCalculator();
          btn.title='The selected target is not reachable without extra Realm purchases beyond your configured routine.';
          return;
        }
        let lo=0,hi=maxHalfSteps;
        while(lo<hi){
          const mid=Math.ceil((lo+hi)/2);
          input.value=String(mid/2);
          if(finishEarlyNoExtraPossible()) lo=mid;
          else hi=mid-1;
        }
        input.value=String(lo/2);
        resetMaxAchievableUi();
        saveState();
        // One full solve only, after the fast feasibility search has found the cutoff.
        updateCalculator();
        btn.title=lo>0
          ? `Maximum no-extra-purchase finish-early value: ${lo/2} days. Uses your configured Realm/Shop routine but no additional recommended Realm purchases.`
          : 'The current target needs the full remaining season without extra Realm purchases.';
      }catch(err){
        console.error('FINISH_EARLY_MAX_FAST_NOEXTRA_V3',err);
        input.value=original;
        updateCalculator();
        btn.title='Could not calculate the no-extra-purchase maximum from the current inputs.';
      }finally{
        btn.disabled=false;
        btn.textContent='Max';
        btn.removeAttribute('aria-busy');
      }
    },0);
  }

'''
runtime = runtime[:start] + new_block + runtime[end:]

old_title = 'Find the largest half-day Finish Early value that still reaches the selected Primostar target'
new_title = 'Find the earliest finish in half-day steps using your configured Realm/Shop routine, without additional recommended Realm purchases'
if old_title in index:
    index = index.replace(old_title, new_title, 1)
elif 'id="finishEarlyMax"' not in index:
    raise SystemExit('finishEarlyMax button not found')

runtime_path.write_text(runtime, encoding='utf-8')
index_path.write_text(index, encoding='utf-8')
