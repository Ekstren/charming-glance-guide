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
      role('Crucible / Conquest','Single-target score / raid-boss meta',['Flame Aura','Blade Storm','Flash Fire','Flickering Blade'],['Piercing Assault','Tactical Adaptation','Blazing Clash','Insightful Eye'],'At high enough Crit, Insightful Eye → Crit Mastery. This setup is built for maximum single-target score; keep Indomitable only when survival is actually costing attempts.','Keep the four-Technique rotation intact; rank/ascension can matter more than tiny theoretical swaps.','Prydwen score core'),
      role('Arena','Solo PvP / anti-Guardian pressure',['Darkness Descends','Doom Blade','Flickering Blade','Blade Storm'],['Piercing Assault','Tactical Adaptation','Soul Breaker','Indomitable Will'],'Darkness Descends is the key Dispel/mobility slot. If you need sustain more than Doom Blade pressure, Doom Blade → Soul Piercer. Low Crit: Soul Breaker → Insightful Eye.','Accuracy is premium into high-Block Guardians. Keep Indomitable Will even when you outpower the target.','Current PvP'),
      role('Tournament · 2v2','Duo PvP: sustain + kill pressure',['Darkness Descends','Soul Piercer','Flickering Blade','Blade Storm'],['Piercing Assault','Tactical Adaptation','Soul Breaker','Indomitable Will'],'Soul Piercer gives the duo bar more self-sustain while Darkness keeps Dispel. Low Crit: Soul Breaker → Insightful Eye. If your partner already supplies enough control, Soul Piercer can flex back to Doom Blade for harder burst.','Keep Indomitable Will in 2v2; one death is half the team.','Current Global PvP'),
      role('Tournament · 4v4','Team PvP: reach, Dispel and coordinated tempo',['Flash Fire','Darkness Descends','Flickering Blade','Blade Storm'],['Insightful Eye','Piercing Assault','Tactical Adaptation','Indomitable Will'],'High Crit: Insightful Eye → Soul Breaker. With two Conquerors, the higher-rank Gale Dance user can flex it in for the team SPD boost while the other keeps the full damage bar.','Flash Fire keeps reach in a spread-out fight; Darkness is retained for buff removal. Indomitable stays mandatory under focus fire.','Current Global PvP')
    ]''',
'Guardian': r'''    Guardian:[
      role('Dungeon · Tank','Primary S2 party-tank meta',['Valor Surge','Heart of Challenge','Luminous Shield','Desperate Protection'],['Iron Will','Holy Aegis','Block Awareness','Soul Protection'],'Need more Taunt: Desperate Protection → Hamper Strike when survival is already stable. If the group is already safe, Desperate Protection → Swirling Blade or Star Shattering Slash for faster clears.','If the team still dies, Iron Fortress is the first extra defensive flex. Aegiswing is the default lead.','Prydwen dungeon core'),
      role('Crucible / Conquest · Tank','Carry-support / boss tank meta',['Valor Surge','Leap Attack','Holy Purification','Lunarwater Threads'],['Frigid Aura','Frigid Glint','Iron Fortress','Oath of Vigil'],'Buff the carry, use Holy Purification for Dispel/utility, and let Lunarwater Threads + the Frigid charms add useful Water/Cold pressure. If the boss has no important buff to remove, Holy Purification → a higher-damage option.','Iron Fortress and Oath of Vigil keep the party protected without overcommitting to personal mitigation. If you are actually dying, Frigid Glint → Soul Protection; if needed, Frigid Aura → Holy Aegis. Kels remains the boss-support Fantomon when Dispel/DEF Down matters.','Guide-backed'),
      role('Arena · Tank','Solo block / reflect wall',['Valor Surge','Luminous Shield','Star Shattering Slash','Desperate Protection'],['Rebound','Holy Aegis','Block Mastery','Soul Protection'],'If your natural Block is not high enough, Soul Protection → Block Awareness. The goal is to survive the opening burst and punish repeated hits rather than imitate a DPS class.','Aegiswing is the safest Arena lead. Against weak pressure, one defensive slot can flex to offense.','Current PvP'),
      role('Tournament · 2v2 · Tank','Duo frontline: protect one carry and still threaten',['Hamper Strike','Heart of Challenge','Luminous Shield','Desperate Protection'],['Iron Will','Rebound','Iron Fortress','Oath of Vigil'],'Oath of Vigil is much stronger here than in Arena because there is exactly one partner to protect. Rebound gives the smaller fight real punishment while Hamper Strike + Heart control targeting.','If focus fire is overwhelming, Rebound → Soul Protection. If your partner is the tankier unit, Holy Aegis is a valid self-survival flex.','Current PvP'),
      role('Tournament · 4v4 · Tank','Full-team tank: Taunt + ally protection',['Hamper Strike','Heart of Challenge','Luminous Shield','Desperate Protection'],['Iron Will','Soul Protection','Iron Fortress','Oath of Vigil'],'Maximize team protection with reliable Taunt, opening effective HP, group mitigation and Oath protection on the ally most likely to be bursted.','If your team already has another reliable frontline, one defensive slot can flex to damage.','Prydwen + Global PvP'),
      role('Dungeon · DPS','Water AoE / fast-clear bruiser',['Valor Surge','Swirling Blade','Lunarwater Threads','Raging Maelstrom'],['Frigid Aura','Defensive Assault','Frigid Glint','Potential Rebirth'],'Stack Cold quickly, pressure groups with Water AoE, and keep enough single-target damage for elites. If you completely outgear the room, Potential Rebirth → Pursuit of Victory or another damage charm.','Keep enough Block/DEF to stay active; Guardian damage still benefits from staying in the fight.','Prydwen Water core'),
      role('Crucible / Conquest · DPS','Single-target Guardian score build',['Valor Surge','Swirling Blade','Lunarwater Threads','Star Shattering Slash'],['Frigid Aura','Defensive Assault','Frigid Glint','Pursuit of Victory'],'Keep the three Water Techniques for consistent Cold stacking, then use Star Shattering Slash for the single-target payoff. If a much stronger carry is present, a support-focused Guardian can still raise total team damage more.','Star Shattering Slash is the Paladin/Guardian line’s heavy single-target nuke. If your copy is badly under-ranked versus Raging Maelstrom, dummy-test the two before forcing the swap.','Prydwen ST hybrid + Global testing'),
      role('Arena · DPS','Offensive block / counter bruiser',['Valor Surge','Swirling Blade','Luminous Shield','Star Shattering Slash'],['Rebound','Holy Aegis','Block Mastery','Eye for an Eye'],'Use Block/Rebound durability while spending the flex slots on real kill pressure. If Pandarial and your ranks support it, Luminous Shield → Light Sword Array for a more aggressive setup; keep Block stats high.','If the opponent can burst through you, Eye for an Eye → Soul Protection or Potential Rebirth before changing the whole bar.','Prydwen + PvP'),
      role('Tournament · 2v2 · DPS','Duo bruiser: survive focus while threatening kills',['Valor Surge','Swirling Blade','Luminous Shield','Star Shattering Slash'],['Rebound','Holy Aegis','Block Mastery','Eye for an Eye'],'2v2 still rewards the counter/bruiser setup because you cannot afford to be deleted; keep the fourth Charm offensive unless you become the enemy team’s obvious first target.','If you become the enemy team’s obvious first target, Eye for an Eye → Soul Protection; otherwise keep the pressure.','Current PvP'),
      role('Tournament · 4v4 · DPS','Water AoE team-pressure build',['Valor Surge','Swirling Blade','Lunarwater Threads','Raging Maelstrom'],['Frigid Aura','Defensive Assault','Frigid Glint','Potential Rebirth'],'Four enemy bodies give the Water/Cold setup plenty of opportunities to stack Cold and spread pressure. If your team already has a frontline and you are not being focused, Potential Rebirth → Pursuit of Victory for more damage.','If your team lacks a frontline, use the Tank setup instead.','Prydwen Water + team-PvP logic')
    ]''',
'Destroyer': r'''    Destroyer:[
      role('Dungeon','Fire AoE horde-clear meta',['Formation Breaker','Fiery Star Trail','Fireball','Meteoric Flames'],['Rapid Cast','Void Bubble','Explosive Spirit','Fiery Burst'],'Fire is strongest for dense dungeon packs because Fiery Burst scales off repeated Fire triggers. If most of the fight is a boss, use the mixed-element setup instead.','Drop Void Bubble for offense only when deaths are no longer costing clears.','Prydwen + Global testing'),
      role('Crucible / Conquest','Single-target score meta',['Formation Breaker','Divine Wrath','Wind Blade Spiral','Thunder of Judgment'],['Rapid Cast','Mana Surge','Radiant Sear','Incarnation of Light'],'Formation Breaker is non-negotiable and also accelerates a stronger carry. Wind Blade Spiral → Wind\'s Delight or Tempest Sphere if your ranks/dummy tests win; high-hit Wind\'s Delight can overperform through Radiant Sear procs.','If survival matters, Incarnation of Light → Void Bubble. On small bosses, Divine Wrath → Meteoric Flames can test better.','Guide + score testing'),
      role('Arena','Wind control / solo tempo',['Formation Breaker','Tempest Sphere','Wind Blade Spiral',"Wind's Delight"],['Cyclone Lament','Repelling Wind',"Wind's Shadow",'Void Bubble'],'Arena is one target, so drop Howling Hurricane’s huge AoE. Formation Breaker stays because its action acceleration remains valuable, while the other three Wind skills provide compact player-sized pressure and Laceration tempo.','Keep Void Bubble unless you massively outgear the opponent; Repelling Wind is the anti-melee control flex.','Prydwen + Global PvP'),
      role('Tournament · 2v2','Duo control + Formation Breaker tempo',['Formation Breaker','Tempest Sphere','Wind Blade Spiral',"Wind's Delight"],['Rapid Cast','Void Bubble','Repelling Wind','Cyclone Lament'],'Formation Breaker gains value because its action acceleration can swing your partner\'s turn order, while the rest of the bar keeps reliable player-sized Wind pressure.','If your teammate already supplies control, Repelling Wind can flex to Radiant Sear for more kill pressure.','Current PvP'),
      role('Tournament · 4v4','Team AoE + Formation Breaker acceleration',['Formation Breaker','Howling Hurricane','Meteoric Flames','Wind Blade Spiral'],['Rapid Cast','Void Bubble','Cyclone Lament','Radiant Sear'],'Formation Breaker is the centerpiece in 4v4: buff/advance allies, then layer broad AoE and Laceration pressure across the enemy team.','Keep Void Bubble under coordinated focus. If another source already covers team tempo, the fourth Technique is the first flex slot.','Prydwen team core')
    ]''',
'Dominator': r'''    Dominator:[
      role('Dungeon · DPS','AoE Dark / Erosion clear',['Mana Blast','Dark Bullet','Abyssal Hand','Shadow Impact'],['Shadow Vengeance',"Night's Blessing",'Shadow Erosion','Linked Misfortune'],'For dungeon packs, all four slots contribute damage so Erosion and direct hits can clear groups quickly.','If Erosion is landing poorly, improve Effect Hit Rate before changing the build. Nyxarchon is the damage lead.','Prydwen AoE core'),
      role('Crucible / Conquest · DPS','Single-target direct / Erosion hybrid',['Dark Bullet','Dark Starburst','Chaos Rune','Shadow of Termination'],['Shadow Vengeance',"Night's Blessing",'Shadow Erosion','Linked Misfortune'],'Dark Starburst + Chaos Rune provide reliable direct damage while Shadow of Termination preserves the Erosion payoff. With high Effect Hit Rate, Chaos Rune → Mana Blast raises the Erosion ceiling.','If a much stronger carry is in the party, the Decoy + Frenzy + Mantra support setup can produce more team score than selfish DPS.','Prydwen ST core'),
      role('Arena · DPS','Single-target Dark pressure',['Dark Bullet','Dark Starburst','Chaos Rune','Shadow of Termination'],['Shadow Vengeance',"Night's Blessing",'Shadow Erosion','Linked Misfortune'],'Arena is one target, so favor the single-target setup over broad Abyssal Hand AoE. High Effect Hit Rate: Chaos Rune → Mana Blast.','If your current Chaos Rune is badly under-ranked or unreliable, test a direct-damage flex rather than forcing it. PvP healing is heavily reduced, so DPS is the normal Arena default.','Prydwen ST + PvP logic'),
      role('Tournament · 2v2 · DPS','Duo kill pressure + revive',['Dark Bullet','Dark Starburst','Chaos Rune','Shadow of Termination'],['Shadow Vengeance','Shadow Erosion','Linked Misfortune','Resurrection'],'Keep the compact single-target damage setup but reserve one Charm slot for Resurrection; reviving your only teammate can swing an entire 2v2 round.','If your partner is the true carry, use the support setup rather than weakening this DPS build with half a support kit.','Prydwen + PvP'),
      role('Tournament · 4v4 · DPS','AoE Dark pressure + revive',['Mana Blast','Dark Bullet','Abyssal Hand','Shadow Impact'],['Shadow Vengeance','Shadow Erosion','Linked Misfortune','Resurrection'],'Four enemy bodies make the AoE/Erosion setup worthwhile. Resurrection replaces the selfish fourth damage Charm because its team-fight swing is unusually high.','If your team is built around a hypercarry, Decoy + Frenzy + Mantra support can be more valuable than personal damage.','Prydwen + PvP'),
      role('Dungeon · Heals','Hard-dungeon healer',['Waterling Summon','Rejuvenating Rain','Radiant Restoration','Frenzy Totem'],['Phantom Light','Healing Mastery','Overhealing','Resurrection'],'This is the reliable dungeon-healing setup. Need more raw healing: Frenzy Totem → Healing Touch. If nobody is dying, Resurrection → Mantra of Blessings.','Phantom Light is mandatory for the dedicated healer build. Mandragora is the pure-healing lead until Pandarial is live and validated.','Prydwen healer core'),
      role('Crucible / Conquest · Heals','Hypercarry support / boss score',['Radiant Restoration','Decoy Clone','Frenzy Totem','Dark Bullet'],['Phantom Light','Healing Mastery','Overhealing','Mantra of Blessings'],'Large-group boss content is where Dominator should often stop chasing its own recount: Decoy + Frenzy + Mantra amplify the strongest carry while Radiant Restoration keeps one efficient heal available.','Only one Decoy can attach effectively and positioning matters. If your team already massively overkills the boss, the DPS setup can be better; otherwise prioritize carry support.','Prydwen + Global support testing'),
      role('Arena · Heals','Specialist sustain hybrid',['Rejuvenating Rain','Radiant Restoration','Dark Bullet','Shadow of Termination'],['Phantom Light','Healing Mastery','Shadow Vengeance','Mantra of Blessings'],'Healing is reduced in PvP, so this is intentionally a hybrid rather than a full four-heal bar: enough sustain to exploit a real Healing Boost/SPD set while retaining kill pressure.','Use this healer setup in Arena only when your Healing Boost/SPD gear is genuinely optimized. Otherwise the DPS Arena setup is stronger.','PvP specialist'),
      role('Tournament · 2v2 · Heals','Duo sustain / carry support',['Rejuvenating Rain','Radiant Restoration','Frenzy Totem','Dark Bullet'],['Phantom Light','Healing Mastery','Resurrection','Shadow Vengeance'],'Keep the partner alive, buff their output, and retain Resurrection as the highest-impact team utility. One Dark attack prevents the bar from becoming dead weight between heals.','PvP healing is reduced; if your Healing Boost/SPD cannot overcome that penalty, use the DPS 2v2 setup and keep Resurrection.','PvP support'),
      role('Tournament · 4v4 · Heals','Hybrid team support',['Radiant Restoration','Decoy Clone','Frenzy Totem','Dark Bullet'],['Phantom Light','Healing Mastery','Resurrection','Mantra of Blessings'],'4v4 rewards buffs, Decoy pressure and Resurrection more than raw healing spam. This is the support-oriented Tournament bar, not a pure healer.','If your gear is exceptionally healing-focused, Mantra can flex to Overhealing. Otherwise keep the team-damage support because PvP healing is reduced.','Team PvP')
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
    const mode=metaMode(), size=metaTournamentSize(), guardianMode=guardianBuildMode(), dominatorMode=dominatorBuildMode();
    document.querySelectorAll('.builds .guardianModeTabs [data-guardian-mode]').forEach(b=>{const on=b.dataset.guardianMode===guardianMode;b.classList.toggle('active',on);b.setAttribute('aria-pressed',String(on));});
    document.querySelectorAll('.builds .dominatorModeTabs [data-dominator-mode]').forEach(b=>{const on=b.dataset.dominatorMode===dominatorMode;b.classList.toggle('active',on);b.setAttribute('aria-pressed',String(on));});
    const wanted=mode==='Tournament'?'Tournament · '+size:mode;
    document.querySelectorAll('.builds .metaBuildTabs button').forEach(b=>b.classList.toggle('active',b.dataset.metaMode===mode));
    const tour=document.querySelector('.builds .metaTournamentTabs');
    if(tour){
      tour.hidden=mode!=='Tournament';
      tour.querySelectorAll('button').forEach(b=>b.classList.toggle('active',b.dataset.tournamentSize===size));
    }
    grid.querySelectorAll(':scope > .buildCard').forEach(card=>{
      const wrongActivity=card.dataset.role!==wanted;
      const selectedRole=cls==='Guardian'?guardianMode:(cls==='Dominator'?dominatorMode:'');
      const wrongRole=(cls==='Guardian'||cls==='Dominator')&&card.dataset.buildRole!==selectedRole;
      card.hidden=wrongActivity||wrongRole;
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
    new = old + "\n    root?.addEventListener('click',e=>{\n      const guardianBtn=e.target.closest?.('[data-guardian-mode]');\n      if(guardianBtn&&activeClass()==='Guardian'){metaWrite('sxs-build-guardian-mode',guardianBtn.dataset.guardianMode==='dps'?'dps':'tank');applyMetaVisibility('Guardian');queueApply();return;}\n      const dominatorBtn=e.target.closest?.('[data-dominator-mode]');\n      if(dominatorBtn&&activeClass()==='Dominator'){metaWrite('sxs-build-dominator-mode',dominatorBtn.dataset.dominatorMode==='heals'?'heals':'dps');applyMetaVisibility('Dominator');queueApply();return;}\n      const modeBtn=e.target.closest?.('[data-meta-mode]');\n      if(modeBtn){metaWrite('sxs-build-meta-mode',modeBtn.dataset.metaMode);applyMetaVisibility(activeClass());return;}\n      const sizeBtn=e.target.closest?.('[data-tournament-size]');\n      if(sizeBtn){metaWrite('sxs-build-tournament-size',sizeBtn.dataset.tournamentSize);applyMetaVisibility(activeClass());}\n    });"
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
    # The old detached Dominator card filter stays disabled; META_BUILD_MODES_V1 now
    # owns both activity and DPS/Heals card visibility while the base toggle owns stats.
    pat = re.compile(r"\n    host\.querySelectorAll\('\.buildGrid \.buildCard'\)\.forEach\(card=>\{.*?\n    \}\);", re.S)
    replacement = "\n    // Dominator loadout cards are role/activity-driven by META_BUILD_MODES_V1; legacy detached card filtering stays disabled."
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
