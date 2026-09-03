from pathlib import Path
import re

INDEX=Path('index.html')
INJECT=Path('.github/build-fantomons-inject.html')
META=Path('scripts/patch_meta_build_modes_v1.py')
GUARDIAN=Path('scripts/patch_guardian_tank_dps_toggle_v1.py')
TOOLTIPS=Path('scripts/patch_build_skill_tooltips_v1.py')
COMPANION=Path('.github/patch-companion-current-season.py')
START='<!-- BUILD_FANTOMON_PAIRS_START -->'
END='<!-- BUILD_FANTOMON_PAIRS_END -->'
MARK='T4_CLASS_ORDER_DOMINATOR_ROLES_V1'

ORDER_OLD="['Conqueror','Guardian','Destroyer','Dominator']"
ORDER_NEW="['Destroyer','Dominator','Conqueror','Guardian']"

DOM_BLOCK=r'''    Dominator:[
      role('Dungeon · DPS','AoE Dark / Erosion clear',['Mana Blast','Dark Bullet','Abyssal Hand','Shadow Impact'],['Shadow Vengeance',"Night's Blessing",'Shadow Erosion','Linked Misfortune'],'Use the published T4 AoE core for dungeon packs. It keeps all four slots contributing damage instead of dragging the healer bar into a DPS role.','If Erosion is landing poorly, improve Effect Hit Rate before replacing the whole shell. Nyxarchon is the damage lead.','Prydwen AoE core'),
      role('Crucible / Conquest · DPS','Single-target direct / Erosion hybrid',['Dark Bullet','Dark Starburst','Chaos Rune','Shadow of Termination'],['Shadow Vengeance',"Night's Blessing",'Shadow Erosion','Linked Misfortune'],'This is the published T4 single-target core: Starburst + Chaos Rune give reliable direct damage while Termination preserves Erosion payoff. With high Effect Hit Rate, Chaos Rune → Mana Blast raises the Erosion ceiling.','If a much stronger carry is in the party, Heals mode’s Decoy + Frenzy + Mantra support setup can produce more team score than selfish DPS.','Prydwen ST core'),
      role('Arena · DPS','Single-target Dark pressure',['Dark Bullet','Dark Starburst','Chaos Rune','Shadow of Termination'],['Shadow Vengeance',"Night's Blessing",'Shadow Erosion','Linked Misfortune'],'Arena is one target, so use the actual single-target shell instead of spending a slot on broad Abyssal Hand AoE. High Effect Hit Rate: Chaos Rune → Mana Blast.','If your current Chaos Rune is badly under-ranked or unreliable, test a direct-damage flex rather than forcing it. PvP healing is heavily reduced, so DPS is the normal Arena default.','Prydwen ST + PvP logic'),
      role('Tournament · 2v2 · DPS','Duo kill pressure + revive',['Dark Bullet','Dark Starburst','Chaos Rune','Shadow of Termination'],['Shadow Vengeance','Shadow Erosion','Linked Misfortune','Resurrection'],'Keep the compact single-target damage shell but reserve one Charm slot for Resurrection; reviving your only teammate can swing an entire 2v2 round.','If your partner is the true carry, switch to Heals mode for the support variant rather than weakening this DPS bar with half a support kit.','ST core + PvP synthesis'),
      role('Tournament · 4v4 · DPS','AoE Dark pressure + revive',['Mana Blast','Dark Bullet','Abyssal Hand','Shadow Impact'],['Shadow Vengeance','Shadow Erosion','Linked Misfortune','Resurrection'],'Four enemy bodies finally justify the full AoE/Erosion shell. Resurrection replaces the selfish fourth damage Charm because its team-fight swing is unusually high.','If your comp is built around a hypercarry, Heals mode’s Decoy/Frenzy/Mantra support bar can be more valuable than personal damage.','Prydwen AoE + PvP synthesis'),
      role('Dungeon · Heals','Hard-dungeon healer',['Waterling Summon','Rejuvenating Rain','Radiant Restoration','Frenzy Totem'],['Phantom Light','Healing Mastery','Overhealing','Resurrection'],'This is the published T4 healer core. Need more raw healing: Frenzy Totem → Healing Touch. If nobody is dying, Resurrection → Mantra of Blessings.','Phantom Light is mandatory for the dedicated healer shell. Mandragora is the pure-healing lead until Pandarial is live and validated.','Prydwen healer core'),
      role('Crucible / Conquest · Heals','Hypercarry support / boss score',['Radiant Restoration','Decoy Clone','Frenzy Totem','Dark Bullet'],['Phantom Light','Healing Mastery','Overhealing','Mantra of Blessings'],'Large-group boss content is where Dominator should often stop chasing its own recount: Decoy + Frenzy + Mantra amplify the strongest carry while Radiant Restoration keeps one efficient heal available.','Only one Decoy can attach effectively and positioning matters. If your team already massively overkills the boss, DPS mode can be better; otherwise this is the support-first score bar.','Prydwen + Global support testing'),
      role('Arena · Heals','Specialist sustain hybrid',['Rejuvenating Rain','Radiant Restoration','Dark Bullet','Shadow of Termination'],['Phantom Light','Healing Mastery','Shadow Vengeance','Mantra of Blessings'],'Healing is reduced in PvP, so this is intentionally a hybrid rather than a full four-heal bar: enough sustain to exploit a real Healing Boost/SPD set while retaining kill pressure.','Only use Heals mode in Arena when your healing gear is genuinely optimized. Otherwise the DPS Arena card is the stronger default.','PvP specialist synthesis'),
      role('Tournament · 2v2 · Heals','Duo sustain / carry support',['Rejuvenating Rain','Radiant Restoration','Frenzy Totem','Dark Bullet'],['Phantom Light','Healing Mastery','Resurrection','Shadow Vengeance'],'Keep the partner alive, buff their output, and retain Resurrection as the highest-impact team utility. One Dark attack prevents the bar from becoming dead weight between heals.','PvP healing is reduced; if your Healing Boost/SPD cannot overcome that penalty, use DPS mode and keep Resurrection there instead.','PvP support synthesis'),
      role('Tournament · 4v4 · Heals','Hybrid team support',['Radiant Restoration','Decoy Clone','Frenzy Totem','Dark Bullet'],['Phantom Light','Healing Mastery','Resurrection','Mantra of Blessings'],'4v4 rewards buffs, Decoy pressure and Resurrection more than raw healing spam. This is the support-oriented Tournament bar, not a pure healer.','If your gear is exceptionally healing-focused, Mantra can flex to Overhealing. Otherwise keep the team-damage support because PvP healing is reduced.','Global team-PvP synthesis')
    ]'''


def replace_dom_runtime(text:str)->str:
    pat=re.compile(r"    Dominator:\[\n.*?\n    \](?=\n  \};)",re.S)
    out,n=pat.subn(DOM_BLOCK,text,count=1)
    if n!=1:
        if "role('Dungeon · DPS','AoE Dark / Erosion clear'" in text:return text
        raise RuntimeError('Could not replace runtime Dominator block')
    return out


def replace_dom_meta_source(text:str)->str:
    pat=re.compile(r"'Dominator': r'''    Dominator:\[\n.*?\n    \]'''",re.S)
    out,n=pat.subn("'Dominator': r'''"+DOM_BLOCK+"'''",text,count=1)
    if n!=1:
        if "role('Dungeon · DPS','AoE Dark / Erosion clear'" in text:return text
        raise RuntimeError('Could not replace maintained Dominator block')
    return out


def generic_role_cards(text:str)->str:
    # Guardian's original helper was class-specific. Generalize the same metadata so
    # Dominator DPS/Heals can select role-specific cards without changing card titles.
    pat=re.compile(r"  function buildCardHtml\(r\)\{.*?\n  \}\n  function applyRoleLoadouts",re.S)
    repl=r'''  function buildCardHtml(r){
    const rm=String(r.name||'').match(/^(.*?) · (Tank|DPS|Heals)$/);
    const displayName=rm?rm[1]:r.name;
    const roleAttr=rm?' data-build-role="'+rm[2].toLowerCase()+'"':'';
    return '<article class="buildCard" data-role="'+esc(displayName)+'"'+roleAttr+'>'
      +'<header><div><h3>'+esc(displayName)+'<span class="roleBadge">'+esc(r.confidence)+'</span></h3><p>'+esc(r.subtitle)+'</p></div></header>'
      +'<div class="skillGroup"><span>Techniques</span><div>'+r.techniques.map(x=>'<b>'+esc(x)+'</b>').join('')+'</div></div>'
      +'<div class="skillGroup"><span>Charms</span><div>'+r.charms.map(x=>'<b>'+esc(x)+'</b>').join('')+'</div></div>'
      +'<ul><li><b>Offensive:</b> '+esc(r.offensive)+'</li><li><b>Defensive:</b> '+esc(r.defensive)+'</li></ul>'
      +'</article>';
  }
  function applyRoleLoadouts'''
    out,n=pat.subn(repl,text,count=1)
    if n!=1:
        if 'data-build-role' in text:return text
        raise RuntimeError('Could not generalize build card role metadata')
    return out


def patch_meta_runtime(text:str)->str:
    if "const dominatorBuildMode=()=>" not in text:
        anchor="  const guardianBuildMode=()=>metaRead('sxs-build-guardian-mode','tank')==='dps'?'dps':'tank';\n"
        if anchor not in text: raise RuntimeError('guardianBuildMode anchor missing')
        text=text.replace(anchor,anchor+"  const dominatorBuildMode=()=>metaRead('sxs-build-dominator-mode','dps')==='heals'?'heals':'dps';\n",1)

    old="    const mode=metaMode(), size=metaTournamentSize(), guardianMode=guardianBuildMode();"
    new="    const mode=metaMode(), size=metaTournamentSize(), guardianMode=guardianBuildMode(), dominatorMode=dominatorBuildMode();"
    if old in text:text=text.replace(old,new,1)
    elif new not in text:raise RuntimeError('applyMetaVisibility mode anchor missing')

    old="    document.querySelectorAll('.builds .guardianModeTabs [data-guardian-mode]').forEach(b=>{const on=b.dataset.guardianMode===guardianMode;b.classList.toggle('active',on);b.setAttribute('aria-pressed',String(on));});"
    new=old+"\n    document.querySelectorAll('.builds .dominatorModeTabs [data-dominator-mode]').forEach(b=>{const on=b.dataset.dominatorMode===dominatorMode;b.classList.toggle('active',on);b.setAttribute('aria-pressed',String(on));});"
    if "dominatorModeTabs [data-dominator-mode]" not in text:
        if old not in text:raise RuntimeError('role tab sync anchor missing')
        text=text.replace(old,new,1)

    old="      const wrongGuardianRole=cls==='Guardian'&&card.dataset.guardianRole!==guardianMode;\n      card.hidden=wrongActivity||wrongGuardianRole;"
    new="      const selectedRole=cls==='Guardian'?guardianMode:(cls==='Dominator'?dominatorMode:'');\n      const wrongRole=(cls==='Guardian'||cls==='Dominator')&&card.dataset.buildRole!==selectedRole;\n      card.hidden=wrongActivity||wrongRole;"
    if old in text:text=text.replace(old,new,1)
    elif new not in text:
        # Also support a partially generalized Guardian helper.
        old2="      const wrongGuardianRole=cls==='Guardian'&&card.dataset.buildRole!==guardianMode;\n      card.hidden=wrongActivity||wrongGuardianRole;"
        if old2 in text:text=text.replace(old2,new,1)
        else:raise RuntimeError('role filter anchor missing')

    if "const dominatorBtn=e.target.closest?.('[data-dominator-mode]');" not in text:
        anchor="      if(guardianBtn&&activeClass()==='Guardian'){metaWrite('sxs-build-guardian-mode',guardianBtn.dataset.guardianMode==='dps'?'dps':'tank');applyMetaVisibility('Guardian');queueApply();return;}\n"
        add=anchor+"      const dominatorBtn=e.target.closest?.('[data-dominator-mode]');\n      if(dominatorBtn&&activeClass()==='Dominator'){metaWrite('sxs-build-dominator-mode',dominatorBtn.dataset.dominatorMode==='heals'?'heals':'dps');applyMetaVisibility('Dominator');queueApply();return;}\n"
        if anchor not in text:raise RuntimeError('Guardian click anchor missing')
        text=text.replace(anchor,add,1)
    return text


def patch_guardian_source(text:str)->str:
    text=text.replace("match(/^(.*?) · (Tank|DPS)$/)","match(/^(.*?) · (Tank|DPS|Heals)$/)")
    text=text.replace("const guardianAttr=gm?' data-guardian-role=\"'+gm[2].toLowerCase()+'\"':'';","const roleAttr=gm?' data-build-role=\"'+gm[2].toLowerCase()+'\"':'';")
    text=text.replace("+guardianAttr+'>'","+roleAttr+'>'")
    text=text.replace("card.dataset.guardianRole!==guardianMode","card.dataset.buildRole!==guardianMode")
    text=text.replace("data-guardian-role","data-build-role")
    return text


def patch_tooltip_source(text:str)->str:
    if "'Chaos Rune':I(" in text:return text
    anchor="    'Dark Bullet':I('Reliable Dark attack used to apply/maintain Erosion pressure.','Cheap, consistent glue for both DPS and support bars that still want debuff value.','Dark · Erosion'),\n"
    if anchor not in text:raise RuntimeError('Dominator tooltip insertion anchor missing')
    additions=(
"    'Mana Blast':I('Dark/Erosion attack used to build the higher-ceiling damage-over-time plan.','Core in AoE and becomes the high-Effect-Hit-Rate single-target flex over Chaos Rune.','Dark · Erosion'),\n"
"    'Chaos Rune':I('Direct-damage Dark Technique used in the published T4 single-target hybrid so damage is less dependent on Erosion landing.','Best when Effect Hit Rate is not high enough to justify going all-in on Erosion; high EHR can flex it to Mana Blast.','Dark · Direct damage · ST'),\n"
"    'Shadow Impact':I('Broad Dark AoE payoff carried forward for T4 because Dominator receives no new dedicated AoE replacement.','The fourth Technique in the published Dungeon/4v4 AoE shell where multiple targets justify its coverage.','Dark · AoE'),\n"
    )
    return text.replace(anchor,additions+anchor,1)


def patch_companion_source(text:str)->str:
    if ORDER_NEW in text:return text
    needle="text=p.read_text(encoding='utf-8')\n"
    if needle not in text:raise RuntimeError('Companion current-season read anchor missing')
    return text.replace(needle,needle+f"text=text.replace(\"  const S2_CLASSES={ORDER_OLD};\",\"  const S2_CLASSES={ORDER_NEW};\")\n",1)

# 1) Maintained build injection and meta source.
inject=INJECT.read_text(encoding='utf-8')
inject=replace_dom_runtime(inject)
inject=generic_role_cards(inject)
inject=patch_meta_runtime(inject)
INJECT.write_text(inject,encoding='utf-8')

meta=META.read_text(encoding='utf-8')
meta=replace_dom_meta_source(meta)
meta=patch_meta_runtime(meta)
# Keep the explanatory legacy-filter comment accurate.
meta=meta.replace('The old Dominator DPS/Heals toggle should continue to control stat/priority\n    # panels, but activity-driven loadout cards must not be hidden by that role toggle.',
                  'The old detached Dominator card filter stays disabled; META_BUILD_MODES_V1 now\n    # owns both activity and DPS/Heals card visibility while the base toggle owns stats.')
meta=meta.replace('// Loadout cards are activity-driven by META_BUILD_MODES_V1; the Dominator DPS/Heals toggle only changes stat/priority panels.',
                  '// Dominator loadout cards are role/activity-driven by META_BUILD_MODES_V1; legacy detached card filtering stays disabled.')
META.write_text(meta,encoding='utf-8')

# 2) Guardian source must not restore class-specific card metadata later.
GUARDIAN.write_text(patch_guardian_source(GUARDIAN.read_text(encoding='utf-8')),encoding='utf-8')

# 3) Add tooltip definitions for newly surfaced Dominator ST/AoE skills.
TOOLTIPS.write_text(patch_tooltip_source(TOOLTIPS.read_text(encoding='utf-8')),encoding='utf-8')

# 4) Rebuild the live build injection from the maintained copy, then update visual class order.
index=INDEX.read_text(encoding='utf-8')
a=index.find(START); b=index.find(END,a)
if a<0 or b<0:raise RuntimeError('Live build injection markers missing')
b+=len(END)
index=index[:a]+inject.strip()+index[b:]
index=index.replace(f"const S2_BUILD_CLASSES={ORDER_OLD};",f"const S2_BUILD_CLASSES={ORDER_NEW};")
index=index.replace(f"const S2_CLASSES={ORDER_OLD};",f"const S2_CLASSES={ORDER_NEW};")
if f"const S2_BUILD_CLASSES={ORDER_NEW};" not in index:raise RuntimeError('Build class order did not land')
if f"const S2_CLASSES={ORDER_NEW};" not in index:raise RuntimeError('Companion class order did not land')
INDEX.write_text(index,encoding='utf-8')

# Normalize future Companion rebuilds to the same in-game class-path order.
COMPANION.write_text(patch_companion_source(COMPANION.read_text(encoding='utf-8')),encoding='utf-8')

print('Reordered T4 classes and made Dominator DPS/Heals activity builds role-specific')
