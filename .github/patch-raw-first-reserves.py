from pathlib import Path

PATH=Path('index.html')
text=PATH.read_text(encoding='utf-8')
MARKER='RAW_FIRST_TOOL_GAPS_V1'
if MARKER in text:
    print('Raw-first reserve/tool-gap UI already applied.')
    raise SystemExit(0)


def replace_block(start_marker,end_marker,new_block,label):
    global text
    start=text.find(start_marker)
    end=text.find(end_marker,start)
    if start<0 or end<0:
        raise SystemExit(f'{label} block not found')
    text=text[:start]+new_block+text[end:]

# Reserve priority: projected raw material first. Only reserve carried Realm tools for any
# remaining gap. This keeps flexible tools available to the S1 optimizer whenever raw supply
# already satisfies the S2 floor.
new_reserves=r'''  /* RAW_FIRST_TOOL_GAPS_V1
     S2 reserves consume projected raw material first. Realm tools are protected only for
     the reserve gap that raw material cannot cover. Result cards show tool rows only when
     tools are actually needed for the S1 plan or an S2 reserve gap. */
  function projectedRawReserveSupply(key,cfg=activeCalcConfig()){
    if(cfg.key!=='s1') return 0;
    const hours=projectionResourceHoursAt(Date.now(),cfg);
    if(key==='essence') return Math.max(0,n('essenceCurrent'))+Math.max(0,n('essenceRate'))*hours;
    if(key==='sand') return savedSandEquivalent()+Math.max(0,n('sandRate'))*hours;
    if(key==='treat') return savedTreatEquivalent()+Math.max(0,n('treatRate'))*hours;
    return 0;
  }

  // Protect enough carried Essence to catch all 8 skills up to the Character level that the
  // held Bed EXP can immediately reach after the S2 reset. Raw Essence covers the reserve first;
  // Knuckles are protected only for any remaining gap.
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
    const rawEssence=Math.min(target,projectedRawReserveSupply('essence',cfg));
    const rawGap=Math.max(0,target-rawEssence);
    const projectedKnuckles=Math.max(0,Math.floor(n('knucklesCurrent',0)))+plannedRealmRunsFor('essence',cfg);
    // Conservative S2 startup floor until the early-S2 Realm bracket is directly verified.
    const conservativePerKnuckle=Math.max(1,Number(CALC_SEASONS.s1.realm?.essence)||1000);
    const knucklesReserved=Math.min(projectedKnuckles,Math.ceil(rawGap/conservativePerKnuckle));
    const knuckleEssence=Math.min(rawGap,knucklesReserved*conservativePerKnuckle);
    const shortfall=Math.max(0,rawGap-knuckleEssence);
    return {target,rawEssence,knucklesReserved,knuckleEssence,projectedKnuckles,conservativePerKnuckle,shortfall,hours,exp:heldExp,targetLevel:level};
  }

  // Preserve one full first S2 Relic round (+10 -> +11 across all 20 slots). Projected raw
  // Sand covers it first; Shovels are protected only for the remaining gap.
  function season2RelicSandReserve(cfg=activeCalcConfig()){
    if(cfg.key!=='s1' || !$('reserveS2Sand')?.checked) return {target:0,rawSand:0,shovelsReserved:0,shovelSand:0,projectedShovels:0,shortfall:0,fromLevel:10,toLevel:11};
    const s2=CALC_SEASONS.s2;
    const fromLevel=10;
    const perRelic=relicStepSand(fromLevel,s2);
    const target=Number.isFinite(perRelic)?perRelic*20:0;
    const rawSand=Math.min(target,projectedRawReserveSupply('sand',cfg));
    const rawGap=Math.max(0,target-rawSand);
    const projectedShovels=Math.max(0,Math.floor(n('shovelCurrent',0)))+plannedRealmRunsFor('sand',cfg);
    const perShovel=Math.max(0,Number(s2.realm?.sand)||0);
    const shovelsReserved=perShovel>0?Math.min(projectedShovels,Math.ceil(rawGap/perShovel)):0;
    const shovelSand=Math.min(rawGap,shovelsReserved*perShovel);
    const shortfall=Math.max(0,rawGap-shovelSand);
    return {target,rawSand,shovelsReserved,shovelSand,projectedShovels,shortfall,perRelic,fromLevel,toLevel:fromLevel+1};
  }

  // Treats have no Realm-tool analogue. Protect only the actual Basic-equivalent Treat amount
  // needed for the S2 startup target; any excess remains spendable in S1.
  function season2FantomonTreatReserve(cfg=activeCalcConfig()){
    if(cfg.key!=='s1' || !$('reserveS2Treats')?.checked) return {target:0,rawTreats:0,shortfall:0,fromLevel:100,toLevel:110,expEquivalent:0};
    const fromLevel=100,toLevel=110;
    const target=Math.max(0,fantoCost(fromLevel,toLevel,CALC_SEASONS.s2));
    const rawTreats=Math.min(target,projectedRawReserveSupply('treat',cfg));
    const shortfall=Math.max(0,target-rawTreats);
    return {target,rawTreats,shortfall,fromLevel,toLevel,expEquivalent:target*TREAT_BASIC_EXP};
  }

  function applySeasonTransitionReserves(resources,cfg=activeCalcConfig()){
    const skillMeta=season2SkillEssenceReserve(cfg);
    const relicMeta=season2RelicSandReserve(cfg);
    const treatMeta=season2FantomonTreatReserve(cfg);
    const essenceTotal=Math.max(0,Number(resources.essence)||0);
    const sandTotal=Math.max(0,Number(resources.sand)||0);
    const treatTotal=Math.max(0,Number(resources.treat)||0);

    const essenceProtected=Math.min(essenceTotal,Math.max(0,skillMeta.target||0));
    const essenceGap=Math.max(0,(skillMeta.target||0)-essenceProtected);
    const projectedKnuckles=Math.max(0,Math.floor(n('knucklesCurrent',0)))+plannedRealmRunsFor('essence',cfg);
    const conservativePerKnuckle=Math.max(1,Number(CALC_SEASONS.s1.realm?.essence)||1000);
    const knucklesReserved=Math.min(projectedKnuckles,Math.ceil(essenceGap/conservativePerKnuckle));
    const knuckleEssence=Math.min(essenceGap,knucklesReserved*conservativePerKnuckle);
    const essenceReserveShortfall=Math.max(0,essenceGap-knuckleEssence);
    const finalSkillReserve={...skillMeta,rawEssence:essenceProtected,knucklesReserved,knuckleEssence,projectedKnuckles,conservativePerKnuckle,shortfall:essenceReserveShortfall,protectedEquivalent:essenceProtected+knuckleEssence};

    const sandProtected=Math.min(sandTotal,Math.max(0,relicMeta.target||0));
    const sandGap=Math.max(0,(relicMeta.target||0)-sandProtected);
    const projectedShovels=Math.max(0,Math.floor(n('shovelCurrent',0)))+plannedRealmRunsFor('sand',cfg);
    const perShovel=Math.max(0,Number(CALC_SEASONS.s2.realm?.sand)||0);
    const shovelsReserved=perShovel>0?Math.min(projectedShovels,Math.ceil(sandGap/perShovel)):0;
    const shovelSand=Math.min(sandGap,shovelsReserved*perShovel);
    const sandReserveShortfall=Math.max(0,sandGap-shovelSand);
    const finalRelicReserve={...relicMeta,rawSand:sandProtected,shovelsReserved,shovelSand,projectedShovels,shortfall:sandReserveShortfall,protectedEquivalent:sandProtected+shovelSand};

    const treatProtected=Math.min(treatTotal,Math.max(0,treatMeta.target||0));
    const treatReserveShortfall=Math.max(0,(treatMeta.target||0)-treatProtected);
    const finalTreatReserve={...treatMeta,rawTreats:treatProtected,shortfall:treatReserveShortfall,protectedEquivalent:treatProtected};

    return {...resources,
      essenceTotal,essenceReserve:essenceProtected,s2SkillReserve:finalSkillReserve,essence:Math.max(0,essenceTotal-essenceProtected),
      sandTotal,sandReserve:sandProtected,s2RelicSandReserve:finalRelicReserve,sand:Math.max(0,sandTotal-sandProtected),
      treatTotal,treatReserve:treatProtected,s2FantomonTreatReserve:finalTreatReserve,treat:Math.max(0,treatTotal-treatProtected)
    };
  }
'''
replace_block('  // Protect enough carried Essence to catch all 8 skills up to the Character level that the\n','  function relicStepSand(level,cfg=activeCalcConfig()){',new_reserves,'reserve')

# Tool rows are exception-only: no inventory/remaining clutter. Show only actual tools consumed
# for the S1 plan, tools protected for a reserve gap, and any additional tools still required.
new_tool=r'''  function setToolBalance(id,top,hardShort,yieldVal,label,protectedRuns=0){
    const el=$(id); if(!el) return;
    el.classList.remove('toolNeed','toolLeft');
    const per=Math.max(0,Number(yieldVal)||0);
    const hard=Math.max(0,Number(hardShort)||0);
    const key=label==='Hammers'?'ore':label==='Knuckles'?'essence':label==='Shovels'?'sand':null;
    const inv=key?realmInventoryFor(key,activeCalcConfig()):null;
    const protectedCount=Math.max(0,Math.floor(Number(inv?.protectedRuns??protectedRuns)||0));
    const materialName=label==='Hammers'?'Ore':label==='Knuckles'?'Essence':label==='Shovels'?'Sand':'materials';
    const finiteRuns=Number(top?.runsUsed);
    const maxRuns=Math.max(0,Math.floor(Number(top?.maxRuns)||0));
    const hardNeedRuns=hard>0.5&&per>0?Math.ceil(hard/per):0;
    const desiredRuns=Math.max(0,Math.floor(Number.isFinite(finiteRuns)?finiteRuns:(hard>0.5?maxRuns+hardNeedRuns:0)));
    const projectedSpendable=Math.max(0,Math.floor(Number(inv?.banked)||0));
    const used=Math.min(desiredRuns,projectedSpendable);
    const usedMaterial=used*per;
    const needed=Math.max(0,desiredRuns-used);
    const neededMaterial=needed*per;
    const reserveMaterial=protectedCount*per;

    const lines=[];
    if(used>0) lines.push(`<span class="toolUsageRow toolUsedLine"><i>Use ${label}</i><b>${fmt(used)}</b><em>${per>0?`covers ≈${fmtCompact(usedMaterial)} ${materialName}`:''}</em></span>`);
    if(protectedCount>0) lines.push(`<span class="toolUsageRow toolReserveLine"><i>S2 reserve gap</i><b>${fmt(protectedCount)} ${label}</b><em>${per>0?`covers ≈${fmtCompact(reserveMaterial)} ${materialName}`:''}</em></span>`);
    if(needed>0) lines.push(`<span class="toolUsageRow toolNeedLine"><i>Need more ${label}</i><b>${fmt(needed)}</b><em>${per>0?`≈${fmtCompact(neededMaterial)} ${materialName}`:''}</em></span>`);

    if(!lines.length){
      el.innerHTML='';
      el.hidden=true;
      return;
    }
    el.hidden=false;
    el.innerHTML=lines.join('');
    el.classList.add(needed?'toolNeed':'toolLeft');
  }
'''
replace_block('  function setToolBalance(id,top,hardShort,yieldVal,label,protectedRuns=0){','  function setRealmShortfallBreakdown(',new_tool,'tool balance')

# Update comments that described tools as reserve-first.
text=text.replace('Spendable Realm tools count as material-equivalent supply; protected\n    // S2 tools do not, because realmInventoryFor() has already removed protected runs.',
                  'Spendable Realm tools count as material-equivalent supply; only tools needed\n    // for a raw-material reserve gap are excluded by realmInventoryFor().')

PATH.write_text(text,encoding='utf-8')
print('Applied raw-first reserves and exception-only tool rows.')
