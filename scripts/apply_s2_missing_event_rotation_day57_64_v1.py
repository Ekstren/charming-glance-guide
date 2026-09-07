from pathlib import Path

path = Path('index.html')
s = path.read_text(encoding='utf-8')

marker = "S2_EVENT_ROTATION_DAY57_64_V1"
if marker in s:
    print('Missing S2 event rotations already patched.')
    raise SystemExit(0)

anchor = "    ['2026-09-12',60,'Dungeon','Warlord’s Rest','Normal 3.55M + Player Lv.130 · Hard 5M · Nightmare 6M','dungeon'],"
if anchor not in s:
    raise SystemExit('Warlord’s Rest anchor not found')

insert = r'''    // S2_EVENT_ROTATION_DAY57_64_V1
    ['2026-09-09',57,'Event','Treasure Hunt 8 + Bingo Draw 3','PROJECTED / EXPECTED from a current Global older-server guild calendar that explicitly maps Treasure Hunt 8 + Bingo Draw 3 to Server Day 57, with Primal Gem as the highlighted Treasure Hunt relic. Charming Glance Server Day 57 maps to Sep. 9. This fills a previously missing weekly rotation between the confirmed Sep. 7 collab launch and the existing later S2 event rows; verify the exact reward set in game when the event opens.','event'],
    ['2026-09-16',64,'Event','Treasure Hunt 9 + Lucky Scratch 3','PROJECTED / EXPECTED from the same current Global older-server guild calendar, which places Treasure Hunt 9 + Lucky Scratch 3 on Server Day 64 and describes the Treasure Hunt reward as a Miracle Relic Box choice. Charming Glance Server Day 64 maps to Sep. 16. Treat the exact reward choice and event pairing as projected until Charming Glance’s in-game event calendar appears.','event'],
'''

s = s.replace(anchor, insert + anchor, 1)

for needle in [
    marker,
    "['2026-09-09',57,'Event','Treasure Hunt 8 + Bingo Draw 3'",
    "['2026-09-16',64,'Event','Treasure Hunt 9 + Lucky Scratch 3'",
    'Primal Gem as the highlighted Treasure Hunt relic',
    'Miracle Relic Box choice'
]:
    if needle not in s:
        raise SystemExit(f'Missing expected patch marker: {needle}')

path.write_text(s, encoding='utf-8')
print('Added projected S2 event rotations for Server Days 57 and 64.')
