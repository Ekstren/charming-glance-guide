from pathlib import Path
import re

PATH=Path('index.html')
text=PATH.read_text(encoding='utf-8')
MARKER='GATED_RAW_FIRST_OPTIMIZER_V1'
if MARKER in text:
    print('Gated raw-first optimizer already applied.')
    raise SystemExit(0)


def sub_once(pattern,repl,label,flags=re.S):
    global text
    updated,count=re.subn(pattern,repl,text,count=1,flags=flags)
    if count!=1:
        raise SystemExit(f'{label}: expected 1 match, got {count}')
    text=updated

# 1) Fully funded CURRENT-SEASON capped resources have no remaining S1 scarcity.
#    S2 reserves are removed before this test. This makes safe raw Essence/Sand/Treats
#    substitute for open-ended Ore before the optimizer reaches for Realm tools.
old_floor="  const SURPLUS_ACQUISITION_FLOORS={ore:1.00,essence:0.10,sand:0.35,treat:0.35};"
new_floor="  /* GATED_RAW_FIRST_OPTIMIZER_V1: once a capped category's remaining S1 headroom is fully funded by SAFE RAW, spending that raw on its own score progression has zero additional S1 opportunity cost. */\n  const SURPLUS_ACQUISITION_FLOORS={ore:1.00,essence:0.00,sand:0.00,treat:0.00};"
if text.count(old_floor)!=1:
    raise SystemExit(f'surplus floor count={text.count(old_floor)}')
text=text.replace(old_floor,new_floor,1)

# 2) Raw-stage scarcity deliberately excludes unreserved Realm tools. Realm entries are a
#    later gate. Enabled S2 Essence/Sand reserves still assign tools FIRST, then withhold only
#    the raw remainder. Fantomon Treats participate in the same gate as raw-only material;
#    there is no Treat Realm tool, so an enabled Treat reserve remains a hard raw reserve.
anchor="  function reserveAdjustedAcquisitionSupply(key,resources,cfg=activeCalcConfig()){"
if text.count(anchor)!=1:
    raise SystemExit(f'reserveAdjustedAcquisitionSupply anchor count={text.count(anchor)}')
helper=r'''  function rawOnlyAcquisitionSupply(key,resources,cfg=activeCalcConfig()){
    const raw=Math.max(0,Number(resources?.[key])||0);
    const reserve=Math.max(0,reserveTargetFor(key,resources,cfg));
    if(key==='treat') return Math.max(0,raw-reserve);
    if(key==='essence'||key==='sand'){
      if(reserve<=0) return raw;
      const split=toolsFirstReserveSplit(key,reserve,raw,resources,cfg);
      // Existing/planned Realm tools cover the enabled S2 reserve first. Only the raw
      // remainder is withheld from the current-season raw-only optimizer.
      if(split.shortfall>0.5) return 0;
      return Math.max(0,raw-split.rawHeld);
    }
    return raw;
  }

'''
text=text.replace(anchor,helper+anchor,1)

old_supply=r'''    resources.acquisitionHeadroomCosts=headroomCosts||{};
    resources.acquisitionSupplyEquiv={
      essence:reserveAdjustedAcquisitionSupply('essence',resources,cfg),
      sand:reserveAdjustedAcquisitionSupply('sand',resources,cfg),
      treat:reserveAdjustedAcquisitionSupply('treat',resources,cfg)
    };'''
new_supply=r'''    resources.acquisitionHeadroomCosts=headroomCosts||{};
    // Gate 2 is RAW ONLY. Realm tools do not make a capped category look overfunded here;
    // they remain banked until no raw-only score plan can reach the requested target.
    resources.acquisitionSupplyEquiv={
      essence:rawOnlyAcquisitionSupply('essence',resources,cfg),
      sand:rawOnlyAcquisitionSupply('sand',resources,cfg),
      treat:rawOnlyAcquisitionSupply('treat',resources,cfg)
    };'''
if text.count(old_supply)!=1:
    raise SystemExit(f'acquisition supply block count={text.count(old_supply)}')
text=text.replace(old_supply,new_supply,1)

# 3) Make the resource gates explicit instead of relying on comparator side-effects.
#    Stage 0 = raw-only S1 plan (reserved banked tools do not count as S1 usage).
#    Stage 1 = unreserved existing/projected Realm tools are required for S1.
#    Stage 2 = additional paid Realm refreshes are required (including reserve top-ups).
anchor2="  function betterFeasibleCandidate(candidate,best){"
if text.count(anchor2)!=1:
    raise SystemExit(f'betterFeasibleCandidate anchor count={text.count(anchor2)}')
stage_helper=r'''  function candidateRealmStage(candidate){
    const realms=['ore','essence','sand'].map(k=>candidate?.realm?.[k]).filter(Boolean);
    // A Treat shortage is a hard resource failure because there is no Fantomon-Treat
    // Material Realm tool. Diagnostics therefore rank it after all actually fundable stages.
    if(Math.max(0,Number(candidate?.treatShortfall)||0)>0.5) return 3;
    if(realms.some(x=>Math.max(0,Number(x?.packs)||0)>0 || Math.max(0,Number(x?.paidRunsUsed)||0)>0)) return 2;
    const usesS1Tools=realms.some(x=>{
      const planRuns=Number.isFinite(Number(x?.planRuns)) ? Number(x.planRuns) : Number(x?.runsUsed)||0;
      return planRuns>0;
    });
    return usesS1Tools?1:0;
  }

'''
text=text.replace(anchor2,stage_helper+anchor2,1)

# 4) Replace feasible comparator with strict gate ordering, then the raw economics.
sub_once(
    r"  function betterFeasibleCandidate\(candidate,best\)\{.*?\n  \}\n\n  function betterDiagnosticCandidate",
    r'''  function betterFeasibleCandidate(candidate,best){
    if(!best) return true;

    // STRICT GATES: raw-only beats existing Realm-tool use; existing Realm-tool use beats
    // buying additional refreshes. Reserved banked tools are not counted as S1 tool usage.
    const cStage=candidateRealmStage(candidate),bStage=candidateRealmStage(best);
    if(cStage<bStage) return true;
    if(cStage>bStage) return false;

    // Paid Realm purchases are the final fallback. Inside that stage, Dawnium cost wins.
    if(cStage===2){
      if(candidate.dawniumCost<best.dawniumCost-1e-9) return true;
      if(candidate.dawniumCost>best.dawniumCost+1e-9) return false;
    }

    // Within a tool-using stage, consume the fewest actual S1 Realm entries before comparing
    // raw economics. This never unlocks a reserved tool: reserveAwareRealmTopupFor already
    // allocates those entries to S2 before exposing any S1 plan runs.
    if(cStage>=1){
      const toolCmp=betterToolBurden(candidate,best);
      if(toolCmp!==null) return toolCmp;
    }

    // Raw-stage economics: fully funded capped raw (Skills / Relics / Fantomons) is allowed
    // to replace open-ended Gear/Ore. Preserve Ore applies the existing +50% Ore premium.
    if(candidate.seasonKey==='s1' || best.seasonKey==='s1'){
      const cm=candidateResourceMetric(candidate),bm=candidateResourceMetric(best);
      if(cm<bm-1e-9) return true;
      if(cm>bm+1e-9) return false;
      if(optimizerMode()==='preserve'){
        if((candidate.oreCost||0)<(best.oreCost||0)) return true;
        if((candidate.oreCost||0)>(best.oreCost||0)) return false;
        if((candidate.bankedHammersUsed||0)<(best.bankedHammersUsed||0)) return true;
        if((candidate.bankedHammersUsed||0)>(best.bankedHammersUsed||0)) return false;
      }
    }

    // Do not spend material just for meaningless overscore once strategic cost is tied.
    return candidate.overshoot<best.overshoot-1e-9||
      (Math.abs(candidate.overshoot-best.overshoot)<1e-9&&candidate.maxShare<best.maxShare-1e-9)||
      (Math.abs(candidate.overshoot-best.overshoot)<1e-9&&Math.abs(candidate.maxShare-best.maxShare)<1e-9&&candidate.sumShare<best.sumShare-1e-9);
  }

  function betterDiagnosticCandidate''',
    'feasible gated comparator'
)

# 5) Diagnostics keep hard feasibility first, then use the same gate order/economics.
sub_once(
    r"  function betterDiagnosticCandidate\(candidate,best\)\{.*?\n  \}\n\n  // Find both the cheapest fundable plan",
    r'''  function betterDiagnosticCandidate(candidate,best){
    if(!best) return true;
    if(candidate.hardShortfall<best.hardShortfall-0.5) return true;
    if(Math.abs(candidate.hardShortfall-best.hardShortfall)>0.5) return false;
    if(candidate.realmOverflow<best.realmOverflow) return true;
    if(candidate.realmOverflow!==best.realmOverflow) return false;
    if(candidate.remainingAfterMax<best.remainingAfterMax-0.5) return true;
    if(Math.abs(candidate.remainingAfterMax-best.remainingAfterMax)>0.5) return false;

    const cStage=candidateRealmStage(candidate),bStage=candidateRealmStage(best);
    if(cStage<bStage) return true;
    if(cStage>bStage) return false;
    if(cStage===2){
      if(candidate.dawniumCost<best.dawniumCost-1e-9) return true;
      if(candidate.dawniumCost>best.dawniumCost+1e-9) return false;
    }
    if(cStage>=1){
      const toolCmp=betterToolBurden(candidate,best);
      if(toolCmp!==null) return toolCmp;
    }

    if(candidate.seasonKey==='s1' || best.seasonKey==='s1'){
      const cm=candidateResourceMetric(candidate),bm=candidateResourceMetric(best);
      if(cm<bm-1e-9) return true;
      if(cm>bm+1e-9) return false;
      if(optimizerMode()==='preserve'){
        if((candidate.oreCost||0)<(best.oreCost||0)) return true;
        if((candidate.oreCost||0)>(best.oreCost||0)) return false;
      }
    }
    return candidate.overshoot<best.overshoot;
  }

  // Find both the cheapest fundable plan''',
    'diagnostic gated comparator'
)

# 6) Explain the new policy in the toggle itself. Keep Preserve Ore at +50% for now.
old_preserve="      ? 'Joint Cart + shared-Stamina efficiency with funded-cap coverage, plus a +50% Ore premium for Gear runway.'"
new_preserve="      ? 'Raw-first gates: reserve S2 tools first, spend safe capped raw before Realm tools, then apply a +50% Ore premium for Gear runway.'"
if text.count(old_preserve)==1:
    text=text.replace(old_preserve,new_preserve,1)
old_acq="      : 'Joint Cart + shared-Stamina efficiency; capped resources get cheaper as their reachable cap becomes funded.';"
new_acq="      : 'Raw-first gates: reserve S2 tools first, spend fully funded capped raw before Realm tools, then minimize replacement effort.';"
if text.count(old_acq)==1:
    text=text.replace(old_acq,new_acq,1)

# Treat reserve explanation: explicitly put Fantomon Treats in the same gated policy while
# acknowledging that it has no Realm-tool conversion path.
old_treat="          treatReserveHint.innerHTML=`<b>S2 Fantomon Treat reserve:</b> ${fmt(tr.target)} basic-equivalent protected for all 4 Fantomons Lv.${tr.fromLevel} → Lv.${tr.toLevel} · ≈${fmtCompact(tr.expEquivalent)} Fantomon EXP${short}. Treats are used by the S1 plan first; whatever remains must still cover this S2 reserve target.`;"
new_treat="          treatReserveHint.innerHTML=`<b>S2 Fantomon Treat reserve:</b> ${fmt(tr.target)} basic-equivalent protected for all 4 Fantomons Lv.${tr.fromLevel} → Lv.${tr.toLevel} · ≈${fmtCompact(tr.expEquivalent)} Fantomon EXP${short}. Treats follow the same raw-first gate, but there is no Treat Realm tool, so this enabled reserve remains raw and untouchable.`;"
if text.count(old_treat)==1:
    text=text.replace(old_treat,new_treat,1)

PATH.write_text(text,encoding='utf-8')
print('Applied gated raw-first optimizer with Treats, capped-raw substitution, Realm stages, and +50% Preserve Ore premium.')
