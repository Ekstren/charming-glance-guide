from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')

marker = 'ACME_NEXUS_DAY71_CORRECTION_SEP9_V1'
if marker in s:
    print('Acme Nexus Day 71 correction already applied.')
    raise SystemExit(0)

pattern = re.compile(
    r"    \['2026-09-13',61,'Seasonal Map','Acme Nexus','OFFICIAL GLOBAL NAME confirmed by the Sword x Staff Global announcements feed on Sep\. 7:.*?','seasonal-map',null,'unconfirmed'\],",
    re.S,
)
replacement = """    // ACME_NEXUS_DAY71_CORRECTION_SEP9_V1
    // Official Global confirms the Global-English name Acme Nexus and its gateway role before Aethyris.
    // Limitless Gaming's live older-server schedule places the Loong Haven seasonal map at Server Day 71.
    // That same schedule matches Charming Glance's established S2 milestones at Days 60, 73, 78, 86, 92 and 99,
    // so Day 71 is stronger cadence evidence than the earlier QY-derived Day 61 projection.
    ['2026-09-23',71,'Seasonal Map','Acme Nexus','Official Global name: Acme Nexus. Current older-server cadence places the Loong Haven seasonal map on Server Day 71, mapping to Sep. 23 for Charming Glance. It is the gateway immediately before Aethyris.','seasonal-map',null,'unconfirmed'],"""

s2, n = pattern.subn(replacement, s, count=1)
if n != 1:
    raise SystemExit(f'Expected exactly one Acme Nexus Day 61 row, found {n}')

p.write_text(s2, encoding='utf-8')
print('Moved Acme Nexus from Server Day 61 / Sep. 13 to Server Day 71 / Sep. 23.')
