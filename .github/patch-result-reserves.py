from pathlib import Path
import re
import subprocess

p=Path('index.html')
s=p.read_text(encoding='utf-8')

old_apply="""  function applySeasonTransitionReserves(resources,cfg=activeCalcConfig()){
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
  }"""
new_apply="""  function applySeasonTransitionReserves(resources,cfg=activeCalcConfig()){
    const skillBase=season2SkillEssenceReserve(cfg);
    const relicBase=season2RelicSandReserve(cfg);
    const treatBase=season2FantomonTreatReserve(cfg);
    const essenceTotal=Math.max(0,Number(resources.essence)||0);
    const sandTotal=Math.max(0,Number(resources.sand)||0);
    const treatTotal=Math.max(0,Number(resources.treat)||0);

    // RESERVE_REQUIREMENT_FIXED_V1: the configured rollover requirement never shrinks just
    // because the account is currently short. Coverage and shortfall are tracked separately.
    const skillSplit=toolsFirstReserveSplit('essence',skillBase.target,essenceTotal,resources,cfg);
    const relicSplit=toolsFirstReserveSplit('sand',relicBase.target,sandTotal,resources,cfg);
    const treatCovered=Math.min(treatTotal,Math.max(0,Number(treatBase.target)||0));
    const skillMeta={...skillBase,rawEssence:skillSplit.rawHeld,knucklesReserved:skillSplit.toolRuns,knuckleEssence:skillSplit.toolValue,shortfall:skillSplit.shortfall};
    const relicMeta={...relicBase,rawSand:relicSplit.rawHeld,shovelsReserved:relicSplit.toolRuns,shovelSand:relicSplit.toolValue,shortfall:relicSplit.shortfall};
    const treatMeta={...treatBase,rawTreats:treatCovered,shortfall:Math.max(0,treatBase.target-treatCovered)};

    return {...resources,
      essenceTotal,essenceReserve:0,s2SkillReserve:skillMeta,essence:essenceTotal,
      sandTotal,sandReserve:0,s2RelicSandReserve:relicMeta,sand:sandTotal,
      treatTotal,treatReserve:0,s2FantomonTreatReserve:treatMeta,treat:treatTotal
    };
  }"""
if old_apply not in s:
    raise SystemExit('applySeasonTransitionReserves block not found')
s=s.replace(old_apply,new_apply,1)

old_balance="""  // TOOLS_FIRST_RAW_RESERVE_DISPLAY_V6: Remaining is strictly RAW material left
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
  }"""
new_balance="""  // RESERVE_REQUIREMENT_DISPLAY_V1: Remaining is post-plan raw material. The configured
  // reserve target is a fixed requirement; never relabel a partial balance as a smaller reserve.
  // Instead show how much of that fixed target is covered and the real shortfall.
  function setReservedRawRemaining(id,cost,resources,key,unitLabel=''){
    const el=$(id); if(!el) return;
    el.classList.remove('shortfallCount','shortfallBreakdown','reserveHasGap');
    el.classList.add('rawRemaining');
    const available=Math.max(0,Number(resources?.[key])||0);
    const left=Math.max(0,Math.floor(available-(Number(cost)||0)+1e-9));
    const reserveTarget=Math.max(0,Math.floor(reserveTargetFor(key,resources)+1e-9));
    const unit=unitLabel?` ${unitLabel}`:'';
    let covered=0,shortfall=0,detail='';

    if(reserveTarget>0 && (key==='essence'||key==='sand')){
      const split=toolsFirstReserveSplit(key,reserveTarget,left,resources,activeCalcConfig());
      covered=Math.min(reserveTarget,Math.floor(split.toolValue+split.rawHeld+1e-9));
      shortfall=Math.max(0,reserveTarget-covered);
      const parts=[];
      if(split.toolValue>0) parts.push(`${fmt(Math.floor(split.toolValue))} via ${key==='essence'?'Knuckles':'Shovels'}`);
      if(split.rawHeld>0) parts.push(`${fmt(Math.floor(split.rawHeld))} raw`);
      detail=parts.length?` · ${parts.join(' + ')}`:'';
    }else if(reserveTarget>0){
      covered=Math.min(left,reserveTarget);
      shortfall=Math.max(0,reserveTarget-covered);
    }

    el.hidden=false;
    el.innerHTML=`<span class="resourceRemainingLine">Remaining: <b>${fmt(left)}</b>${unit}</span>`+
      (reserveTarget>0?`<span class="reserveRequirementLine${shortfall>0?' reserveShort':''}">Reserve target: <b>${fmt(reserveTarget)}</b>${unit} · ${fmt(covered)} covered${detail}${shortfall>0?` · <strong>${fmt(shortfall)} short</strong>`:' · ✓ protected'}</span>`:'');
    el.classList.toggle('reserveHasGap',shortfall>0);
  }"""
if old_balance not in s:
    raise SystemExit('setReservedRawRemaining block not found')
s=s.replace(old_balance,new_balance,1)

marker='RESULT_CARD_POLISH_AND_FIXED_RESERVES_V1'
if marker not in s:
    css='''
<style id="result-card-polish-v1">
/* RESULT_CARD_POLISH_AND_FIXED_RESERVES_V1 */
.calcResults{border-radius:22px!important;padding:24px!important}
.calcEyebrow{font-size:9px!important;letter-spacing:.12em!important}
.starTotal{font-size:52px!important;margin:8px 0 10px!important}
.starTotal small{font-size:15px!important;color:var(--gold)!important;font-weight:800!important}
.resultScoreLine{border:1px solid var(--line)!important;border-radius:12px!important;padding:11px 12px!important;margin:0 0 18px!important}
.optimizerTargets{gap:8px!important;margin-bottom:10px!important}
.optimizerTargets span{min-height:62px!important;padding:11px 12px!important}
.optimizerTargets b{font-size:17px!important;margin-top:2px!important}
.suggestedGear{gap:6px!important;margin-bottom:18px!important}
.suggestedGear span{min-height:62px!important;border-radius:10px!important;padding:9px 5px!important}
.suggestedGear b{font-size:17px!important}
.planCosts,.planCostsFour{gap:9px!important;margin:0 0 20px!important}
.planCosts>span{border-radius:12px!important;padding:12px 13px!important;gap:4px!important;min-height:106px!important;align-content:start}
.planCosts>span>b:before{content:'Needed';display:block;color:var(--muted);font-size:7px;line-height:1.2;text-transform:uppercase;letter-spacing:.07em;font-weight:800;margin-bottom:2px}
.planCosts>span>b{font-size:19px!important;line-height:1.15}
.planCosts small.rawRemaining{display:grid!important;gap:4px!important;margin-top:3px!important;color:var(--status-positive,var(--green))!important}
.planCosts .resourceRemainingLine{display:block;color:var(--status-positive,var(--green));font-size:10px;text-transform:none;font-weight:800}
.planCosts .resourceRemainingLine b{font-size:inherit!important;color:inherit}
.planCosts .reserveRequirementLine{display:block;border-top:1px solid var(--line);padding-top:6px;margin-top:2px;color:var(--secondary-text);font-size:8px;line-height:1.4;text-transform:none;font-weight:750}
.planCosts .reserveRequirementLine b{font-size:inherit!important;color:var(--ink)}
.planCosts .reserveRequirementLine.reserveShort,.planCosts .reserveRequirementLine.reserveShort strong{color:var(--status-negative,var(--red))!important}
.planCosts small.reserveHasGap{color:var(--status-negative,var(--red))!important}
.resultDetails{margin-top:4px!important}
@media(max-width:700px){.calcResults{padding:18px!important;border-radius:18px!important}.starTotal{font-size:46px!important}.planCosts>span{min-height:0!important}}
</style>
'''
    s=s.replace('</head>',css+'</head>',1)

p.write_text(s,encoding='utf-8')

# Validate every inline script independently so separate global script scopes do not conflict.
text=p.read_text(encoding='utf-8')
scripts=re.findall(r'<script(?:\s[^>]*)?>(.*?)</script>',text,re.S|re.I)
if not scripts:
    raise SystemExit('No inline scripts found')
for i,js in enumerate(scripts):
    tmp=Path(f'/tmp/charming-inline-{i}.js')
    tmp.write_text(js,encoding='utf-8')
    subprocess.run(['node','--check',str(tmp)],check=True)
print(f'Validated {len(scripts)} inline scripts')
