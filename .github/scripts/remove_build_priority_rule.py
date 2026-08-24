from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
old='  <div class="buildPriorityRule">Upgrade priorities rank <b>equipped build slots only</b>. Situational swap-only skills stay in each build card instead of being ranked as core investments.</div>\n'
if old not in s:
    raise SystemExit('buildPriorityRule note not found')
s=s.replace(old,'',1)
p.write_text(s,encoding='utf-8')
print('Removed build priority rule note.')
# trigger
