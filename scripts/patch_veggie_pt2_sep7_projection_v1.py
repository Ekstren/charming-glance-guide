from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

old = "    ['2026-09-09',57,'Collab','Vegetables Fairy Collab Pt. 2 · projected launch','PROJECTED / EXPECTED, not a confirmed Global launch date. Official Global announcements on Aug. 31 confirmed Pt. 2 is coming soon and specifically teased the Cabbage Dog Fantomon; the mirrored official Discord showcase on Sep. 2 also confirmed collab-exclusive Visages including Spicy Chick Plush, Rose Dog Plush, Violet Kitty, Chili/Eggplant/Rose weapons, and themed headwear. Neither announcement gave an exact launch date. Sep. 9 remains the single lead projection because the original CN Pt. 2 was teased Aug. 11, 2025 and launched Aug. 18 (7 days later), while Global code VEGGIE expires immediately beforehand on Sep. 8. The older Sep. 7 Cabbage Dog projection was removed to avoid showing two conflicting launch dates for the same collab. Re-date this row as soon as Global posts the exact event window.','event'],"
new = "    ['2026-09-07',55,'Collab','Vegetables Fairy Collab Pt. 2 · projected launch','PROJECTED / EXPECTED, not a confirmed Global launch date. Official Global announcements on Aug. 31 confirmed Pt. 2 is coming soon and specifically teased the Cabbage Dog Fantomon; the mirrored official Discord showcase on Sep. 2 also confirmed collab-exclusive Visages including Spicy Chick Plush, Rose Dog Plush, Violet Kitty, Chili/Eggplant/Rose weapons, and themed headwear, but neither official post gave an exact event window. Sep. 7 is now the lead projection because the original CN Pt. 2 launched 7 days after its Aug. 11, 2025 teaser, which maps the Global Aug. 31 coming-soon teaser to Sep. 7, and LDShop’s current Oceanic Festival guide independently expects Vegetables Fairy Part Two on Sep. 7. The VEGGIE code remains valid until Sep. 7 at 10:00 PM PDT, so a launch earlier that day is possible; the previous Sep. 9 post-expiry estimate is retained here only as the conflicting later inference, not as a confirmed date. Re-date this row immediately when Global posts the exact event window.','event'],"

if new in s:
    print('VEGGIE_PT2_SEP7_PROJECTION_V1 already applied')
    raise SystemExit(0)
if old not in s:
    raise SystemExit('current Sep 9 Vegetables Fairy projection row not found')

s = s.replace(old, new, 1)
p.write_text(s, encoding='utf-8')
print('VEGGIE_PT2_SEP7_PROJECTION_V1')
