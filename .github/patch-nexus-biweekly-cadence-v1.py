from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

old = """    ['2026-09-13',61,'Event','Nexus Tournament · 4v4','UNCONFIRMED Charming Glance projection, revised after a deeper cadence check. Older-Global S2 players explicitly describe the first Nexus as the SECOND weekend after Season 2 starts and as a Sunday event; with Charming Glance entering S2 on Sun Aug 30, that maps more naturally to Sun Sep 13, following the projected Sep 12 server Tournament qualifier. Qualification is strongly community-corroborated as top 4 teams from each server Tournament; an observed bracket had 16 teams from four servers. Event-details screenshots/discussion report only a ~5-minute prediction window, which appears to open once the bracket reaches the final four rather than at a fixed clock time. Community reward reports say participating/placing teams earn Honor Medal currency for the Nexus cosmetic shop; top 32 are reported to receive some medals, while the winning team receives the full cosmetic set temporarily for 7 days. Exact Charming Glance preparation, prediction and battle times remain unconfirmed.','event',null,'unconfirmed'],
"""
new = """    ['2026-09-13',61,'Event','Nexus Tournament · 4v4','STRONGLY SUPPORTED / UNCONFIRMED FOR CHARMING GLANCE. Multiple older-Global reports place Nexus on Sundays, and a player-provided older-server calendar independently shows Nexus 4v4 on Aug. 30 and Sep. 13 exactly 14 days apart. That calendar’s other S2 season-day milestones (Bladeshire Day 40, Pandarial Day 46, Celestship Day 53, season end Day 67) match the established roadmap, increasing confidence that Nexus follows a biweekly Sunday cadence after a server becomes eligible. Community reports also say the first Nexus is the second weekend after S2 begins; with Charming Glance entering S2 on Sun Aug. 30, Sep. 13 remains the best first-event projection. Top 4 teams from each server Tournament qualify; one observed bracket had 16 teams from four servers. Prediction appears to open for only about 5 minutes once the bracket reaches the final four. Exact Charming Glance battle time remains unconfirmed.','event',null,'unconfirmed'],
    ['2026-09-26',74,'Event','Server Tournament · Nexus qualifier','UNCONFIRMED recurring projection. If the newly corroborated 14-day Sunday Nexus cadence holds for Charming Glance, the next server Tournament qualifier should occur the preceding Saturday, Sep. 26. Qualification format is community-corroborated as top 4 teams advancing to Nexus.','event',null,'unconfirmed'],
    ['2026-09-27',75,'Event','Nexus Tournament · 4v4','UNCONFIRMED recurring projection from the older-server biweekly Sunday cadence: two weeks after the projected Sep. 13 Charming Glance Nexus.','event',null,'unconfirmed'],
    ['2026-10-10',88,'Event','Server Tournament · Nexus qualifier','UNCONFIRMED recurring projection. If the biweekly Nexus cadence continues unchanged, the qualifying server Tournament should be the preceding Saturday, Oct. 10.','event',null,'unconfirmed'],
    ['2026-10-11',89,'Event','Nexus Tournament · 4v4','UNCONFIRMED recurring projection from the older-server biweekly Sunday cadence: two weeks after Sep. 27.','event',null,'unconfirmed'],
    ['2026-10-24',102,'Event','Server Tournament · Nexus qualifier','UNCONFIRMED recurring projection. If the biweekly Nexus cadence continues unchanged, the qualifying server Tournament should be the preceding Saturday, Oct. 24.','event',null,'unconfirmed'],
    ['2026-10-25',103,'Event','Nexus Tournament · 4v4','UNCONFIRMED recurring projection from the older-server biweekly Sunday cadence: two weeks after Oct. 11 and likely the final S2 Nexus before the projected Nov. 5 rollover.','event',null,'unconfirmed'],
"""

if old not in s:
    raise SystemExit('target Nexus row not found')
s = s.replace(old, new, 1)

p.write_text(s, encoding='utf-8')
print('patched Nexus cadence')
