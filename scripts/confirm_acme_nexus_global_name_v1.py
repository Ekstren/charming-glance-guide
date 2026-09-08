from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
old="""    ['2026-09-13',61,'Seasonal Map','Acme Nexus','UNCONFIRMED TIMING. QY-derived Season 2 scheduling places this Loong Haven seasonal map on S2 Day 15 / Server Day 61, which maps to Sep. 13 for Charming Glance. A separate older-server calendar instead lists the equivalent seasonal-map milestone as “Sky Tower” on Server Day 71, which would map to Sep. 23. Keep Sep. 13 as the current lead projection, but treat the date and Global-English name as unresolved until Charming Glance’s in-game unlock/telescope confirms which cadence applies.','seasonal-map',null,'unconfirmed'],"""
new="""    ['2026-09-13',61,'Seasonal Map','Acme Nexus','OFFICIAL GLOBAL NAME confirmed by the Sword x Staff Global announcements feed on Sep. 7: the Aethyris dungeon preview explicitly says “Reach the top of Acme Nexus, and Aethyris awaits,” confirming Acme Nexus as the current Global-English name and its role immediately before Aethyris. TIMING REMAINS PROJECTED: QY-derived Season 2 scheduling places the Loong Haven seasonal map on S2 Day 15 / Server Day 61, which maps to Sep. 13 for Charming Glance, while a separate older-server calendar lists the equivalent seasonal-map milestone on Server Day 71 (Sep. 23). Keep Sep. 13 as the lead projection until Charming Glance’s in-game unlock/telescope resolves the cadence conflict.','seasonal-map',null,'unconfirmed'],"""
if old not in s:
    if new in s:
        print('Acme Nexus official-name confirmation already applied.')
        raise SystemExit(0)
    raise SystemExit('Acme Nexus timeline anchor not found')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')
print('Confirmed Acme Nexus Global-English name while preserving date uncertainty.')
