from pathlib import Path

files=[Path('index.html'),Path('scripts/patch_restore_rich_builds_v1.py')]
old="""    Destroyer:{
      rule:'Elemental ranged DPS. Crit quality and Accuracy are major S2 damage checks.',
      rows:[['Staff','Elemental Mastery > Crit > ATK > SPD > Effect Hit Rate'],['Codex','Elemental Mastery > Crit > ATK > SPD > Effect Hit Rate'],['Helmet','DEF / RES > HP'],['Chest','DEF / RES > HP'],['Boots','Elemental Mastery > SPD > ATK']],
      substats:'Crit + Accuracy / Crit + Crit DMG > Elemental Mastery > Crit Rate / Accuracy / Crit DMG'
    },"""
new="""    Destroyer:{
      rule:'T4 Destroyer values ATK much more than older EM-first advice suggests. Formation Breaker scales from ATK; EM is still strong, especially in PvP/equal-level content.',
      rows:[['Staff','ATK ≥ Elemental Mastery > Crit > SPD'],['Codex','ATK ≥ Elemental Mastery > Crit > SPD'],['Helmet','DEF / RES > HP'],['Chest','DEF / RES > HP'],['Boots','Elemental Mastery / ATK > SPD']],
      substats:'Crit Rate + Crit DMG / Crit Rate + Accuracy > ATK / Elemental Mastery > Accuracy / SPD.'
    },"""
for p in files:
    s=p.read_text(encoding='utf-8')
    if old not in s:
        if new in s:
            print(f'{p}: already updated')
            continue
        raise SystemExit(f'{p}: Destroyer profile anchor not found')
    s=s.replace(old,new,1)
    p.write_text(s,encoding='utf-8')
    print(f'{p}: Destroyer stat priorities updated')
