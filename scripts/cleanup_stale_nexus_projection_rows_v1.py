from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

needles = [
    "['2026-09-12',60,'Tournament','First S2 Server Tournament · Nexus qualifier'",
    "['2026-09-13',61,'Tournament','First S2 Nexus Tournament'",
]

removed = []
lines = s.splitlines(keepends=True)
out = []
for line in lines:
    if any(n in line for n in needles):
        removed.append(line)
        continue
    out.append(line)

if not removed:
    print('No stale Nexus projection rows found; already clean.')
else:
    p.write_text(''.join(out), encoding='utf-8')
    print(f'Removed {len(removed)} stale projected tournament row(s).')

new = p.read_text(encoding='utf-8')
for n in needles:
    if n in new:
        raise SystemExit(f'Stale row still present: {n}')
if "['2026-09-12',60,'Event','Nexus Tournament · 4v4'" not in new:
    raise SystemExit('Confirmed Sep 12 Nexus row missing after cleanup')
if "['2026-09-05',53,'Event','Server Tournament'" not in new:
    raise SystemExit('Confirmed Sep 5 Server Tournament row missing after cleanup')
