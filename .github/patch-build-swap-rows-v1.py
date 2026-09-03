from pathlib import Path
import re

paths = [Path('index.html'), Path('.github/build-fantomons-inject.html')]

old_css = '''.buildCard .techniqueSwapScenarios{grid-column:1/-1;border-top:1px solid var(--line);padding:9px 0 1px;margin-top:0;display:flex;align-items:flex-start;gap:10px;min-width:0}
.buildCard .techniqueSwapScenarios>span{flex:0 0 auto;color:var(--muted);font-size:8px;font-weight:900;letter-spacing:.08em;text-transform:uppercase;padding-top:2px}
.buildCard .techniqueSwapScenarios>div{display:flex;flex-wrap:wrap;gap:5px 12px;min-width:0}
.buildCard .techniqueSwapScenarios p{margin:0;color:var(--muted);font-size:9px;line-height:1.4}
.buildCard .techniqueSwapScenarios p b{color:var(--ink);font-weight:800}
@media(max-width:620px){.buildCard .techniqueSwapScenarios{display:block}.buildCard .techniqueSwapScenarios>span{display:block;margin-bottom:5px}.buildCard .techniqueSwapScenarios>div{display:grid;grid-template-columns:1fr;gap:5px}}
'''
new_css = '''.buildCard .buildSwapRows{grid-column:1/-1;border-top:1px solid var(--line);padding:8px 0 1px;margin-top:0;display:grid;gap:5px;min-width:0}
.buildCard .buildSwapRows p{margin:0;color:var(--muted);font-size:9px;line-height:1.4}
.buildCard .buildSwapRows p>strong{color:var(--muted);font-size:8px;font-weight:900;letter-spacing:.06em;text-transform:uppercase;margin-right:5px}
.buildCard .buildSwapRows .swapNames{color:var(--ink);font-weight:800}
'''

new_technique_block = r'''  const TECHNIQUE_SWAP_SCENARIOS={
    'Dungeon|Flash Fire|Flame Aura|Flickering Blade|Blade Storm':[
      ['Need Dispel','Flame Aura','Darkness Descends']
    ],
    'Arena|Darkness Descends|Doom Blade|Flickering Blade|Blade Storm':[
      ['Need sustain','Doom Blade','Soul Piercer']
    ],
    'Tournament · 2v2|Darkness Descends|Soul Piercer|Flickering Blade|Blade Storm':[
      ['Need more burst','Soul Piercer','Doom Blade']
    ],
    'Dungeon · Tank|Valor Surge|Heart of Challenge|Luminous Shield|Desperate Protection':[
      ['Need more Taunt','Valor Surge','Hamper Strike']
    ],
    'Arena · Tank|Luminous Shield|Forceful Charge|Star Shattering Slash|Desperate Protection':[
      ['Need cleanse + damage buff','Forceful Charge','Valor Surge']
    ],
    'Tournament · 2v2 · Tank|Valor Surge|Hamper Strike|Luminous Shield|Desperate Protection':[
      ['Need opening AoE Taunt','Hamper Strike','Heart of Challenge']
    ],
    'Tournament · 4v4 · Tank|Valor Surge|Heart of Challenge|Luminous Shield|Desperate Protection':[
      ['Need repeatable Taunt','Heart of Challenge','Hamper Strike']
    ],
    'Dungeon · DPS|Swirling Blade|Lunarwater Threads|Seismic Tide|Raging Maelstrom':[
      ['Boss / elite focus','Raging Maelstrom','Star Shattering Slash']
    ],
    'Crucible / Conquest · DPS|Swirling Blade|Lunarwater Threads|Seismic Tide|Star Shattering Slash':[
      ['Star Shattering is under-ranked','Star Shattering Slash','Raging Maelstrom']
    ],
    'Arena · DPS|Swirling Blade|Luminous Shield|Forceful Charge|Star Shattering Slash':[
      ['Need cleanse + damage buff','Forceful Charge','Valor Surge']
    ],
    'Tournament · 2v2 · DPS|Swirling Blade|Luminous Shield|Forceful Charge|Star Shattering Slash':[
      ['Need cleanse + duo buff','Forceful Charge','Valor Surge']
    ],
    'Crucible / Conquest|Formation Breaker|Divine Wrath|Wind Blade Spiral|Thunder of Judgment':[
      ['Small target / poor Divine Wrath hits','Divine Wrath','Meteoric Flames'],
      ['Wind Blade Spiral is under-ranked','Wind Blade Spiral',"Wind's Delight"]
    ],
    'Crucible / Conquest · DPS|Dark Bullet|Dark Starburst|Chaos Rune|Shadow of Termination':[
      ['High Effect Hit Rate','Chaos Rune','Mana Blast']
    ],
    'Arena · DPS|Dark Bullet|Dark Starburst|Chaos Rune|Shadow of Termination':[
      ['High Effect Hit Rate','Chaos Rune','Mana Blast']
    ],
    'Dungeon · Heals|Waterling Summon|Rejuvenating Rain|Radiant Restoration|Frenzy Totem':[
      ['Need more healing','Frenzy Totem','Healing Touch']
    ]
  };

  const CHARM_SWAP_SCENARIOS={
    'Dungeon|Piercing Assault|Tactical Adaptation|Soul Splash|Insightful Eye':[
      ['High Crit','Insightful Eye','Soul Breaker'],
      ['Need more survival','Soul Splash','Indomitable Will']
    ],
    'Crucible / Conquest|Piercing Assault|Tactical Adaptation|Blazing Clash|Insightful Eye':[
      ['High Crit','Insightful Eye','Crit Mastery'],
      ['Need more survival','Blazing Clash','Indomitable Will']
    ],
    'Arena|Piercing Assault|Tactical Adaptation|Soul Breaker|Indomitable Will':[
      ['Low Crit','Soul Breaker','Insightful Eye']
    ],
    'Tournament · 2v2|Piercing Assault|Tactical Adaptation|Soul Breaker|Indomitable Will':[
      ['Low Crit','Soul Breaker','Insightful Eye']
    ],
    'Tournament · 4v4|Insightful Eye|Piercing Assault|Tactical Adaptation|Indomitable Will':[
      ['High Crit','Insightful Eye','Soul Breaker']
    ],
    'Dungeon · Tank|Iron Will|Holy Aegis|Block Awareness|Soul Protection':[
      ['Need more team mitigation','Soul Protection','Iron Fortress']
    ],
    'Crucible / Conquest · Tank|Frigid Aura|Frigid Glint|Iron Fortress|Oath of Vigil':[
      ['Need more personal survival','Frigid Glint','Soul Protection'],
      ['Still too fragile','Frigid Aura','Holy Aegis']
    ],
    'Arena · Tank|Rebound|Holy Aegis|Block Mastery|Soul Protection':[
      ['Low Block','Soul Protection','Block Awareness']
    ],
    'Tournament · 2v2 · Tank|Iron Will|Rebound|Iron Fortress|Oath of Vigil':[
      ['Getting focused','Rebound','Soul Protection']
    ],
    'Dungeon · DPS|Frigid Aura|Defensive Assault|Frigid Glint|Potential Rebirth':[
      ['Survival is comfortable','Potential Rebirth','Pursuit of Victory']
    ],
    'Arena · DPS|Rebound|Holy Aegis|Block Mastery|Eye for an Eye':[
      ['Taking too much burst','Eye for an Eye','Soul Protection']
    ],
    'Tournament · 2v2 · DPS|Rebound|Holy Aegis|Block Mastery|Eye for an Eye':[
      ['Getting focused','Eye for an Eye','Soul Protection']
    ],
    'Tournament · 4v4 · DPS|Frigid Aura|Defensive Assault|Frigid Glint|Potential Rebirth':[
      ['Frontline is protecting you','Potential Rebirth','Pursuit of Victory']
    ],
    'Crucible / Conquest|Rapid Cast|Mana Surge|Radiant Sear|Incarnation of Light':[
      ['Need more survival','Incarnation of Light','Void Bubble']
    ],
    'Tournament · 2v2|Rapid Cast|Void Bubble|Repelling Wind|Cyclone Lament':[
      ['Teammate already has control','Repelling Wind','Radiant Sear']
    ],
    'Dungeon · Heals|Phantom Light|Healing Mastery|Overhealing|Resurrection':[
      ['Nobody is dying','Resurrection','Mantra of Blessings']
    ]
  };

'''

for path in paths:
    text = path.read_text(encoding='utf-8')

    if text.count(old_css) != 1:
        raise SystemExit(f'{path}: old swap CSS match count {text.count(old_css)}')
    text = text.replace(old_css, new_css, 1)

    text, count = re.subn(
        r"  const TECHNIQUE_SWAP_SCENARIOS=\{.*?\n  \};\n\n(?=  const FANTO=\{)",
        new_technique_block,
        text,
        count=1,
        flags=re.S,
    )
    if count != 1:
        raise SystemExit(f'{path}: Technique swap block match count {count}')

    old_lookup = "    const techniqueSwaps=TECHNIQUE_SWAP_SCENARIOS[r.name+'|'+r.techniques.join('|')]||[];"
    new_lookup = old_lookup + "\n    const charmSwaps=CHARM_SWAP_SCENARIOS[r.name+'|'+r.charms.join('|')]||[];"
    if text.count(old_lookup) != 1:
        raise SystemExit(f'{path}: Technique lookup match count {text.count(old_lookup)}')
    text = text.replace(old_lookup, new_lookup, 1)

    old_render = "      +'<ul><li><b>Offensive:</b> '+esc(r.offensive)+'</li><li><b>Defensive:</b> '+esc(r.defensive)+'</li></ul>'\n      +(techniqueSwaps.length?'<div class=\"techniqueSwapScenarios\"><span>Technique swaps</span><div>'+techniqueSwaps.map(s=>'<p><b>'+esc(s[0])+':</b> '+esc(s[1])+' → '+esc(s[2])+'</p>').join('')+'</div></div>':'')"
    new_render = "      +((techniqueSwaps.length||charmSwaps.length)?'<div class=\"buildSwapRows\">'\n        +techniqueSwaps.map(s=>'<p><strong>Technique Swap:</strong> '+esc(s[0])+' — <span class=\"swapNames\">'+esc(s[1])+' → '+esc(s[2])+'</span></p>').join('')\n        +charmSwaps.map(s=>'<p><strong>Charm Swap:</strong> '+esc(s[0])+' — <span class=\"swapNames\">'+esc(s[1])+' → '+esc(s[2])+'</span></p>').join('')\n        +'</div>':'')"
    if text.count(old_render) != 1:
        raise SystemExit(f'{path}: old renderer output match count {text.count(old_render)}')
    text = text.replace(old_render, new_render, 1)

    text = text.replace("  .builds .buildGrid.metaModeGrid>.buildCard:not([hidden])>ul,\n", "", 1)

    path.write_text(text, encoding='utf-8')

print('replaced offense/defense notes with compact Technique/Charm swap rows')
