from pathlib import Path

paths = [Path('index.html'), Path('.github/build-fantomons-inject.html')]

css_anchor = ".buildCard .roleBadge{display:inline-flex;align-items:center;border:1px solid var(--line);border-radius:999px;padding:2px 6px;margin-left:6px;color:var(--muted);font-size:7px;font-weight:900;letter-spacing:.06em;text-transform:uppercase;vertical-align:2px}\n"
css_add = css_anchor + """.buildCard .techniqueSwapScenarios{grid-column:1/-1;border-top:1px solid var(--line);padding:9px 0 1px;margin-top:0;display:flex;align-items:flex-start;gap:10px;min-width:0}\n.buildCard .techniqueSwapScenarios>span{flex:0 0 auto;color:var(--muted);font-size:8px;font-weight:900;letter-spacing:.08em;text-transform:uppercase;padding-top:2px}\n.buildCard .techniqueSwapScenarios>div{display:flex;flex-wrap:wrap;gap:5px 12px;min-width:0}\n.buildCard .techniqueSwapScenarios p{margin:0;color:var(--muted);font-size:9px;line-height:1.4}\n.buildCard .techniqueSwapScenarios p b{color:var(--ink);font-weight:800}\n@media(max-width:620px){.buildCard .techniqueSwapScenarios{display:block}.buildCard .techniqueSwapScenarios>span{display:block;margin-bottom:5px}.buildCard .techniqueSwapScenarios>div{display:grid;grid-template-columns:1fr;gap:5px}}\n"""

data_anchor = "  const FANTO={\n"
data_add = r'''  const TECHNIQUE_SWAP_SCENARIOS={
    'Flash Fire|Flame Aura|Flickering Blade|Blade Storm':[
      ['Need Dispel or extra mobility','Flame Aura','Darkness Descends']
    ],
    'Darkness Descends|Doom Blade|Flickering Blade|Blade Storm':[
      ['Need more sustain','Doom Blade','Soul Piercer']
    ],
    'Darkness Descends|Soul Piercer|Flickering Blade|Blade Storm':[
      ['Partner already supplies enough control; want harder burst','Soul Piercer','Doom Blade']
    ],
    'Valor Surge|Heart of Challenge|Luminous Shield|Desperate Protection':[
      ['Need more repeatable Taunt','Valor Surge','Hamper Strike'],
      ['Easy clear; want more damage','Desperate Protection','Swirling Blade or Star Shattering Slash']
    ],
    'Luminous Shield|Forceful Charge|Star Shattering Slash|Desperate Protection':[
      ['Need cleanse + self damage buff more than gap-closing','Forceful Charge','Valor Surge']
    ],
    'Valor Surge|Hamper Strike|Luminous Shield|Desperate Protection':[
      ['Need a broader opening Taunt','Hamper Strike','Heart of Challenge']
    ],
    'Swirling Blade|Lunarwater Threads|Seismic Tide|Raging Maelstrom':[
      ['Boss or elite focus','Raging Maelstrom','Star Shattering Slash']
    ],
    'Swirling Blade|Lunarwater Threads|Seismic Tide|Star Shattering Slash':[
      ['Star Shattering Slash is badly under-ranked','Star Shattering Slash','Raging Maelstrom']
    ],
    'Swirling Blade|Luminous Shield|Forceful Charge|Star Shattering Slash':[
      ['Need cleanse + self damage buff; can stay on target without the extra gap-close','Forceful Charge','Valor Surge']
    ],
    'Formation Breaker|Divine Wrath|Wind Blade Spiral|Thunder of Judgment':[
      ['Small boss or Divine Wrath is landing poorly','Divine Wrath','Meteoric Flames'],
      ['A better-ranked Wind option wins on your account','Wind Blade Spiral',"Wind's Delight or Tempest Sphere"]
    ],
    'Dark Bullet|Dark Starburst|Chaos Rune|Shadow of Termination':[
      ['High Effect Hit Rate','Chaos Rune','Mana Blast']
    ],
    'Waterling Summon|Rejuvenating Rain|Radiant Restoration|Frenzy Totem':[
      ['Need more raw healing','Frenzy Totem','Healing Touch']
    ]
  };

''' + data_anchor

fn_anchor = """  function buildCardHtml(r){\n    const rm=String(r.name||'').match(/^(.*?) · (Tank|DPS|Heals)$/);\n    const displayName=rm?rm[1]:r.name;\n    const roleAttr=rm?' data-build-role=\\\"'+rm[2].toLowerCase()+'\\\"':'';\n"""
fn_add = """  function buildCardHtml(r){\n    const rm=String(r.name||'').match(/^(.*?) · (Tank|DPS|Heals)$/);\n    const displayName=rm?rm[1]:r.name;\n    const roleAttr=rm?' data-build-role=\\\"'+rm[2].toLowerCase()+'\\\"':'';\n    const techniqueSwaps=TECHNIQUE_SWAP_SCENARIOS[r.techniques.join('|')]||[];\n"""

render_anchor = "      +'<ul><li><b>Offensive:</b> '+esc(r.offensive)+'</li><li><b>Defensive:</b> '+esc(r.defensive)+'</li></ul>'\n      +'</article>';"
render_add = "      +'<ul><li><b>Offensive:</b> '+esc(r.offensive)+'</li><li><b>Defensive:</b> '+esc(r.defensive)+'</li></ul>'\n      +(techniqueSwaps.length?'<div class=\\\"techniqueSwapScenarios\\\"><span>Technique swaps</span><div>'+techniqueSwaps.map(s=>'<p><b>'+esc(s[0])+':</b> '+esc(s[1])+' → '+esc(s[2])+'</p>').join('')+'</div></div>':'')\n      +'</article>';"

for path in paths:
    text = path.read_text(encoding='utf-8')
    for old, new, label in [
        (css_anchor, css_add, 'swap CSS'),
        (data_anchor, data_add, 'swap data'),
        (fn_anchor, fn_add, 'renderer setup'),
        (render_anchor, render_add, 'renderer output'),
    ]:
        count = text.count(old)
        if count != 1:
            raise SystemExit(f'{path}: expected one {label} anchor, found {count}')
        text = text.replace(old, new, 1)
    path.write_text(text, encoding='utf-8')

print('added conditional Technique swap scenarios to active build cards')
