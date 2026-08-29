from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
marker='NEXUS_TOURNAMENT_AUG30_LEAD_V1'
if marker in s:
    raise SystemExit('Nexus Tournament lead already present')
needle="""    ['2026-08-30',47,'Region','Loong Haven opens','CONFIRMED for Charming Glance: Season 2 Day 1 begins Aug 30 at the 6:00 AM PDT reset. On Aug 26 at about 8:15 AM PDT, the in-game season countdown showed 3d 21h remaining, aligning with this reset; Prydwen independently places T4 at Server Day 47. Once S2 is live: Lv.106 = T4 class advancement + Loong Haven Five; Fantomon Adult / Materialization requires Lv.108, Numbuville unlocked, and Mythic rarity (duplicate); Lv.116 = Demonbind Tower.','region'],
"""
insert=needle+"""    // NEXUS_TOURNAMENT_AUG30_LEAD_V1
    ['2026-08-30',47,'Event','Nexus Tournament · expected','UNCONFIRMED for Charming Glance: an Aug 29 community post says the next Tournament PvP event is starting soon. Community records show Nexus Tournament activity on Jul 19 and Aug 2, consistent with a roughly two-week Sunday cadence that points to Aug 30; exact Charming Glance registration/battle timing has not been independently verified. Check the in-game Event screen after rollover before relying on the window.','event',null,'unconfirmed'],
"""
if needle not in s:
    raise SystemExit('Loong Haven anchor not found')
s=s.replace(needle,insert,1)
p.write_text(s,encoding='utf-8')
