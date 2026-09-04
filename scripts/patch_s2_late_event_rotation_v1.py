from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

rows=[
("    ['2026-09-25',73,'Dungeon','Cloudcrest Temple'", "    ['2026-09-23',71,'Event','Treasure Hunt 10 + Feneck\'s Puzzle 3','PROJECTED / EXPECTED from the same current Limitless server-age calendar used for the earlier S2 event rows. It places Treasure Hunt 10 on Server Day 71 with Lucky Idol as the highlighted relic, paired with Feneck\'s Puzzle 3. Charming Glance Server Day 71 maps to Sep. 23. Treat the exact reward/pairing as projected until the in-game event calendar appears.','event'],\n"),
("    ['2026-09-30',78,'Ancient Relic','Ethereal Oracle'", "    ['2026-09-30',78,'Event','Treasure Hunt 11 + Bingo Draw 4','PROJECTED / EXPECTED from the current Limitless server-age calendar. It places Treasure Hunt 11 on Server Day 78 with a Tier 4 skill-fragment choice, paired with Bingo Draw 4. Charming Glance Server Day 78 maps to Sep. 30. Treat the exact reward/pairing as projected until the in-game event calendar appears.','event'],\n"),
("    ['2026-10-08',86,'Dungeon','Bladeshire'", "    ['2026-10-07',85,'Event','Treasure Hunt 12 + Lucky Scratch 4','PROJECTED / EXPECTED from the current Limitless server-age calendar. It places Treasure Hunt 12 on Server Day 85 with Primal Gem as the highlighted relic, paired with Lucky Scratch 4. Charming Glance Server Day 85 maps to Oct. 7. Treat the exact reward/pairing as projected until the in-game event calendar appears.','event'],\n"),
("    ['2026-10-14',92,'Fantomon','Pandarial'", "    ['2026-10-14',92,'Event','Treasure Hunt 13 + Feneck\'s Puzzle 4','PROJECTED / EXPECTED from the current Limitless server-age calendar. It places Treasure Hunt 13 on Server Day 92 with a Miracle Relic Box choice, paired with Feneck\'s Puzzle 4. Charming Glance Server Day 92 maps to Oct. 14. Treat the exact reward/pairing as projected until the in-game event calendar appears.','event'],\n"),
("    ['2026-10-21',99,'Dungeon','Celestship'", "    ['2026-10-21',99,'Event','Treasure Hunt 14 + Bingo Draw 5','PROJECTED / EXPECTED from the current Limitless server-age calendar. It places Treasure Hunt 14 on Server Day 99 with Lucky Idol as the highlighted relic, paired with Bingo Draw 5. Charming Glance Server Day 99 maps to Oct. 21. Treat the exact reward/pairing as projected until the in-game event calendar appears.','event'],\n"),
("    // ---- Season 3 · Aethyris ----", "    ['2026-10-28',106,'Event','Treasure Hunt 15 + Lucky Scratch 5','PROJECTED / EXPECTED from the current Limitless server-age calendar. It places Treasure Hunt 15 on Server Day 106 with a Tier 4 skill-fragment choice, paired with Lucky Scratch 5. Charming Glance Server Day 106 maps to Oct. 28. Treat the exact reward/pairing as projected until the in-game event calendar appears.','event'],\n    ['2026-11-04',113,'Event','Treasure Hunt 16 + Feneck\'s Puzzle 5','PROJECTED / EXPECTED from the current Limitless server-age calendar. It places Treasure Hunt 16 on Server Day 113 with Primal Gem as the highlighted relic, paired with Feneck\'s Puzzle 5. Charming Glance Server Day 113 maps to Nov. 4, the day before the projected S3 rollover. Treat the exact reward/pairing as projected until the in-game event calendar appears.','event'],\n\n")
]

changed=False
for anchor,payload in rows:
    title=payload.split("','Event','",1)[1].split("'",1)[0]
    if title in s:
        continue
    idx=s.find(anchor)
    if idx<0:
        raise SystemExit(f'Anchor not found: {anchor}')
    s=s[:idx]+payload+s[idx:]
    changed=True

if changed:
    p.write_text(s,encoding='utf-8')
    print('Added late-S2 projected event rotation rows')
else:
    print('Late-S2 projected event rotation already present')
