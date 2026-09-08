#!/usr/bin/env python3
from pathlib import Path
import re
import sys

path = Path(sys.argv[1] if len(sys.argv) > 1 else 'index.html')
text = path.read_text(encoding='utf-8')
normalized = text.replace("\\'", "'")

errors = []

# The recurring generator already emits Grand Treasure Hunt plus the separate
# Bingo Draw / Lucky Scratch / Feneck's Puzzle entry. A manual combined row
# creates the exact duplicate presentation we want to prevent.
combined_re = re.compile(
    r"Treasure Hunt\s+\d+\s*\+\s*(?:Bingo Draw|Lucky Scratch|Feneck's Puzzle)\s+\d+",
    re.IGNORECASE,
)
combined = sorted(set(combined_re.findall(normalized)))
if combined:
    errors.append('combined recurring rows found: ' + ', '.join(combined))

# Catch exact duplicate literal timeline rows as a second line of defense.
rows = [
    line.strip()
    for line in text.splitlines()
    if re.match(r"^\s*\['\d{4}-\d{2}-\d{2}',\s*\d+,", line)
]
seen = set()
dupes = []
for row in rows:
    if row in seen and row not in dupes:
        dupes.append(row)
    seen.add(row)
if dupes:
    errors.append('exact duplicate literal timeline rows found: ' + ' | '.join(dupes[:5]))

if 'function addRecurringEvents()' not in text:
    errors.append('recurring-event generator is missing')

if errors:
    print('TIMELINE DUPLICATE CHECK FAILED')
    for error in errors:
        print(' -', error)
    raise SystemExit(1)

print(f'Timeline duplicate check passed: {len(rows)} literal rows; no combined recurring duplicates.')
