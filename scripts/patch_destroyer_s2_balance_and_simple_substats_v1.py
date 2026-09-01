from pathlib import Path

INDEX = Path('index.html')
RESTORE = Path('scripts/patch_restore_rich_builds_v1.py')

simple_replacements = [
    (
        "substats:'PvE: Crit Rate + Crit DMG > Crit Rate + Accuracy. PvP/high-Block: Crit Rate + Accuracy can be equal or better. Then Elemental Mastery / Accuracy > SPD / useful HP-or-SPD-to-ATK conversions. ATK/ATK% affixes are lower priority than the premium Crit packages.'",
        "substats:'Crit Rate / Crit DMG > Accuracy > Elemental Mastery > SPD > ATK.'"
    ),
    (
        "substats:'Best tier: Block Rate% / Block Rate + Block Efficiency / PvE-PvP Bonus DMG + DMG RES. Next: flat DEF / SPD / HP / useful Crit. Accuracy and Crit DMG are situational damage stats.'",
        "substats:'Block Rate > DEF > SPD > HP.'"
    ),
    (
        "rule:'T4 Destroyer is Elemental Mastery-first on Staff/Codex/Boots, with Crit as the next major damage check. ATK still matters and Formation Breaker scales from it, but that does not make ATK the universal first gearing stat.'",
        "rule:'S2 Destroyer is balance-sensitive, not permanently EM-first. Keep a healthy Elemental Mastery floor, then flat ATK can match or beat more EM on developed accounts. Crit remains premium; dummy-test close swaps.'"
    ),
    (
        "rows:[['Staff','Elemental Mastery > Crit > ATK > SPD > Effect Hit Rate'],['Codex','Elemental Mastery > Crit > ATK > SPD > Effect Hit Rate'],['Helmet','DEF ≥ Physical RES = Elemental RES > HP > Effect RES'],['Chest','DEF ≥ Physical RES = Elemental RES > HP'],['Boots','Elemental Mastery > SPD > ATK']],",
        "rows:[['Staff','ATK ≈ Elemental Mastery > Crit > SPD'],['Codex','ATK ≈ Elemental Mastery > Crit > SPD'],['Helmet','DEF ≥ Physical RES = Elemental RES > HP > Effect RES'],['Chest','DEF ≥ Physical RES = Elemental RES > HP'],['Boots','ATK ≈ Elemental Mastery > SPD']],"
    ),
    (
        "substats:'Crit Rate + Accuracy / Crit Rate + Crit DMG / PvP Bonus DMG + PvP DMG RES > Elemental Mastery / Crit Rate% / Accuracy% / Crit DMG% > ATK / SPD.'",
        "substats:'Crit Rate / Crit DMG > ATK ≈ Elemental Mastery > Accuracy > SPD.'"
    ),
    (
        "substats:'Best: Crit Rate + Accuracy / Crit Rate + Crit DMG / ailment DMG / Block Rate + Block Resistance. Then Effect Hit Rate until reliable, damage-vs-monster/player packages, Crit, and Elemental Mastery. ATK/ATK% are only average affixes.'",
        "substats:'Effect Hit Rate > Crit Rate / Crit DMG > Elemental Mastery > ATK > SPD.'"
    ),
    (
        "substats:'Best tier: DMG RES + Healing / Block Rate + Block Resistance / Healing Boost. Next: evade-on-hit / Crit RES + Block / SPD / HP. Effect Hit Rate is only average as a healer reroll affix.'",
        "substats:'Healing Boost > SPD > HP > DMG RES.'"
    ),
]

for path in (INDEX, RESTORE):
    text = path.read_text(encoding='utf-8')
    for old, new in simple_replacements:
        count = text.count(old)
        if count == 1:
            text = text.replace(old, new, 1)
        elif count == 0 and new in text:
            pass
        else:
            raise SystemExit(f'{path}: expected one match for {old[:70]!r}, found {count}')
    path.write_text(text, encoding='utf-8')
    print(f'{path}: simplified quick stat profiles')

text = INDEX.read_text(encoding='utf-8')
index_replacements = [
    (
        '<div class="guideSummary"><div><span>Ranged elemental DPS</span><strong>Destroyer</strong><p>T4 is more specialized than Archmage: Light/Wind handles general and boss content while pure Fire becomes the horde-clearing specialist. Freeze remains playable but is less reliable.</p></div><p><b>Stat priority</b>Elemental Mastery &gt; Crit &gt; ATK &gt; SPD on Staff/Codex. Your best builds are Crit-sensitive, especially Fire, so good Crit/Accuracy lines matter more than raw ATK%.</p></div>',
        '<div class="guideSummary"><div><span>Ranged elemental DPS</span><strong>Destroyer</strong><p>T4 is more specialized than Archmage: mixed Light/Wind/Fire handles general and boss content, pure Fire is the horde specialist, and Wind remains strong in PvP. Freeze is playable but less reliable.</p></div><p><b>Stat priority</b>ATK ≈ Elemental Mastery &gt; Crit &gt; SPD on Staff/Codex. Keep enough EM to avoid an underbuilt multiplier, but once EM is healthy, developed S2 accounts often gain more from flat ATK. Dummy-test close swaps.</p></div>'
    ),
    (
        '<div class="gearPanel"><div class="gearIntro"><span>Season 2 gearing</span><strong>Gear & stat priorities</strong><p>Destroyer leans harder into elemental scaling than the other classes. Affinity and Crit quality can matter more than a small power-score gain.</p></div><div class="gearGrid"><div class="gearItem"><span>Main lines</span><p>Staff/Codex: Elemental Mastery &gt; Crit &gt; ATK &gt; SPD &gt; Effect Hit Rate. Helmet/Chest: DEF/RES &gt; HP. Boots: Elemental Mastery &gt; SPD &gt; ATK.</p></div><div class="gearItem"><span>Best substats</span><p>Top unique survival/dodge lines are excellent. Otherwise Crit + Accuracy, Crit + Crit DMG, then Elemental Mastery / Crit Rate / Accuracy / Crit DMG.</p></div><div class="gearItem"><span>Gem plan</span><p>Weapon &amp; Off-hand: Obsidian / Amethyst. Boots: Amethyst. Armor: Moonstone. Helm: Citrine; use Beryl/Sapphire mainly for conversion or power padding.</p></div><div class="gearItem"><span>Relic elements</span><p>Light is mandatory priority, Fire is next because of the new horde build. Then Wind &gt; Water &gt; Dark for most Destroyer accounts.</p></div></div></div>',
        '<div class="gearPanel"><div class="gearIntro"><span>Season 2 gearing</span><strong>Gear & stat priorities</strong><p>Destroyer wants a balanced damage profile. EM supplies the elemental multiplier, but flat ATK keeps scaling every damaging Technique and becomes increasingly competitive once your EM pool is already strong.</p></div><div class="gearGrid"><div class="gearItem"><span>Main lines</span><p>Staff/Codex: ATK ≈ Elemental Mastery &gt; Crit &gt; SPD. Helmet/Chest: DEF/RES &gt; HP. Boots: ATK ≈ Elemental Mastery &gt; SPD. If two pieces are close, use the 50-round dummy test.</p></div><div class="gearItem"><span>Best substats</span><p>Crit Rate / Crit DMG &gt; ATK ≈ Elemental Mastery &gt; Accuracy &gt; SPD.</p></div><div class="gearItem"><span>Gem plan</span><p>Weapon &amp; Off-hand: Obsidian / Amethyst. Boots: Amethyst. Armor: Moonstone. Helm: Citrine; use Beryl/Sapphire mainly for conversion or power padding.</p></div><div class="gearItem"><span>Relic elements</span><p>Light is the safest general priority, Fire is excellent for horde content, and Wind is especially strong for PvP/control. Favor Affinity over Aegis on offensive relic slots.</p></div></div></div>'
    ),
    (
        '<li>Small bosses: Divine Wrath can be replaced by Meteoric Flames</li>',
        '<li><b>Test slot:</b> Wind Blade Spiral, Meteoric Flames, or Wind\'s Delight can win depending on ranks and Radiant Sear proc rate; use a long dummy test</li>'
    ),
    (
        '<p class="buildSource">Research snapshot Aug 21, 2026 · <a href="https://www.prydwen.gg/sword-x-staff/guides/build-guide-destroyer" rel="noreferrer" target="_blank">Prydwen Destroyer ↗</a> · <a href="https://lootandwaifus.com/guides/sword-x-staff-how-to-play-sorcerer/" rel="noreferrer" target="_blank">Loot &amp; Waifus Sorcerer/Destroyer ↗</a></p>',
        '<p class="buildSource">Research snapshot Aug 31, 2026 · <a href="https://www.prydwen.gg/sword-x-staff/guides/build-guide-destroyer" rel="noreferrer" target="_blank">Prydwen Destroyer ↗</a> · <a href="https://www.reddit.com/r/SwordxStaff_Official/comments/1vdjbo4/better_destroyer_builds/" rel="noreferrer" target="_blank">S2 community testing ↗</a> · <a href="https://lootandwaifus.com/guides/sword-x-staff-how-to-play-sorcerer/" rel="noreferrer" target="_blank">Loot &amp; Waifus ↗</a></p>'
    ),
]

for old, new in index_replacements:
    count = text.count(old)
    if count == 1:
        text = text.replace(old, new, 1)
    elif count == 0 and new in text:
        pass
    else:
        raise SystemExit(f'index.html: expected one full-build match for {old[:80]!r}, found {count}')

INDEX.write_text(text, encoding='utf-8')
print('index.html: Destroyer S2 balance/community notes refreshed')
