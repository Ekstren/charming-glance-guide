from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
marker='S3_DUNGEON_LOCALIZATION_SEP9_V1'
if marker in s:
    print('S3 Sep 9 dungeon localization already applied.')
    raise SystemExit(0)
old_comment="    // S3_AETHYRIS_SEP9_RESEARCH_V1: LDShop's Sep. 9 Season 3 guide independently names the Aethyris subzones Skyrend Cliff, Unbroken Camp, and Harmonic Crystal. Keep these names as current secondary-source localization until Global in-game text or an official announcement supersedes them.\n"
new_comment=old_comment+"    // S3_DUNGEON_LOCALIZATION_SEP9_V1: the same current Sep. 9 guide names Crystal Spiral Tree's Sylvan Set and the second Aethyris dungeon Eternal Garden with the Lifespring Set. This supersedes the older pre-release label Eternal Blossom Courtyard while preserving the existing Day-127 cadence placement.\n"
if old_comment not in s: raise SystemExit('S3 research comment anchor missing')
s=s.replace(old_comment,new_comment,1)
old_c="    ['2026-11-05',114,'Dungeon','Crystal Spiral Tree','OFFICIAL GLOBAL NAME confirmed by the Sword x Staff Global announcements feed on Sep. 7: the Aethyris dungeon preview calls Crystal Spiral Tree the very first dungeon reached after entering Aethyris. The Nov. 5 Charming Glance placement remains PROJECTED from the current Server Day 114 / Season 3 rollover model; the official preview confirms the dungeon name and its position as Aethyris’s first dungeon, but does not confirm Charming Glance’s exact unlock date. Current older-server/data guidance still lists Hard at 9M; recheck the in-game requirement when S3 approaches.','dungeon'],\n"
new_c="    ['2026-11-05',114,'Dungeon','Crystal Spiral Tree','OFFICIAL GLOBAL NAME confirmed by the Sword x Staff Global announcements feed on Sep. 7: the Aethyris dungeon preview calls Crystal Spiral Tree the very first dungeon reached after entering Aethyris. The Nov. 5 Charming Glance placement remains PROJECTED from the current Server Day 114 / Season 3 rollover model; the official preview confirms the dungeon name and its position as Aethyris’s first dungeon, but does not confirm Charming Glance’s exact unlock date. Current Sep. 9 Season 3 guidance identifies the Sylvan Set here; older-server/data guidance lists Hard at 9M. Recheck the in-game requirement when S3 approaches.','dungeon'],\n"
if old_c not in s: raise SystemExit('Crystal Spiral Tree row anchor missing')
s=s.replace(old_c,new_c,1)
old_e="    ['2026-11-18',127,'Dungeon','Eternal Blossom Courtyard','Normal 12.5M + Player Lv.160 · Hard 15M · Nightmare 18M · Purgatory 28.5M · pre-release English/data name','dungeon'],\n"
new_e="    ['2026-11-18',127,'Dungeon','Eternal Garden','Normal 12.5M + Player Lv.160 · Hard 15M · Nightmare 18M · Purgatory 28.5M · Lifespring Set','dungeon'],\n"
if old_e not in s: raise SystemExit('Eternal Blossom Courtyard row anchor missing')
s=s.replace(old_e,new_e,1)
old_sum="    if(title==='Crystal Spiral Tree') return 'Aethyris’s first dungeon · current older-server guidance lists Hard at 9M.';\n"
new_sum="    if(title==='Crystal Spiral Tree') return 'Aethyris’s first dungeon · Sylvan Set · current older-server guidance lists Hard at 9M.';\n"
if old_sum not in s: raise SystemExit('Crystal summary anchor missing')
s=s.replace(old_sum,new_sum,1)
p.write_text(s,encoding='utf-8')
print('Applied S3 Sep 9 dungeon localization and gear-set names.')
