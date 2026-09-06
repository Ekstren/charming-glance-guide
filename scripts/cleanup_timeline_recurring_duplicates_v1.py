from pathlib import Path
import re

path = Path('index.html')
text = path.read_text(encoding='utf-8')
lines = text.splitlines(keepends=True)

# The recurring-event generator is the single source of truth for Grand Treasure Hunt
# plus the Bingo -> Lucky Scratch -> Feneck weekly rotation. Older manual additions
# combined those events into one title and, in a couple cases, were inserted repeatedly.
combined_re = re.compile(
    r"^\s*\['\d{4}-\d{2}-\d{2}',\d+,'Event','Treasure Hunt \d+ \+ "
    r"(?:Bingo Draw|Lucky Scratch|Feneck\\?'s Puzzle) \d+'"
)

cleaned = []
removed_combined = []
for line in lines:
    if combined_re.search(line):
        removed_combined.append(line.strip())
        continue
    cleaned.append(line)

# Remove exact duplicate literal timeline rows while preserving the first occurrence.
# Scope this to array rows only so unrelated repeated HTML/JS remains untouched.
seen_rows = set()
deduped = []
removed_exact = []
row_re = re.compile(r"^\s*\['\d{4}-\d{2}-\d{2}',\d+,")
for line in cleaned:
    stripped = line.strip()
    if row_re.match(line) and stripped in seen_rows:
        removed_exact.append(stripped)
        continue
    if row_re.match(line):
        seen_rows.add(stripped)
    deduped.append(line)

out = ''.join(deduped)

# Guardrails: generated recurring schedule must remain present and no manual combined
# recurring titles may survive.
if 'function addRecurringEvents()' not in out:
    raise SystemExit('Recurring-event generator missing; refusing cleanup')
if re.search(r"'Treasure Hunt \d+ \+ (?:Bingo Draw|Lucky Scratch|Feneck\\?'s Puzzle) \d+'", out):
    raise SystemExit('A combined recurring-event row survived cleanup')

path.write_text(out, encoding='utf-8')
print(f'Removed {len(removed_combined)} combined recurring rows')
print(f'Removed {len(removed_exact)} exact duplicate timeline rows')
for row in removed_combined:
    print('  combined:', row[:180])
for row in removed_exact:
    print('  duplicate:', row[:180])
