from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

repls={
"['2026-11-05',114,'Region','Aethyris opens','STRONGLY SUPPORTED / UNCONFIRMED FOR CHARMING GLANCE. A fixed older-server Global timeline places Aethyris and Tier 5 on Server Day 114; Charming Glance Server Day 114 maps to Nov. 5 at the 6:00 AM PST reset. Current Season 3 guide localization names three Aethyris subzones: Skyrend Cliff, Unbroken Camp, and Harmonic Crystal. Keep the date unconfirmed until Charming Glance receives its in-game season countdown/telescope. PROJECTED NEXUS CHANGE: multiple Global community reports agree that the cross-server Nexus group grows from 4 servers in S2 to 8 servers in S3/Aethyris. This is an expansion of the Nexus grouping rather than a literal character/server merge; verify the exact Charming Glance grouping at rollover.','region',null,'unconfirmed'],":"['2026-11-05',114,'Region','Aethyris opens','Skyrend Cliff · Unbroken Camp · Harmonic Crystal · Tier 5 era begins','region',null,'unconfirmed'],",
"['2026-11-05',114,'Dungeon','Crystal Spiral Tree','OFFICIAL GLOBAL NAME confirmed by the Sword x Staff Global announcements feed on Sep. 7: the Aethyris dungeon preview calls Crystal Spiral Tree the very first dungeon reached after entering Aethyris. The Nov. 5 Charming Glance placement remains PROJECTED from the current Server Day 114 / Season 3 rollover model; the official preview confirms the dungeon name and its position as Aethyris’s first dungeon, but does not confirm Charming Glance’s exact unlock date. Current Sep. 9 Season 3 guidance identifies the Sylvan Set here; older-server/data guidance lists Hard at 9M. Recheck the in-game requirement when S3 approaches.','dungeon'],":"['2026-11-05',114,'Dungeon','Crystal Spiral Tree','First Aethyris dungeon · Sylvan Set · Hard 9M','dungeon'],",
"['2026-11-05',114,'Class Advancement','Tier 5 class advancement','Player Lv.136 · Class Lv.180 · Tier 4 class Lv.40 · Aethyris Five. Global-English T5 paths: Conqueror → Ravager, Guardian → Templar, Destroyer → Magister, and Dominator → Prophet. Prydwen now has dedicated T5 build guides for Ravager, Magister, and Prophet; Templar remains present in current class/skill data but does not yet have a dedicated T5 guide on the guide index. Unreal Guild\\'s current class-path tool independently maps all four progressions the same way.','class-advancement'],":"['2026-11-05',114,'Class Advancement','Tier 5 class advancement','Player Lv.136 · Class Lv.180 · Tier 4 class Lv.40 · Conqueror → Ravager · Guardian → Templar · Destroyer → Magister · Dominator → Prophet','class-advancement'],",
"['2026-12-20',159,'Fantomon','Prismora','UNCONFIRMED Charming Glance date. Current Global Fantomon database name · QY roadmap label is Prismatic Astralite. QY places it at S3 Day 46, which maps to Server Day 159 / Dec. 20 from the projected Nov. 5 S3 anchor. The older-server “Rainbow Star Spirit” label appears to describe this same pet/milestone, so that duplicate translated-name row has been retired.','fantomon',null,'unconfirmed'],":"['2026-12-20',159,'Fantomon','Prismora','Aethyris Fantomon · S3 Day 46','fantomon',null,'unconfirmed'],"
}
for old,new in repls.items():
    if old not in s:
        raise SystemExit('Expected timeline anchor missing:\n'+old[:140])
    s=s.replace(old,new,1)

anchor="    ['2026-11-05',114,'Feature','Bond Odyssey + Stone Symphony','Season 3 passive progression · Vista Dispatch milestones · timed companion expeditions · souvenir rewards','feature'],\n"
if anchor not in s:
    raise SystemExit('Bond Odyssey anchor missing')
comp="    // S3_COMPANIONS_SEP9_V1: LDShop's Sep. 9 Season 3 guide names Isla and Astrid as new Aethyris companions.\n    ['2026-11-05',114,'Companions','Isla + Astrid','New Season 3 companions joining in Aethyris','companions'],\n"
if "'Isla + Astrid'" not in s:
    s=s.replace(anchor,anchor+comp,1)

# Keep research provenance in comments, never visible card copy.
marker="    // S3_SUMMARY_ONLY_CLEANUP_SEP9_V1: visible S3 cards were stripped of confidence/source-audit prose; provenance remains in comments and maintained research notes.\n"
season_anchor="    // ---- Season 3 · Aethyris ----\n"
if marker not in s:
    s=s.replace(season_anchor,season_anchor+marker,1)

p.write_text(s,encoding='utf-8')
print('Refreshed S3 summary-only cards and added Isla/Astrid companion row.')
