from pathlib import Path

files=[Path('index.html'),Path('scripts/patch_restore_rich_builds_v1.py')]
repls={
"""    Conqueror:{
      rule:'Elemental melee DPS. S2 Crit RES makes Crit Rate especially valuable.',
      rows:[['Sword','ATK ≥ Elemental Mastery > SPD'],['Gauntlets','ATK ≥ Elemental Mastery > SPD'],['Helmet','DEF ≥ Physical RES = Elemental RES > HP'],['Chest','DEF ≥ Physical RES = Elemental RES > HP'],['Boots','ATK ≥ Elemental Mastery > SPD']],
      substats:'Crit Rate% > Crit DMG% > Elemental Mastery / Accuracy% > SPD or HP/SPD-to-ATK conversion'
    },""":
"""    Conqueror:{
      rule:'Current T4 evidence supports ATK ≥ Elemental Mastery on main secondaries. Crit Rate/Crit DMG are the premium reroll stats; Accuracy matters more in PvP and high-Block fights.',
      rows:[['Sword','ATK ≥ Elemental Mastery > SPD'],['Gauntlets','ATK ≥ Elemental Mastery > SPD'],['Helmet','DEF ≥ Physical RES = Elemental RES > HP'],['Chest','DEF ≥ Physical RES = Elemental RES > HP'],['Boots','ATK ≥ Elemental Mastery > SPD']],
      substats:'Crit Rate + Crit DMG > Crit Rate + Accuracy > Elemental Mastery / Accuracy > SPD / useful HP-or-SPD-to-ATK conversions. ATK/ATK% affixes are lower priority than the premium Crit packages.'
    },""",
"""    Guardian:{
      rule:'Block is the premium defensive stat; offensive slots still value speed.',
      rows:[['Sword','SPD > ATK > Physical Mastery > Elemental Mastery'],['Shield','DEF > HP > Physical / Elemental RES'],['Helmet','DEF > HP > RES'],['Chest','DEF > HP > RES'],['Boots','SPD > ATK > Elemental / Physical Mastery']],
      substats:'Block Rate% > Block Efficiency > PvE/PvP DMG + DMG RES > DEF / SPD / HP / useful Crit'
    },""":
"""    Guardian:{
      rule:'Block is Guardian’s defining stat. Stack Block Rate first; after that, DEF/DMG RES drive survival while SPD remains the best offensive/support tempo stat.',
      rows:[['Sword','SPD > ATK > Physical Mastery > Elemental Mastery'],['Shield','DEF > HP > Physical / Elemental RES'],['Helmet','DEF > HP > RES'],['Chest','DEF > HP > RES'],['Boots','SPD > ATK > Elemental / Physical Mastery']],
      substats:'Block Rate% / Block Rate + Block Efficiency > PvE/PvP Bonus DMG + DMG RES > DEF / SPD / HP > useful Crit. Accuracy and Crit DMG are situational damage stats.'
    },""",
"""      dps:{
        rule:'Dark DPS. High Effect Hit Rate is required before Erosion becomes dependable.',
        rows:[['Staff','Effect Hit Rate ≥ Elemental Mastery ≥ ATK > SPD'],['Orb','Effect Hit Rate ≥ Elemental Mastery ≥ ATK > SPD'],['Helmet','DEF / RES > HP'],['Chest','DEF / RES > HP'],['Boots','Elemental Mastery > ATK > SPD']],
        substats:'Crit + Accuracy / Crit + Crit DMG / ailment damage > Effect Hit Rate > useful conversions'
      },
      heals:{
        rule:'Healing/support is Dominator’s most reliable S2 role.',
        rows:[['Staff','SPD > Effect Hit Rate > Elemental Mastery > ATK'],['Orb','SPD > Effect Hit Rate > Elemental Mastery > ATK'],['Helmet','HP > DEF / RES'],['Chest','HP > DEF / RES'],['Boots','SPD > Elemental Mastery > ATK']],
        substats:'DMG RES + Healing > Healing Boost > Block packages > SPD / HP'
      }""":
"""      dps:{
        rule:'Effect Hit Rate is a threshold stat: get enough to land Erosion reliably, then favor damage-quality affixes instead of blindly stacking more EHR. If Erosion is unreliable, hybrid/direct damage is safer.',
        rows:[['Staff','Effect Hit Rate ≥ Elemental Mastery ≥ ATK > SPD'],['Orb','Effect Hit Rate ≥ Elemental Mastery ≥ ATK > SPD'],['Helmet','DEF / RES > HP'],['Chest','DEF / RES > HP'],['Boots','Elemental Mastery > ATK > SPD']],
        substats:'Crit Rate + Accuracy / Crit Rate + Crit DMG / ailment DMG > Effect Hit Rate until reliable > Elemental Mastery > useful conversions. ATK/ATK% are lower-priority affixes.'
      },
      heals:{
        rule:'Healing scales from Max HP, while SPD gives more support actions. Effect Hit Rate is useful when your support bar also needs debuffs to land.',
        rows:[['Staff','SPD > Effect Hit Rate > Elemental Mastery > ATK'],['Orb','SPD > Effect Hit Rate > Elemental Mastery > ATK'],['Helmet','HP > DEF / RES'],['Chest','HP > DEF / RES'],['Boots','SPD > Elemental Mastery > ATK']],
        substats:'DMG RES + Healing > Healing Boost > Block packages > SPD / HP. ATK and Elemental Mastery mainly help the damage side of a healer loadout.'
      }"""
}
for p in files:
    s=p.read_text(encoding='utf-8')
    for old,new in repls.items():
        if old in s:
            s=s.replace(old,new,1)
        elif new not in s:
            raise SystemExit(f'{p}: stat profile anchor not found')
    p.write_text(s,encoding='utf-8')
    print(f'{p}: Conqueror, Guardian, and Dominator stat guidance refreshed')
