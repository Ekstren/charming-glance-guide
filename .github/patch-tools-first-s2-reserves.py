from pathlib import Path
import re

PATH=Path('index.html')
text=PATH.read_text(encoding='utf-8')
MARKER='TOOLS_FIRST_S2_RESERVES_V1'
if MARKER in text:
    print('Tools-first S2 reserve model already applied.')
    raise SystemExit(0)


def sub_once(pattern,repl,label,flags=re.S):
    global text
    text2,count=re.subn(pattern,repl,text,count=1,flags=flags)
    if count!=1:
        raise SystemExit(f'{label}: expected 1 match, got {count}')
    text=text2

# 1) Central split helper + acquisition supply.
#    Enabled S2 Essence/Sand reserves are funded from carried/planned Realm tools FIRST.
#    Raw material is held only for whatever the reserved tools cannot cover.
sub_once(
    r"  /\* OPTIMIZER_AUDIT_V3\n     Resource scarcity is evaluated against supply that is genuinely safe to spend after\n     enabled S2 reserves\..*?\n  function dynamicAcquisitionWeights\(resources\)\{",
    r'''  /* OPTIMIZER_AUDIT_V3 · TOOLS_FIRST_S2_RESERVES_V1
     Enabled S2 Essence/Sand reserves hold carried/planned Realm tools first. Raw material
     is reserved only for the portion those tools cannot cover. If a reserve is disabled,
     raw remains the first current-season spend source and Realm tools stay untouched until
     the raw material is genuinely exhausted. */
  function toolsFirstReserveSplit(key,reserveTarget,rawAvailable,resources,cfg=activeCalcConfig()){
    const target=Math.max(0,Number(reserveTarget)||0);
    const raw=Math.max(0,Number(rawAvailable)||0);
    if(target<=0 || (key!=='essence'&&key!=='sand')) return {target,toolRuns:0,toolValue:0,rawHeld:Math.min(raw,target),shortfall:Math.max(0,target-raw),reservePerRun:0,toolsAvailable:0};
    const inv=realmInventoryFor(key,cfg);
    const tools=Math.max(0,Math.floor(Number(inv?.banked)||0));
    const reservePerRun=Math.max(0,reserveYieldFor(key,cfg));
    if(reservePerRun<=0) return {target,toolRuns:0,toolValue:0,rawHeld:Math.min(raw,target),shortfall:Math.max(0,target-raw),reservePerRun,toolsAvailable:tools};
    const toolRuns=Math.min(tools,Math.ceil(target/reservePerRun));
    const toolValue=Math.min(target,toolRuns*reservePerRun);
    const rawNeed=Math.max(0,target-toolValue);
    const rawHeld=Math.min(raw,rawNeed);
    const shortfall=Math.max(0,rawNeed-rawHeld);
    return {target,toolRuns,toolValue,rawHeld,shortfall,reservePerRun,toolsAvailable:tools};
  }

  function reserveAdjustedAcquisitionSupply(key,resources,cfg=activeCalcConfig()){
    const raw=Math.max(0,Number(resources?.[key])||0);
    const reserve=Math.max(0,reserveTargetFor(key,resources,cfg));
    if(key==='treat') return Math.max(0,raw-reserve);
    if(key!=='essence'&&key!=='sand') return raw;

    const inv=realmInventoryFor(key,cfg);
    const tools=Math.max(0,Math.floor(Number(inv?.banked)||0));
    const currentPer=Math.max(0,realmYieldFor(resources,key));
    if(reserve<=0) return raw+tools*currentPer;

    const split=toolsFirstReserveSplit(key,reserve,raw,resources,cfg);
    // If the enabled reserve still cannot be covered, every existing raw unit/tool is
    // already spoken for; additional Realm purchases are a last-resort feasibility path.
    if(split.shortfall>0.5) return 0;
    return Math.max(0,raw-split.rawHeld)+Math.max(0,tools-split.toolRuns)*currentPer;
  }

  function dynamicAcquisitionWeights(resources){''',
    'tools-first acquisition supply'
)

# 2) Candidate-specific Realm funding.
#    Reserve tools are allocated before raw. Only the reserve remainder is held as raw.
#    The S1 plan then spends all unreserved raw before touching any unreserved Realm tools.
sub_once(
    r"  function reserveAwareRealmTopupFor\(key,planCost,rawBudget,resources,cfg=activeCalcConfig\(\),p=null\)\{.*?\n  \}\n\n  function formatRealmSchedule",
    r'''  function reserveAwareRealmTopupFor(key,planCost,rawBudget,resources,cfg=activeCalcConfig(),p=null){
    if(cfg.key!=='s1' || (key!=='essence'&&key!=='sand')) return realmTopupFor(key,planCost,rawBudget,resources,cfg,p);
    const raw=Math.max(0,Number(rawBudget)||0);
    const cost=Math.max(0,Number(planCost)||0);
    const reserveTarget=reserveTargetFor(key,resources,cfg);
    if(reserveTarget<=0) return realmTopupFor(key,cost,raw,resources,cfg,p);

    const inv=realmInventoryFor(key,cfg);
    const days=Number.isFinite(resources?.realmDays)?resources.realmDays:materialRealmDaysAvailable(cfg);
    const planPerRun=Math.max(0,realmYieldFor(resources,key));
    const reservePerRun=Math.max(0,reserveYieldFor(key,cfg));
    const split=toolsFirstReserveSplit(key,reserveTarget,raw,resources,cfg);
    const rawSpendable=Math.max(0,raw-split.rawHeld);
    const planShortfall=Math.max(0,cost-rawSpendable);
    const planRuns=planShortfall>0&&planPerRun>0?Math.ceil(planShortfall/planPerRun):(planShortfall>0?Infinity:0);
    const reserveExtraRuns=split.shortfall>0&&reservePerRun>0?Math.ceil(split.shortfall/reservePerRun):(split.shortfall>0?Infinity:0);
    if(!Number.isFinite(planRuns)||!Number.isFinite(reserveExtraRuns)){
      return {feasible:false,unsupported:true,shortfall:planShortfall+split.shortfall,runsNeeded:Infinity,runsUsed:0,bankedUsed:0,bankedRemaining:inv.banked,packs:Infinity,attempts:Infinity,purchasedRuns:0,paidRunsUsed:0,sparePurchasedRuns:0,dawnium:Infinity,days,dailyCounts:[],provided:0,maxPacks:0,maxAttempts:0,maxRuns:inv.banked,maxProvided:0,remainingAfterMax:planShortfall+split.shortfall,baselinePerDay:inv.baselineRefreshes,planRuns:0,reserveRuns:split.toolRuns,planProvided:0,reserveProvided:split.toolValue,reserveGap:split.shortfall,rawAfterPlan:Math.max(0,raw-cost),rawReserveHeld:split.rawHeld,rawSpendable,reserveTarget,reservePerRun,planPerRun};
    }

    const reserveRuns=split.toolRuns+reserveExtraRuns;
    const totalRuns=reserveRuns+planRuns;
    // Run realmTopup in TOOL units so banked entries, 5-entry purchases, daily limits and
    // Dawnium pricing are shared correctly between the held reserve and the S1 plan.
    const top=realmTopup(totalRuns,0,1,days,inv.banked,inv.baselineRefreshes);
    const maxToolRuns=Math.max(0,Math.floor(Number(top.maxRuns)||0));
    const actualReserveRuns=Math.min(reserveRuns,maxToolRuns);
    const maxPlanRuns=Math.max(0,maxToolRuns-actualReserveRuns);
    const actualPlanRuns=top.feasible?planRuns:Math.min(planRuns,maxPlanRuns);
    const planProvided=actualPlanRuns*planPerRun;
    const reserveProvided=Math.min(reserveTarget,actualReserveRuns*reservePerRun+split.rawHeld);
    const reserveShortAfterMax=Math.max(0,reserveTarget-(actualReserveRuns*reservePerRun+split.rawHeld));
    const planShortAfterMax=Math.max(0,planShortfall-actualPlanRuns*planPerRun);
    const remainingAfterMax=reserveShortAfterMax+planShortAfterMax;
    const rawAfterPlan=Math.max(0,raw+planProvided-cost);

    return {...top,
      shortfall:planShortfall+split.shortfall,
      runsNeeded:totalRuns,
      runsUsed:top.feasible?totalRuns:Math.min(totalRuns,maxToolRuns),
      provided:planProvided,
      maxProvided:maxPlanRuns*planPerRun,
      planRuns,reserveRuns,planProvided,reserveProvided,
      reserveBankedRuns:split.toolRuns,reserveExtraRuns,
      planShortfall,reserveGap:split.shortfall,rawAfterPlan,
      rawReserveHeld:split.rawHeld,rawSpendable,reserveTarget,
      reservePerRun,planPerRun,remainingAfterMax
    };
  }

  function formatRealmSchedule''',
    'tools-first reserve topup'
)

# 3) Raw Remaining remains strictly raw. Its parenthetical reserve is ONLY the raw portion
#    of the S2 reserve after tools have been allocated first.
sub_once(
    r"  // RAW_FIRST_RESERVE_DISPLAY_V5:.*?\n  function setEssenceBalance\(id,cost,resources\)\{ setReservedRawRemaining\(id,cost,resources,'essence'\); \}",
    r'''  // TOOLS_FIRST_RAW_RESERVE_DISPLAY_V6: Remaining is strictly RAW material left
  // after the S1 plan. The reserve annotation is only the raw remainder that must be held
  // AFTER carried/planned Realm tools have been assigned to the enabled S2 reserve first.
  function setReservedRawRemaining(id,cost,resources,key,unitLabel=''){
    const el=$(id); if(!el) return;
    el.classList.remove('shortfallCount','shortfallBreakdown','reserveHasGap');
    el.classList.add('rawRemaining');
    const available=Math.max(0,Number(resources?.[key])||0);
    const left=Math.max(0,Math.floor(available-(Number(cost)||0)+1e-9));
    const reserveTarget=Math.max(0,Math.floor(reserveTargetFor(key,resources)+1e-9));
    let rawReserved=0;
    if(reserveTarget>0){
      if(key==='essence'||key==='sand'){
        const split=toolsFirstReserveSplit(key,reserveTarget,available,resources,activeCalcConfig());
        rawReserved=Math.min(left,Math.max(0,Math.floor(split.rawHeld+1e-9)));
      }else{
        rawReserved=Math.min(left,reserveTarget);
      }
    }
    const unit=unitLabel?` ${unitLabel}`:'';
    el.hidden=false;
    el.textContent=`Remaining: ${fmt(left)}${unit}${rawReserved>0?` (${fmt(rawReserved)}${unit} reserved)`:''}`;
  }
  function setEssenceBalance(id,cost,resources){ setReservedRawRemaining(id,cost,resources,'essence'); }''',
    'raw reserve display'
)

# 4) Reserve-only Realm tools must remain visible. With reserves OFF and no S1 tool need,
#    these rows stay hidden, so the result naturally reads as raw-only spending.
old_hide="    // TOOL_DAILY_GAP_V13: shared by Hammers, Knuckles and Shovels.\n    // Reserve-only tools stay hidden unless the current-season plan actually uses this tool.\n    // Need = additional tool entries required beyond the CURRENT daily refresh plan. It falls\n    // as the user raises that daily setting and disappears once the configured plan covers it.\n    if(planRuns<=0 && missing<=0){ el.innerHTML=''; el.hidden=true; return; }"
new_hide="    // TOOL_DAILY_GAP_V13 · TOOLS_FIRST_S2_RESERVES_V1: reserve-only tools stay visible\n    // so it is clear which entries are being held for S2. With reserves off and no S1\n    // shortage, the tool row remains hidden.\n    if(planRuns<=0 && reserveRuns<=0 && missing<=0){ el.innerHTML=''; el.hidden=true; return; }"
if text.count(old_hide)!=1:
    raise SystemExit(f'tool hide block count={text.count(old_hide)}')
text=text.replace(old_hide,new_hide,1)

reserve_only_anchor="    if(missing>0){\n      const rawStillShort=Math.max(0,Math.ceil(Number(hardShort)||0));"
reserve_only_insert="    if(planRuns<=0 && reserveRuns>0 && remainingTools>0){\n      lines.push(`<div class=\"toolSimpleLine toolRemainingLine\"><i>Remaining:</i><b>${fmt(remainingTools)} ${remainingToolLabel} <em>(${fmt(reserveRuns)} reserved)</em></b></div>`);\n    }\n    if(missing>0){\n      const rawStillShort=Math.max(0,Math.ceil(Number(hardShort)||0));"
if text.count(reserve_only_anchor)!=1:
    raise SystemExit(f'reserve-only display anchor count={text.count(reserve_only_anchor)}')
text=text.replace(reserve_only_anchor,reserve_only_insert,1)

# 5) Left-side reserve explanations now match the actual tools-first split.
sub_once(
    r"    const reserveHint=\$\('s2SkillReserveHint'\);.*?    const displayedSand=Number\(resources\.sandTotal\?\?resources\.sand\)\|\|0;",
    r'''    const reserveHint=$('s2SkillReserveHint');
    if(reserveHint){
      if(cfg.key==='s1'&&(sr?.target||0)>0){
        reserveHint.hidden=false;
        const split=toolsFirstReserveSplit('essence',sr.target,displayedEssence,resources,cfg);
        const toolPart=split.toolRuns?`${fmt(split.toolRuns)} Knuckles first`:'';
        const rawPart=split.rawHeld?`${fmt(split.rawHeld)} raw Essence`:'';
        const parts=[toolPart,rawPart].filter(Boolean).join(' + ');
        const short=split.shortfall>0?` · reserve still short ${fmt(split.shortfall)} Essence before extra purchases`:'';
        reserveHint.innerHTML=`<b>S2 Skill reserve:</b> ${fmt(sr.target)} Essence-equivalent for all 8 skills Lv.100 → Lv.${sr.targetLevel}${parts?` · ${parts}`:''}${short}. Material Realm tools cover the reserve first; raw Essence is held only for any remainder.`;
      }else if(cfg.key==='s1'){
        reserveHint.hidden=false;
        reserveHint.innerHTML = !$('reserveS2Essence')?.checked
          ? '<b>S2 Skill reserve:</b> off · raw Essence is spent first; Knuckles stay banked unless raw runs out.'
          : '<b>S2 Skill reserve:</b> 0 · enable held Bed EXP to reserve startup skill materials automatically.';
      }else reserveHint.hidden=true;
    }
    const relicReserveHint=$('s2RelicReserveHint');
    if(relicReserveHint){
      if(cfg.key==='s1'){
        const rr=resources.s2RelicSandReserve||season2RelicSandReserve(cfg);
        relicReserveHint.hidden=false;
        if(!$('reserveS2Sand')?.checked){
          relicReserveHint.innerHTML='<b>S2 Relic Sand reserve:</b> off · raw Sand is spent first; Shovels stay banked unless raw runs out.';
        }else{
          const split=toolsFirstReserveSplit('sand',rr.target,Number(resources.sandTotal??resources.sand)||0,resources,cfg);
          const toolPart=split.toolRuns?`${fmt(split.toolRuns)} Shovels first`:'';
          const rawPart=split.rawHeld?`${fmt(split.rawHeld)} raw Sand`:'';
          const parts=[toolPart,rawPart].filter(Boolean).join(' + ');
          const short=split.shortfall>0?` · reserve still short ${fmt(split.shortfall)} Sand before extra purchases`:'';
          relicReserveHint.innerHTML=`<b>S2 Relic Sand reserve:</b> ${fmt(rr.target)} Sand-equivalent protected for one full +${rr.fromLevel} → +${rr.toLevel} round across all 20 relics${parts?` · ${parts}`:''}${short}. Material Realm tools cover the reserve first; raw Sand is held only for any remainder.`;
        }
      }else relicReserveHint.hidden=true;
    }
    const displayedSand=Number(resources.sandTotal??resources.sand)||0;''',
    'reserve explanation block'
)

# 6) The Material Realm panel's "S2 reserve" counts come from the chosen plan, not stale
#    pre-plan metadata. These counts include the tool-first reservation actually enforced.
old_protected="    const protectedKnuckles=Math.max(0,Math.floor(Number(resources.s2SkillReserve?.knucklesReserved)||0));\n    const protectedShovels=Math.max(0,Math.floor(Number(resources.s2RelicSandReserve?.shovelsReserved)||0));"
new_protected="    const protectedKnuckles=Math.max(0,Math.floor(Number(plan.realm?.essence?.reserveRuns)||0));\n    const protectedShovels=Math.max(0,Math.floor(Number(plan.realm?.sand?.reserveRuns)||0));"
if text.count(old_protected)!=1:
    raise SystemExit(f'protected tool counts block count={text.count(old_protected)}')
text=text.replace(old_protected,new_protected,1)

# Update stale optimizer comments/phrasing without changing any S2 scoring or yield constants.
text=text.replace('Raw and carried tools can trade off: whichever combination leaves\n     the most current-season material available while still funding the reserve is used.',
                  'Carried/planned Realm tools are assigned to enabled S2 reserves first; raw is held only for the remaining reserve gap.')

PATH.write_text(text,encoding='utf-8')
print('Applied tools-first S2 reserve accounting; S2 scoring/yield constants unchanged.')
