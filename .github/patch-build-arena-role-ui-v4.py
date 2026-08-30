from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')
MARK='BUILD_ARENA_ROLE_UI_REPAIR_V4'
if MARK in s:
    print('already patched')
    raise SystemExit(0)

# 1) Keep the existing PvE source intact and append canonical Arena/Tournament cards
#    at render time. This prevents the Fantomon renderer from deleting PvP cards.
needle = "  const FANTO={\n"
if needle not in s:
    raise SystemExit('FANTO anchor not found')

pvp = r'''  /* BUILD_ARENA_ROLE_UI_REPAIR_V4
     Arena/Tournament belong to the same canonical loadout renderer as PvE. Keeping
     them here prevents later Fantomon/build polishing passes from replacing them. */
  const PVP_ROLE_PRESETS={
    Berserker:[
      role('Arena','Burst, reach and survival',['Darkness Descends','Lion Combo','Eclipse Slash','Sunset Sword'],['Insightful Eye','Blade of Judgment','Frame of Battles','Indomitable Will'],'Indomitable Will → Blazing Clash when the matchup is safe enough to greed damage.','Keep Indomitable Will when survival or anti-burst value matters.','Guide consensus'),
      role('Tournament','Fast team-fight pressure',["Hunter's Judgment",'Flame Aura','Eclipse Slash','Sunset Sword'],['Insightful Eye','Blade of Judgment','Frame of Battles','Indomitable Will'],'Indomitable Will → Blazing Clash when your team already protects you.','Keep Indomitable Will for safer tournament rounds.','Guide consensus')
    ],
    Paladin:[
      role('Arena','Control, pressure and Block',['Luminous Shield','Leap Attack','Star Shattering Slash','Valor Surge'],['Rebound','Block Mastery','Block Awareness','Stone Skin'],'Stone Skin → a damage/counter charm when your defenses are already comfortable.','Keep Stone Skin for maximum durability.','Guide consensus'),
      role('Tournament','Team tank / protection',['Valor Surge','Heart of Challenge','Luminous Shield','Desperate Protection'],['Iron Fortress','Block Mastery','Block Awareness','Stone Skin'],'Stone Skin → an offensive flex only when the enemy cannot break you.','This is already the defense-first tournament shell.','Guide consensus')
    ],
    Archmage:[
      role('Arena','Immediate ranged pressure',['Tempest Sphere','Howling Hurricane','Meteoric Flames',"Wind's Delight"],['Rapid Cast','Void Bubble','Mana Surge','Radiant Sear'],'Void Bubble → an offensive charm if you can safely play full burst.','Keep Void Bubble when enemy burst can reach you.','Guide consensus'),
      role('Tournament','AoE team-fight damage',['Tempest Sphere','Howling Hurricane','Meteoric Flames','Lightning Chain'],['Rapid Cast','Void Bubble','Mana Surge','Radiant Sear'],'Void Bubble → an offensive charm if your team provides enough protection.','Keep Void Bubble for safer tournament rounds.','Guide consensus')
    ],
    Arcanist:[
      role('Arena','Erosion pressure with single-target finish',['Mana Blast','Dark Bullet','Abyssal Hand','Shadow of Termination'],['Shadow Vengeance',"Night's Blessing",'Shadow Erosion','Linked Misfortune'],'Shadow Vengeance → a greedier damage charm when you are not being focused.','Keep Shadow Vengeance when surviving the first burst is important.','Guide consensus'),
      role('Tournament','Hybrid support / sub-DPS',['Mana Blast','Abyssal Hand','Radiant Restoration','Frenzy Totem'],['Resurrection','Shadow Vengeance','Shadow Erosion','Linked Misfortune'],'Resurrection → a damage/support charm if your team does not need the revive safety net.','Keep Resurrection for progression or fragile teams.','Hybrid support')
    ],
    Conqueror:[
      role('Arena','Mobility, burst and anti-burst',['Darkness Descends','Doom Blade','Flickering Blade','Blade Storm'],['Piercing Assault','Tactical Adaptation','Soul Breaker','Indomitable Will'],'Indomitable Will → Insightful Eye / another damage charm when the matchup is safe.','Keep Indomitable Will against real burst threats.','Guide consensus'),
      role('Tournament','Fast team-fight pressure',['Flash Fire','Darkness Descends','Flickering Blade','Blade Storm'],['Insightful Eye','Piercing Assault','Tactical Adaptation','Indomitable Will'],'Indomitable Will → Soul Breaker when your team already covers survival.','Keep Indomitable Will for safer tournament rounds.','Guide consensus')
    ],
    Guardian:[
      role('Arena','Block, control and disruption',['Luminous Shield','Forceful Charge','Star Shattering Slash','Desperate Protection'],['Rebound','Holy Aegis','Block Mastery','Block Awareness'],'Block Awareness → an offensive flex if your defensive stats are already excessive.','Keep the full Block shell when holding the line matters most.','Guide consensus'),
      role('Tournament','Team tank / peel',['Hamper Strike','Heart of Challenge','Luminous Shield','Desperate Protection'],['Iron Will','Holy Aegis','Iron Fortress','Oath of Vigil'],'Oath of Vigil → an offensive/support flex only when team survival is solved.','This is already the defense-first tournament setup.','Guide consensus')
    ],
    Destroyer:[
      role('Arena','Immediate caster pressure',['Tempest Sphere','Wind Blade Spiral',"Wind's Delight",'Howling Hurricane'],['Cyclone Lament','Repelling Wind',"Wind's Shadow",'Void Bubble'],'Void Bubble → Rapid Cast / another damage charm if you can safely full-send.','Keep Void Bubble when enemy burst can reach you.','Guide consensus'),
      role('Tournament','AoE team-fight burst',['Formation Breaker','Howling Hurricane','Meteoric Flames','Wind Blade Spiral'],['Rapid Cast','Void Bubble','Cyclone Lament','Radiant Sear'],'Void Bubble → a damage charm if your team provides enough protection.','Keep Void Bubble for safer tournament rounds.','Guide consensus')
    ],
    Dominator:[
      role('Arena','Dark pressure with utility',['Abyssal Hand','Dark Starburst','Dark Bullet','Shadow of Termination'],['Linked Misfortune','Shadow Erosion','Mantra of Blessings','Shadow Vengeance'],'Shadow Vengeance → a greedier damage charm when you are not being focused.','Keep Shadow Vengeance when surviving the opener matters.','Guide consensus'),
      role('Tournament','Hybrid support / sub-DPS',['Decoy Clone','Frenzy Totem','Dark Starburst','Abyssal Hand'],['Mantra of Blessings','Resurrection','Shadow Vengeance',"Night's Blessing"],'Resurrection → Linked Misfortune / another damage flex if your team does not need revive insurance.','Keep Resurrection for fragile teams and progression rounds.','Hybrid support')
    ]
  };

'''
s = s.replace(needle, pvp + needle, 1)

# 2) The canonical loadout renderer must combine PvE + Arena/Tournament instead of
#    replacing the whole grid with only ROLE_PRESETS.
old = """  function applyRoleLoadouts(cls){\n    const presets=ROLE_PRESETS[cls];\n    const grid=document.querySelector('.builds .buildGrid');\n    if(!presets||!grid) return;\n"""
new = """  function applyRoleLoadouts(cls){\n    const presets=[...(ROLE_PRESETS[cls]||[]),...(PVP_ROLE_PRESETS[cls]||[])];\n    const grid=document.querySelector('.builds .buildGrid');\n    if(!presets.length||!grid) return;\n"""
if old not in s:
    raise SystemExit('applyRoleLoadouts anchor not found')
s = s.replace(old,new,1)

# 3) Teach Fantomon role mapping about Arena/Tournament. Previously those branches
#    existed in picksFor(), but roleKey() could never return them.
old = """  function roleKey(title){\n    const t=(title||'').toLowerCase();\n    if(t.startsWith('pvp')) return 'PvP';\n"""
new = """  function roleKey(title){\n    const t=(title||'').toLowerCase();\n    if(t==='arena'||t.startsWith('arena ')) return 'Arena';\n    if(t==='tournament'||t.startsWith('tournament ')) return 'Tournament';\n    if(t.startsWith('pvp')) return 'PvP';\n"""
if old not in s:
    raise SystemExit('roleKey anchor not found')
s = s.replace(old,new,1)

# 4) Arcanist's Tournament Fantomon pair is intentionally hybrid-specific.
old = """    if(role==='Tournament'){\n      return pools.Tournament||pools.PvP||pools.Dungeon||[];\n    }\n"""
new = """    if(role==='Tournament'){\n      if(cls==='Arcanist') return [\n        pick('Nyxarchon','Main hybrid Tournament pick: adds damage and DEF shred while Arcanist supplies healing/support.'),\n        pick('Sylvaerie','Alt hybrid pick: permanent ATK + SPD improves both support tempo and sub-DPS output.')\n      ];\n      return pools.Tournament||pools.PvP||pools.Dungeon||[];\n    }\n"""
if old not in s:
    raise SystemExit('Tournament picks anchor not found')
s = s.replace(old,new,1)

# 5) BUILD_STATS_ROLES_V3 and BUILD_ROLE_TOGGLE_V2 were both creating role tabs.
#    Keep V2 as the single interactive control; V3 only updates the priority panels.
start = s.find('function applyBuildRole(root,name,mode){')
end = s.find('\n\nfunction polishBuildLayout(){', start)
if start < 0 or end < 0:
    raise SystemExit('applyBuildRole block not found')
replacement = '''function applyBuildRole(root,name,mode){
  if(!BUILD_ROLE_KEYS[name]) return;
  // BUILD_ARENA_ROLE_UI_REPAIR_V4: BUILD_ROLE_TOGGLE_V2 is the one canonical
  // DPS/Heals control. Remove the legacy duplicate and only sync role metadata here.
  root.querySelectorAll('.buildRoleTabs').forEach(x=>x.remove());
  const panels=[...root.querySelectorAll(':scope > .priorityPanel, :scope > .priorityPair > .priorityPanel')];
  const pdata=BUILD_ROLE_PRIORITY[name]?.[mode];
  if(pdata && panels.length>=2){setPriorityPanel(panels[0],pdata[0]);setPriorityPanel(panels[1],pdata[1]);}
}'''
s = s[:start] + replacement + s[end:]

# 6) DPS/Heals filtering applies only to role-specific PvE cards. Arena/Tournament
#    stay visible in both modes.
old = """      const isHealing=(card.dataset.role||'').toLowerCase()==='healing';\n      card.style.display=(mode==='heals' ? isHealing : !isHealing) ? '' : 'none';\n"""
new = """      const role=(card.dataset.role||'').toLowerCase();\n      const alwaysVisible=role==='arena'||role==='tournament';\n      const isHealing=role==='healing';\n      card.style.display=alwaysVisible ? '' : ((mode==='heals' ? isHealing : !isHealing) ? '' : 'none');\n"""
if old not in s:
    raise SystemExit('applyModeVisibility anchor not found')
s = s.replace(old,new,1)

# CSS guard: even if an old DOM survives briefly during mutation reconciliation,
# never display the legacy duplicate tab set.
css_anchor='<!-- BUILD_ROLE_TOGGLE_START -->\n<style>'
if css_anchor not in s:
    raise SystemExit('role toggle style anchor not found')
s = s.replace(css_anchor, "<!-- BUILD_ROLE_TOGGLE_START -->\n<style>\n/* BUILD_ARENA_ROLE_UI_REPAIR_V4: only .buildModeTabs is interactive. */\n.buildRoleTabs{display:none!important}\n", 1)

p.write_text(s,encoding='utf-8')
print('patched build Arena/Tournament and role UI')
