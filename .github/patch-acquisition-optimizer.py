from pathlib import Path

PATH = Path('index.html')
text = PATH.read_text(encoding='utf-8')
MARKER = 'ACQUISITION_OPTIMIZER_V1'

if MARKER in text:
    print('Acquisition optimizer already applied.')
    raise SystemExit(0)


def replace_once(old: str, new: str, label: str):
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly 1 match, found {count}')
    text = text.replace(old, new, 1)

# Rename the neutral control and make both strategies explain their actual objective.
replace_once(
'''          <div class="optimizerModeCopy"><b>Optimization priority</b><small id="optimizerModeNote">Protect Ore/Hammers after the target and hard S2 reserves are safe.</small></div>
          <div class="optimizerModeToggle" role="group" aria-label="Optimization priority">
            <button type="button" data-optimizer-mode="preserve" aria-pressed="true">Preserve Ore</button>
            <button type="button" data-optimizer-mode="balanced" aria-pressed="false">Balanced resources</button>
          </div>
''',
'''          <div class="optimizerModeCopy"><b>Optimization priority</b><small id="optimizerModeNote">Use acquisition effort, with an extra future-value premium on Ore/Hammers.</small></div>
          <div class="optimizerModeToggle" role="group" aria-label="Optimization priority">
            <button type="button" data-optimizer-mode="preserve" aria-pressed="true">Preserve Ore</button>
            <button type="button" data-optimizer-mode="acquisition" aria-pressed="false">Acquisition Efficient</button>
          </div>
''',
'optimizer mode UI',
)

old_runtime = '''  const optimizerMode = () => $('optimizerMode')?.value === 'balanced' ? 'balanced' : 'preserve';
  function updateOptimizerModeUI(){
    const mode=optimizerMode();
    const row=$('optimizerModeRow');
    if(row) row.hidden=activeCalcConfig().key!=='s1';
    document.querySelectorAll('[data-optimizer-mode]').forEach(btn=>{
      const active=btn.dataset.optimizerMode===mode;
      btn.classList.toggle('active',active);
      btn.setAttribute('aria-pressed',active?'true':'false');
    });
    const note=$('optimizerModeNote');
    if(note) note.textContent=mode==='preserve'
      ? 'Protect Ore/Hammers after the target and hard S2 reserves are safe.'
      : 'Treat Ore like the other spendable resources and use the generic balanced-resource tie breaker.';
  }
  document.querySelectorAll('[data-optimizer-mode]').forEach(btn=>btn.addEventListener('click',()=>{
    const input=$('optimizerMode');
    if(!input) return;
    input.value=btn.dataset.optimizerMode==='balanced'?'balanced':'preserve';
    updateOptimizerModeUI();
    saveState();
    scheduleCalculatorUpdate(0);
  }));
'''
new_runtime = '''  const optimizerMode = () => {
    const raw=$('optimizerMode')?.value;
    // Migrate the short-lived Balanced mode to the new acquisition-efficiency model.
    return raw==='acquisition'||raw==='balanced' ? 'acquisition' : 'preserve';
  };
  function updateOptimizerModeUI(){
    const mode=optimizerMode();
    const input=$('optimizerMode');
    if(input && input.value==='balanced') input.value='acquisition';
    const row=$('optimizerModeRow');
    if(row) row.hidden=activeCalcConfig().key!=='s1';
    document.querySelectorAll('[data-optimizer-mode]').forEach(btn=>{
      const active=btn.dataset.optimizerMode===mode;
      btn.classList.toggle('active',active);
      btn.setAttribute('aria-pressed',active?'true':'false');
    });
    const note=$('optimizerModeNote');
    if(note) note.textContent=mode==='preserve'
      ? 'Acquisition effort + 75% Ore premium for Gear runway; strong Ore preference, no longer absolute.'
      : 'Minimize estimated replacement effort using Cart/hr + one 5-Stamina map node per hour; no special Ore premium.';
  }
  document.querySelectorAll('[data-optimizer-mode]').forEach(btn=>btn.addEventListener('click',()=>{
    const input=$('optimizerMode');
    if(!input) return;
    input.value=btn.dataset.optimizerMode==='acquisition'?'acquisition':'preserve';
    updateOptimizerModeUI();
    saveState();
    scheduleCalculatorUpdate(0);
  }));
'''
replace_once(old_runtime, new_runtime, 'optimizer runtime')

# Insert a resource-accrual metric before candidate construction. One hour naturally
# regenerates 5 Stamina, i.e. one 5-Stamina map node, while Cart accrues in parallel.
# For speed inside the large plan search we use focused replacement-hours per material;
# this is transparent, monotonic, and materially closer to reacquisition cost than
# percentage-of-inventory balancing. Treats use the entered Cart rate; when that is 0,
# projected spendable Treats over the remaining horizon provide a scarcity fallback.
anchor = '''  function makePlanCandidate(go,so,ro,fo,score,desired,resources,realms){
'''
helper = '''  const ORE_PRESERVE_PREMIUM=0.75; // +75% strategic value, bounded rather than absolute.
  function acquisitionEffortFor(costs,resources,cfg=activeCalcConfig()){
    const map=resources?.yields?.map||cfg.map||{};
    const horizon=Math.max(24,Number(resources?.cartHours)||24);
    const projectedTreat=Math.max(0,Number(resources?.treat)||0);
    const enteredTreatRate=Math.max(0,n('treatRate'));
    const fallbackTreatRate=projectedTreat>0?projectedTreat/horizon:0;
    const rates={
      ore:Math.max(0,n('oreRate'))+Math.max(0,Number(map.ore)||0),
      essence:Math.max(0,n('essenceRate'))+Math.max(0,Number(map.essence)||0),
      sand:Math.max(0,n('sandRate'))+Math.max(0,Number(map.sand)||0),
      treat:enteredTreatRate>0?enteredTreatRate:fallbackTreatRate
    };
    const safeHours=(amount,rate)=>{
      const a=Math.max(0,Number(amount)||0),r=Math.max(0,Number(rate)||0);
      if(a<=0) return 0;
      return r>0?a/r:1e9;
    };
    const oreHours=safeHours(costs.ore,rates.ore);
    const essenceHours=safeHours(costs.essence,rates.essence);
    const sandHours=safeHours(costs.sand,rates.sand);
    const treatHours=safeHours(costs.treat,rates.treat);
    const hours=oreHours+essenceHours+sandHours+treatHours;
    return {hours,oreHours,essenceHours,sandHours,treatHours,treatFallback:enteredTreatRate<=0&&fallbackTreatRate>0};
  }
  function candidateResourceMetric(candidate){
    const base=Number(candidate?.acquisitionHours);
    if(!Number.isFinite(base)) return 1e18;
    return optimizerMode()==='preserve'
      ? Number(candidate?.preserveAcquisitionScore)||base
      : base;
  }

'''+anchor
replace_once(anchor, helper, 'acquisition helper insertion')

# Candidate metrics.
old_candidate_metrics = '''    // S1 opportunity cost AFTER the hard S2 reserves are removed from the spendable budget.
    // Surplus Essence is cheapest to burn, Treats next, then surplus Sand. Ore/Hammers are
    // preserved hardest because Gear has the longest uncapped progression runway next season.
    const s1ResourcePolicyScore=essenceShare*0.20+treatShare*0.45+sandShare*0.75+oreShare*1.20;
    return {
'''
new_candidate_metrics = '''    const acquisition=acquisitionEffortFor({ore:go.oreCost,essence:so.cost,sand:ro.cost,treat:fo.cost},resources,activeCalcConfig());
    const preserveAcquisitionScore=acquisition.hours+acquisition.oreHours*ORE_PRESERVE_PREMIUM;
    return {
'''
replace_once(old_candidate_metrics, new_candidate_metrics, 'candidate metric setup')
replace_once(
'''      oreShare,essenceShare,sandShare,treatShare,refinedShare,s1ResourcePolicyScore,
''',
'''      oreShare,essenceShare,sandShare,treatShare,refinedShare,
      acquisitionHours:acquisition.hours,oreAcquisitionHours:acquisition.oreHours,preserveAcquisitionScore,
''',
'candidate metric fields',
)

# Replace the old absolute Ore-first feasible comparator with the bounded acquisition model.
old_feasible_policy = '''    // Late-S1 policy. S2 Essence and one full S2 Relic Sand round are already protected,
    // so compare only the remaining spendable surplus. Lower is better:
    // Essence -> Treats -> surplus Sand -> Ore (most protected).
    if(optimizerMode()==='preserve' && (candidate.seasonKey==='s1' || best.seasonKey==='s1')){
      // After hard S2 reserves are protected, Ore is the resource with the longest useful runway.
      // At equal paid-Realm cost, minimize actual Ore required before balancing the other surpluses.
      if(candidate.oreCost<best.oreCost-0.5) return true;
      if(candidate.oreCost>best.oreCost+0.5) return false;
      const cp=Number(candidate.s1ResourcePolicyScore)||0;
      const bp=Number(best.s1ResourcePolicyScore)||0;
      if(cp<bp-1e-9) return true;
      if(cp>bp+1e-9) return false;

      // Exact ties: preserve Hammers/Ore first. Reserved Shovels/Knuckles never enter this pool;
      // surplus Knuckles/Shovels are fair game for current-season score.
      if((candidate.bankedHammersUsed||0)<(best.bankedHammersUsed||0)) return true;
      if((candidate.bankedHammersUsed||0)>(best.bankedHammersUsed||0)) return false;
      if(candidate.skillAdds>best.skillAdds) return true;
      if(candidate.skillAdds<best.skillAdds) return false;
      if(candidate.fantoAdds>best.fantoAdds) return true;
      if(candidate.fantoAdds<best.fantoAdds) return false;
      if(candidate.relicAdds>best.relicAdds) return true;
      if(candidate.relicAdds<best.relicAdds) return false;
      if((candidate.bankedKnucklesUsed||0)>(best.bankedKnucklesUsed||0)) return true;
      if((candidate.bankedKnucklesUsed||0)<(best.bankedKnucklesUsed||0)) return false;
      if((candidate.bankedShovelsUsed||0)>(best.bankedShovelsUsed||0)) return true;
      if((candidate.bankedShovelsUsed||0)<(best.bankedShovelsUsed||0)) return false;
    }

'''
new_feasible_policy = '''    // After paid-Realm cost is tied, compare modeled replacement effort. Preserve Ore uses
    // the same acquisition model with a bounded +75% Ore premium rather than an absolute veto.
    if(candidate.seasonKey==='s1' || best.seasonKey==='s1'){
      const cm=candidateResourceMetric(candidate),bm=candidateResourceMetric(best);
      if(cm<bm-1e-9) return true;
      if(cm>bm+1e-9) return false;
      if(optimizerMode()==='preserve'){
        if((candidate.bankedHammersUsed||0)<(best.bankedHammersUsed||0)) return true;
        if((candidate.bankedHammersUsed||0)>(best.bankedHammersUsed||0)) return false;
      }
    }

'''
replace_once(old_feasible_policy, new_feasible_policy, 'feasible resource policy')

old_diag_policy = '''    if(optimizerMode()==='preserve' && (candidate.seasonKey==='s1' || best.seasonKey==='s1')){
      if(candidate.oreCost<best.oreCost-0.5) return true;
      if(candidate.oreCost>best.oreCost+0.5) return false;
      const cp=Number(candidate.s1ResourcePolicyScore)||0;
      const bp=Number(best.s1ResourcePolicyScore)||0;
      if(cp<bp-1e-9) return true;
      if(cp>bp+1e-9) return false;
      if((candidate.bankedHammersUsed||0)<(best.bankedHammersUsed||0)) return true;
      if((candidate.bankedHammersUsed||0)>(best.bankedHammersUsed||0)) return false;
      if(candidate.skillAdds>best.skillAdds) return true;
      if(candidate.skillAdds<best.skillAdds) return false;
      if(candidate.fantoAdds>best.fantoAdds) return true;
      if(candidate.fantoAdds<best.fantoAdds) return false;
      if(candidate.relicAdds>best.relicAdds) return true;
      if(candidate.relicAdds<best.relicAdds) return false;
      if((candidate.bankedKnucklesUsed||0)>(best.bankedKnucklesUsed||0)) return true;
      if((candidate.bankedKnucklesUsed||0)<(best.bankedKnucklesUsed||0)) return false;
      if((candidate.bankedShovelsUsed||0)>(best.bankedShovelsUsed||0)) return true;
      if((candidate.bankedShovelsUsed||0)<(best.bankedShovelsUsed||0)) return false;
    }

'''
new_diag_policy = '''    if(candidate.seasonKey==='s1' || best.seasonKey==='s1'){
      const cm=candidateResourceMetric(candidate),bm=candidateResourceMetric(best);
      if(cm<bm-1e-9) return true;
      if(cm>bm+1e-9) return false;
      if(optimizerMode()==='preserve'){
        if((candidate.bankedHammersUsed||0)<(best.bankedHammersUsed||0)) return true;
        if((candidate.bankedHammersUsed||0)>(best.bankedHammersUsed||0)) return false;
      }
    }

'''
replace_once(old_diag_policy, new_diag_policy, 'diagnostic resource policy')

# Diagnostic candidates are not built by makePlanCandidate, so attach the same metrics explicitly.
old_diag_setup = '''          const diagOreShare=resources.ore>0?go.oreCost/resources.ore:(go.oreCost>0?go.oreCost/100000:0),diagEssenceShare=resources.essence>0?so.cost/resources.essence:(so.cost>0?so.cost/100000:0),diagSandShare=resources.sand>0?ro.cost/resources.sand:(ro.cost>0?ro.cost/100000:0),diagTreatShare=resources.treat>0?fo.cost/resources.treat:(fo.cost>0?fo.cost/10000:0);
          const diagnostic={gear:go.target,skill:so.avg,relic:ro.avg,fanto:fo.avg,skillLevels:so.levels,relicLevels:ro.levels,fantoLevels:fo.levels,oreCost:go.oreCost,essenceCost:so.cost,sandCost:ro.cost,treatCost:fo.cost,refinedCost:go.refinedCost,score,gearAdds:go.adds,skillAdds:so.adds,relicAdds:ro.adds,fantoAdds:fo.adds,overshoot:score-desired,dawniumCost,realmAttempts:realmPacks,realmPacks,oreShare:diagOreShare,essenceShare:diagEssenceShare,sandShare:diagSandShare,treatShare:diagTreatShare,s1ResourcePolicyScore:diagEssenceShare*0.20+diagTreatShare*0.45+diagSandShare*0.75+diagOreShare*1.20,bankedHammersUsed:(oreRealm.bankedUsed||0),bankedKnucklesUsed:(essenceRealm.bankedUsed||0),bankedShovelsUsed:(sandRealm.bankedUsed||0),bankedToolsUsed:(oreRealm.bankedUsed||0)+(essenceRealm.bankedUsed||0)+(sandRealm.bankedUsed||0),realmOverflow,remainingAfterMax,treatShortfall,refinedShortfall,hardShortfall,seasonKey:cfg.key,realmFeasible:allFeasible,realm:{days:realmDays,ore:oreRealm,essence:essenceRealm,sand:sandRealm}};
'''
new_diag_setup = '''          const diagOreShare=resources.ore>0?go.oreCost/resources.ore:(go.oreCost>0?go.oreCost/100000:0),diagEssenceShare=resources.essence>0?so.cost/resources.essence:(so.cost>0?so.cost/100000:0),diagSandShare=resources.sand>0?ro.cost/resources.sand:(ro.cost>0?ro.cost/100000:0),diagTreatShare=resources.treat>0?fo.cost/resources.treat:(fo.cost>0?fo.cost/10000:0);
          const diagAcquisition=acquisitionEffortFor({ore:go.oreCost,essence:so.cost,sand:ro.cost,treat:fo.cost},resources,cfg);
          const diagnostic={gear:go.target,skill:so.avg,relic:ro.avg,fanto:fo.avg,skillLevels:so.levels,relicLevels:ro.levels,fantoLevels:fo.levels,oreCost:go.oreCost,essenceCost:so.cost,sandCost:ro.cost,treatCost:fo.cost,refinedCost:go.refinedCost,score,gearAdds:go.adds,skillAdds:so.adds,relicAdds:ro.adds,fantoAdds:fo.adds,overshoot:score-desired,dawniumCost,realmAttempts:realmPacks,realmPacks,oreShare:diagOreShare,essenceShare:diagEssenceShare,sandShare:diagSandShare,treatShare:diagTreatShare,acquisitionHours:diagAcquisition.hours,oreAcquisitionHours:diagAcquisition.oreHours,preserveAcquisitionScore:diagAcquisition.hours+diagAcquisition.oreHours*ORE_PRESERVE_PREMIUM,bankedHammersUsed:(oreRealm.bankedUsed||0),bankedKnucklesUsed:(essenceRealm.bankedUsed||0),bankedShovelsUsed:(sandRealm.bankedUsed||0),bankedToolsUsed:(oreRealm.bankedUsed||0)+(essenceRealm.bankedUsed||0)+(sandRealm.bankedUsed||0),realmOverflow,remainingAfterMax,treatShortfall,refinedShortfall,hardShortfall,seasonKey:cfg.key,realmFeasible:allFeasible,realm:{days:realmDays,ore:oreRealm,essence:essenceRealm,sand:sandRealm}};
'''
replace_once(old_diag_setup, new_diag_setup, 'diagnostic acquisition metrics')

# Auto-Stamina convergence must rank its alternate stable states with the same strategy,
# otherwise an old absolute remaining-Ore tie break could undo the tuned plan comparator.
old_state_policy = '''        if(optimizerMode()==='preserve'){
          const cOre=(Number(state.resources.ore)||0)-(Number(cp.oreCost)||0);
          const bOre=(Number(best.resources.ore)||0)-(Number(bp.oreCost)||0);
          if(cOre>bOre+0.5) return true;
          if(cOre<bOre-0.5) return false;
        }
'''
new_state_policy = '''        if(cp.seasonKey==='s1'||bp.seasonKey==='s1'){
          const cm=candidateResourceMetric(cp),bm=candidateResourceMetric(bp);
          if(cm<bm-1e-9) return true;
          if(cm>bm+1e-9) return false;
        }
'''
replace_once(old_state_policy, new_state_policy, 'auto stamina state ranking')

# Keep the visible summary and methodology honest.
replace_once(
'''    const policy=optimizerMode()==='preserve'?'minimize Ore':'balance spendable resources';
''',
'''    const policy=optimizerMode()==='preserve'?'acquisition effort + 75% Ore premium':'minimize reacquisition effort';
''',
'optimizer summary label',
)

replace_once(
'''After those are protected, surplus Essence is cheapest to spend, then Treats, then surplus Sand, while Ore/Hammers are preserved most aggressively.''',
'''After those are protected, the Optimization priority decides the tie-break: Acquisition Efficient minimizes estimated replacement effort from the entered Cart rates plus the current map yield (one 5-Stamina node per natural hour); Preserve Ore uses the same acquisition model but applies a 75% strategic premium to Ore/Hammers because Gear has the broadest progression runway.''',
'methodology resource policy',
)

# Marker near the existing optimizer style block.
replace_once(
'''<style id="optimizer-priority-toggle-v1">\n/* OPTIMIZER_PRIORITY_TOGGLE_V1 */''',
'''<style id="optimizer-priority-toggle-v1">\n/* OPTIMIZER_PRIORITY_TOGGLE_V1 · ACQUISITION_OPTIMIZER_V1 */''',
'optimizer marker',
)

PATH.write_text(text, encoding='utf-8')
print('Applied acquisition-efficiency optimizer and bounded Ore premium.')
