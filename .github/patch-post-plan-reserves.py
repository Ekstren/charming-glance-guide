from pathlib import Path

PATH=Path('index.html')
text=PATH.read_text(encoding='utf-8')
MARKER='POST_PLAN_RAW_RESERVE_V2'
if MARKER in text:
    print('Post-plan raw reserve model already applied.')
    raise SystemExit(0)


def replace_block(start_marker,end_marker,new_block,label):
    global text
    start=text.find(start_marker)
    end=text.find(end_marker,start)
    if start<0 or end<0:
        raise SystemExit(f'{label} block not found')
    text=text[:start]+new_block+text[end:]

# 1) Reserves are no longer removed from the raw-material budget before optimization.
#    They are season-end requirements: S1 upgrades consume raw first, then leftover raw
#    fills the reserve, and tools cover only the remaining reserve gap.
new_reserves=r'''  /* POST_PLAN_RAW_RESERVE_V2
     S2 reserves are requirements AFTER the recommended S1 plan, not pre-locked raw piles.
     S1 upgrades consume projected raw material first. Whatever raw remains covers the S2
     reserve target; Realm tools are used only for the post-plan reserve gap. */
  function season2SkillEssenceReserve(cfg=activeCalcConfig()){
    if(cfg.key!=='s1' || !$('reserveS2Essence')?.checked || !$('holdExp')?.checked) return {target:0,rawEssence:0,knucklesReserved:0,knuckleEssence:0,projectedKnuckles:0,shortfall:0,hours:0,exp:0,targetLevel:100};
    const hours=clamp(n('reserveHours',36),0,36);
    const heldExp=Math.max(0,n('bedExp',0))*hours;
    let level=100,exp=heldExp,safety=0;
    while(safety++<200){
      const req=expRequiredForLevel(level,CALC_SEASONS.s2);
      if(exp<req) break;
      exp-=req; level++;
    }
    const target=Math.max(0,skillCost(100,level,CALC_SEASONS.s2));
    return {target,rawEssence:0,knucklesReserved:0,knuckleEssence:0,projectedKnuckles:Math.max(0,Math.floor(n('knucklesCurrent',0)))+plannedRealmRunsFor('essence',cfg),shortfall:0,hours,exp:heldExp,targetLevel:level};
  }

  function season2RelicSandReserve(cfg=activeCalcConfig()){
    if(cfg.key!=='s1' || !$('reserveS2Sand')?.checked) return {target:0,rawSand:0,shovelsReserved:0,shovelSand:0,projectedShovels:0,shortfall:0,fromLevel:10,toLevel:11};
    const s2=CALC_SEASONS.s2;
    const fromLevel=10;
    const perRelic=relicStepSand(fromLevel,s2);
    const target=Number.isFinite(perRelic)?perRelic*20:0;
    return {target,rawSand:0,shovelsReserved:0,shovelSand:0,projectedShovels:Math.max(0,Math.floor(n('shovelCurrent',0)))+plannedRealmRunsFor('sand',cfg),shortfall:0,perRelic,fromLevel,toLevel:fromLevel+1};
  }

  function season2FantomonTreatReserve(cfg=activeCalcConfig()){
    if(cfg.key!=='s1' || !$('reserveS2Treats')?.checked) return {target:0,rawTreats:0,shortfall:0,fromLevel:100,toLevel:110,expEquivalent:0};
    const fromLevel=100,toLevel=110;
    const target=Math.max(0,fantoCost(fromLevel,toLevel,CALC_SEASONS.s2));
    return {target,rawTreats:0,shortfall:0,fromLevel,toLevel,expEquivalent:target*TREAT_BASIC_EXP};
  }

  function applySeasonTransitionReserves(resources,cfg=activeCalcConfig()){
    const skillMeta=season2SkillEssenceReserve(cfg);
    const relicMeta=season2RelicSandReserve(cfg);
    const treatMeta=season2FantomonTreatReserve(cfg);
    const essenceTotal=Math.max(0,Number(resources.essence)||0);
    const sandTotal=Math.max(0,Number(resources.sand)||0);
    const treatTotal=Math.max(0,Number(resources.treat)||0);
    return {...resources,
      essenceTotal,essenceReserve:0,s2SkillReserve:skillMeta,essence:essenceTotal,
      sandTotal,sandReserve:0,s2RelicSandReserve:relicMeta,sand:sandTotal,
      treatTotal,treatReserve:0,s2FantomonTreatReserve:treatMeta,treat:treatTotal
    };
  }
'''
replace_block('  /* RAW_FIRST_TOOL_GAPS_V1','  function relicStepSand(level,cfg=activeCalcConfig()){',new_reserves,'reserve model')

# 2) All projected tools stay available. Candidate-specific reserve gaps decide how many
#    tools must actually be held/used.
old_inv=r'''  function realmInventoryFor(key,cfg=activeCalcConfig()){
    const ids={ore:'hammerCurrent',essence:'knucklesCurrent',sand:'shovelCurrent'};
    const id=ids[key];
    const manualBanked=id?Math.max(0,Math.floor(n(id,0))):0;
    const plannedRuns=plannedRealmRunsFor(key,cfg);
    let protectedRuns=0;
    if(cfg.key==='s1'&&key==='sand') protectedRuns=Math.max(0,Math.floor(season2RelicSandReserve(cfg).shovelsReserved||0));
    if(cfg.key==='s1'&&key==='essence') protectedRuns=Math.max(0,Math.floor(season2SkillEssenceReserve(cfg).knucklesReserved||0));
    return {banked:Math.max(0,manualBanked+plannedRuns-protectedRuns),manualBanked,plannedRuns,protectedRuns,baselineRefreshes:realmDailyValue(key)};
  }
'''
new_inv=r'''  function realmInventoryFor(key,cfg=activeCalcConfig()){
    const ids={ore:'hammerCurrent',essence:'knucklesCurrent',sand:'shovelCurrent'};
    const id=ids[key];
    const manualBanked=id?Math.max(0,Math.floor(n(id,0))):0;
    const plannedRuns=plannedRealmRunsFor(key,cfg);
    return {banked:Math.max(0,manualBanked+plannedRuns),manualBanked,plannedRuns,protectedRuns:0,baselineRefreshes:realmDailyValue(key)};
  }
'''
if text.count(old_inv)!=1:
    raise SystemExit(f'realmInventoryFor count={text.count(old_inv)}')
text=text.replace(old_inv,new_inv,1)

# 3) Reserve-aware tool plan. Raw always pays the S1 plan first. Only then do tools fill
#    the reserve gap. If raw cannot even fund the S1 plan, current-season tools cover that
#    plan shortfall first and the remaining tool requirement is calculated at S2 reserve yield.
anchor='  function formatRealmSchedule(topup,label){'
if text.count(anchor)!=1:
    raise SystemExit(f'formatRealmSchedule anchor count={text.count(anchor)}')
helper=r'''  function reserveTargetFor(key,resources,cfg=activeCalcConfig()){
    if(cfg.key!=='s1') return 0;
    if(key==='essence') return Math.max(0,Number(resources?.s2SkillReserve?.target)||0);
    if(key==='sand') return Math.max(0,Number(resources?.s2RelicSandReserve?.target)||0);
    if(key==='treat') return Math.max(0,Number(resources?.s2FantomonTreatReserve?.target)||0);
    return 0;
  }
  function reserveYieldFor(key,cfg=activeCalcConfig()){
    if(key==='essence') return Math.max(1,Number(CALC_SEASONS.s1.realm?.essence)||1000); // conservative startup floor
    if(key==='sand') return Math.max(1,Number(CALC_SEASONS.s2.realm?.sand)||1000);
    return 0;
  }
  function reserveAwareRealmTopupFor(key,planCost,rawBudget,resources,cfg=activeCalcConfig(),p=null){
    if(cfg.key!=='s1' || (key!=='essence'&&key!=='sand')) return realmTopupFor(key,planCost,rawBudget,resources,cfg,p);
    const raw=Math.max(0,Number(rawBudget)||0);
    const cost=Math.max(0,Number(planCost)||0);
    const reserveTarget=reserveTargetFor(key,resources,cfg);
    const planPerRun=Math.max(0,realmYieldFor(resources,key));
    const reservePerRun=Math.max(0,reserveYieldFor(key,cfg));
    const rawPlanShortfall=Math.max(0,cost-raw);
    const rawAfterPlan=Math.max(0,raw-cost);
    const reserveGap=Math.max(0,reserveTarget-rawAfterPlan);
    const planRuns=rawPlanShortfall>0&&planPerRun>0?Math.ceil(rawPlanShortfall/planPerRun):(rawPlanShortfall>0?Infinity:0);
    const reserveRuns=reserveGap>0&&reservePerRun>0?Math.ceil(reserveGap/reservePerRun):(reserveGap>0?Infinity:0);
    if(!Number.isFinite(planRuns)||!Number.isFinite(reserveRuns)){
      const inv=realmInventoryFor(key,cfg);
      return {feasible:false,unsupported:true,shortfall:rawPlanShortfall+reserveGap,runsNeeded:Infinity,runsUsed:0,bankedUsed:0,bankedRemaining:inv.banked,packs:Infinity,attempts:Infinity,purchasedRuns:0,sparePurchasedRuns:0,dawnium:Infinity,days:Number.isFinite(resources?.realmDays)?resources.realmDays:materialRealmDaysAvailable(cfg),dailyCounts:[],provided:0,maxPacks:0,maxAttempts:0,maxRuns:inv.banked,maxProvided:0,remainingAfterMax:rawPlanShortfall+reserveGap,baselinePerDay:inv.baselineRefreshes,planRuns:0,reserveRuns:0,planProvided:0,reserveProvided:0,reserveGap,rawAfterPlan,reserveTarget};
    }
    const totalRuns=planRuns+reserveRuns;
    const inv=realmInventoryFor(key,cfg);
    const days=Number.isFinite(resources?.realmDays)?resources.realmDays:materialRealmDaysAvailable(cfg);
    const top=realmTopup(totalRuns,0,1,days,inv.banked,inv.baselineRefreshes);
    const planProvided=planRuns*planPerRun;
    const reserveProvided=reserveRuns*reservePerRun;
    return {...top,
      shortfall:rawPlanShortfall+reserveGap,
      runsNeeded:totalRuns,runsUsed:totalRuns,
      provided:planProvided,
      planRuns,reserveRuns,planProvided,reserveProvided,
      planShortfall:rawPlanShortfall,reserveGap,rawAfterPlan,reserveTarget,
      reservePerRun,planPerRun,
      // realmTopup() operated in run units; expose a material-scale diagnostic as well.
      remainingRunsAfterMax:Math.max(0,Number(top.remainingAfterMax)||0)
    };
  }

'''
text=text.replace(anchor,helper+anchor,1)

# 4) Search feasibility includes the post-plan reserve instead of subtracting it before search.
old_zero="realm:{days:realmDays,ore:realmTopupFor('ore',0,resources.ore,resources,cfg,p),essence:realmTopupFor('essence',0,resources.essence,resources,cfg,p),sand:realmTopupFor('sand',0,resources.sand,resources,cfg,p)}};"
new_zero="realm:{days:realmDays,ore:realmTopupFor('ore',0,resources.ore,resources,cfg,p),essence:reserveAwareRealmTopupFor('essence',0,resources.essence,resources,cfg,p),sand:reserveAwareRealmTopupFor('sand',0,resources.sand,resources,cfg,p)}};"
if text.count(old_zero)!=1:
    raise SystemExit(f'zero realm block count={text.count(old_zero)}')
text=text.replace(old_zero,new_zero,1)

old_cache="    const essFor=so=>{const k=so.cost;if(!essCache.has(k))essCache.set(k,realmTopupFor('essence',k,resources.essence,resources,cfg,p));return essCache.get(k);};\n    const sandFor=ro=>{const k=ro.cost;if(!sandCache.has(k))sandCache.set(k,realmTopupFor('sand',k,resources.sand,resources,cfg,p));return sandCache.get(k);};"
new_cache="    const essFor=so=>{const k=so.cost;if(!essCache.has(k))essCache.set(k,reserveAwareRealmTopupFor('essence',k,resources.essence,resources,cfg,p));return essCache.get(k);};\n    const sandFor=ro=>{const k=ro.cost;if(!sandCache.has(k))sandCache.set(k,reserveAwareRealmTopupFor('sand',k,resources.sand,resources,cfg,p));return sandCache.get(k);};"
if text.count(old_cache)!=1:
    raise SystemExit(f'reserve cache block count={text.count(old_cache)}')
text=text.replace(old_cache,new_cache,1)

old_treat="        const treatShortfall=Math.max(0,fo.cost-resources.treat);"
new_treat="        const treatShortfall=Math.max(0,fo.cost+reserveTargetFor('treat',resources,cfg)-resources.treat);"
if text.count(old_treat)!=1:
    raise SystemExit(f'treatShortfall count={text.count(old_treat)}')
text=text.replace(old_treat,new_treat,1)

# 5) Separate reserve/result lines. The raw line is computed AFTER plan spending, and the
#    reserve line shows how much of the target is still covered by raw before any tool gap.
start='  /* CLEAR_RESERVE_BALANCE_LABELS_V1'
end='  function setBalance(id, cost, budget, yieldVal, itemName){'
new_balance=r'''  /* POST_PLAN_RESERVE_BALANCE_LINES_V2 */
  function setReserveAwareBalance(id,cost,rawBudget,reserveTarget,label){
    const el=$(id); if(!el) return;
    const raw=Math.max(0,Number(rawBudget)||0);
    const spend=Math.max(0,Number(cost)||0);
    const target=Math.max(0,Number(reserveTarget)||0);
    const rawAfterPlan=Math.max(0,raw-spend);
    const reserveFromRaw=Math.min(target,rawAfterPlan);
    const reserveGap=Math.max(0,target-reserveFromRaw);
    const spendable=Math.max(0,rawAfterPlan-reserveFromRaw);
    const lines=[`<span class="reserveBalanceLine reserveSpendable">${fmt(spendable)} spendable after plan</span>`];
    if(target>0){
      const reserveText=reserveGap>0
        ? `S2 reserve · ${fmt(reserveFromRaw)} / ${fmt(target)} ${label} from raw`
        : `S2 reserve · ${fmt(target)} ${label} covered by raw`;
      lines.push(`<span class="reserveBalanceLine ${reserveGap>0?'reserveGapLine':'reserveCoveredLine'}">${reserveText}</span>`);
    }
    el.innerHTML=lines.join('');
    el.classList.toggle('shortfallCount',false);
  }
  function setEssenceBalance(id,cost,resources){
    const planGenerated=Math.max(0,Number(resources?.planRealmProvided)||0);
    setReserveAwareBalance(id,cost,Math.max(0,Number(resources.essence)||0)+planGenerated,resources.s2SkillReserve?.target,'Essence');
  }
  function setSandBalance(id,cost,resources){
    const planGenerated=Math.max(0,Number(resources?.planRealmProvided)||0);
    setReserveAwareBalance(id,cost,Math.max(0,Number(resources.sand)||0)+planGenerated,resources.s2RelicSandReserve?.target,'Sand');
  }
  function setTreatBalance(id,cost,resources){
    setReserveAwareBalance(id,cost,resources.treat,resources.s2FantomonTreatReserve?.target,'basic-eq.');
  }

'''
replace_block(start,end,new_balance,'reserve balance helpers')

# 6) Tool rows are exception-only and distinguish plan tools from reserve-gap tools.
new_tool=r'''  function setToolBalance(id,top,hardShort,yieldVal,label,protectedRuns=0){
    const el=$(id); if(!el) return;
    el.classList.remove('toolNeed','toolLeft');
    const materialName=label==='Hammers'?'Ore':label==='Knuckles'?'Essence':label==='Shovels'?'Sand':'materials';
    const planRuns=Math.max(0,Math.floor(Number(top?.planRuns ?? top?.runsUsed)||0));
    const reserveRuns=Math.max(0,Math.floor(Number(top?.reserveRuns)||0));
    const planPer=Math.max(0,Number(top?.planPerRun ?? yieldVal)||0);
    const reservePer=Math.max(0,Number(top?.reservePerRun)||0);
    const lines=[];
    if(planRuns>0) lines.push(`<span class="toolUsageRow toolUsedLine"><i>Use ${label}</i><b>${fmt(planRuns)}</b><em>${planPer>0?`covers ≈${fmtCompact(planRuns*planPer)} ${materialName}`:''}</em></span>`);
    if(reserveRuns>0) lines.push(`<span class="toolUsageRow toolReserveLine"><i>S2 reserve gap</i><b>${fmt(reserveRuns)} ${label}</b><em>${reservePer>0?`covers ≈${fmtCompact(reserveRuns*reservePer)} ${materialName}`:''}</em></span>`);
    const required=Math.max(0,planRuns+reserveRuns);
    const maxRuns=Math.max(0,Math.floor(Number(top?.maxRuns)||0));
    const missing=Math.max(0,required-maxRuns);
    if(missing>0) lines.push(`<span class="toolUsageRow toolNeedLine"><i>Need more ${label}</i><b>${fmt(missing)}</b><em></em></span>`);
    if(!lines.length){el.innerHTML='';el.hidden=true;return;}
    el.hidden=false;
    el.innerHTML=lines.join('');
    el.classList.add(missing?'toolNeed':'toolLeft');
  }
'''
replace_block('  function setToolBalance(id,top,hardShort,yieldVal,label,protectedRuns=0){','  function setRealmShortfallBreakdown(',new_tool,'tool balance')

# 7) Result rendering uses full raw totals and only S1-plan Realm production before calculating
#    the post-plan reserve line.
old_render="      const oreBudgetWithRealm=resources.ore+(plan.realm?.ore?.provided||0),essenceBudgetWithRealm=resources.essence+(plan.realm?.essence?.provided||0),sandBudgetWithRealm=resources.sand+(plan.realm?.sand?.provided||0);\n      setBalance('oreBalance',plan.oreCost,oreBudgetWithRealm,resources.yields.orePerHammer,'Hammers');setEssenceBalance('essenceBalance',plan.essenceCost,{...resources,essence:essenceBudgetWithRealm});setSandBalance('sandBalance',plan.sandCost,{...resources,sand:sandBudgetWithRealm});setTreatBalance('treatBalance',plan.treatCost,resources);"
new_render="      const oreBudgetWithRealm=resources.ore+(plan.realm?.ore?.provided||0);\n      setBalance('oreBalance',plan.oreCost,oreBudgetWithRealm,resources.yields.orePerHammer,'Hammers');\n      setEssenceBalance('essenceBalance',plan.essenceCost,{...resources,planRealmProvided:plan.realm?.essence?.planProvided||0});\n      setSandBalance('sandBalance',plan.sandCost,{...resources,planRealmProvided:plan.realm?.sand?.planProvided||0});\n      setTreatBalance('treatBalance',plan.treatCost,resources);"
if text.count(old_render)!=1:
    raise SystemExit(f'result render block count={text.count(old_render)}')
text=text.replace(old_render,new_render,1)

# 8) The explanatory hints now describe the actual priority order.
text=text.replace("Knuckles are reserved first, so raw Essence stays spendable in S1 whenever your carried tools already cover the startup level.","Raw Essence is used by the S1 plan first; leftover raw covers this reserve, and Knuckles are needed only for any remaining reserve gap.")
text=text.replace("Surplus Sand above this reserve is spendable in S1.","Raw Sand is used by the S1 plan first; leftover raw covers this reserve, and Shovels are needed only for any remaining reserve gap.")
text=text.replace("Surplus Treats above this reserve are spendable in S1.","Treats are used by the S1 plan first; whatever remains must still cover this S2 reserve target.")

# 9) Separate-line styling for reserve status and reserve-gap tools.
style='''\n<style id="post-plan-reserve-lines-v2">\n.planCosts small .reserveBalanceLine{display:block!important;line-height:1.35}\n.planCosts small .reserveBalanceLine+.reserveBalanceLine{margin-top:4px}\n.planCosts small .reserveSpendable{color:var(--status-positive)!important;font-weight:800}\n.planCosts small .reserveCoveredLine{color:var(--status-info)!important;font-weight:750}\n.planCosts small .reserveGapLine{color:var(--status-warning)!important;font-weight:800}\n.planCosts small.toolBalance .toolReserveLine{display:block;color:var(--status-info)!important;font-weight:800}\n</style>\n'''
if '</head>' not in text:
    raise SystemExit('head close not found')
text=text.replace('</head>',style+'</head>',1)

# Update stale optimizer comment now that reserves are evaluated post-plan rather than removed first.
text=text.replace('     Enabled S2 hard reserves are removed before this S1 tie-breaker runs. Reacquisition is',
                  '     Enabled S2 hard reserves are enforced after each S1 candidate plan. Reacquisition is')

PATH.write_text(text,encoding='utf-8')
print('Applied post-plan raw reserve model and separate reserve lines.')
