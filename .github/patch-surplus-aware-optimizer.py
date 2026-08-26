from pathlib import Path

PATH = Path('index.html')
text = PATH.read_text(encoding='utf-8')
MARKER = 'SURPLUS_AWARE_OPTIMIZER_V2'

if MARKER in text:
    print('Surplus-aware optimizer tuning already applied.')
    raise SystemExit(0)


def replace_once(old: str, new: str, label: str):
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly 1 match, found {count}')
    text = text.replace(old, new, 1)

old_helper = '''  const ORE_PRESERVE_PREMIUM=0.75; // +75% strategic value, bounded rather than absolute.
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
'''

new_helper = '''  /* SURPLUS_AWARE_OPTIMIZER_V2
     The resource object presented to the S1 optimizer has already had enabled S2 hard
     reserves removed. What remains is spendable surplus, not protected rollover stock.
     Value that surplus by replacement effort *and* by how constrained its future use is.
     Essence is most aggressively discounted because Skills cannot exceed Character level;
     Sand/Treats are also progression-gated. Ore retains full opportunity value because Gear
     has the longest useful runway. Preserve Ore adds a bounded premium rather than a veto. */
  const SURPLUS_ACQUISITION_WEIGHTS={ore:1.00,essence:0.10,sand:0.35,treat:0.35};
  const ORE_PRESERVE_PREMIUM=0.50;
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
    const hours=
      oreHours*SURPLUS_ACQUISITION_WEIGHTS.ore+
      essenceHours*SURPLUS_ACQUISITION_WEIGHTS.essence+
      sandHours*SURPLUS_ACQUISITION_WEIGHTS.sand+
      treatHours*SURPLUS_ACQUISITION_WEIGHTS.treat;
    return {hours,oreHours,essenceHours,sandHours,treatHours,treatFallback:enteredTreatRate<=0&&fallbackTreatRate>0};
  }
'''
replace_once(old_helper, new_helper, 'surplus-aware acquisition helper')

replace_once(
"      ? 'Acquisition effort + 75% Ore premium for Gear runway; strong Ore preference, no longer absolute.'\n      : 'Minimize estimated replacement effort using Cart/hr + one 5-Stamina map node per hour; no special Ore premium.';",
"      ? 'Spend capped surplus first; replacement effort then gets a +50% Ore premium for Gear runway.'\n      : 'Spend capped surplus efficiently: reserves stay protected, then replacement effort is weighted by future usability.';",
'optimizer mode notes',
)

# Keep the compact result summary aligned with the actual policy if this exact V1 text is present.
text = text.replace("const policy=optimizerMode()==='preserve'?'preserve Ore with 75% future-value premium':'minimize acquisition effort';",
                    "const policy=optimizerMode()==='preserve'?'spend capped surplus + preserve Ore':'spend capped surplus by acquisition efficiency';")

PATH.write_text(text, encoding='utf-8')
print('Applied surplus-aware optimizer tuning.')
