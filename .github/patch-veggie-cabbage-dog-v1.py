from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')
old = "    ['2026-09-07',55,'Collab','Vegetable Fairy Part Two','CONFIRMED by the official Sword x Staff Global announcements channel on Aug. 31: Sword x Staff × Vegetables Fairy Collab Pt. 2 is coming soon. The previously reported Sep. 7 date remains the expected start date, but the official announcement did not state an exact launch date, so Sep. 7 remains date-unconfirmed until the in-game Event screen or an official dated notice confirms it. The announcement also teases a Fantomon coming with the collab.','event',null,'confirmed'],"
new = "    ['2026-09-07',55,'Collab','Vegetables Fairy Part Two · Cabbage Dog','CONFIRMED by the official Sword x Staff Global announcements channel on Aug. 31: Sword x Staff × Vegetables Fairy Collab Pt. 2 is coming soon, with the announcement headline naming Cabbage Dog and the body teasing that the Fantomon is coming too. Existing Fantomon databases also identify Cabbage Dog as a Fantomon. The previously reported Sep. 7 date remains expected only because the official announcement did not state an exact launch date; keep the date unconfirmed until the in-game Event screen or an official dated notice confirms it. Do not change Main/Alt build recommendations until the live Global release establishes Cabbage Dog’s actual availability and performance.','event',null,'confirmed'],"
if old not in s:
    raise SystemExit('current Vegetables Fairy row not found')
s = s.replace(old, new, 1)
p.write_text(s, encoding='utf-8')
print('VEGGIE_CABBAGE_DOG_V1')
