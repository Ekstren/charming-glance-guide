from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

row57_title = 'Treasure Hunt 8 + Bingo Draw 3'
row64_title = 'Treasure Hunt 9 + Lucky Scratch 3'

row57 = "    ['2026-09-09',57,'Event','Treasure Hunt 8 + Bingo Draw 3','PROJECTED / EXPECTED from a current older-server community timeline whose Day 47 Tier 4 / Demonseal Gorge and Day 60 Warlord’s Rest milestones match the established server-day cadence. That timeline places Treasure Hunt 8 on Server Day 57 with Primal Gem as the highlighted relic reward, alongside Bingo Draw 3. For Charming Glance, Server Day 57 maps to Sep. 9. Treat the exact reward pool and event pairing as projected until the in-game event calendar appears.','event',null,'unconfirmed'],\n"
row64 = "    ['2026-09-16',64,'Event','Treasure Hunt 9 + Lucky Scratch 3','PROJECTED / EXPECTED from the same older-server event calendar: Treasure Hunt 9 lands on Server Day 64 with a Miracle Relic Box choice, paired with Lucky Scratch 3. Charming Glance Server Day 64 maps to Sep. 16. The cadence is useful for planning but remains unconfirmed for Charming Glance until the in-game event calendar/countdown appears.','event',null,'unconfirmed'],\n"

if row57_title not in s:
    anchor57 = "    ['2026-09-07',55,'Collab','Vegetables Fairy Collab Pt. 2 · projected launch'"
    pos = s.find(anchor57)
    if pos < 0:
        raise SystemExit('Could not find Sep 7 collab anchor; refusing blind edit')
    end = s.find('\n', pos)
    if end < 0:
        raise SystemExit('Could not find end of Sep 7 collab row')
    s = s[:end+1] + row57 + s[end+1:]

if row64_title not in s:
    anchor64 = "    ['2026-09-13',61,'Seasonal Map','Acme Nexus'"
    pos = s.find(anchor64)
    if pos < 0:
        raise SystemExit('Could not find Acme Nexus anchor; refusing blind edit')
    end = s.find('\n', pos)
    if end < 0:
        raise SystemExit('Could not find end of Acme Nexus row')
    s = s[:end+1] + row64 + s[end+1:]

p.write_text(s, encoding='utf-8')
print('Added projected S2 Day 57/64 recurring event rotations')
