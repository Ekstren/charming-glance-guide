from pathlib import Path

p = Path('.github/build-fantomons-inject.html')
s = p.read_text()

new_presets = r'''  const ROLE_PRESETS={
    Berserker:[
      role('Generic PvE','Default S1 progression and general PvE',["Hunter's Judgment",'Sunset Sword','Eclipse Slash','Lion Combo'],['Insightful Eye','Blade of Judgment','Blade Siphon','Indomitable Will'],'If survival is already solved, Indomitable Will → a damage charm.','Low Crit: Blade Siphon → Blade of Lament.','Guide consensus'),
      role('Dragon','Long single-target / Dragon damage',['Flame Aura','Sunset Sword','Eclipse Slash','Lion Combo'],['Insightful Eye','Blade of Judgment','Blazing Clash','Crit Mastery'],'This is the dedicated damage setup for Dragon and similar long single-target fights.','If the boss can actually kill you, replace one greed charm with Indomitable Will.','Guide consensus'),
      role('PvP','Mobility, burst and cheat-death',['Darkness Descends','Lion Combo','Eclipse Slash','Sunset Sword'],['Insightful Eye','Blade of Judgment','Frame of Battles','Indomitable Will'],'For 2v2/4v4, Lion Combo → Hunter’s Judgment when grouping is more valuable.','Keep Indomitable Will for PvP.','Guide consensus')
    ],
    Paladin:[
      role('Dungeon Tank','Primary party-tank setup',['Valor Surge','Heart of Challenge','Luminous Shield','Desperate Protection'],['Iron Fortress','Block Mastery','Block Awareness','Stone Skin'],'If survival is comfortable, Luminous Shield → Lunarwater Threads for damage and pull utility.','This is the defense-first setup for difficult dungeons and also maps well to team PvP.','Guide consensus'),
      role('Water Offensive','AoE-oriented Water / counter damage',['Guardian Ring','Lunarwater Threads','Frostbite Blossom','Heart of Challenge'],['Ripple Impact','Defensive Assault','Pursuit of Victory','Insightful Eye'],'Use when you need real damage instead of maximum party protection.','If you die too easily, move back toward the Dungeon Tank shell or add Potential Rebirth.','Prydwen core'),
      role('Boss DPS / Off-Tank','Damage-oriented boss setup',['Valor Surge','Leap Attack','Heavy Impact','Star Shattering Slash'],['Strength Rules','Insightful Eye','Pursuit of Victory',"Warrior's Essence"],'Use when another tank or your gear already handles survival and the group needs more damage.','If survival becomes the limiter, use Dungeon Tank instead.','Multi-guide')
    ],
    Archmage:[
      role('AoE','Best general wave-clear and mixed-group setup',['Divine Wrath','Howling Hurricane','Meteoric Flames','Lightning Chain'],['Rapid Cast','Void Bubble','Mana Surge','Radiant Sear'],'Mana Surge can flex to Repelling Wind, Lightning Mystery, or Elemental Harmony if one tests better for your account.','Keep Void Bubble unless you completely outgear the content.','Guide consensus'),
      role('Single Target','Boss / concentrated damage',['Divine Wrath','Howling Hurricane','Meteoric Flames',"Wind's Delight"],['Rapid Cast','Void Bubble','Mana Surge','Radiant Sear'],'On smaller bosses, Divine Wrath → Tempest Sphere. The Tempest Sphere version is also the better PvP adaptation.','Keep Void Bubble unless survival is irrelevant.','Guide consensus')
    ],
    Arcanist:[
      role('AoE DPS','Dark Erosion for groups and mixed waves',['Mana Blast','Dark Bullet','Abyssal Hand','Shadow Impact'],['Shadow Vengeance',"Night's Blessing",'Shadow Erosion','Linked Misfortune'],'This is the standard T3 AoE Erosion package.','Effect Hit Rate matters; fix EHR before breaking the Erosion core.','Guide consensus'),
      role('Single Target DPS','Boss-focused Dark Erosion',['Mana Blast','Dark Bullet','Abyssal Hand','Shadow of Termination'],['Shadow Vengeance',"Night's Blessing",'Shadow Erosion','Linked Misfortune'],'Use for bosses and other concentrated targets.','If Erosion is unreliable, the problem is usually insufficient Effect Hit Rate.','Guide consensus'),
      role('Healing','Dungeon / group healer',['Void Blessing','Waterling Summon','Radiant Restoration','Frenzy Totem'],['Resurrection','Healing Mastery','Overhealing','Gale Shield'],'Gale Shield is the practical default flex from AllClash; replace it with encounter-specific utility when needed.','This is the dedicated healer/support setup, not a DPS variation.','Guide consensus')
    ],
    Conqueror:[
      role('All-Content','Default S2 build for almost everything',['Flash Fire','Flame Aura','Flickering Blade','Blade Storm'],['Insightful Eye','Piercing Assault','Tactical Adaptation','Indomitable Will'],'High Crit: Insightful Eye → Soul Breaker. If you are safe in PvE, Indomitable Will → Soul Splash. Flame Aura → Darkness Descends for mobility/dispel and PvP.','Always keep Indomitable Will for PvP.','Guide consensus'),
      role('Dragon','Dedicated sustained boss damage',['Flame Aura','Blade Storm','Flash Fire','Flickering Blade'],['Insightful Eye','Piercing Assault','Tactical Adaptation','Blazing Clash'],'Once Crit is high enough, Insightful Eye → Crit Mastery.','If surviving is the real damage loss, Blazing Clash → Indomitable Will.','Guide consensus')
    ],
    Guardian:[
      role('Dungeon Tank','Primary S2 party tank',['Valor Surge','Heart of Challenge','Luminous Shield','Desperate Protection'],['Iron Will','Holy Aegis','Block Awareness','Soul Protection'],'Need more Taunt: Valor Surge → Hamper Strike. Need more damage: Desperate Protection → Swirling Blade or Star Shattering Slash.','If the team still dies, Iron Fortress is the first extra defensive flex.','Prydwen core'),
      role('Water Offensive','Cold-stacking offensive Guardian',['Swirling Blade','Lunarwater Threads','Seismic Tide','Raging Maelstrom'],['Frigid Aura','Defensive Assault','Frigid Glint','Potential Rebirth'],'Use for AoE and content where Guardian needs to contribute meaningful personal damage.','Potential Rebirth is the safety slot; other damage/sustain charms can replace it when appropriate.','Prydwen core'),
      role('Support / Boss','Boss, Chaos and group support',['Valor Surge','Leap Attack','Holy Purification','Lunarwater Threads'],['Frigid Aura','Frigid Glint','Iron Fortress','Oath of Vigil'],'If there is nothing worth dispelling, Holy Purification → damage. Lunarwater Threads → Seismic Tide for steadier Cold stacking.','This is the support setup both Prydwen and AllClash point toward for boss/group content.','Guide consensus')
    ],
    Destroyer:[
      role('AoE','Default S2 mixed-wave damage',['Formation Breaker','Howling Hurricane','Meteoric Flames','Wind Blade Spiral'],['Rapid Cast','Void Bubble','Cyclone Lament','Radiant Sear'],'Best general setup for mixed packs and boss+mob encounters.','Strong accounts can replace Void Bubble with more offense.','Guide consensus'),
      role('Single Target','Boss-focused Destroyer',['Formation Breaker','Divine Wrath','Wind Blade Spiral','Thunder of Judgment'],['Rapid Cast','Void Bubble','Mana Surge','Radiant Sear'],'Wind Blade Spiral → Tempest Sphere if it tests better; on small bosses Divine Wrath → Meteoric Flames.','Mana Surge → Overload Protection when a little extra survival is enough to stabilize the fight.','Guide consensus'),
      role('Fire AoE','Dedicated horde-clear setup',['Formation Breaker','Fiery Star Trail','Fireball','Meteoric Flames'],['Rapid Cast','Void Bubble','Explosive Spirit','Fiery Burst'],'Use specifically for dense mob waves; Fiery Burst is the engine of the build.','Do not default to this against bosses or small packs just because it is a distinct element build.','Guide consensus')
    ],
    Dominator:[
      role('AoE DPS','Legacy T3 Erosion remains the T4 AoE build',['Mana Blast','Dark Bullet','Abyssal Hand','Shadow Impact'],['Shadow Vengeance',"Night's Blessing",'Shadow Erosion','Linked Misfortune'],'Dominator gains no better T4 AoE package, so the Arcanist AoE core remains correct.','Effect Hit Rate remains essential for reliable Erosion.','Guide consensus'),
      role('Single Target DPS','T4 boss / direct-damage hybrid',['Dark Bullet','Dark Starburst','Chaos Rune','Shadow of Termination'],['Shadow Vengeance',"Night's Blessing",'Shadow Erosion','Linked Misfortune'],'High EHR: Chaos Rune → Mana Blast for the higher Erosion ceiling. Frenzy Totem + Soul Pact Resonance is another viable hybrid depending on ranks/stats.','The listed direct-damage hybrid is safer when Erosion landing is inconsistent.','Guide consensus'),
      role('Healing','Primary T4 healer/support',['Waterling Summon','Rejuvenating Rain','Radiant Restoration','Frenzy Totem'],['Phantom Light','Healing Mastery','Overhealing','Resurrection'],'Need more raw healing: Frenzy Totem → Healing Touch. If nobody needs Resurrection, use Mantra of Blessings; if you personally die early, use Shadow Vengeance.','Phantom Light is mandatory for the T4 healer identity.','Guide consensus')
    ]
  };'''

a = s.index('  const ROLE_PRESETS={')
b = s.index('\n\n  const FANTO={', a)
s = s[:a] + new_presets + s[b:]

# Map the real build names to the existing role-sensitive Main/Alt Fantomon research.
a = s.index('  function roleKey(title){')
b = s.index('\n  function buildCardHtml', a)
new_role_key = r'''  function roleKey(title){
    const t=(title||'').toLowerCase();
    if(t.startsWith('pvp')) return 'PvP';
    if(t.includes('dragon') || t.includes('single target') || t.includes('boss dps') || t.includes('support / boss')) return 'Boss';
    if(t.includes('dungeon tank') || t==='healing' || t.includes('fire aoe')) return 'Dungeon';
    return 'Solo';
  }'''
s = s[:a] + new_role_key + s[b:]

s = s.replace('/* BUILD_FANTOMON_PAIRS_V4_CLASS_ROLES_MAIN_ALT */','/* BUILD_FANTOMON_PAIRS_V5_GUIDE_LOADOUTS_MAIN_ALT */')
p.write_text(s)
