from pathlib import Path

path = Path('index.html')
s = path.read_text(encoding='utf-8')

old = "    ['2026-11-05',114,'Region','Aethyris opens','STRONGLY SUPPORTED / UNCONFIRMED FOR CHARMING GLANCE. A fixed older-server Global timeline places Aethyris and Tier 5 on Server Day 114; Charming Glance Server Day 114 maps to Nov. 5 at the 6:00 AM PST reset. Keep the date unconfirmed until Charming Glance receives its in-game season countdown/telescope, but this is now a server-day schedule projection rather than a generic season-length estimate.','region',null,'unconfirmed'],"
new = "    ['2026-11-05',114,'Region','Aethyris opens','STRONGLY SUPPORTED / UNCONFIRMED FOR CHARMING GLANCE. A fixed older-server Global timeline places Aethyris and Tier 5 on Server Day 114; Charming Glance Server Day 114 maps to Nov. 5 at the 6:00 AM PST reset. Keep the date unconfirmed until Charming Glance receives its in-game season countdown/telescope, but this is now a server-day schedule projection rather than a generic season-length estimate. PROJECTED NEXUS CHANGE: multiple Global community reports agree that the cross-server Nexus group grows from 4 servers in S2 to 8 servers in S3/Aethyris. This is an expansion of the Nexus grouping rather than a literal character/server merge; verify the exact Charming Glance grouping at rollover.','region',null,'unconfirmed'],"

if new in s:
    print('S3 Nexus expansion note already current')
elif old in s:
    s = s.replace(old, new, 1)
    path.write_text(s, encoding='utf-8')
    print('Added projected S3 Nexus expansion note')
else:
    raise SystemExit('Aethyris timeline anchor not found; refusing broad edit')
