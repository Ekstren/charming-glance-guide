from pathlib import Path

# v5 contains the full audited replacement payload, but its one interpolation block was
# accidentally written as a Python f-string even though it also contains JavaScript braces.
# Read it as text, turn only that block into an ordinary triple-quoted string, fill the two
# intended data placeholders explicitly, then execute the corrected patch source.
src_path=Path('scripts/apply_exact_s2_upgrade_costs_v5.py')
src=src_path.read_text(encoding='utf-8')
if "insert=f'''" not in src:
    raise SystemExit('v5 interpolation anchor not found')
src=src.replace("insert=f'''","insert='''",1)
anchor="'''\nif anchor not in s: raise SystemExit('EXP insert anchor not found')"
replacement="'''\ninsert=insert.replace('{char_data}',char_data).replace('{fanto_data}',fanto_data)\nif anchor not in s: raise SystemExit('EXP insert anchor not found')"
if anchor not in src:
    raise SystemExit('v5 interpolation close anchor not found')
src=src.replace(anchor,replacement,1)
try:
    exec(compile(src,str(src_path)+'::v6-fixed','exec'))
except SystemExit as exc:
    if 'already applied' not in str(exc):
        raise

p=Path('index.html')
s=p.read_text(encoding='utf-8')
if '__sxsExactCostProbeV5' not in s:
    probe="""
  /* Read-only internal regression probe for the extracted S2 cost tables. */
  window.__sxsExactCostProbeV5=()=>{
    const cfg=CALC_SEASONS.s2;
    return {
      charLen:S2_EXACT_CHARACTER_EXP_FROM_130.length,
      fantoLen:S2_EXACT_FANTOMON_EXP_FROM_130.length,
      gear130:gearStepCost(130,cfg),gear131:gearStepCost(131,cfg),gear160:gearStepCost(160,cfg),gear188:gearStepCost(188,cfg),
      skill130:skillStepCost(130,cfg),skill140:skillStepCost(140,cfg),skill160:skillStepCost(160,cfg),skill180:skillStepCost(180,cfg),
      relic13:relicStepSand(13,cfg),relic18:relicStepSand(18,cfg),relic27:relicStepSand(27,cfg),
      fanto130:fantoStepTreatCost(130,cfg),fanto160:fantoStepTreatCost(160,cfg),
      xp130:expRequiredForLevel(130,cfg),xp210:expRequiredForLevel(210,cfg),xp281:expRequiredForLevel(281,cfg),xp287:expRequiredForLevel(287,cfg),xp288:expRequiredForLevel(288,cfg),
      refined134:gearStepRefined(134,cfg),refined139:gearStepRefined(139,cfg),refined135:gearStepRefined(135,cfg),
      preGear121:gearStepCost(121,cfg),preSkill121:skillStepCost(121,cfg)
    };
  };
"""
    insert_anchor='\n  function balancedGearTarget(base, increments){'
    if insert_anchor not in s:
        raise SystemExit('diagnostic probe anchor not found')
    s=s.replace(insert_anchor,probe+insert_anchor,1)
    p.write_text(s,encoding='utf-8')
    print('Added exact S2 cost diagnostic probe.')
