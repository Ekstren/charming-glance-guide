from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')
orig = s

old_bed = "if(title==='Season 2 final-day prep') return 'Aug 29: sell unused S1 dungeon shards unless they buy another Primostar tier; bank dungeon attempts plus skill/relic pulls for S2. Bed EXP hold begins 34h before reset; full 36h banking remains unconfirmed.';"
new_bed = "if(title==='Season 2 final-day prep') return 'Historical rollover note: the Bed EXP hold used 34 hours of natural accumulation plus the single 2-hour reset boost, filling the 36-hour Bed capacity.';"
assert old_bed in s, 'stale Bed summary anchor missing'
s = s.replace(old_bed, new_bed, 1)

nexus = "    // NEXUS_TOURNAMENT_AUG30_LEAD_V1\n    ['2026-08-30',47,'Event','Nexus Tournament · expected','UNCONFIRMED for Charming Glance: an Aug 29 community post says the next Tournament PvP event is starting soon. Community records show Nexus Tournament activity on Jul 19 and Aug 2, consistent with a roughly two-week Sunday cadence that points to Aug 30; exact Charming Glance registration/battle timing has not been independently verified. Check the in-game Event screen after rollover before relying on the window.','event',null,'unconfirmed'],\n"
assert nexus in s, 'stale Nexus prediction anchor missing'
s = s.replace(nexus, '', 1)

old_s1 = "<p><b>Season 1:</b> 10 fixed stars plus 1 star per 100 cultivation score. Character = 100 points per seasonal level and 1 point per completed 1% EXP progress inside the level; Gear = 38; Skills = 13; Relics = 57 per level above +10; Fantomons = 14. Levels at or below 100 do not score. Fantomon upgrades use the next 10-level seasonal band, so Character Lv.130 opens Fantomons through Lv.140.</p>"
new_s1 = "<p><b>Season 1 carry-forward:</b> Season 1 / Tier III is retired from the live guide. Only historical values required by Season 2 calculations are retained internally, including carried S1 Primostars and cumulative Astral Pact math.</p>"
assert old_s1 in s, 'S1 formula paragraph anchor missing'
s = s.replace(old_s1, new_s1, 1)

old_ready = "<p><b>S2 Primostar calculator readiness:</b> Season 2 is preloaded as a separate scoring-only profile and does not replace Season 1. QY's current timeline confirms Season Power at Player Lv.130; Lv.120 is only the maximum S2 Material Realm bracket."
new_ready = "<p><b>S2 Primostar calculator:</b> Season 2 is the active Charming Glance scoring profile. Season 1 is retained only where carry-forward history is required. QY's current timeline confirms Season Power at Player Lv.130; Lv.120 is only the maximum S2 Material Realm bracket."
assert old_ready in s, 'S2 readiness paragraph anchor missing'
s = s.replace(old_ready, new_ready, 1)

# Guard intentional post-launch structure and Bed model.
for required in [
    "['Conqueror','Guardian','Destroyer','Dominator']",
    "Collect the banked 34 hours now",
    "Use the free 2-hour Bed boost",
    "45 + floor(score / 27)",
    "Arena",
    "Tournament",
]:
    assert required in s, f'required S2 content missing: {required}'

assert 'full 36h banking remains unconfirmed' not in s
assert 'Nexus Tournament · expected' not in s
assert 'does not replace Season 1' not in s
assert s != orig, 'no changes made'

p.write_text(s, encoding='utf-8')
print('Applied S2 post-launch cleanup v1')
