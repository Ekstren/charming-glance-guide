from pathlib import Path
import re

paths = [Path('index.html'), Path('.github/build-fantomons-inject.html')]

new_block = r'''  const TECHNIQUE_SWAP_SCENARIOS={
    'Dungeon|Flash Fire|Flame Aura|Flickering Blade|Blade Storm':[
      ['Need Dispel or extra mobility','Flame Aura','Darkness Descends']
    ],
    'Arena|Darkness Descends|Doom Blade|Flickering Blade|Blade Storm':[
      ['Need more sustain','Doom Blade','Soul Piercer']
    ],
    'Tournament · 2v2|Darkness Descends|Soul Piercer|Flickering Blade|Blade Storm':[
      ['Partner already supplies enough control; want harder burst','Soul Piercer','Doom Blade']
    ],
    'Dungeon · Tank|Valor Surge|Heart of Challenge|Luminous Shield|Desperate Protection':[
      ['Need more repeatable Taunt','Valor Surge','Hamper Strike'],
      ['Easy clear; want more damage','Desperate Protection','Swirling Blade or Star Shattering Slash']
    ],
    'Arena · Tank|Luminous Shield|Forceful Charge|Star Shattering Slash|Desperate Protection':[
      ['Need cleanse + self damage buff more than the extra gap-close','Forceful Charge','Valor Surge']
    ],
    'Tournament · 2v2 · Tank|Valor Surge|Hamper Strike|Luminous Shield|Desperate Protection':[
      ['Need a broader opening Taunt','Hamper Strike','Heart of Challenge']
    ],
    'Tournament · 4v4 · Tank|Valor Surge|Heart of Challenge|Luminous Shield|Desperate Protection':[
      ['Need repeatable Taunt after the opener','Heart of Challenge','Hamper Strike']
    ],
    'Dungeon · DPS|Swirling Blade|Lunarwater Threads|Seismic Tide|Raging Maelstrom':[
      ['Boss or elite focus','Raging Maelstrom','Star Shattering Slash']
    ],
    'Crucible / Conquest · DPS|Swirling Blade|Lunarwater Threads|Seismic Tide|Star Shattering Slash':[
      ['Star Shattering Slash is badly under-ranked','Star Shattering Slash','Raging Maelstrom']
    ],
    'Arena · DPS|Swirling Blade|Luminous Shield|Forceful Charge|Star Shattering Slash':[
      ['Need cleanse + self damage buff; can stay on target without the extra gap-close','Forceful Charge','Valor Surge']
    ],
    'Tournament · 2v2 · DPS|Swirling Blade|Luminous Shield|Forceful Charge|Star Shattering Slash':[
      ['Need cleanse + duo damage buff; can stay on target without the extra gap-close','Forceful Charge','Valor Surge']
    ],
    'Crucible / Conquest|Formation Breaker|Divine Wrath|Wind Blade Spiral|Thunder of Judgment':[
      ['Small boss or Divine Wrath is landing poorly','Divine Wrath','Meteoric Flames'],
      ['A better-ranked Wind option wins on your account','Wind Blade Spiral',"Wind's Delight or Tempest Sphere"]
    ],
    'Crucible / Conquest · DPS|Dark Bullet|Dark Starburst|Chaos Rune|Shadow of Termination':[
      ['High Effect Hit Rate','Chaos Rune','Mana Blast']
    ],
    'Arena · DPS|Dark Bullet|Dark Starburst|Chaos Rune|Shadow of Termination':[
      ['High Effect Hit Rate','Chaos Rune','Mana Blast']
    ],
    'Dungeon · Heals|Waterling Summon|Rejuvenating Rain|Radiant Restoration|Frenzy Totem':[
      ['Need more raw healing','Frenzy Totem','Healing Touch']
    ]
  };

'''

for path in paths:
    text = path.read_text(encoding='utf-8')
    text, count = re.subn(
        r"  const TECHNIQUE_SWAP_SCENARIOS=\{.*?\n  \};\n\n(?=  const FANTO=\{)",
        new_block,
        text,
        count=1,
        flags=re.S,
    )
    if count != 1:
        raise SystemExit(f'{path}: expected one Technique swap scenario block, found {count}')

    old = "    const techniqueSwaps=TECHNIQUE_SWAP_SCENARIOS[r.techniques.join('|')]||[];"
    new = "    const techniqueSwaps=TECHNIQUE_SWAP_SCENARIOS[r.name+'|'+r.techniques.join('|')]||[];"
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{path}: expected one Technique swap lookup, found {count}')
    text = text.replace(old, new, 1)
    path.write_text(text, encoding='utf-8')

print('scoped Technique swap scenarios to the exact build role')
