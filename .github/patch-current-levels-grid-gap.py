from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')
old = '.currentProgressGrid{grid-template-columns:repeat(3,minmax(0,1fr))}'
new = '.currentProgressGrid{grid-template-columns:repeat(3,minmax(0,1fr));margin-bottom:11px}'

if new in s:
    print('Current-level spacing already applied')
elif old in s:
    s = s.replace(old, new, 1)
    p.write_text(s, encoding='utf-8')
    print('Matched current progression row spacing to calcGrid gap')
else:
    raise SystemExit('Expected currentProgressGrid rule not found')
