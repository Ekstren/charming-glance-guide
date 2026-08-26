from pathlib import Path
import re

p=Path('index.html')
text=p.read_text(encoding='utf-8')

# Remove any prior cleanup override so this stays idempotent.
text=re.sub(r'\n?<!-- COMPANION_CURRENT_SEASON_CSS_START -->.*?<!-- COMPANION_CURRENT_SEASON_CSS_END -->\n?', '\n', text, flags=re.S)

# Companion progression follows the live server season; there is no manual S1/S2 selector here.
text,n=re.subn(
    r'\n\s*<div class="companionSeasonToggle" id="companionSeasonToggle".*?</div>\n',
    '\n',text,count=1,flags=re.S
)
if n!=1:
    raise SystemExit(f'Expected one companion season toggle, found {n}')

text=text.replace(
    '<p>Level the companions that give your class the right passive stats at the important Affinity breakpoints. Companion Affinity survives seasonal resets, so S1 investment carries directly into S2.</p>',
    '<p>Level the companions that give your class the right passive stats at the important Affinity breakpoints. Focus gifts where they create the most permanent account power.</p>'
)

# Compact header styling and role toggle beside the Sage class title.
css='''<!-- COMPANION_CURRENT_SEASON_CSS_START -->
<style id="companion-current-season-v1">
.companionTop{grid-template-columns:1fr!important}
.companionTitleRow{display:flex;align-items:center;justify-content:space-between;gap:14px;margin-top:4px}
.companionTitleRow h2{margin:0!important}
.companionTitleRow .companionRoleToggle{flex:0 0 auto}
@media(max-width:560px){.companionTitleRow{align-items:flex-start;gap:10px}.companionTitleRow .companionRoleToggle{margin-top:-2px}}
</style>
<!-- COMPANION_CURRENT_SEASON_CSS_END -->'''
marker='<!-- COMPANION_GUIDE_CSS_END -->'
if marker not in text:
    raise SystemExit('Companion CSS marker not found')
text=text.replace(marker,css+'\n'+marker,1)

# Live season is determined only by the Charming Glance rollover, not the Builds manual preview toggle.
text=text.replace("  const seasonStorage='sxs-companion-season';\n",'')
text=text.replace(
"  function defaultSeason(){\n    try{ if(typeof buildSeasonKey==='function') return buildSeasonKey()==='s2'?'s2':'s1'; }catch(_){}\n    return Date.now()>=new Date('2026-08-30T06:00:00-07:00').getTime()?'s2':'s1';\n  }",
"  function defaultSeason(){\n    return Date.now()>=new Date('2026-08-30T06:00:00-07:00').getTime()?'s2':'s1';\n  }"
)

old_load="""  function loadPrefs(){
    currentSeason=defaultSeason();
    try{
      const s=localStorage.getItem(seasonStorage); if(s==='s1'||s==='s2') currentSeason=s;
      const r=localStorage.getItem(roleStorage); if(r==='dps'||r==='heals') sageRole=r;
    }catch(_){}
    const list=currentSeason==='s2'?S2_CLASSES:S1_CLASSES;
    let saved=''; try{saved=localStorage.getItem(classStorage[currentSeason])||'';}catch(_){}
    currentClass=list.includes(saved)?saved:list[0];
  }
  function savePrefs(){
    try{localStorage.setItem(seasonStorage,currentSeason);localStorage.setItem(classStorage[currentSeason],currentClass);localStorage.setItem(roleStorage,sageRole);}catch(_){}
  }"""
new_load="""  function loadPrefs(){
    currentSeason=defaultSeason();
    try{
      const r=localStorage.getItem(roleStorage); if(r==='dps'||r==='heals') sageRole=r;
    }catch(_){}
    const list=currentSeason==='s2'?S2_CLASSES:S1_CLASSES;
    let saved=''; try{saved=localStorage.getItem(classStorage[currentSeason])||'';}catch(_){}
    currentClass=list.includes(saved)?saved:list[0];
  }
  function savePrefs(){
    try{localStorage.setItem(classStorage[currentSeason],currentClass);localStorage.setItem(roleStorage,sageRole);}catch(_){}
  }"""
if old_load not in text:
    raise SystemExit('Companion preference block not found')
text=text.replace(old_load,new_load,1)

# Strip seasonal language from S2 class summaries; the visible guide is simply for the current class.
text=text.replace("Conqueror continues the Berserker companion plan. Do not restart your roster in S2: the same Crit-first investment remains useful, with Accuracy following for consistency.","Conqueror wants the same Crit-first offensive progression: establish the best Crit breakpoints first, then add Accuracy for consistency.")
text=text.replace("Guardian remains a Block-first class. Continue the Paladin defensive roster, then branch into offensive companions only if you are deliberately building Water/offensive Guardian.","Guardian is a Block-first class. Build the strongest Block breakpoints first, then branch into offensive companions only if you deliberately play Water/offensive Guardian.")
text=text.replace("Destroyer keeps the Archmage Crit-first plan. The Fire branch especially likes reliable Crits, while Accuracy remains the next best Companion-side consistency stat.","Destroyer is Crit-first. The Fire branch especially likes reliable Crits, while Accuracy remains the next best Companion-side consistency stat.")
text=text.replace("Dominator keeps the Sage split: Accuracy/Crit for damage, or a dedicated Lv100 Healing Boost push for support. Your Arcanist Affinity investment carries straight across.","Dominator has two real paths: Accuracy/Crit for damage, or a dedicated Lv100 Healing Boost push for support.")

# Render only the live-season class list, with the DPS/Heals toggle beside Arcanist/Dominator's name.
text=text.replace("    document.querySelectorAll('[data-companion-season]').forEach(b=>{const a=b.dataset.companionSeason===currentSeason;b.classList.toggle('active',a);b.setAttribute('aria-pressed',String(a));});\n",'')
old_role="""    const roleRow=isSage?`<div class="companionRoleRow"><div class="companionRoleToggle" role="group" aria-label="${currentClass} companion role"><button type="button" data-companion-role="dps" class="${sageRole==='dps'?'active':''}">DPS</button><button type="button" data-companion-role="heals" class="${sageRole==='heals'?'active':''}">Heals</button></div></div>`:'';
    const carry=meta.carry?`<div class="companionCarry"><b>S2 carryover:</b> ${meta.carry}</div>`:'';"""
new_role="""    const roleToggle=isSage?`<div class="companionRoleToggle" role="group" aria-label="${currentClass} companion role"><button type="button" data-companion-role="dps" class="${sageRole==='dps'?'active':''}">DPS</button><button type="button" data-companion-role="heals" class="${sageRole==='heals'?'active':''}">Heals</button></div>`:'';"""
if old_role not in text:
    raise SystemExit('Companion role row block not found')
text=text.replace(old_role,new_role,1)

old_hero='''        <div class="companionHeroMain"><span>${meta.season.toUpperCase()} · ${meta.line}</span><h2>${currentClass}</h2><p>${meta.summary}</p></div>'''
new_hero='''        <div class="companionHeroMain"><span>${meta.line}</span><div class="companionTitleRow"><h2>${currentClass}</h2>${roleToggle}</div><p>${meta.summary}</p></div>'''
if old_hero not in text:
    raise SystemExit('Companion hero block not found')
text=text.replace(old_hero,new_hero,1)
text=text.replace('      ${carry}${roleRow}\n','',1)

season_listener="    $c('companionSeasonToggle')?.addEventListener('click',e=>{const b=e.target.closest('[data-companion-season]');if(!b)return;currentSeason=b.dataset.companionSeason;const list=currentSeason==='s2'?S2_CLASSES:S1_CLASSES;let saved='';try{saved=localStorage.getItem(classStorage[currentSeason])||'';}catch(_){}currentClass=list.includes(saved)?saved:list[0];render();});\n"
if season_listener not in text:
    raise SystemExit('Companion season listener not found')
text=text.replace(season_listener,'',1)

p.write_text(text,encoding='utf-8')
print('Applied live-season Companion layout cleanup')
