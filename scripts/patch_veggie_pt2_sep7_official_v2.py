from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')

new_row = "    ['2026-09-07',55,'Collab','Vegetables Fairy Collab Pt. 2','CONFIRMED GLOBAL DATE from the official Sword x Staff announcements feed on Sep. 4: the official reward preview says only 3 days remain until the collab begins, placing the launch on Sep. 7. The post does not give an exact clock time or say it starts at Charming Glance reset, so this row confirms the calendar date without claiming a 6:00 AM PDT start. Confirmed Pt. 2 rewards/activities include daily sign-in rewards (Eggplant Mallet, Vegetable Cuddle Hairpin, Wheel Tickets and collab Emoticons), Golden Veggie Coins from event quests for the Veggie Shop, daily Veggie Shuffle stages toward the Violet Kitty Suit, and Lemon Whale purification 3 times for the Lemon Whale Plushie. Earlier official Global previews also confirmed the Cabbage Dog Fantomon and Pt. 2 Visages. Exact event end date remains unannounced.','event'],"

pattern = re.compile(r"^\s*\['2026-09-07',55,'Collab','Vegetables Fairy Collab Pt\. 2(?: · projected launch)?'.*?,'event'\],$", re.M)
match = pattern.search(s)
if not match:
    if new_row.strip() in s:
        print('VEGGIE_PT2_SEP7_OFFICIAL_V2 already applied')
        raise SystemExit(0)
    raise SystemExit('Sep. 7 Vegetables Fairy Pt. 2 timeline row not found')

s = s[:match.start()] + new_row + s[match.end():]
p.write_text(s, encoding='utf-8')
print('VEGGIE_PT2_SEP7_OFFICIAL_V2')
