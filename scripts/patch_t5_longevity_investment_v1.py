from pathlib import Path

p = Path('index.html')
text = p.read_text(encoding='utf-8')


def replace_once(haystack, old, new, label):
    count = haystack.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 match, found {count}')
    return haystack.replace(old, new, 1)


def replace_class_priority_pair(haystack, cls, next_cls, replacement):
    start_marker = f"    if(cls==='{cls}') return `"
    end_marker = f"\n\n    if(cls==='{next_cls}') return `"
    start = haystack.index(start_marker)
    end = haystack.index(end_marker, start)
    segment = haystack[start:end]
    pair_start = segment.index('      <div class="priorityPanel"><div class="priorityIntro"><span>Technique investment</span>')
    grid_start = segment.index('      <div class="buildGrid">', pair_start)
    old_pair = segment[pair_start:grid_start]
    if old_pair.count('<div class="priorityPanel">') != 2:
        raise SystemExit(f'{cls}: expected exactly 2 direct priority panels before build grid')
    segment = segment[:pair_start] + replacement + segment[grid_start:]
    return haystack[:start] + segment + haystack[end:]


conqueror_pair = '''      <div class="priorityPanel"><div class="priorityIntro"><span>Technique investment</span><strong>Flickering first; keep late ranks flexible</strong><p>Prydwen still calls Flickering Blade the best T4 Technique. With no T5 guide for this class line yet, spend deepest on the proven core pair and be more conservative with narrower T4-only damage slots.</p></div><ol class="priorityList"><li><b>1</b><div><strong>Flickering Blade</strong><p>Best current T4 Technique, no cooldown, huge repeat ceiling, and equipped across every current Conqueror activity.</p></div></li><li><b>2</b><div><strong>Blade Storm</strong><p>Broad current value across PvE and PvP. A safer second deep investment than activity-specific utility.</p></div></li><li><b>3</b><div><strong>Flash Fire</strong><p>Excellent S2 reach and Elemental pressure, but its T5 carryover is not confirmed yet; rank after the core pair.</p></div></li><li><b>4</b><div><strong>Flame Aura</strong><p>Strong current PvE damage, but the narrower use makes it the first place to stop if you want to preserve tickets for T5.</p></div></li></ol></div>
      <div class="priorityPanel"><div class="priorityIntro"><span>Charm investment</span><strong>Piercing Assault is the long-term spend</strong><p>Prydwen explicitly says Piercing Assault remains useful on T5 and beyond. Tactical Adaptation is the next safest current investment; gear-dependent Crit and survival slots should receive fewer scarce ranks.</p></div><ol class="priorityList"><li><b>1</b><div><strong>Piercing Assault</strong><p>Confirmed long-term value: Prydwen calls it the number-one T4 target and says it continues into T5 and later tiers.</p></div></li><li><b>2</b><div><strong>Tactical Adaptation</strong><p>Universal offensive/defensive value in every current Conqueror activity, making it the next safest rank target.</p></div></li><li><b>3</b><div><strong>Soul Breaker</strong><p>Better long-run S2 offense once gear solves Crit Rate; preferable to sinking extra ranks into Insightful Eye.</p></div></li><li><b>4</b><div><strong>Indomitable Will</strong><p>Valuable PvP insurance and still worth a functional rank, but do not prioritize it over the two universal core Charms.</p></div></li></ol></div>
'''
text = replace_class_priority_pair(text, 'Conqueror', 'Guardian', conqueror_pair)


destroyer_pair = '''      <div class="priorityPanel"><div class="priorityIntro"><span>Technique investment</span><strong>Formation Breaker has real T5 longevity</strong><p>The new Magister guide gives unusually clear carryover evidence: Formation Breaker remains universal, while Wind Blade Spiral, Thunder of Judgment and Meteoric Flames all survive into showcased T5 builds.</p></div><ol class="priorityList"><li><b>1</b><div><strong>Formation Breaker</strong><p>Deepest investment by far. Prydwen says to use it in every Magister build and even in later tiers.</p></div></li><li><b>2</b><div><strong>Wind Blade Spiral</strong><p>Retained in T5 Wind AoE and PvP, giving it excellent cross-mode longevity on top of strong S2 cycling.</p></div></li><li><b>3</b><div><strong>Thunder of Judgment</strong><p>Retained in T5 single-target and PvP. Strong boss-priority damage now with clear future use.</p></div></li><li><b>4</b><div><strong>Meteoric Flames</strong><p>Still appears in T5 Fire AoE and remains a T5 single-target flex, so current ranks are not stranded next season.</p></div></li></ol></div>
      <div class="priorityPanel"><div class="priorityIntro"><span>Charm investment</span><strong>T5 carryovers before T4 tempo</strong><p>Favor Charms that the Magister guide still equips. Rapid Cast is excellent now but disappears from the showcased T5 bars, so it no longer deserves a top scarce-rank recommendation.</p></div><ol class="priorityList"><li><b>1</b><div><strong>Radiant Sear</strong><p>Retained in T5 Wind AoE and single-target. It is no longer the top damage proc there, but Prydwen still considers it too valuable to drop.</p></div></li><li><b>2</b><div><strong>Cyclone Lament</strong><p>Retained in T5 Wind AoE and PvP, with additional single-target flex value when running multiple Wind Techniques.</p></div></li><li><b>3</b><div><strong>Mana Surge</strong><p>Retained in the T5 single-target setup, giving a current boss investment a clean next-season landing spot.</p></div></li><li><b>4</b><div><strong>Fiery Burst / Explosive Spirit</strong><p>Both survive in the T5 Fire AoE shell. Rank them after the broader carryovers unless Fire is your main long-term build.</p></div></li></ol></div>
'''
text = replace_class_priority_pair(text, 'Destroyer', 'Dominator', destroyer_pair)


guardian_new = '''  const GUARDIAN_PRIORITY={
    tank:[
      ['Tank technique investment','Valor Surge first','Prydwen says Guardian\'s long-run value is mostly in its supporting options. Favor the party-wide utility first, then the T4 Taunt and survival tools that solve current content.',[
        ['Valor Surge','Best longevity-weighted Tank rank: party damage support plus cleanse utility, and it is equipped across every current Guardian role.'],
        ['Heart of Challenge','Core S2 group Taunt and still a high current-content priority after Valor Surge.'],
        ['Luminous Shield','Reliable shield layer across dungeon and PvP tank bars; useful now without overcommitting to pure damage.'],
        ['Desperate Protection / Hamper Strike','Finish the current Tank shell with survival or extra Taunt, but keep these below the broader support core.']
      ]],
      ['Tank charm investment','Soul Protection first','The support identity is the safer long-term Guardian investment. Build the universal mitigation core before spending heavily on narrower damage Charms.',[
        ['Soul Protection','Massive opening effective HP and the most universal Guardian T4 Charm.'],
        ['Iron Will','Excellent damage reduction once Taunt is active and broadly useful in difficult group content.'],
        ['Holy Aegis','DEF plus stronger DEF-scaling shields; dependable across Tank and bruiser setups.'],
        ['Iron Fortress / Oath of Vigil','Team mitigation and ally protection are the right place for later Tank ranks, especially for Tournament.']
      ]]
    ],
    dps:[
      ['DPS technique investment','Valor Surge before Water ranks','Water Guardian is strong in S2, but Prydwen explicitly says the class benefits more from support in the long run. Keep Valor Surge deepest, then rank the current Water damage core.',[
        ['Valor Surge','Equipped in every Guardian DPS bar and provides party value that is less dependent on the current Water damage shell.'],
        ['Swirling Blade','Best reusable T4 offensive Technique: strong Water damage plus a self-shield.'],
        ['Lunarwater Threads','Reliable Water pressure and Cold setup across dungeon, boss and team-PvP DPS bars.'],
        ['Raging Maelstrom / Star Shattering Slash','Strong current finishers for AoE or concentrated targets, but rank them after the broader utility pieces.']
      ]],
      ['DPS charm investment','Water core, but do not overextend it','These are real current DPS pieces, but the class\'s longer-term identity is support. If tickets are scarce, finish Tank/support priorities before chasing extra ranks on the narrower Water shell.',[
        ['Frigid Aura','Core current Water/Cold amplifier and the best first offensive Charm rank.'],
        ['Frigid Glint','Directly supports the current Cold-based offensive loop.'],
        ['Defensive Assault','Turns Guardian durability into useful offensive pressure while preserving bruiser value.'],
        ['Potential Rebirth / Pursuit of Victory','Safety or greed depending on content; useful functional ranks, not first-choice deep investments.']
      ]]
    ]
  };'''
start = text.index('  const GUARDIAN_PRIORITY={')
end = text.index('\n\n  const DOMINATOR_PRIORITY={', start)
text = text[:start] + guardian_new + text[end:]


dominator_new = '''  const DOMINATOR_PRIORITY={
    dps:[
      ['DPS technique investment','Carryovers first; then save','Prophet changes the DPS kit heavily, so do not blindly max the whole T4 bar. Rank the T4 Techniques that Prydwen still shows in T5 variants, then preserve tickets for the new T5 core.',[
        ['Dark Starburst','Still used in the T5 Pure Erosion build, so current single-target ranks retain a real next-season role.'],
        ['Shadow of Termination','Also retained in T5 Pure Erosion and remains a strong current finisher.'],
        ['Abyssal Hand','The one old AoE Technique Prydwen explicitly keeps in the T5 Direct AoE build.'],
        ['Dark Bullet','Very useful throughout S2, but largely displaced by new T5 DPS Techniques; stop earlier here if tickets are scarce.']
      ]],
      ['DPS charm investment','Shadow Vengeance is the safest deep rank','T5 Prophet keeps several T4 Charms. Favor the ones that survive into direct or Erosion builds and demote Night\'s Blessing because T5 introduces a stronger competitor.',[
        ['Shadow Vengeance','Still a must-have survival window in T5 and remains useful in direct DPS and PvP.'],
        ['Shadow Erosion','Retained as a core T5 Erosion Charm for long fights.'],
        ['Linked Misfortune','Retained as another core piece of the T5 Pure Erosion package.'],
        ["Night's Blessing",'Strong now, but T5 Shadowy Current competes directly with it; keep it below the confirmed carryover core.']
      ]]
    ],
    heals:[
      ['Healing technique investment','Radiant Restoration first','Prophet\'s published T5 healer bar retains most of the current healing kit. These ranks have much better shelf life than Dominator DPS ranks.',[
        ['Radiant Restoration','Retained directly in the T5 Prophet healing build and provides dependable party sustain now.'],
        ['Rejuvenating Rain','Also retained in T5; repeatable healing remains useful, though it can be flexed when burst healing matters more.'],
        ['Frenzy Totem','Still usable in the T5 healer bar and even remains a T5 DPS/PvP alternative, giving it unusually broad longevity.'],
        ['Waterling Summon','Retained in the T5 healer build, but rank after the more reliable tools because the summon can be killed quickly.']
      ]],
      ['Healing charm investment','Phantom Light and Overhealing age extremely well','Prydwen keeps Phantom Light, Healing Mastery and Overhealing in the T5 healing build; Overhealing also gains a new interaction with Radiant Rhythm.',[
        ['Phantom Light','Must-have healer Charm now and still equipped in the published T5 Prophet healing build.'],
        ['Overhealing','Retained in T5 and gains direct synergy with Radiant Rhythm\'s bouncing heals.'],
        ['Healing Mastery','Straightforward throughput that remains equipped in the T5 healer shell.'],
        ['Resurrection / Mantra of Blessings','Both remain valid T5 flex choices depending on whether allies need recovery or the team can greed for damage.']
      ]]
    ]
  };'''
start = text.index('  const DOMINATOR_PRIORITY={')
end = text.index('\n\n  const esc=', start)
text = text[:start] + dominator_new + text[end:]

# Durable maintenance rule: current recommendations may consider verified next-tier carryover,
# but never recommend unavailable future skills in the current build panel.
policy = Path('.github/build-maintenance.md')
policy_text = policy.read_text(encoding='utf-8')
anchor = '- **Investment recommendations must come from Techniques/Charms actually equipped in the displayed loadouts.** Do not rank wishlist, swap-only, or unrelated pieces as core investments. If an item is only a situational swap, keep it in the build note instead of the ranked investment panel.\n'
addition = anchor + '- **Weight investment ranks by longevity when credible next-tier guides exist.** A current equipped Technique/Charm that is explicitly retained next tier should move up; a current piece that is largely replaced next tier should move down or be labeled a bridge investment. Never put unavailable future-tier skills into the current-season rank list, and when the next tier replaces most of a role\'s kit, explicitly recommend preserving scarce tickets after the useful current breakpoints.\n'
policy_text = replace_once(policy_text, anchor, addition, 'maintenance longevity rule')
policy.write_text(policy_text, encoding='utf-8')

p.write_text(text, encoding='utf-8')

# Post-patch invariants.
checks = {
    'conqueror long-term charm': 'Piercing Assault is the long-term spend',
    'destroyer t5 technique': 'Formation Breaker has real T5 longevity',
    'destroyer charm carryover': 'T5 carryovers before T4 tempo',
    'guardian support weighting': 'Valor Surge before Water ranks',
    'dominator save guidance': 'Carryovers first; then save',
    'dominator healer longevity': 'Phantom Light and Overhealing age extremely well',
}
for label, needle in checks.items():
    if needle not in text:
        raise SystemExit(f'missing {label}: {needle}')
if "['Seismic Tide','Keeps Cold stacking consistent" in text:
    raise SystemExit('stale Guardian DPS Seismic Tide investment remains')
print('T5 longevity investment reprioritization applied')
