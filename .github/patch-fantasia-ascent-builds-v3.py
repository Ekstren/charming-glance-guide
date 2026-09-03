from pathlib import Path
import re
import subprocess

# Apply the base Fantasia patch, then ensure every live preset copy receives the
# new cards and move Tournament-size selection into the Tournament card itself.
subprocess.run(['python','.github/patch-fantasia-ascent-builds-v1.py'],check=True)

targets=[Path('index.html'),Path('.github/build-fantomons-inject.html')]

roles={
'Conqueror':["      role('Fantasia Ascent','Solo push: high-DEF floors and mixed packs',['Gale Dance','Flash Fire','Flickering Blade','Blade Storm'],['Piercing Assault','Tactical Adaptation','Soul Splash','Indomitable Will'],'Gale Dance improves opening tempo while the T4 damage core handles mixed floors.','Soul Splash + Indomitable Will give the push setup enough sustain for above-power stages.','Community Ascent')"],
'Guardian':[
"      role('Fantasia Ascent · Tank','Solo push: Block / reflect survival',['Luminous Shield','Forceful Charge','Star Shattering Slash','Desperate Protection'],['Rebound','Holy Aegis','Block Mastery','Soul Protection'],'Luminous Shield and Desperate Protection stabilize hard floors while Rebound turns repeated hits into damage.','Forceful Charge keeps contact and Star Shattering Slash gives the tank setup a real finisher.','Community Ascent')",
"      role('Fantasia Ascent · DPS','Solo push: Water AoE with a safety slot',['Swirling Blade','Lunarwater Threads','Seismic Tide','Raging Maelstrom'],['Frigid Aura','Defensive Assault','Frigid Glint','Potential Rebirth'],'The Water/Cold package clears dense floors while Swirling Blade adds its own shield.','Potential Rebirth keeps the damage setup from folding to a bad burst window.','Prydwen + Ascent')"],
'Destroyer':["      role('Fantasia Ascent','Solo push: mixed damage with Void Bubble safety',['Formation Breaker','Meteoric Flames','Wind Blade Spiral','Thunder of Judgment'],['Rapid Cast','Void Bubble','Cyclone Lament','Radiant Sear'],'Formation Breaker keeps tempo high while Fire, Wind, and Light coverage handles varied floors.','Void Bubble is the default safety slot for pushing above listed power.','Guide-derived Ascent')"],
'Dominator':[
"      role('Fantasia Ascent · DPS','Solo push: Erosion AoE with Shadow Vengeance safety',['Mana Blast','Dark Bullet','Abyssal Hand','Shadow Impact'],['Shadow Vengeance',\"Night's Blessing\",'Shadow Erosion','Linked Misfortune'],'The AoE Erosion package handles mixed floors and Shadow Vengeance buys time to finish dangerous waves.','Effect Hit Rate still matters whenever the floor depends on Erosion sticking.','Community Ascent')",
"      role('Fantasia Ascent · Heals','Solo push: sustain hybrid for Healing Boost builds',['Rejuvenating Rain','Radiant Restoration','Dark Bullet','Shadow of Termination'],['Phantom Light','Healing Mastery','Shadow Vengeance','Mantra of Blessings'],'Rejuvenating Rain + Radiant Restoration sustain the run while Dark Bullet and Shadow of Termination preserve kill pressure.','Best for accounts already invested into Healing Boost and SPD.','Ascent sustain')"]
}

def add_roles(text,cls,next_cls,entries):
    if next_cls:
        pat=re.compile(rf"(    {re.escape(cls)}:\[\n)(.*?)(\n    \],\n    {re.escape(next_cls)}:\[)",re.S)
    else:
        pat=re.compile(rf"(    {re.escape(cls)}:\[\n)(.*?)(\n    \]\n  \}};)",re.S)
    seen=0
    def repl(m):
        nonlocal seen
        seen+=1
        body=m.group(2)
        if "role('Fantasia Ascent" in body:
            return m.group(0)
        return m.group(1)+body.rstrip()+',\n'+',\n'.join(entries)+m.group(3)
    text=pat.sub(repl,text)
    if seen<1:
        raise SystemExit(f'missing {cls} ROLE_PRESETS block')
    return text

for path in targets:
    text=path.read_text(encoding='utf-8')
    for cls,next_cls in [('Conqueror','Guardian'),('Guardian','Destroyer'),('Destroyer','Dominator'),('Dominator',None)]:
        text=add_roles(text,cls,next_cls,roles[cls])

    text=text.replace('.builds .metaBuildTabs{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:5px;flex:1;min-width:0}',
                      '.builds .metaBuildTabs{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:5px;flex:1;min-width:0}')
    text=text.replace("const META_MODES=['Dungeon','Crucible / Conquest','Arena','Tournament'];",
                      "const META_MODES=['Dungeon','Crucible / Conquest','Arena','Fantasia Ascent','Tournament'];")
    text=text.replace("    if(t==='crucible / conquest') return 'Boss';\n    if(t.startsWith('arena')) return 'Arena';",
                      "    if(t==='crucible / conquest') return 'Boss';\n    if(t==='fantasia ascent') return 'Solo';\n    if(t.startsWith('arena')) return 'Arena';")

    # Healing-mode Dominator should use its support Fantomon pool in Ascent.
    text=text.replace("    const base=pools[role]||[];\n    if(guardianDps){",
                      "    if(role==='Solo'&&cls==='Dominator'&&typeof dominatorBuildMode==='function'&&dominatorBuildMode()==='heals') return pools.Dungeon||pools.Solo||[];\n    const base=pools[role]||[];\n    if(guardianDps){")

    # Keep only the activity tabs in the outer selector.
    old_box="box.innerHTML='<div class=\"metaBuildTabs\">'+META_MODES.map(m=>'<button type=\"button\" data-meta-mode=\"'+esc(m)+'\">'+esc(m)+'</button>').join('')+'</div><div class=\"metaTournamentTabs\"><button type=\"button\" data-tournament-size=\"2v2\">2v2</button><button type=\"button\" data-tournament-size=\"4v4\">4v4</button></div>';"
    new_box="box.innerHTML='<div class=\"metaBuildTabs\">'+META_MODES.map(m=>'<button type=\"button\" data-meta-mode=\"'+esc(m)+'\">'+esc(m)+'</button>').join('')+'</div>';"
    if old_box not in text:
        raise SystemExit(f'{path}: metaBuildControls markup anchor missing')
    text=text.replace(old_box,new_box)

    # Restyle the tournament selector for card placement.
    text=text.replace('.builds .metaTournamentTabs{display:flex;gap:4px;padding-left:7px;border-left:1px solid var(--line)}',
                      '.builds .metaTournamentTabs{display:inline-flex;gap:4px;margin-top:8px;padding:3px;border:1px solid var(--line);border-radius:10px;background:var(--surface)}')
    text=text.replace('  .builds .metaTournamentTabs{border-left:0;border-top:1px solid var(--line);padding:5px 0 0;margin-top:5px}\n  .builds .metaTournamentTabs button{flex:1}',
                      '  .builds .buildCard>header>.metaTournamentTabs{width:100%;margin-top:8px}\n  .builds .metaTournamentTabs button{flex:1}')

    old_vis="""    const wanted=mode==='Tournament'?'Tournament · '+size:mode;
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
    });"""
    new_vis="""    const wanted=mode==='Tournament'?'Tournament · '+size:mode;
    document.querySelectorAll('.builds .metaBuildTabs button').forEach(b=>b.classList.toggle('active',b.dataset.metaMode===mode));
    grid.querySelectorAll(':scope > .buildCard').forEach(card=>{
      const wrongActivity=card.dataset.role!==wanted;
      const selectedRole=cls==='Guardian'?guardianMode:(cls==='Dominator'?dominatorMode:'');
      const wrongRole=(cls==='Guardian'||cls==='Dominator')&&card.dataset.buildRole!==selectedRole;
      card.hidden=wrongActivity||wrongRole;
    });
    grid.querySelectorAll('.metaTournamentTabs').forEach(x=>x.remove());
    if(mode==='Tournament'){
      const card=[...grid.querySelectorAll(':scope > .buildCard')].find(x=>!x.hidden);
      const header=card?.querySelector(':scope > header');
      if(header){
        const tour=document.createElement('div');
        tour.className='metaTournamentTabs';
        tour.innerHTML='<button type=\"button\" data-tournament-size=\"2v2\">2v2</button><button type=\"button\" data-tournament-size=\"4v4\">4v4</button>';
        tour.querySelectorAll('button').forEach(b=>b.classList.toggle('active',b.dataset.tournamentSize===size));
        header.append(tour);
      }
    }"""
    if old_vis not in text:
        raise SystemExit(f'{path}: tournament visibility anchor missing')
    text=text.replace(old_vis,new_vis)
    path.write_text(text,encoding='utf-8')

# v1 already adds Fantasia browser coverage. Add the specific placement regression check.
smoke=Path('scripts/site_smoke_test.mjs')
text=smoke.read_text(encoding='utf-8')
anchor="""// Restore the existing Dominator smoke assumptions.
await page.locator('#buildContent .metaBuildTabs button[data-meta-mode=\"Dungeon\"]').click();"""
insert="""// Tournament size buttons live inside the active Tournament card.
await waitBuild('Conqueror');
await page.locator('#buildContent .metaBuildTabs button[data-meta-mode=\"Tournament\"]').click();
await page.waitForTimeout(80);
const tournamentTabs=page.locator('#buildContent .buildCard:visible > header > .metaTournamentTabs');
assert(await tournamentTabs.count()===1, 'Tournament 2v2/4v4 selector is not inside the visible Tournament card');
assert(await tournamentTabs.locator('button').count()===2, 'Tournament card is missing the 2v2/4v4 buttons');

"""+anchor
if anchor not in text:
    raise SystemExit('smoke Tournament insertion anchor missing')
text=text.replace(anchor,insert,1)
smoke.write_text(text,encoding='utf-8')

print('patched Fantasia Ascent builds and nested Tournament selector')
