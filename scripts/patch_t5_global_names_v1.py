from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

old = "Global-English T5 names now published by Prydwen (guides updated Sep. 1, 2026) confirm Destroyer → Magister and Dominator → Prophet. The Duelist- and Knight-line T5 Global-English names are not yet published there, so this row remains generic for those two lines."
new = "Global-English T5 names are now exposed in current Global-English skill/class data: Conqueror → Ravager, Guardian → Templar, Destroyer → Magister, and Dominator → Prophet. Ravager/Templar are visible in Prydwen\\'s current skill database even though dedicated T5 build guides are not yet published for those two paths; Unreal Guild\\'s current class-path tool independently maps all four progressions the same way."

if new in s:
    print('T5 Global names already applied')
    raise SystemExit(0)
if old not in s:
    raise SystemExit('Tier 5 timeline detail anchor not found')

s = s.replace(old, new, 1)
p.write_text(s, encoding='utf-8')
print('Updated Tier 5 timeline row with all four Global-English class names')
