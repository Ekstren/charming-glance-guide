from pathlib import Path

path = Path('index.html')
s = path.read_text(encoding='utf-8')

old = "    ['2026-09-12',60,'Dungeon','Warlord’s Rest','Normal 3.55M + Player Lv.130 · Hard 5M · Nightmare 6M','dungeon'],"
new = "    ['2026-09-12',60,'Dungeon','Warlord’s Rest','CONFIRMED CHARMING GLANCE DATE + NORMAL REQUIREMENTS: an in-game Warlord’s Rest — Normal countdown captured on Sep. 8 at about 8:54 PM PDT showed 3d 09h 05m 54s remaining, resolving exactly to the Sep. 12, 2026 6:00 AM PDT server reset. The same Charming Glance unlock screen directly shows Player Lv.130 and 3.55M Power for Normal. Existing higher-difficulty requirements remain Hard 5M · Nightmare 6M; those two thresholds are not established by this Normal-mode screenshot.','dungeon'],"

if new in s:
    print("Warlord's Rest confirmation is already current; no change needed.")
elif old in s:
    s = s.replace(old, new, 1)
    path.write_text(s, encoding='utf-8')
    print("Upgraded Warlord's Rest Sep. 12 row to Charming Glance in-game confirmation.")
else:
    raise SystemExit("Could not find the expected Warlord's Rest timeline row")

for needle in [
    "'2026-09-12',60,'Dungeon','Warlord’s Rest'",
    'CONFIRMED CHARMING GLANCE DATE + NORMAL REQUIREMENTS',
    'Sep. 12, 2026 6:00 AM PDT server reset',
    'Player Lv.130 and 3.55M Power for Normal',
    'Hard 5M · Nightmare 6M'
]:
    if needle not in s:
        raise SystemExit(f'Missing expected Warlord confirmation marker: {needle}')
