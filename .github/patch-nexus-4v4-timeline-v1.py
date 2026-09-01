from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')
anchor = "    ['2026-09-07',55,'Collab','Vegetables Fairy Part Two · Cabbage Dog'"
idx = s.find(anchor)
if idx < 0:
    raise SystemExit('timeline anchor not found')
insert = "    ['2026-09-05',53,'Event','Server Tournament · Nexus qualifier','UNCONFIRMED Charming Glance projection. Community reports from older Global servers say the top 4 teams from each server Tournament qualify for the cross-server Nexus Tournament, and a July Nexus field was described as 16 teams made from the top 4 of four servers from the previous day’s server Tournament. If Charming Glance follows that cadence, the likely qualifier window is Sat Sep 5. No official Charming Glance registration or battle time has been posted yet.','event',null,'unconfirmed'],\n    ['2026-09-06',54,'Event','Nexus Tournament · 4v4','UNCONFIRMED Charming Glance projection. Current community evidence says Nexus 4v4 begins only after Season 2, with players on older servers describing the first S2 Nexus as the second weekend after S2 / the following Sunday. With Charming Glance entering S2 on Sun Aug 30, the best current projection is Sun Sep 6, likely following a server Tournament qualifier the previous day. Exact registration, preparation, prediction and battle times remain unconfirmed; community reports say the prediction window does not open until the bracket reaches the final four and may last only about 5 minutes. Top 4 server Tournament teams are reported to qualify.','event',null,'unconfirmed'],\n"
if "'Nexus Tournament · 4v4'" not in s:
    s = s[:idx] + insert + s[idx:]
else:
    raise SystemExit('Nexus 4v4 row already present')
p.write_text(s, encoding='utf-8')
print('NEXUS_4V4_TIMELINE_V1')
