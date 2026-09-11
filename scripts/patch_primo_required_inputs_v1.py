from pathlib import Path

runtime_path = Path('assets/runtime.js')
runtime = runtime_path.read_text(encoding='utf-8')

replacements = [
    (
        "The heavy optimizer stays paused until Bed EXP and at least one Cart/hr rate are provided.",
        "The heavy optimizer stays paused until Bed EXP and all four Cart/hr rates are provided."
    ),
    (
        "S2 optimizer needs real Bed EXP plus at least one Cart/hr production rate.",
        "S2 optimizer needs real Bed EXP plus all four Cart/hr production rates."
    ),
    (
        "const cartIds=['oreRate','essenceRate','sandRate','treatRate'];\n    const cartRates=cartIds.map(id=>Math.max(0,parseCompactNumber($(id)?.value,0)));\n    return {bed,cartRates,hasBed:bed>0,hasCart:cartRates.some(value=>value>0)};",
        "const cartInputs=[['oreRate','Raw Ore Cart/hr'],['essenceRate','Skill Essence Cart/hr'],['sandRate','Chrono Sand Cart/hr'],['treatRate','Fantomon Treats Cart/hr']];\n    const cartRates=cartInputs.map(([id])=>Math.max(0,parseCompactNumber($(id)?.value,0)));\n    const missingCart=cartInputs.filter((_,i)=>cartRates[i]<=0).map(([,label])=>label);\n    return {bed,cartRates,missingCart,hasBed:bed>0,hasAllCart:missingCart.length===0};"
    ),
    (
        "if(!requirements.hasCart) missing.push('at least one Cart/hr rate');",
        "missing.push(...requirements.missingCart);"
    ),
    (
        "$('optimizerSummary').textContent='The heavy Primostar search is paused until Bed EXP and Cart production are entered.';",
        "$('optimizerSummary').textContent='The heavy Primostar search is paused until Bed EXP and all four Cart production rates are entered.';"
    ),
    (
        "if(!required.hasBed || !required.hasCart){ clearS2ForRequiredPlannerInputs(cfg,required); return; }",
        "if(!required.hasBed || !required.hasAllCart){ clearS2ForRequiredPlannerInputs(cfg,required); return; }"
    ),
]

for old, new in replacements:
    count = runtime.count(old)
    if count != 1:
        raise SystemExit(f'Expected exactly one runtime replacement, found {count}: {old[:100]!r}')
    runtime = runtime.replace(old, new, 1)

runtime_path.write_text(runtime, encoding='utf-8')

runtime_check = runtime_path.read_text(encoding='utf-8')
assert "hasAllCart:missingCart.length===0" in runtime_check
assert "if(!required.hasBed || !required.hasAllCart){ clearS2ForRequiredPlannerInputs(cfg,required); return; }" in runtime_check
assert "Raw Ore Cart/hr" in runtime_check
assert "Skill Essence Cart/hr" in runtime_check
assert "Chrono Sand Cart/hr" in runtime_check
assert "Fantomon Treats Cart/hr" in runtime_check

print('Primostar all-production-input guard patched successfully.')
