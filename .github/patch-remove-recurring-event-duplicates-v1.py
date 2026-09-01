from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')

# The recurring-event generator already creates Grand Treasure Hunt + Bingo/Lucky Scratch/Feneck
# cards. Recent timeline research also added combined static rows for the same dates, which caused
# duplicate cards. Remove only those combined static rows; keep the richer generated cards.
lines = s.splitlines()
pat = re.compile(r"^\s*\['\d{4}-\d{2}-\d{2}',\d+,'Event','Grand Treasure Hunt \(\d+\) · ")
kept = []
removed = []
for line in lines:
    if pat.search(line):
        removed.append(line)
    else:
        kept.append(line)

if not removed:
    raise SystemExit('No combined recurring-event duplicate rows found; refusing no-op patch')

s = '\n'.join(kept) + ('\n' if s.endswith('\n') else '')

old_th = "timelineData.push([start,serverDay,'Treasure Hunt',`Grand Treasure Hunt · Phase ${phase}`,`Lv.5: ${reward} · ${strategy}`,'event',end]);"
new_th = "timelineData.push([start,serverDay,'Treasure Hunt',`Grand Treasure Hunt · Phase ${phase}`,`UNCONFIRMED recurring server-age projection · Lv.5: ${reward} · ${strategy}`,'event',end,'unconfirmed']);"
if old_th not in s:
    raise SystemExit('Treasure Hunt generator marker not found')
s = s.replace(old_th, new_th, 1)

old_mini = "timelineData.push([start,serverDay,def.name,`${def.name} · ${count}`,`${def.prep} · ${note}`,'event',end]);"
new_mini = "timelineData.push([start,serverDay,def.name,`${def.name} · ${count}`,`UNCONFIRMED recurring server-age projection · ${def.prep} · ${note}`,'event',end,'unconfirmed']);"
if old_mini not in s:
    raise SystemExit('Mini-event generator marker not found')
s = s.replace(old_mini, new_mini, 1)

# Safety checks: no combined duplicate rows remain, generated event cards remain, and uncertainty
# is carried by the actual generated cards instead of a separate duplicate summary card.
if any(pat.search(line) for line in s.splitlines()):
    raise SystemExit('Combined recurring-event duplicate rows still remain')
if "Grand Treasure Hunt · Phase ${phase}" not in s or "`${def.name} · ${count}`" not in s:
    raise SystemExit('Recurring-event generators were damaged')
if s.count("'event',end,'unconfirmed'") < 2:
    raise SystemExit('Recurring-event uncertainty tags were not added')

p.write_text(s, encoding='utf-8')
print(f'Removed {len(removed)} duplicate combined recurring-event rows and tagged generated recurring cards UNCONFIRMED.')
