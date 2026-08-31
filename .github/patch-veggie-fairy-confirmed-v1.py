from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')
old = "    ['2026-09-07',55,'Collab','Vegetable Fairy Part Two','Expected Sep 7 according to LDShop’s Aug 18 Oceanic Festival guide, which says the next collaboration is expected on that date. No official Global announcement or Charming Glance-specific confirmation has been found yet, so timing and applicability may change.','event',null,'unconfirmed'],"
new = "    ['2026-09-07',55,'Collab','Vegetable Fairy Part Two','CONFIRMED by the official Sword x Staff Global announcements channel on Aug. 31: Sword x Staff × Vegetables Fairy Collab Pt. 2 is coming soon. The previously reported Sep. 7 date remains the expected start date, but the official announcement did not state an exact launch date, so Sep. 7 remains date-unconfirmed until the in-game Event screen or an official dated notice confirms it. The announcement also teases a Fantomon coming with the collab.','event',null,'confirmed'],"
if old not in s:
    raise SystemExit('target Vegetable Fairy timeline row not found')
s = s.replace(old, new, 1)
p.write_text(s, encoding='utf-8')
print('VEGGIE_FAIRY_CONFIRMED_V1')
