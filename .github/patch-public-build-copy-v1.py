from pathlib import Path
import re

ROOT = Path('.')
TARGETS = [
    Path('index.html'),
    Path('.github/build-fantomons-inject.html'),
]
TARGETS += sorted(Path('scripts').glob('*.py'))
TARGETS += sorted(Path('.github').glob('*.py'))

REPL = [
    # Legacy / hidden build copy that can still be restored by maintenance scripts.
    ("This is the published solo-PvP core: mobility, multi-hit pressure and cheat-death.",
     "Use mobility, multi-hit pressure and cheat-death to stay on the target through the opening exchange."),
    ("anti-tank shell.", "anti-tank setup."),
    ("Dungeon Tank shell", "Dungeon Tank setup"),
    ("full tank shell", "full tank setup"),
    ("Prydwen specifically recommends the single-target shell without Divine Wrath for PvP; Tempest Sphere is more reliable on player-sized targets.",
     "The single-target setup without Divine Wrath is more reliable in PvP because Tempest Sphere hits player-sized targets more consistently."),
    ("dedicated Healing card", "dedicated Healing setup"),

    # Conqueror copy.
    ("At high enough Crit, Insightful Eye → Crit Mastery. This is the greedier Dragon-style score bar: no Indomitable unless survival is actually costing attempts.",
     "At high enough Crit, Insightful Eye → Crit Mastery. This setup is built for maximum single-target score; keep Indomitable only when survival is actually costing attempts."),
    ("Do not greed away Indomitable in 2v2; one death is half the team.",
     "Keep Indomitable Will in 2v2; one death is half the team."),
    ("Current PvP synthesis", "Current PvP"),

    # Guardian: Conquest Tank now uses the guide-backed Water-support charm mix.
    (
      "role('Crucible / Conquest · Tank','Carry-support / boss tank meta',['Valor Surge','Leap Attack','Holy Purification','Lunarwater Threads'],['Holy Aegis','Soul Protection','Iron Fortress','Oath of Vigil'],'This is the true Tank/support version: buff the carry, contribute Dispel/DEF-down utility, and spend the Charm bar on staying alive plus team protection. If there is no buff worth dispelling, Holy Purification → damage.','Frigid Aura + Frigid Glint belong to Guardian DPS/Water mode, not this Tank card. If your Block is still inconsistent, Soul Protection → Block Awareness. Kels remains the default boss-support Fantomon when Dispel/DEF Down matters.','Tank/support synthesis')",
      "role('Crucible / Conquest · Tank','Carry-support / boss tank meta',['Valor Surge','Leap Attack','Holy Purification','Lunarwater Threads'],['Frigid Aura','Frigid Glint','Iron Fortress','Oath of Vigil'],'Buff the carry, use Holy Purification for Dispel/utility, and let Lunarwater Threads + the Frigid charms add useful Water/Cold pressure. If the boss has no important buff to remove, Holy Purification → a higher-damage option.','Iron Fortress and Oath of Vigil keep the party protected without overcommitting to personal mitigation. If you are actually dying, Frigid Glint → Soul Protection; if needed, Frigid Aura → Holy Aegis. Kels remains the boss-support Fantomon when Dispel/DEF Down matters.','Guide-backed')"
    ),
    ("This is the maximum team-protection shell: reliable Taunt, opening effective HP, group mitigation and Oath protection on the ally most likely to be bursted.",
     "Maximize team protection with reliable Taunt, opening effective HP, group mitigation and Oath protection on the ally most likely to be bursted."),
    ("Do not swap into the Water damage bar unless your team already has another real frontline.",
     "If your team already has another reliable frontline, one defensive slot can flex to damage."),
    ("This is the published offensive Water Guardian shell: fast Cold stacking, strong AoE and enough single-target damage to stay useful on elites. If you completely outgear the room, Potential Rebirth → Pursuit of Victory or another damage charm.",
     "Stack Cold quickly, pressure groups with Water AoE, and keep enough single-target damage for elites. If you completely outgear the room, Potential Rebirth → Pursuit of Victory or another damage charm."),
    ("Keep enough Block/DEF to stay active. DPS Guardian is a bruiser conversion, not a glass cannon.",
     "Keep enough Block/DEF to stay active; Guardian damage still benefits from staying in the fight."),
    ("Keep the three Water Techniques to stack Cold and preserve the Water/Frigid package, but replace Raging Maelstrom’s broad AoE with Star Shattering Slash for the actual single-target payoff. This is the personal-DPS version; if a stronger carry is present, Tank mode’s support bar can still produce more team damage.",
     "Keep the three Water Techniques for consistent Cold stacking, then use Star Shattering Slash for the single-target payoff. If a much stronger carry is present, a support-focused Guardian can still raise total team damage more."),
    ("This keeps the proven Block/Rebound PvP shell but spends the flex slots on actual kill pressure. If Pandarial and your ranks support it, Luminous Shield → Light Sword Array is the aggressive flex; keep Block stats high.",
     "Use Block/Rebound durability while spending the flex slots on real kill pressure. If Pandarial and your ranks support it, Luminous Shield → Light Sword Array for a more aggressive setup; keep Block stats high."),
    ("2v2 still rewards the counter/bruiser shell because you cannot afford to be deleted, but DPS mode keeps the fourth charm offensive instead of protecting the partner with Oath.",
     "2v2 still rewards the counter/bruiser setup because you cannot afford to be deleted; keep the fourth Charm offensive unless you become the enemy team’s obvious first target."),
    ("Four enemy bodies give the Water shell its best chance to stack Cold and spread pressure. If your team already has a real frontline and you are not being focused, Potential Rebirth → Pursuit of Victory for the greedier version.",
     "Four enemy bodies give the Water/Cold setup plenty of opportunities to stack Cold and spread pressure. If your team already has a frontline and you are not being focused, Potential Rebirth → Pursuit of Victory for more damage."),
    ("If your team lacks a tank, switch the role toggle back to Tank rather than trying to make this bar absorb coordinated focus.",
     "If your team lacks a frontline, use the Tank setup instead."),
    ("Meta reflect synthesis", "Current PvP"),
    ("Team-PvP synthesis", "Current PvP"),
    ("Prydwen secondary + PvP synthesis", "Prydwen + PvP"),
    ("Current Guardian PvP synthesis", "Current PvP"),
    ("Rank the Techniques that define the true frontline setup rather than the Water DPS shell.",
     "Prioritize Taunt, team support and reliable survival—the tools that make Guardian valuable in difficult group content."),
    ("Prioritize the universal shield/mitigation package before niche damage charms.",
     "Start with reliable mitigation and party protection, then add situational damage only when survival is already comfortable."),
    ("The offensive role is the Water/counter bruiser package, not a fake glass-cannon tank.",
     "Build around Water/Cold pressure while keeping enough Block and durability to stay active."),

    # Destroyer copy.
    ("Fire is the dedicated dungeon/horde build because Fiery Burst scales off repeated Fire triggers across packs. If the room is boss-heavy and packs survive poorly, swap to the mixed AoE core instead.",
     "Fire is strongest for dense dungeon packs because Fiery Burst scales off repeated Fire triggers. If most of the fight is a boss, use the mixed-element setup instead."),
    ("Strong accounts can drop Void Bubble for offense, but a dead Destroyer loses more time than the greed gains.",
     "Drop Void Bubble for offense only when deaths are no longer costing clears."),
    ("Arena is one target, so drop Howling Hurricane’s huge AoE. Formation Breaker stays even here: current T4/future-tier guidance treats it as a core Technique, while the other three Wind skills provide compact player-sized pressure and Laceration tempo.",
     "Arena is one target, so drop Howling Hurricane’s huge AoE. Formation Breaker stays because its action acceleration remains valuable, while the other three Wind skills provide compact player-sized pressure and Laceration tempo."),
    ("Meta synthesis", "Current PvP"),

    # Dominator copy.
    ("Use the published T4 AoE core for dungeon packs. It keeps all four slots contributing damage instead of dragging the healer bar into a DPS role.",
     "For dungeon packs, all four slots contribute damage so Erosion and direct hits can clear groups quickly."),
    ("If Erosion is landing poorly, improve Effect Hit Rate before replacing the whole shell. Nyxarchon is the damage lead.",
     "If Erosion is landing poorly, improve Effect Hit Rate before changing the build. Nyxarchon is the damage lead."),
    ("This is the published T4 single-target core: Starburst + Chaos Rune give reliable direct damage while Termination preserves Erosion payoff. With high Effect Hit Rate, Chaos Rune → Mana Blast raises the Erosion ceiling.",
     "Dark Starburst + Chaos Rune provide reliable direct damage while Shadow of Termination preserves the Erosion payoff. With high Effect Hit Rate, Chaos Rune → Mana Blast raises the Erosion ceiling."),
    ("If a much stronger carry is in the party, Heals mode’s Decoy + Frenzy + Mantra support setup can produce more team score than selfish DPS.",
     "If a much stronger carry is in the party, the Decoy + Frenzy + Mantra support setup can produce more team score than selfish DPS."),
    ("Arena is one target, so use the actual single-target shell instead of spending a slot on broad Abyssal Hand AoE. High Effect Hit Rate: Chaos Rune → Mana Blast.",
     "Arena is one target, so favor the single-target setup over broad Abyssal Hand AoE. High Effect Hit Rate: Chaos Rune → Mana Blast."),
    ("Keep the compact single-target damage shell but reserve one Charm slot for Resurrection; reviving your only teammate can swing an entire 2v2 round.",
     "Keep the compact single-target damage setup but reserve one Charm slot for Resurrection; reviving your only teammate can swing an entire 2v2 round."),
    ("If your partner is the true carry, switch to Heals mode for the support variant rather than weakening this DPS bar with half a support kit.",
     "If your partner is the true carry, use the support setup rather than weakening this DPS build with half a support kit."),
    ("Four enemy bodies finally justify the full AoE/Erosion shell. Resurrection replaces the selfish fourth damage Charm because its team-fight swing is unusually high.",
     "Four enemy bodies make the AoE/Erosion setup worthwhile. Resurrection replaces the selfish fourth damage Charm because its team-fight swing is unusually high."),
    ("If your comp is built around a hypercarry, Heals mode’s Decoy/Frenzy/Mantra support bar can be more valuable than personal damage.",
     "If your team is built around a hypercarry, Decoy + Frenzy + Mantra support can be more valuable than personal damage."),
    ("This is the published T4 healer core. Need more raw healing: Frenzy Totem → Healing Touch. If nobody is dying, Resurrection → Mantra of Blessings.",
     "This is the reliable dungeon-healing setup. Need more raw healing: Frenzy Totem → Healing Touch. If nobody is dying, Resurrection → Mantra of Blessings."),
    ("Phantom Light is mandatory for the dedicated healer shell. Mandragora is the pure-healing lead until Pandarial is live and validated.",
     "Phantom Light is mandatory for the dedicated healer build. Mandragora is the pure-healing lead until Pandarial is live and validated."),
    ("Only one Decoy can attach effectively and positioning matters. If your team already massively overkills the boss, DPS mode can be better; otherwise this is the support-first score bar.",
     "Only one Decoy can attach effectively and positioning matters. If your team already massively overkills the boss, the DPS setup can be better; otherwise prioritize carry support."),
    ("Only use Heals mode in Arena when your healing gear is genuinely optimized. Otherwise the DPS Arena card is the stronger default.",
     "Use this healer setup in Arena only when your Healing Boost/SPD gear is genuinely optimized. Otherwise the DPS Arena setup is stronger."),
    ("PvP healing is reduced; if your Healing Boost/SPD cannot overcome that penalty, use DPS mode and keep Resurrection there instead.",
     "PvP healing is reduced; if your Healing Boost/SPD cannot overcome that penalty, use the DPS 2v2 setup and keep Resurrection."),
    ("ST core + PvP synthesis", "Prydwen + PvP"),
    ("Prydwen AoE + PvP synthesis", "Prydwen + PvP"),
    ("PvP specialist synthesis", "PvP specialist"),
    ("PvP support synthesis", "PvP support"),
    ("Global team-PvP synthesis", "Team PvP"),

    # Skill-tooltip copy: describe gameplay, not implementation/UI concepts.
    ("Reliable damage in every current Conqueror mode, especially when enemies can be lined up.",
     "Reliable damage across current Conqueror content, especially when enemies can be lined up."),
    ("The best reusable offensive T4 Guardian investment and the anchor of DPS mode.",
     "The best reusable offensive T4 Guardian investment and a core offensive Technique."),
    ("Water pressure and Cold-setup Technique used in offensive and support shells.",
     "Water pressure and Cold-setup Technique used in offensive and support builds."),
    ("Large Water/AoE payoff for the full offensive shell.",
     "Large Water/AoE payoff for the full offensive Water build."),
    ("Keeps the PvP bruiser shell consistent against repeated-hit attackers.",
     "Keeps the PvP bruiser build consistent against repeated-hit attackers."),
    ("The first Charm you build around in the Water DPS shell.",
     "The first Charm you build around in the Water DPS build."),
    ("Paired with Frigid Aura in the dedicated Water shell.",
     "Paired with Frigid Aura in the Water DPS build."),
    ("Part of the standard sustain shell in Dungeon and carry-support setups.",
     "Part of the standard sustain build in Dungeon and carry-support setups."),
    ("Direct-damage Dark Technique used in the published T4 single-target hybrid so damage is less dependent on Erosion landing.",
     "Direct-damage Dark Technique used in the single-target hybrid so damage is less dependent on Erosion landing."),
    ("The fourth Technique in the published Dungeon/4v4 AoE shell where multiple targets justify its coverage.",
     "The fourth Technique in the Dungeon/4v4 AoE setup where multiple targets justify its coverage."),
    ("Pairs with Shadow Erosion to raise the ceiling of the Dark DPS shell.",
     "Pairs with Shadow Erosion to raise the ceiling of the Dark DPS build."),
    ("A standard selfish DPS slot in the Erosion/direct-damage shell.",
     "A standard selfish DPS slot in the Erosion/direct-damage build."),
    ("See the build card’s offensive/defensive notes for the mode-specific reason it is equipped.",
     "See the build notes for why it is equipped in this setup."),
]

changed = []
total = 0
for path in TARGETS:
    if not path.exists():
        continue
    text = path.read_text(encoding='utf-8')
    original = text
    for old, new in REPL:
        if old in text:
            c = text.count(old)
            text = text.replace(old, new)
            total += c
    if text != original:
        path.write_text(text, encoding='utf-8')
        changed.append(str(path))

# Add a durable maintenance rule so future build passes don't reintroduce internal/dev wording.
policy = Path('.github/build-maintenance.md')
ptext = policy.read_text(encoding='utf-8')
marker = "## Public build copy\n"
if marker not in ptext:
    insert = """\n## Public build copy\n\n- Build notes are player-facing. Describe what to equip, why it works, and when to swap it.\n- Avoid implementation/editorial language in visible copy such as “this card,” “shell,” “mode/toggle,” “published core,” or “synthesis” when a direct gameplay description works better.\n- When comparing alternatives, name the actual activity or setup (for example “Tank setup” or “boss support”) rather than referring to UI controls or hidden build variants.\n- Source/evidence labels may identify a guide or testing basis, but should still read naturally to a player.\n"""
    anchor = "## Current intended loadout structure\n"
    if anchor not in ptext:
        raise RuntimeError('maintenance policy insertion anchor missing')
    ptext = ptext.replace(anchor, insert + "\n" + anchor, 1)
    policy.write_text(ptext, encoding='utf-8')
    changed.append(str(policy))

# Bring the browser smoke test in line with the current one-scenario-at-a-time Builds UI.
smoke = Path('scripts/site_smoke_test.mjs')
stext = smoke.read_text(encoding='utf-8')

old = """  const titles=await buildTitles();
  assert(titles.some(x=>/^Arena/i.test(x)), `${cls} Arena loadout was lost: ${titles.join(' | ')}`);
  assert(titles.some(x=>/^Tournament/i.test(x)), `${cls} Tournament loadout was lost: ${titles.join(' | ')}`);
  const visibleCards=page.locator('#buildContent .buildGrid .buildCard:visible');
  assert(await visibleCards.count()>=4, `${cls} rich loadout set was reduced unexpectedly`);
  assert(await visibleCards.locator('.fantomonPair').count()===await visibleCards.count(), `${cls} does not show a Fantomon pair on every visible loadout`);
  const badFanto=await visibleCards.locator('.fantomonPair').evaluateAll(xs=>xs.filter(x=>x.querySelectorAll('.fantomonPick').length!==2).length);
  assert(badFanto===0, `${cls} has a loadout without exactly Main + Alt Fantomons`);

  // Recommendations must come from Techniques/Charms actually equipped somewhere in
  // the displayed loadouts, not from unrelated wishlist/swap-only pieces.
  const equipped=await visibleCards.evaluateAll(cards=>{"""
new = """  const visibleCards=page.locator('#buildContent .buildGrid .buildCard:visible');
  assert(await visibleCards.count()===1, `${cls} should show exactly one activity build at a time`);
  assert(await visibleCards.locator('.fantomonPair').count()===1, `${cls} visible build is missing its Fantomon pair`);
  const badFanto=await visibleCards.locator('.fantomonPair').evaluateAll(xs=>xs.filter(x=>x.querySelectorAll('.fantomonPick').length!==2).length);
  assert(badFanto===0, `${cls} visible build does not have exactly Main + Alt Fantomons`);

  // Recommendations must come from Techniques/Charms equipped in at least one
  // available loadout for the class, not from unrelated wishlist/swap-only pieces.
  const equipped=await page.locator('#buildContent .buildGrid .buildCard').evaluateAll(cards=>{"""
if old not in stext:
    raise RuntimeError('site smoke multi-card block anchor missing')
stext = stext.replace(old, new, 1)

old = """// Dominator keeps its DPS / Heals switch, role-specific slot stats, and a separate
// Technique-left / Charm-right recommendation pair for each role. Arena/Tournament
// remain visible reference cards in BOTH modes; only role-specific PvE cards filter.
await waitBuild('Dominator');
assert(await page.locator('#buildContent .dominatorModeTabs button').count() === 2, 'Dominator DPS/Heals tabs missing');
let titles=await buildTitles();
assert(titles.some(x=>/Single Target DPS/i.test(x)) && titles.some(x=>/AoE DPS/i.test(x)), `Dominator DPS cards not visible: ${titles.join(' | ')}`);
assert(titles.some(x=>/^Arena/i.test(x)) && titles.some(x=>/^Tournament/i.test(x)), `Dominator PvP cards missing in DPS mode: ${titles.join(' | ')}`);
assert(!titles.some(x=>/^Healing/i.test(x)), 'Dominator Healing card visible in DPS mode');
let domPair=page.locator('#buildContent > .priorityPair[data-dominator-role=\"dps\"]:visible');
assert(await domPair.count()===1 && await domPair.locator(':scope > .priorityPanel').count()===2, 'Dominator DPS Technique/Charm pair missing');
let domKinds=await domPair.locator('.priorityIntro span').allTextContents();
assert(/technique/i.test(domKinds[0]||'') && /charm/i.test(domKinds[1]||''), `Dominator DPS pair order wrong: ${domKinds.join(' | ')}`);
const dpsStatText=await page.locator('#buildContent .buildQuickStats').innerText();
assert(/Dark DPS|Effect Hit Rate/i.test(dpsStatText), 'Dominator DPS stat profile missing');

await page.locator('#buildContent button[data-dominator-mode=\"heals\"]').click();
await page.waitForFunction(()=>[...document.querySelectorAll('#buildContent .buildGrid .buildCard')].filter(x=>!x.hidden&&getComputedStyle(x).display!=='none').some(x=>/^Healing/i.test(x.querySelector('h3')?.textContent||'')),null,{timeout:3000});
await page.waitForTimeout(80);
titles=await buildTitles();
assert(titles.some(x=>/^Healing/i.test(x)), `Dominator healer card not visible: ${titles.join(' | ')}`);
assert(titles.some(x=>/^Arena/i.test(x)) && titles.some(x=>/^Tournament/i.test(x)), `Dominator PvP reference cards disappeared in Heals mode: ${titles.join(' | ')}`);
assert(!titles.some(x=>/Single Target DPS|AoE DPS/i.test(x)), `Dominator DPS PvE cards remained visible in Heals mode: ${titles.join(' | ')}`);
domPair=page.locator('#buildContent > .priorityPair[data-dominator-role=\"heals\"]:visible');
assert(await domPair.count()===1 && await domPair.locator(':scope > .priorityPanel').count()===2, 'Dominator Heals Technique/Charm pair missing');
domKinds=await domPair.locator('.priorityIntro span').allTextContents();
assert(/technique/i.test(domKinds[0]||'') && /charm/i.test(domKinds[1]||''), `Dominator Heals pair order wrong: ${domKinds.join(' | ')}`);
const healStatText=await page.locator('#buildContent .buildQuickStats').innerText();
assert(/Healing\\/support|Healing Boost/i.test(healStatText), 'Dominator Heals stat profile did not switch');
"""
new = """// Dominator keeps its DPS / Heals switch, role-specific slot stats, and a separate
// Technique-left / Charm-right recommendation pair for each role. The activity tabs
// still show one matching build at a time.
await waitBuild('Dominator');
assert(await page.locator('#buildContent .dominatorModeTabs button').count() === 2, 'Dominator DPS/Heals tabs missing');
let titles=await buildTitles();
assert(titles.length===1 && /^Dungeon/i.test(titles[0]||''), `Dominator DPS Dungeon build not visible: ${titles.join(' | ')}`);
let domPair=page.locator('#buildContent > .priorityPair[data-dominator-role=\"dps\"]:visible');
assert(await domPair.count()===1 && await domPair.locator(':scope > .priorityPanel').count()===2, 'Dominator DPS Technique/Charm pair missing');
let domKinds=await domPair.locator('.priorityIntro span').allTextContents();
assert(/technique/i.test(domKinds[0]||'') && /charm/i.test(domKinds[1]||''), `Dominator DPS pair order wrong: ${domKinds.join(' | ')}`);
const dpsStatText=await page.locator('#buildContent .buildQuickStats').innerText();
assert(/Dark DPS|Effect Hit Rate/i.test(dpsStatText), 'Dominator DPS stat profile missing');

await page.locator('#buildContent button[data-dominator-mode=\"heals\"]').click();
await page.waitForFunction(()=>[...document.querySelectorAll('#buildContent .buildGrid .buildCard')].filter(x=>!x.hidden&&getComputedStyle(x).display!=='none').some(x=>x.dataset.buildRole==='heals'),null,{timeout:3000});
await page.waitForTimeout(80);
titles=await buildTitles();
assert(titles.length===1 && /^Dungeon/i.test(titles[0]||''), `Dominator healer Dungeon build not visible: ${titles.join(' | ')}`);
domPair=page.locator('#buildContent > .priorityPair[data-dominator-role=\"heals\"]:visible');
assert(await domPair.count()===1 && await domPair.locator(':scope > .priorityPanel').count()===2, 'Dominator Heals Technique/Charm pair missing');
domKinds=await domPair.locator('.priorityIntro span').allTextContents();
assert(/technique/i.test(domKinds[0]||'') && /charm/i.test(domKinds[1]||''), `Dominator Heals pair order wrong: ${domKinds.join(' | ')}`);
const healStatText=await page.locator('#buildContent .buildQuickStats').innerText();
assert(/Healing\\/support|Healing Boost/i.test(healStatText), 'Dominator Heals stat profile did not switch');
"""
if old not in stext:
    raise RuntimeError('site smoke Dominator legacy block anchor missing')
stext = stext.replace(old, new, 1)

if stext != smoke.read_text(encoding='utf-8'):
    smoke.write_text(stext, encoding='utf-8')
    changed.append(str(smoke))

# Validation: public runtime copy should no longer contain these implementation/editorial phrases.
live = Path('.github/build-fantomons-inject.html').read_text(encoding='utf-8')
for forbidden in [
    'not this Tank card',
    'Water DPS shell',
    'Water shell',
    'DPS shell',
    'switch the role toggle',
    'Heals mode',
    'DPS mode',
    'published T4',
    'synthesis',
    'fake glass-cannon',
]:
    if forbidden in live:
        raise RuntimeError(f'public build copy still contains forbidden phrase: {forbidden!r}')

needle = "role('Crucible / Conquest · Tank','Carry-support / boss tank meta',['Valor Surge','Leap Attack','Holy Purification','Lunarwater Threads'],['Frigid Aura','Frigid Glint','Iron Fortress','Oath of Vigil']"
if needle not in live:
    raise RuntimeError('Guardian Conquest Tank Water-support charm update did not land')

if total == 0:
    raise RuntimeError('no build-copy replacements were applied')

print(f'applied {total} public-copy replacements across {len(changed)} files')
for p in changed:
    print(' -', p)
