from pathlib import Path
import re

INDEX = Path('index.html')
INJECT = Path('.github/build-fantomons-inject.html')
RESTORE = Path('scripts/patch_restore_rich_builds_v1.py')
MARK = 'META_BUILD_MODES_V1'
START = '<!-- BUILD_FANTOMON_PAIRS_START -->'
END = '<!-- BUILD_FANTOMON_PAIRS_END -->'

# Current Global S2 synthesis (Sep 3, 2026):
# - Prydwen T4 guides (Conqueror Jul 6; Guardian/Destroyer/Dominator Sep 1)
# - Loot & Waifus Sage/Dominator testing
# - AllClash T4 class guides
# - Recent r/SwordxStaff_Official Global PvP / S2 testing through Sep 3
# The goal is activity-specific META bars, not a dump of every viable build.

T4_BLOCKS = {
'Conqueror': r'''    Conqueror:[
      role('Dungeon','Fast-clear S2 dungeon meta',['Flash Fire','Flame Aura','Flickering Blade','Blade Storm'],['Piercing Assault','Tactical Adaptation','Soul Splash','Insightful Eye'],'High Crit: Insightful Eye → Soul Breaker. If a room is too dangerous, Soul Splash → Indomitable Will. Darkness Descends can replace Flame Aura when Dispel or extra movement matters.','Nyxarchon is the damage default; use Aegiswing only when dying is the real limiter.','Current Global meta'),
      role('Crucible / Conquest','Single-target score / raid-boss meta',['Flame Aura','Blade Storm','Flash Fire','Flickering Blade'],['Piercing Assault','Tactical Adaptation','Blazing Clash','Insightful Eye'],'At high enough Crit, Insightful Eye → Crit Mastery. This is the greedier Dragon-style score bar: no Indomitable unless survival is actually costing attempts.','Keep the four-Technique rotation intact; rank/ascension can matter more than tiny theoretical swaps.','Prydwen score core'),
      role('Arena','Solo PvP / anti-Guardian pressure',['Darkness Descends','Doom Blade','Flickering Blade','Blade Storm'],['Piercing Assault','Tactical Adaptation','Soul Breaker','Indomitable Will'],'Darkness Descends is the key Dispel/mobility slot. If you need sustain more than Doom Blade pressure, Doom Blade → Soul Piercer. Low Crit: Soul Breaker → Insightful Eye.','Accuracy is premium into high-Block Guardians. Keep Indomitable Will even when you outpower the target.','Current PvP synthesis'),
      role('Tournament · 2v2','Duo PvP: sustain + kill pressure',['Darkness Descends','Soul Piercer','Flickering Blade','Blade Storm'],['Piercing Assault','Tactical Adaptation','Soul Breaker','Indomitable Will'],'Soul Piercer gives the duo bar more self-sustain while Darkness keeps Dispel. Low Crit: Soul Breaker → Insightful Eye. If your partner already supplies enough control, Soul Piercer can flex back to Doom Blade for harder burst.','Do not greed away Indomitable in 2v2; one death is half the team.','Current Global PvP'),
      role('Tournament · 4v4','Team PvP: reach, Dispel and coordinated tempo',['Flash Fire','Darkness Descends','Flickering Blade','Blade Storm'],['Insightful Eye','Piercing Assault','Tactical Adaptation','Indomitable Will'],'High Crit: Insightful Eye → Soul Breaker. With two Conquerors, the higher-rank Gale Dance user can flex it in for the team SPD boost while the other keeps the full damage bar.','Flash Fire keeps reach in a spread-out fight; Darkness is retained for buff removal. Indomitable stays mandatory under focus fire.','Current Global PvP')
    ]''',
'Guardian': r'''    Guardian:[
      role('Dungeon · Tank','Primary S2 party-tank meta',['Valor Surge','Heart of Challenge','Luminous Shield','Desperate Protection'],['Iron Will','Holy Aegis','Block Awareness','Soul Protection'],'Need more Taunt: Valor Surge → Hamper Strike. If the group is already safe, Desperate Protection → Swirling Blade or Star Shattering Slash for faster clears.','If the team still dies, Iron Fortress is the first extra defensive flex. Aegiswing is the default lead.','Prydwen dungeon core'),
      role('Crucible / Conquest · Tank','Carry-support / boss-score meta',['Valor Surge','Leap Attack','Holy Purification','Lunarwater Threads'],['Frigid Aura','Frigid Glint','Iron Fortress','Oath of Vigil'],'This bar exists to make the strongest carry better. If there is no buff worth dispelling, Holy Purification → damage. Lunarwater Threads → Seismic Tide for steadier Cold stacking.','Kels is the default boss-support Fantomon when Dispel/DEF Down matters; Nyxarchon is the greedier damage-amplification option.','Prydwen support core'),
      role('Arena · Tank','Solo block / reflect wall',['Luminous Shield','Forceful Charge','Star Shattering Slash','Desperate Protection'],['Rebound','Holy Aegis','Block Mastery','Soul Protection'],'If your natural Block is not high enough, Soul Protection → Block Awareness. The goal is to survive the opening burst and punish repeated hits rather than imitate a DPS class.','Aegiswing is the safest Arena lead. Against weak pressure, one defensive slot can flex to offense.','Meta reflect synthesis'),
      role('Tournament · 2v2 · Tank','Duo frontline: protect one carry and still threaten',['Hamper Strike','Heart of Challenge','Luminous Shield','Desperate Protection'],['Iron Will','Rebound','Iron Fortress','Oath of Vigil'],'Oath of Vigil is much stronger here than in Arena because there is exactly one partner to protect. Rebound gives the smaller fight real punishment while Hamper Strike + Heart control targeting.','If focus fire is overwhelming, Rebound → Soul Protection. If your partner is the tankier unit, Holy Aegis is a valid self-survival flex.','Team-PvP synthesis'),
      role('Tournament · 4v4 · Tank','Full-team tank: Taunt + ally protection',['Hamper Strike','Heart of Challenge','Luminous Shield','Desperate Protection'],['Iron Will','Soul Protection','Iron Fortress','Oath of Vigil'],'This is the maximum team-protection shell: reliable Taunt, opening effective HP, group mitigation and Oath protection on the ally most likely to be bursted.','Do not swap into the Water damage bar unless your team already has another real frontline.','Prydwen + Global PvP'),
      role('Dungeon · DPS','Water AoE / fast-clear bruiser',['Swirling Blade','Lunarwater Threads','Seismic Tide','Raging Maelstrom'],['Frigid Aura','Defensive Assault','Frigid Glint','Potential Rebirth'],'This is the published offensive Water Guardian shell: fast Cold stacking, strong AoE and enough single-target damage to stay useful on elites. If you completely outgear the room, Potential Rebirth → Pursuit of Victory or another damage charm.','Keep enough Block/DEF to stay active. DPS Guardian is a bruiser conversion, not a glass cannon.','Prydwen Water core'),
      role('Crucible / Conquest · DPS','Personal-damage Water score build',['Swirling Blade','Lunarwater Threads','Seismic Tide','Raging Maelstrom'],['Frigid Aura','Defensive Assault','Frigid Glint','Pursuit of Victory'],'Use the Water shell when Guardian itself is the damage slot: drop the safety charm for Pursuit of Victory and lean into repeated Cold/Water pressure. If your team has a much stronger carry, Tank mode’s support bar will usually produce the better team score.','On bosses where Raging Maelstrom loses value, test a high-rank Star Shattering Slash in that flex slot rather than forcing AoE.','Prydwen Water + score logic'),
      role('Arena · DPS','Offensive block / counter bruiser',['Swirling Blade','Luminous Shield','Forceful Charge','Star Shattering Slash'],['Rebound','Holy Aegis','Block Mastery','Eye for an Eye'],'This keeps the proven Block/Rebound PvP shell but spends the flex slots on actual kill pressure. If Pandarial and your ranks support it, Luminous Shield → Light Sword Array is the aggressive flex; keep Block stats high.','If the opponent can burst through you, Eye for an Eye → Soul Protection or Potential Rebirth before changing the whole bar.','Prydwen secondary + PvP synthesis'),
      role('Tournament · 2v2 · DPS','Duo bruiser: survive focus while threatening kills',['Swirling Blade','Luminous Shield','Forceful Charge','Star Shattering Slash'],['Rebound','Holy Aegis','Block Mastery','Eye for an Eye'],'2v2 still rewards the counter/bruiser shell because you cannot afford to be deleted, but DPS mode keeps the fourth charm offensive instead of protecting the partner with Oath.','If you become the enemy team’s obvious first target, Eye for an Eye → Soul Protection; otherwise keep the pressure.','Current Guardian PvP synthesis'),
      role('Tournament · 4v4 · DPS','Water AoE team-pressure build',['Swirling Blade','Lunarwater Threads','Seismic Tide','Raging Maelstrom'],['Frigid Aura','Defensive Assault','Frigid Glint','Potential Rebirth'],'Four enemy bodies give the Water shell its best chance to stack Cold and spread pressure. If your team already has a real frontline and you are not being focused, Potential Rebirth → Pursuit of Victory for the greedier version.','If your team lacks a tank, switch the role toggle back to Tank rather than trying to make this bar absorb coordinated focus.','Prydwen Water + team-PvP logic')
    ]''',
'Destroyer': r'''    Destroyer:[
      role('Dungeon','Fire AoE horde-clear meta',['Formation Breaker','Fiery Star Trail','Fireball','Meteoric Flames'],['Rapid Cast','Void Bubble','Explosive Spirit','Fiery Burst'],'Fire is the dedicated dungeon/horde build because Fiery Burst scales off repeated Fire triggers across packs. If the room is boss-heavy and packs survive poorly, swap to the mixed AoE core instead.','Strong accounts can drop Void Bubble for offense, but a dead Destroyer loses more time than the greed gains.','Prydwen + Global testing'),
      role('Crucible / Conquest','Single-target score meta',['Formation Breaker','Divine Wrath','Wind Blade Spiral','Thunder of Judgment'],['Rapid Cast','Mana Surge','Radiant Sear','Incarnation of Light'],'Formation Breaker is non-negotiable and also accelerates a stronger carry. Wind Blade Spiral → Wind\'s Delight or Tempest Sphere if your ranks/dummy tests win; high-hit Wind\'s Delight can overperform through Radiant Sear procs.','If survival matters, Incarnation of Light → Void Bubble. On small bosses, Divine Wrath → Meteoric Flames can test better.','Guide + score testing'),
      role('Arena','Wind control / solo tempo',['Tempest Sphere','Wind Blade Spiral',"Wind's Delight",'Howling Hurricane'],['Cyclone Lament','Repelling Wind',"Wind's Shadow",'Void Bubble'],'Mono-Wind gives the cleanest solo-PvP identity: movement pressure, Laceration, knockback/delay and enough repeated hits to keep pressure on one target.','Keep Void Bubble unless you massively outgear the opponent; fragile casters usually need the extra turn.','Guide + community PvP'),
      role('Tournament · 2v2','Duo control + Formation Breaker tempo',['Formation Breaker','Tempest Sphere','Wind Blade Spiral',"Wind's Delight"],['Rapid Cast','Void Bubble','Repelling Wind','Cyclone Lament'],'Formation Breaker gains value because its action acceleration can swing your partner\'s turn order, while the rest of the bar keeps reliable player-sized Wind pressure.','If your teammate already supplies control, Repelling Wind can flex to Radiant Sear for more kill pressure.','Meta synthesis'),
      role('Tournament · 4v4','Team AoE + Formation Breaker acceleration',['Formation Breaker','Howling Hurricane','Meteoric Flames','Wind Blade Spiral'],['Rapid Cast','Void Bubble','Cyclone Lament','Radiant Sear'],'Formation Breaker is the centerpiece in 4v4: buff/advance allies, then layer broad AoE and Laceration pressure across the enemy team.','Keep Void Bubble under coordinated focus. If another source already covers team tempo, the fourth Technique is the first flex slot.','Prydwen team core')
    ]''',
'Dominator': r'''    Dominator:[
      role('Dungeon','Hard-dungeon healer/support meta',['Waterling Summon','Rejuvenating Rain','Radiant Restoration','Frenzy Totem'],['Phantom Light','Healing Mastery','Overhealing','Resurrection'],'Need more raw healing: Frenzy Totem → Healing Touch. If nobody is dying, Resurrection → Mantra of Blessings. Phantom Light is mandatory for the T4 healer shell.','Use the Heals stat profile for this card. Mandragora is the pure-heal lead until Pandarial becomes live and validated.','Prydwen healer core'),
      role('Crucible / Conquest','Booster support for a stronger carry',['Radiant Restoration','Decoy Clone','Frenzy Totem','Dark Bullet'],['Phantom Light','Healing Mastery','Overhealing','Mantra of Blessings'],'This is team-score optimization, not personal recount chasing: Decoy + Totem + Mantra amplify the carry while Dark Bullet still contributes Erosion/debuff value. Coordinate duplicates—multiple Decoy/Mantra effects may not stack efficiently.','If you are actually the damage carry or playing solo, use the high-EHR ST Dark bar instead of this booster setup.','Loot & Waifus + Global testing'),
      role('Arena','Solo Dark burst / Erosion cash-out',['Abyssal Hand','Dark Starburst','Dark Bullet','Shadow of Termination'],['Linked Misfortune','Shadow Erosion','Mantra of Blessings','Shadow Vengeance'],'This is the simple current solo-PvP burst shell: apply Erosion, keep reliable direct Dark damage, then Termination cashes out. Mantra buffs you in solo play; Shadow Vengeance buys the finishing turn.','Do not force a pure-healer Arena bar unless your Healing Boost/SPD gear is unusually optimized; PvP healing is reduced.','Loot & Waifus Arena'),
      role('Tournament · 2v2','Duo anti-tank pressure + revive utility',['Dark Bullet','Dark Starburst','Abyssal Hand','Shadow of Termination'],['Linked Misfortune','Shadow Erosion','Resurrection','Shadow Vengeance'],'2v2 needs more kill pressure than 4v4. Keep the Erosion/Termination threat, but trade the selfish Arena buff slot for Resurrection because restoring your only teammate can flip the match.','If your partner is a much stronger carry, Linked Misfortune or Abyssal Hand can flex to Mantra/Frenzy support instead.','PvP synthesis'),
      role('Tournament · 4v4','Hybrid support / anti-tank utility',['Decoy Clone','Frenzy Totem','Dark Starburst','Abyssal Hand'],['Mantra of Blessings','Resurrection','Shadow Vengeance','Aberrancy'],'Do not default to full healing: Decoy pressures shield-heavy tanks, Totem + Mantra amplify the carry, Resurrection steals rounds, and Aberrancy is much better in broad debuff-heavy team fights than Arena.','If your team truly lacks sustain, Abyssal Hand → Radiant Restoration. Full-heal Tournament only makes sense on dedicated Healing Boost/SPD gear.','Community + guide PvP')
    ]'''
}

META_CSS = r'''
/* META_BUILD_MODES_V1 */
/* GUARDIAN_ROLE_TOGGLE_V1 */
.builds .guardianHeadingRow{display:flex;align-items:center;gap:9px;margin-top:3px;min-width:0;flex-wrap:wrap}
.builds .guardianHeadingRow>strong{margin-top:0;flex:0 0 auto}
.builds .guardianModeTabs{display:inline-flex;align-items:center;gap:3px;margin:0;padding:3px;border:1px solid var(--line);border-radius:10px;background:var(--surface);flex:0 0 auto}
.builds .guardianModeTabs button{min-height:30px;min-width:52px;padding:4px 9px;border:0;border-radius:7px;background:transparent;color:var(--muted);cursor:pointer;font-size:10px;font-weight:850}
.builds .guardianModeTabs button:hover{color:var(--green)}
.builds .guardianModeTabs button.active{background:var(--accent-strong);color:#fff}
@media(max-width:520px){.builds .guardianHeadingRow{gap:7px}.builds .guardianModeTabs button{min-height:30px;min-width:50px}}
.builds .metaBuildControls{display:flex;align-items:center;gap:7px;margin:10px 0;padding:5px;border:1px solid var(--line);border-radius:13px;background:var(--surface)}
.builds .metaBuildTabs{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:5px;flex:1;min-width:0}
.builds .metaBuildTabs button,.builds .metaTournamentTabs button{border:0;border-radius:9px;background:transparent;color:var(--muted);cursor:pointer;font-size:10px;font-weight:850;min-height:36px;padding:8px 10px}
.builds .metaBuildTabs button.active,.builds .metaTournamentTabs button.active{background:var(--accent-strong);color:#fff}
.builds .metaTournamentTabs{display:flex;gap:4px;padding-left:7px;border-left:1px solid var(--line)}
.builds .metaTournamentTabs[hidden]{display:none!important}
.builds .buildGrid.metaModeGrid{grid-template-columns:1fr!important;margin-top:0}
.builds .buildGrid.metaModeGrid>.buildCard[hidden]{display:none!important}
@media(min-width:761px){
  .builds .buildGrid.metaModeGrid>.buildCard:not([hidden]){display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);column-gap:18px;align-items:start}
  .builds .buildGrid.metaModeGrid>.buildCard:not([hidden])>header,
  .builds .buildGrid.metaModeGrid>.buildCard:not([hidden])>ul,
  .builds .buildGrid.metaModeGrid>.buildCard:not([hidden])>.fantomonPair{grid-column:1/-1}
}
@media(max-width:620px){
  .builds .metaBuildControls{display:block}
  .builds .metaBuildTabs{grid-template-columns:repeat(2,minmax(0,1fr))}
  .builds .metaTournamentTabs{border-left:0;border-top:1px solid var(--line);padding:5px 0 0;margin-top:5px}
  .builds .metaTournamentTabs button{flex:1}
}
'''

META_JS = r'''
  const META_CLASSES=new Set(['Conqueror','Guardian','Destroyer','Dominator']);
  const META_MODES=['Dungeon','Crucible / Conquest','Arena','Tournament'];
  const metaRead=(key,fallback)=>{try{return localStorage.getItem(key)||fallback}catch(_){return fallback}};
  const metaWrite=(key,val)=>{try{localStorage.setItem(key,val)}catch(_){}};
  const metaMode=()=>META_MODES.includes(metaRead('sxs-build-meta-mode','Dungeon'))?metaRead('sxs-build-meta-mode','Dungeon'):'Dungeon';
  const metaTournamentSize=()=>metaRead('sxs-build-tournament-size','4v4')==='2v2'?'2v2':'4v4';
  const guardianBuildMode=()=>metaRead('sxs-build-guardian-mode','tank')==='dps'?'dps':'tank';
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
      box.innerHTML='<div class="metaBuildTabs">'+META_MODES.map(m=>'<button type="button" data-meta-mode="'+esc(m)+'">'+esc(m)+'</button>').join('')+'</div><div class="metaTournamentTabs"><button type="button" data-tournament-size="2v2">2v2</button><button type="button" data-tournament-size="4v4">4v4</button></div>';
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
    const mode=metaMode(), size=metaTournamentSize(), guardianMode=guardianBuildMode();
    document.querySelectorAll('.builds .guardianModeTabs [data-guardian-mode]').forEach(b=>{const on=b.dataset.guardianMode===guardianMode;b.classList.toggle('active',on);b.setAttribute('aria-pressed',String(on));});
    const wanted=mode==='Tournament'?'Tournament · '+size:mode;
    document.querySelectorAll('.builds .metaBuildTabs button').forEach(b=>b.classList.toggle('active',b.dataset.metaMode===mode));
    const tour=document.querySelector('.builds .metaTournamentTabs');
    if(tour){
      tour.hidden=mode!=='Tournament';
      tour.querySelectorAll('button').forEach(b=>b.classList.toggle('active',b.dataset.tournamentSize===size));
    }
    grid.querySelectorAll(':scope > .buildCard').forEach(card=>{
      const wrongActivity=card.dataset.role!==wanted;
      const wrongGuardianRole=cls==='Guardian'&&card.dataset.guardianRole!==guardianMode;
      card.hidden=wrongActivity||wrongGuardianRole;
    });
  }
'''


def patch_inject(text: str) -> str:
    if MARK in text:
        return text
    rs = text.index('  const ROLE_PRESETS={')
    re_ = text.index('\n  const FANTO={', rs)
    role_text = text[rs:re_]
    for cls, block in T4_BLOCKS.items():
        pat = re.compile(rf'(?ms)^    {cls}:\[\n.*?^    \](?=,\n    [A-Za-z]+:|\n  \}};)')
        role_text, n = pat.subn(block, role_text, count=1)
        if n != 1:
            raise RuntimeError(f'Could not replace {cls} ROLE_PRESETS block')
    text = text[:rs] + role_text + text[re_:]

    # Add the mode UI styling to the maintained injection.
    first_style_end = text.find('</style>')
    if first_style_end < 0:
        raise RuntimeError('Injector style block not found')
    text = text[:first_style_end] + META_CSS + '\n' + text[first_style_end:]

    # Add activity-mode helpers before activeClass().
    anchor = '  function activeClass(){'
    if anchor not in text:
        raise RuntimeError('activeClass anchor missing')
    text = text.replace(anchor, META_JS + '\n' + anchor, 1)

    # After cards/fantos are installed, apply activity filtering.
    old = "    applyRoleLoadouts(cls);\n    applyFantos(cls);"
    new = "    applyRoleLoadouts(cls);\n    applyFantos(cls);\n    ensureMetaControls(cls);\n    applyMetaVisibility(cls);"
    if old not in text:
        raise RuntimeError('apply() anchor missing')
    text = text.replace(old, new, 1)

    # Click behavior for the new primary and Tournament-size toggles.
    old = "    if(root) new MutationObserver(queueApply).observe(root,{subtree:true,childList:true,attributes:true,attributeFilter:['class','aria-pressed']});"
    new = old + "\n    root?.addEventListener('click',e=>{\n      const guardianBtn=e.target.closest?.('[data-guardian-mode]');\n      if(guardianBtn&&activeClass()==='Guardian'){metaWrite('sxs-build-guardian-mode',guardianBtn.dataset.guardianMode==='dps'?'dps':'tank');applyMetaVisibility('Guardian');queueApply();return;}\n      const modeBtn=e.target.closest?.('[data-meta-mode]');\n      if(modeBtn){metaWrite('sxs-build-meta-mode',modeBtn.dataset.metaMode);applyMetaVisibility(activeClass());return;}\n      const sizeBtn=e.target.closest?.('[data-tournament-size]');\n      if(sizeBtn){metaWrite('sxs-build-tournament-size',sizeBtn.dataset.tournamentSize);applyMetaVisibility(activeClass());}\n    });"
    if old not in text:
        raise RuntimeError('DOMContentLoaded observer anchor missing')
    text = text.replace(old, new, 1)

    # Put a stable marker in the header comments.
    comment_anchor = '/* ARENA_TOURNAMENT_RESTORE_V2 */'
    if comment_anchor not in text:
        raise RuntimeError('Injector header marker missing')
    text = text.replace(comment_anchor, comment_anchor + '\n/* ' + MARK + ' */', 1)
    return text


def disable_dominator_card_filter(text: str) -> str:
    # The old Dominator DPS/Heals toggle should continue to control stat/priority
    # panels, but activity-driven loadout cards must not be hidden by that role toggle.
    pat = re.compile(r"\n    host\.querySelectorAll\('\.buildGrid \.buildCard'\)\.forEach\(card=>\{.*?\n    \}\);", re.S)
    replacement = "\n    // Loadout cards are activity-driven by META_BUILD_MODES_V1; the Dominator DPS/Heals toggle only changes stat/priority panels."
    out, n = pat.subn(replacement, text, count=1)
    if n != 1 and 'activity-driven by META_BUILD_MODES_V1' not in text:
        raise RuntimeError('Could not disable old Dominator card-role filter')
    return out


inject = patch_inject(INJECT.read_text(encoding='utf-8'))
INJECT.write_text(inject, encoding='utf-8')

index = INDEX.read_text(encoding='utf-8')
a = index.find(START)
b = index.find(END, a)
if a < 0 or b < 0:
    raise RuntimeError('Live build injection block missing')
b += len(END)
index = index[:a] + inject.strip() + index[b:]
index = disable_dominator_card_filter(index)
INDEX.write_text(index, encoding='utf-8')

restore = RESTORE.read_text(encoding='utf-8')
restore = restore.replace("    'BUILD_ARENA_TOURNAMENT_SPLIT_V1',\n    \"role('Arena'\",\n    \"role('Tournament'\",", "    'META_BUILD_MODES_V1',\n    \"role('Arena'\",\n    \"role('Tournament · 2v2'\",\n    \"role('Tournament · 4v4'\",")
restore = disable_dominator_card_filter(restore)
RESTORE.write_text(restore, encoding='utf-8')

print('Installed S2 meta activity builds with Dungeon / Crucible-Conquest / Arena / Tournament 2v2-4v4 modes')
