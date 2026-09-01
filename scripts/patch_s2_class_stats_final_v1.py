from pathlib import Path

FILES = [Path('index.html'), Path('scripts/patch_restore_rich_builds_v1.py')]

REPLACEMENTS = [
    (
        "substats:'Crit Rate + Crit DMG > Crit Rate + Accuracy > Elemental Mastery / Accuracy > SPD / useful HP-or-SPD-to-ATK conversions. ATK/ATK% affixes are lower priority than the premium Crit packages.'",
        "substats:'PvE: Crit Rate + Crit DMG > Crit Rate + Accuracy. PvP/high-Block: Crit Rate + Accuracy can be equal or better. Then Elemental Mastery / Accuracy > SPD / useful HP-or-SPD-to-ATK conversions. ATK/ATK% affixes are lower priority than the premium Crit packages.'"
    ),
    (
        "rows:[['Sword','SPD > ATK > Physical Mastery > Elemental Mastery'],['Shield','DEF > HP > Physical / Elemental RES'],['Helmet','DEF > HP > RES'],['Chest','DEF > HP > RES'],['Boots','SPD > ATK > Elemental / Physical Mastery']],",
        "rows:[['Sword','SPD > ATK > Physical Mastery > Elemental Mastery'],['Shield','DEF > HP > Physical RES = Elemental RES'],['Helmet','DEF ≥ Physical RES = Elemental RES > HP > Effect RES'],['Chest','DEF ≥ Physical RES = Elemental RES > HP'],['Boots','SPD > ATK > Elemental Mastery = Physical Mastery']],"
    ),
    (
        "substats:'Block Rate% / Block Rate + Block Efficiency > PvE/PvP Bonus DMG + DMG RES > DEF / SPD / HP > useful Crit. Accuracy and Crit DMG are situational damage stats.'",
        "substats:'Best tier: Block Rate% / Block Rate + Block Efficiency / PvE-PvP Bonus DMG + DMG RES. Next: flat DEF / SPD / HP / useful Crit. Accuracy and Crit DMG are situational damage stats.'"
    ),
    (
        "rule:'T4 Destroyer values ATK much more than older EM-first advice suggests. Formation Breaker scales from ATK; EM is still strong, especially in PvP/equal-level content.'",
        "rule:'T4 Destroyer is Elemental Mastery-first on Staff/Codex/Boots, with Crit as the next major damage check. ATK still matters and Formation Breaker scales from it, but that does not make ATK the universal first gearing stat.'"
    ),
    (
        "rows:[['Staff','ATK ≥ Elemental Mastery > Crit > SPD'],['Codex','ATK ≥ Elemental Mastery > Crit > SPD'],['Helmet','DEF / RES > HP'],['Chest','DEF / RES > HP'],['Boots','Elemental Mastery / ATK > SPD']],",
        "rows:[['Staff','Elemental Mastery > Crit > ATK > SPD > Effect Hit Rate'],['Codex','Elemental Mastery > Crit > ATK > SPD > Effect Hit Rate'],['Helmet','DEF ≥ Physical RES = Elemental RES > HP > Effect RES'],['Chest','DEF ≥ Physical RES = Elemental RES > HP'],['Boots','Elemental Mastery > SPD > ATK']],"
    ),
    (
        "substats:'Crit Rate + Crit DMG / Crit Rate + Accuracy > ATK / Elemental Mastery > Accuracy / SPD.'",
        "substats:'Crit Rate + Accuracy / Crit Rate + Crit DMG / PvP Bonus DMG + PvP DMG RES > Elemental Mastery / Crit Rate% / Accuracy% / Crit DMG% > ATK / SPD.'"
    ),
    (
        "rows:[['Staff','Effect Hit Rate ≥ Elemental Mastery ≥ ATK > SPD'],['Orb','Effect Hit Rate ≥ Elemental Mastery ≥ ATK > SPD'],['Helmet','DEF / RES > HP'],['Chest','DEF / RES > HP'],['Boots','Elemental Mastery > ATK > SPD']],",
        "rows:[['Staff','Effect Hit Rate ≥ Elemental Mastery ≥ ATK > SPD'],['Orb','Effect Hit Rate ≥ Elemental Mastery ≥ ATK > SPD'],['Helmet','DEF ≥ Physical RES = Elemental RES > HP > Effect RES'],['Chest','DEF ≥ Physical RES = Elemental RES > HP'],['Boots','Elemental Mastery > ATK > SPD']],"
    ),
    (
        "substats:'Crit Rate + Accuracy / Crit Rate + Crit DMG / ailment DMG > Effect Hit Rate until reliable > Elemental Mastery > useful conversions. ATK/ATK% are lower-priority affixes.'",
        "substats:'Best: Crit Rate + Accuracy / Crit Rate + Crit DMG / ailment DMG / Block Rate + Block Resistance. Then Effect Hit Rate until reliable, damage-vs-monster/player packages, Crit, and Elemental Mastery. ATK/ATK% are only average affixes.'"
    ),
    (
        "rule:'Healing scales from Max HP, while SPD gives more support actions. Effect Hit Rate is useful when your support bar also needs debuffs to land.'",
        "rule:'Healer Dominator is SPD-first on Staff/Orb/Boots and HP-first on Helmet/Chest. Effect Hit Rate is the second main-secondary target on Staff/Orb, but only an average healer affix when rerolling substats.'"
    ),
    (
        "rows:[['Staff','SPD > Effect Hit Rate > Elemental Mastery > ATK'],['Orb','SPD > Effect Hit Rate > Elemental Mastery > ATK'],['Helmet','HP > DEF / RES'],['Chest','HP > DEF / RES'],['Boots','SPD > Elemental Mastery > ATK']],",
        "rows:[['Staff','SPD > Effect Hit Rate > Elemental Mastery > ATK'],['Orb','SPD > Effect Hit Rate > Elemental Mastery > ATK'],['Helmet','HP > DEF ≥ Physical RES = Elemental RES > Effect RES'],['Chest','HP > DEF ≥ Physical RES = Elemental RES'],['Boots','SPD > Elemental Mastery > ATK']],"
    ),
    (
        "substats:'DMG RES + Healing > Healing Boost > Block packages > SPD / HP. ATK and Elemental Mastery mainly help the damage side of a healer loadout.'",
        "substats:'Best tier: DMG RES + Healing / Block Rate + Block Resistance / Healing Boost. Next: evade-on-hit / Crit RES + Block / SPD / HP. Effect Hit Rate is only average as a healer reroll affix.'"
    ),
]

for path in FILES:
    text = path.read_text(encoding='utf-8')
    changed = 0
    for old, new in REPLACEMENTS:
        count = text.count(old)
        if count == 1:
            text = text.replace(old, new, 1)
            changed += 1
        elif count == 0 and new in text:
            # Idempotent reruns are fine.
            continue
        else:
            raise SystemExit(f'{path}: expected exactly one match for {old[:80]!r}, found {count}')
    path.write_text(text, encoding='utf-8')
    print(f'{path}: final S2 class-stat audit applied ({changed} replacements)')
