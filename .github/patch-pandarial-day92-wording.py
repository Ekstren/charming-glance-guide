from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
old="Global Fantomon name · older translated calendars may call it Bamboo Immortal. UNCONFIRMED CONFLICT: Aug. 27 BlueStacks and recent LDShop/WishGM general-Global guides say Pandarial joined the Summon Crystal exchange on Aug. 18, but a server-age community roadmap places Pandarial at Server Day 92. For Charming Glance, Day 92 maps to Oct. 14; do not treat Pandarial as usable before the in-game exchange confirms it on this server."
new="Global Fantomon name · older translated calendars may call it Bamboo Immortal. UNCONFIRMED FOR CHARMING GLANCE: recent community reports that say either ‘S2 Day 46’ or ‘Server Day 92’ are describing the same server-age unlock, because Season 2 begins on Server Day 47. For Charming Glance that maps to Oct. 14. General-Global guides also report Pandarial appearing in the wider Summon Crystal exchange from Aug. 18, so do not treat it as usable here until Charming Glance’s in-game exchange confirms it."
if old not in s:
    raise SystemExit('Pandarial timeline text not found')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')
