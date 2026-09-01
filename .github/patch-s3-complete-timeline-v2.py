from pathlib import Path

p = Path('index.html')
text = p.read_text(encoding='utf-8')
lines = text.splitlines()

# Correct two items from the first deep-dive pass using the fresher fixed server-day calendar.
corrected = []
for line in lines:
    if "Grand Treasure Hunt (17) · Bingo Draw (8)" in line:
        line = "    ['2026-11-11',120,'Event','Grand Treasure Hunt (17) · Bingo Draw (6)','UNCONFIRMED Charming Glance projection, strongly supported by a fixed older-server Aethyris calendar: Server Day 120 has Treasure Hunt (17), with the Miracle Relic selection-box rotation, plus Bingo Draw (6). Charming Glance Server Day 120 maps to Nov. 11.','event',null,'unconfirmed'],"
    if "Harpadia / Season 4 boundary" in line:
        # Remove the earlier Day 212 extrapolation; the fixed older-server schedule has a short gap and starts Harpadia on Day 215.
        continue
    if "['2026-11-05',114,'Region','Aethyris opens'" in line:
        line = "    ['2026-11-05',114,'Region','Aethyris opens','STRONGLY SUPPORTED / UNCONFIRMED FOR CHARMING GLANCE. A fixed older-server Global timeline places Aethyris and Tier 5 on Server Day 114; Charming Glance Server Day 114 maps to Nov. 5 at the 6:00 AM PST reset. Keep the date unconfirmed until Charming Glance receives its in-game season countdown/telescope, but this is now a server-day schedule projection rather than a generic season-length estimate.','region',null,'unconfirmed'],"
    corrected.append(line)
lines = corrected
text = '\n'.join(lines) + ('\n' if text.endswith('\n') else '')

# Add the missing fixed-server-day Aethyris milestones and weekly rotations.
rows = [
    "    ['2026-11-18',127,'Dungeon','Eternal Flower Garden','UNCONFIRMED Charming Glance projection from the fixed older-server Aethyris schedule: Server Day 127. Normal 12.5M + Player Lv.160 · Hard 15M · Nightmare 18M · Purgatory 28.5M.','dungeon',null,'unconfirmed'],",
    "    ['2026-11-18',127,'Event','Grand Treasure Hunt (18) · Lucky Scratch (6)','UNCONFIRMED Charming Glance projection from Server Day 127: Treasure Hunt (18) rotates to Lucky Idol / Golden Divine Tree, alongside Lucky Scratch (6).','event',null,'unconfirmed'],",
    "    ['2026-11-19',128,'Seasonal Map','Starry Sea Cruise','UNCONFIRMED Charming Glance projection from the fixed older-server Aethyris schedule: seasonal map unlock on Server Day 128. Global-English localization may change before Charming Glance reaches it.','seasonal-map',null,'unconfirmed'],",
    "    ['2026-11-25',134,'Event','Grand Treasure Hunt (19) · Feneck’s Puzzle (6)','UNCONFIRMED Charming Glance projection from Server Day 134: Treasure Hunt (19) has a Tier V / 5th-job Skill Fragment choice, alongside Feneck’s Puzzle (6).','event',null,'unconfirmed'],",
    "    ['2026-12-02',141,'Dungeon','Battle Abyss Fortress','UNCONFIRMED Charming Glance projection from the fixed older-server Aethyris schedule: Server Day 141. Normal 20M · Hard 26M · Nightmare 30M · Purgatory 46M.','dungeon',null,'unconfirmed'],",
    "    ['2026-12-02',141,'Event','Grand Treasure Hunt (20) · Bingo Draw (7)','UNCONFIRMED Charming Glance projection from Server Day 141: Treasure Hunt (20) rotates to Primal Gem / Philosopher’s Stone, alongside Bingo Draw (7).','event',null,'unconfirmed'],",
    "    ['2026-12-05',144,'Ancient Relic','Celestial Covenant','UNCONFIRMED Charming Glance projection from the fixed older-server Aethyris schedule: Server Day 144 · Aethyris/Feather-region Phase 2 Ancient Relic. Name is current community English and should be replaced if Global localizes it differently.','ancient-relic',null,'unconfirmed'],",
    "    ['2026-12-09',148,'Event','Grand Treasure Hunt (21) · Lucky Scratch (7)','UNCONFIRMED Charming Glance projection from Server Day 148: Treasure Hunt (21) has the Miracle Relic selection-box rotation, alongside Lucky Scratch (7).','event',null,'unconfirmed'],",
    "    ['2026-12-16',155,'Dungeon','Purification Garden','UNCONFIRMED Charming Glance projection from the fixed older-server Aethyris schedule: Server Day 155. Normal 32.5M · Hard 43M · Nightmare 50.5M · Purgatory 75M.','dungeon',null,'unconfirmed'],",
    "    ['2026-12-16',155,'Event','Grand Treasure Hunt (22) · Feneck’s Puzzle (7)','UNCONFIRMED Charming Glance projection from Server Day 155: Treasure Hunt (22) rotates to Lucky Idol / Golden Divine Tree, alongside Feneck’s Puzzle (7).','event',null,'unconfirmed'],",
    "    ['2026-12-21',160,'Fantomon','Rainbow Star Spirit','UNCONFIRMED Charming Glance projection from the fixed older-server Aethyris schedule: new Fantomon/Pet listed on Server Day 160. Do not treat it as available or alter Main/Alt recommendations until the Global release and actual skill text are confirmed.','fantomon',null,'unconfirmed'],",
    "    ['2026-12-23',162,'Event','Grand Treasure Hunt (23) · Bingo Draw (8)','UNCONFIRMED Charming Glance projection from Server Day 162: Treasure Hunt (23) has a Tier V / 5th-job Skill Fragment choice, alongside Bingo Draw (8).','event',null,'unconfirmed'],",
    "    ['2026-12-30',169,'Event','Grand Treasure Hunt (24) · Lucky Scratch (8)','UNCONFIRMED Charming Glance projection from Server Day 169: Treasure Hunt (24) rotates to Primal Gem / Philosopher’s Stone, alongside Lucky Scratch (8).','event',null,'unconfirmed'],",
    "    ['2027-01-06',176,'Event','Grand Treasure Hunt (25) · Feneck’s Puzzle (8)','UNCONFIRMED Charming Glance projection from Server Day 176: Treasure Hunt (25) has the Miracle Relic selection-box rotation, alongside Feneck’s Puzzle (8).','event',null,'unconfirmed'],",
    "    ['2027-01-13',183,'Event','Grand Treasure Hunt (26) · Bingo Draw (9)','UNCONFIRMED Charming Glance projection from Server Day 183: Treasure Hunt (26) rotates to Lucky Idol / Golden Divine Tree, alongside Bingo Draw (9).','event',null,'unconfirmed'],",
    "    ['2027-01-20',190,'Event','Grand Treasure Hunt (27) · Lucky Scratch (9)','UNCONFIRMED Charming Glance projection from Server Day 190: Treasure Hunt (27) has a Tier V / 5th-job Skill Fragment choice, alongside Lucky Scratch (9).','event',null,'unconfirmed'],",
    "    ['2027-01-27',197,'Event','Grand Treasure Hunt (28) · Feneck’s Puzzle (9)','UNCONFIRMED Charming Glance projection from Server Day 197: Treasure Hunt (28) rotates to Primal Gem / Philosopher’s Stone, alongside Feneck’s Puzzle (9).','event',null,'unconfirmed'],",
    "    ['2027-02-03',204,'Event','Grand Treasure Hunt (29) · Bingo Draw (10)','UNCONFIRMED Charming Glance projection from Server Day 204: Treasure Hunt (29) has the Miracle Relic selection-box rotation, alongside Bingo Draw (10).','event',null,'unconfirmed'],",
    "    ['2027-02-10',211,'Event','Grand Treasure Hunt (30) · Lucky Scratch (10)','UNCONFIRMED Charming Glance projection from Server Day 211: Treasure Hunt (30) rotates to Lucky Idol / Golden Divine Tree, alongside Lucky Scratch (10). This is the final listed Aethyris recurring-event rotation on the fixed older-server calendar.','event',null,'unconfirmed'],",
    "    ['2027-02-14',215,'Region','Harpadia / Tier 6 boundary','UNCONFIRMED long-range planning marker. The fixed older-server schedule starts Harpadia / Tier 6 on Server Day 215, after Aethyris’s final listed Day 211 event rotation. Charming Glance Server Day 215 maps to Feb. 14, 2027. Do not treat this as a confirmed Charming Glance season-reset date until the in-game countdown/telescope appears.','region',null,'unconfirmed'],",
]

# Insert only missing rows near the S3 block. The renderer sorts by date, so source order is secondary.
marker = "Eternal Flower Garden"
if marker not in text:
    anchor = "    ['2026-11-05',114,'Dungeon','Crystalline Spiralwood'"
    pos = text.find(anchor)
    if pos == -1:
        raise SystemExit('S3 insertion anchor not found')
    end = text.find('\n', pos)
    if end == -1:
        raise SystemExit('S3 anchor line end not found')
    block = '\n' + '\n'.join(rows)
    text = text[:end] + block + text[end:]

p.write_text(text, encoding='utf-8')
print('S3 timeline completed and corrected')
