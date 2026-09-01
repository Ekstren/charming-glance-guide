from pathlib import Path

p = Path('index.html')
text = p.read_text(encoding='utf-8')
lines = text.splitlines()
out = []
changed = False
for line in lines:
    if "['2026-09-13',61,'Seasonal Map','Acme Nexus'" in line:
        out.append("    ['2026-09-13',61,'Seasonal Map','Acme Nexus','UNCONFIRMED TIMING. QY-derived Season 2 scheduling places this Loong Haven seasonal map on S2 Day 15 / Server Day 61, which maps to Sep. 13 for Charming Glance. A separate older-server calendar instead lists the equivalent seasonal-map milestone as “Sky Tower” on Server Day 71, which would map to Sep. 23. Keep Sep. 13 as the current lead projection, but treat the date and Global-English name as unresolved until Charming Glance’s in-game unlock/telescope confirms which cadence applies.','seasonal-map',null,'unconfirmed'],")
        changed = True
    else:
        out.append(line)
if not changed:
    raise SystemExit('Acme Nexus row not found')
p.write_text('\n'.join(out) + ('\n' if text.endswith('\n') else ''), encoding='utf-8')
print('Acme Nexus timing conflict tagged unconfirmed')
