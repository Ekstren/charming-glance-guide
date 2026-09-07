from pathlib import Path

path = Path('index.html')
s = path.read_text(encoding='utf-8')
old = "    ['2026-11-05',114,'Dungeon','Crystalline Spiralwood','Normal · Hard 9M · pre-release English/data name until Global reaches S3','dungeon'],"
new = "    ['2026-11-05',114,'Dungeon','Crystal Spiral Tree','OFFICIAL GLOBAL NAME confirmed by the Sword x Staff Global announcements feed on Sep. 7: the Aethyris dungeon preview calls Crystal Spiral Tree the very first dungeon reached after entering Aethyris. The Nov. 5 Charming Glance placement remains PROJECTED from the current Server Day 114 / Season 3 rollover model; the official preview confirms the dungeon name and its position as Aethyris’s first dungeon, but does not confirm Charming Glance’s exact unlock date. Current older-server/data guidance still lists Hard at 9M; recheck the in-game requirement when S3 approaches.','dungeon'],"
if old not in s:
    if new in s:
        print('Crystal Spiral Tree timeline row already current.')
        raise SystemExit(0)
    raise SystemExit('Expected Crystalline Spiralwood timeline row not found')
s = s.replace(old, new, 1)
path.write_text(s, encoding='utf-8')
print('Updated Aethyris first dungeon to official Global name: Crystal Spiral Tree.')
