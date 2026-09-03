from pathlib import Path

paths=[Path('index.html'),Path('.github/build-fantomons-inject.html')]

roles={
'Conqueror':[
"      role('Fantasia Ascent','Solo push: high-DEF floors and mixed packs',['Gale Dance','Flash Fire','Flickering Blade','Blade Storm'],['Piercing Assault','Tactical Adaptation','Soul Splash','Indomitable Will'],'Gale Dance improves opening tempo while the T4 damage core handles mixed floors.','Soul Splash + Indomitable Will give the push setup enough sustain for above-power stages.','Community Ascent')"
],
'Guardian':[
"      role('Fantasia Ascent · Tank','Solo push: Block / reflect survival',['Luminous Shield','Forceful Charge','Star Shattering Slash','Desperate Protection'],['Rebound','Holy Aegis','Block Mastery','Soul Protection'],'Luminous Shield and Desperate Protection stabilize hard floors while Rebound turns repeated hits into damage.','Forceful Charge keeps contact and Star Shattering Slash gives the tank setup a real finisher.','Community Ascent')",
"      role('Fantasia Ascent · DPS','Solo push: Water AoE with a safety slot',['Swirling Blade','Lunarwater Threads','Seismic Tide','Raging Maelstrom'],['Frigid Aura','Defensive Assault','Frigid Glint','Potential Rebirth'],'The Water/Cold package clears dense floors while Swirling Blade adds its own shield.','Potential Rebirth keeps the damage setup from folding to a bad burst window.','Prydwen + Ascent')"
],
'Destroyer':[
"      role('Fantasia Ascent','Solo push: mixed damage with Void Bubble safety',['Formation Breaker','Meteoric Flames','Wind Blade Spiral','Thunder of Judgment'],['Rapid Cast','Void Bubble','Cyclone Lament','Radiant Sear'],'Formation Breaker keeps tempo high while Fire, Wind, and Light coverage handles varied floors.','Void Bubble is the default safety slot for pushing above listed power.','Guide-derived Ascent')"
],
'Dominator':[
"      role('Fantasia Ascent · DPS','Solo push: Erosion AoE with Shadow Vengeance safety',['Mana Blast','Dark Bullet','Abyssal Hand','Shadow Impact'],['Shadow Vengeance',\"Night's Blessing\",'Shadow Erosion','Linked Misfortune'],'The AoE Erosion package handles mixed floors and Shadow Vengeance buys time to finish dangerous waves.','Effect Hit Rate still matters whenever the floor depends on Erosion sticking.','Community Ascent')",
"      role('Fantasia Ascent · Heals','Solo push: sustain hybrid for Healing Boost builds',['Rejuvenating Rain','Radiant Restoration','Dark Bullet','Shadow of Termination'],['Phantom Light','Healing Mastery','Shadow Vengeance','Mantra of Blessings'],'Rejuvenating Rain + Radiant Restoration sustain the run while Dark Bullet and Shadow of Termination preserve kill pressure.','Best for accounts already invested into Healing Boost and SPD.','Ascent sustain')"
]
}


def insert_roles(text,cls,next_marker,lines):
    presets_start=text.find('  const ROLE_PRESETS={')
    if presets_start<0: raise SystemExit('missing ROLE_PRESETS')
    presets_end=text.find('\n  };\n\n\n  const META_CLASSES',presets_start)
    if presets_end<0: raise SystemExit('missing ROLE_PRESETS end')
    start=text.find(f'\n    {cls}:[',presets_start,presets_end)
    if start<0: raise SystemExit(f'missing active {cls} preset block')
    if next_marker:
        end=text.find(next_marker,start,presets_end)
        if end<0: raise SystemExit(f'missing end marker for active {cls}')
    else:
        end=presets_end
    close=text.rfind('\n    ]',start,end)
    if close<0: raise SystemExit(f'missing close for active {cls}')
    if "role('Fantasia Ascent" in text[start:end]:
        raise SystemExit(f'{cls} already has Fantasia Ascent')
    return text[:close]+',\n'+',\n'.join(lines)+text[close:]

tech_entries="""
    'Fantasia Ascent|Gale Dance|Flash Fire|Flickering Blade|Blade Storm':[
      ['Need more wave damage','Gale Dance','Flame Aura'],
      ['Need Dispel / repositioning','Flash Fire','Darkness Descends']
    ],
    'Fantasia Ascent · Tank|Luminous Shield|Forceful Charge|Star Shattering Slash|Desperate Protection':[
      ['Need more damage','Forceful Charge','Swirling Blade'],
      ['Dense mob floor','Star Shattering Slash','Lunarwater Threads']
    ],
    'Fantasia Ascent · DPS|Swirling Blade|Lunarwater Threads|Seismic Tide|Raging Maelstrom':[
      ['Boss floor','Raging Maelstrom','Star Shattering Slash']
    ],
    'Fantasia Ascent|Formation Breaker|Meteoric Flames|Wind Blade Spiral|Thunder of Judgment':[
      ['Dense mob floor','Thunder of Judgment','Howling Hurricane'],
      ['Boss floor','Meteoric Flames','Divine Wrath']
    ],
    'Fantasia Ascent · DPS|Mana Blast|Dark Bullet|Abyssal Hand|Shadow Impact':[
      ['Boss floor','Shadow Impact','Shadow of Termination']
    ],
    'Fantasia Ascent · Heals|Rejuvenating Rain|Radiant Restoration|Dark Bullet|Shadow of Termination':[
      ['Dense mob floor','Shadow of Termination','Abyssal Hand'],
      ['Need more healing','Dark Bullet','Healing Touch']
    ]
""".strip('\n')

charm_entries="""
    'Fantasia Ascent|Piercing Assault|Tactical Adaptation|Soul Splash|Indomitable Will':[
      ['High Crit + survival is comfortable','Indomitable Will','Soul Breaker']
    ],
    'Fantasia Ascent · Tank|Rebound|Holy Aegis|Block Mastery|Soul Protection':[
      ['Low Block','Soul Protection','Block Awareness']
    ],
    'Fantasia Ascent · DPS|Frigid Aura|Defensive Assault|Frigid Glint|Potential Rebirth':[
      ['Survival is comfortable','Potential Rebirth','Pursuit of Victory']
    ],
    'Fantasia Ascent|Rapid Cast|Void Bubble|Cyclone Lament|Radiant Sear':[
      ['Survival is comfortable','Void Bubble','Mana Surge']
    ],
    'Fantasia Ascent · Heals|Phantom Light|Healing Mastery|Shadow Vengeance|Mantra of Blessings':[
      ['Need more raw sustain','Mantra of Blessings','Overhealing']
    ]
""".strip('\n')


def insert_object_entries(text,obj_marker,next_marker,entries):
    start=text.find(obj_marker)
    if start<0: raise SystemExit(f'missing {obj_marker}')
    end=text.find(next_marker,start)
    if end<0: raise SystemExit(f'missing next marker after {obj_marker}')
    close=text.rfind('\n  };',start,end)
    if close<0: raise SystemExit(f'missing object close for {obj_marker}')
    if 'Fantasia Ascent|' in text[start:end]:
        raise SystemExit(f'{obj_marker} already has Fantasia entries')
    return text[:close]+',\n'+entries+text[close:]

for path in paths:
    text=path.read_text(encoding='utf-8')
    old_css='.builds .metaBuildTabs{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:5px;flex:1;min-width:0}'
    new_css='.builds .metaBuildTabs{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:5px;flex:1;min-width:0}'
    if text.count(old_css)!=1: raise SystemExit(f'{path}: desktop meta tab CSS count={text.count(old_css)}')
    text=text.replace(old_css,new_css,1)
    old_modes="const META_MODES=['Dungeon','Crucible / Conquest','Arena','Tournament'];"
    new_modes="const META_MODES=['Dungeon','Crucible / Conquest','Arena','Fantasia Ascent','Tournament'];"
    if text.count(old_modes)!=1: raise SystemExit(f'{path}: META_MODES count={text.count(old_modes)}')
    text=text.replace(old_modes,new_modes,1)

    text=insert_roles(text,'Conqueror','\n    Guardian:[',roles['Conqueror'])
    text=insert_roles(text,'Guardian','\n    Destroyer:[',roles['Guardian'])
    text=insert_roles(text,'Destroyer','\n    Dominator:[',roles['Destroyer'])
    text=insert_roles(text,'Dominator',None,roles['Dominator'])

    old_rolekey="    if(t==='crucible / conquest') return 'Boss';\n    if(t.startsWith('arena')) return 'Arena';"
    new_rolekey="    if(t==='crucible / conquest') return 'Boss';\n    if(t==='fantasia ascent') return 'Solo';\n    if(t.startsWith('arena')) return 'Arena';"
    if text.count(old_rolekey)!=1: raise SystemExit(f'{path}: roleKey anchor count={text.count(old_rolekey)}')
    text=text.replace(old_rolekey,new_rolekey,1)

    text=insert_object_entries(text,'  const TECHNIQUE_SWAP_SCENARIOS={','  const CHARM_SWAP_SCENARIOS={',tech_entries)
    text=insert_object_entries(text,'  const CHARM_SWAP_SCENARIOS={','  const FANTO={',charm_entries)
    path.write_text(text,encoding='utf-8')

smoke=Path('scripts/site_smoke_test.mjs')
text=smoke.read_text(encoding='utf-8')
anchor="""}

// Dominator keeps its DPS / Heals switch, role-specific slot stats, and a separate
"""
if text.count(anchor)!=1: raise SystemExit(f'smoke Fantasia insertion anchor count={text.count(anchor)}')
block=r'''// Fantasia Ascent is a first-class solo-push mode for every current S2 class.
await waitBuild('Conqueror');
assert(await page.locator('#buildContent .metaBuildTabs button').count()===5, 'build activity selector does not contain five modes');
await page.locator('#buildContent .metaBuildTabs button[data-meta-mode="Fantasia Ascent"]').click();
await page.waitForTimeout(80);
let fantasiaTitles=await buildTitles();
assert(fantasiaTitles.length===1 && /^Fantasia Ascent/i.test(fantasiaTitles[0]||''), `Conqueror Fantasia build missing: ${fantasiaTitles.join(' | ')}`);

await waitBuild('Guardian');
await page.locator('#buildContent .metaBuildTabs button[data-meta-mode="Fantasia Ascent"]').click();
await page.locator('#buildContent button[data-guardian-mode="tank"]').click();
await page.waitForTimeout(80);
fantasiaTitles=await buildTitles();
assert(fantasiaTitles.length===1 && /^Fantasia Ascent/i.test(fantasiaTitles[0]||''), `Guardian Tank Fantasia build missing: ${fantasiaTitles.join(' | ')}`);
await page.locator('#buildContent button[data-guardian-mode="dps"]').click();
await page.waitForTimeout(80);
fantasiaTitles=await buildTitles();
assert(fantasiaTitles.length===1 && /^Fantasia Ascent/i.test(fantasiaTitles[0]||''), `Guardian DPS Fantasia build missing: ${fantasiaTitles.join(' | ')}`);

await waitBuild('Destroyer');
await page.locator('#buildContent .metaBuildTabs button[data-meta-mode="Fantasia Ascent"]').click();
await page.waitForTimeout(80);
fantasiaTitles=await buildTitles();
assert(fantasiaTitles.length===1 && /^Fantasia Ascent/i.test(fantasiaTitles[0]||''), `Destroyer Fantasia build missing: ${fantasiaTitles.join(' | ')}`);

await waitBuild('Dominator');
await page.locator('#buildContent .metaBuildTabs button[data-meta-mode="Fantasia Ascent"]').click();
await page.locator('#buildContent button[data-dominator-mode="dps"]').click();
await page.waitForTimeout(80);
fantasiaTitles=await buildTitles();
assert(fantasiaTitles.length===1 && /^Fantasia Ascent/i.test(fantasiaTitles[0]||''), `Dominator DPS Fantasia build missing: ${fantasiaTitles.join(' | ')}`);
await page.locator('#buildContent button[data-dominator-mode="heals"]').click();
await page.waitForTimeout(80);
fantasiaTitles=await buildTitles();
assert(fantasiaTitles.length===1 && /^Fantasia Ascent/i.test(fantasiaTitles[0]||''), `Dominator Heals Fantasia build missing: ${fantasiaTitles.join(' | ')}`);
// Restore the existing Dominator smoke assumptions.
await page.locator('#buildContent .metaBuildTabs button[data-meta-mode="Dungeon"]').click();
await page.locator('#buildContent button[data-dominator-mode="dps"]').click();
await page.waitForTimeout(80);

'''
text=text.replace(anchor,'}\n\n'+block+'// Dominator keeps its DPS / Heals switch, role-specific slot stats, and a separate\n',1)
text=text.replace('rich S2 Builds + slot stats + Technique/Charm pair + Main/two-Alt Fantomons + Dominator roles/PvP refs + mobile stack','rich S2 Builds + Fantasia Ascent + slot stats + Technique/Charm pair + Main/two-Alt Fantomons + Dominator roles/PvP refs + mobile stack',1)
smoke.write_text(text,encoding='utf-8')

print('added Fantasia Ascent mode and solo-push builds')
