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
    ("Use mobility, multi-hit pressure and cheat-death to stay on the target through the opening exchange.",
     "Use mobility, multi-hit pressure and cheat-death to stay on the target through the opening exchange."),
    ("anti-tank setup.", "anti-tank setup."),
    ("Dungeon Tank setup", "Dungeon Tank setup"),
    ("full tank setup", "full tank setup"),
    ("The single-target setup without Divine Wrath is more reliable in PvP because Tempest Sphere hits player-sized targets more consistently.",
     "The single-target setup without Divine Wrath is more reliable in PvP because Tempest Sphere hits player-sized targets more consistently."),
    ("dedicated Healing setup", "dedicated Healing setup"),

    # Conqueror copy.
    ("At high enough Crit, Insightful Eye → Crit Mastery. This setup is built for maximum single-target score; keep Indomitable only when survival is actually costing attempts.",
     "At high enough Crit, Insightful Eye → Crit Mastery. This setup is built for maximum single-target score; keep Indomitable only when survival is actually costing attempts."),
    ("Keep Indomitable Will in 2v2; one death is half the team.",
     "Keep Indomitable Will in 2v2; one death is half the team."),
    ("Current PvP", "Current PvP"),

    # Guardian: Conquest Tank now uses the guide-backed Water-support charm mix.
    (
      "role('Crucible / Conquest · Tank','Carry-support / boss tank meta',['Valor Surge','Leap Attack','Holy Purification','Lunarwater Threads'],['Frigid Aura','Frigid Glint','Iron Fortress','Oath of Vigil'],'Buff the carry, use Holy Purification for Dispel/utility, and let Lunarwater Threads + the Frigid charms add useful Water/Cold pressure. If the boss has no important buff to remove, Holy Purification → a higher-damage option.','Iron Fortress and Oath of Vigil keep the party protected without overcommitting to personal mitigation. If you are actually dying, Frigid Glint → Soul Protection; if needed, Frigid Aura → Holy Aegis. Kels remains the boss-support Fantomon when Dispel/DEF Down matters.','Guide-backed')",
      "role('Crucible / Conquest · Tank','Carry-support / boss tank meta',['Valor Surge','Leap Attack','Holy Purification','Lunarwater Threads'],['Frigid Aura','Frigid Glint','Iron Fortress','Oath of Vigil'],'Buff the carry, use Holy Purification for Dispel/utility, and let Lunarwater Threads + the Frigid charms add useful Water/Cold pressure. If the boss has no important buff to remove, Holy Purification → a higher-damage option.','Iron Fortress and Oath of Vigil keep the party protected without overcommitting to personal mitigation. If you are actually dying, Frigid Glint → Soul Protection; if needed, Frigid Aura → Holy Aegis. Kels remains the boss-support Fantomon when Dispel/DEF Down matters.','Guide-backed')"
    ),
    ("Maximize team protection with reliable Taunt, opening effective HP, group mitigation and Oath protection on the ally most likely to be bursted.",
     "Maximize team protection with reliable Taunt, opening effective HP, group mitigation and Oath protection on the ally most likely to be bursted."),
    ("If your team already has another reliable frontline, one defensive slot can flex to damage.",
     "If your team already has another reliable frontline, one defensive slot can flex to damage."),
    ("Stack Cold quickly, pressure groups with Water AoE, and keep enough single-target damage for elites. If you completely outgear the room, Potential Rebirth → Pursuit of Victory or another damage charm.",
     "Stack Cold quickly, pressure groups with Water AoE, and keep enough single-target damage for elites. If you completely outgear the room, Potential Rebirth → Pursuit of Victory or another damage charm."),
    ("Keep enough Block/DEF to stay active; Guardian damage still benefits from staying in the fight.",
     "Keep enough Block/DEF to stay active; Guardian damage still benefits from staying in the fight."),
    ("Keep the three Water Techniques for consistent Cold stacking, then use Star Shattering Slash for the single-target payoff. If a much stronger carry is present, a support-focused Guardian can still raise total team damage more.",
     "Keep the three Water Techniques for consistent Cold stacking, then use Star Shattering Slash for the single-target payoff. If a much stronger carry is present, a support-focused Guardian can still raise total team damage more."),
    ("Use Block/Rebound durability while spending the flex slots on real kill pressure. If Pandarial and your ranks support it, Luminous Shield → Light Sword Array for a more aggressive setup; keep Block stats high.",
     "Use Block/Rebound durability while spending the flex slots on real kill pressure. If Pandarial and your ranks support it, Luminous Shield → Light Sword Array for a more aggressive setup; keep Block stats high."),
    ("2v2 still rewards the counter/bruiser setup because you cannot afford to be deleted; keep the fourth Charm offensive unless you become the enemy team’s obvious first target.",
     "2v2 still rewards the counter/bruiser setup because you cannot afford to be deleted; keep the fourth Charm offensive unless you become the enemy team’s obvious first target."),
    ("Four enemy bodies give the Water/Cold setup plenty of opportunities to stack Cold and spread pressure. If your team already has a frontline and you are not being focused, Potential Rebirth → Pursuit of Victory for more damage.",
     "Four enemy bodies give the Water/Cold setup plenty of opportunities to stack Cold and spread pressure. If your team already has a frontline and you are not being focused, Potential Rebirth → Pursuit of Victory for more damage."),
    ("If your team lacks a frontline, use the Tank setup instead.",
     "If your team lacks a frontline, use the Tank setup instead."),
    ("Current PvP", "Current PvP"),
    ("Current PvP", "Current PvP"),
    ("Prydwen + PvP", "Prydwen + PvP"),
    ("Current PvP", "Current PvP"),
    ("Prioritize Taunt, team support and reliable survival—the tools that make Guardian valuable in difficult group content.",
     "Prioritize Taunt, team support and reliable survival—the tools that make Guardian valuable in difficult group content."),
    ("Start with reliable mitigation and party protection, then add situational damage only when survival is already comfortable.",
     "Start with reliable mitigation and party protection, then add situational damage only when survival is already comfortable."),
    ("Build around Water/Cold pressure while keeping enough Block and durability to stay active.",
     "Build around Water/Cold pressure while keeping enough Block and durability to stay active."),

    # Destroyer copy.
    ("Fire is strongest for dense dungeon packs because Fiery Burst scales off repeated Fire triggers. If most of the fight is a boss, use the mixed-element setup instead.",
     "Fire is strongest for dense dungeon packs because Fiery Burst scales off repeated Fire triggers. If most of the fight is a boss, use the mixed-element setup instead."),
    ("Drop Void Bubble for offense only when deaths are no longer costing clears.",
     "Drop Void Bubble for offense only when deaths are no longer costing clears."),
    ("Arena is one target, so drop Howling Hurricane’s huge AoE. Formation Breaker stays because its action acceleration remains valuable, while the other three Wind skills provide compact player-sized pressure and Laceration tempo.",
     "Arena is one target, so drop Howling Hurricane’s huge AoE. Formation Breaker stays because its action acceleration remains valuable, while the other three Wind skills provide compact player-sized pressure and Laceration tempo."),
    ("Current PvP", "Current PvP"),

    # Dominator copy.
    ("For dungeon packs, all four slots contribute damage so Erosion and direct hits can clear groups quickly.",
     "For dungeon packs, all four slots contribute damage so Erosion and direct hits can clear groups quickly."),
    ("If Erosion is landing poorly, improve Effect Hit Rate before changing the build. Nyxarchon is the damage lead.",
     "If Erosion is landing poorly, improve Effect Hit Rate before changing the build. Nyxarchon is the damage lead."),
    ("Dark Starburst + Chaos Rune provide reliable direct damage while Shadow of Termination preserves the Erosion payoff. With high Effect Hit Rate, Chaos Rune → Mana Blast raises the Erosion ceiling.",
     "Dark Starburst + Chaos Rune provide reliable direct damage while Shadow of Termination preserves the Erosion payoff. With high Effect Hit Rate, Chaos Rune → Mana Blast raises the Erosion ceiling."),
    ("If a much stronger carry is in the party, the Decoy + Frenzy + Mantra support setup can produce more team score than selfish DPS.",
     "If a much stronger carry is in the party, the Decoy + Frenzy + Mantra support setup can produce more team score than selfish DPS."),
    ("Arena is one target, so favor the single-target setup over broad Abyssal Hand AoE. High Effect Hit Rate: Chaos Rune → Mana Blast.",
     "Arena is one target, so favor the single-target setup over broad Abyssal Hand AoE. High Effect Hit Rate: Chaos Rune → Mana Blast."),
    ("Keep the compact single-target damage setup but reserve one Charm slot for Resurrection; reviving your only teammate can swing an entire 2v2 round.",
     "Keep the compact single-target damage setup but reserve one Charm slot for Resurrection; reviving your only teammate can swing an entire 2v2 round."),
    ("If your partner is the true carry, use the support setup rather than weakening this DPS build with half a support kit.",
     "If your partner is the true carry, use the support setup rather than weakening this DPS build with half a support kit."),
    ("Four enemy bodies make the AoE/Erosion setup worthwhile. Resurrection replaces the selfish fourth damage Charm because its team-fight swing is unusually high.",
     "Four enemy bodies make the AoE/Erosion setup worthwhile. Resurrection replaces the selfish fourth damage Charm because its team-fight swing is unusually high."),
    ("If your team is built around a hypercarry, Decoy + Frenzy + Mantra support can be more valuable than personal damage.",
     "If your team is built around a hypercarry, Decoy + Frenzy + Mantra support can be more valuable than personal damage."),
    ("This is the reliable dungeon-healing setup. Need more raw healing: Frenzy Totem → Healing Touch. If nobody is dying, Resurrection → Mantra of Blessings.",
     "This is the reliable dungeon-healing setup. Need more raw healing: Frenzy Totem → Healing Touch. If nobody is dying, Resurrection → Mantra of Blessings."),
    ("Phantom Light is mandatory for the dedicated healer build. Mandragora is the pure-healing lead until Pandarial is live and validated.",
     "Phantom Light is mandatory for the dedicated healer build. Mandragora is the pure-healing lead until Pandarial is live and validated."),
    ("Only one Decoy can attach effectively and positioning matters. If your team already massively overkills the boss, the DPS setup can be better; otherwise prioritize carry support.",
     "Only one Decoy can attach effectively and positioning matters. If your team already massively overkills the boss, the DPS setup can be better; otherwise prioritize carry support."),
    ("Use this healer setup in Arena only when your Healing Boost/SPD gear is genuinely optimized. Otherwise the DPS Arena setup is stronger.",
     "Use this healer setup in Arena only when your Healing Boost/SPD gear is genuinely optimized. Otherwise the DPS Arena setup is stronger."),
    ("PvP healing is reduced; if your Healing Boost/SPD cannot overcome that penalty, use the DPS 2v2 setup and keep Resurrection.",
     "PvP healing is reduced; if your Healing Boost/SPD cannot overcome that penalty, use the DPS 2v2 setup and keep Resurrection."),
    ("Prydwen + PvP", "Prydwen + PvP"),
    ("Prydwen + PvP", "Prydwen + PvP"),
    ("PvP specialist", "PvP specialist"),
    ("PvP support", "PvP support"),
    ("Team PvP", "Team PvP"),

    # Skill-tooltip copy: describe gameplay, not implementation/UI concepts.
    ("Reliable damage across current Conqueror content, especially when enemies can be lined up.",
     "Reliable damage across current Conqueror content, especially when enemies can be lined up."),
    ("The best reusable offensive T4 Guardian investment and a core offensive Technique.",
     "The best reusable offensive T4 Guardian investment and a core offensive Technique."),
    ("Water pressure and Cold-setup Technique used in offensive and support builds.",
     "Water pressure and Cold-setup Technique used in offensive and support builds."),
    ("Large Water/AoE payoff for the full offensive Water build.",
     "Large Water/AoE payoff for the full offensive Water build."),
    ("Keeps the PvP bruiser build consistent against repeated-hit attackers.",
     "Keeps the PvP bruiser build consistent against repeated-hit attackers."),
    ("The first Charm you build around in the Water DPS build.",
     "The first Charm you build around in the Water DPS build."),
    ("Paired with Frigid Aura in the Water DPS build.",
     "Paired with Frigid Aura in the Water DPS build."),
    ("Part of the standard sustain build in Dungeon and carry-support setups.",
     "Part of the standard sustain build in Dungeon and carry-support setups."),
    ("Direct-damage Dark Technique used in the single-target hybrid so damage is less dependent on Erosion landing.",
     "Direct-damage Dark Technique used in the single-target hybrid so damage is less dependent on Erosion landing."),
    ("The fourth Technique in the Dungeon/4v4 AoE setup where multiple targets justify its coverage.",
     "The fourth Technique in the Dungeon/4v4 AoE setup where multiple targets justify its coverage."),
    ("Pairs with Shadow Erosion to raise the ceiling of the Dark DPS build.",
     "Pairs with Shadow Erosion to raise the ceiling of the Dark DPS build."),
    ("A standard selfish DPS slot in the Erosion/direct-damage build.",
     "A standard selfish DPS slot in the Erosion/direct-damage build."),
    ("See the build notes for why it is equipped in this setup.",
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
