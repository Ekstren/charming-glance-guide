from pathlib import Path

p = Path('.github/build-fantomons-inject.html')
s = p.read_text()

new_presets = r'''  const ROLE_PRESETS={
    Berserker:[
      role('Solo','General S1 PvE / progression',["Hunter's Judgment",'Sunset Sword','Eclipse Slash','Lion Combo'],['Insightful Eye','Blade of Judgment','Blade Siphon','Indomitable Will'],'Indomitable Will → Blazing Clash when the stage cannot threaten you.','Low Crit: Blade Siphon → Blade of Lament. This is the published T3 generic PvE core.'),
      role('Dungeon','General dungeon clear / grouping',["Hunter's Judgment",'Sunset Sword','Eclipse Slash','Lion Combo'],['Insightful Eye','Blade of Judgment','Blade Siphon','Indomitable Will'],'Indomitable Will → Blazing Clash when your party already covers survival.','Keep Hunter’s Judgment for grouping and Indomitable Will when pushing above your power.','Guide core'),
      role('Boss','Dragon / long single-target damage',['Flame Aura','Sunset Sword','Eclipse Slash','Lion Combo'],['Insightful Eye','Blade of Judgment','Blazing Clash','Crit Mastery'],'This is already the published greedier Dragon damage setup.','If the boss can kill you, Blazing Clash or Crit Mastery → Indomitable Will.','Guide core'),
      role('PvP','Burst, reach and survival',['Darkness Descends','Lion Combo','Eclipse Slash','Sunset Sword'],['Insightful Eye','Blade of Judgment','Frame of Battles','Indomitable Will'],'Keep the published PvP core; in favorable matchups you can greed a damage charm over Indomitable Will.','For 2v2/4v4, Lion Combo → Hunter’s Judgment for grouping.','Guide core')
    ],
    Paladin:[
      role('Solo','General S1 PvE / tank-and-spank',['Luminous Shield','Forceful Charge','Star Shattering Slash','Heart of Challenge'],['Rebound','Counter Blade','Block Mastery','Block Awareness'],'Luminous Shield → Valor Surge once survival is comfortable.','Use the published generic PvE counter/block core for progression.','Guide core'),
      role('Dungeon','Party-first tanking',['Valor Surge','Heart of Challenge','Luminous Shield','Desperate Protection'],['Iron Fortress','Block Mastery','Block Awareness','Stone Skin'],'Luminous Shield → Lunarwater Threads only when the group is already safe.','This is the published dungeon tank setup; prioritize keeping the party alive.','Guide core'),
      role('Boss','Boss damage / off-tank',['Valor Surge','Leap Attack','Heavy Impact','Star Shattering Slash'],['Strength Rules','Insightful Eye','Pursuit of Victory',"Warrior's Essence"],'Use this only when another tank or your gear already covers survival; it is the damage-oriented boss setup seen in current build guides.','If survival becomes the limiter, fall back to the Dungeon tank build.','Multi-guide boss core'),
      role('PvP','Team protection and anti-burst',['Star Shattering Slash','Heart of Challenge','Luminous Shield','Desperate Protection'],['Iron Fortress','Block Mastery','Block Awareness','Stone Skin'],'Star Shattering Slash gives you real threat while the rest of the kit protects the team.','Keep the full defensive package in 4v4; this role is derived from the guide’s team-PvP recommendations.','Guide-derived PvP')
    ],
    Archmage:[
      role('Solo','General AoE / mixed-wave progression',['Divine Wrath','Howling Hurricane','Meteoric Flames','Lightning Chain'],['Rapid Cast','Void Bubble','Mana Surge','Radiant Sear'],'Mana Surge can flex to Repelling Wind, Lightning Mystery, or Elemental Harmony if it tests better.','Keep Void Bubble when the stage can reach you before your burst.','Guide core'),
      role('Dungeon','Turn-one AoE room clearing',['Divine Wrath','Howling Hurricane','Meteoric Flames','Lightning Chain'],['Rapid Cast','Void Bubble','Mana Surge','Radiant Sear'],'If the party fully covers survival, Void Bubble → your best tested offensive charm.','Rapid Cast + the AoE core is the reason Archmage excels at dungeon wave clear.','Guide core'),
      role('Boss','Single-target / large-boss damage',['Divine Wrath','Howling Hurricane','Meteoric Flames',"Wind's Delight"],['Rapid Cast','Void Bubble','Mana Surge','Radiant Sear'],'On smaller bosses, Divine Wrath → Tempest Sphere for more reliable targeting.','Keep Void Bubble unless the boss cannot realistically threaten you.','Guide core'),
      role('PvP','Reliable burst without Divine Wrath RNG',['Tempest Sphere','Howling Hurricane','Meteoric Flames',"Wind's Delight"],['Rapid Cast','Void Bubble','Mana Surge','Radiant Sear'],'This follows the guide recommendation to use the ST setup without Divine Wrath in PvP.','Do not drop Void Bubble unless you can reliably act first and survive.','Guide-derived PvP')
    ],
    Arcanist:[
      role('Solo','AoE Dark DoT progression',['Mana Blast','Dark Bullet','Abyssal Hand','Shadow Impact'],['Shadow Vengeance',"Night's Blessing",'Shadow Erosion','Linked Misfortune'],'Use the published AoE Erosion core for solo and mixed-wave content.','If survival is the limiter, flex the lowest-impact damage charm rather than breaking the DoT engine.','Guide core'),
      role('Dungeon','Healing / party sustain',['Void Blessing','Waterling Summon','Radiant Restoration','Frenzy Totem'],['Resurrection','Healing Mastery','Overhealing','Flex'],'Use the Flex charm for party damage/utility when healing is comfortable.','If another healer is already covering the party, switch to the AoE DPS build.','Guide core'),
      role('Boss','Single-target Dark DoT',['Mana Blast','Dark Bullet','Abyssal Hand','Shadow of Termination'],['Shadow Vengeance',"Night's Blessing",'Shadow Erosion','Linked Misfortune'],'This is the published single-target Erosion setup; Effect Hit Rate matters heavily.','If Erosion consistency is poor, fix EHR before assuming the loadout itself is weak.','Guide core'),
      role('PvP','Healing / survival support',['Void Blessing','Waterling Summon','Radiant Restoration','Frenzy Totem'],['Resurrection','Healing Mastery','Overhealing','Shadow Vengeance'],'Shadow Vengeance fills the healer Flex slot when enemy burst is the main threat.','If you are not being focused, use a utility/support charm in the Flex slot instead.','Guide-derived PvP')
    ],
    Conqueror:[
      role('Solo','S2 generic all-content core',['Flash Fire','Flame Aura','Flickering Blade','Blade Storm'],['Insightful Eye','Piercing Assault','Tactical Adaptation','Indomitable Will'],'High Crit: Insightful Eye → Soul Breaker. If survival is solved, Indomitable Will → Soul Splash.','This is the published T4 generic core and should be your default starting point.','Guide core'),
      role('Dungeon','Aggressive S2 dungeon clear',['Flash Fire','Flame Aura','Flickering Blade','Blade Storm'],['Insightful Eye','Piercing Assault','Tactical Adaptation','Soul Splash'],'High Crit: Insightful Eye → Soul Breaker. Soul Splash is the greed slot when the dungeon cannot kill you.','If the dungeon is dangerous, Soul Splash → Indomitable Will and you are back on the generic core.','Guide-derived dungeon'),
      role('Boss','Dragon / sustained single-target',['Flame Aura','Blade Storm','Flash Fire','Flickering Blade'],['Insightful Eye','Piercing Assault','Tactical Adaptation','Blazing Clash'],'High Crit: Insightful Eye → Crit Mastery for Dragon.','If survival becomes the actual DPS loss, Blazing Clash → Indomitable Will.','Guide core'),
      role('PvP','Mobility, dispel and durability',['Flash Fire','Darkness Descends','Flickering Blade','Blade Storm'],['Insightful Eye','Piercing Assault','Tactical Adaptation','Indomitable Will'],'High Crit: Insightful Eye → Soul Breaker. Darkness Descends replaces Flame Aura for mobility/dispel.','Always keep Indomitable Will in PvP.','Guide core')
    ],
    Guardian:[
      role('Solo','Flexible S2 PvE tank-and-spank',['Desperate Protection','Luminous Shield','Forceful Charge','Star Shattering Slash'],['Rebound','Holy Aegis','Block Mastery','Block Awareness'],'Luminous Shield → Valor Surge when you want more damage and can afford less safety.','This is the published secondary PvE build and the best all-purpose solo shell.','Guide core'),
      role('Dungeon','Primary party tank',['Valor Surge','Heart of Challenge','Luminous Shield','Desperate Protection'],['Iron Will','Holy Aegis','Block Awareness','Soul Protection'],'Need more Taunt: Valor Surge → Hamper Strike. Need more damage: Desperate Protection → Swirling Blade or Star Shattering Slash.','If the team still dies, flex Iron Fortress into the charm set.','Guide core'),
      role('Boss','Dragon / Chaos / Guild support',['Valor Surge','Leap Attack','Holy Purification','Lunarwater Threads'],['Frigid Aura','Frigid Glint','Iron Fortress','Oath of Vigil'],'No important buff to dispel: Holy Purification → damage. Lunarwater Threads → Seismic Tide for steadier Cold stacking.','This is the published Support Knight boss/group setup.','Guide core'),
      role('PvP','Taunt and ally protection',['Hamper Strike','Heart of Challenge','Luminous Shield','Desperate Protection'],['Iron Will','Holy Aegis','Iron Fortress','Oath of Vigil'],'Hamper Strike adds reliable Taunt; Iron Fortress and Oath of Vigil are explicitly strongest in group PvP.','Keep the defense-first shell; only add damage if your team no longer needs protection.','Guide-derived PvP')
    ],
    Destroyer:[
      role('Solo','General S2 AoE / mixed fights',['Formation Breaker','Howling Hurricane','Meteoric Flames','Wind Blade Spiral'],['Rapid Cast','Void Bubble','Cyclone Lament','Radiant Sear'],'If you heavily outgear the content, Void Bubble → offense.','This is the published AoE core and works well into mixed boss + mob fights.','Guide core'),
      role('Dungeon','Fire AoE for dense mob waves',['Formation Breaker','Fiery Star Trail','Fireball','Meteoric Flames'],['Rapid Cast','Void Bubble','Explosive Spirit','Fiery Burst'],'This is the dedicated horde-clear setup; use the generic AoE build when the room is less dense or more mixed.','Keep Void Bubble if you need one extra turn to survive the pull.','Guide core'),
      role('Boss','Single-target boss damage',['Formation Breaker','Divine Wrath','Wind Blade Spiral','Thunder of Judgment'],['Rapid Cast','Void Bubble','Mana Surge','Radiant Sear'],'Wind Blade Spiral → Tempest Sphere if it tests better. Small boss: Divine Wrath → Meteoric Flames.','Mana Surge → Overload Protection if a little more safety is enough to stabilize the fight.','Guide core'),
      role('PvP','Conservative burst / survival core',['Formation Breaker','Howling Hurricane','Meteoric Flames','Wind Blade Spiral'],['Rapid Cast','Void Bubble','Mana Surge','Radiant Sear'],'No major guide publishes a settled T4 Destroyer PvP-only build, so this keeps the reliable general burst core instead of inventing a gimmick.','Keep Void Bubble; swap only after testing against your actual bracket.','Conservative adaptation')
    ],
    Dominator:[
      role('Solo','AoE Dark DPS',['Mana Blast','Dark Bullet','Abyssal Hand','Shadow Impact'],['Shadow Vengeance',"Night's Blessing",'Shadow Erosion','Linked Misfortune'],'This is still the published AoE core in T4 because Dominator gains no better AoE package.','High Effect Hit Rate is important; do not force Erosion with poor EHR.','Guide core'),
      role('Dungeon','Healing / support',['Waterling Summon','Rejuvenating Rain','Radiant Restoration','Frenzy Totem'],['Phantom Light','Healing Mastery','Overhealing','Resurrection'],'If nobody is dying, Resurrection → Mantra of Blessings. Need more raw healing: Frenzy Totem → Healing Touch.','Phantom Light is mandatory for the T4 healer identity.','Guide core'),
      role('Boss','Single-target Dark DPS',['Dark Bullet','Dark Starburst','Chaos Rune','Shadow of Termination'],['Shadow Vengeance',"Night's Blessing",'Shadow Erosion','Linked Misfortune'],'With high EHR, Chaos Rune → Mana Blast for a higher Erosion ceiling.','Use the direct-damage hybrid as listed when Erosion landing is inconsistent.','Guide core'),
      role('PvP','Healing / survival support',['Waterling Summon','Rejuvenating Rain','Radiant Restoration','Frenzy Totem'],['Phantom Light','Healing Mastery','Overhealing','Shadow Vengeance'],'If you are not being focused, Shadow Vengeance → Mantra of Blessings or Resurrection based on team needs.','This deliberately treats T4 Dominator as support first rather than forcing a weak damage PvP identity.','Guide-derived PvP')
    ]
  };'''

a = s.index('  const ROLE_PRESETS={')
b = s.index('\n\n  const FANTO={', a)
s = s[:a] + new_presets + s[b:]

s = s.replace('/* BUILD_FANTOMON_PAIRS_V2_ROLE_PRESETS */', '/* BUILD_FANTOMON_PAIRS_V4_CLASS_ROLES_MAIN_ALT */')
if '.builds .buildRoleTabs{display:none!important}' not in s:
    s = s.replace('/* BUILD_FANTOMON_PAIRS_V4_CLASS_ROLES_MAIN_ALT */\n', '/* BUILD_FANTOMON_PAIRS_V4_CLASS_ROLES_MAIN_ALT */\n.builds .buildRoleTabs{display:none!important}\n', 1)

if "document.querySelectorAll('.builds .buildRoleTabs').forEach(x=>x.remove());" not in s:
    s = s.replace("    if(!cls) return;\n    applyRoleLoadouts(cls);", "    if(!cls) return;\n    document.querySelectorAll('.builds .buildRoleTabs').forEach(x=>x.remove());\n    applyRoleLoadouts(cls);", 1)

# Preserve the user's requested Main + Alt UI. This pass changes build presets only;
# it does not re-rank the underlying Fantomon research.
marker = "      box.innerHTML='<span>Combat Fantomons · ranked</span>'"
if marker in s:
    x = s.index(marker)
    y = s.index("        +'</div>';", x) + len("        +'</div>';")
    replacement = """      const pair=picks.slice(0,2);\n      box.innerHTML='<span>Combat Fantomons</span>'\n        +'<div class=\"fantomonRankList\">'\n        +pair.map((p,i)=>'<div class=\"fantomonPick'+(i===0?' main':'')+'\"><small>'+(i===0?'Main':'Alt')+'</small><b>'+esc(p.name)+'</b><p>'+esc(p.why)+'</p></div>').join('')\n        +'</div>';"""
    s = s[:x] + replacement + s[y:]

p.write_text(s)
