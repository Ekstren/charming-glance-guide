from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
marker='S3_BOND_ODYSSEY_STONE_SYMPHONY_SEP9_V1'
if marker in s:
    print('S3 Bond Odyssey/Stone Symphony update already applied.')
    raise SystemExit(0)
anchor="""    ['2026-11-05',114,'Class Advancement','Tier 5 class advancement','Player Lv.136 · Class Lv.180 · Tier 4 class Lv.40 · Aethyris Five. Global-English T5 paths: Conqueror → Ravager, Guardian → Templar, Destroyer → Magister, and Dominator → Prophet. Prydwen now has dedicated T5 build guides for Ravager, Magister, and Prophet; Templar remains present in current class/skill data but does not yet have a dedicated T5 guide on the guide index. Unreal Guild\\'s current class-path tool independently maps all four progressions the same way.','class-advancement'],
"""
insert=anchor+"""    // S3_BOND_ODYSSEY_STONE_SYMPHONY_SEP9_V1: LDShop's Sep. 9 Season 3 guide identifies Bond Odyssey/Vista Dispatch and Stone Symphony as Aethyris systems, with timed companion expeditions and souvenir rewards. The visible row stays summary-only; the Nov. 5 placement follows the maintained S3 Day-114 rollover model.
    ['2026-11-05',114,'Feature','Bond Odyssey + Stone Symphony','Season 3 passive progression · Vista Dispatch milestones · timed companion expeditions · souvenir rewards','feature'],
"""
if anchor not in s:
    raise SystemExit('Tier 5 anchor not found')
s=s.replace(anchor,insert,1)
p.write_text(s,encoding='utf-8')
print('Added S3 Bond Odyssey + Stone Symphony timeline feature.')
