from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

title = 'Official Top-Up Platform events open'
if title in s:
    print('Official top-up timeline row already present')
    raise SystemExit(0)

anchor = "    ['2026-09-01',49,'Event','Gift code · VEGGIE','Confirmed by the official Sword x Staff Global Discord gift-code announcement: 10 Rare Auroral Badges + 80 Dawnium. Active now. Official validity ends Sep. 8 at 00:00 (UTC-5), which is Sep. 7 at 10:00 PM PDT for Charming Glance. Redeem before 10:00 PM PDT Sep. 7.','event','2026-09-08',null,'2026-09-08T05:00:00Z'],\n"
if anchor not in s:
    raise SystemExit('Could not find VEGGIE timeline anchor; refusing blind edit')

row = "    ['2026-09-06',54,'Event','Official Top-Up Platform events open','CONFIRMED by the official Sword x Staff Global announcements feed on Sep. 4. The Official Top-Up Platform launches two reward events at Sep. 7, 00:00 (UTC-5), which is Sep. 6 at 10:00 PM PDT for Charming Glance: Cumulative Top-up Lottery runs through Oct. 4, 23:59:59 (UTC-5), awarding 1 draw per 9,999 Vouchers topped up with prizes including 29,999 / 9,999 / 4,999 / 999 Vouchers; Daily Top-up Sign-in runs through Sep. 6, 2027 and gives 1 daily draw after any official-platform top-up, with prizes including Vouchers, Bond Trinket, and Covenite. These are paid top-up promotions, not a Charming Glance progression unlock, and they begin about 8 hours before the Sep. 7 server reset.','event','2026-10-05',null,'2026-09-07T05:00:00Z'],\n"

s = s.replace(anchor, anchor + row, 1)
p.write_text(s, encoding='utf-8')
print('Added official Sep 7 top-up platform events to timeline')
