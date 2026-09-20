
import { localDeadlineLabel, nextResetLocalLabel } from '../display-time.mjs';
import { CALC_SEASONS, S2_PLANNER_START_LEVEL, ASTRAL_PACT_NODES, ASTRAL_LABELS, ASTRAL_ORDER, GEAR_OUTPUT_IDS, fmt, fmtCompact, activeCalcConfig, remainingHoursAt, formatRemaining, characterScore, categoryInputCapsForCharacter, automaticResourceYields, targetMomentLabel, compactDurationMs, REALM_RUNS_PER_REFRESH } from './model.mjs';
export function createCalculatorRenderer(__calculatorDeps){
function renderRealmToolProjection(cfg=activeCalcConfig()){
    const days=Math.max(0,Math.floor(__calculatorDeps.futureRealmPurchaseDays(cfg)||0));
    const daily={ore:__calculatorDeps.realmDailyValue('ore'),essence:__calculatorDeps.realmDailyValue('essence'),sand:__calculatorDeps.realmDailyValue('sand')};
    const added={ore:days*daily.ore*REALM_RUNS_PER_REFRESH,essence:days*daily.essence*REALM_RUNS_PER_REFRESH,sand:days*daily.sand*REALM_RUNS_PER_REFRESH};
    const totals={
      hammer:Math.max(0,Math.floor(__calculatorDeps.n('hammerCurrent',0)))+added.ore,
      knuckles:Math.max(0,Math.floor(__calculatorDeps.n('knucklesCurrent',0)))+added.essence,
      shovel:Math.max(0,Math.floor(__calculatorDeps.n('shovelCurrent',0)))+added.sand
    };
    const onHand={
      hammer:Math.max(0,Math.floor(__calculatorDeps.n('hammerCurrent',0))),
      knuckles:Math.max(0,Math.floor(__calculatorDeps.n('knucklesCurrent',0))),
      shovel:Math.max(0,Math.floor(__calculatorDeps.n('shovelCurrent',0)))
    };
    const realmYield=cfg.realm||{};
    const currentLevel=Math.max(1,Math.floor(__calculatorDeps.n('charLevel',cfg.key==='s2'?100:122)));
    const worthLabel=currentLevel<cfg.realmMaxLevel?`Worth at Lv.${cfg.realmMaxLevel} max`:'Worth now';
    if(__calculatorDeps.$('hammerMaterialValue')) __calculatorDeps.$('hammerMaterialValue').textContent=`${worthLabel}: ~${fmtCompact(onHand.hammer*(Number(realmYield.ore)||0))} Raw Ore`;
    if(__calculatorDeps.$('knucklesMaterialValue')) __calculatorDeps.$('knucklesMaterialValue').textContent=`${worthLabel}: ~${fmtCompact(onHand.knuckles*(Number(realmYield.essence)||0))} Skill Essence`;
    if(__calculatorDeps.$('shovelMaterialValue')) __calculatorDeps.$('shovelMaterialValue').textContent=`${worthLabel}: ~${fmtCompact(onHand.shovel*(Number(realmYield.sand)||0))} Chrono Sand`;
    if(__calculatorDeps.$('hammerProjected')) __calculatorDeps.$('hammerProjected').textContent=`Season-end estimate: ${fmt(totals.hammer)}`;
    if(__calculatorDeps.$('knucklesProjected')) __calculatorDeps.$('knucklesProjected').textContent=`Season-end estimate: ${fmt(totals.knuckles)}`;
    if(__calculatorDeps.$('shovelProjected')) __calculatorDeps.$('shovelProjected').textContent=`Season-end estimate: ${fmt(totals.shovel)}`;
  }

function renderRealmDailyRecommendations(plan,resources,cfg=activeCalcConfig()){
    const defs=[
      {key:'ore',out:'realmDailyOreRec'},
      {key:'essence',out:'realmDailyEssenceRec'},
      {key:'sand',out:'realmDailySandRec'}
    ];
    const suggested=__calculatorDeps.suggestedRealmDailyPlan(plan,cfg);
    for(const d of defs){
      const el=__calculatorDeps.$(d.out); if(!el) continue;
      el.classList.remove('realmRecommendUp','realmRecommendMax');
      if(!plan){ el.textContent='Recommended: —'; continue; }
      const selected=__calculatorDeps.realmDailyValue(d.key);
      const top=plan.realm?.[d.key];
      if(top?.feasible===false && Number(top.remainingAfterMax)>0){
        el.textContent=`20/day max · still ${fmt(Math.ceil(Number(top.remainingAfterMax)||0))} short`;
        el.classList.add('realmRecommendMax');
      }else if(suggested[d.key]>selected){
        el.textContent=`Suggested: up to ${suggested[d.key]}/day`;
        el.classList.add('realmRecommendUp');
      }else if(Number(top?.packs)>0){
        el.textContent='Extra Realm entries required';
        el.classList.add('realmRecommendUp');
      }else{
        el.textContent='Covers target';
      }
    }
  }

function renderLocalTimeLabels(){
    const reset=nextResetLocalLabel();
    if(__calculatorDeps.$('headerResetLocal')) __calculatorDeps.$('headerResetLocal').textContent=`Reset: ${reset}`;
    if(__calculatorDeps.$('timelineResetLocal')) __calculatorDeps.$('timelineResetLocal').textContent=reset;
  }

function renderTargetResourceSnapshot(reached,plan,pEnd,cfg=activeCalcConfig()){
    if(!Number.isFinite(Number(reached)) || !plan) return;
    const carry=__calculatorDeps.postTargetCarryAt(reached,plan,pEnd,cfg);
    const r=carry?.resourceSnapshot;
    if(!carry?.valid || !r) return;
    const added=r.staminaAdded||{ore:0,essence:0,sand:0,rolla:0};
    const allocation=r.staminaAllocation||{ore:0,essence:0,sand:0,rolla:0,unassigned:r.staminaNodes||0};
    renderStaminaCurrentPlan(allocation,added,r,'To target');
    const oreStam=added.ore?` · Stamina +${fmtCompact(added.ore)}`:'';
    const essStam=added.essence?` · Stamina +${fmtCompact(added.essence)}`:'';
    const sandStam=added.sand?` · Stamina +${fmtCompact(added.sand)}`:'';
    if(__calculatorDeps.$('oreProjected')) __calculatorDeps.$('oreProjected').textContent=`Projected to target: ${fmtCompact(Number(r.ore)||0)}${oreStam}`;
    if(__calculatorDeps.$('essenceProjected')) __calculatorDeps.$('essenceProjected').textContent=`Projected to target: ${fmtCompact(Number(r.essence)||0)}${essStam}`;
    if(__calculatorDeps.$('sandProjected')) __calculatorDeps.$('sandProjected').textContent=`Projected to target: ${fmtCompact(Number(r.sand)||0)}${sandStam}`;
    if(__calculatorDeps.$('treatProjected')) __calculatorDeps.$('treatProjected').textContent=`Projected to target: ${fmtCompact(Number(r.treat)||0)} basic-eq.`;
    // The upper cards are the inventory snapshot at the instant the requested score is reached.
    // Everything after that instant belongs only in the post-target season-end totals below.
    setRawRemaining('oreBalance',0,carry.ore);
    setRawRemaining('essenceBalance',0,carry.essence);
    setRawRemaining('sandBalance',0,carry.sand);
    setRawRemaining('treatBalance',0,carry.treat,'basic-eq.');
    const yields=r.yields||automaticResourceYields(__calculatorDeps.n('charLevel',cfg.key==='s2'?100:122),cfg);
    const oreYield=Math.max(0,Number(yields.orePerHammer)||0);
    const essenceYield=Math.max(0,Number(yields.essencePerKnuckles)||0);
    const sandYield=Math.max(0,Number(yields.sandPerShovel)||0);
    setToolBalance('oreToolBalance',carry.oreTop,0,oreYield,'Hammers',0,carry.ore);
    setToolBalance('essenceToolBalance',carry.essenceTop,0,essenceYield,'Knuckles',0,carry.essence);
    setToolBalance('sandToolBalance',carry.sandTop,0,sandYield,'Shovels',0,carry.sand);
    appendStaminaProjection('oreToolBalance',allocation.ore,added.ore,'Ore');
    appendStaminaProjection('essenceToolBalance',allocation.essence,added.essence,'Essence');
    appendStaminaProjection('sandToolBalance',allocation.sand,added.sand,'Sand');
  }

function renderPostTargetGains(reached,plan,pEnd,cfg=activeCalcConfig()){
    const host=__calculatorDeps.$('postTargetGains');
    if(!host) return;
    __calculatorDeps.ensurePostTargetControls();
    const end=cfg.end.getTime();
    if(!Number.isFinite(reached) || reached>=end){ __calculatorDeps.hidePostTargetGains(); return; }
    __calculatorDeps.postTargetLastReachMs=reached;
    __calculatorDeps.postTargetLastCfg=cfg;
    __calculatorDeps.postTargetLastPlan=plan;
    __calculatorDeps.postTargetLastPEnd=pEnd;
    host.hidden=false;
    const state=__calculatorDeps.selectedPostTargetToolState();
    if(__calculatorDeps.$('postTargetCustom')) __calculatorDeps.$('postTargetCustom').hidden=state.mode!=='custom';
    const carry=__calculatorDeps.postTargetCarryAt(reached,plan,pEnd,cfg);
    const gains=__calculatorDeps.postTargetRawGains(reached,cfg,state,carry.staminaUnused);
    const daily=state.mode==='stop'
      ? {ore:0,essence:0,sand:0}
      : state.mode==='custom'
        ? {ore:state.ore,essence:state.essence,sand:state.sand}
        : {ore:__calculatorDeps.realmDailyValue('ore'),essence:__calculatorDeps.realmDailyValue('essence'),sand:__calculatorDeps.realmDailyValue('sand')};
    const toolMultiplier=Math.max(0,Math.floor(Number(REALM_RUNS_PER_REFRESH)||5))*gains.resets;
    const tools={
      ore:carry.hammers+daily.ore*toolMultiplier,
      essence:carry.knuckles+daily.essence*toolMultiplier,
      sand:carry.shovels+daily.sand*toolMultiplier
    };
    const totals={
      ore:carry.ore+gains.ore,
      essence:carry.essence+gains.essence,
      sand:carry.sand+gains.sand,
      treat:carry.treat+gains.treat
    };
    if(__calculatorDeps.$('postTargetWindow')) __calculatorDeps.$('postTargetWindow').textContent=`${compactDurationMs(Math.max(0,end-reached))} of post-target gathering · season-end carry`;
    if(__calculatorDeps.$('postTargetOreGain')) __calculatorDeps.$('postTargetOreGain').textContent=fmt(Math.floor(totals.ore));
    if(__calculatorDeps.$('postTargetEssenceGain')) __calculatorDeps.$('postTargetEssenceGain').textContent=fmt(Math.floor(totals.essence));
    if(__calculatorDeps.$('postTargetSandGain')) __calculatorDeps.$('postTargetSandGain').textContent=fmt(Math.floor(totals.sand));
    if(__calculatorDeps.$('postTargetTreatGain')) __calculatorDeps.$('postTargetTreatGain').textContent=fmt(Math.floor(totals.treat));
    if(__calculatorDeps.$('postTargetHammerGain')) __calculatorDeps.$('postTargetHammerGain').textContent=`${fmt(tools.ore)} Hammers total`;
    if(__calculatorDeps.$('postTargetKnuckleGain')) __calculatorDeps.$('postTargetKnuckleGain').textContent=`${fmt(tools.essence)} Knuckles total`;
    if(__calculatorDeps.$('postTargetShovelGain')) __calculatorDeps.$('postTargetShovelGain').textContent=`${fmt(tools.sand)} Shovels total`;
  }

function renderTargetTiming(plan,resourceBlocked,requestedDesired,pEnd,cfg=activeCalcConfig()){
    const host=__calculatorDeps.$('targetTiming'),dateEl=__calculatorDeps.$('targetReachedDate'),leftEl=__calculatorDeps.$('targetSeasonLeft');
    const targetCharEl=__calculatorDeps.$('targetCharacterAtGoal'),seasonCharEl=__calculatorDeps.$('seasonEndCharacterResult');
    const excessStarsEl=__calculatorDeps.$('seasonEndExcessStars'),excessScoreEl=__calculatorDeps.$('seasonEndExcessScore'),excessNoteEl=__calculatorDeps.$('seasonEndExcessNote');
    if(!host||!dateEl||!leftEl) return;
    const reached=__calculatorDeps.estimateTargetReachMoment(plan,resourceBlocked,requestedDesired,pEnd,cfg);
    host.classList.toggle('isUnreachable',!Number.isFinite(reached));
    if(!Number.isFinite(reached)){
      dateEl.textContent='Not projected';
      leftEl.textContent='—';
      if(targetCharEl) targetCharEl.textContent='—';
      if(seasonCharEl) seasonCharEl.textContent='—';
      if(excessStarsEl){excessStarsEl.hidden=true;excessStarsEl.textContent='';}
      if(excessScoreEl){excessScoreEl.hidden=true;excessScoreEl.textContent='';}
      if(excessNoteEl){excessNoteEl.hidden=true;excessNoteEl.textContent='';}
      __calculatorDeps.hidePostTargetGains();
      return;
    }
    const now=Date.now();
    const targetP=__calculatorDeps.projectCharacterTo(reached,cfg);
    const seasonP=__calculatorDeps.projectCharacter(cfg);
    dateEl.textContent=reached<=now+60_000?'Now':targetMomentLabel(reached);
    leftEl.textContent=compactDurationMs(Math.max(0,cfg.end.getTime()-reached));
    if(targetCharEl) targetCharEl.textContent=`Lv.${targetP.level} · ${(targetP.pct*100).toFixed(1)}%`;
    if(seasonCharEl) seasonCharEl.textContent=`Lv.${seasonP.level} · ${(seasonP.pct*100).toFixed(1)}%`;
    /* SEASON_END_EXCESS_V1
       Keep the requested plan/build fixed. Parenthetical values show what Character EXP alone
       adds AFTER the displayed target-route score, through the normal season-end EXP projection.
       Primostar excess is recomputed from the actual floor conversion, not excessScore/scorePerStar. */
    const planScore=Math.max(0,Number(plan?.score)||0);
    const nonCharacterScore=Math.max(0,planScore-characterScore(pEnd,cfg));
    const seasonEndScore=Math.max(planScore,nonCharacterScore+characterScore(seasonP,cfg));
    const excessScore=Math.max(0,Math.floor(seasonEndScore-planScore+1e-9));
    const historical=Math.max(0,Math.floor(__calculatorDeps.n('historicalStars',0)));
    const planStars=historical+cfg.starBase+Math.floor(planScore/cfg.scorePerStar);
    const seasonEndStars=historical+cfg.starBase+Math.floor(seasonEndScore/cfg.scorePerStar);
    const excessStars=Math.max(0,seasonEndStars-planStars);
    const timeAfterTargetMs=Math.max(0,cfg.end.getTime()-reached);
    const timeAfterTarget=compactDurationMs(timeAfterTargetMs);
    if(excessStarsEl){
      excessStarsEl.textContent=`(+${fmt(excessStars)})`;
      excessStarsEl.hidden=excessStars<=0;
    }
    if(excessScoreEl){
      excessScoreEl.textContent=`(+${fmt(excessScore)})`;
      excessScoreEl.hidden=excessScore<=0;
    }
    if(excessNoteEl){
      const hasExcess=excessStars>0||excessScore>0;
      excessNoteEl.textContent=`( ) = projected extra gained after reaching the target ${timeAfterTarget} before season end`;
      excessNoteEl.hidden=!hasExcess||timeAfterTargetMs<=0;
    }
    renderPostTargetGains(reached,plan,pEnd,cfg);
  }

function renderStaminaCurrentPlan(allocation,added,resources,horizon='By planned finish'){
    const el=__calculatorDeps.$('staminaCurrentPlan');
    const result=__calculatorDeps.$('resultStamina');
    const write=html=>{
      if(el) el.innerHTML=html;
      if(result){
        __calculatorDeps.$('resultStaminaPlan').innerHTML=html;
        __calculatorDeps.$('resultStaminaHorizon').textContent=horizon;
        result.hidden=false;
      }
    };
    const a=allocation||{ore:0,essence:0,sand:0,rolla:0,unassigned:0};
    const gain=added||{ore:0,essence:0,sand:0,rolla:0};
    const labels={ore:'Ore',essence:'Essence',sand:'Sand',rolla:'Rolla'};
    const active=['ore','essence','sand','rolla'].filter(k=>(Number(a[k])||0)>0);
    const mode=__calculatorDeps.staminaMode();
    if(!resources?.yields?.mapReady){
      const bracket=activeCalcConfig().realmMaxLevel;
      write(`Current plan: waiting for the Lv.${bracket} map bracket`);
      return;
    }
    if(!active.length){
      const unassigned=Math.max(0,Math.floor(Number(a.unassigned)||0));
      write(unassigned?`Current plan: ${fmt(unassigned)} node${unassigned===1?'':'s'} unassigned`:'Current plan: no projected Stamina nodes');
      return;
    }
    const prefix=mode==='auto'?'Auto allocation:':'Current allocation:';
    const allocText=active.map(k=>`${labels[k]} ${fmt(Math.floor(Number(a[k])||0))}`).join(' · ');
    const gainText=active.map(k=>`+${fmtCompact(Number(gain[k])||0)} ${labels[k]}`).join(' · ');
    write(`${prefix} ${allocText}<span class="staminaGain"><br>Projected gain: ${gainText}</span>`);
  }

/* TOOL_ONLY_RESOURCE_GAPS_V4
     S2 reserve math stays internal. On a feasible plan, result cards show no leftover or
     reserve bookkeeping. If Realm tools are actually consumed, show only total tools used,
     their approximate material value, and the tools left afterward with approximate value. */
function hidePlanBalance(id){
    const el=__calculatorDeps.$(id); if(!el) return;
    el.textContent=''; el.innerHTML=''; el.hidden=true;
    el.classList.remove('shortfallCount','shortfallBreakdown','reserveHasGap');
  }

/* RAW_REMAINING_DISPLAY_V1: visible balance is only material-equivalent left
     after the S1 upgrade spend. Reserve bookkeeping stays internal.
     RAW_REMAINING_NO_RAW_LABEL_V2 */
function setRawRemaining(id,cost,available,unitLabel=''){
    const el=__calculatorDeps.$(id); if(!el) return;
    el.classList.remove('shortfallCount','shortfallBreakdown','reserveHasGap');
    el.classList.add('rawRemaining');
    const left=Math.max(0,Math.floor((Number(available)||0)-(Number(cost)||0)+1e-9));
    el.hidden=false;
    el.innerHTML=`<span class="resourceRemainingLine">Remaining: <b>${fmt(left)}${unitLabel?` ${unitLabel}`:''}</b></span>`;
  }

function setSandBalance(id,cost,resources){ setRawRemaining(id,cost,resources.sand); }

function setTreatBalance(id,cost,resources){ setRawRemaining(id,cost,resources.treat,'basic-eq.'); }

function setBalance(id, cost, budget, yieldVal, itemName){
    const el=__calculatorDeps.$(id); if(!el) return;
    const diff=budget-cost;
    el.classList.remove('shortfallCount','shortfallBreakdown');
    if(diff>=-0.5){ hidePlanBalance(id); return; }
    const short=Math.ceil(-diff);
    const count = yieldVal>0 ? Math.ceil(short/yieldVal) : 0;
    el.hidden=false;
    el.textContent=`${fmt(short)} short${count?` · ${fmt(count)} ${itemName}`:''}`;
    el.classList.add('shortfallCount');
  }

function setToolBalance(id,top,hardShort,yieldVal,label,protectedRuns=0,rawRemaining=0){
    const el=__calculatorDeps.$(id); if(!el) return;
    el.classList.remove('toolNeed','toolLeft');
    const materialName=label==='Hammers'?'Ore':label==='Knuckles'?'Essence':label==='Shovels'?'Sand':'materials';
    const planRuns=Math.max(0,Math.floor(Number(top?.planRuns ?? top?.runsUsed)||0));
    const reserveRuns=Math.max(0,Math.floor(Number(top?.reserveRuns)||0));
    const totalRuns=Math.max(0,planRuns+reserveRuns);
    const planPer=Math.max(0,Number(top?.planPerRun ?? yieldVal)||0);
    const reservePer=Math.max(0,Number(top?.reservePerRun)||0);
    const left=Math.max(0,Math.floor(Number(top?.bankedRemaining)||0)+Math.floor(Number(top?.sparePurchasedRuns)||0));
    // TOOL_VALUE_DISPLAY_V6: Use one display value per tool for BOTH Used and Left.
    // This applies to Hammers, Knuckles and Shovels, so a card can never mix S1 and S2
    // rates between the two rows. If any of the tools are fulfilling the season-transition
    // requirement, the whole card uses that carried-forward value; otherwise it uses the
    // current plan yield.
    // TOOL_RESERVE_HOLD_LABEL_V7: distinguish tools actually consumed for the
    // current-season plan from tools merely allocated to the S2 reserve. This keeps the
    // card from telling the player to "Use" tools that should stay banked for rollover.
    const planDisplayPer=Math.max(0,Number(planPer||yieldVal)||0);
    const reserveDisplayPer=Math.max(0,Number(reservePer)||0);
    const leftDisplayPer=reserveRuns>0&&reserveDisplayPer>0
      ? reserveDisplayPer
      : planDisplayPer;
    const planGained=planRuns*planDisplayPer;
    const reserveValue=reserveRuns*reserveDisplayPer;
    const leftValue=left*leftDisplayPer;
    const required=Math.max(0,Math.floor(Number(top?.runsNeeded)||totalRuns));
    const maxRuns=Math.max(0,Math.floor(Number(top?.maxRuns)||0));
    const missing=Math.max(0,required-maxRuns);
    // REMAINING_REALM_TOOLS_VISIBLE_V1
    // Keep the cards compact: never print Use: 0, but always preserve useful inventory context
    // by showing remaining Hammers/Knuckles/Shovels when any are still available.
    const remainingTools=Math.max(0,left+reserveRuns);
    const dailyGapRuns=Math.max(0,Math.floor(Number(top?.paidRunsUsed)||0));
    const toolSingular=label==='Hammers'?'Hammer':label==='Knuckles'?'Knuckle':label==='Shovels'?'Shovel':'tool';
    const toolNeedLabel=dailyGapRuns===1?toolSingular:label;
    // TOOL_NEED_VALUE_V14: show the material-equivalent value beside Need, matching Use.
    // If the gap exists to preserve an enabled rollover reserve, value those tools at the
    // reserve yield; otherwise use the current-season Material Realm yield.
    const dailyGapDisplayPer=reserveRuns>0&&reserveDisplayPer>0?reserveDisplayPer:planDisplayPer;
    const dailyGapValue=dailyGapRuns*dailyGapDisplayPer;
    // TOOL_COUNT_LABELS_V15: Use / Need / Remaining are Material Realm TOOL counts.
    // RAW_MATERIAL_SHORTFALL_DISPLAY_V1: once Realm capacity is exhausted, stop expressing
    // the unresolved gap as a tool count. Show the exact raw material still missing instead.
    const lines=[];
    const planToolLabel=planRuns===1?toolSingular:label;
    const remainingToolLabel=remainingTools===1?toolSingular:label;
    if(planRuns>0){
      lines.push(`<div class="toolSimpleLine toolUseLine"><i>Use:</i><b>${fmt(planRuns)} ${planToolLabel}${planGained>0?` <em>≈ ${fmtCompact(planGained)} ${materialName}</em>`:''}</b></div>`);
      if(dailyGapRuns>0){
        lines.push(`<div class="toolSimpleLine toolNeedLine"><i>Need:</i><b>${fmt(dailyGapRuns)} ${toolNeedLabel}${dailyGapValue>0?` <em>≈ ${fmtCompact(dailyGapValue)} ${materialName}</em>`:''}</b></div>`);
      }
    }
    // CONDITIONAL_TOOL_REMAINING_V1:
    // Show a remainder only when no additional Realm tools are required. If the plan
    // still has a Need line, suppress the tiny remainder created by whole-tool purchase
    // rounding so the result does not read as Need -> Remaining.
    if(dailyGapRuns<=0 && remainingTools>0){
      lines.push(`<div class="toolSimpleLine toolRemainingLine"><i>Remaining:</i><b>${fmt(remainingTools)} ${remainingToolLabel}${reserveRuns>0?` <em>(${fmt(reserveRuns)} reserved)</em>`:''}</b></div>`);
    }
    // Hard/recoverable material shortages are already communicated by the resource card above.
    // Do not resurrect the old duplicate "Still short" tool footer.
    if(!lines.length){ el.innerHTML=''; el.hidden=true; return; }
    el.hidden=false;
    el.innerHTML=lines.join('');
    el.classList.add((missing>0||dailyGapRuns>0)?'toolNeed':'toolLeft');
  }

// RESULT_STAMINA_PROJECTION_V1: repeat the optimizer's Stamina target in the
  // right-side resource cards so the next farming target remains obvious when Realm is closed.
function appendStaminaProjection(id,nodes,gain,materialName){
    const el=__calculatorDeps.$(id); if(!el) return;
    const count=Math.max(0,Math.floor(Number(nodes)||0));
    const value=Math.max(0,Number(gain)||0);
    if(count<=0) return;
    const line=document.createElement('div');
    line.className='toolSimpleLine staminaProjectionLine';
    line.innerHTML=`<i>Stamina:</i><b>${fmt(count)}${value>0?` <em>→ +${fmtCompact(value)} ${materialName}</em>`:''}</b>`;
    el.appendChild(line);
    el.hidden=false;
    if(!el.classList.contains('toolNeed')) el.classList.add('toolLeft');
  }

/* RICH_RESOURCE_SHORTFALL_NO_DUPLICATE_V1
     Keep the richer daily-plan / hard-cap presentation in the resource card itself.
     The separate Material Realm tool footer no longer repeats a "Still short" line. */
function setRealmShortfallBreakdown(id,planShort,yieldVal,itemName,maxExtraRuns,hardShort,resourceName='resource',appendText=''){
    const el=__calculatorDeps.$(id); if(!el) return;
    const short=Math.max(0,Math.ceil(Number(planShort)||0));
    const per=Math.max(0,Number(yieldVal)||0);
    const runsToCover=per>0?Math.ceil(short/per):0;
    const extraRuns=Math.max(0,Math.floor(Number(maxExtraRuns)||0));
    const usableExtra=Math.min(runsToCover,extraRuns);
    const extraResource=usableExtra*per;
    const hard=Math.max(0,Math.ceil(Number(hardShort)||0));
    el.classList.remove('shortfallCount','rawRemaining','reserveHasGap');
    el.classList.add('shortfallBreakdown');
    el.hidden=false;
    if(short<=0){
      el.textContent=`0 short${appendText}`;
      return;
    }
    /* SHORTFALL_MESSAGING_V2
       Hard shorts collapse to one red failure line; don't show a theoretical daily-plan
       bridge that cannot actually succeed. Recoverable shortages keep a concise red+yellow
       two-line pattern with the exact raw-material deficit. */
    if(hard>0){
      const hardLine=`${fmt(hard)} ${resourceName} still missing · max Realm capacity exhausted`;
      el.innerHTML=`<span class="hardShort">${hardLine}</span>${appendText?`<span>${appendText}</span>`:''}`;
      return;
    }
    /* RECOVERABLE_SHORTFALL_REFRESH_PLAN_V1
       Recoverable resource cards show the exact material gap and additional tool count.
       Once the combined daily Realm recommendation is known later in updateCalculator(),
       the yellow bridge line is replaced with that resource's actionable refreshes/day. */
    const line1=`${fmt(short)} ${resourceName} short${runsToCover?` · +${fmt(runsToCover)} ${itemName}`:''}`;
    let line2='';
    if(extraRuns>0 && per>0){
      line2=`${fmt(runsToCover)} ${itemName} can cover`;
    }
    el.dataset.shortfallTools=String(runsToCover||0);
    el.dataset.shortfallItem=itemName;
    el.dataset.shortfallResource=resourceName;
    el.innerHTML=`<span class="planShort">${line1}</span>${line2?`<span class="realmBridge">${line2}</span>`:''}${appendText?`<span>${appendText}</span>`:''}`;
  }

let lastAstralRenderKey='';

let lastPrimostarRewardRenderKey='';

function renderAstralPact(totalStars){
    const stars=Math.max(0,Math.floor(Number(totalStars)||0));
    const renderKey=String(stars);
    if(renderKey===lastAstralRenderKey) return;
    lastAstralRenderKey=renderKey;
    const totals=Object.fromEntries(ASTRAL_ORDER.map(k=>[k,0]));
    let unlocked=0;
    for(const [threshold,key,value] of ASTRAL_PACT_NODES){
      if(threshold>stars) break;
      totals[key]=(totals[key]||0)+value;
      unlocked++;
    }
    const box=__calculatorDeps.$('astralRewardTotals');
    if(box){
      box.innerHTML=ASTRAL_ORDER.map(key=>`<span>${ASTRAL_LABELS[key]}<b>+${fmt(totals[key]||0)}%</b></span>`).join('');
    }
    const next=ASTRAL_PACT_NODES.find(([threshold])=>threshold>stars);
    const count=__calculatorDeps.$('astralRewardCount');
    if(count){
      const s1Unlocked=ASTRAL_PACT_NODES.slice(0,40).filter(([threshold])=>threshold<=stars).length;
      const seasonText=stars<=480?`${s1Unlocked} of 40 documented S1 nodes unlocked`:`${unlocked} of ${ASTRAL_PACT_NODES.length} documented S1–S2 nodes unlocked`;
      const nextText=next?` · next: ${fmt(next[0])} → ${ASTRAL_LABELS[next[1]]} +${next[2]}%`:' · all documented S1–S2 nodes unlocked';
      count.textContent=`${fmt(stars)} projected total Primostars · ${seasonText}${nextText}.`;
    }
  }

/* PRIMOSTAR_REWARD_REFERENCE_V2
     Checkmarks mean actually reached now, never merely targeted/projected.
     Season 2 rows stay hidden until the live calculator season is actually S2. */
function renderPrimostarRewardReference(currentTotalStars,projectedTotalStars=currentTotalStars){
    const currentStars=Math.max(0,Math.floor(Number(currentTotalStars)||0));
    const projectedStars=Math.max(currentStars,Math.floor(Number(projectedTotalStars)||0));
    const rewardRenderKey=`${activeCalcConfig().key}|${currentStars}|${projectedStars}`;
    if(rewardRenderKey===lastPrimostarRewardRenderKey) return;
    lastPrimostarRewardRenderKey=rewardRenderKey;
    const host=__calculatorDeps.$('primostarRewardSeasons');
    const intro=__calculatorDeps.$('primostarRewardsIntro');
    if(!host) return;
    const cfg=activeCalcConfig();
    const s1Nodes=ASTRAL_PACT_NODES.slice(0,40);
    const visibleNodes=cfg.key==='s2'?ASTRAL_PACT_NODES:s1Nodes;
    // The result card is a season-end projection, so the highlighted "next" reward must
    // be the first threshold AFTER the projected total, not merely the next reward after
    // today's current total. Otherwise a 920 projection could misleadingly say "next 305".
    const nextIndex=visibleNodes.findIndex(([threshold])=>threshold>projectedStars);
    const nextReward=visibleNodes.find(([threshold])=>threshold>projectedStars);
    const groups=[{title:'Witching Hours',nodes:s1Nodes,offset:0}];
    if(cfg.key==='s2') groups.push({title:'Crossed Paths',nodes:ASTRAL_PACT_NODES.slice(40),offset:40});
    const row=(node,index)=>{
      const [threshold,key,value]=node;
      const projected=threshold>currentStars&&threshold<=projectedStars;
      const state=threshold<=currentStars?'reached':projected?'projected':index===nextIndex?'next':'future';
      return `<div class="primostarRewardRow ${state}"><span class="rewardThreshold">${fmt(threshold)}</span><span class="rewardName">${ASTRAL_LABELS[key]||key}</span><span class="rewardValue">+${fmt(value)}%</span></div>`;
    };
    // RESOURCE_TOOLS_REWARD_LAYOUT_V1: long reward tables use two vertical columns on desktop.
    const rewardLists=(group)=>{
      if(group.nodes.length<=20) return `<div class="primostarRewardList">${group.nodes.map((node,i)=>row(node,group.offset+i)).join('')}</div>`;
      const split=Math.ceil(group.nodes.length/2);
      const left=group.nodes.slice(0,split);
      const right=group.nodes.slice(split);
      return `<div class="primostarRewardColumns"><div class="primostarRewardList">${left.map((node,i)=>row(node,group.offset+i)).join('')}</div><div class="primostarRewardList">${right.map((node,i)=>row(node,group.offset+split+i)).join('')}</div></div>`;
    };
    host.innerHTML=groups.map(group=>`<section class="primostarRewardSeason"><h4>${group.title}</h4>${rewardLists(group)}</section>`).join('');
    if(intro){
      const projectedCount=visibleNodes.filter(([threshold])=>threshold>currentStars&&threshold<=projectedStars).length;
      if(projectedStars>currentStars){
        const projectionText=`${fmt(currentStars)} current · ${fmt(projectedStars)} projected`;
        intro.textContent=nextReward
          ? `${projectionText} · ${fmt(projectedCount)} more reward${projectedCount===1?'':'s'} projected · next after projection at ${fmt(nextReward[0])}: ${ASTRAL_LABELS[nextReward[1]]} +${fmt(nextReward[2])}%.`
          : `${projectionText} · ${fmt(projectedCount)} more reward${projectedCount===1?'':'s'} projected · all currently available Astral Pact rewards covered.`;
      }else{
        intro.textContent=nextReward
          ? `${fmt(currentStars)} current · next reward at ${fmt(nextReward[0])}: ${ASTRAL_LABELS[nextReward[1]]} +${fmt(nextReward[2])}%.`
          : `${fmt(currentStars)} current · all currently available Astral Pact rewards reached.`;
      }
    }
  }

function renderCalculatorSeasonChrome(cfg){
    renderLocalTimeLabels();
    __calculatorDeps.$('seasonDeadlineLabel').textContent=`${cfg.name} ends`;
    __calculatorDeps.$('seasonDeadlineDate').textContent=localDeadlineLabel(cfg.end,cfg.key==='s2');
    __calculatorDeps.$('historicalStarsLabel').textContent='Season 1 Primostars';
    __calculatorDeps.$('projectionNote').textContent=`Uses exact server resets (${nextResetLocalLabel()} on this device); future free 2-hour reset boosts are included automatically.`;
    if(__calculatorDeps.$('astralBonusReference')) __calculatorDeps.$('astralBonusReference').hidden=false;
    const s2Presets=__calculatorDeps.$('s2TargetPresets'),s2Gates=__calculatorDeps.$('s2ProgressionGates'),seasonHint=__calculatorDeps.$('seasonRulesHint');
    if(s2Presets) s2Presets.hidden=cfg.key!=='s2';
    if(s2Gates) s2Gates.hidden=cfg.key!=='s2';
    if(seasonHint) seasonHint.hidden=cfg.key!=='s2';
    if(s2Presets){
      const currentTarget=Math.floor(__calculatorDeps.n('targetStars',cfg.key==='s2'?680:200));
      s2Presets.querySelectorAll('[data-s2-target]').forEach(btn=>btn.classList.toggle('active',Number(btn.dataset.s2Target)===currentTarget));
    }
    const setInputMax=(id,max)=>{const el=__calculatorDeps.$(id);if(!el)return;if(Number.isFinite(max))el.max=String(max);else el.removeAttribute('max');};
    if(cfg.key==='s2'){
      __calculatorDeps.$('seasonRulesHint').innerHTML='<b>S2 scoring still starts at Lv.130:</b> +45 fixed · 27 score / Primostar · normal floor Lv.130 / Relics above +13 · weights Character 100, Gear 18, Skill 7, Relic 33, Fantomon 8. <b>Lv.120+</b> can use the planner now; while you are Lv.120–130 it runs a clearly labeled <b>Lv.131 unlock preview</b> for upgrade availability so stockpiled resources can be evaluated before full seasonal progression opens. No pre-130 Character score is awarded. Starter floor: Gear 130 · Skills 130 · Fantomons 130 · Relics +13.';
      const currentCaps=categoryInputCapsForCharacter(__calculatorDeps.characterSnapshot(cfg).level,cfg);
      /* S2_SCORING_INPUT_FLOOR_V2: Character Lv.130 unlocks the planner; actual category
         inputs may still be below their score floors and must retain their real catch-up costs. */
      __calculatorDeps.$('skillLevel').min='100'; setInputMax('skillLevel',currentCaps.skill); __calculatorDeps.$('skillLevel').step='0.125';
      __calculatorDeps.$('relicLevel').min='10'; setInputMax('relicLevel',currentCaps.relic); __calculatorDeps.$('relicLevel').step='0.05';
      __calculatorDeps.$('fantomonLevel').min='100'; setInputMax('fantomonLevel',currentCaps.fanto); __calculatorDeps.$('fantomonLevel').step='0.25';
      if(__calculatorDeps.$('gearLevel')){__calculatorDeps.$('gearLevel').min='100';setInputMax('gearLevel',currentCaps.gear);__calculatorDeps.$('gearLevel').step='0.2';}
    } else {
      __calculatorDeps.$('seasonRulesHint').innerHTML='Season 2 data is preloaded: <b>Material Realm reaches its S2 max at Lv.120</b>; Season Power scoring starts at Lv.130.';
      const currentCaps=categoryInputCapsForCharacter(__calculatorDeps.characterSnapshot(cfg).level,cfg);
      __calculatorDeps.$('skillLevel').min='100'; setInputMax('skillLevel',currentCaps.skill); __calculatorDeps.$('skillLevel').step='0.125';
      __calculatorDeps.$('relicLevel').min='10'; setInputMax('relicLevel',currentCaps.relic); __calculatorDeps.$('relicLevel').step='0.05';
      __calculatorDeps.$('fantomonLevel').min='100'; setInputMax('fantomonLevel',currentCaps.fanto); __calculatorDeps.$('fantomonLevel').step='0.25';
      if(__calculatorDeps.$('gearLevel')){__calculatorDeps.$('gearLevel').min='100';setInputMax('gearLevel',currentCaps.gear);__calculatorDeps.$('gearLevel').step='0.2';}
    }
    // S2_AUTO_RESET_STALE_SNAPSHOT_V1: stale pre-S2 calculator state is never offered for reuse.
    // Load clean S2 defaults immediately so old seasonal levels/resources cannot leak into the new season.
    if(cfg.key==='s2' && __calculatorDeps.snapshotSeason!==cfg.key){
      __calculatorDeps.applyS2ScoringStartDefaults();
      __calculatorDeps.snapshotSeason=cfg.key;
      __calculatorDeps.snapshotAtMs=Date.now();
      __calculatorDeps.snapshotCarry={ore:0,essence:0,sand:0,treat:0,exp:0};
      __calculatorDeps.snapshotStateLoaded=true;
      __calculatorDeps.saveState();
    }
    const mismatch=__calculatorDeps.snapshotSeason!==cfg.key;
    __calculatorDeps.$('calcSeasonNotice').hidden=!mismatch;
    __calculatorDeps.$('calcResults').classList.toggle('rolloverBlocked',mismatch);
    if(mismatch){
      __calculatorDeps.$('calcSeasonNoticeTitle').textContent=`${cfg.name} is live — refresh the saved snapshot`;
      __calculatorDeps.$('calcSeasonNoticeText').textContent=cfg.key==='s2'
        ? `Your saved calculator state is from ${CALC_SEASONS[__calculatorDeps.snapshotSeason]?.name||'the prior season'}. S2 Season Power does not unlock until Lv.130, so this scoring planner intentionally ignores the Lv.100→130 catch-up phase. At Lv.130, enter your actual carried Primostars/resources and current progression, then confirm the S2 snapshot.`
        : `Your saved calculator state is from ${CALC_SEASONS[__calculatorDeps.snapshotSeason]?.name||'the prior season'}. Update Character level/EXP, Gear, Skills, Relics, Fantomons, resources/Cart rates and carried Primostars, then confirm. The site intentionally refuses to assume how the seasonal reset changed your account.`;
      __calculatorDeps.$('confirmSeasonSnapshot').textContent=`Use entries as ${cfg.name} snapshot`;
    }
    return mismatch;
  }

function clearS2PreScoring(cfg){
    if(__calculatorDeps.$('resultStamina')) __calculatorDeps.$('resultStamina').hidden=true;
    const current=__calculatorDeps.characterSnapshot(cfg),p=__calculatorDeps.projectCharacter(cfg);
    __calculatorDeps.$('seasonRemaining').textContent=formatRemaining(remainingHoursAt(Date.now(),cfg));
    __calculatorDeps.$('projectedCharacter').value=`Lv.${p.level} · ${(p.pct*100).toFixed(1)}%`;
    __calculatorDeps.$('resultProjectedCharacter').textContent=`Lv.${p.level} (${(p.pct*100).toFixed(1)}%)`;
    __calculatorDeps.$('currentStars').textContent='—'; __calculatorDeps.$('currentScoreNow').textContent='—'; __calculatorDeps.$('summaryOptimizedScore').textContent='—'; __calculatorDeps.$('desiredScore').textContent='—';
    __calculatorDeps.$('targetMessage').hidden=false; __calculatorDeps.$('targetMessage').classList.remove('danger'); __calculatorDeps.$('targetMessage').classList.add('warning','caution');
    __calculatorDeps.$('targetMessage').textContent=`Season Power scoring still uses the Lv.${cfg.scoreFloor} baseline, but forward planning becomes available at Lv.${S2_PLANNER_START_LEVEL}. Current Lv.${current.level} is below that planning threshold, so the calculator stays paused until Lv.${S2_PLANNER_START_LEVEL}.`;
    if(__calculatorDeps.$('targetStatus')){__calculatorDeps.$('targetStatus').textContent='locked';__calculatorDeps.$('targetStatus').classList.remove('notMet');}
    __calculatorDeps.$('optimizerSummary').textContent=`Return at Lv.${S2_PLANNER_START_LEVEL} and enter your actual state. From there the calculator projects EXP and resources through the Lv.${cfg.scoreFloor} Season Power baseline and season end.`;
    __calculatorDeps.$('optimizedScore').textContent='—';
    __calculatorDeps.$('materialRealmRecommendation').hidden=true;
    renderRealmToolProjection(cfg);
  }

function clearS2ProjectedAtFloor(cfg,p=__calculatorDeps.projectCharacter(cfg)){
    if(__calculatorDeps.$('resultStamina')) __calculatorDeps.$('resultStamina').hidden=true;
    const historical=Math.max(0,Math.floor(__calculatorDeps.n('historicalStars',0)));
    const carried=historical+cfg.starBase;
    const seasonEndP=__calculatorDeps.projectCharacter(cfg);
    __calculatorDeps.$('seasonRemaining').textContent=formatRemaining(seasonEndP.hours);
    __calculatorDeps.$('projectedCharacter').value=`Lv.${seasonEndP.level} · ${(seasonEndP.pct*100).toFixed(1)}%`;
    __calculatorDeps.$('resultProjectedCharacter').textContent=`Lv.${p.level} (${(p.pct*100).toFixed(1)}%)`;
    __calculatorDeps.$('currentStars').textContent=fmt(carried);
    __calculatorDeps.$('currentScoreNow').textContent='0';
    __calculatorDeps.$('summaryOptimizedScore').textContent='—';
    __calculatorDeps.$('desiredScore').textContent='—';
    if(__calculatorDeps.$('recommendedBreakdownSection')) __calculatorDeps.$('recommendedBreakdownSection').hidden=true;
    __calculatorDeps.$('targetMessage').hidden=false;
    __calculatorDeps.$('targetMessage').classList.remove('danger');
    __calculatorDeps.$('targetMessage').classList.add('warning','caution');
    __calculatorDeps.$('targetMessage').textContent=`Projected season-end Character is Lv.${p.level}. The S2 optimizer stays paused until the projection reaches Lv.131, so a Lv.130-or-lower projection never runs the heavy upgrade search.`;
    if(__calculatorDeps.$('targetStatus')){__calculatorDeps.$('targetStatus').textContent='waiting for Lv.131';__calculatorDeps.$('targetStatus').classList.remove('notMet');}
    __calculatorDeps.$('optimizerSummary').textContent='No Gear / Skill / Relic / Fantomon optimization runs while projected season-end Character remains Lv.130 or lower.';
    __calculatorDeps.$('optimizedScore').textContent='—';
    ['targetSkills','targetRelics','targetFantomons'].forEach(id=>{if(__calculatorDeps.$(id))__calculatorDeps.$(id).textContent='—';});
    GEAR_OUTPUT_IDS.forEach(id=>{if(__calculatorDeps.$(id))__calculatorDeps.$(id).textContent='—';});
    ['oreCost','essenceCost','sandCost','treatCost'].forEach(id=>{if(__calculatorDeps.$(id))__calculatorDeps.$(id).textContent='0';});
    ['oreBalance','essenceBalance','sandBalance','treatBalance','oreToolBalance','essenceToolBalance','sandToolBalance'].forEach(hidePlanBalance);
    __calculatorDeps.$('materialRealmRecommendation').hidden=true;__calculatorDeps.$('materialRealmRecommendation').textContent='';
    __calculatorDeps.$('secondaryCostNote').hidden=true;__calculatorDeps.$('secondaryCostNote').textContent='';
    __calculatorDeps.$('milestoneNote').hidden=true;__calculatorDeps.$('milestoneNote').textContent='';
    renderAstralPact(carried);
    renderPrimostarRewardReference(carried,carried);
    __calculatorDeps.saveState();
    const calcSection=__calculatorDeps.$('calculatorSection');
    if(calcSection) calcSection.dataset.lastSolveMs='0.0';
  }

function clearCalcForRollover(cfg){
    if(__calculatorDeps.$('resultStamina')) __calculatorDeps.$('resultStamina').hidden=true;
    __calculatorDeps.$('seasonRemaining').textContent=formatRemaining(remainingHoursAt(Date.now(),cfg));
    __calculatorDeps.$('projectedCharacter').value='Update snapshot';
    __calculatorDeps.$('resultProjectedCharacter').textContent='Update snapshot';
    __calculatorDeps.$('currentStars').textContent='—'; __calculatorDeps.$('currentScoreNow').textContent='—'; __calculatorDeps.$('summaryOptimizedScore').textContent='—'; __calculatorDeps.$('desiredScore').textContent='—';
    __calculatorDeps.$('targetMessage').hidden=false; __calculatorDeps.$('targetMessage').classList.add('warning');
    __calculatorDeps.$('targetMessage').textContent=`${cfg.name} rules are ready, but the calculator is paused until you confirm a fresh ${cfg.name} snapshot.`;
    if(__calculatorDeps.$('targetStatus')){__calculatorDeps.$('targetStatus').textContent='—';__calculatorDeps.$('targetStatus').classList.remove('notMet');}
    __calculatorDeps.$('optimizerSummary').textContent='Update all current-state fields above, then use the season snapshot button.';
    __calculatorDeps.$('optimizedScore').textContent='—';
    __calculatorDeps.$('materialRealmRecommendation').hidden=true;
  }

function clearS2ForRequiredPlannerInputs(cfg,requirements,p=null){
    if(__calculatorDeps.$('resultStamina')) __calculatorDeps.$('resultStamina').hidden=true;
    const missing=[];
    if(!requirements.hasBed) missing.push('Bed EXP/hr');
    missing.push(...requirements.missingCart);
    // Character projection is lightweight and only needs Bed EXP; keep it available while
    // the material-production guard continues to block the expensive Primostar optimizer.
    if(requirements.hasBed && p){
      if(__calculatorDeps.$('seasonRemaining')) __calculatorDeps.$('seasonRemaining').textContent=formatRemaining(p.hours);
      if(__calculatorDeps.$('projectedCharacter')) __calculatorDeps.$('projectedCharacter').value=`Lv.${p.level} · ${(p.pct*100).toFixed(1)}%`;
      if(__calculatorDeps.$('resultProjectedCharacter')) __calculatorDeps.$('resultProjectedCharacter').textContent=`Lv.${p.level} (${(p.pct*100).toFixed(1)}%)`;
    }else{
      if(__calculatorDeps.$('projectedCharacter')) __calculatorDeps.$('projectedCharacter').value='Enter Bed EXP';
      if(__calculatorDeps.$('resultProjectedCharacter')) __calculatorDeps.$('resultProjectedCharacter').textContent='—';
    }
    ['currentStars','currentScoreNow','summaryOptimizedScore','desiredScore','optimizedScore'].forEach(id=>{if(__calculatorDeps.$(id))__calculatorDeps.$(id).textContent='—';});
    if(__calculatorDeps.$('targetStatus')){
      __calculatorDeps.$('targetStatus').textContent='waiting for production inputs';
      __calculatorDeps.$('targetStatus').classList.remove('notMet');
    }
    if(__calculatorDeps.$('targetMessage')){
      __calculatorDeps.$('targetMessage').hidden=false;
      __calculatorDeps.$('targetMessage').classList.remove('danger');
      __calculatorDeps.$('targetMessage').classList.add('warning','caution');
      __calculatorDeps.$('targetMessage').textContent=`Enter ${missing.join(' and ')} to run the S2 optimizer. Saved materials and Material Realm purchases can stay at 0.`;
    }
    if(__calculatorDeps.$('optimizerSummary')){
      __calculatorDeps.$('optimizerSummary').hidden=false;
      __calculatorDeps.$('optimizerSummary').textContent='The heavy Primostar search is paused until Bed EXP and all four Cart production rates are entered.';
    }
    if(__calculatorDeps.$('recommendedBreakdownSection')) __calculatorDeps.$('recommendedBreakdownSection').hidden=true;
    ['targetSkills','targetRelics','targetFantomons'].forEach(id=>{if(__calculatorDeps.$(id))__calculatorDeps.$(id).textContent='—';});
    GEAR_OUTPUT_IDS.forEach(id=>{if(__calculatorDeps.$(id))__calculatorDeps.$(id).textContent='—';});
    ['oreCost','essenceCost','sandCost','treatCost'].forEach(id=>{if(__calculatorDeps.$(id))__calculatorDeps.$(id).textContent='0';});
    ['oreBalance','essenceBalance','sandBalance','treatBalance','oreToolBalance','essenceToolBalance','sandToolBalance'].forEach(hidePlanBalance);
    if(__calculatorDeps.$('materialRealmRecommendation')){__calculatorDeps.$('materialRealmRecommendation').hidden=true;__calculatorDeps.$('materialRealmRecommendation').textContent='';}
    if(__calculatorDeps.$('secondaryCostNote')){__calculatorDeps.$('secondaryCostNote').hidden=true;__calculatorDeps.$('secondaryCostNote').textContent='';}
    if(__calculatorDeps.$('milestoneNote')){__calculatorDeps.$('milestoneNote').hidden=true;__calculatorDeps.$('milestoneNote').textContent='';}
    const calcSection=__calculatorDeps.$('calculatorSection');
    if(calcSection) calcSection.dataset.lastSolveMs='0.0';
    __calculatorDeps.saveState();
  }
return {renderRealmToolProjection, renderRealmDailyRecommendations, renderLocalTimeLabels, renderTargetResourceSnapshot, renderPostTargetGains, renderTargetTiming, renderStaminaCurrentPlan, hidePlanBalance, setRawRemaining, setSandBalance, setTreatBalance, setBalance, setToolBalance, appendStaminaProjection, setRealmShortfallBreakdown, renderAstralPact, renderPrimostarRewardReference, renderCalculatorSeasonChrome, clearS2PreScoring, clearS2ProjectedAtFloor, clearCalcForRollover, clearS2ForRequiredPlannerInputs};
}
