from pathlib import Path

path=Path('index.html')
s=path.read_text(encoding='utf-8')

old_a="""    ['2026-11-05',114,'Region','Aethyris opens','STRONGLY SUPPORTED / UNCONFIRMED FOR CHARMING GLANCE. A fixed older-server Global timeline places Aethyris and Tier 5 on Server Day 114; Charming Glance Server Day 114 maps to Nov. 5 at the 6:00 AM PST reset. Keep the date unconfirmed until Charming Glance receives its in-game season countdown/telescope, but this is now a server-day schedule projection rather than a generic season-length estimate. PROJECTED NEXUS CHANGE: multiple Global community reports agree that the cross-server Nexus group grows from 4 servers in S2 to 8 servers in S3/Aethyris. This is an expansion of the Nexus grouping rather than a literal character/server merge; verify the exact Charming Glance grouping at rollover.','region',null,'unconfirmed'],"""
new_a="""    // S3_AETHYRIS_SEP9_RESEARCH_V1: LDShop's Sep. 9 Season 3 guide independently names the Aethyris subzones Skyrend Cliff, Unbroken Camp, and Harmonic Crystal. Keep these names as current secondary-source localization until Global in-game text or an official announcement supersedes them.
    ['2026-11-05',114,'Region','Aethyris opens','STRONGLY SUPPORTED / UNCONFIRMED FOR CHARMING GLANCE. A fixed older-server Global timeline places Aethyris and Tier 5 on Server Day 114; Charming Glance Server Day 114 maps to Nov. 5 at the 6:00 AM PST reset. Current Season 3 guide localization names three Aethyris subzones: Skyrend Cliff, Unbroken Camp, and Harmonic Crystal. Keep the date unconfirmed until Charming Glance receives its in-game season countdown/telescope. PROJECTED NEXUS CHANGE: multiple Global community reports agree that the cross-server Nexus group grows from 4 servers in S2 to 8 servers in S3/Aethyris. This is an expansion of the Nexus grouping rather than a literal character/server merge; verify the exact Charming Glance grouping at rollover.','region',null,'unconfirmed'],"""
if old_a not in s: raise SystemExit('Aethyris row anchor not found')
s=s.replace(old_a,new_a,1)

old_c="""    ['2026-11-05',114,'Class Advancement','Tier 5 class advancement','Player Lv.136 · Class Lv.180 · Tier 4 class Lv.40 · Aethyris Five. Global-English T5 names are now exposed in current Global-English skill/class data: Conqueror → Ravager, Guardian → Templar, Destroyer → Magister, and Dominator → Prophet. Ravager/Templar are visible in Prydwen\\'s current skill database even though dedicated T5 build guides are not yet published for those two paths; Unreal Guild\\'s current class-path tool independently maps all four progressions the same way.','class-advancement'],"""
new_c="""    // S3_T5_GUIDE_STATUS_SEP9_V1: Prydwen now publishes dedicated Ravager, Magister, and Prophet T5 guides; Templar remains the only T5 path without a dedicated guide on its current guide index.
    ['2026-11-05',114,'Class Advancement','Tier 5 class advancement','Player Lv.136 · Class Lv.180 · Tier 4 class Lv.40 · Aethyris Five. Global-English T5 paths: Conqueror → Ravager, Guardian → Templar, Destroyer → Magister, and Dominator → Prophet. Prydwen now has dedicated T5 build guides for Ravager, Magister, and Prophet; Templar remains present in current class/skill data but does not yet have a dedicated T5 guide on the guide index. Unreal Guild\\'s current class-path tool independently maps all four progressions the same way.','class-advancement'],"""
if old_c not in s: raise SystemExit('Tier 5 row anchor not found')
s=s.replace(old_c,new_c,1)

old_summary="""    if(title==='Aethyris opens') return 'Season 3 · Aethyris · Tier 5 · Nexus grouping expands from 4 servers to an 8-server pool.';"""
new_summary="""    if(title==='Aethyris opens') return 'Season 3 · Aethyris · Tier 5 · Skyrend Cliff, Unbroken Camp and Harmonic Crystal · Nexus grouping expands from 4 servers to an 8-server pool.';"""
if old_summary not in s: raise SystemExit('Aethyris summary anchor not found')
s=s.replace(old_summary,new_summary,1)

path.write_text(s,encoding='utf-8')
print('Applied Sep. 9 Season 3 research refresh.')
