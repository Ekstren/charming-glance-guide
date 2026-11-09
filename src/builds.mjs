import {BUILD_STAT_PROFILES,FANTOMON_GUIDANCE,ROLL_PROFILES,ROLL_VALUES} from './build-guidance.mjs';

const $=id=>document.getElementById(id);
const LIVE_BUILD_CLASSES=['Magister','Prophet','Ravager','Templar'];
const PREVIOUS_CLASS={Magister:'Destroyer',Prophet:'Dominator',Ravager:'Conqueror',Templar:'Guardian'};
const PROMOTED_CLASS=Object.fromEntries(Object.entries(PREVIOUS_CLASS).map(([current,previous])=>[previous,current]));
const BUILD_CLASS_STORAGE_KEY='sxs-build-class-s3';
const MODE_STORAGE_KEYS={Templar:'sxs-build-guardian-mode',Prophet:'sxs-build-dominator-mode'};

const T4_SOURCE_BUILDS={
  Destroyer:{
    url:'https://www.prydwen.gg/sword-x-staff/guides/build-guide-destroyer',updated:'Sep 1, 2026',
    builds:[
      {name:'AOE Build',techniques:['Formation Breaker','Howling Hurricane','Meteoric Flames','Wind Blade Spiral'],charms:['Rapid Cast','Void Bubble','Cyclone Lament','Radiant Sear'],note:'Radiant Sear is core here; Cyclone Lament benefits from the two Wind Techniques. Keep Void Bubble unless you comfortably outgear the fight.'},
      {name:'ST Build',techniques:['Formation Breaker','Divine Wrath','Wind Blade Spiral','Thunder of Judgment'],charms:['Rapid Cast','Void Bubble','Mana Surge','Radiant Sear'],note:'For bosses under 3×3, the source suggests Meteoric Flames over Divine Wrath; Tempest Sphere can replace Wind Blade Spiral. Mana Surge can become Overload Protection for more safety.'},
      {name:'Fire AoE Build',techniques:['Formation Breaker','Fiery Star Trail','Fireball','Meteoric Flames'],charms:['Rapid Cast','Void Bubble','Explosive Spirit','Fiery Burst'],note:'Built around Fiery Burst: the Techniques support its triggers. Explosive Spirit supplies Crit for Fire casts; Mana Surge is the source-listed substitute if you do not have it.'},
      {name:'Elsa Build',techniques:['Flowing Doom','Water Assault','Frosty Nova','Ice Spike'],charms:['Rapid Cast','Void Bubble','Shattering Ice','Water to Ice'],note:'A moderate-pack Freeze option, weaker than Fire against hordes and limited against bosses until their white gauge breaks. The source suggests Aqua Vortex in the first slot instead of Ice Spike for more Freeze.'}
    ]
  },
  Dominator:{
    url:'https://www.prydwen.gg/sword-x-staff/guides/build-guide-dominator',updated:'Sep 1, 2026',
    builds:[
      {name:'Single Target',techniques:['Dark Bullet','Dark Starburst','Chaos Rune','Shadow of Termination'],charms:['Shadow Vengeance',"Night's Blessing",'Shadow Erosion','Linked Misfortune'],note:'Dark Starburst and Chaos Rune keep some damage independent of Erosion. With high Effect Hit Rate, the source suggests Mana Blast over Chaos Rune; Frenzy Totem + Soul Pact Resonance are rarity/stat-dependent alternatives.'},
      {name:'AoE',techniques:['Mana Blast','Dark Bullet','Abyssal Hand','Shadow Impact'],charms:['Shadow Vengeance',"Night's Blessing",'Shadow Erosion','Linked Misfortune'],note:'This retains Dominator’s existing AoE set; the source says T4 adds no new AoE Technique or Charm for this class.'},
      {name:'Healing Build',techniques:['Waterling Summon','Rejuvenating Rain','Radiant Restoration','Frenzy Totem'],charms:['Phantom Light','Healing Mastery','Overhealing','FLEX'],note:'Phantom Light is the healer core. Use Healing Touch instead of Frenzy Totem for more healing; choose the last Charm for your need: Shadow Vengeance for your survival, Resurrection for allies, or Mantra of Blessings when survival is covered.'}
    ]
  },
  Conqueror:{
    url:'https://www.prydwen.gg/sword-x-staff/guides/build-guide-conqueror',updated:'Sep 1, 2026',
    builds:[
      {name:'Generic Build for all Content',techniques:['Flash Fire','Flame Aura','Flickering Blade','Blade Storm'],charms:['Insightful Eye','Piercing Assault','Tactical Adaptation','Indomitable Will'],note:'Use Darkness Descends instead of Flame Aura when you need mobility or Dispel; the source calls it a better PvP option. Drop Insightful Eye only after reaching about 118% Crit Rate in PvE (enemies have 18% Crit RES), and keep Indomitable Will in PvP.'},
      {name:'Dragon Build',techniques:['Flame Aura','Blade Storm','Flash Fire','Flickering Blade'],charms:['Insightful Eye','Piercing Assault','Tactical Adaptation','Blazing Clash'],note:'At about 118% Crit Rate in PvE, the source suggests Crit Mastery over Insightful Eye. Only replace Blazing Clash with extra offense if survival is already safe.'}
    ]
  },
  Guardian:{
    url:'https://www.prydwen.gg/sword-x-staff/guides/build-guide-guardian',updated:'Sep 1, 2026',
    builds:[
      {name:'Generic Dungeon Grid',techniques:['Valor Surge','Heart of Challenge','Luminous Shield','Desperate Protection'],charms:['Iron Will','Holy Aegis','Block Awareness','Soul Protection'],note:'For more Taunt, replace Valor Surge with Hamper Strike. If the party still dies, Iron Fortress is an option (the source says it is mostly a PvP Charm); Desperate Protection can flex to Swirling Blade or Star Shattering Slash for damage.'},
      {name:'Water Paladin',techniques:['Swirling Blade','Lunarwater Threads','Seismic Tide','Raging Maelstrom'],charms:['Frigid Aura','Defensive Assault','Frigid Glint','Potential Rebirth'],note:'Primarily an AoE Water/Cold bar with decent single-target damage. The source lists Potential Rebirth, Blade of Lament, and Pursuit of Victory as goal-dependent Charm options.'},
      {name:'Support Knight',techniques:['Valor Surge','Leap Attack','Holy Purification','Lunarwater Threads'],charms:['Frigid Aura','Frigid Glint','Iron Fortress','Oath of Vigil'],note:'A support option for Dragon, Chaos, and Guild Bosses. If Dispel is unnecessary, drop Holy Purification; swap Lunarwater Threads for Seismic Tide for more consistent Cold stacking.'},
      {name:'Secondary PvE build',techniques:['Desperate Protection','Luminous Shield','Forceful Charge','Star Shattering Slash'],charms:['Rebound','Holy Aegis','Block Mastery','Block Awareness'],note:'The source presents this as a secondary PvE option alongside the more support-oriented dungeon build.'}
    ]
  }
};

const T5_SOURCE_BUILDS={
  "Magister": {
    "url": "https://www.prydwen.gg/sword-x-staff/guides/build-guide-magister",
    "updated": "Sep 1, 2026",
    "builds": [
      {
        "name": "Wind AOE Build",
        "techniques": [
          "Formation Breaker",
          "Wind Blade Spiral",
          "Storm Rhapsody",
          "Howling Hurricane"
        ],
        "charms": [
          "Radiant Warp",
          "Thunder Judgment",
          "Cyclone Lament",
          "Radiant Sear"
        ],
        "note": "Keep Formation Breaker against high-DEF enemies. If survival is limiting, replace Thunder Judgment with Overload Protection or Vital Rhythm."
      },
      {
        "name": "ST Build",
        "techniques": [
          "Formation Breaker",
          "Divine Wrath",
          "Twin Gale",
          "Thunder of Judgment"
        ],
        "charms": [
          "Radiant Warp",
          "Thunderbolt Mark",
          "Mana Surge",
          "Radiant Sear"
        ],
        "note": "The source suggests Meteoric Flames against stationary or Wind-resistant bosses. Fire Blast can replace Twin Gale when one rarity higher; Cyclone Lament is a Wind-heavy Charm alternative."
      },
      {
        "name": "Fire AoE Build",
        "techniques": [
          "Formation Breaker",
          "Fiery Star Trail",
          "Crimson Whirl",
          "Meteoric Flames"
        ],
        "charms": [
          "Radiant Warp",
          "Ember Flare",
          "Explosive Spirit",
          "Fiery Burst"
        ],
        "note": "With enough Crit from gear, the source lists Raging Wildfire over Explosive Spirit and Blast Spirit over Meteoric Flames. Keep defensive tools when pushing harder content."
      },
      {
        "name": "PVP Build",
        "techniques": [
          "Formation Breaker",
          "Wind Blade Spiral",
          "Twin Gale",
          "Thunder of Judgment"
        ],
        "charms": [
          "Radiant Warp",
          "Thunder Judgment",
          "Vital Rhythm",
          "Cyclone Lament"
        ],
        "note": "The published setup combines kiting and single-target pressure. Radiant Warp and Vital Rhythm provide survival; Pandarial supports its opening tempo and healing."
      }
    ]
  },
  "Prophet": {
    "url": "https://www.prydwen.gg/sword-x-staff/guides/build-guide-prophet",
    "updated": "Sep 4, 2026",
    "builds": [
      {
        "name": "Direct Single Target",
        "techniques": [
          "Thalasson Summon",
          "Desperate Shadow",
          "Hexed Blast",
          "Soul Reap"
        ],
        "charms": [
          "Shadowy Current",
          "Shadow Vengeance",
          "Mana Surge",
          "Soul Pact Resonance"
        ],
        "note": "Keep Soul Reap last. Frenzy Totem is the source’s sturdier summon alternative and PvP default. Ring of Omen can replace a survival or damage Charm when appropriate."
      },
      {
        "name": "Pure Erosion Remastered Edition",
        "techniques": [
          "Desperate Shadow",
          "Dark Starburst",
          "Hexed Blast",
          "Shadow of Termination"
        ],
        "charms": [
          "Ring of Omen",
          "Mana Surge",
          "Linked Misfortune",
          "Shadow Erosion"
        ],
        "note": "Published for longer fights such as Hieromon and Chaos Boss. Keep Ring of Omen, Linked Misfortune and Shadow Erosion; Mana Surge is the flexible Charm slot."
      },
      {
        "name": "Direct AoE",
        "techniques": [
          "Thalasson Summon",
          "Abyssal Hand",
          "Desperate Shadow",
          "Hexed Blast"
        ],
        "charms": [
          "Soul Pact Resonance",
          "Night's Blessing",
          "Shadowy Current",
          "Mana Surge"
        ],
        "note": "Use a different summon when its utility is needed. Shadow Vengeance can replace Night’s Blessing or Mana Surge if the damage setup cannot survive."
      },
      {
        "name": "Healing Build",
        "techniques": [
          "Rejuvenating Rain",
          "Radiant Rhythm",
          "Radiant Restoration",
          "Waterling Summon"
        ],
        "charms": [
          "Phantom Light",
          "Healing Mastery",
          "Overhealing",
          "FLEX"
        ],
        "note": "The last Charm is Shadow Vengeance for personal survival, Resurrection for allies, or Mantra of Blessings for offense. High-HP builds can put Void Blessing first."
      }
    ]
  },
  "Ravager": {
    "url": "https://www.prydwen.gg/sword-x-staff/guides/build-guide-ravager",
    "updated": "Sep 4, 2026",
    "builds": [
      {
        "name": "Stages and Dungeons Build",
        "techniques": [
          "Night Curse",
          "Solaris Storm",
          "Soul Piercer",
          "Flickering Blade"
        ],
        "charms": [
          "Piercing Assault",
          "Tactical Adaptation",
          "Blade of Lament",
          "Indomitable Will"
        ],
        "note": "If survival is comfortable, the source allows Soulfire Protection instead of Indomitable Will, or Insightful Eye when more Crit Rate is needed."
      },
      {
        "name": "Dragon Build",
        "techniques": [
          "Flame Aura",
          "Solaris Storm",
          "Eclipse Slash",
          "Flickering Blade"
        ],
        "charms": [
          "Piercing Assault",
          "Tactical Adaptation",
          "Blade of Judgment",
          "Insightful Eye"
        ],
        "note": "With enough Crit Rate elsewhere, use Crit Mastery instead of Insightful Eye. Compare Flame Aura with Sunset Sword by rarity; if using Sunset Sword, put it last."
      },
      {
        "name": "PVP Build",
        "techniques": [
          "Shattering Dance",
          "Sunset Sword",
          "Flickering Blade",
          "Blade Storm"
        ],
        "charms": [
          "Piercing Assault",
          "Tactical Adaptation",
          "Soulfire Protection",
          "Indomitable Will"
        ],
        "note": "This is the source’s PvP bar. Shattering Dance supplies anti-Block utility, while the defensive Charms support its damage window."
      }
    ]
  },
  "Templar": {
    "url": "https://www.prydwen.gg/sword-x-staff/guides/build-guide-templar",
    "updated": "Sep 10, 2026",
    "builds": [
      {
        "name": "Generic Dungeon/4vs4 Build",
        "techniques": [
          "Valor Surge",
          "Heart of Challenge",
          "Lunarwater Threads",
          "Hamper Strike"
        ],
        "charms": [
          "Iron Will",
          "Block Mastery",
          "Block Awareness",
          "Soul Protection"
        ],
        "note": "The published bar assumes Pandarial. With sufficient Block versus enemy Accuracy, Block Awareness can become Rebound for damage or Oath of Vigil for protection."
      },
      {
        "name": "Water Templar",
        "techniques": [
          "Swirling Blade",
          "Lunarwater Threads",
          "Seismic Tide",
          "Raging Maelstrom"
        ],
        "charms": [
          "Frigid Aura",
          "Defensive Assault",
          "Frigid Glint",
          "Sacred Rhythm"
        ],
        "note": "The source highlights Chaos Invasion and solo content. Frostbite Blossom is its Chaos swap for Lunarwater Threads; Blade of Lament or Pursuit of Victory are AoE Charm options."
      },
      {
        "name": "PvP Templar",
        "techniques": [
          "Valor Surge",
          "Swirling Blade",
          "Star Shattering Slash",
          "Iron Slashes"
        ],
        "charms": [
          "Defensive Assault",
          "Block Mastery",
          "Block Awareness",
          "Soul Protection"
        ],
        "note": "With enough Crit, Boiling Bloodlust can replace Valor Surge. Light Sword Array is the source’s alternative to a weak Iron Slashes; check Block against the enemy’s Accuracy."
      },
      {
        "name": "Light Templar",
        "techniques": [
          "Light Sword Array",
          "Phantom Blade",
          "Dawnburst",
          "Sacred Shine"
        ],
        "charms": [
          "Soul Protection",
          "Defensive Assault",
          "Holy Restoration",
          "Healing Shift"
        ],
        "note": "An AoE option with less sustain than Water. The source suggests Hamper Strike plus Iron Will when Taunt and damage reduction are more useful."
      }
    ]
  }
};

const SECONDARY_SOURCE_DATA={
  Destroyer:{
    community:{name:'Community-posted Wind 4v4',author:'Reddit · player build',url:'https://www.reddit.com/r/SwordxStaff_Official/comments/1w7mldt/looking_for_t4_destroyer_tournament_build/',builds:[
      {name:'Wind Tournament Build',techniques:['Formation Breaker','Wind Blade Spiral','Howling Hurricane',"Wind's Delight"],charms:['Rapid Cast','Radiant Sear',"Wind's Shadow",'Cyclone Lament'],note:'The poster says to put Formation Breaker first and Wind’s Delight last for distance. Repelling Wind is called a strong Arena-vs-Swords option, but less useful in team 4v4.'}
    ],note:'The same discussion offers a mixed-AoE alternative when Wind affinity is low: Meteoric Flames + Divine Wrath, with Lightning Mystery + Mana Surge. It recommends testing both in the game’s skill test.'},
    reference:{name:'Kanstein Codex · Destroyer T4 notes',url:'https://swordxstaff.online/guides/destroyer-build/',note:'Independent class notes on stat and survivability direction; the page says it does not publish an exact T4 skill kit.'}
  },
  Conqueror:{
    community:{name:'Community PvP swaps',author:'Reddit · player discussion',url:'https://www.reddit.com/r/SwordxStaff_Official/comments/1vlpw7j/t4_conqueror_build_help/',note:'One player reports Flash Fire → Soul Piercer for sustain, Darkness Descends when Dispel is needed, and assigning Gale Dance to the higher-quality copy when two Conquerors are on the team. This is a set of reported swaps, not a complete published bar.'},
    reference:{name:'Kanstein Codex · Conqueror T4 notes',url:'https://swordxstaff.online/guides/conqueror-build/',note:'Independent class notes cover the inherited build direction but explicitly do not publish a complete T4 skill kit.'}
  },
  Dominator:{
    community:{name:'Community 1v1 discussion',author:'Reddit · player discussion',url:'https://www.reddit.com/r/SwordxStaff_Official/comments/1w4z966/destroyer_vs_dominator/',note:'The reply describes a partial Dark PvP setup and says Waterling versus Rock Rex depends on needing Dispel or peel. Its skill and Charm names are incomplete, so it is not shown as a complete loadout.'},
    reference:{name:'Kanstein Codex · Dominator T4 notes',url:'https://swordxstaff.online/guides/arcanist-dominator-build/',note:'Independent class notes discuss role and stat direction; the page does not publish a complete T4 skill bar.'}
  },
  Guardian:{
    reference:{name:'Kanstein Codex · Guardian class notes',url:'https://swordxstaff.online/guides/paladin-guardian-build/',note:'Independent tank and stat notes; the page says Guardian’s exact T4 skill kit is not published there.'}
  }
};

let currentClass='Ravager';
try{
  const saved=localStorage.getItem(BUILD_CLASS_STORAGE_KEY)||localStorage.getItem('sxs-build-class-s2')||localStorage.getItem('sxs-build-class');
  const promoted=PROMOTED_CLASS[saved]||saved;
  if(LIVE_BUILD_CLASSES.includes(promoted)) currentClass=promoted;
}catch(_){}

const escapeHtml=value=>String(value).replace(/[&<>"']/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
const modeFor=cls=>{
  const allowed=cls==='Templar'?['tank','dps']:cls==='Prophet'?['dps','heals']:[];
  try{
    const saved=localStorage.getItem(MODE_STORAGE_KEYS[cls]);
    return allowed.includes(saved)?saved:(cls==='Templar'?'tank':'dps');
  }catch(_){return cls==='Templar'?'tank':'dps';}
};

function renderBuildGroup(label,items){
  return '<div class="skillGroup"><span>'+escapeHtml(label)+'</span><div>'+items.map(item=>'<b>'+escapeHtml(item)+'</b>').join('')+'</div></div>';
}

function renderCard(build,sourceClass){
  return '<article class="buildCard '+sourceClass+'">'
    +'<header><div><h3>'+escapeHtml(build.name)+'</h3></div></header>'
    +renderBuildGroup('Techniques',build.techniques)
    +renderBuildGroup('Charms',build.charms)
    +(build.note?'<p class="buildCaveat"><strong>Technique / Charm caveat</strong>'+escapeHtml(build.note)+'</p>':'')
    +'</article>';
}

function renderModeTabs(cls,mode){
  if(!MODE_STORAGE_KEYS[cls]) return '';
  const options=cls==='Templar'?[['tank','Tank'],['dps','DPS']]:[['dps','DPS'],['heals','Heals']];
  return '<div class="buildGuideModeTabs" role="group" aria-label="Gear profile">'+options.map(([key,label])=>'<button type="button" data-build-mode="'+key+'" class="'+(key===mode?'active':'')+'" aria-pressed="'+(key===mode)+'">'+label+'</button>').join('')+'</div>';
}

function renderRollGuide(cls,mode){
  const profile=ROLL_PROFILES[cls];
  const keys=Array.isArray(profile)?profile:profile?.[mode];
  const rows=(keys||ROLL_PROFILES.Ravager).map(key=>ROLL_VALUES[key]);
  const label=cls==='Prophet'?cls+' · '+(mode==='heals'?'Heals':'DPS'):cls==='Templar'?cls+' · '+(mode==='dps'?'DPS':'Tank'):cls;
  return '<details class="rollGuide" data-roll-sig="'+escapeHtml(cls+'|'+mode)+'">'
    +'<summary><span>Roll guide</span><small>'+escapeHtml(label)+' · Recorded baseline</small></summary>'
    +'<div class="rollGuideBody"><div class="rollGuideNote">Recorded Affix Preview maxima. Season 3 special-affix values are not inferred here.</div>'
    +'<div class="rollGuideGrid">'+rows.map(([name,value])=>'<div class="rollGuideRow"><span class="rollGuideName">'+escapeHtml(name)+'</span><span class="rollGuideValue">'+escapeHtml(value)+'</span></div>').join('')+'</div>'
    +'<div class="rollGuideSources">Values confirmed in the in-game Affix Preview. Paired values follow the listed stat order.</div></div>'
    +'</details>';
}

function renderGearPanel(cls,mode){
  const all=BUILD_STAT_PROFILES[cls];
  const profile=all?.[mode]||all;
  return '<section class="buildInfoPanel gearAdvicePanel">'
    +'<div class="buildInfoHeader"><h3>Gear &amp; stat priorities</h3>'+renderModeTabs(cls,mode)+'</div>'
    +'<p class="gearStatRule">'+escapeHtml(profile.rule)+'</p>'
    +'<div class="quickGearGrid">'+profile.rows.map(([slot,stats])=>'<div class="quickGearRow"><b>'+escapeHtml(slot)+'</b><span>'+escapeHtml(stats)+'</span></div>').join('')+'</div>'
    +'<div class="quickSubstats"><b>Substats</b><span>'+escapeHtml(profile.substats)+'</span></div>'
    +renderRollGuide(cls,mode)
    +'<p class="buildPanelSource">Related T5 class guide: <a href="'+T5_SOURCE_BUILDS[cls].url+'" rel="noreferrer" target="_blank">Prydwen · '+escapeHtml(cls)+' ↗</a></p>'
    +'</section>';
}

function renderFantomonPanel(cls){
  const picks=FANTOMON_GUIDANCE[cls];
  return '<section class="buildInfoPanel fantomonAdvicePanel">'
    +'<div class="buildInfoHeader"><h3>Fantomon suggestions</h3><span class="buildInfoKicker">Lead Fantomon options</span></div>'
    +'<p class="fantomonRule">Only the lead Fantomon uses its ability; the others contribute passive stats.</p>'
    +'<div class="fantomonSuggestionList">'+picks.map(([label,name,why])=>'<div class="fantomonSuggestion"><span>'+escapeHtml(label)+'</span><strong>'+escapeHtml(name)+'</strong><p>'+escapeHtml(why)+'</p></div>').join('')+'</div>'
    +'<p class="buildPanelSource">Class recommendations: <a href="'+T5_SOURCE_BUILDS[cls].url+'" rel="noreferrer" target="_blank">Prydwen ↗</a> · <a href="https://swordxstaff.online/guides/fantomon-guide/" rel="noreferrer" target="_blank">independent Fantomon guide ↗</a></p>'
    +'</section>';
}

function renderSecondarySources(cls){
  const data=SECONDARY_SOURCE_DATA[cls];
  let html='';
  if(data.community?.builds?.length){
    html+='<section class="otherBuildSource"><div class="otherBuildSourceHeader"><h3>Community-posted build</h3><span>'+escapeHtml(data.community.author)+'</span></div>'
    +'<div class="buildGrid communityBuildGrid">'+data.community.builds.map(build=>renderCard(build,'communityBuildCard')).join('')+'</div>'
      +(data.community.note?'<p class="otherSourceCaveat">'+escapeHtml(data.community.note)+'</p>':'')
      +'<p class="buildSource">Source: <a class="buildSourceLink" href="'+data.community.url+'" rel="noreferrer" target="_blank">Open community post ↗</a></p></section>';
  }
  const notes=[data.community?.note&&!data.community?.builds?.length?{title:data.community.name,text:data.community.note,url:data.community.url,author:data.community.author}:null,data.reference?{title:data.reference.name,text:data.reference.note,url:data.reference.url,author:'Independent community guide'}:null].filter(Boolean);
  if(notes.length){
    html+='<details class="otherSourceNotes"><summary><span>More source notes</span><small>Community reports and independent class guides</small></summary>'
      +'<div class="otherSourceNoteGrid">'+notes.map(note=>'<article class="otherSourceNote"><h4>'+escapeHtml(note.title)+'</h4><span>'+escapeHtml(note.author)+'</span><p>'+escapeHtml(note.text)+'</p><a href="'+note.url+'" rel="noreferrer" target="_blank">Open source ↗</a></article>').join('')+'</div>'
      +'</details>';
  }
  return html;
}

const T5_PLAYER_SOURCES={
  Magister:'Crucible: Max Dps by Rezaj · Split Mirage: Takin’ out the Trash (Mobs) by Darkstorm.',
  Prophet:'Dungeon DPS by Rezaj · Arena, AOE Mob clear, Exploring and Boss fight by JustinPantheon · Support by Torrent · Heal Overload by Keshi.',
  Ravager:'Map build by SchlorKor.',
  Templar:'Dungeon: Double Taunt Dungeon Panda by Rezaj and Generic Dungeon by Useless · Split Mirage: Split Endless by Torrent · Arena: Balanced Offense and Reflect by Torrent.'
};
function renderPlayerSources(cls){
  const directory='https://www.sxscompanion.com/builds/t5/'+cls.toLowerCase();
  return '<details class="otherSourceNotes"><summary><span>More Season 3 player builds</span><small>Published activity-specific alternatives</small></summary>'
    +'<div class="otherSourceNoteGrid"><article class="otherSourceNote"><h4>SxS Companion · '+escapeHtml(cls)+'</h4><p>'+escapeHtml(T5_PLAYER_SOURCES[cls])+'</p><a href="'+directory+'" rel="noreferrer" target="_blank">Open creator loadouts ↗</a></article>'
    +'<article class="otherSourceNote"><h4>Purrwikimania · Community loadouts</h4><p>Choose Tier 5 and your class to browse player-posted Techniques, Charms and their authors’ notes.</p><a href="https://www.purrwikimania.com/loadouts" rel="noreferrer" target="_blank">Browse player loadouts ↗</a></article></div></details>';
}
function buildHtml(cls){
  const source=T5_SOURCE_BUILDS[cls];
  if(!source)return '';
  const mode=modeFor(cls),previous=PREVIOUS_CLASS[cls],legacy=T4_SOURCE_BUILDS[previous];
  const cards=source.builds.map(build=>renderCard(build,'sourceBuildCard')).join('');
  return '<div class="sourceBuildCollection">'
    +'<p class="sourceBuildNote">Season 3 · Current T5 loadouts from published guides, shown under their original names. Technique and Charm caveats stay with each preset.</p>'
    +'<section class="publishedBuildSource"><div class="otherBuildSourceHeader"><h3>Published T5 builds</h3><span>Guide updated '+escapeHtml(source.updated)+'</span></div>'
    +'<div class="buildGrid sourceBuildGrid">'+cards+'</div>'
    +'<p class="buildSource">Source: <a class="buildSourceLink" href="'+source.url+'" rel="noreferrer" target="_blank">Prydwen · '+escapeHtml(cls)+' T5 build guide ↗</a> · checked Nov 8, 2026.</p>'
    +'</section>'+renderPlayerSources(cls)
    +'<div class="buildGuideGrid">'+renderGearPanel(cls,mode)+renderFantomonPanel(cls)+'</div>'
    +'<details class="otherSourceNotes legacyBuildArchive"><summary><span>Season 2 · '+escapeHtml(previous)+' reference builds</span><small>Previous-tier archive</small></summary>'
    +'<p class="otherSourceCaveat">Historical T4 loadouts and player notes are retained here; they are not Season 3 recommendations.</p>'
    +'<div class="buildGrid">'+legacy.builds.map(build=>renderCard(build,'legacyBuildCard')).join('')+'</div>'
    +'<p class="buildSource">Source: <a href="'+legacy.url+'" rel="noreferrer" target="_blank">Prydwen · '+escapeHtml(previous)+' T4 guide ↗</a></p>'
    +renderSecondarySources(previous)+'</details></div>';
}

function renderClassTabs(){
  const tabs=$('classTabs');
  tabs.innerHTML=LIVE_BUILD_CLASSES.map(cls=>'<button type="button" role="tab" aria-selected="'+(cls===currentClass)+'" class="'+(cls===currentClass?'active':'')+'" data-class="'+cls+'">'+cls+'</button>').join('');
}

function renderBuilds(){
  renderClassTabs();
  $('buildContent').innerHTML=buildHtml(currentClass);
}

function setupBuilds(){
  $('classTabs').addEventListener('click',event=>{
    const button=event.target.closest('button[data-class]');
    if(!button||button.dataset.class===currentClass)return;
    currentClass=button.dataset.class;
    try{localStorage.setItem(BUILD_CLASS_STORAGE_KEY,currentClass);}catch(_){}
    renderBuilds();
  });
  $('buildContent').addEventListener('click',event=>{
    const button=event.target.closest('button[data-build-mode]');
    if(!button||!MODE_STORAGE_KEYS[currentClass]) return;
    try{localStorage.setItem(MODE_STORAGE_KEYS[currentClass],button.dataset.buildMode);}catch(_){}
    renderBuilds();
  });
  renderBuilds();
}

let initialized=false;
export function initialize(){
  if(initialized)return;
  initialized=true;
  setupBuilds();
}
