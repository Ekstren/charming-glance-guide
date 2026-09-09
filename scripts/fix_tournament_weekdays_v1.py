from pathlib import Path

path = Path('index.html')
s = path.read_text(encoding='utf-8')

replacements = {
"['2026-09-12',60,'Event','Nexus Tournament · 4v4','CONFIRMED FOR CHARMING GLANCE from the in-game Nexus screen captured Sep. 2 at about 8:00 AM PDT: “Starts in 10d 12h,” placing the start at about Sat Sep. 12, 8:00 PM PDT. This supersedes the older-server Sunday projection. Top-4 qualification format remains community-corroborated; prediction/bracket subphase timing should still be checked in game.','event'],":
"['2026-09-13',61,'Event','Nexus Tournament · 4v4','Nexus Tournament runs Sunday. The earlier Sep. 12 countdown was interpreted as the tournament itself, but it corresponds to the lead-in / preparation timing rather than the Sunday tournament day. Top-4 qualification format remains community-corroborated; bracket and prediction subphases are handled in game.','event'],",
"['2026-09-26',74,'Event','Nexus Tournament · 4v4','PROJECTED from the now-confirmed Sep. 12 Charming Glance Nexus plus the previously corroborated 14-day older-server cadence. If the cadence holds, the next Nexus should be Sep. 26; exact start time remains unconfirmed until an in-game countdown appears.','event',null,'unconfirmed'],":
"['2026-09-27',75,'Event','Nexus Tournament · 4v4','14-day Nexus cadence following the Sunday Sep. 13 tournament. Recheck the in-game phase timer as the date approaches.','event'],",
"['2026-10-10',88,'Event','Nexus Tournament · 4v4','PROJECTED from the confirmed Sep. 12 Charming Glance Nexus and the corroborated 14-day cadence. If unchanged, the next cycle should land Oct. 10; exact start time remains unconfirmed.','event',null,'unconfirmed'],":
"['2026-10-11',89,'Event','Nexus Tournament · 4v4','14-day Nexus cadence following the Sunday Sep. 13 tournament. Recheck the in-game phase timer as the date approaches.','event'],",
"['2026-10-24',102,'Event','Nexus Tournament · 4v4','PROJECTED from the confirmed Sep. 12 Charming Glance Nexus and the corroborated 14-day cadence. If unchanged, this cycle should land Oct. 24 and is likely the final S2 Nexus before the projected Nov. 5 rollover; exact start time remains unconfirmed.','event',null,'unconfirmed'],":
"['2026-10-25',103,'Event','Nexus Tournament · 4v4','14-day Nexus cadence following the Sunday Sep. 13 tournament; likely the final S2 Nexus before rollover. Recheck the in-game phase timer as the date approaches.','event'],",
}

for old, new in replacements.items():
    if old not in s:
        raise SystemExit(f'Missing expected tournament row: {old[:90]}')
    s = s.replace(old, new, 1)

# Guard the weekday model directly in maintained source comments.
needle = "    ['2026-09-05',53,'Event','Server Tournament'"
if needle not in s:
    raise SystemExit('Server Tournament row missing')

marker = "    // TOURNAMENT_WEEKDAY_MODEL_V1: Server Tournament = Saturday; Nexus Tournament = Sunday.\n"
if marker not in s:
    s = s.replace("    ['2026-09-05',53,'Event','Server Tournament'", marker + "    ['2026-09-05',53,'Event','Server Tournament'", 1)

for expected in [
    "['2026-09-05',53,'Event','Server Tournament'",
    "['2026-09-13',61,'Event','Nexus Tournament · 4v4'",
    "['2026-09-27',75,'Event','Nexus Tournament · 4v4'",
    "['2026-10-11',89,'Event','Nexus Tournament · 4v4'",
    "['2026-10-25',103,'Event','Nexus Tournament · 4v4'",
]:
    if expected not in s:
        raise SystemExit(f'Missing corrected tournament row: {expected}')

for forbidden in [
    "['2026-09-12',60,'Event','Nexus Tournament · 4v4'",
    "['2026-09-26',74,'Event','Nexus Tournament · 4v4'",
    "['2026-10-10',88,'Event','Nexus Tournament · 4v4'",
    "['2026-10-24',102,'Event','Nexus Tournament · 4v4'",
]:
    if forbidden in s:
        raise SystemExit(f'Old Saturday Nexus row still present: {forbidden}')

path.write_text(s, encoding='utf-8')
print('Corrected tournament weekdays: Server Saturday, Nexus Sunday.')
