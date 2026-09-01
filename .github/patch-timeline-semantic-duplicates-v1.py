from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

# These rows were added during the timeline deep-dive under alternate translated/community
# names even though the maintained QY/Global-name rows already existed. Keep one card per
# milestone and preserve the maintained/current-name version.
remove_rows = [
"    ['2026-11-18',127,'Dungeon','Eternal Flower Garden','UNCONFIRMED Charming Glance projection from the fixed older-server Aethyris schedule: Server Day 127. Normal 12.5M + Player Lv.160 · Hard 15M · Nightmare 18M · Purgatory 28.5M.','dungeon',null,'unconfirmed'],\n",
"    ['2026-11-19',128,'Seasonal Map','Starry Sea Cruise','UNCONFIRMED Charming Glance projection from the fixed older-server Aethyris schedule: seasonal map unlock on Server Day 128. Global-English localization may change before Charming Glance reaches it.','seasonal-map',null,'unconfirmed'],\n",
"    ['2026-12-02',141,'Dungeon','Battle Abyss Fortress','UNCONFIRMED Charming Glance projection from the fixed older-server Aethyris schedule: Server Day 141. Normal 20M · Hard 26M · Nightmare 30M · Purgatory 46M.','dungeon',null,'unconfirmed'],\n",
"    ['2026-12-05',144,'Ancient Relic','Celestial Covenant','UNCONFIRMED Charming Glance projection from the fixed older-server Aethyris schedule: Server Day 144 · Aethyris/Feather-region Phase 2 Ancient Relic. Name is current community English and should be replaced if Global localizes it differently.','ancient-relic',null,'unconfirmed'],\n",
"    ['2026-12-16',155,'Dungeon','Purification Garden','UNCONFIRMED Charming Glance projection from the fixed older-server Aethyris schedule: Server Day 155. Normal 32.5M · Hard 43M · Nightmare 50.5M · Purgatory 75M.','dungeon',null,'unconfirmed'],\n",
"    ['2026-12-21',160,'Fantomon','Rainbow Star Spirit','UNCONFIRMED Charming Glance projection from the fixed older-server Aethyris schedule: new Fantomon/Pet listed on Server Day 160. Do not treat it as available or alter Main/Alt recommendations until the Global release and actual skill text are confirmed.','fantomon',null,'unconfirmed'],\n",
"    ['2026-12-08',147,'Fantomon','Prismora','UNCONFIRMED mid-Season 3 projection. Current Sage/Dominator guidance from Loot & Waifus identifies Prismora as a Mythic Fantomon aimed specifically at healer builds and says it releases mid Season 3. Dec. 8 is only a midpoint estimate based on the projected Nov. 5 Charming Glance S3 start and should move if the S3 anchor changes or a server-day release is confirmed.','fantomon',null,'unconfirmed'],\n",
"    ['2026-12-30',169,'Dungeon','Order Temple','UNCONFIRMED Charming Glance projection from the older-server Aethyris calendar at Server Day 169. Normal 55M · Hard 65M · Nightmare 82M · Purgatory 115M. Global-English localization and the exact Charming Glance date should be rechecked as S3 approaches.','dungeon',null,'unconfirmed'],\n",
"    ['2027-01-04',174,'Ancient Relic','Azure Radiance Codex','UNCONFIRMED Charming Glance projection from the older-server Aethyris calendar: Server Day 174 · Aethyris/Feather-region Phase 3 Ancient Relic. Name is the current community English rendering and should be replaced if Global localizes it differently.','ancient-relic',null,'unconfirmed'],\n",
"    ['2027-01-13',183,'Dungeon','Blazing Sun Spire','UNCONFIRMED Charming Glance projection from the older-server Aethyris calendar at Server Day 183. Normal 84.5M · Hard 100M · Nightmare 120M · Purgatory 180M.','dungeon',null,'unconfirmed'],\n",
"    ['2027-01-27',197,'Dungeon','Sovereign’s Nest','UNCONFIRMED Charming Glance projection from the older-server Aethyris calendar at Server Day 197. Normal 125M · Hard 145M · Nightmare 180M · Purgatory 250M.','dungeon',null,'unconfirmed'],\n",
"    ['2027-02-02',203,'Dungeon','Sovereign’s Nest · Abyss','UNCONFIRMED Charming Glance projection from the older-server Aethyris calendar: Abyss difficulty opens on Server Day 203 at 350M power.','dungeon',null,'unconfirmed'],\n",
"    ['2027-02-14',215,'Region','Harpadia / Tier 6 boundary','UNCONFIRMED long-range planning marker. The fixed older-server schedule starts Harpadia / Tier 6 on Server Day 215, after Aethyris’s final listed Day 211 event rotation. Charming Glance Server Day 215 maps to Feb. 14, 2027. Do not treat this as a confirmed Charming Glance season-reset date until the in-game countdown/telescope appears.','region',null,'unconfirmed'],\n",
]

removed = 0
for row in remove_rows:
    if row in s:
        s = s.replace(row, '', 1)
        removed += 1

# Keep the current QY Season-4 projection as the single boundary row, but retain the
# older-server Day-215 conflict in Details instead of rendering a second region card.
old_hapadi = "    ['2027-02-25',226,'Region','Hapadi opens','Projected Season 4 start from QY’s current ~112-day S3 duration · “Hapadi” is already present in current Global relic data · QY reference: full 16-server merge. Absolute date remains merger-sensitive.','region'],"
new_hapadi = "    ['2027-02-25',226,'Region','Hapadi opens','UNCONFIRMED Charming Glance Season 4 projection. Current QY scheduling uses an ~112-day S3 and places Hapadi at Server Day 226 / Feb. 25. A separate fixed older-server calendar points to a Tier 6 boundary at Server Day 215 / Feb. 14, so the exact rollover remains unresolved; Feb. 25 stays the lead projection until the Charming Glance telescope/countdown or official Global notice confirms it. “Hapadi” is already present in current Global relic data.','region',null,'unconfirmed'],"
if old_hapadi in s:
    s = s.replace(old_hapadi, new_hapadi, 1)
elif new_hapadi not in s:
    raise SystemExit('Hapadi anchor row not found')

# The surviving Prismora row has the stronger server-day/QY basis. Make its projected
# status visible since Charming Glance has not reached S3 yet.
old_prismora = "    ['2026-12-20',159,'Fantomon','Prismora','Current Global Fantomon database name · QY roadmap label is Prismatic Astralite. Corrected to QY S3 Day 46 from the projected Nov 5 S3 anchor.','fantomon'],"
new_prismora = "    ['2026-12-20',159,'Fantomon','Prismora','UNCONFIRMED Charming Glance date. Current Global Fantomon database name · QY roadmap label is Prismatic Astralite. QY places it at S3 Day 46, which maps to Server Day 159 / Dec. 20 from the projected Nov. 5 S3 anchor. The older-server “Rainbow Star Spirit” label appears to describe this same pet/milestone, so that duplicate translated-name row has been retired.','fantomon',null,'unconfirmed'],"
if old_prismora in s:
    s = s.replace(old_prismora, new_prismora, 1)
elif new_prismora not in s:
    raise SystemExit('Prismora anchor row not found')

# Sanity checks: alternate-name duplicates must be gone; maintained rows must remain.
for marker in [
    "'Eternal Flower Garden'", "'Starry Sea Cruise'", "'Battle Abyss Fortress'",
    "'Celestial Covenant'", "'Purification Garden'", "'Rainbow Star Spirit'",
    "['2026-12-08',147,'Fantomon','Prismora'", "'Order Temple'", "'Azure Radiance Codex'",
    "'Blazing Sun Spire'", "['2027-02-02',203,'Dungeon','Sovereign’s Nest · Abyss'",
    "'Harpadia / Tier 6 boundary'"
]:
    if marker in s:
        raise SystemExit(f'duplicate marker still present: {marker}')

for marker in [
    "'Eternal Blossom Courtyard'", "'Astral Odyssey'", "'Abyssal Bastion'",
    "'Aethyris Relic II'", "'Courtyard of Purification'", "['2026-12-20',159,'Fantomon','Prismora'",
    "'Temple of Order'", "'Aethyris Relic III'", "'Solar Spire'",
    "Normal 125M · Hard 145M · Nightmare 180M · Purgatory 250M · Abyss 350M",
    "['2027-02-25',226,'Region','Hapadi opens'"
]:
    if marker not in s:
        raise SystemExit(f'maintained marker missing: {marker}')

if removed < 10:
    raise SystemExit(f'expected to remove many semantic duplicates; removed only {removed}')

p.write_text(s, encoding='utf-8')
print(f'Removed {removed} duplicate/conflicting timeline rows and consolidated S4/Prismora projections.')
