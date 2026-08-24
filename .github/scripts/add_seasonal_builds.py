from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

# Make the Builds heading season-aware.
old_heading='''<div class="sectionHeading"><div><span>Tier IV build guide</span><h2>Builds</h2></div><p>Class tabs, loadouts and gear priorities are kept separate from the server timeline.</p></div>'''
new_heading='''<div class="sectionHeading"><div><span id="buildSeasonLabel">Season build guide</span><h2>Builds</h2></div><p id="buildSeasonNote">Builds automatically follow the active Charming Glance season.</p></div>'''
if old_heading in s:
    s=s.replace(old_heading,new_heading,1)
elif new_heading not in s:
    raise SystemExit('Build section heading anchor changed')

# Replace the fixed T4 class state with season-aware state. Preserve the old S2 saved tab as a migration fallback.
old_state='''  // Tier IV build library researched Aug 21, 2026 from current Prydwen guides,
  // cross-checked with Loot & Waifus and community references where useful.
  const classes=['Conqueror','Guardian','Destroyer','Dominator'];
  const BUILD_CLASS_STORAGE_KEY='sxs-build-class';
  let currentClass='Conqueror';
  try{
    const savedClass=localStorage.getItem(BUILD_CLASS_STORAGE_KEY);
    if(classes.includes(savedClass)) currentClass=savedClass;
  }catch(_){}
  function buildHtml(cls){'''
new_state='''  // Build library follows the live Charming Glance season boundary at the 6:00 AM Pacific reset.
  // S1 uses the current Tier III classes; S2 switches automatically to the existing Tier IV library.
  const S1_BUILD_CLASSES=['Berserker','Paladin','Archmage','Arcanist'];
  const S2_BUILD_CLASSES=['Conqueror','Guardian','Destroyer','Dominator'];
  const BUILD_CLASS_STORAGE_KEYS={s1:'sxs-build-class-s1',s2:'sxs-build-class-s2'};
  function buildSeasonKey(){ return currentResetIso()<'2026-08-30'?'s1':'s2'; }
  function buildClassesForSeason(key=buildSeasonKey()){ return key==='s1'?S1_BUILD_CLASSES:S2_BUILD_CLASSES; }
  let currentBuildSeason=buildSeasonKey();
  let currentClass=currentBuildSeason==='s1'?'Berserker':'Conqueror';
  try{
    const classes=buildClassesForSeason(currentBuildSeason);
    const savedClass=localStorage.getItem(BUILD_CLASS_STORAGE_KEYS[currentBuildSeason]) || (currentBuildSeason==='s2'?localStorage.getItem('sxs-build-class'):null);
    if(classes.includes(savedClass)) currentClass=savedClass;
  }catch(_){}
  function buildHtmlS2(cls){'''
if old_state in s:
    s=s.replace(old_state,new_state,1)
elif 'function buildHtmlS2(cls)' not in s:
    raise SystemExit('Build state anchor changed')

# Tier III / Season 1 build library. Concise site-native summaries based on current Prydwen T3 guides.
s1_func=r'''
  function buildHtmlS1(cls){
    if(cls==='Berserker') return `
      <div class="guideSummary"><div><span>Season 1 · Tier III</span><strong>Berserker</strong><p>Physical multi-hit DPS. Blade of Judgment is the core T3 engine: stack marks quickly with multi-hit techniques and burst them repeatedly.</p></div><p><b>Quick stat rule</b>Physical Mastery &gt; ATK &gt; SPD on offensive main lines. Crit Rate and Crit DMG are premium substats; Elemental Mastery is not a T3 priority.</p></div>
      <div class="gearPanel"><div class="gearIntro"><span>Season 1 gearing</span><strong>Gear & stat priorities</strong><p>Stay Physical through the end of S1. Do not pre-convert your whole setup to the T4 Elemental plan before the season actually changes.</p></div><div class="gearGrid"><div class="gearItem"><span>Main lines</span><p>Sword / Gauntlets / Boots: Physical Mastery &gt; ATK &gt; SPD. Helmet / Chest: DEF ≥ Physical RES = Elemental RES &gt; HP.</p></div><div class="gearItem"><span>Best substats</span><p>Crit Rate% → Crit DMG% → Technique DMG vs debuffed targets → Physical Mastery / Accuracy → SPD.</p></div><div class="gearItem"><span>Fantomon</span><p>Nyxarchon is the strongest all-content lead when available. Sylvaerie and Zeioletus are strong damage alternatives; Aegiswing is more PvP/safety focused.</p></div><div class="gearItem"><span>S2 transition</span><p>Physical gear remains correct for Berserker today. Conqueror changes the damage plan in S2, so save exceptional S2-ready affixes without weakening your current S1 build.</p></div></div></div>
      <div class="priorityPanel"><div class="priorityIntro"><span>Core investment</span><strong>Blade of Judgment first</strong><p>Prioritize pieces that are actually used in the standard T3 loadouts below.</p></div><ol class="priorityList"><li><b>1</b><div><strong>Blade of Judgment</strong><p>The defining T3 charm and the reason multi-hit techniques outperform many larger single hits.</p></div></li><li><b>2</b><div><strong>Eclipse Slash</strong><p>Six-hit single-target nuke that feeds Blade of Judgment extremely well.</p></div></li><li><b>3</b><div><strong>Insightful Eye</strong><p>Reliable Crit support across PvE, Dragon and PvP.</p></div></li><li><b>4</b><div><strong>Indomitable Will / damage slot</strong><p>Keep Indomitable for safety; greed the slot only when survival is already solved.</p></div></li></ol></div>
      <div class="buildGrid">
        <article class="buildCard"><header><div><h3>Generic PvE</h3><p>Default S1 farming / dungeon setup</p></div></header><div class="skillGroup"><span>Techniques</span><div><b>Hunter's Judgment</b><b>Sunset Sword</b><b>Eclipse Slash</b><b>Lion Combo</b></div></div><div class="skillGroup"><span>Charms</span><div><b>Insightful Eye</b><b>Blade of Judgment</b><b>Blade Siphon</b><b>Indomitable Will</b></div></div><ul><li><b>Offensive:</b> Indomitable Will → Blazing Clash / another damage charm when safe</li><li><b>Defensive:</b> keep Indomitable Will; low Crit can use Blade of Lament instead of Blade Siphon</li></ul></article>
        <article class="buildCard"><header><div><h3>Dragon / Boss</h3><p>Single-target damage</p></div></header><div class="skillGroup"><span>Techniques</span><div><b>Flame Aura</b><b>Sunset Sword</b><b>Eclipse Slash</b><b>Lion Combo</b></div></div><div class="skillGroup"><span>Charms</span><div><b>Insightful Eye</b><b>Blade of Judgment</b><b>Blazing Clash</b><b>Crit Mastery</b></div></div><ul><li><b>Offensive:</b> this is already the greedier damage version</li><li><b>Defensive:</b> Crit Mastery or Blazing Clash → Indomitable Will if the fight can kill you</li></ul></article>
        <article class="buildCard"><header><div><h3>PvP / Mobility</h3><p>Burst, reach and survival</p></div></header><div class="skillGroup"><span>Techniques</span><div><b>Darkness Descends</b><b>Lion Combo</b><b>Eclipse Slash</b><b>Sunset Sword</b></div></div><div class="skillGroup"><span>Charms</span><div><b>Insightful Eye</b><b>Blade of Judgment</b><b>Frame of Battles</b><b>Indomitable Will</b></div></div><ul><li><b>Offensive:</b> Indomitable Will → Blazing Clash for lower-risk fights</li><li><b>Defensive:</b> keep Indomitable Will; in team PvP Lion Combo → Hunter's Judgment for grouping</li></ul></article>
      </div><p class="buildSource">Season 1 Tier III · <a href="https://www.prydwen.gg/sword-x-staff/guides/build-guide-berserker" rel="noreferrer" target="_blank">Prydwen Berserker ↗</a></p>`;

    if(cls==='Paladin') return `
      <div class="guideSummary"><div><span>Season 1 · Tier III</span><strong>Paladin</strong><p>Tank/support with Block, shields, taunt and stronger Water options. Your first job in party content is still keeping the group alive.</p></div><p><b>Quick stat rule</b>Block Rate and DEF are premium. Sword/Boots value SPD; Shield and defensive slots prioritize DEF, HP and RES.</p></div>
      <div class="gearPanel"><div class="gearIntro"><span>Season 1 gearing</span><strong>Gear & stat priorities</strong><p>Build enough speed to establish taunt/buffs early, then stack Block/DEF so your counter and protection loop stays alive.</p></div><div class="gearGrid"><div class="gearItem"><span>Main lines</span><p>Sword: SPD &gt; ATK &gt; Physical Mastery. Shield: DEF &gt; HP &gt; RES. Boots: SPD &gt; ATK &gt; Elemental/Physical Mastery.</p></div><div class="gearItem"><span>Best substats</span><p>Block Rate% → DEF% → DEF / HP% / HP. Damage stats come after the tank loop is reliable.</p></div><div class="gearItem"><span>Dungeon role</span><p>Valor Surge + Heart of Challenge establish support/taunt; Desperate Protection adds party safety when damage is threatening.</p></div><div class="gearItem"><span>Damage option</span><p>Star Shattering Slash is your major T3 nuke. Water builds use Lunarwater Threads and Frostbite Blossom when survival allows it.</p></div></div></div>
      <div class="buildGrid">
        <article class="buildCard"><header><div><h3>Dungeon Tank</h3><p>Party-first defensive setup</p></div></header><div class="skillGroup"><span>Techniques</span><div><b>Valor Surge</b><b>Heart of Challenge</b><b>Luminous Shield</b><b>Desperate Protection</b></div></div><div class="skillGroup"><span>Charms</span><div><b>Iron Fortress</b><b>Block Mastery</b><b>Block Awareness</b><b>Stone Skin</b></div></div><ul><li><b>Offensive:</b> Luminous Shield → Lunarwater Threads when survival is easy</li><li><b>Defensive:</b> keep the listed setup; it is already the party-safety version</li></ul></article>
        <article class="buildCard"><header><div><h3>Generic PvE</h3><p>Solo progression / balanced damage</p></div></header><div class="skillGroup"><span>Techniques</span><div><b>Luminous Shield</b><b>Forceful Charge</b><b>Star Shattering Slash</b><b>Heart of Challenge</b></div></div><div class="skillGroup"><span>Charms</span><div><b>Rebound</b><b>Counter Blade</b><b>Block Mastery</b><b>Block Awareness</b></div></div><ul><li><b>Offensive:</b> Luminous Shield → Valor Surge once survival is solved</li><li><b>Defensive:</b> keep Luminous Shield or add Desperate Protection for harder stages</li></ul></article>
        <article class="buildCard"><header><div><h3>Water Paladin</h3><p>More aggressive elemental variant</p></div></header><div class="skillGroup"><span>Techniques</span><div><b>Guardian Ring</b><b>Lunarwater Threads</b><b>Frostbite Blossom</b><b>Heart of Challenge</b></div></div><div class="skillGroup"><span>Charms</span><div><b>Ripple Impact</b><b>Defensive Assault</b><b>Pursuit of Victory</b><b>Insightful Eye</b></div></div><ul><li><b>Offensive:</b> retain Insightful Eye for consistency</li><li><b>Defensive:</b> Insightful Eye → Potential Rebirth if survivability is the problem</li></ul></article>
      </div><p class="buildSource">Season 1 Tier III · <a href="https://www.prydwen.gg/sword-x-staff/guides/build-guide-paladin" rel="noreferrer" target="_blank">Prydwen Paladin ↗</a></p>`;

    if(cls==='Archmage') return `
      <div class="guideSummary"><div><span>Season 1 · Tier III</span><strong>Archmage</strong><p>Front-loaded multi-element DPS. Rapid Cast is the defining T3 charm because acting before enemies is often both your damage plan and your survival plan.</p></div><p><b>Quick stat rule</b>Elemental Mastery &gt; ATK &gt; Crit &gt; SPD on Staff/Codex; Crit Rate, Crit DMG and SPD are premium substats.</p></div>
      <div class="gearPanel"><div class="gearIntro"><span>Season 1 gearing</span><strong>Gear & stat priorities</strong><p>Stay Elemental and lean into fast burst. Light is especially valuable; Fire/Wind remain important parts of the T3 damage package.</p></div><div class="gearGrid"><div class="gearItem"><span>Main lines</span><p>Staff / Codex: Elemental Mastery &gt; ATK &gt; Crit &gt; SPD. Boots: Elemental Mastery &gt; ATK &gt; SPD. Defensive slots: DEF/RES &gt; HP.</p></div><div class="gearItem"><span>Core charms</span><p>Rapid Cast is extremely hard to replace. Radiant Sear is a premier damage trigger; Void Bubble and Mana Surge round out the standard set.</p></div><div class="gearItem"><span>Boss note</span><p>Divine Wrath shines on large single targets but is less reliable into scattered/small groups.</p></div><div class="gearItem"><span>Fantomon</span><p>Nyxarchon is the premium damage lead; Sylvaerie and Zeioletus are strong offensive alternatives.</p></div></div></div>
      <div class="buildGrid">
        <article class="buildCard"><header><div><h3>AoE / Dungeons</h3><p>Front-load the room</p></div></header><div class="skillGroup"><span>Techniques</span><div><b>Divine Wrath</b><b>Howling Hurricane</b><b>Meteoric Flames</b><b>Lightning Chain</b></div></div><div class="skillGroup"><span>Charms</span><div><b>Rapid Cast</b><b>Void Bubble</b><b>Mana Surge</b><b>Radiant Sear</b></div></div><ul><li><b>Offensive:</b> Mana Surge → Lightning Mystery / Elemental Harmony if it sims better for your account</li><li><b>Defensive:</b> Mana Surge → Repelling Wind when control/safety matters more</li></ul></article>
        <article class="buildCard"><header><div><h3>Single Target</h3><p>Boss-focused elemental burst</p></div></header><div class="skillGroup"><span>Techniques</span><div><b>Divine Wrath</b><b>Howling Hurricane</b><b>Meteoric Flames</b><b>Wind's Delight</b></div></div><div class="skillGroup"><span>Charms</span><div><b>Rapid Cast</b><b>Void Bubble</b><b>Mana Surge</b><b>Radiant Sear</b></div></div><ul><li><b>Offensive:</b> Divine Wrath can become Tempest Sphere on smaller targets to trigger Radiant Sear more consistently</li><li><b>Defensive:</b> Mana Surge → Repelling Wind if you need breathing room</li></ul></article>
      </div><p class="buildSource">Season 1 Tier III · <a href="https://www.prydwen.gg/sword-x-staff/guides/build-guide-archmage" rel="noreferrer" target="_blank">Prydwen Archmage ↗</a></p>`;

    if(cls==='Arcanist') return `
      <div class="guideSummary"><div><span>Season 1 · Tier III</span><strong>Arcanist</strong><p>Dark DoT DPS with a real healer/support branch. T3 shifts damage builds toward Effect Hit Rate so the DoT package lands reliably on bosses.</p></div><p><b>Quick stat rule</b>DPS: Effect Hit Rate ≥ Elemental Mastery ≥ ATK &gt; SPD. Healer: SPD first, then EHR/Elemental Mastery; defensive slots favor HP.</p></div>
      <div class="gearPanel"><div class="gearIntro"><span>Season 1 gearing</span><strong>Gear & stat priorities</strong><p>DoT and healer sets want different priorities. Do not flatten them into one compromise set if you routinely swap roles.</p></div><div class="gearGrid"><div class="gearItem"><span>DPS</span><p>Staff / Orb: EHR ≥ Elemental Mastery ≥ ATK &gt; SPD. Boots: Elemental Mastery &gt; ATK &gt; SPD. Crit remains valuable as a substat.</p></div><div class="gearItem"><span>Healer</span><p>Staff / Orb / Boots: SPD first. Helmet/Chest: HP first, then DEF/RES. Healing Boost% is the premium healer substat.</p></div><div class="gearItem"><span>DoT core</span><p>Shadow Vengeance, Night's Blessing, Shadow Erosion and Linked Misfortune form the standard damage charm package.</p></div><div class="gearItem"><span>Support core</span><p>Resurrection + Healing Mastery + Overhealing are the stable healer charms, leaving one flexible slot.</p></div></div></div>
      <div class="buildGrid">
        <article class="buildCard"><header><div><h3>Single Target DoT</h3><p>Boss / long-fight damage</p></div></header><div class="skillGroup"><span>Techniques</span><div><b>Mana Blast</b><b>Dark Bullet</b><b>Abyssal Hand</b><b>Shadow of Termination</b></div></div><div class="skillGroup"><span>Charms</span><div><b>Shadow Vengeance</b><b>Night's Blessing</b><b>Shadow Erosion</b><b>Linked Misfortune</b></div></div><ul><li><b>Offensive:</b> keep the full DoT package</li><li><b>Defensive:</b> flex the lowest-impact damage slot only when survival becomes the limiter</li></ul></article>
        <article class="buildCard"><header><div><h3>AoE DoT</h3><p>Multi-target clearing</p></div></header><div class="skillGroup"><span>Techniques</span><div><b>Mana Blast</b><b>Dark Bullet</b><b>Abyssal Hand</b><b>Shadow Impact</b></div></div><div class="skillGroup"><span>Charms</span><div><b>Shadow Vengeance</b><b>Night's Blessing</b><b>Shadow Erosion</b><b>Linked Misfortune</b></div></div><ul><li><b>Offensive:</b> standard full DoT package</li><li><b>Defensive:</b> swap a damage charm only if the stage requires extra sustain/control</li></ul></article>
        <article class="buildCard"><header><div><h3>Healing / Support</h3><p>Party sustain</p></div></header><div class="skillGroup"><span>Techniques</span><div><b>Void Blessing</b><b>Waterling Summon</b><b>Radiant Restoration</b><b>Frenzy Totem</b></div></div><div class="skillGroup"><span>Charms</span><div><b>Resurrection</b><b>Healing Mastery</b><b>Overhealing</b><b>Flex</b></div></div><ul><li><b>Offensive:</b> use the flex slot for party damage/utility when healing is comfortable</li><li><b>Defensive:</b> keep the three core healing charms and use the flex slot for additional safety</li></ul></article>
      </div><p class="buildSource">Season 1 Tier III · <a href="https://www.prydwen.gg/sword-x-staff/guides/build-guide-arcanist" rel="noreferrer" target="_blank">Prydwen Arcanist ↗</a></p>`;

    return '<div class="emptyBuild">No Season 1 build data is available for this class yet.</div>';
  }
'''.rstrip()
anchor='  function buildHtmlS2(cls){'
if 'function buildHtmlS1(cls)' not in s:
    if anchor not in s: raise SystemExit('Could not find S2 build function anchor')
    s=s.replace(anchor,s1_func+'\n  '+anchor,1)

# Replace fixed render/setup with season-aware rendering and separate remembered tabs.
old_render='''  function renderBuilds(){
    $('classTabs').innerHTML=classes.map(c=>`<button class="${c===currentClass?'active':''}" data-class="${c}">${c}</button>`).join('');
    $('buildContent').innerHTML=buildHtml(currentClass);
  }
  let buildsInitialized=false;
  function setupBuilds(){
    $('classTabs').addEventListener('click',e=>{
      const b=e.target.closest('button[data-class]');
      if(!b)return;
      currentClass=b.dataset.class;
      try{localStorage.setItem(BUILD_CLASS_STORAGE_KEY,currentClass);}catch(_){}
      renderBuilds();
    });
    renderBuilds();
    buildsInitialized=true;
  }'''
new_render='''  function buildHtml(cls){ return buildSeasonKey()==='s1'?buildHtmlS1(cls):buildHtmlS2(cls); }
  function syncBuildSeason(){
    const nextSeason=buildSeasonKey();
    const classes=buildClassesForSeason(nextSeason);
    if(nextSeason!==currentBuildSeason || !classes.includes(currentClass)){
      currentBuildSeason=nextSeason;
      let saved=null;
      try{ saved=localStorage.getItem(BUILD_CLASS_STORAGE_KEYS[nextSeason]) || (nextSeason==='s2'?localStorage.getItem('sxs-build-class'):null); }catch(_){}
      currentClass=classes.includes(saved)?saved:classes[0];
    }
    return classes;
  }
  function renderBuilds(){
    const classes=syncBuildSeason();
    const s1=currentBuildSeason==='s1';
    if($('buildSeasonLabel')) $('buildSeasonLabel').textContent=s1?'Season 1 · Tier III build guide':'Season 2 · Tier IV build guide';
    if($('buildSeasonNote')) $('buildSeasonNote').textContent=s1
      ? 'Showing the live Season 1 / Tier III meta. This section switches to Tier IV automatically at the Aug 30, 6:00 AM Pacific reset.'
      : 'Season 2 / Tier IV is live. Your selected class tab is remembered separately for each season.';
    $('classTabs').innerHTML=classes.map(c=>`<button class="${c===currentClass?'active':''}" data-class="${c}">${c}</button>`).join('');
    $('buildContent').innerHTML=buildHtml(currentClass);
  }
  let buildsInitialized=false;
  function setupBuilds(){
    $('classTabs').addEventListener('click',e=>{
      const b=e.target.closest('button[data-class]');
      if(!b)return;
      currentClass=b.dataset.class;
      try{localStorage.setItem(BUILD_CLASS_STORAGE_KEYS[currentBuildSeason],currentClass);}catch(_){}
      renderBuilds();
    });
    renderBuilds();
    buildsInitialized=true;
    setInterval(()=>{ if(buildsInitialized && buildSeasonKey()!==currentBuildSeason) renderBuilds(); },60_000);
  }'''
if old_render in s:
    s=s.replace(old_render,new_render,1)
elif 'function syncBuildSeason()' not in s:
    raise SystemExit('Build render/setup anchor changed')

p.write_text(s,encoding='utf-8')
