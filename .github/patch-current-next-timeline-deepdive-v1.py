from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')

rows = [
    "    ['2026-09-02',50,'Event','Grand Treasure Hunt (7) · Feneck’s Puzzle (2)','STRONGLY SUPPORTED / UNCONFIRMED FOR CHARMING GLANCE. Two independent older-server calendars place this rotation on Server Day 50: Grand Treasure Hunt (7) with a Class IV Skill Shard / 4th-job skill-fragment choice, plus Feneck’s Puzzle (2). Charming Glance Server Day 50 maps to Sep. 2. Treat 6:00 AM PDT reset availability as expected until the in-game Event screen confirms it.','event',null,'unconfirmed'],",
    "    ['2026-09-09',57,'Event','Grand Treasure Hunt (8) · Bingo Draw (3)','STRONGLY SUPPORTED / UNCONFIRMED FOR CHARMING GLANCE. Older-server calendars agree on Server Day 57 for Grand Treasure Hunt (8), featuring Primal Gem in the high-tier rotation, alongside Bingo Draw (3). Charming Glance Server Day 57 maps to Sep. 9.','event',null,'unconfirmed'],",
    "    ['2026-09-16',64,'Event','Grand Treasure Hunt (9) · Lucky Scratch (3)','STRONGLY SUPPORTED / UNCONFIRMED FOR CHARMING GLANCE. Older-server calendars agree on Server Day 64 for Grand Treasure Hunt (9), with the Miracle Relic selection-box rotation, alongside Lucky Scratch (3). Charming Glance Server Day 64 maps to Sep. 16.','event',null,'unconfirmed'],",
    "    ['2026-09-23',71,'Event','Grand Treasure Hunt (10) · Feneck’s Puzzle (3)','UNCONFIRMED Charming Glance projection from the established older-server Loong Haven cadence: Server Day 71 has Grand Treasure Hunt (10), with Lucky Idol in the high-tier rotation, plus Feneck’s Puzzle (3). Charming Glance Server Day 71 maps to Sep. 23.','event',null,'unconfirmed'],",
    "    ['2026-09-30',78,'Event','Grand Treasure Hunt (11) · Bingo Draw (4)','UNCONFIRMED Charming Glance projection from the older-server Loong Haven cadence: Server Day 78 has Grand Treasure Hunt (11), with a Class IV Skill Shard / 4th-job skill-fragment choice, plus Bingo Draw (4). This falls on the same projected day as Loong Haven Relic II.','event',null,'unconfirmed'],",
    "    ['2026-10-07',85,'Event','Grand Treasure Hunt (12) · Lucky Scratch (4)','UNCONFIRMED Charming Glance projection from the older-server Loong Haven cadence: Server Day 85 has Grand Treasure Hunt (12), with Primal Gem in the high-tier rotation, plus Lucky Scratch (4).','event',null,'unconfirmed'],",
    "    ['2026-10-14',92,'Event','Grand Treasure Hunt (13) · Feneck’s Puzzle (4)','UNCONFIRMED Charming Glance projection from the older-server Loong Haven cadence: Server Day 92 has Grand Treasure Hunt (13), with the Miracle Relic selection-box rotation, plus Feneck’s Puzzle (4). This is also the current Pandarial projection day.','event',null,'unconfirmed'],",
    "    ['2026-10-21',99,'Event','Grand Treasure Hunt (14) · Bingo Draw (5)','UNCONFIRMED Charming Glance projection from the older-server Loong Haven cadence: Server Day 99 has Grand Treasure Hunt (14), with Lucky Idol in the high-tier rotation, plus Bingo Draw (5). This is also the projected Celestship unlock day.','event',null,'unconfirmed'],",
    "    ['2026-10-28',106,'Event','Grand Treasure Hunt (15) · Lucky Scratch (5)','UNCONFIRMED Charming Glance projection from the older-server Loong Haven cadence: Server Day 106 has Grand Treasure Hunt (15), with a Class IV Skill Shard / 4th-job skill-fragment choice, plus Lucky Scratch (5).','event',null,'unconfirmed'],",
    "    ['2026-11-04',113,'Event','Grand Treasure Hunt (16) · Feneck’s Puzzle (5)','UNCONFIRMED Charming Glance projection from the older-server Loong Haven cadence: Server Day 113, the day before the projected Aethyris rollover, has Grand Treasure Hunt (16), with Primal Gem in the high-tier rotation, plus Feneck’s Puzzle (5).','event',null,'unconfirmed'],",
]

# Insert all newly researched S2 recurring events immediately before the existing Sep. 12 dungeon row.
marker = "Grand Treasure Hunt (7) · Feneck’s Puzzle (2)"
anchor = "    ['2026-09-12',60,'Dungeon','Warlord’s Rest'"
if marker not in text:
    pos = text.find(anchor)
    if pos == -1:
        raise SystemExit('S2 insertion anchor not found')
    block = '\n'.join(rows) + '\n'
    text = text[:pos] + block + text[pos:]

# Add the T5 advancement gate after the Aethyris region row.
t5_marker = "Tier 5 class advancement"
if t5_marker not in text:
    lines = text.splitlines()
    out = []
    inserted = False
    for line in lines:
        out.append(line)
        if (not inserted and "['2026-11-05',114,'Region','Aethyris opens'" in line):
            out.append("    ['2026-11-05',114,'Class Advancement','Tier 5 class advancement','UNCONFIRMED FOR CHARMING GLANCE but strongly supported by the older-server Aethyris schedule and current end-of-S2 community reports: Aethyris / T5 opens on Server Day 114, with class advancement gated by Player Lv.136 · total Class Lv.180 · Tier 4 class Lv.40. Charming Glance Server Day 114 maps to Nov. 5. Actual advancement may take additional days if Lv.136 is not reached at rollover.','class-advancement',null,'unconfirmed'],")
            inserted = True
    if not inserted:
        raise SystemExit('Aethyris anchor not found')
    text = '\n'.join(out) + ('\n' if text.endswith('\n') else '')

# Add next-season milestones that are explicitly listed on the current older-server Aethyris calendar.
s3_marker = "Order Temple"
if s3_marker not in text:
    lines = text.splitlines()
    out = []
    inserted = False
    s3_rows = [
        "    ['2026-11-11',120,'Event','Grand Treasure Hunt (17) · Bingo Draw (8)','UNCONFIRMED Charming Glance projection from the older-server Aethyris calendar: Server Day 120 has Grand Treasure Hunt (17), with the Miracle Relic selection-box rotation, plus Bingo Draw (8). This is the first explicitly listed recurring-event rotation after the projected Season 3 rollover.','event',null,'unconfirmed'],",
        "    ['2026-12-30',169,'Dungeon','Order Temple','UNCONFIRMED Charming Glance projection from the older-server Aethyris calendar at Server Day 169. Normal 55M · Hard 65M · Nightmare 82M · Purgatory 115M. Global-English localization and the exact Charming Glance date should be rechecked as S3 approaches.','dungeon',null,'unconfirmed'],",
        "    ['2027-01-04',174,'Ancient Relic','Azure Radiance Codex','UNCONFIRMED Charming Glance projection from the older-server Aethyris calendar: Server Day 174 · Aethyris/Feather-region Phase 3 Ancient Relic. Name is the current community English rendering and should be replaced if Global localizes it differently.','ancient-relic',null,'unconfirmed'],",
        "    ['2027-01-13',183,'Dungeon','Blazing Sun Spire','UNCONFIRMED Charming Glance projection from the older-server Aethyris calendar at Server Day 183. Normal 84.5M · Hard 100M · Nightmare 120M · Purgatory 180M.','dungeon',null,'unconfirmed'],",
        "    ['2027-01-27',197,'Dungeon','Sovereign’s Nest','UNCONFIRMED Charming Glance projection from the older-server Aethyris calendar at Server Day 197. Normal 125M · Hard 145M · Nightmare 180M · Purgatory 250M.','dungeon',null,'unconfirmed'],",
        "    ['2027-02-02',203,'Dungeon','Sovereign’s Nest · Abyss','UNCONFIRMED Charming Glance projection from the older-server Aethyris calendar: Abyss difficulty opens on Server Day 203 at 350M power.','dungeon',null,'unconfirmed'],",
        "    ['2027-02-11',212,'Region','Harpadia / Season 4 boundary','UNCONFIRMED long-range boundary. The current older-server roadmap/calendar spans Aethyris through Server Day 211 and lists Harpadia as the following region/Tier 6 season. If that cadence is unchanged, Charming Glance Server Day 212 maps to Feb. 11, 2027. Keep this as a planning marker only until Global or the in-game telescope/countdown confirms it.','region',null,'unconfirmed'],",
    ]
    for line in lines:
        out.append(line)
        if (not inserted and "['2026-11-05',114,'Dungeon','Crystalline Spiralwood'" in line):
            out.extend(s3_rows)
            inserted = True
    if not inserted:
        raise SystemExit('Crystalline Spiralwood anchor not found')
    text = '\n'.join(out) + ('\n' if text.endswith('\n') else '')

path.write_text(text, encoding='utf-8')
print('current + next season timeline deep-dive patch applied')
