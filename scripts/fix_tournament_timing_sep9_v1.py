from pathlib import Path

path = Path('index.html')
s = path.read_text(encoding='utf-8')

old = """    // TOURNAMENT_WEEKDAY_MODEL_V1: Server Tournament = Saturday; Nexus Tournament = Sunday.\n    ['2026-09-05',53,'Event','Server Tournament','CONFIRMED FOR CHARMING GLANCE from the in-game Tournament screen captured Sep. 2 at about 8:00 AM PDT: registration begins at the Sep. 4 6:00 AM PDT reset, and the user confirmed registration opens one day before the non-Nexus tournament. The timeline therefore shows the actual Server Tournament on Sat Sep. 5 rather than the registration day, keeping it clearly distinct from Nexus Tournament.','event'],\n    ['2026-09-13',61,'Event','Nexus Tournament · 4v4','Nexus Tournament runs Sunday. The earlier Sep. 12 countdown was interpreted as the tournament itself, but it corresponds to the lead-in / preparation timing rather than the Sunday tournament day. Top-4 qualification format remains community-corroborated; bracket and prediction subphases are handled in game.','event'],\n    ['2026-09-27',75,'Event','Nexus Tournament · 4v4','14-day Nexus cadence following the Sunday Sep. 13 tournament. Recheck the in-game phase timer as the date approaches.','event'],\n    ['2026-10-11',89,'Event','Nexus Tournament · 4v4','14-day Nexus cadence following the Sunday Sep. 13 tournament. Recheck the in-game phase timer as the date approaches.','event'],\n    ['2026-10-25',103,'Event','Nexus Tournament · 4v4','14-day Nexus cadence following the Sunday Sep. 13 tournament; likely the final S2 Nexus before rollover. Recheck the in-game phase timer as the date approaches.','event'],\n"""

new = """    // TOURNAMENT_TIMING_SEP9_V1: direct Charming Glance screenshots taken just after midnight Sep. 9 PDT.\n    // Standard Tournament registration showed ~2d 5h remaining (Friday reset); Nexus itself showed ~3d 19h to start (Saturday evening).\n    ['2026-09-05',53,'Event','Server Tournament','The weekly Server Tournament runs Saturday; registration opens the day before.','event'],\n    ['2026-09-12',60,'Event','Server Tournament','Registration opens Friday Sep. 11 · tournament Saturday Sep. 12.','event'],\n    ['2026-09-12',60,'Event','Nexus Tournament · 4v4','Direct Charming Glance countdown just after midnight Sep. 9 showed 3d 19h to start, placing Nexus on Saturday evening Sep. 12.','event'],\n    ['2026-09-26',74,'Event','Nexus Tournament · 4v4','14-day Nexus cadence following the Saturday Sep. 12 tournament. Recheck the in-game timer as the date approaches.','event'],\n    ['2026-10-10',88,'Event','Nexus Tournament · 4v4','14-day Nexus cadence following the Saturday Sep. 12 tournament. Recheck the in-game timer as the date approaches.','event'],\n    ['2026-10-24',102,'Event','Nexus Tournament · 4v4','14-day Nexus cadence following the Saturday Sep. 12 tournament; likely the final S2 Nexus before rollover.','event'],\n"""

if old not in s:
    raise SystemExit('Expected tournament block not found')
s = s.replace(old, new, 1)

old_summary = "    if(title==='Server Tournament') return 'Registration opens Sep. 4 · tournament Sep. 5.';"
new_summary = "    if(title==='Server Tournament') return e[0]==='2026-09-12' ? 'Registration opens Friday Sep. 11 · tournament Saturday Sep. 12.' : 'Registration opens the day before · tournament Saturday.';"
if old_summary not in s:
    raise SystemExit('Expected Server Tournament summary not found')
s = s.replace(old_summary, new_summary, 1)

for needle in [
    "TOURNAMENT_TIMING_SEP9_V1",
    "['2026-09-12',60,'Event','Server Tournament'",
    "['2026-09-12',60,'Event','Nexus Tournament · 4v4'",
    "['2026-09-26',74,'Event','Nexus Tournament · 4v4'",
    "['2026-10-10',88,'Event','Nexus Tournament · 4v4'",
    "['2026-10-24',102,'Event','Nexus Tournament · 4v4'",
]:
    if needle not in s:
        raise SystemExit(f'Missing expected tournament marker: {needle}')

path.write_text(s, encoding='utf-8')
print('Corrected Tournament/Nexus timing from Sep. 9 Charming Glance screenshots.')
