from pathlib import Path

TARGETS=[Path('index.html'),Path('.github/build-fantomons-inject.html')]

old_modes="const META_MODES=['Dungeon','Crucible / Conquest','Arena','Fantasia Ascent','Tournament'];"
new_modes="const META_MODES=['Dungeon','Crucible / Conquest','Fantasia Ascent','Arena','Tournament'];"

old_markup="box.innerHTML='<div class=\"metaBuildTabs\">'+META_MODES.map(m=>'<button type=\"button\" data-meta-mode=\"'+esc(m)+'\">'+esc(m)+'</button>').join('')+'</div>';"
new_markup="box.innerHTML='<div class=\"metaBuildTabs\">'+META_MODES.map(m=>m==='Tournament'?'<div class=\"metaTournamentScenario\"><button type=\"button\" class=\"metaTournamentMain\" data-meta-mode=\"Tournament\">Tournament</button><div class=\"metaTournamentTabs\"><button type=\"button\" data-tournament-size=\"2v2\">2v2</button><button type=\"button\" data-tournament-size=\"4v4\">4v4</button></div></div>':'<button type=\"button\" data-meta-mode=\"'+esc(m)+'\">'+esc(m)+'</button>').join('')+'</div>';"

old_css=""".builds .metaBuildTabs button,.builds .metaTournamentTabs button{border:0;border-radius:9px;background:transparent;color:var(--muted);cursor:pointer;font-size:10px;font-weight:850;min-height:36px;padding:8px 10px}
.builds .metaBuildTabs button.active,.builds .metaTournamentTabs button.active{background:var(--accent-strong);color:#fff}
.builds .metaTournamentTabs{display:inline-flex;gap:4px;margin-top:8px;padding:3px;border:1px solid var(--line);border-radius:10px;background:var(--surface)}
.builds .metaTournamentTabs[hidden]{display:none!important}"""
new_css=""".builds .metaBuildTabs>button,.builds .metaTournamentMain{border:0;border-radius:9px;background:transparent;color:var(--muted);cursor:pointer;font-size:10px;font-weight:850;min-height:36px;padding:8px 10px;width:100%}
.builds .metaBuildTabs>button.active{background:var(--accent-strong);color:#fff}
.builds .metaTournamentScenario{display:grid;grid-template-columns:minmax(0,1fr);align-items:center;min-width:0;border-radius:9px;overflow:hidden;background:transparent}
.builds .metaTournamentScenario.active{grid-template-columns:minmax(0,1fr) auto;background:var(--accent-strong)}
.builds .metaTournamentScenario.active>.metaTournamentMain{background:transparent;color:#fff}
.builds .metaTournamentTabs{display:none;align-items:center;gap:2px;padding-right:4px}
.builds .metaTournamentScenario.active>.metaTournamentTabs{display:flex}
.builds .metaTournamentTabs button{border:0;border-radius:6px;background:rgba(255,255,255,.12);color:#fff;cursor:pointer;font-size:9px;font-weight:850;min-height:26px;padding:4px 7px}
.builds .metaTournamentTabs button:hover{background:rgba(255,255,255,.2)}
.builds .metaTournamentTabs button.active{background:rgba(255,255,255,.3)}"""

old_mobile="""  .builds .buildCard>header>.metaTournamentTabs{width:100%;margin-top:8px}
  .builds .metaTournamentTabs button{flex:1}"""
new_mobile="""  .builds .metaTournamentScenario.active{grid-template-columns:minmax(0,1fr) auto}
  .builds .metaTournamentTabs button{min-width:34px;padding:4px 6px}"""

old_visibility="""    const wanted=mode==='Tournament'?'Tournament · '+size:mode;
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
new_visibility="""    const wanted=mode==='Tournament'?'Tournament · '+size:mode;
    document.querySelectorAll('.builds .metaBuildTabs [data-meta-mode]').forEach(b=>b.classList.toggle('active',b.dataset.metaMode===mode));
    document.querySelectorAll('.builds .metaTournamentScenario').forEach(x=>x.classList.toggle('active',mode==='Tournament'));
    document.querySelectorAll('.builds .metaTournamentTabs [data-tournament-size]').forEach(b=>b.classList.toggle('active',b.dataset.tournamentSize===size));
    grid.querySelectorAll(':scope > .buildCard').forEach(card=>{
      const wrongActivity=card.dataset.role!==wanted;
      const selectedRole=cls==='Guardian'?guardianMode:(cls==='Dominator'?dominatorMode:'');
      const wrongRole=(cls==='Guardian'||cls==='Dominator')&&card.dataset.buildRole!==selectedRole;
      card.hidden=wrongActivity||wrongRole;
    });"""

old_fanto="""    const guardianDps=cls==='Guardian'&&typeof guardianBuildMode==='function'&&guardianBuildMode()==='dps';
    if(role==='Arena'){"""
new_fanto="""    const guardianDps=cls==='Guardian'&&typeof guardianBuildMode==='function'&&guardianBuildMode()==='dps';
    const ascent=String(title||'').startsWith('Fantasia Ascent');
    if(ascent&&cls==='Destroyer') return [
      pick('Nyxarchon','Best damage-first Ascent lead: strong Dark AoE plus stacking DEF reduction helps beat high-DEF floors.'),
      pick('Aegiswing','Use when deaths are ending the push before your rotation can finish.'),
      pick('Armopi','Best no-shop survival option: DEF stacking and shields can buy the extra turn Destroyer needs.'),
      pick('Zeioletus','No-shop damage alternative when survival is already comfortable.')
    ];
    if(ascent&&cls==='Dominator'){
      const heals=typeof dominatorBuildMode==='function'&&dominatorBuildMode()==='heals';
      if(heals) return [
        pick('Herbote','Best S2 solo-sustain lead when evolved: self-healing, cleanse chance, and owner healing directly support long Ascent fights.'),
        pick('Aegiswing','Safety alternative when burst damage is killing you before the healing loop stabilizes.'),
        pick('Mandragora','No-shop healing alternative for ally-targeted Technique builds, especially before Herbote is evolved.'),
        pick('Terragon','Damage-mitigation alternative when lowering enemy ATK/DMG matters more than extra raw healing.')
      ];
      return [
        pick('Nyxarchon','Best DPS Ascent lead: Dark damage matches Dominator and the DEF reduction improves the whole damage loop.'),
        pick('Aegiswing','Survival alternative when you are losing the floor before Erosion and Dark damage can ramp.'),
        pick('Zeioletus','Best straightforward no-shop damage alternative.'),
        pick('Sylvaerie','SPD-focused alternative; test it against Zeioletus if extra actions outperform direct pet damage.')
      ];
    }
    if(role==='Arena'){"""

for path in TARGETS:
    text=path.read_text(encoding='utf-8')
    for old,new,label in [
        (old_modes,new_modes,'META_MODES order'),
        (old_markup,new_markup,'scenario markup'),
        (old_css,new_css,'Tournament scenario CSS'),
        (old_mobile,new_mobile,'mobile Tournament CSS'),
        (old_visibility,new_visibility,'Tournament visibility logic'),
        (old_fanto,new_fanto,'Fantasia Fantomon override'),
    ]:
        count=text.count(old)
        if count<1:
            raise SystemExit(f'{path}: missing {label} anchor')
        text=text.replace(old,new)
    path.write_text(text,encoding='utf-8')
    print(f'{path}: moved Fantasia, fixed Tournament scenario controls, and added Ascent Fantomon picks')

smoke=Path('scripts/site_smoke_test.mjs')
text=smoke.read_text(encoding='utf-8')
text=text.replace("assert(await page.locator('#buildContent .metaBuildTabs button').count()===5, 'build activity selector does not contain five modes');",
                  "assert(await page.locator('#buildContent .metaBuildTabs [data-meta-mode]').count()===5, 'build activity selector does not contain five modes');")
old_test="""// Tournament size buttons live inside the active Tournament card.
await waitBuild('Conqueror');
await page.locator('#buildContent .metaBuildTabs button[data-meta-mode=\"Tournament\"]').click();
await page.waitForTimeout(80);
const tournamentTabs=page.locator('#buildContent .buildCard:visible > header > .metaTournamentTabs');
assert(await tournamentTabs.count()===1, 'Tournament 2v2/4v4 selector is not inside the visible Tournament card');
assert(await tournamentTabs.locator('button').count()===2, 'Tournament card is missing the 2v2/4v4 buttons');

// Restore the existing Dominator smoke assumptions.
await page.locator('#buildContent .metaBuildTabs button[data-meta-mode=\"Dungeon\"]').click();
await page.locator('#buildContent button[data-dominator-mode=\"dps\"]').click();
await page.waitForTimeout(80);

// Dominator keeps its DPS / Heals switch, role-specific slot stats, and a separate
// Technique-left / Charm-right recommendation pair for each role. The activity tabs
// still show one matching build at a time.
await waitBuild('Dominator');"""
new_test="""// Fantasia sits directly after Crucible / Conquest in the activity selector.
await waitBuild('Conqueror');
const scenarioOrder=await page.locator('#buildContent .metaBuildTabs [data-meta-mode]').evaluateAll(xs=>xs.map(x=>x.dataset.metaMode));
assert(JSON.stringify(scenarioOrder)===JSON.stringify(['Dungeon','Crucible / Conquest','Fantasia Ascent','Arena','Tournament']), `activity order wrong: ${scenarioOrder.join(' | ')}`);

// Rechecked Ascent Fantomon choices: Destroyer and Dominator use push-specific pools.
await waitBuild('Destroyer');
await page.locator('#buildContent .metaBuildTabs [data-meta-mode=\"Fantasia Ascent\"]').click();
await page.waitForTimeout(80);
let ascentPets=await page.locator('#buildContent .buildCard:visible .fantomonPick b').allTextContents();
assert(JSON.stringify(ascentPets)===JSON.stringify(['Nyxarchon','Aegiswing','Armopi']), `Destroyer Ascent Fantomons wrong: ${ascentPets.join(' | ')}`);
await waitBuild('Dominator');
await page.locator('#buildContent .metaBuildTabs [data-meta-mode=\"Fantasia Ascent\"]').click();
await page.locator('#buildContent button[data-dominator-mode=\"dps\"]').click();
await page.waitForTimeout(80);
ascentPets=await page.locator('#buildContent .buildCard:visible .fantomonPick b').allTextContents();
assert(JSON.stringify(ascentPets)===JSON.stringify(['Nyxarchon','Aegiswing','Zeioletus']), `Dominator DPS Ascent Fantomons wrong: ${ascentPets.join(' | ')}`);
await page.locator('#buildContent button[data-dominator-mode=\"heals\"]').click();
await page.waitForTimeout(80);
ascentPets=await page.locator('#buildContent .buildCard:visible .fantomonPick b').allTextContents();
assert(JSON.stringify(ascentPets)===JSON.stringify(['Herbote','Aegiswing','Mandragora']), `Dominator Heals Ascent Fantomons wrong: ${ascentPets.join(' | ')}`);

// Tournament size controls live inside the Tournament scenario tab and are interactive.
await waitBuild('Conqueror');
await page.locator('#buildContent .metaBuildTabs [data-meta-mode=\"Tournament\"]').click();
await page.waitForTimeout(80);
const tournamentScenario=page.locator('#buildContent .metaTournamentScenario');
assert(await tournamentScenario.count()===1, 'Tournament scenario wrapper missing');
const tournamentTabs=tournamentScenario.locator('.metaTournamentTabs');
assert(await tournamentTabs.locator('button').count()===2, 'Tournament scenario is missing 2v2/4v4 buttons');
assert(await tournamentTabs.isVisible(), 'Tournament 2v2/4v4 buttons are not visible inside the active Tournament tab');
assert(await page.locator('#buildContent .buildCard:visible .metaTournamentTabs').count()===0, 'Tournament size controls leaked back into the build card');
await tournamentTabs.locator('[data-tournament-size=\"4v4\"]').click();
await page.waitForTimeout(80);
let tournamentTitle=(await buildTitles())[0]||'';
assert(/^Tournament · 4v4/i.test(tournamentTitle), `4v4 selector did not switch build: ${tournamentTitle}`);
await page.locator('#buildContent .metaTournamentScenario [data-tournament-size=\"2v2\"]').click();
await page.waitForTimeout(80);
tournamentTitle=(await buildTitles())[0]||'';
assert(/^Tournament · 2v2/i.test(tournamentTitle), `2v2 selector did not switch build: ${tournamentTitle}`);

// Restore the existing Dominator smoke assumptions.
await waitBuild('Dominator');
await page.locator('#buildContent .metaBuildTabs [data-meta-mode=\"Dungeon\"]').click();
await page.locator('#buildContent button[data-dominator-mode=\"dps\"]').click();
await page.waitForTimeout(80);

// Dominator keeps its DPS / Heals switch, role-specific slot stats, and a separate
// Technique-left / Charm-right recommendation pair for each role. The activity tabs
// still show one matching build at a time."""
if old_test not in text:
    raise SystemExit('smoke: old Tournament placement block missing')
text=text.replace(old_test,new_test,1)
smoke.write_text(text,encoding='utf-8')
print('scripts/site_smoke_test.mjs: added scenario interaction and Ascent Fantomon regression coverage')
