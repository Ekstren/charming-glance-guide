from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

server_row = "    ['2026-09-12',60,'Tournament','First S2 Server Tournament · Nexus qualifier','PROJECTED / EXPECTED from multiple older-server Global community reports. Players consistently describe the first Season 2 Nexus Tournament as the second weekend after S2 begins, with the top 4 teams from the preceding server Tournament qualifying. For Charming Glance, S2 began Aug. 30, so the lead projection places the qualifying Server Tournament on Saturday Sep. 12. Event existence and qualification structure are strongly community-supported; the exact Charming Glance date remains unconfirmed until the in-game Tournament schedule appears.','event'],\n"
nexus_row = "    ['2026-09-13',61,'Tournament','First S2 Nexus Tournament','PROJECTED / EXPECTED from multiple older-server Global community reports. The first Nexus Tournament is reported on the Sunday after the first S2 Server Tournament / during the second weekend of Season 2, with the top 4 teams from each participating server qualifying. For Charming Glance, that maps to Sunday Sep. 13. Community reports also describe Nexus Tournament Honor Medal rewards for participating/placing teams. Treat the exact date and reward amounts as projected until Charming Glance shows the in-game registration/bracket schedule.','event'],\n"

# Idempotent: do nothing if the intended rows are already present.
if "'First S2 Server Tournament · Nexus qualifier'" not in s:
    anchor = "    ['2026-09-12',60,'Dungeon','Warlord’s Rest'"
    if anchor not in s:
        raise SystemExit('Warlord’s Rest anchor not found')
    s = s.replace(anchor, server_row + anchor, 1)

if "'First S2 Nexus Tournament'" not in s:
    anchor = "    ['2026-09-13',61,'Seasonal Map','Acme Nexus'"
    if anchor not in s:
        raise SystemExit('Acme Nexus anchor not found')
    s = s.replace(anchor, nexus_row + anchor, 1)

p.write_text(s, encoding='utf-8')
