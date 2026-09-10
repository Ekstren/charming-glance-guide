from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
marker='TIMELINE_SUMMARY_PROVENANCE_CLEAN_V2'
if marker in s:
    print('Timeline summary provenance cleanup v2 already applied.')
    raise SystemExit(0)

anchor="""    if(title==='Aethyris opens') return 'Season 3 · Aethyris · Tier 5 · Skyrend Cliff, Unbroken Camp and Harmonic Crystal · Nexus grouping expands from 4 servers to an 8-server pool.';
"""
insert=anchor+"""    // TIMELINE_SUMMARY_PROVENANCE_CLEAN_V2: keep source/confidence wording in raw rows/comments only.
    if(title==='Aethyris area-unlock stockpile') return 'Gateway Key ×5 · Magic Drill ×2 · Water Mine ×2 · cloud key ×2 · hammer ×5';
    if(title==='Astral Odyssey') return 'Aethyris season map';
    if(title==='Abyssal Bastion') return 'Normal 20M · Hard 26M · Nightmare 30M · Purgatory 46M';
    if(title==='Aethyris Relic II') return 'Second Aethyris relic gacha';
    if(title==='Courtyard of Purification') return 'Normal 32.5M · Hard 43M · Nightmare 50.5M · Purgatory 75M';
    if(title==='Temple of Order') return 'Normal 55M · Hard 65M · Nightmare 82M · Purgatory 115M';
    if(title==='Aethyris Relic III') return 'Third Aethyris relic gacha';
    if(title==='Solar Spire') return 'Normal 84.5M · Hard 100M · Nightmare 120M · Purgatory 180M';
    if(title==='Sovereign’s Nest') return 'Normal 125M · Hard 145M · Nightmare 180M · Purgatory 250M · Abyss 350M';
    if(title==='Hapadi opens') return 'Season 4 · Hapadi';
    if(title==='Ingenious Clocktower') return 'Hapadi Day 1 · Normal · Hard 27M';
    if(title==='Tier 6 class advancement') return 'Player Lv.172 · Class Lv.280 · Tier 5 class Lv.50 · Hapadi Nine';
    if(title==='Hapadi area-unlock stockpile') return 'Gateway Key ×5 · Magic Drill ×2 · Water Mine ×2 · season item ×5';
    if(title==='Fantomon Resonance unlock') return 'Player Lv.180';
    if(title==='Pirate Galleon') return 'Hapadi Day 14 · Normal 35M · Hard 48M · Nightmare 57M · Purgatory 84M';
    if(title==='Grotesque Fairground') return 'Hapadi Day 15 season map';
    if(title==='Leviathan Submersible') return 'Hapadi Day 28 · Normal 62M · Hard 72M · Nightmare 87M · Purgatory 130M';
"""
if anchor not in s:
    raise SystemExit('timeline summary anchor not found')
s=s.replace(anchor,insert,1)
p.write_text(s,encoding='utf-8')
print('Applied timeline summary provenance cleanup v2.')
