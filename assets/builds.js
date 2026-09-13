(function(){
  const role=(name,subtitle,techniques,charms,offensive,defensive,confidence='Guide core')=>({name,subtitle,techniques,charms,offensive,defensive,confidence});
  const pick=(name,why)=>({name,why});

  const ROLE_PRESETS={
    Berserker:[
      role('Generic PvE','Default S1 progression and general PvE',["Hunter's Judgment",'Sunset Sword','Eclipse Slash','Lion Combo'],['Insightful Eye','Blade of Judgment','Blade Siphon','Indomitable Will'],'If survival is already solved, Indomitable Will → a damage charm.','Low Crit: Blade Siphon → Blade of Lament.','Guide consensus'),
      role('Dragon','Long single-target / Dragon damage',['Flame Aura','Sunset Sword','Eclipse Slash','Lion Combo'],['Insightful Eye','Blade of Judgment','Blazing Clash','Crit Mastery'],'This is the dedicated damage setup for Dragon and similar long single-target fights.','If the boss can actually kill you, replace one greed charm with Indomitable Will.','Guide consensus'),
      role('Arena','Solo PvP burst / mobility',['Darkness Descends','Lion Combo','Eclipse Slash','Sunset Sword'],['Insightful Eye','Blade of Judgment','Frame of Battles','Indomitable Will'],'Use mobility, multi-hit pressure and cheat-death to stay on the target through the opening exchange.','Keep Indomitable Will. Into reflect/block tanks, reduce multi-hit exposure with the Flash Dash / Heavy Impact / Doom Blade / Darkness Descends anti-tank setup.','Prydwen Arena'),
      role('Tournament','Team PvP grouping / area pressure',["Hunter's Judgment",'Flame Aura','Eclipse Slash','Sunset Sword'],['Insightful Eye','Blade of Judgment','Frame of Battles','Indomitable Will'],'Hunter’s Judgment groups targets for teammates while Flame Aura adds team-fight pressure; if your comp already controls targets, Hunter’s Judgment → Lion Combo.','Keep Indomitable Will; the team build should not greed away its survival layer.','Multi-guide team PvP')
    ],
    Paladin:[
      role('Dungeon Tank','Primary party-tank setup',['Valor Surge','Heart of Challenge','Luminous Shield','Desperate Protection'],['Iron Fortress','Block Mastery','Block Awareness','Stone Skin'],'If survival is comfortable, Luminous Shield → Lunarwater Threads for damage and pull utility.','This is the defense-first setup for difficult dungeons and also maps well to team PvP.','Guide consensus'),
      role('Water Offensive','AoE-oriented Water / counter damage',['Guardian Ring','Lunarwater Threads','Frostbite Blossom','Heart of Challenge'],['Ripple Impact','Defensive Assault','Pursuit of Victory','Insightful Eye'],'Use when you need real damage instead of maximum party protection.','If you die too easily, move back toward the Dungeon Tank setup or add Potential Rebirth.','Prydwen core'),
      role('Boss DPS / Off-Tank','Damage-oriented boss setup',['Valor Surge','Leap Attack','Heavy Impact','Star Shattering Slash'],['Strength Rules','Insightful Eye','Pursuit of Victory',"Warrior's Essence"],'Use when another tank or your gear already handles survival and the group needs more damage.','If survival becomes the limiter, use Dungeon Tank instead.','Multi-guide'),
      role('Arena','Solo reflect / block bruiser',['Luminous Shield','Leap Attack','Star Shattering Slash','Valor Surge'],['Rebound','Block Mastery','Block Awareness','Stone Skin'],'Arena is about surviving the burst window and letting Block/Rebound punish repeated hits before Star Shattering Slash comes online.','If the opponent cannot pressure you, Stone Skin can flex to a damage charm; do not sacrifice Block consistency just for sheet power.','Community Arena'),
      role('Tournament','Team protection / frontline',['Valor Surge','Heart of Challenge','Luminous Shield','Desperate Protection'],['Iron Fortress','Block Mastery','Block Awareness','Stone Skin'],'Use the full tank setup in team PvP: buff, hold aggro/control space and keep allies alive instead of chasing solo damage.','If the team is already safe, Luminous Shield can flex to Lunarwater Threads for pull pressure.','Guide-derived team PvP')
    ],
    Archmage:[
      role('AoE','Best general wave-clear and mixed-group setup',['Divine Wrath','Howling Hurricane','Meteoric Flames','Lightning Chain'],['Rapid Cast','Void Bubble','Mana Surge','Radiant Sear'],'Mana Surge can flex to Repelling Wind, Lightning Mystery, or Elemental Harmony if one tests better for your account.','Keep Void Bubble unless you completely outgear the content.','Guide consensus'),
      role('Single Target','Boss / concentrated damage',['Divine Wrath','Howling Hurricane','Meteoric Flames',"Wind's Delight"],['Rapid Cast','Void Bubble','Mana Surge','Radiant Sear'],'On smaller bosses, Divine Wrath → Tempest Sphere. The Tempest Sphere version is also the better PvP adaptation.','Keep Void Bubble unless survival is irrelevant.','Guide consensus'),
      role('Arena','Fast solo burst without Divine Wrath RNG',['Tempest Sphere','Howling Hurricane','Meteoric Flames',"Wind's Delight"],['Rapid Cast','Void Bubble','Mana Surge','Radiant Sear'],'The single-target setup without Divine Wrath is more reliable in PvP because Tempest Sphere hits player-sized targets more consistently.','Keep Void Bubble; Mana Surge → Repelling Wind when melee pressure is the matchup problem.','Prydwen Arena'),
      role('Tournament','Team AoE pressure',['Tempest Sphere','Howling Hurricane','Meteoric Flames','Lightning Chain'],['Rapid Cast','Void Bubble','Mana Surge','Radiant Sear'],'Tournament rewards wider coverage more than solo Arena, so keep the reliable PvP core but trade the single-target finisher for Lightning Chain.','Keep Void Bubble. Do not force Divine Wrath into small-player targeting just because it is strong on bosses.','Guide-derived team PvP')
    ],
    Arcanist:[
      role('AoE DPS','Dark Erosion for groups and mixed waves',['Mana Blast','Dark Bullet','Abyssal Hand','Shadow Impact'],['Shadow Vengeance',"Night's Blessing",'Shadow Erosion','Linked Misfortune'],'This is the standard T3 AoE Erosion package.','Effect Hit Rate matters; fix EHR before breaking the Erosion core.','Guide consensus'),
      role('Single Target DPS','Boss-focused Dark Erosion',['Mana Blast','Dark Bullet','Abyssal Hand','Shadow of Termination'],['Shadow Vengeance',"Night's Blessing",'Shadow Erosion','Linked Misfortune'],'Use for bosses and other concentrated targets.','If Erosion is unreliable, the problem is usually insufficient Effect Hit Rate.','Guide consensus'),
      role('Healing','Dungeon / group healer',['Void Blessing','Waterling Summon','Radiant Restoration','Frenzy Totem'],['Resurrection','Healing Mastery','Overhealing','Gale Shield'],'Gale Shield is the practical default flex from AllClash; replace it with encounter-specific utility when needed.','This is the dedicated healer/support setup, not a DPS variation.','Guide consensus'),
      role('Arena','Solo Dark burst / Erosion cash-out',['Mana Blast','Dark Bullet','Abyssal Hand','Shadow of Termination'],['Shadow Vengeance',"Night's Blessing",'Shadow Erosion','Linked Misfortune'],'Solo Arena favors actually killing the target: build Erosion, cash it out with Shadow of Termination and let Shadow Vengeance buy the finishing turn.','Do not default to the healer bar in solo PvP; PvP healing is reduced and needs real Healing Boost/SPD investment to justify it.','Guide-derived Arena'),
      role('Tournament','Hybrid team pressure / revive utility',['Mana Blast','Abyssal Hand','Radiant Restoration','Frenzy Totem'],['Resurrection','Shadow Vengeance','Shadow Erosion','Linked Misfortune'],'Tournament should not default to full healing: Mana Blast + Abyssal Hand provide Dark pressure, Erosion and Slow while Frenzy Totem buffs the team and Radiant Restoration gives one efficient group-heal slot.','PvP healing is heavily reduced. Only move toward the dedicated Healing setup when your Healing Boost/SPD are genuinely built for it; otherwise keep Resurrection + damage/debuff utility.','Community hybrid PvP')
    ],
    Conqueror:[
      role('Dungeon','Fast-clear S2 dungeon meta',['Flash Fire','Flame Aura','Flickering Blade','Blade Storm'],['Piercing Assault','Tactical Adaptation','Soul Splash','Insightful Eye'],'Flash Fire and Flame Aura provide fast area pressure while Flickering Blade and Blade Storm clean up survivors. High Crit: Insightful Eye → Soul Breaker.','Soul Splash is the default safety slot. Use Indomitable Will if deaths are costing clears, and Aegiswing when you need more survivability.','Current Global meta'),
      role('Crucible / Conquest','Single-target score / raid-boss meta',['Flame Aura','Blade Storm','Flash Fire','Flickering Blade'],['Piercing Assault','Tactical Adaptation','Blazing Clash','Insightful Eye'],'Flame Aura, Blade Storm, Flash Fire, and Flickering Blade maximize sustained single-target pressure. High Crit: Insightful Eye → Crit Mastery.','Prioritize rank and ascension on the four equipped Techniques. Indomitable Will is the safety flex when the boss can kill you.','Prydwen score core'),
      role('Arena','Solo PvP / anti-Guardian pressure',['Darkness Descends','Doom Blade','Flickering Blade','Blade Storm'],['Piercing Assault','Tactical Adaptation','Soul Breaker','Indomitable Will'],'Darkness Descends supplies mobility and Dispel, while Doom Blade, Flickering Blade, and Blade Storm keep pressure high. Low Crit: Soul Breaker → Insightful Eye.','Accuracy is especially valuable against high-Block Guardians. Indomitable Will protects against opening burst.','Current PvP'),
      role('Tournament · 2v2','Duo PvP: sustain + kill pressure',['Darkness Descends','Soul Piercer','Flickering Blade','Blade Storm'],['Piercing Assault','Tactical Adaptation','Soul Breaker','Indomitable Will'],'Soul Piercer adds sustain, Darkness Descends handles mobility and Dispel, and Flickering Blade + Blade Storm provide kill pressure. Low Crit: Soul Breaker → Insightful Eye.','Indomitable Will is core insurance in 2v2. Doom Blade is an offensive flex when your partner already provides enough control.','Current Global PvP'),
      role('Tournament · 4v4','Team PvP: reach, Dispel and coordinated tempo',['Flash Fire','Darkness Descends','Flickering Blade','Blade Storm'],['Insightful Eye','Piercing Assault','Tactical Adaptation','Indomitable Will'],'Flash Fire gives reach, Darkness Descends removes buffs, and Flickering Blade + Blade Storm provide coordinated pressure. If your team wants Gale Dance, swap Flash Fire → Gale Dance; normally only one Conqueror should carry it, preferably the higher-rank Gale Dance user.','Indomitable Will protects against focus fire. Insightful Eye → Soul Breaker at high Crit.','Current Global PvP'),
    ],
    Guardian:[
      role('Dungeon · Tank','Primary S2 party-tank meta',['Valor Surge','Heart of Challenge','Luminous Shield','Desperate Protection'],['Iron Will','Holy Aegis','Block Awareness','Soul Protection'],'Valor Surge buffs the party, Heart of Challenge controls aggro, and Luminous Shield + Desperate Protection stabilize heavy damage. Need more Taunt: Desperate Protection → Hamper Strike when survival is already stable.','Iron Will, Holy Aegis, Block Awareness, and Soul Protection form the default survival package. Iron Fortress is the first flex when the whole team needs more mitigation.','Prydwen dungeon core'),
      role('Crucible / Conquest · Tank','Carry-support / boss tank meta',['Valor Surge','Leap Attack','Holy Purification','Lunarwater Threads'],['Frigid Aura','Frigid Glint','Iron Fortress','Oath of Vigil'],'Valor Surge supports the carry, Holy Purification brings Dispel, Leap Attack contributes DEF Down, and Lunarwater Threads adds Water/Cold pressure.','Frigid Aura + Frigid Glint add boss damage while Iron Fortress + Oath of Vigil protect the party. If personal survival is a problem, Frigid Glint → Soul Protection; then Frigid Aura → Holy Aegis.','Guide-backed'),
      role('Arena · Tank','Solo block / reflect wall',['Valor Surge','Luminous Shield','Star Shattering Slash','Desperate Protection'],['Rebound','Holy Aegis','Block Mastery','Soul Protection'],'Valor Surge keeps the damage buff and cleanse online while Star Shattering Slash supplies kill pressure; Luminous Shield and Desperate Protection cover burst windows.','Rebound, Holy Aegis, Block Mastery, and Soul Protection reward high Block and punish repeated hits. Low Block: Soul Protection → Block Awareness.','Current PvP'),
      role('Tournament · 2v2 · Tank','Duo frontline: protect one carry and still threaten',['Valor Surge','Hamper Strike','Luminous Shield','Desperate Protection'],['Iron Will','Rebound','Iron Fortress','Oath of Vigil'],'Valor Surge buffs and cleanses the duo, Hamper Strike provides repeatable Taunt, and Luminous Shield + Desperate Protection absorb focus pressure.','Oath of Vigil protects your partner; Iron Fortress and Iron Will absorb team pressure. Rebound → Soul Protection if you are being focused too hard.','Current PvP'),
      role('Tournament · 4v4 · Tank','Full-team control tank: pull + Taunt + self-survival',['Valor Surge','Heart of Challenge','Lunarwater Threads','Luminous Shield'],['Iron Will','Soul Protection','Iron Fortress','Oath of Vigil'],'Valor Surge buffs and cleanses the team, Lunarwater Threads pulls enemies into your control zone, Heart of Challenge applies broad Taunt, and Luminous Shield helps the Guardian survive the resulting focus fire.','This is the default organized 4v4 control bar. Desperate Protection is an ally-protection fallback when Taunt/control is unreliable; when the control package is working, keeping the Guardian alive is the higher-value fourth-slot job.','Current Global PvP control tank'),
      role('Dungeon · DPS','Water AoE / fast-clear bruiser',['Valor Surge','Swirling Blade','Lunarwater Threads','Raging Maelstrom'],['Frigid Aura','Defensive Assault','Frigid Glint','Potential Rebirth'],'Valor Surge keeps the damage buff and cleanse online while Swirling Blade, Lunarwater Threads, and Raging Maelstrom handle Water/Cold AoE pressure.','Potential Rebirth covers risky clears. Pursuit of Victory is the damage flex once survivability is comfortable.','Prydwen Water core'),
      role('Crucible / Conquest · DPS','Single-target Guardian score build',['Valor Surge','Swirling Blade','Lunarwater Threads','Star Shattering Slash'],['Frigid Aura','Defensive Assault','Frigid Glint','Pursuit of Victory'],'Valor Surge keeps the damage buff active while Swirling Blade + Lunarwater Threads maintain Water/Cold pressure and Star Shattering Slash delivers the heavy single-target hit.','Frigid Aura, Defensive Assault, Frigid Glint, and Pursuit of Victory maximize the Water/Cold damage package. If Star Shattering Slash is badly under-ranked, compare it with Raging Maelstrom on your account.','Prydwen ST hybrid + Global testing'),
      role('Arena · DPS','Offensive block / counter bruiser',['Valor Surge','Swirling Blade','Luminous Shield','Star Shattering Slash'],['Rebound','Holy Aegis','Block Mastery','Eye for an Eye'],'Valor Surge keeps its buff and cleanse active while Swirling Blade + Star Shattering Slash supply kill pressure and Luminous Shield preserves bruiser durability.','Rebound, Holy Aegis, Block Mastery, and Eye for an Eye turn Block into counter pressure. Eye for an Eye → Soul Protection or Potential Rebirth if burst is too high.','Prydwen + PvP'),
      role('Tournament · 2v2 · DPS','Duo bruiser: survive focus while threatening kills',['Valor Surge','Swirling Blade','Luminous Shield','Star Shattering Slash'],['Rebound','Holy Aegis','Block Mastery','Eye for an Eye'],'Valor Surge buffs and cleanses the duo while Swirling Blade + Star Shattering Slash create kill pressure and Luminous Shield helps survive focus.','Rebound, Holy Aegis, and Block Mastery support the bruiser core. Eye for an Eye → Soul Protection when you are the primary focus target.','Current PvP'),
      role('Tournament · 4v4 · DPS','Water AoE team-pressure build',['Valor Surge','Swirling Blade','Lunarwater Threads','Raging Maelstrom'],['Frigid Aura','Defensive Assault','Frigid Glint','Potential Rebirth'],'Valor Surge buffs and cleanses the team while Swirling Blade, Lunarwater Threads, and Raging Maelstrom spread Water/Cold pressure across the enemy team.','Potential Rebirth is the safety slot. Pursuit of Victory is the damage flex when another frontline is reliably absorbing focus.','Prydwen Water + PvP'),
    ],
    Destroyer:[
      role('Dungeon','Fire AoE horde-clear meta',['Formation Breaker','Fiery Star Trail','Fireball','Meteoric Flames'],['Rapid Cast','Void Bubble','Explosive Spirit','Fiery Burst'],'Fiery Star Trail, Fireball, and Meteoric Flames repeatedly trigger Fiery Burst across dense packs, with Formation Breaker improving tempo.','Void Bubble is the default safety slot; an offensive Charm can take its place when survivability is comfortable.','Prydwen + Global testing'),
      role('Crucible / Conquest','Single-target score meta',['Formation Breaker','Divine Wrath','Wind Blade Spiral','Thunder of Judgment'],['Rapid Cast','Mana Surge','Radiant Sear','Incarnation of Light'],'Formation Breaker accelerates the team while Divine Wrath, Wind Blade Spiral, and Thunder of Judgment concentrate boss damage. Wind\'s Delight or Tempest Sphere are rank-dependent flexes for Wind Blade Spiral.','Incarnation of Light favors score; Void Bubble adds safety. Meteoric Flames can outperform Divine Wrath on smaller bosses, so test both if needed.','Guide + score testing'),
      role('Arena','Wind control / solo tempo',['Formation Breaker','Tempest Sphere','Wind Blade Spiral',"Wind's Delight"],['Cyclone Lament','Repelling Wind',"Wind's Shadow",'Void Bubble'],'Formation Breaker accelerates actions while Tempest Sphere, Wind Blade Spiral, and Wind\'s Delight concentrate Wind pressure on a single target.','Void Bubble provides the safety layer; Repelling Wind helps keep melee opponents off you.','Prydwen + Global PvP'),
      role('Tournament · 2v2','Duo control + Formation Breaker tempo',['Formation Breaker','Tempest Sphere','Wind Blade Spiral',"Wind's Delight"],['Rapid Cast','Void Bubble','Repelling Wind','Cyclone Lament'],'Formation Breaker improves duo tempo while Tempest Sphere, Wind Blade Spiral, and Wind\'s Delight apply focused Wind pressure.','Void Bubble provides safety, Repelling Wind controls melee pressure, and Cyclone Lament rewards repeated Wind attacks. Radiant Sear is the damage flex when your teammate already supplies control.','Current PvP'),
      role('Tournament · 4v4','Team AoE + Formation Breaker acceleration',['Formation Breaker','Howling Hurricane','Meteoric Flames','Wind Blade Spiral'],['Rapid Cast','Void Bubble','Cyclone Lament','Radiant Sear'],'Formation Breaker accelerates the team while Howling Hurricane, Meteoric Flames, and Wind Blade Spiral spread AoE and Laceration pressure.','Void Bubble protects against coordinated focus; Cyclone Lament and Radiant Sear turn repeated hits into additional pressure.','Prydwen team core'),
    ],
    Dominator:[
      role('Dungeon · DPS','AoE Dark / Erosion clear',['Mana Blast','Dark Bullet','Abyssal Hand','Shadow Impact'],['Shadow Vengeance',"Night's Blessing",'Shadow Erosion','Linked Misfortune'],'Mana Blast, Dark Bullet, Abyssal Hand, and Shadow Impact spread Erosion and direct damage across dungeon packs.','Effect Hit Rate is the key consistency stat for Erosion. Nyxarchon is the default damage Fantomon.','Prydwen AoE core'),
      role('Crucible / Conquest · DPS','Single-target direct / Erosion hybrid',['Dark Bullet','Dark Starburst','Chaos Rune','Shadow of Termination'],['Shadow Vengeance',"Night's Blessing",'Shadow Erosion','Linked Misfortune'],'Dark Starburst + Chaos Rune provide reliable direct damage while Dark Bullet + Shadow of Termination maintain and cash out Erosion. High EHR: Chaos Rune → Mana Blast.','Shadow Vengeance, Night\'s Blessing, Shadow Erosion, and Linked Misfortune maximize personal boss damage. For carry-support teams, Decoy + Frenzy + Mantra is the team-amplification option.','Prydwen ST core'),
      role('Arena · DPS','Single-target Dark pressure',['Dark Bullet','Dark Starburst','Chaos Rune','Shadow of Termination'],['Shadow Vengeance',"Night's Blessing",'Shadow Erosion','Linked Misfortune'],'Dark Bullet, Dark Starburst, Chaos Rune, and Shadow of Termination focus Dark pressure and Erosion on one opponent. High EHR: Chaos Rune → Mana Blast.','Shadow Vengeance provides a survival window while Night\'s Blessing, Shadow Erosion, and Linked Misfortune scale the damage cycle. Use a direct-damage flex if Chaos Rune is badly under-ranked.','Prydwen ST + PvP'),
      role('Tournament · 2v2 · DPS','Duo kill pressure + revive',['Dark Bullet','Dark Starburst','Chaos Rune','Shadow of Termination'],['Shadow Vengeance','Shadow Erosion','Linked Misfortune','Resurrection'],'Dark Bullet, Dark Starburst, Chaos Rune, and Shadow of Termination provide focused kill pressure.','Resurrection can swing the round after a teammate falls, while Shadow Vengeance, Shadow Erosion, and Linked Misfortune preserve damage and survivability.','Prydwen + PvP'),
      role('Tournament · 4v4 · DPS','AoE Dark pressure + revive',['Mana Blast','Dark Bullet','Abyssal Hand','Shadow Impact'],['Shadow Vengeance','Shadow Erosion','Linked Misfortune','Resurrection'],'Mana Blast, Dark Bullet, Abyssal Hand, and Shadow Impact spread Dark/Erosion pressure across multiple targets.','Resurrection adds high-impact team utility while Shadow Vengeance, Shadow Erosion, and Linked Misfortune keep the AoE damage engine active.','Prydwen + PvP'),
      role('Dungeon · Heals','Hard-dungeon healer',['Waterling Summon','Rejuvenating Rain','Radiant Restoration','Frenzy Totem'],['Phantom Light','Healing Mastery','Overhealing','Resurrection'],'Waterling Summon, Rejuvenating Rain, Radiant Restoration, and Frenzy Totem provide steady healing plus team offense. Need more raw healing: Frenzy Totem → Healing Touch.','Phantom Light, Healing Mastery, Overhealing, and Resurrection form the main sustain package. If nobody is dying, Resurrection → Mantra of Blessings.','Prydwen healer core'),
      role('Crucible / Conquest · Heals','Hypercarry support / boss score',['Radiant Restoration','Decoy Clone','Frenzy Totem','Dark Bullet'],['Phantom Light','Healing Mastery','Overhealing','Mantra of Blessings'],'Radiant Restoration covers efficient healing while Decoy Clone, Frenzy Totem, and Dark Bullet support the strongest carry and maintain debuff pressure.','Phantom Light, Healing Mastery, Overhealing, and Mantra of Blessings prioritize support throughput. Decoy positioning matters because only one effective link can attach.','Prydwen + Global support testing'),
      role('Arena · Heals','Specialist sustain hybrid',['Rejuvenating Rain','Radiant Restoration','Dark Bullet','Shadow of Termination'],['Phantom Light','Healing Mastery','Shadow Vengeance','Mantra of Blessings'],'Rejuvenating Rain and Radiant Restoration provide sustain while Dark Bullet and Shadow of Termination keep kill pressure.','Phantom Light and Healing Mastery scale sustain; Shadow Vengeance and Mantra of Blessings preserve tempo and damage. This role works best with strong Healing Boost/SPD gear.','PvP specialist'),
      role('Tournament · 2v2 · Heals','Duo sustain / carry support',['Rejuvenating Rain','Radiant Restoration','Frenzy Totem','Dark Bullet'],['Phantom Light','Healing Mastery','Resurrection','Shadow Vengeance'],'Rejuvenating Rain and Radiant Restoration keep your partner stable while Frenzy Totem boosts output and Dark Bullet maintains pressure.','Resurrection is the key swing utility; Phantom Light and Healing Mastery raise sustain while Shadow Vengeance protects your own damage window.','PvP support'),
      role('Tournament · 4v4 · Heals','Hybrid team support',['Radiant Restoration','Decoy Clone','Frenzy Totem','Dark Bullet'],['Phantom Light','Healing Mastery','Resurrection','Mantra of Blessings'],'Radiant Restoration, Decoy Clone, and Frenzy Totem support the team while Dark Bullet maintains debuff pressure.','Phantom Light, Healing Mastery, Resurrection, and Mantra of Blessings balance healing, revive utility, and team damage.','Team PvP'),
    ]
  };

  const TECHNIQUE_SWAP_SCENARIOS={
    'Dungeon|Flash Fire|Flame Aura|Flickering Blade|Blade Storm':[
      ['Need Dispel','Flame Aura','Darkness Descends']
    ],
    'Tournament · 4v4|Flash Fire|Darkness Descends|Flickering Blade|Blade Storm':[
      ['Team SPD / Gale Dance','Flash Fire','Gale Dance']
    ],
    'Arena|Darkness Descends|Doom Blade|Flickering Blade|Blade Storm':[
      ['Need sustain','Doom Blade','Soul Piercer']
    ],
    'Tournament · 2v2|Darkness Descends|Soul Piercer|Flickering Blade|Blade Storm':[
      ['Need more burst','Soul Piercer','Doom Blade']
    ],
    'Dungeon · Tank|Valor Surge|Heart of Challenge|Luminous Shield|Desperate Protection':[
      ['Need more Taunt','Desperate Protection','Hamper Strike']
    ],
    'Arena · Tank|Valor Surge|Luminous Shield|Star Shattering Slash|Desperate Protection':[
      ['Need more mobility','Star Shattering Slash','Forceful Charge']
    ],
    'Tournament · 2v2 · Tank|Valor Surge|Hamper Strike|Luminous Shield|Desperate Protection':[
      ['Need opening AoE Taunt','Hamper Strike','Heart of Challenge']
    ],
    'Tournament · 4v4 · Tank|Valor Surge|Heart of Challenge|Lunarwater Threads|Luminous Shield':[
      ['Taunt/control is unreliable','Lunarwater Threads','Desperate Protection'],
      ['Need repeatable Taunt','Heart of Challenge','Hamper Strike']
    ],
    'Dungeon · DPS|Valor Surge|Swirling Blade|Lunarwater Threads|Raging Maelstrom':[
      ['Boss / elite focus','Raging Maelstrom','Star Shattering Slash']
    ],
    'Crucible / Conquest · DPS|Valor Surge|Swirling Blade|Lunarwater Threads|Star Shattering Slash':[
      ['Star Shattering is under-ranked','Star Shattering Slash','Raging Maelstrom']
    ],
    'Arena · DPS|Valor Surge|Swirling Blade|Luminous Shield|Star Shattering Slash':[
      ['Need more mobility','Star Shattering Slash','Forceful Charge']
    ],
    'Tournament · 2v2 · DPS|Valor Surge|Swirling Blade|Luminous Shield|Star Shattering Slash':[
      ['Need more mobility','Star Shattering Slash','Forceful Charge']
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
    ],
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
      ['Nobody is dying','Resurrection','Mantra of Blessings'],
    ],
  };

  const FANTO={
    Berserker:{
      Solo:[pick('Nyxarchon','Main damage choice: extra damage plus DEF shred works in every S1 fight.'),pick('Aegiswing','S1 Assist survival/recovery is excellent for pushing stages above your power.'),pick('Sylvaerie','Permanent ATK + SPD improves both damage and turn tempo.'),pick('Zeioletus','Straightforward recurring burst when you want more damage instead of safety.')],
      Dungeon:[pick('Nyxarchon','Best overall clear lead: damage plus DEF shred benefits every target you focus.'),pick('Sylvaerie','ATK + SPD is consistent across every dungeon room.'),pick('Zeioletus','Extra AoE burst helps clean packs quickly.'),pick('Terragon','Physical-friendly damage with a chance to cut enemy ATK; useful when rooms hit hard.')],
      Boss:[pick('Nyxarchon','Best long-fight damage lead thanks to repeated damage and DEF shred.'),pick('Sylvaerie','Permanent ATK + SPD scales your whole boss rotation.'),pick('Terragon','Physical-friendly extra damage plus an ATK-down chance on the boss.'),pick('Zeioletus','Reliable extra burst if it outperforms Sylvaerie on your stats.')],
      PvP:[pick('Aegiswing','Main PvP pick: its S1 Assist survival/recovery buys another life without relying on Materialization.'),pick('Nyxarchon','Greedy option when you can trade safety for damage and DEF shred.'),pick('Sylvaerie','Speed can help you win action tempo while still adding ATK.'),pick('Terragon','ATK reduction can blunt enemy burst while still adding damage.')]
    },
    Paladin:{
      Solo:[pick('Aegiswing','Main S1 tank pick: survival/recovery adds a strong durability layer.'),pick('Armopi','Its S1 Assist already cycles DEF into a personal shield; good for DEF-heavy counter builds.'),pick('Boaro','Budget shield option that repeatedly triggers as you lose HP.'),pick('Kels','Useful when solo enemies have buffs worth dispelling.')],
      Dungeon:[pick('Aegiswing','Best general tank lead for surviving repeated party-dungeon pressure.'),pick('Armopi','DEF stacking and its personal shield work in S1 without Materialization.'),pick('Kels','Bring it when dungeon enemies use important buffs you want to dispel.'),pick('Boaro','Cheap repeated shielding when you need raw durability.')],
      Boss:[pick('Aegiswing','Safest default boss lead and Prydwen’s primary Paladin tank recommendation.'),pick('Kels','Excellent situational boss pick when dispel matters; its S1 value does not require Materialization.'),pick('Armopi','DEF + personal shield is strong when the boss repeatedly tests your tankiness.'),pick('Boaro','Budget defensive alternative with repeated shields.')],
      PvP:[pick('Aegiswing','Main PvP tank pick: S1 survival/recovery is immediately useful.'),pick('Armopi','DEF stacking plus personal shield helps into sustained focus fire.'),pick('Boaro','Repeated shields can be annoying to chew through in longer fights.'),pick('Kels','Use when stripping enemy buffs matters more than maximum personal durability.')]
    },
    Archmage:{
      Solo:[pick('Nyxarchon','Main damage lead: DEF shred and strong pet damage fit glass-cannon progression.'),pick('Armopi','Its pre-Materialization DEF-to-shield Assist can buy the one extra turn Archmage often needs.'),pick('Sylvaerie','Permanent ATK + SPD improves burst and action order.'),pick('Zeioletus','Extra recurring damage is strong when survival is already solved.')],
      Dungeon:[pick('Nyxarchon','Best premium damage lead for deleting rooms quickly.'),pick('Sylvaerie','ATK + SPD is ideal for fast dungeon clears.'),pick('Zeioletus','Additional AoE burst helps finish packs.'),pick('Armopi','Take the personal DEF/shield cycle if you are dying before the room is cleared.')],
      Boss:[pick('Nyxarchon','Best premium boss damage option with DEF shred.'),pick('Sylvaerie','Permanent ATK + SPD scales every cast.'),pick('Zeioletus','Good recurring damage when it tests better on your account.'),pick('Armopi','Safety option if the boss survives long enough to threaten you.')],
      PvP:[pick('Aegiswing','Main survival-first PvP pick; its base Assist buys extra life before Materialization exists.'),pick('Nyxarchon','Greedy damage/DEF-shred alternative.'),pick('Armopi','Pre-Materialization DEF + personal shield can buy a critical extra turn.'),pick('Sylvaerie','SPD helps contest turn order while adding ATK.')]
    },
    Arcanist:{
      Tournament:[pick('Nyxarchon','Main hybrid Tournament pick: damage plus DEF shred contributes even while you spend slots on team utility.'),pick('Sylvaerie','Alt for ATK + SPD; speed is especially valuable for getting support/debuff actions out early.')],
      Solo:[pick('Nyxarchon','Main DPS lead: Dark damage and the debuff line up naturally with Arcanist.'),pick('Zeioletus','Best simple F2P damage stopgap before Nyx.'),pick('Sylvaerie','Permanent SPD + ATK can beat Zei depending on your stats.'),pick('Aegiswing','Use its S1 survival/recovery when staying alive is more important than max DPS.')],
      Dungeon:[pick('Mandragora','Main healer pick: every ally-targeted Technique can trigger extra healing, with no Materialization needed.'),pick('Sylvaerie','SPD means more turns to heal and support.'),pick('Aegiswing','Keeps the healer alive through dangerous rooms using only its S1 Assist effect.'),pick('Herbote','Fallback self-heal/cleanse option, but unevolved S1 Herbote is weaker for pure healing than Mandragora.')],
      Boss:[pick('Nyxarchon','Main boss DPS choice: Dark damage plus a useful debuff.'),pick('Zeioletus','Straightforward damage alternative before Nyx.'),pick('Sylvaerie','SPD + ATK scales the whole DoT rotation.'),pick('Terragon','Can reduce boss ATK while still contributing damage.')],
      PvP:[pick('Aegiswing','Main support PvP choice: base survival/recovery helps you keep healing through burst.'),pick('Mandragora','More raw healing whenever you target allies.'),pick('Nyxarchon','Offensive option when you can afford to pressure instead of purely sustain.'),pick('Sylvaerie','Extra SPD improves support tempo.')]
    },
    Conqueror:{
      Solo:[pick('Nyxarchon','Main current S2 pick: Prydwen still rates its damage + DEF shred as BIS for generic content.'),pick('Aegiswing','Excellent high-push alternative when survival is the limiter.'),pick('Sylvaerie','Permanent ATK + SPD is the best currently available general damage alternative.'),pick('Zeioletus','Extra recurring burst if your stats make it outperform Sylvaerie.')],
      Dungeon:[pick('Nyxarchon','Best default damage lead for fast clears and DEF-shred stacking.'),pick('Aegiswing','Use when a high dungeon is killing you before your damage comes online.'),pick('Sylvaerie','ATK + SPD improves room-clearing speed.'),pick('Zeioletus','Adds direct burst to help finish packs.')],
      Boss:[pick('Nyxarchon','Main long-fight choice: DEF shred remains extremely valuable on hard bosses.'),pick('Sylvaerie','Permanent ATK + SPD scales the full boss rotation.'),pick('Zeioletus','Reliable extra damage if it tests better on your account.'),pick('Aegiswing','Defensive fallback for bosses where dying is the actual DPS loss.')],
      PvP:[pick('Aegiswing','Main PvP choice: extra survival plus its S2 Materialization utility is more valuable here than pure damage.'),pick('Nyxarchon','Greedy damage/DEF-shred alternative.'),pick('Sylvaerie','SPD can help win action tempo while still boosting ATK.'),pick('Zeioletus','Pure damage alternative when survivability is already covered.')]
    },
    Guardian:{
      Solo:[pick('Aegiswing','Main Guardian investment: Prydwen calls it the priority Mythic for the class, with survival and Taunt synergy.'),pick('Nyxarchon','Best offensive support alternative when you need more damage and debuffs.'),pick('Kels','Useful dispel/DEF-down utility when the stage benefits from it.'),pick('Boaro','Budget defensive option with shielding and S2 knockback utility.')],
      Dungeon:[pick('Aegiswing','Main tank lead: survival, extra Taunt and reduced damage from taunted enemies fit the dungeon job perfectly.'),pick('Kels','Strong party utility through dispel and Materialized DEF Down.'),pick('Nyxarchon','Offensive support option when your team wants faster kills.'),pick('Terragon','ATK/DMG reduction utility when enemy damage is the bigger problem.')],
      Boss:[pick('Kels','Main boss-support pick: Prydwen specifically highlights its dispel + Materialized DEF Down for team support.'),pick('Nyxarchon','Amplifies team damage with reliable debuffs and its own damage.'),pick('Terragon','Great when the raid needs enemy ATK/DMG reduction more than another damage debuff.'),pick('Aegiswing','Use when your personal survival or Taunt uptime is the limiting factor.')],
      PvP:[pick('Aegiswing','Main PvP Guardian pet: extra Taunt, survival and anti-Taunt damage reduction match the class role.'),pick('Kels','Utility alternative for dispelling buffs and adding DEF Down.'),pick('Nyxarchon','Greedy pressure option when your team already has enough protection.'),pick('Boaro','Budget control/survival alternative with shielding and knockback utility.')]
    },
    Destroyer:{
      Solo:[pick('Nyxarchon','Main premium choice: DEF shred plus strong damage suits a glass-cannon Destroyer.'),pick('Armopi','Prydwen’s survival alternative; its DEF/shield cycle can buy one extra turn.'),pick('Sylvaerie','Permanent ATK + SPD improves damage and action order.'),pick('Zeioletus','Simple recurring burst when you do not need extra safety.')],
      Dungeon:[pick('Nyxarchon','Main damage lead for clearing difficult rooms quickly.'),pick('Sylvaerie','ATK + SPD is excellent for speed-clearing dungeons.'),pick('Zeioletus','Extra AoE burst complements the Fire/AoE setup.'),pick('Armopi','Take the shield/DEF option if you are dying before your turn.')],
      Boss:[pick('Nyxarchon','Main premium boss option with damage and DEF shred.'),pick('Sylvaerie','Permanent ATK + SPD scales every cast.'),pick('Zeioletus','Additional recurring damage when it tests better on your stats.'),pick('Armopi','Safety fallback when the boss survives long enough to threaten you.')],
      PvP:[pick('Aegiswing','Main PvP survival pick: cheat-death style utility is more valuable than another pure damage pet here.'),pick('Nyxarchon','Greedy damage/DEF-shred option.'),pick('Armopi','DEF + shield gives a fragile caster another way to survive focus.'),pick('Sylvaerie','SPD helps contest turn order and still adds ATK.')]
    },
    Dominator:{
      Tournament:[pick('Nyxarchon','Main hybrid Tournament pick: adds real damage and DEF shred while the Dominator handles buffs and utility.'),pick('Terragon','Alt team-utility pick when reducing enemy ATK/pressure matters more than personal damage.'),pick('Sylvaerie','No-shop alternative: ATK + SPD improves both pressure and support tempo.')],
      Solo:[pick('Nyxarchon','Main DPS choice: Prydwen calls Nyx Dominator’s BIS thanks to Dark AoE damage and its supportive effect.'),pick('Zeioletus','Best straightforward F2P damage stopgap.'),pick('Sylvaerie','ATK + SPD can outperform Zei on some accounts.'),pick('Aegiswing','Use when surviving solo progression is more important than max damage.')],
      Dungeon:[pick('Mandragora','Main pure-healing pick: directly adds healing whenever you use ally-targeted Techniques.'),pick('Herbote','Strong S2 healing alternative once Materialized because it can extend its healing to allies.'),pick('Sylvaerie','SPD gives you more actions to heal/support.'),pick('Terragon','Support alternative when reducing enemy ATK/DMG helps the whole party more than extra healing.')],
      Boss:[pick('Nyxarchon','Main DPS lead for single-target Dark builds and team damage support.'),pick('Zeioletus','Direct damage alternative before or instead of Nyx.'),pick('Sylvaerie','Permanent SPD + ATK scales the whole boss rotation.'),pick('Terragon','Useful support option when lowering the boss’s ATK matters.')],
      PvP:[pick('Mandragora','Main support/healing pick when your job is keeping teammates alive.'),pick('Aegiswing','Survival-first alternative when you are being focused.'),pick('Terragon','Debuffing option that can reduce enemy pressure while you support.'),pick('Sylvaerie','SPD improves support tempo when raw healing is already sufficient.')]
    }
  };


  const META_CLASSES=new Set(['Conqueror','Guardian','Destroyer','Dominator']);
  const META_MODES=['Dungeon','Crucible / Conquest','Arena','Tournament'];
  const metaRead=(key,fallback)=>{try{return localStorage.getItem(key)||fallback}catch(_){return fallback}};
  const metaWrite=(key,val)=>{try{localStorage.setItem(key,val)}catch(_){}};
  const metaMode=()=>META_MODES.includes(metaRead('sxs-build-meta-mode','Dungeon'))?metaRead('sxs-build-meta-mode','Dungeon'):'Dungeon';
  const metaTournamentSize=()=>metaRead('sxs-build-tournament-size','4v4')==='2v2'?'2v2':'4v4';
  const guardianBuildMode=()=>metaRead('sxs-build-guardian-mode','tank')==='dps'?'dps':'tank';
  const dominatorBuildMode=()=>metaRead('sxs-build-dominator-mode','dps')==='heals'?'heals':'dps';
  function ensureGuardianRoleControl(cls){
    if(cls!=='Guardian') return;
    const guide=document.querySelector('.builds .guideSummary');
    const strong=guide?.querySelector(':scope > div > strong');
    if(!guide||!strong) return;
    let row=guide.querySelector('.guardianHeadingRow');
    if(!row){
      row=document.createElement('div');
      row.className='guardianHeadingRow';
      strong.before(row);
      row.append(strong);
      const tabs=document.createElement('div');
      tabs.className='guardianModeTabs';
      tabs.setAttribute('role','group');
      tabs.setAttribute('aria-label','Guardian build role');
      tabs.innerHTML='<button type="button" data-guardian-mode="tank">Tank</button><button type="button" data-guardian-mode="dps">DPS</button>';
      row.append(tabs);
    }
    const active=guardianBuildMode();
    row.querySelectorAll('[data-guardian-mode]').forEach(btn=>{
      const on=btn.dataset.guardianMode===active;
      btn.classList.toggle('active',on);
      btn.setAttribute('aria-pressed',String(on));
    });
  }
  function ensureMetaControls(cls){
    const grid=document.querySelector('.builds .buildGrid');
    if(!grid) return;
    ensureGuardianRoleControl(cls);
    let box=document.querySelector('.builds .metaBuildControls');
    if(!META_CLASSES.has(cls)){
      box?.remove();
      grid.classList.remove('metaModeGrid');
      grid.querySelectorAll('.buildCard[hidden]').forEach(c=>c.hidden=false);
      return;
    }
    if(!box){
      box=document.createElement('div');
      box.className='metaBuildControls';
      box.innerHTML='<div class="metaBuildTabs">'+META_MODES.map(m=>m==='Tournament'?'<div class="metaTournamentScenario"><button type="button" class="metaTournamentMain" data-meta-mode="Tournament">Tournament</button><div class="metaTournamentTabs"><button type="button" data-tournament-size="2v2">2v2</button><button type="button" data-tournament-size="4v4">4v4</button></div></div>':'<button type="button" data-meta-mode="'+esc(m)+'">'+esc(m)+'</button>').join('')+'</div>';
    }
    // Keep the scenario selector immediately above the activity build card. Rich
    // role-specific investment panels (Guardian/Dominator) may be inserted later,
    // so re-anchor the selector after those panels instead of leaving it above them.
    if(box.nextElementSibling!==grid) grid.before(box);
    grid.classList.add('metaModeGrid');
  }
  function applyMetaVisibility(cls){
    const grid=document.querySelector('.builds .buildGrid');
    if(!grid||!META_CLASSES.has(cls)) return;
    ensureMetaControls(cls);
    const mode=metaMode(), size=metaTournamentSize(), guardianMode=guardianBuildMode(), dominatorMode=dominatorBuildMode();
    document.querySelectorAll('.builds .guardianModeTabs [data-guardian-mode]').forEach(b=>{const on=b.dataset.guardianMode===guardianMode;b.classList.toggle('active',on);b.setAttribute('aria-pressed',String(on));});
    document.querySelectorAll('.builds .dominatorModeTabs [data-dominator-mode]').forEach(b=>{const on=b.dataset.dominatorMode===dominatorMode;b.classList.toggle('active',on);b.setAttribute('aria-pressed',String(on));});
    const wanted=mode==='Tournament'?'Tournament · '+size:mode;
    document.querySelectorAll('.builds .metaBuildTabs [data-meta-mode]').forEach(b=>b.classList.toggle('active',b.dataset.metaMode===mode));
    document.querySelectorAll('.builds .metaTournamentScenario').forEach(x=>x.classList.toggle('active',mode==='Tournament'));
    document.querySelectorAll('.builds .metaTournamentTabs [data-tournament-size]').forEach(b=>b.classList.toggle('active',b.dataset.tournamentSize===size));
    grid.querySelectorAll(':scope > .buildCard').forEach(card=>{
      const wrongActivity=card.dataset.role!==wanted;
      const selectedRole=cls==='Guardian'?guardianMode:(cls==='Dominator'?dominatorMode:'');
      const wrongRole=(cls==='Guardian'||cls==='Dominator')&&card.dataset.buildRole!==selectedRole;
      card.hidden=wrongActivity||wrongRole;
    });
  }

  function activeClass(){
    const b=document.querySelector('.builds .classTabs button.active');
    return b ? b.textContent.trim() : '';
  }
  function esc(s){
    return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  }
  function roleKey(title){
    const t=(title||'').toLowerCase();
    if(t==='dungeon') return 'Dungeon';
    if(t==='crucible / conquest') return 'Boss';
    if(t==='fantasia ascent') return 'Solo';
    if(t.startsWith('arena')) return 'Arena';
    if(t.startsWith('tournament')) return 'Tournament';
    if(t.startsWith('pvp')) return 'PvP';
    if(t.includes('dragon') || t.includes('single target') || t.includes('boss dps') || t.includes('support / boss')) return 'Boss';
    if(t.includes('dungeon tank') || t==='healing' || t.includes('fire aoe')) return 'Dungeon';
    return 'Solo';
  }
  function buildCardHtml(r){
    const rm=String(r.name||'').match(/^(.*?) · (Tank|DPS|Heals)$/);
    const displayName=rm?rm[1]:r.name;
    const roleAttr=rm?' data-build-role="'+rm[2].toLowerCase()+'"':'';
    const techniqueSwaps=TECHNIQUE_SWAP_SCENARIOS[r.name+'|'+r.techniques.join('|')]||[];
    const charmSwaps=CHARM_SWAP_SCENARIOS[r.name+'|'+r.charms.join('|')]||[];
    return '<article class="buildCard" data-role="'+esc(displayName)+'"'+roleAttr+'>'
      +'<header><div><h3>'+esc(displayName)+'<span class="roleBadge">'+esc(r.confidence)+'</span></h3><p>'+esc(r.subtitle)+'</p></div></header>'
      +'<div class="buildLoadoutColumn">'
        +'<div class="skillGroup"><span>Techniques</span><div>'+r.techniques.map(x=>'<b>'+esc(x)+'</b>').join('')+'</div></div>'
        +'<div class="skillGroup"><span>Charms</span><div>'+r.charms.map(x=>'<b>'+esc(x)+'</b>').join('')+'</div></div>'
        +((techniqueSwaps.length||charmSwaps.length)?'<div class="buildSwapRows">'
          +techniqueSwaps.map(s=>'<p><strong>Technique Swap:</strong><span class="swapText">'+esc(s[0])+' — <span class="swapNames">'+esc(s[1])+' → '+esc(s[2])+'</span></span></p>').join('')
          +charmSwaps.map(s=>'<p><strong>Charm Swap:</strong><span class="swapText">'+esc(s[0])+' — <span class="swapNames">'+esc(s[1])+' → '+esc(s[2])+'</span></span></p>').join('')
          +'</div>':'')
      +'</div>'
      +'</article>';
  }
  function applyRoleLoadouts(cls){
    const presets=ROLE_PRESETS[cls];
    const grid=document.querySelector('.builds .buildGrid');
    if(!presets||!grid) return;
    const sig=cls+'|'+presets.map(r=>[r.name,...r.techniques,...r.charms,r.offensive,r.defensive].join('~')).join('|');
    if(grid.dataset.rolePresetSig===sig) return;
    grid.dataset.rolePresetSig=sig;
    grid.innerHTML=presets.map(buildCardHtml).join('');
  }
  function picksFor(cls,title){
    const role=roleKey(title);
    const pools=FANTO[cls]||{};
    // Guardian DPS role prefers the offensive pet order; this automatically promotes Pandarial once the staged release patch adds it.
    const guardianDps=cls==='Guardian'&&typeof guardianBuildMode==='function'&&guardianBuildMode()==='dps';
    if(role==='Arena'){const base=pools.Arena||pools.PvP||[];if(guardianDps){const order=['Pandarial','Nyxarchon','Kels','Aegiswing','Terragon','Boaro'];return [...base].sort((a,b)=>(order.indexOf(a.name)<0?99:order.indexOf(a.name))-(order.indexOf(b.name)<0?99:order.indexOf(b.name)));}return base;}
    if(role==='Tournament'){
      const base=pools.Tournament||pools.PvP||pools.Dungeon||[];if(guardianDps){const order=['Pandarial','Nyxarchon','Kels','Aegiswing','Terragon','Boaro'];return [...base].sort((a,b)=>(order.indexOf(a.name)<0?99:order.indexOf(a.name))-(order.indexOf(b.name)<0?99:order.indexOf(b.name)));}return base;
    }
    if(role==='Solo'&&cls==='Dominator'&&typeof dominatorBuildMode==='function'&&dominatorBuildMode()==='heals') return pools.Dungeon||pools.Solo||[];
    const base=pools[role]||[];
    if(guardianDps){
      const order=['Pandarial','Nyxarchon','Kels','Aegiswing','Terragon','Boaro'];
      return [...base].sort((a,b)=>{const ai=order.indexOf(a.name),bi=order.indexOf(b.name);return (ai<0?99:ai)-(bi<0?99:bi);});
    }
    return base;
  }
  // Current S2 direct shop Fantomons. Keep F2P / No Shop eligible for every other acquisition source.
  const SHOP_SOURCE_FANTOMONS=new Set(['Aegiswing','Nyxarchon']);
  function f2pFantomon(picks,pair){
    const used=new Set(pair.map(p=>p.name));
    return picks.find(p=>!SHOP_SOURCE_FANTOMONS.has(p.name)&&!used.has(p.name))
      ||picks.find(p=>!SHOP_SOURCE_FANTOMONS.has(p.name))
      ||null;
  }

  function applyFantos(cls){
    document.querySelectorAll('.builds .buildCard').forEach(card=>{
      const h3=card.querySelector('h3');
      const title=h3?.childNodes?.[0]?.textContent?.trim() || h3?.textContent.trim() || '';
      const picks=picksFor(cls,title);
      if(!picks.length) return;
      let box=card.querySelector('.fantomonPair');
      if(!box){
        box=document.createElement('div');
        box.className='fantomonPair';
        card.appendChild(box);
      }
      const sig=[cls,roleKey(title),...picks.flatMap(p=>[p.name,p.why])].join('|');
      if(box.dataset.sig===sig) return;
      box.dataset.sig=sig;
      const pair=picks.slice(0,2);
      const noShop=f2pFantomon(picks,pair);
      const shown=noShop?[...pair,noShop]:pair;
      const labels=['Main','Alt','Alt'];
      box.innerHTML='<span>Combat Fantomons</span>'
        +'<div class="fantomonRankList">'
        +shown.map((p,i)=>'<div class="fantomonPick'+(i===0?' main':'')+'"><small>'+labels[i]+'</small><b>'+esc(p.name)+'</b><p>'+esc(p.why)+'</p></div>').join('')
        +'</div>';
    });
  }
  function apply(){
    const cls=activeClass();
    if(!cls) return;
    document.querySelectorAll('.builds .buildRoleTabs').forEach(x=>x.remove());
    applyRoleLoadouts(cls);
    applyFantos(cls);
    ensureMetaControls(cls);
    applyMetaVisibility(cls);
  }
  let queued=false,suppressQueuedApply=false;
  function queueApply(){
    if(queued) return;
    queued=true;
    requestAnimationFrame(()=>{queued=false;apply();});
  }
  // BUILD_SWITCH_NO_FLICKER_V1: main Builds renderer calls this inside the class-click task.
  // META controls/loadouts/Fantomons therefore exist before the next paint instead of appearing
  // one animation frame after the raw class markup. Suppress the observer echo for that task.
  window.__applyBuildMetaNow=()=>{
    suppressQueuedApply=true;
    apply();
    setTimeout(()=>{suppressQueuedApply=false;},0);
  };
  document.addEventListener('DOMContentLoaded',()=>{
    // Initial/restored Builds view gets the same one-paint treatment.
    apply();
    const root=document.querySelector('.builds');
    if(root) new MutationObserver(()=>{if(!suppressQueuedApply) queueApply();}).observe(root,{subtree:true,childList:true,attributes:true,attributeFilter:['class','aria-pressed']});
    root?.addEventListener('click',e=>{
      const guardianBtn=e.target.closest?.('[data-guardian-mode]');
      if(guardianBtn&&activeClass()==='Guardian'){metaWrite('sxs-build-guardian-mode',guardianBtn.dataset.guardianMode==='dps'?'dps':'tank');applyMetaVisibility('Guardian');queueApply();return;}
      const dominatorBtn=e.target.closest?.('[data-dominator-mode]');
      if(dominatorBtn&&activeClass()==='Dominator'){metaWrite('sxs-build-dominator-mode',dominatorBtn.dataset.dominatorMode==='heals'?'heals':'dps');applyMetaVisibility('Dominator');queueApply();return;}
      const modeBtn=e.target.closest?.('[data-meta-mode]');
      if(modeBtn){metaWrite('sxs-build-meta-mode',modeBtn.dataset.metaMode);applyMetaVisibility(activeClass());return;}
      const sizeBtn=e.target.closest?.('[data-tournament-size]');
      if(sizeBtn){metaWrite('sxs-build-tournament-size',sizeBtn.dataset.tournamentSize);applyMetaVisibility(activeClass());}
    });
  });
  window.addEventListener('load',queueApply);
})();

/* ---- build module boundary ---- */

(()=>{
  const I=(effect,why,meta='')=>({effect,why,meta});
  const INFO={
    // Conqueror / Duelist line
    'Flash Fire':I('Fast elemental attack with useful reach and mobility. It helps Conqueror cross space while still contributing damage.','Preferred in Dungeon and 4v4 when reach and fast target access matter.','Elemental · Mobility'),
    'Flame Aura':I('Repeating Fire damage that performs well into both single targets and groups; one of the strongest inherited elemental engines for the class.','Core PvE damage piece when Dispel or extra mobility is not required.','Fire · Repeating damage'),
    'Flickering Blade':I('Single-target Technique with no cooldown. If the target survives, it has a 60% chance to repeat, up to two extra attacks.','The repeat mechanic gives Conqueror excellent cleanup and boss pressure every turn.','0 CD · Single target · Repeat'),
    'Blade Storm':I('Hard-hitting line AoE. Positioning matters because its coverage is narrower than broad circular AoE skills.','Reliable damage across current Conqueror content, especially when enemies can be lined up.','AoE · Line'),
    'Darkness Descends':I('Mobility plus buff removal/Dispel, trading some raw PvE damage for control and access.','A premium PvP slot for stripping enemy buffs and staying on priority targets.','Mobility · Dispel'),
    'Doom Blade':I('Aggressive leap/area-pressure Technique used to close distance and add immediate burst.','Arena flex when you want harder pressure instead of the sustain offered by Soul Piercer.','Mobility · AoE pressure'),
    'Soul Piercer':I('Damage Technique with sustain utility, giving the Conqueror a safer way to keep pressure up.','Especially useful in 2v2 where losing one unit is half the team.','Damage · Sustain'),
    'Piercing Assault':I('Core T4 Charm that lets Conqueror ignore enemy DEF; the effect improves while you have buffs.','The defining damage Charm for current Conqueror and a long-term investment.','DEF ignore'),
    'Tactical Adaptation':I('Adaptive Charm that shifts between a strong offensive or defensive benefit depending on how many enemies are nearby.','Universal because it automatically changes value between bosses, packs and PvP.','Adaptive offense/defense'),
    'Soul Splash':I('Offensive follow-up/proc Charm that benefits from repeated attacks.','Pairs especially well with Flickering Blade repeats in fast PvE clears.','Follow-up damage'),
    'Insightful Eye':I('Crit-focused Charm used to stabilize Crit Rate before gear and other permanent sources solve the breakpoint.','Use early; replace with a greedier damage Charm once your effective Crit Rate is high enough.','Crit support'),
    'Soul Breaker':I('Greedy offensive Charm used after Crit Rate is already solved.','The standard upgrade over Insightful Eye in PvP or developed S2 accounts.','Offense'),
    'Indomitable Will':I('Major survival Charm with a strong safety window and self-healing.','Keep it in serious PvP; in easy PvE it is the first slot you can greed into damage.','Survival · Heal'),
    'Blazing Clash':I('Boss-oriented offensive Charm that adds sustained Fire/elemental pressure in longer fights.','Used in the greedier Crucible/Conquest score setup when survival is already handled.','Boss offense'),
    'Crit Mastery':I('Crit payoff Charm for accounts that already have enough Crit Rate without Insightful Eye.','A high-end boss flex once the Crit breakpoint is solved.','Crit payoff'),
    'Gale Dance':I('Team-tempo Technique that can provide a useful SPD advantage when coordinated with another Conqueror.','A 4v4 composition flex; normally only one Conqueror needs to carry it.','Team SPD · Utility'),

    // Guardian / Knight line
    'Valor Surge':I('Team-oriented buff Technique with cleanse utility.','Universal Guardian slot: keep it equipped for the team damage buff and cleanse; flex another Technique when you need more Taunt.','Team buff · Cleanse'),
    'Heart of Challenge':I('Core group-Taunt Technique that finally gives Guardian reliable frontline control.','Central to the Tank setup whenever you need enemies focused on you instead of allies.','Taunt · Tank'),
    'Luminous Shield':I('Reliable shield Technique that supports Guardian’s DEF/Block survival loop.','Tank staple and a useful defensive anchor in PvP bruiser builds.','Shield'),
    'Desperate Protection':I('Emergency ally-protection Technique for covering a vulnerable teammate when aggro or control breaks down.','Strong in 2v2 and as a 4v4 fallback, but not the default organized 4v4 slot when Lunarwater Threads + Heart of Challenge are reliably funneling damage into the Guardian.','Ally protection · Emergency defense'),
    'Hamper Strike':I('Direct Taunt option with no pre-cast and a 1-turn cooldown.','Use when the normal Tank bar needs more reliable Taunt uptime.','Taunt · 1 CD'),
    'Swirling Blade':I('Strong Water damage Technique that also grants a self-shield.','The best reusable offensive T4 Guardian investment and a core offensive Technique.','Water · Damage · Shield'),
    'Lunarwater Threads':I('Wide Water control Technique that pulls enemies together while contributing Cold setup and pressure.','Premium organized-4v4 control: group enemies into the Guardian’s zone, then pair it with Heart of Challenge so Taunt funnels pressure into the tank.','Water · Pull · Control · Cold setup'),
    'Seismic Tide':I('Water Technique favored for steadier Cold stacking.','Used when consistency matters more than a situational utility slot.','Water · Cold stacking'),
    'Raging Maelstrom':I('Large Water/AoE payoff for the full offensive Water build.','Best when multiple enemies let DPS Guardian spread pressure and exploit Cold setup.','Water · AoE'),
    'Forceful Charge':I('Engage/mobility Technique that helps Guardian stay attached to a target and apply pressure.','Useful in Arena and 2v2 where target access matters more than broad AoE.','Mobility · Pressure'),
    'Star Shattering Slash':I('Heavy direct-damage Technique inherited from Paladin; it starts as one of the Knight line’s strongest single-target nukes and scales hard with rank.','Use it for Crucible/Conquest and other concentrated targets; it also adds real kill pressure to Block/counter PvP builds.','Single target · Heavy hit'),
    'Leap Attack':I('Mobile attack with a chance to reduce enemy DEF.','Boss-support Guardian uses it to contribute damage amplification while staying active.','Mobility · DEF down'),
    'Holy Purification':I('Purification/Dispel utility Technique for removing problematic enemy buffs or effects.','Excellent in boss support when there is actually something important to remove; otherwise it is a flex slot.','Dispel utility'),
    'Light Sword Array':I('Aggressive Light damage flex used when Guardian can afford to give up part of its shield package.','A later/Pandarial-friendly offensive swap rather than the default Tank choice.','Light · Offense'),
    'Iron Will':I('Reduces damage taken from enemies that are Taunted.','Extremely efficient in Tank builds because Guardian now has reliable Taunt access.','Taunt synergy · Mitigation'),
    'Holy Aegis':I('Raises DEF and improves DEF-based shields.','Universal Guardian durability that also strengthens the shield loop.','DEF · Shield scaling'),
    'Block Awareness':I('Improves Block consistency.','Use when your natural Block rate is not yet high enough to make the defensive loop reliable.','Block'),
    'Soul Protection':I('At battle start, converts 50% of HP into a large shield; remaining shield can restore HP at the end of the fight.','One of Guardian’s strongest universal T4 survival Charms, especially in dungeons.','Opening shield'),
    'Iron Fortress':I('Heavy team-mitigation Charm for protecting the party through dangerous windows.','Premium in hard group content and Tournament; less necessary when the team already survives comfortably.','Team mitigation'),
    'Oath of Vigil':I('Protects the lowest-HP ally with Vigil, redirecting part of their incoming damage to Guardian and reducing that redirected damage.','Especially strong in 2v2/4v4 where protecting a carry can decide the round.','Ally protection'),
    'Rebound':I('Counter/reflect-style Charm that punishes enemies for repeatedly hitting a durable Guardian.','Core Arena and small-team PvP pressure without abandoning the Block identity.','Counter · Reflect'),
    'Block Mastery':I('Turns high Block investment into a stronger defensive/counter package.','Keeps the PvP bruiser build consistent against repeated-hit attackers.','Block scaling'),
    'Frigid Aura':I('Core Water/Cold damage amplifier for offensive Guardian.','The first Charm you build around in the Water DPS build.','Water/Cold amp'),
    'Defensive Assault':I('Converts Guardian’s defensive investment into offensive pressure.','Lets DPS Guardian remain bruiser-tanky instead of becoming a fragile pseudo-DPS.','Defense → offense'),
    'Frigid Glint':I('Cold-synergy offensive Charm that rewards the Water stacking loop.','Paired with Frigid Aura in the Water DPS build.','Cold synergy'),
    'Potential Rebirth':I('Second-chance survival Charm.','The safety flex in offensive Guardian; replace it with more damage only when deaths are no longer a concern.','Cheat death'),
    'Pursuit of Victory':I('Greedy offensive Charm for situations where survival is already solved.','Used in boss-score or overgeared PvE versions of DPS Guardian.','Offense'),
    'Eye for an Eye':I('Counter-oriented offensive Charm that adds punishment while Guardian absorbs pressure.','PvP DPS flex when you can survive without another pure defensive slot.','Counter offense'),

    // Destroyer / Sorcerer line
    'Formation Breaker':I('Core Destroyer Technique that buffs from your own ATK and has a 50% chance to accelerate allied actions.','Long-lived core even in Arena; in team content the ally action advance becomes especially valuable.','ATK buff · Action advance'),
    'Fiery Star Trail':I('Fire AoE setup piece that adds Fire pressure across packs.','Dungeon Fire build uses it to generate more Fire events for the Fiery Burst package.','Fire · AoE'),
    'Fireball':I('Straightforward Fire damage Technique.','In the horde build its main job is reliable Fire triggering for the Crit/Fiery Burst engine.','Fire'),
    'Meteoric Flames':I('Strong Fire/area damage Technique that remains useful in mixed-element setups.','Excellent on packs and can outperform some boss options when target size/resistance favors it.','Fire · AoE'),
    'Divine Wrath':I('Heavy area damage whose value improves on large targets.','Boss-score option; on small bosses Meteoric Flames can test better.','AoE · Boss-size sensitive'),
    'Wind Blade Spiral':I('A smaller, faster-cooldown alternative to Howling Hurricane that produces strong sustained Wind damage.','One of Destroyer’s best repeatable damage Techniques in both PvE and PvP.','Wind · Fast cycle'),
    'Thunder of Judgment':I('Destroyer’s highest single-target Technique and it prioritizes bosses.','Ideal for Crucible/Conquest because it avoids wasting the big hit on random adds.','Single target · Boss priority'),
    "Wind's Delight":I('High-hit Wind single-target pressure that can produce excellent proc value.','A rank-dependent score/PvP flex; dummy-test it against Wind Blade Spiral or Tempest Sphere.','Wind · Multi-hit'),
    'Tempest Sphere':I('Compact Wind pressure that is more reliable on player-sized or small targets than giant-area skills.','A strong Arena/2v2 option where precise targeting matters.','Wind · Small-target'),
    'Howling Hurricane':I('Broad Wind AoE with strong multi-target coverage.','Best when you can actually hit several enemies; 4v4 gives it much more value than 1v1.','Wind · AoE'),
    'Rapid Cast':I('Front-loads the caster rotation so damage comes online faster.','Core tempo Charm for PvE score and team builds where acting quickly matters.','Tempo'),
    'Void Bubble':I('Defensive Charm that buys a fragile Mage extra survival.','Keep it until you clearly outgear the content; a dead Destroyer loses more damage than the greed slot gains.','Defense'),
    'Explosive Spirit':I('Builds Crit support as you use Fire Techniques.','One of the two core pieces of the Fire horde setup because it helps trigger Fiery Burst.','Fire · Crit support'),
    'Fiery Burst':I('Bonus Fire damage triggered from Fire crits; AoE can create separate burst instances on multiple targets.','The main payoff of the Dungeon Fire build.','Fire · Crit proc'),
    'Mana Surge':I('Greedy offensive Charm used to push damage when extra protection is unnecessary.','Boss-score flex; swap to a defensive option when survival costs attempts.','Offense'),
    'Radiant Sear':I('Major repeat-hit/proc damage Charm that rewards multi-hit elemental rotations.','A staple in mixed Wind/Light damage setups and 4v4 AoE pressure.','Proc damage'),
    'Incarnation of Light':I('Greedy Light-oriented damage slot for score content.','Used only when the encounter lets Destroyer sacrifice defensive utility for more output.','Light · Offense'),
    'Cyclone Lament':I('Wind/Laceration payoff Charm that benefits from repeated Wind Techniques.','Core mono-Wind pressure in Arena and strong when the build carries multiple Wind attacks.','Wind · Laceration'),
    'Repelling Wind':I('PvP control Charm used to create space and disrupt enemy tempo.','Excellent against melee pressure in Arena/2v2; flex to damage if your team already controls targets.','Control · Knockback'),
    "Wind's Shadow":I('Wind PvP utility slot focused on tempo/mobility rather than raw sheet damage.','Used in the dedicated solo-control setup where surviving and maintaining spacing matter.','Wind · PvP utility'),

    // Dominator / Sage line
    'Waterling Summon':I('Summons a Waterling that provides recurring healing/support.','A stable source of sustain in the dedicated Dungeon healer bar.','Summon · Healing'),
    'Rejuvenating Rain':I('Simple single-target heal that can be used every turn.','Reliable spot-healing and the first active healer Technique to prioritize.','0 CD · Single-target heal'),
    'Radiant Restoration':I('Direct party-healing Technique.','Main group-sustain button and the one healing slot retained in several hybrid support bars.','Group heal'),
    'Frenzy Totem':I('Team-support Totem that increases offensive throughput.','Used when the goal is boosting a carry rather than maximizing personal Dominator damage.','Team buff · Summon'),
    'Healing Touch':I('Additional direct-healing Technique.','Swap it in when the default healer bar needs more raw healing than Frenzy Totem provides.','Healing'),
    'Phantom Light':I('Improves healing and converts overhealing into shields.','Mandatory core Charm for a dedicated T4 healer.','Healing amp · Overheal shield'),
    'Healing Mastery':I('Universal healing-throughput Charm.','Straightforward core scaling for the healer profile.','Healing boost'),
    'Overhealing':I('Healer safety/value Charm that rewards excess healing rather than letting it go to waste.','Part of the standard sustain build in Dungeon and carry-support setups.','Healing utility'),
    'Resurrection':I('Revives a fallen ally.','Massive round-swing utility in 2v2/4v4 and valuable insurance in difficult PvE.','Revive'),
    'Mantra of Blessings':I('Strong damage buff for a carry or for yourself in solo content.','Excellent in scoring teams; in hard dungeons it loses priority to survival tools.','Damage buff'),
    'Decoy Clone':I('Position-dependent support Technique that can amplify a hypercarry’s damage.','One of the best score-support tools when your team can exploit the clone connection.','Carry amp · Positioning'),
    'Mana Blast':I('Dark/Erosion attack used to build the higher-ceiling damage-over-time plan.','Core in AoE and becomes the high-Effect-Hit-Rate single-target flex over Chaos Rune.','Dark · Erosion'),
    'Chaos Rune':I('Direct-damage Dark Technique used in the single-target hybrid so damage is less dependent on Erosion landing.','Best when Effect Hit Rate is not high enough to justify going all-in on Erosion; high EHR can flex it to Mana Blast.','Dark · Direct damage · ST'),
    'Shadow Impact':I('Broad Dark AoE payoff carried forward for T4 because Dominator receives no new dedicated AoE replacement.','The fourth Technique in the Dungeon/4v4 AoE setup where multiple targets justify its coverage.','Dark · AoE'),
    'Dark Bullet':I('Reliable Dark attack used to apply/maintain Erosion pressure.','Cheap, consistent glue for both DPS and support bars that still want debuff value.','Dark · Erosion'),
    'Dark Starburst':I('Reliable multi-hit direct Dark damage that does not require Erosion stacks to deal good damage.','Keeps Dominator functional when Effect Hit Rate or Erosion RNG is not perfect.','Dark · Multi-hit · Direct damage'),
    'Abyssal Hand':I('Dark AoE/control Technique used to spread pressure and debuffs across multiple targets.','Excellent in Arena/Tournament hybrids where broad Erosion/Slow pressure matters.','Dark · AoE · Debuff'),
    'Shadow of Termination':I('Single-target Dark finisher that cashes out the Erosion-oriented damage plan.','The kill-pressure payoff in Arena and 2v2.','Dark · Finisher'),
    'Shadow Erosion':I('Core Charm for the Erosion damage engine.','Mandatory whenever the bar is actually trying to win through Erosion rather than pure support.','Erosion'),
    'Linked Misfortune':I('Accelerates Erosion/debuff stack generation.','Pairs with Shadow Erosion to raise the ceiling of the Dark DPS build.','Erosion support'),
    'Shadow Vengeance':I('Defensive/offensive safety-window Charm that helps Dominator survive long enough to finish a damage cycle.','Very valuable in PvP where fragile Sage builds otherwise die before their setup pays off.','Survival · Damage window'),
    "Night's Blessing":I('General Dark-damage scaling Charm.','A standard selfish DPS slot in the Erosion/direct-damage build.','Dark damage'),
    'Aberrancy':I('Broad debuff-oriented Charm whose value rises when several enemies/effects are in play.','More attractive in 4v4 than solo Arena because team fights provide more debuff interactions.','Debuff utility')
  };

  const finePointer=()=>matchMedia('(hover:hover) and (pointer:fine)').matches;
  let layer=null,active=null,closeTimer=0,raf=0;
  const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  function ensureLayer(){
    if(layer) return layer;
    layer=document.createElement('div');
    layer.className='buildSkillTipLayer';
    layer.setAttribute('role','tooltip');
    layer.id='buildSkillTooltip';
    document.body.append(layer);
    return layer;
  }
  function dataFor(el){
    const name=el.textContent.trim();
    const kind=el.closest('.skillGroup')?.querySelector(':scope > span')?.textContent.trim()?.replace(/s$/,'')||'Skill';
    const info=INFO[name]||I('This skill is part of the selected loadout. Exact values and scaling depend on its rarity, level and ascension.','See the build notes for why it is equipped in this setup.');
    return {name,kind,...info};
  }
  function position(){
    if(!layer||!active||!active.isConnected) return close();
    const r=active.getBoundingClientRect(),w=layer.offsetWidth||300,h=layer.offsetHeight||120,pad=8,gap=7;
    let left=r.left+(r.width-w)/2;
    left=Math.max(pad,Math.min(left,innerWidth-w-pad));
    const roomBelow=innerHeight-r.bottom-gap;
    let top=roomBelow>=h+pad?r.bottom+gap:r.top-h-gap;
    top=Math.max(pad,Math.min(top,innerHeight-h-pad));
    layer.style.left=Math.round(left)+'px';
    layer.style.top=Math.round(top)+'px';
  }
  function open(el){
    clearTimeout(closeTimer);
    const d=dataFor(el),tip=ensureLayer();
    if(active&&active!==el) active.setAttribute('aria-expanded','false');
    active=el;
    const tags=(d.meta||'').split('·').map(x=>x.trim()).filter(Boolean);
    tip.innerHTML=`<div class="buildSkillTipHead"><strong>${esc(d.name)}</strong><span>${esc(d.kind)}</span></div><div class="buildSkillTipMeta">${tags.map(x=>`<i>${esc(x)}</i>`).join('')}</div><p class="buildSkillTipEffect">${esc(d.effect)}</p><p class="buildSkillTipWhy"><b>Why here:</b> ${esc(d.why)}</p>`;
    el.setAttribute('aria-describedby',tip.id);
    el.setAttribute('aria-expanded','true');
    tip.classList.add('open');
    requestAnimationFrame(position);
  }
  function close(){
    clearTimeout(closeTimer);
    if(active){active.setAttribute('aria-expanded','false');active.removeAttribute('aria-describedby');}
    active=null;
    layer?.classList.remove('open');
  }
  function scheduleClose(){clearTimeout(closeTimer);closeTimer=setTimeout(close,70)}
  function prep(root=document){
    root.querySelectorAll?.('#buildContent .skillGroup b:not([data-skill-tooltip])').forEach(el=>{
      el.dataset.skillTooltip='1';
      el.tabIndex=0;
      el.setAttribute('role','button');
      el.setAttribute('aria-haspopup','true');
      el.setAttribute('aria-expanded','false');
      el.addEventListener('mouseenter',()=>{if(finePointer())open(el)});
      el.addEventListener('mouseleave',()=>{if(finePointer())scheduleClose()});
      el.addEventListener('focus',()=>open(el));
      el.addEventListener('blur',()=>{if(finePointer())scheduleClose()});
      el.addEventListener('click',e=>{
        if(finePointer()) return;
        e.preventDefault();e.stopPropagation();
        active===el?close():open(el);
      });
      el.addEventListener('keydown',e=>{
        if(e.key==='Escape'){close();el.blur();return;}
        if((e.key==='Enter'||e.key===' ')&&!finePointer()){e.preventDefault();active===el?close():open(el);}
      });
    });
  }
  document.addEventListener('pointerdown',e=>{if(active&&!e.target.closest?.('#buildContent .skillGroup b[data-skill-tooltip]'))close()});
  document.addEventListener('keydown',e=>{if(e.key==='Escape')close()});
  addEventListener('resize',()=>{if(active)position()});
  document.addEventListener('scroll',()=>{if(!active||raf)return;raf=requestAnimationFrame(()=>{raf=0;position()})},true);
  document.addEventListener('DOMContentLoaded',()=>{
    const host=document.getElementById('buildContent');
    prep(document);
    if(host)new MutationObserver(()=>{if(active&&!active.isConnected)close();prep(document)}).observe(host,{subtree:true,childList:true});
  });
  addEventListener('load',()=>prep(document));
})();

/* ---- build module boundary ---- */

(()=>{
  const BUILD_STAT_PROFILES={
    Conqueror:{
      rule:'Current T4 evidence supports ATK ≥ Elemental Mastery on main secondaries. Crit Rate/Crit DMG are the premium reroll stats; Accuracy matters more in PvP and high-Block fights.',
      rows:[['Sword','ATK ≥ Elemental Mastery > SPD'],['Gauntlets','ATK ≥ Elemental Mastery > SPD'],['Helmet','DEF ≥ Physical RES = Elemental RES > HP'],['Chest','DEF ≥ Physical RES = Elemental RES > HP'],['Boots','ATK ≥ Elemental Mastery > SPD']],
      substats:'Crit Rate / Crit DMG > Accuracy > Elemental Mastery > SPD / SPD% > ATK / ATK%'
    },
    Guardian:{
      tank:{
        rule:'Tank Guardian is built around Block first. After that, DEF/DMG RES drive survival while SPD keeps Taunt, shields and buffs cycling before the enemy can act.',
        rows:[['Sword','SPD > ATK > Physical Mastery > Elemental Mastery'],['Shield','DEF > HP > Physical RES = Elemental RES'],['Helmet','DEF ≥ Physical RES = Elemental RES > HP > Effect RES'],['Chest','DEF ≥ Physical RES = Elemental RES > HP'],['Boots','SPD > ATK > Elemental Mastery = Physical Mastery']],
        substats:'Block Rate > DEF > SPD > HP > DEF% > SPD% > HP%'
      },
      dps:{
        rule:'DPS Guardian uses the offensive Water/counter shell, but Block still matters because the class gains damage by staying active. After a healthy Block floor, Crit Rate, SPD and ATK/Mastery are the damage-quality rolls.',
        rows:[['Sword','SPD > ATK > Elemental Mastery > Physical Mastery'],['Shield','DEF > HP > Physical RES = Elemental RES'],['Helmet','DEF ≥ Physical RES = Elemental RES > HP'],['Chest','DEF ≥ Physical RES = Elemental RES > HP'],['Boots','SPD > ATK > Elemental Mastery = Physical Mastery']],
        substats:'Block Rate > Crit Rate > SPD / SPD% > ATK / ATK% > Elemental Mastery > Crit DMG'
      }
    },
    Destroyer:{
      rule:'S2 Destroyer is balance-sensitive, not permanently EM-first. Keep a healthy Elemental Mastery floor, then flat ATK can match or beat more EM on developed accounts. Crit remains premium; dummy-test close swaps.',
      rows:[['Staff','ATK ≈ Elemental Mastery > Crit > SPD'],['Codex','ATK ≈ Elemental Mastery > Crit > SPD'],['Helmet','DEF ≥ Physical RES = Elemental RES > HP > Effect RES'],['Chest','DEF ≥ Physical RES = Elemental RES > HP'],['Boots','ATK ≈ Elemental Mastery > SPD']],
      substats:'Crit Rate / Crit DMG > ATK / ATK% ≈ Elemental Mastery > Accuracy > SPD / SPD%'
    },
    Dominator:{
      dps:{
        rule:'Effect Hit Rate is a threshold stat: get enough to land Erosion reliably, then favor damage-quality affixes instead of blindly stacking more EHR. If Erosion is unreliable, hybrid/direct damage is safer.',
        rows:[['Staff','Effect Hit Rate ≥ Elemental Mastery ≥ ATK > SPD'],['Orb','Effect Hit Rate ≥ Elemental Mastery ≥ ATK > SPD'],['Helmet','DEF ≥ Physical RES = Elemental RES > HP > Effect RES'],['Chest','DEF ≥ Physical RES = Elemental RES > HP'],['Boots','Elemental Mastery > ATK > SPD']],
        substats:'Effect Hit Rate > Crit Rate / Crit DMG > Elemental Mastery > ATK / ATK% > SPD / SPD%'
      },
      heals:{
        rule:'Healer Dominator is SPD-first on Staff/Orb/Boots and HP-first on Helmet/Chest. Effect Hit Rate is the second main-secondary target on Staff/Orb, but only an average healer affix when rerolling substats.',
        rows:[['Staff','SPD > Effect Hit Rate > Elemental Mastery > ATK'],['Orb','SPD > Effect Hit Rate > Elemental Mastery > ATK'],['Helmet','HP > DEF ≥ Physical RES = Elemental RES > Effect RES'],['Chest','HP > DEF ≥ Physical RES = Elemental RES'],['Boots','SPD > Elemental Mastery > ATK']],
        substats:'Healing Boost > SPD / SPD% > HP / HP% > DMG RES'
      }
    }
  };

  const GUARDIAN_PRIORITY={
    tank:[
      ['Tank technique investment','Heart of Challenge first','Prioritize Taunt, team support and reliable survival—the tools that make Guardian valuable in difficult group content.',[
        ['Heart of Challenge','Core group Taunt and one of the most important reasons to bring a Guardian.'],
        ['Valor Surge','Pre-cast team damage buff plus cleanse utility.'],
        ['Luminous Shield','Reliable shield layer across dungeon and PvP tank bars.'],
        ['Desperate Protection / Hamper Strike','Choose survival or more Taunt based on the encounter.']
      ]],
      ['Tank charm investment','Soul Protection first','Start with reliable mitigation and party protection, then add situational damage only when survival is already comfortable.',[
        ['Soul Protection','Massive opening effective HP and the most universal Guardian T4 charm.'],
        ['Iron Will','Excellent damage reduction once Taunt is active.'],
        ['Holy Aegis','DEF plus stronger DEF-scaling shields.'],
        ['Iron Fortress / Oath of Vigil','Team mitigation and ally protection become premium in Tournament.']
      ]]
    ],
    dps:[
      ['DPS technique investment','Swirling Blade first','Build around Water/Cold pressure while keeping enough Block and durability to stay active.',[
        ['Swirling Blade','Best reusable T4 offensive Technique: Water damage plus a self-shield.'],
        ['Raging Maelstrom','The high-value AoE payoff in the full Water shell.'],
        ['Lunarwater Threads','Reliable Water pressure and Cold setup.'],
        ['Seismic Tide','Keeps Cold stacking consistent in both AoE and boss variants.']
      ]],
      ['DPS charm investment','Frigid Aura first','Build around the actual Water shell, then keep one survival flex when content can punish you.',[
        ['Frigid Aura','Core Water/Cold damage amplifier.'],
        ['Frigid Glint','Directly supports the Cold-based offensive loop.'],
        ['Defensive Assault','Turns Guardian durability into useful offensive pressure.'],
        ['Potential Rebirth / Pursuit of Victory','Safety for hard content; swap to Pursuit when survival is already solved.']
      ]]
    ]
  };

  const DOMINATOR_PRIORITY={
    dps:[
      ['DPS technique investment','Dark Starburst first','Only Techniques that are actually equipped in the DPS loadouts are ranked here.',[
        ['Dark Starburst','Reliable multi-hit single-target damage.'],
        ['Shadow of Termination','Key single-target Dark finisher.'],
        ['Dark Bullet','Consistent Erosion application across the DPS bars.'],
        ['Mana Blast / Abyssal Hand','Both are equipped in the AoE/Erosion loadout.']
      ]],
      ['DPS charm investment','Shadow Erosion first','Only Charms that actually occupy the DPS loadouts are ranked here.',[
        ['Shadow Erosion','Core Erosion engine.'],
        ['Linked Misfortune','Accelerates stack generation.'],
        ["Night's Blessing",'Universal Dark damage scaling.'],
        ['Shadow Vengeance','The equipped survival/damage-window slot in both DPS bars.']
      ]]
    ],
    heals:[
      ['Healing technique investment','Rejuvenating Rain first','Rank the active healing Techniques that are actually equipped in the healer loadout.',[
        ['Rejuvenating Rain','Repeatable single-target heal and a core T4 upgrade.'],
        ['Radiant Restoration','Strong direct party sustain.'],
        ['Waterling Summon','Reliable recurring healing.'],
        ['Frenzy Totem','The equipped support/throughput slot in the main healing bar.']
      ]],
      ['Healing charm investment','Phantom Light first','Rank the healer Charms that actually occupy the support shell.',[
        ['Phantom Light','Mandatory healing boost plus overheal-to-shield conversion.'],
        ['Healing Mastery','Universal throughput.'],
        ['Overhealing','Core healer-shell safety and value.'],
        ['Resurrection / Overhealing','The carry-support recovery/flex slot as actually shown below.']
      ]]
    ]
  };

  const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const root=()=>document.getElementById('buildContent');
  const activeClass=()=>document.querySelector('#classTabs button.active')?.dataset.class||'';
  const roleMode=cls=>{
    try{
      if(cls==='Guardian') return localStorage.getItem('sxs-build-guardian-mode')==='dps'?'dps':'tank';
      return localStorage.getItem('sxs-build-dominator-mode')==='heals'?'heals':'dps';
    }catch(_){return cls==='Guardian'?'tank':'dps';}
  };
  const profileFor=(cls,mode)=>{
    const p=BUILD_STAT_PROFILES[cls];
    return p?.[mode]||p||null;
  };
  function renderQuickStats(host,cls,mode){
    const profile=profileFor(cls,mode);
    const guide=host.querySelector(':scope > .guideSummary');
    if(!profile||!guide) return;
    let quick=guide.querySelector('.buildQuickStats');
    if(!quick){
      quick=document.createElement('div');
      quick.className='buildQuickStats';
      if(guide.children[1]) guide.children[1].replaceWith(quick); else guide.append(quick);
      guide.classList.add('buildSummaryCompact');
    }
    quick.innerHTML=`<div class="quickTitle">Stat priorities</div><p class="quickRule">${esc(profile.rule)}</p><div class="quickGearGrid">${profile.rows.map(([slot,stats])=>`<div class="quickGearRow"><b>${esc(slot)}</b><span>${esc(stats)}</span></div>`).join('')}</div><div class="quickSubstats"><b>Substats</b><span>${esc(profile.substats)}</span></div>`;
    const gear=host.querySelector(':scope > .gearPanel');
    if(gear) gear.remove();
  }
  function makePanel(data){
    const [kind,title,desc,items]=data;
    const panel=document.createElement('section');
    panel.className='priorityPanel';
    panel.innerHTML=`<div class="priorityIntro"><span>${esc(kind)}</span><strong>${esc(title)}</strong><p>${esc(desc)}</p></div><ol class="priorityList">${items.map((it,i)=>`<li><b>${i+1}</b><div><strong>${esc(it[0])}</strong><p>${esc(it[1])}</p></div></li>`).join('')}</ol>`;
    return panel;
  }
  function ensurePriorityPair(host,cls,mode){
    if(cls==='Guardian'){
      [...host.children].filter(el=>el.classList?.contains('priorityPanel')).forEach(el=>el.remove());
      let pair=host.querySelector(':scope > .priorityPair');
      if(!pair){
        pair=document.createElement('div');
        pair.className='priorityPair';
        const grid=host.querySelector(':scope > .buildGrid');
        if(grid) grid.before(pair); else host.append(pair);
      }
      if(pair.dataset.guardianMode!==mode){
        pair.innerHTML='';
        const data=GUARDIAN_PRIORITY[mode]||GUARDIAN_PRIORITY.tank;
        pair.append(makePanel(data[0]),makePanel(data[1]));
        pair.dataset.guardianMode=mode;
      }
      return;
    }
    if(cls==='Dominator'){
      // The temporary regressed template mixed Techniques and Charms into one panel.
      // Replace those direct panels with one true Technique-left / Charm-right pair per role.
      [...host.children].filter(el=>el.classList?.contains('priorityPanel')).forEach(el=>el.remove());
      for(const key of ['dps','heals']){
        let pair=host.querySelector(`:scope > .priorityPair[data-dominator-role="${key}"]`);
        if(!pair){
          pair=document.createElement('div');
          pair.className='priorityPair';
          pair.dataset.dominatorRole=key;
          const data=DOMINATOR_PRIORITY[key];
          pair.append(makePanel(data[0]),makePanel(data[1]));
          const grid=host.querySelector(':scope > .buildGrid');
          if(grid) grid.before(pair); else host.append(pair);
        }
        pair.hidden=key!==mode;
      }
      return;
    }
    if(host.querySelector(':scope > .priorityPair')) return;
    const panels=[...host.children].filter(el=>el.classList?.contains('priorityPanel'));
    if(panels.length>=2){
      const pair=document.createElement('div');
      pair.className='priorityPair';
      panels[0].before(pair);
      // Existing class templates are ordered Technique first, Charm second.
      pair.append(panels[0],panels[1]);
    }
  }
  // RICH_BUILDS_V2: role tabs filter only role-specific PvE. Arena and Tournament
  // remain useful references in either Dominator mode and stay visible in both.
  function applyDominatorRole(host,mode){
    if(activeClass()!=='Dominator') return;
    host.querySelectorAll(':scope > .priorityPair[data-dominator-role]').forEach(el=>{
      el.hidden=el.dataset.dominatorRole!==mode;
    });
    // Loadout cards are activity-driven by META_BUILD_MODES_V1; the Dominator DPS/Heals toggle only changes stat/priority panels.
  }
  function signature(host,cls,mode){
    const cards=[...host.querySelectorAll('.buildGrid .buildCard h3')].map(x=>x.textContent.trim()).join('|');
    return `${cls}|${mode}|${cards}`;
  }
  let queued=false;
  function apply(){
    queued=false;
    const host=root(),cls=activeClass();
    if(!host||!cls||!BUILD_STAT_PROFILES[cls]) return;
    const mode=(cls==='Dominator'||cls==='Guardian')?roleMode(cls):'dps';
    const sig=signature(host,cls,mode);
    const complete=host.querySelector('.buildQuickStats')&&host.querySelector(':scope > .priorityPair');
    if(host.dataset.richBuildSig===sig&&complete) return;
    host.dataset.richBuildSig=sig;
    renderQuickStats(host,cls,mode);
    ensurePriorityPair(host,cls,mode);
    applyDominatorRole(host,mode);
  }
  // BUILD_VISUAL_STABILITY_V2: class switching calls the rich-layout transformer
  // in the same click task, before the browser paints the newly mounted class.
  window.__applyBuildRichNow=apply;
  function queue(){
    if(queued) return;
    queued=true;
    requestAnimationFrame(()=>setTimeout(apply,0));
  }
  document.addEventListener('DOMContentLoaded',()=>{
    const host=root();
    if(host) new MutationObserver(queue).observe(host,{subtree:true,childList:true});
    document.getElementById('classTabs')?.addEventListener('click',queue);
    host?.addEventListener('click',e=>{if(e.target.closest?.('[data-dominator-mode],[data-guardian-mode]')) setTimeout(()=>{if(host) host.dataset.richBuildSig='';queue();},0);});
    queue();
  });
  window.addEventListener('load',queue);
})();

/* ---- build module boundary ---- */

(()=>{
  function stripLegacyBuildSeasonNav(){
    const toggle=document.getElementById('buildSeasonToggle');
    if(toggle) toggle.remove();
    const cell=document.querySelector('.sectionSwitch > .buildsNavCell');
    if(!cell) return;
    const button=cell.querySelector(':scope > button[data-section="builds"]');
    if(button) cell.replaceWith(button);
    else cell.remove();
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',stripLegacyBuildSeasonNav,{once:true});
  else stripLegacyBuildSeasonNav();
  window.addEventListener('load',stripLegacyBuildSeasonNav,{once:true});
})();

/* ---- build module boundary ---- */

(()=>{
  // BUILD_ROLL_GUIDE_WARLORD_V1
  const R={
    atk:['ATK','Lv162 scaling',1,'Flat ATK scales with receiving gear level. Global-English Warlord-era transfer evidence at Lv162 shows inherited ATK lines reaching 3577 and 4501, but those are observed values rather than a proven Affix Preview maximum.',1],
    atkpct:['ATK%','Lv162 max unconfirmed',1,'ATK% is a separate percentage substat from flat ATK. Current Global guides confirm the affix exists, but I do not have a direct Global-English Warlord Affix Preview proving its Lv162 maximum.',0],
    def:['DEF','Lv162 scaling',1,'Flat DEF scales with receiving gear level. Global-English Warlord-era transfer evidence at Lv162 shows an inherited DEF line reaching 3603, but that is an observed value rather than a proven Affix Preview maximum.',1],
    defpct:['DEF%','Lv162 max unconfirmed',1,'DEF% is a separate percentage substat from flat DEF. Current Global evidence includes percentage DEF refinement lines, but I do not have a direct Warlord Affix Preview proving the Lv162 maximum.',0],
    hp:['HP','Lv162 scaling',1,'Flat HP scales with receiving gear level. I do not have a direct Global-English Warlord Affix Preview capture proving the maximum Lv162 roll.',1],
    hppct:['HP%','Lv162 max unconfirmed',1,'HP% is a separate percentage substat from flat HP. Current Global guides confirm the affix exists, but I do not have a direct Global-English Warlord Affix Preview proving its Lv162 maximum.',0],
    spd:['SPD','Lv162 scaling',1,'Flat SPD scales with receiving gear level. I do not have a direct Global-English Warlord Affix Preview capture proving the maximum Lv162 roll.',1],
    spdpct:['SPD%','Lv162 max unconfirmed',1,'SPD% is a separate percentage substat from flat SPD. Current Global guides confirm the affix exists, but I do not have a direct Global-English Warlord Affix Preview proving its Lv162 maximum.',0],
    crit:['Crit Rate','≈ 7.50%',1,'Approximate Warlord/Lv162 standalone Crit Rate maximum. Older-server first-post-160 scaling reports about +50% for normal percentage affixes, and Global community evidence independently places high-end Crit rolls around 7.5%; a direct current English-client Affix Preview maximum is still needed.',0],
    critdmg:['Crit DMG','≈ 11.25%',1,'Approximate Warlord/Lv162 standalone Crit DMG maximum from the first-post-160 normal-affix scaling step. A direct current English-client Affix Preview maximum is still needed.',0],
    block:['Block Rate','≈ 7.50%',1,'Approximate Warlord/Lv162 standalone Block Rate maximum from the first-post-160 normal-affix scaling step. A direct current English-client Affix Preview maximum is still needed.',0],
    acc:['Accuracy','≈ 7.50%',1,'Approximate Warlord/Lv162 standalone Accuracy maximum from the first-post-160 normal-affix scaling step. A direct current English-client Affix Preview maximum is still needed.',0],
    em:['Elemental Mastery','Lv162 scaling',1,'Elemental Mastery is a flat-number refinable affix whose inherited value scales with receiving gear level. I do not have a direct Global-English Warlord Affix Preview capture proving the maximum Lv162 roll.',1],
    ehr:['Effect Hit Rate','Lv162 scaling',1,'Effect Hit Rate is a flat-number refinable affix. I do not have a direct Global-English Warlord Affix Preview capture proving the maximum Lv162 roll.',1],
    dmgres:['DMG RES','No verified standalone max',1,'The current refinement pool clearly exposes the paired DMG RES + Healing Boost affix, but I could not establish a trustworthy standalone Warlord DMG RES refinement maximum.',0],
    heal:['Healing Boost','≈ 15.00%',1,'Approximate Warlord/Lv162 standalone Healing Boost maximum from the first-post-160 normal-affix scaling step. A direct current English-client Affix Preview maximum is still needed.',0],
    critpair:['Crit Rate + Crit DMG','15.3% + 23%',0,'',0],
    critacc:['Crit Rate + Accuracy','15.3% + 15.3%',1,'High-confidence post-160 special-affix maximum from the documented 3× special-affix breakpoint and older-server S2 affix table, but not retained as a direct current Global-English Affix Preview capture.',0],
    blockpair:['Block Rate + Block Efficiency','15.3% + 23%',1,'High-confidence post-160 special-affix maximum from the documented 3× special-affix breakpoint and older-server S2 affix table, but not retained as a direct current Global-English Affix Preview capture.',0],
    healpair:['DMG RES + Healing Boost','7.68% + 30.7%',1,'High-confidence post-160 special-affix maximum from the documented 3× special-affix breakpoint and older-server S2 affix table, but not retained as a direct current Global-English Affix Preview capture.',0],
  };
  const PROFILES={
    Conqueror:['crit','critdmg','critpair','acc','critacc','em','spd','spdpct','atk','atkpct'],
    Guardian:{
      tank:['block','blockpair','def','spd','hp','defpct','spdpct','hppct'],
      dps:['block','blockpair','crit','critdmg','spd','spdpct','atk','atkpct','em']
    },
    Destroyer:['crit','critdmg','critpair','atk','atkpct','em','acc','critacc','spd','spdpct'],
    Dominator:{
      dps:['ehr','crit','critdmg','critpair','em','atk','atkpct','spd','spdpct'],
      heals:['heal','healpair','spd','spdpct','hp','hppct','dmgres']
    }
  };
  const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const activeClass=()=>document.querySelector('#classTabs button.active')?.dataset.class||'Conqueror';
  const role=cls=>{try{if(cls==='Guardian')return localStorage.getItem('sxs-build-guardian-mode')==='dps'?'dps':'tank';return localStorage.getItem('sxs-build-dominator-mode')==='heals'?'heals':'dps'}catch(_){return cls==='Guardian'?'tank':'dps'}};
  const rowsFor=(cls,mode)=>{
    const profile=PROFILES[cls];
    const keys=Array.isArray(profile)?profile:profile?.[mode];
    return (keys||PROFILES.Conqueror).map(k=>R[k]);
  };
  const help=tip=>`<button type="button" class="rollHelp" aria-label="Approximate or unconfirmed value" data-tip="${esc(tip)}">?</button>`;
  const guideHtml=(cls,mode)=>{
    const rows=rowsFor(cls,mode);
    const label=cls==='Dominator'?`${cls} · ${mode==='heals'?'Heals':'DPS'}`:cls==='Guardian'?`${cls} · ${mode==='dps'?'DPS':'Tank'}`:cls;
    return `<details class="rollGuide" data-roll-sig="${esc(cls+'|'+mode)}"><summary><span>Roll guide</span><small>${esc(label)} · Warlord's Rest · Lv162</small></summary><div class="rollGuideBody"><div class="rollGuideNote">Only substats recommended above are shown. <b>?</b> = approximate, derived, or not directly confirmed on the current Global client.</div><div class="rollGuideGrid">${rows.map(([name,val,approx,tip,scaling])=>`<div class="rollGuideRow"><span class="rollGuideName">${esc(name)}${approx?help(tip):''}</span><span class="rollGuideValue${scaling?' rollScaling':''}">${esc(val)}</span></div>`).join('')}</div><div class="rollGuideSources">Warlord's Rest / Lv162 reference. Double-Crit is directly documented; other paired values marked <b>?</b> use the documented post-160 special-affix breakpoint. Normal single-stat caps marked <b>?</b> are first-post-160 estimates; flat-number stats scale with gear level.</div></div></details>`;
  };
  let queued=false;
  function apply(){
    queued=false;
    const cls=activeClass(),mode=(cls==='Dominator'||cls==='Guardian')?role(cls):'dps',sig=cls+'|'+mode;
    document.querySelectorAll('#buildContent .buildQuickStats').forEach(quick=>{
      const existing=quick.querySelector(':scope > .rollGuide');
      if(existing?.dataset.rollSig===sig) return;
      const html=guideHtml(cls,mode);
      if(existing) existing.outerHTML=html;
      else quick.querySelector(':scope > .quickSubstats')?.insertAdjacentHTML('afterend',html);
    });
  }
  // BUILD_VISUAL_STABILITY_V2: Roll Guide is part of the finished class layout,
  // so make it available to the synchronous Builds render pipeline.
  window.__applyBuildRollNow=apply;
  function queue(){if(queued)return;queued=true;requestAnimationFrame(()=>setTimeout(apply,0))}
  document.addEventListener('DOMContentLoaded',()=>{
    const host=document.getElementById('buildContent');
    if(host) new MutationObserver(queue).observe(host,{subtree:true,childList:true});
    document.getElementById('classTabs')?.addEventListener('click',queue);
    host?.addEventListener('click',e=>{if(e.target.closest?.('[data-dominator-mode],[data-guardian-mode]'))setTimeout(queue,0)});
    queue();
  });
  window.addEventListener('load',queue);
})();
