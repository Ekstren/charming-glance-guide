from pathlib import Path

FILES=[Path('index.html'),Path('.github/build-fantomons-inject.html')]
MARK='BUILD_GUIDE_CONSENSUS_PVP_V1'

ROLE_BLOCK=r'''  const ROLE_PRESETS={
    Berserker:[
      role('Generic PvE','Default S1 progression and general PvE',["Hunter's Judgment",'Sunset Sword','Eclipse Slash','Lion Combo'],['Insightful Eye','Blade of Judgment','Blade Siphon','Indomitable Will'],'If survival is already solved, Indomitable Will → Blazing Clash or another damage charm.','Low Crit: Blade Siphon → Blade of Lament.','Guide consensus'),
      role('Dragon','Long single-target / Dragon damage',['Flame Aura','Sunset Sword','Eclipse Slash','Lion Combo'],['Insightful Eye','Blade of Judgment','Blazing Clash','Crit Mastery'],'This is the dedicated damage setup for Dragon and similar long single-target fights.','If the boss can actually kill you, replace one greed charm with Indomitable Will.','Prydwen core'),
      role('PvP','Mobility, burst and cheat-death',['Darkness Descends','Lion Combo','Eclipse Slash','Sunset Sword'],['Insightful Eye','Blade of Judgment','Frame of Battles','Indomitable Will'],'For 2v2/4v4, Lion Combo → Hunter’s Judgment when grouping is more valuable.','Keep Indomitable Will for PvP.','Prydwen PvP')
    ],
    Paladin:[
      role('Dungeon Tank','Primary party-tank setup',['Valor Surge','Heart of Challenge','Luminous Shield','Desperate Protection'],['Iron Fortress','Block Mastery','Block Awareness','Stone Skin'],'If survival is comfortable, Luminous Shield → Lunarwater Threads for damage and pull utility.','This is the defense-first setup for difficult dungeons and maps well to team PvP.','Prydwen core'),
      role('Water Offensive','AoE-oriented Water / counter damage',['Guardian Ring','Lunarwater Threads','Frostbite Blossom','Heart of Challenge'],['Ripple Impact','Defensive Assault','Pursuit of Victory','Insightful Eye'],'Use when you need real damage instead of maximum party protection.','If you die too easily, move back toward the Dungeon Tank shell or add Potential Rebirth.','Multi-guide'),
      role('Boss DPS / Off-Tank','Damage-oriented boss setup',['Valor Surge','Leap Attack','Heavy Impact','Star Shattering Slash'],['Strength Rules','Insightful Eye','Pursuit of Victory',"Warrior's Essence"],'Use when another tank or your gear already handles survival and the group needs more damage.','If survival becomes the limiter, use Dungeon Tank instead.','Multi-guide'),
      role('PvP','Reflect / block pressure with team protection',['Luminous Shield','Leap Attack','Star Shattering Slash','Heart of Challenge'],['Iron Fortress','Rebound','Block Mastery','Block Awareness'],'Star Shattering Slash gives real kill pressure while Leap Attack/Heart of Challenge keep control and Rebound converts DEF into return damage.','For 4v4 or heavy enemy burst, Star Shattering Slash → Desperate Protection; Stone Skin is the first defensive charm flex.','Multi-guide PvP')
    ],
    Archmage:[
      role('AoE','Best general wave-clear and mixed-group setup',['Divine Wrath','Howling Hurricane','Meteoric Flames','Lightning Chain'],['Rapid Cast','Void Bubble','Mana Surge','Radiant Sear'],'Mana Surge can flex to Repelling Wind, Lightning Mystery, or Elemental Harmony if one tests better for your account.','Keep Void Bubble unless you completely outgear the content.','Prydwen core'),
      role('Single Target','Boss / concentrated damage',['Divine Wrath','Howling Hurricane','Meteoric Flames',"Wind's Delight"],['Rapid Cast','Void Bubble','Mana Surge','Radiant Sear'],'On smaller bosses, Divine Wrath → Tempest Sphere for more reliable Radiant Sear triggers.','Keep Void Bubble unless survival is irrelevant.','Prydwen core'),
      role('PvP','Fast elemental burst without Divine Wrath targeting RNG',['Tempest Sphere','Howling Hurricane','Meteoric Flames',"Wind's Delight"],['Rapid Cast','Void Bubble','Mana Surge','Radiant Sear'],'This is Prydwen’s single-target shell with Divine Wrath removed for PvP reliability.','Keep Void Bubble; Mana Surge → Repelling Wind if control/survival is more valuable than greed.','Prydwen PvP')
    ],
    Arcanist:[
      role('AoE DPS','Dark Erosion for groups and mixed waves',['Mana Blast','Dark Bullet','Abyssal Hand','Shadow Impact'],['Shadow Vengeance',"Night's Blessing",'Shadow Erosion','Linked Misfortune'],'This is the standard T3 AoE Erosion package.','Effect Hit Rate matters; fix EHR before breaking the Erosion core.','Guide consensus'),
      role('Single Target DPS','Boss-focused Dark Erosion',['Mana Blast','Dark Bullet','Abyssal Hand','Shadow of Termination'],['Shadow Vengeance',"Night's Blessing",'Shadow Erosion','Linked Misfortune'],'Use for bosses and other concentrated targets.','If Erosion is unreliable, the problem is usually insufficient Effect Hit Rate.','Guide consensus'),
      role('Healing','Dungeon / group healer',['Void Blessing','Waterling Summon','Radiant Restoration','Frenzy Totem'],['Resurrection','Healing Mastery','Overhealing','Gale Shield'],'Gale Shield is a practical flex; replace it with encounter-specific utility when needed.','This is the dedicated healer/support setup, not a DPS variation.','Guide consensus'),
      role('PvP','4v4 sustain / support shell',['Void Blessing','Waterling Summon','Radiant Restoration','Frenzy Totem'],['Resurrection','Healing Mastery','Overhealing','Shadow Vengeance'],'Use the healer shell when your team benefits more from sustain than another damage dealer; Shadow Vengeance keeps you relevant through focus fire.','Healing is less efficient in PvP, so if your Healing Boost/SPD are weak, switch to the Single Target DPS shell instead of forcing sustain.','Community PvP')
    ],
    Conqueror:[
      role('All-Content','Default S2 build for almost everything',['Flash Fire','Flame Aura','Flickering Blade','Blade Storm'],['Insightful Eye','Piercing Assault','Tactical Adaptation','Indomitable Will'],'High Crit: Insightful Eye → Soul Breaker. If you are safe in PvE, Indomitable Will → Soul Splash.','This is the published T4 generic core and the best default starting point.','Prydwen core'),
      role('Dragon','Dedicated sustained boss damage',['Flame Aura','Blade Storm','Flash Fire','Flickering Blade'],['Insightful Eye','Piercing Assault','Tactical Adaptation','Blazing Clash'],'Once Crit is high enough, Insightful Eye → Crit Mastery.','If surviving is the real damage loss, Blazing Clash → Indomitable Will.','Prydwen core'),
      role('PvP','Mobility, dispel and durable elemental pressure',['Flash Fire','Darkness Descends','Flickering Blade','Blade Storm'],['Insightful Eye','Piercing Assault','Tactical Adaptation','Indomitable Will'],'Darkness Descends replaces Flame Aura for mobility and Dispel. High Crit: Insightful Eye → Soul Breaker.','Always keep Indomitable Will in PvP; against high-block tanks, Accuracy becomes much more important than another small damage roll.','Prydwen PvP')
    ],
    Guardian:[
      role('Dungeon Tank','Primary S2 party tank',['Valor Surge','Heart of Challenge','Luminous Shield','Desperate Protection'],['Iron Will','Holy Aegis','Block Awareness','Soul Protection'],'Need more Taunt: Valor Surge → Hamper Strike. Need more damage: Desperate Protection → Swirling Blade or Star Shattering Slash.','If the team still dies, Iron Fortress is the first extra defensive flex.','Prydwen core'),
      role('Water Offensive','Cold-stacking offensive Guardian',['Swirling Blade','Lunarwater Threads','Seismic Tide','Raging Maelstrom'],['Frigid Aura','Defensive Assault','Frigid Glint','Potential Rebirth'],'Use for AoE and content where Guardian needs to contribute meaningful personal damage.','Potential Rebirth is the safety slot; other damage/sustain charms can replace it when appropriate.','Prydwen core'),
      role('Support / Boss','Boss, Chaos and group support',['Valor Surge','Leap Attack','Holy Purification','Lunarwater Threads'],['Frigid Aura','Frigid Glint','Iron Fortress','Oath of Vigil'],'If there is nothing worth dispelling, Holy Purification → damage. Lunarwater Threads → Seismic Tide for steadier Cold stacking.','This is the support setup Prydwen recommends for boss/group content.','Prydwen core'),
      role('PvP','Taunt, reflection and ally protection',['Hamper Strike','Heart of Challenge','Luminous Shield','Desperate Protection'],['Iron Will','Holy Aegis','Iron Fortress','Oath of Vigil'],'Hamper Strike gives reliable Taunt while Oath of Vigil protects the ally most likely to get bursted.','Iron Fortress and Oath of Vigil are explicitly PvP-oriented; keep the defense-first shell unless your team already has another Guardian.','Prydwen-derived PvP')
    ],
    Destroyer:[
      role('AoE','Default S2 mixed-wave damage',['Formation Breaker','Howling Hurricane','Meteoric Flames','Wind Blade Spiral'],['Rapid Cast','Void Bubble','Cyclone Lament','Radiant Sear'],'Best general setup for mixed packs and boss+mob encounters.','Strong accounts can replace Void Bubble with more offense.','Prydwen core'),
      role('Single Target','Boss-focused Destroyer',['Formation Breaker','Divine Wrath','Wind Blade Spiral','Thunder of Judgment'],['Rapid Cast','Void Bubble','Mana Surge','Radiant Sear'],'Wind Blade Spiral → Tempest Sphere if it tests better; on small bosses Divine Wrath → Meteoric Flames.','Mana Surge → Overload Protection when a little extra survival is enough to stabilize the fight.','Prydwen core'),
      role('Fire AoE','Dedicated horde-clear setup',['Formation Breaker','Fiery Star Trail','Fireball','Meteoric Flames'],['Rapid Cast','Void Bubble','Explosive Spirit','Fiery Burst'],'Use specifically for dense mob waves; Fiery Burst is the engine of the build.','Do not default to this against bosses or small packs just because it is a distinct element build.','Prydwen core'),
      role('PvP','Wind pressure / action-tempo burst',['Formation Breaker','Howling Hurricane','Meteoric Flames','Wind Blade Spiral'],['Rapid Cast','Void Bubble','Cyclone Lament','Radiant Sear'],'Community T4 testing consistently favors Wind in PvP; this uses the published Wind-heavy core rather than inventing a separate untested bar. Stack enough Effect Hit Rate for Laceration to matter.','Keep Void Bubble unless you are reliably deleting targets before they act; PvP Accuracy rolls are valuable into Block-heavy Guardians.','Community consensus')
    ],
    Dominator:[
      role('AoE DPS','Legacy T3 Erosion remains the T4 AoE build',['Mana Blast','Dark Bullet','Abyssal Hand','Shadow Impact'],['Shadow Vengeance',"Night's Blessing",'Shadow Erosion','Linked Misfortune'],'Dominator gains no better T4 AoE package, so the Arcanist AoE core remains correct.','Effect Hit Rate remains essential for reliable Erosion.','Prydwen core'),
      role('Single Target DPS','T4 boss / direct-damage hybrid',['Dark Bullet','Dark Starburst','Chaos Rune','Shadow of Termination'],['Shadow Vengeance',"Night's Blessing",'Shadow Erosion','Linked Misfortune'],'High EHR: Chaos Rune → Mana Blast for the higher Erosion ceiling. Frenzy Totem + Soul Pact Resonance is another viable hybrid depending on ranks/stats.','The listed direct-damage hybrid is safer when Erosion landing is inconsistent.','Guide consensus'),
      role('Healing','Primary T4 healer/support',['Waterling Summon','Rejuvenating Rain','Radiant Restoration','Frenzy Totem'],['Phantom Light','Healing Mastery','Overhealing','Resurrection'],'Need more raw healing: Frenzy Totem → Healing Touch. If nobody needs Resurrection, use Mantra of Blessings; if you personally die early, use Shadow Vengeance.','Phantom Light is mandatory for the T4 healer identity.','Guide consensus'),
      role('PvP','Solo Arena burst / utility',['Abyssal Hand','Dark Starburst','Dark Bullet','Shadow of Termination'],['Linked Misfortune','Shadow Erosion','Mantra of Blessings','Shadow Vengeance'],'This follows the published Loot & Waifus Solo PvP shell: reliable Dark pressure plus Mantra utility instead of forcing a full healer bar.','For coordinated 4v4, pivot toward Decoy Clone / Waterling / Mantra / Resurrection support if your team already has the damage carry.','Loot & Waifus PvP')
    ]
  };'''

for p in FILES:
    s=p.read_text(encoding='utf-8')
    if MARK in s:
        print(p, 'already patched')
        continue
    a=s.find('  const ROLE_PRESETS={')
    if a<0:
        raise SystemExit(f'ROLE_PRESETS start not found in {p}')
    b=s.find('\n\n  const FANTO={',a)
    if b<0:
        raise SystemExit(f'FANTO anchor not found in {p}')
    s=s[:a]+ROLE_BLOCK+s[b:]
    # Add a durable marker beside the injected build-library marker when available.
    if '/* BUILD_FANTOMON_PAIRS_V5_GUIDE_LOADOUTS_MAIN_ALT */' in s:
        s=s.replace('/* BUILD_FANTOMON_PAIRS_V5_GUIDE_LOADOUTS_MAIN_ALT */','/* BUILD_FANTOMON_PAIRS_V5_GUIDE_LOADOUTS_MAIN_ALT */\n/* '+MARK+' */',1)
    else:
        s=s[:a]+'  // '+MARK+'\n'+s[a:]
    p.write_text(s,encoding='utf-8')
    print('updated',p)
