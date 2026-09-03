from pathlib import Path
import re

INDEX = Path('index.html')
INJECT = Path('.github/build-fantomons-inject.html')
META_SRC = Path('scripts/patch_meta_build_modes_v1.py')
RICH_SRC = Path('scripts/patch_restore_rich_builds_v1.py')
ROLL_SRC = Path('scripts/patch_build_roll_guide_v2.py')
MARK = 'GUARDIAN_ROLE_TOGGLE_V1'

GUARDIAN_BLOCK = r'''    Guardian:[
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
    ]'''

GUARDIAN_PROFILE_OLD = r'''    Guardian:{
      rule:'Block is Guardian’s defining stat. Stack Block Rate first; after that, DEF/DMG RES drive survival while SPD remains the best offensive/support tempo stat.',
      rows:[['Sword','SPD > ATK > Physical Mastery > Elemental Mastery'],['Shield','DEF > HP > Physical RES = Elemental RES'],['Helmet','DEF ≥ Physical RES = Elemental RES > HP > Effect RES'],['Chest','DEF ≥ Physical RES = Elemental RES > HP'],['Boots','SPD > ATK > Elemental Mastery = Physical Mastery']],
      substats:'Block Rate > DEF > SPD > HP > DEF% > SPD% > HP%'
    },'''

GUARDIAN_PROFILE_NEW = r'''    Guardian:{
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
    },'''

GUARDIAN_PRIORITY = r'''  const GUARDIAN_PRIORITY={
    tank:[
      ['Tank technique investment','Heart of Challenge first','Rank the Techniques that define the true frontline setup rather than the Water DPS shell.',[
        ['Heart of Challenge','Core group Taunt and one of the most important reasons to bring a Guardian.'],
        ['Valor Surge','Pre-cast team damage buff plus cleanse utility.'],
        ['Luminous Shield','Reliable shield layer across dungeon and PvP tank bars.'],
        ['Desperate Protection / Hamper Strike','Choose survival or more Taunt based on the encounter.']
      ]],
      ['Tank charm investment','Soul Protection first','Prioritize the universal shield/mitigation package before niche damage charms.',[
        ['Soul Protection','Massive opening effective HP and the most universal Guardian T4 charm.'],
        ['Iron Will','Excellent damage reduction once Taunt is active.'],
        ['Holy Aegis','DEF plus stronger DEF-scaling shields.'],
        ['Iron Fortress / Oath of Vigil','Team mitigation and ally protection become premium in Tournament.']
      ]]
    ],
    dps:[
      ['DPS technique investment','Swirling Blade first','The offensive role is the Water/counter bruiser package, not a fake glass-cannon tank.',[
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

'''

GUARDIAN_CSS = r'''/* GUARDIAN_ROLE_TOGGLE_V1 */
.builds .guardianHeadingRow{display:flex;align-items:center;gap:9px;margin-top:3px;min-width:0;flex-wrap:wrap}
.builds .guardianHeadingRow>strong{margin-top:0;flex:0 0 auto}
.builds .guardianModeTabs{display:inline-flex;align-items:center;gap:3px;margin:0;padding:3px;border:1px solid var(--line);border-radius:10px;background:var(--surface);flex:0 0 auto}
.builds .guardianModeTabs button{min-height:30px;min-width:52px;padding:4px 9px;border:0;border-radius:7px;background:transparent;color:var(--muted);cursor:pointer;font-size:10px;font-weight:850}
.builds .guardianModeTabs button:hover{color:var(--green)}
.builds .guardianModeTabs button.active{background:var(--accent-strong);color:#fff}
@media(max-width:520px){.builds .guardianHeadingRow{gap:7px}.builds .guardianModeTabs button{min-height:30px;min-width:50px}}
'''

GUARDIAN_META_JS = r'''  const guardianBuildMode=()=>metaRead('sxs-build-guardian-mode','tank')==='dps'?'dps':'tank';
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
'''


def replace_guardian_block_runtime(text: str) -> str:
    pat = re.compile(r"    Guardian:\[\n      role\('Dungeon','Primary S2 party-tank meta'.*?\n    \],\n    Destroyer:", re.S)
    if pat.search(text):
        return pat.sub(GUARDIAN_BLOCK + ',\n    Destroyer:', text, count=1)
    if "role('Dungeon · Tank'" in text and "role('Dungeon · DPS'" in text:
        return text
    raise RuntimeError('Could not locate current Guardian meta block')


def replace_guardian_block_meta_source(text: str) -> str:
    pat = re.compile(r"'Guardian': r'''    Guardian:\[.*?\n    \]''',\n'Destroyer':", re.S)
    if pat.search(text):
        return pat.sub("'Guardian': r'''" + GUARDIAN_BLOCK + "''',\n'Destroyer':", text, count=1)
    if "role('Dungeon · Tank'" in text and "role('Dungeon · DPS'" in text:
        return text
    raise RuntimeError('Could not locate Guardian T4 block in meta patch source')


def patch_build_helpers(text: str) -> str:
    # Display the activity name only; the Tank/DPS suffix is metadata for Guardian filtering.
    if 'data-guardian-role' not in text:
        pat = re.compile(r"  function buildCardHtml\(r\)\{.*?\n  \}\n  function applyRoleLoadouts", re.S)
        repl = r'''  function buildCardHtml(r){
    const gm=String(r.name||'').match(/^(.*?) · (Tank|DPS)$/);
    const displayName=gm?gm[1]:r.name;
    const guardianAttr=gm?' data-guardian-role="'+gm[2].toLowerCase()+'"':'';
    return '<article class="buildCard" data-role="'+esc(displayName)+'"'+guardianAttr+'>'
      +'<header><div><h3>'+esc(displayName)+'<span class="roleBadge">'+esc(r.confidence)+'</span></h3><p>'+esc(r.subtitle)+'</p></div></header>'
      +'<div class="skillGroup"><span>Techniques</span><div>'+r.techniques.map(x=>'<b>'+esc(x)+'</b>').join('')+'</div></div>'
      +'<div class="skillGroup"><span>Charms</span><div>'+r.charms.map(x=>'<b>'+esc(x)+'</b>').join('')+'</div></div>'
      +'<ul><li><b>Offensive:</b> '+esc(r.offensive)+'</li><li><b>Defensive:</b> '+esc(r.defensive)+'</li></ul>'
      +'</article>';
  }
  function applyRoleLoadouts'''
        text, n = pat.subn(repl, text, count=1)
        if n != 1:
            raise RuntimeError('Could not patch buildCardHtml for Guardian role metadata')

    if "if(t==='dungeon') return 'Dungeon';" not in text:
        anchor = "    const t=(title||'').toLowerCase();\n"
        if anchor not in text:
            raise RuntimeError('Could not find roleKey title anchor')
        text = text.replace(anchor, anchor + "    if(t==='dungeon') return 'Dungeon';\n    if(t==='crucible / conquest') return 'Boss';\n", 1)

    # DPS Guardian should receive offensive Fantomon ordering while Tank keeps the established pools.
    if 'Guardian DPS role prefers the offensive pet order' not in text:
        old = "    const pools=FANTO[cls]||{};\n"
        new = old + "    // Guardian DPS role prefers the offensive pet order; this automatically promotes Pandarial once the staged release patch adds it.\n    const guardianDps=cls==='Guardian'&&typeof guardianBuildMode==='function'&&guardianBuildMode()==='dps';\n"
        if old not in text:
            raise RuntimeError('Could not find FANTO pool anchor')
        text = text.replace(old, new, 1)
        old_return = "    return pools[role]||[];\n"
        new_return = "    const base=pools[role]||[];\n    if(guardianDps){\n      const order=['Pandarial','Nyxarchon','Kels','Aegiswing','Terragon','Boaro'];\n      return [...base].sort((a,b)=>{const ai=order.indexOf(a.name),bi=order.indexOf(b.name);return (ai<0?99:ai)-(bi<0?99:bi);});\n    }\n    return base;\n"
        if old_return not in text:
            raise RuntimeError('Could not patch normal FANTO return')
        text = text.replace(old_return, new_return, 1)
        # Arena/Tournament return early, so make their base pools role-aware too.
        text = text.replace("    if(role==='Arena') return pools.Arena||pools.PvP||[];\n", "    if(role==='Arena'){const base=pools.Arena||pools.PvP||[];if(guardianDps){const order=['Pandarial','Nyxarchon','Kels','Aegiswing','Terragon','Boaro'];return [...base].sort((a,b)=>(order.indexOf(a.name)<0?99:order.indexOf(a.name))-(order.indexOf(b.name)<0?99:order.indexOf(b.name)));}return base;}\n", 1)
        text = text.replace("      return pools.Tournament||pools.PvP||pools.Dungeon||[];\n", "      const base=pools.Tournament||pools.PvP||pools.Dungeon||[];if(guardianDps){const order=['Pandarial','Nyxarchon','Kels','Aegiswing','Terragon','Boaro'];return [...base].sort((a,b)=>(order.indexOf(a.name)<0?99:order.indexOf(a.name))-(order.indexOf(b.name)<0?99:order.indexOf(b.name)));}return base;\n", 1)
    return text


def patch_meta_runtime(text: str) -> str:
    if MARK not in text:
        # Add CSS next to the existing meta controls.
        css_anchor = '/* META_BUILD_MODES_V1 */\n.builds .metaBuildControls'
        if css_anchor not in text:
            raise RuntimeError('Could not locate META_BUILD_MODES CSS anchor')
        text = text.replace(css_anchor, '/* META_BUILD_MODES_V1 */\n' + GUARDIAN_CSS + '.builds .metaBuildControls', 1)

    if 'const guardianBuildMode=' not in text:
        anchor = "  const metaTournamentSize=()=>metaRead('sxs-build-tournament-size','4v4')==='2v2'?'2v2':'4v4';\n"
        if anchor not in text:
            raise RuntimeError('Could not find meta tournament-size anchor')
        text = text.replace(anchor, anchor + GUARDIAN_META_JS, 1)

    old = "    if(!grid) return;\n    let box=document.querySelector('.builds .metaBuildControls');"
    new = "    if(!grid) return;\n    ensureGuardianRoleControl(cls);\n    let box=document.querySelector('.builds .metaBuildControls');"
    if old in text:
        text = text.replace(old, new, 1)

    if "const mode=metaMode(), size=metaTournamentSize(), guardianMode=guardianBuildMode();" not in text:
        old = "    const mode=metaMode(), size=metaTournamentSize();\n"
        new = "    const mode=metaMode(), size=metaTournamentSize(), guardianMode=guardianBuildMode();\n    document.querySelectorAll('.builds .guardianModeTabs [data-guardian-mode]').forEach(b=>{const on=b.dataset.guardianMode===guardianMode;b.classList.toggle('active',on);b.setAttribute('aria-pressed',String(on));});\n"
        if old not in text:
            raise RuntimeError('Could not patch meta visibility mode declaration')
        text = text.replace(old, new, 1)

    old = "    grid.querySelectorAll(':scope > .buildCard').forEach(card=>{card.hidden=card.dataset.role!==wanted;});\n"
    new = "    grid.querySelectorAll(':scope > .buildCard').forEach(card=>{\n      const wrongActivity=card.dataset.role!==wanted;\n      const wrongGuardianRole=cls==='Guardian'&&card.dataset.guardianRole!==guardianMode;\n      card.hidden=wrongActivity||wrongGuardianRole;\n    });\n"
    if old in text:
        text = text.replace(old, new, 1)

    if "const guardianBtn=e.target.closest?.('[data-guardian-mode]');" not in text:
        old = "    root?.addEventListener('click',e=>{\n      const modeBtn=e.target.closest?.('[data-meta-mode]');"
        new = "    root?.addEventListener('click',e=>{\n      const guardianBtn=e.target.closest?.('[data-guardian-mode]');\n      if(guardianBtn&&activeClass()==='Guardian'){metaWrite('sxs-build-guardian-mode',guardianBtn.dataset.guardianMode==='dps'?'dps':'tank');applyMetaVisibility('Guardian');queueApply();return;}\n      const modeBtn=e.target.closest?.('[data-meta-mode]');"
        if old not in text:
            raise RuntimeError('Could not patch meta click handler for Guardian toggle')
        text = text.replace(old, new, 1)
    return text


def patch_meta_source(text: str) -> str:
    text = replace_guardian_block_meta_source(text)

    # Patch the META_CSS raw string carried by the maintained meta installer.
    if MARK not in text:
        css_anchor = '/* META_BUILD_MODES_V1 */\n.builds .metaBuildControls'
        if css_anchor not in text:
            raise RuntimeError('Could not locate META_BUILD_MODES CSS anchor in meta source')
        text = text.replace(css_anchor, '/* META_BUILD_MODES_V1 */\n' + GUARDIAN_CSS + '.builds .metaBuildControls', 1)

    # Patch the META_JS raw string carried by the maintained meta installer.
    if 'const guardianBuildMode=' not in text:
        anchor = "  const metaTournamentSize=()=>metaRead('sxs-build-tournament-size','4v4')==='2v2'?'2v2':'4v4';\n"
        if anchor not in text:
            raise RuntimeError('Could not find meta tournament-size anchor in meta source')
        text = text.replace(anchor, anchor + GUARDIAN_META_JS, 1)

    old = "    if(!grid) return;\n    let box=document.querySelector('.builds .metaBuildControls');"
    new = "    if(!grid) return;\n    ensureGuardianRoleControl(cls);\n    let box=document.querySelector('.builds .metaBuildControls');"
    if old in text:
        text = text.replace(old, new, 1)

    if "const mode=metaMode(), size=metaTournamentSize(), guardianMode=guardianBuildMode();" not in text:
        old = "    const mode=metaMode(), size=metaTournamentSize();\n"
        new = "    const mode=metaMode(), size=metaTournamentSize(), guardianMode=guardianBuildMode();\n    document.querySelectorAll('.builds .guardianModeTabs [data-guardian-mode]').forEach(b=>{const on=b.dataset.guardianMode===guardianMode;b.classList.toggle('active',on);b.setAttribute('aria-pressed',String(on));});\n"
        if old not in text:
            raise RuntimeError('Could not patch meta visibility declaration in meta source')
        text = text.replace(old, new, 1)

    old = "    grid.querySelectorAll(':scope > .buildCard').forEach(card=>{card.hidden=card.dataset.role!==wanted;});\n"
    new = "    grid.querySelectorAll(':scope > .buildCard').forEach(card=>{\n      const wrongActivity=card.dataset.role!==wanted;\n      const wrongGuardianRole=cls==='Guardian'&&card.dataset.guardianRole!==guardianMode;\n      card.hidden=wrongActivity||wrongGuardianRole;\n    });\n"
    if old in text:
        text = text.replace(old, new, 1)

    # The click handler is generated by patch_inject() rather than living in META_JS.
    if "const guardianBtn=e.target.closest?.('[data-guardian-mode]');" not in text:
        old = "    new = old + \"\\n    root?.addEventListener('click',e=>{\\n      const modeBtn=e.target.closest?.('[data-meta-mode]');\\n      if(modeBtn){metaWrite('sxs-build-meta-mode',modeBtn.dataset.metaMode);applyMetaVisibility(activeClass());return;}\\n      const sizeBtn=e.target.closest?.('[data-tournament-size]');\\n      if(sizeBtn){metaWrite('sxs-build-tournament-size',sizeBtn.dataset.tournamentSize);applyMetaVisibility(activeClass());}\\n    });\""
        new = "    new = old + \"\\n    root?.addEventListener('click',e=>{\\n      const guardianBtn=e.target.closest?.('[data-guardian-mode]');\\n      if(guardianBtn&&activeClass()==='Guardian'){metaWrite('sxs-build-guardian-mode',guardianBtn.dataset.guardianMode==='dps'?'dps':'tank');applyMetaVisibility('Guardian');queueApply();return;}\\n      const modeBtn=e.target.closest?.('[data-meta-mode]');\\n      if(modeBtn){metaWrite('sxs-build-meta-mode',modeBtn.dataset.metaMode);applyMetaVisibility(activeClass());return;}\\n      const sizeBtn=e.target.closest?.('[data-tournament-size]');\\n      if(sizeBtn){metaWrite('sxs-build-tournament-size',sizeBtn.dataset.tournamentSize);applyMetaVisibility(activeClass());}\\n    });\""
        if old not in text:
            raise RuntimeError('Could not patch generated click handler in meta source')
        text = text.replace(old, new, 1)

    if 'GUARDIAN_ROLE_TOGGLE_V1' not in text or 'data-guardian-mode' not in text:
        raise RuntimeError('Guardian meta source patch incomplete')
    return text


def patch_rich(text: str) -> str:
    if GUARDIAN_PROFILE_OLD in text:
        text = text.replace(GUARDIAN_PROFILE_OLD, GUARDIAN_PROFILE_NEW, 1)
    elif GUARDIAN_PROFILE_NEW not in text:
        raise RuntimeError('Could not replace Guardian stat profile')

    if 'const GUARDIAN_PRIORITY=' not in text:
        anchor = '  const DOMINATOR_PRIORITY={\n'
        if anchor not in text:
            raise RuntimeError('Could not find Dominator priority anchor')
        text = text.replace(anchor, GUARDIAN_PRIORITY + anchor, 1)

    old = "  const roleMode=()=>{\n    try{return localStorage.getItem('sxs-build-dominator-mode')==='heals'?'heals':'dps';}catch(_){return 'dps';}\n  };"
    new = "  const roleMode=cls=>{\n    try{\n      if(cls==='Guardian') return localStorage.getItem('sxs-build-guardian-mode')==='dps'?'dps':'tank';\n      return localStorage.getItem('sxs-build-dominator-mode')==='heals'?'heals':'dps';\n    }catch(_){return cls==='Guardian'?'tank':'dps';}\n  };"
    if old in text:
        text = text.replace(old, new, 1)

    if "if(cls==='Guardian'){" not in text.split("if(cls==='Dominator'){",1)[0]:
        anchor = "  function ensurePriorityPair(host,cls,mode){\n    if(cls==='Dominator'){"
        guardian_branch = "  function ensurePriorityPair(host,cls,mode){\n    if(cls==='Guardian'){\n      [...host.children].filter(el=>el.classList?.contains('priorityPanel')).forEach(el=>el.remove());\n      let pair=host.querySelector(':scope > .priorityPair');\n      if(!pair){\n        pair=document.createElement('div');\n        pair.className='priorityPair';\n        const grid=host.querySelector(':scope > .buildGrid');\n        if(grid) grid.before(pair); else host.append(pair);\n      }\n      if(pair.dataset.guardianMode!==mode){\n        pair.innerHTML='';\n        const data=GUARDIAN_PRIORITY[mode]||GUARDIAN_PRIORITY.tank;\n        pair.append(makePanel(data[0]),makePanel(data[1]));\n        pair.dataset.guardianMode=mode;\n      }\n      return;\n    }\n    if(cls==='Dominator'){"
        if anchor not in text:
            raise RuntimeError('Could not add Guardian priority branch')
        text = text.replace(anchor, guardian_branch, 1)

    text = text.replace("    const mode=cls==='Dominator'?roleMode():'dps';", "    const mode=(cls==='Dominator'||cls==='Guardian')?roleMode(cls):'dps';", 1)
    text = text.replace("host?.addEventListener('click',e=>{if(e.target.closest?.('[data-dominator-mode]')) setTimeout(()=>{if(host) host.dataset.richBuildSig='';queue();},0);});", "host?.addEventListener('click',e=>{if(e.target.closest?.('[data-dominator-mode],[data-guardian-mode]')) setTimeout(()=>{if(host) host.dataset.richBuildSig='';queue();},0);});", 1)

    # Make restore validation explicitly require the maintained Guardian toggle.
    if "'GUARDIAN_ROLE_TOGGLE_V1'" not in text:
        text = text.replace("    'META_BUILD_MODES_V1',\n", "    'META_BUILD_MODES_V1',\n    'GUARDIAN_ROLE_TOGGLE_V1',\n", 1)
    return text


def patch_roll(text: str) -> str:
    old = "    Guardian:['block','blockpair','def','spd','hp','defpct','spdpct','hppct'],"
    new = "    Guardian:{\n      tank:['block','blockpair','def','spd','hp','defpct','spdpct','hppct'],\n      dps:['block','blockpair','crit','critdmg','spd','spdpct','atk','atkpct','em']\n    },"
    if old in text:
        text = text.replace(old, new, 1)

    old = "  const role=()=>{try{return localStorage.getItem('sxs-build-dominator-mode')==='heals'?'heals':'dps'}catch(_){return 'dps'}};"
    new = "  const role=cls=>{try{if(cls==='Guardian')return localStorage.getItem('sxs-build-guardian-mode')==='dps'?'dps':'tank';return localStorage.getItem('sxs-build-dominator-mode')==='heals'?'heals':'dps'}catch(_){return cls==='Guardian'?'tank':'dps'}};"
    if old in text:
        text = text.replace(old, new, 1)

    old = "    const keys=cls==='Dominator'?PROFILES.Dominator[mode]:PROFILES[cls];"
    new = "    const profile=PROFILES[cls];\n    const keys=Array.isArray(profile)?profile:profile?.[mode];"
    if old in text:
        text = text.replace(old, new, 1)

    old = "    const label=cls==='Dominator'?`${cls} · ${mode==='heals'?'Heals':'DPS'}`:cls;"
    new = "    const label=cls==='Dominator'?`${cls} · ${mode==='heals'?'Heals':'DPS'}`:cls==='Guardian'?`${cls} · ${mode==='dps'?'DPS':'Tank'}`:cls;"
    if old in text:
        text = text.replace(old, new, 1)

    old = "    const cls=activeClass(),mode=cls==='Dominator'?role():'dps',sig=cls+'|'+mode;"
    new = "    const cls=activeClass(),mode=(cls==='Dominator'||cls==='Guardian')?role(cls):'dps',sig=cls+'|'+mode;"
    if old in text:
        text = text.replace(old, new, 1)

    text = text.replace("host?.addEventListener('click',e=>{if(e.target.closest?.('[data-dominator-mode]'))setTimeout(queue,0)});", "host?.addEventListener('click',e=>{if(e.target.closest?.('[data-dominator-mode],[data-guardian-mode]'))setTimeout(queue,0)});", 1)
    return text


def patch_guardian_summary(text: str) -> str:
    text = text.replace('<div class=\\"guideSummary\\"><div><span>Tank / support / bruiser</span><strong>Guardian</strong><p>T4 finally gives Knight real taunt tools plus stronger Water/Light offense. The long-term identity is still protection: Block, DEF, shields, taunt control and party support.</p></div>', '<div class=\\"guideSummary\\"><div><span>Tank / Water DPS / support</span><strong>Guardian</strong><p>T4 Guardian can be a true frontline or an offensive Water/counter bruiser. Use the Tank / DPS toggle to keep the same activity categories while changing the job you want the class to perform.</p></div>', 1)
    return text


# Generated/runtime sources.
for path in (INDEX, INJECT):
    text = path.read_text(encoding='utf-8')
    text = replace_guardian_block_runtime(text)
    text = patch_build_helpers(text)
    text = patch_meta_runtime(text)
    if path == INDEX:
        text = patch_guardian_summary(text)
        text = patch_rich(text)
        text = patch_roll(text)
    path.write_text(text, encoding='utf-8')

# Maintained patch sources, so future restores/reapplications cannot revert the toggle.
text = META_SRC.read_text(encoding='utf-8')
text = patch_meta_source(text)
META_SRC.write_text(text, encoding='utf-8')

text = RICH_SRC.read_text(encoding='utf-8')
text = patch_rich(text)
RICH_SRC.write_text(text, encoding='utf-8')

text = ROLL_SRC.read_text(encoding='utf-8')
text = patch_roll(text)
ROLL_SRC.write_text(text, encoding='utf-8')

# Final marker validation.
for path in (INDEX, INJECT):
    text = path.read_text(encoding='utf-8')
    required = [MARK, "role('Dungeon · Tank'", "role('Dungeon · DPS'", 'data-guardian-mode', 'data-guardian-role']
    for token in required:
        if token not in text:
            raise RuntimeError(f'{path}: missing Guardian toggle token {token}')

print('Installed Guardian Tank/DPS toggle with activity-specific meta builds, role stats, priorities and Roll-guide profiles')
