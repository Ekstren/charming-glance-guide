from pathlib import Path

FILES=[Path('index.html'),Path('scripts/patch_restore_rich_builds_v1.py')]
repls={
"substats:'Crit Rate / Crit DMG > Accuracy > Elemental Mastery > SPD > ATK.'":"substats:'Crit Rate / Crit DMG > Accuracy > Elemental Mastery > SPD > ATK'",
"substats:'Block Rate > DEF > SPD > HP.'":"substats:'Block Rate > DEF > SPD > HP'",
"substats:'Crit Rate / Crit DMG > ATK ≈ Elemental Mastery > Accuracy > SPD.'":"substats:'Crit Rate / Crit DMG > ATK ≈ Elemental Mastery > Accuracy > SPD'",
"substats:'Effect Hit Rate > Crit Rate / Crit DMG > Elemental Mastery > ATK > SPD.'":"substats:'Effect Hit Rate > Crit Rate / Crit DMG > Elemental Mastery > ATK > SPD'",
"substats:'Healing Boost > SPD > HP > DMG RES.'":"substats:'Healing Boost > SPD > HP > DMG RES'",
}
for p in FILES:
    s=p.read_text(encoding='utf-8')
    changed=0
    for old,new in repls.items():
        if old in s:
            s=s.replace(old,new)
            changed+=1
    p.write_text(s,encoding='utf-8')
    print(f'{p}: removed terminal periods from {changed} substat profile(s)')
