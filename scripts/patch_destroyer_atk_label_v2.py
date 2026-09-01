from pathlib import Path

files=[Path('index.html'),Path('scripts/patch_restore_rich_builds_v1.py'),Path('scripts/patch_destroyer_stat_prio_v1.py')]
repls={
"T4 Destroyer values flat ATK much more than older EM-first advice suggests. Formation Breaker scales from ATK; EM is still strong, especially in PvP/equal-level content.":"T4 Destroyer values ATK much more than older EM-first advice suggests. Formation Breaker scales from ATK; EM is still strong, especially in PvP/equal-level content.",
"Flat ATK ≥ Elemental Mastery > Crit > SPD":"ATK ≥ Elemental Mastery > Crit > SPD",
"Elemental Mastery / Flat ATK > SPD":"Elemental Mastery / ATK > SPD",
"Crit Rate + Crit DMG / Crit Rate + Accuracy > Flat ATK / Elemental Mastery > Accuracy / SPD. Do not value ATK% like flat ATK.":"Crit Rate + Crit DMG / Crit Rate + Accuracy > ATK / Elemental Mastery > Accuracy / SPD."
}
for p in files:
    s=p.read_text(encoding='utf-8')
    changed=False
    for old,new in repls.items():
        if old in s:
            s=s.replace(old,new)
            changed=True
    if changed:
        p.write_text(s,encoding='utf-8')
        print(f'{p}: normalized Destroyer ATK labels')
    else:
        print(f'{p}: no matching old labels found')
