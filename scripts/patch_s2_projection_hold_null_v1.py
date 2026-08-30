from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')
marker = 'S2_PROJECTION_HOLD_NULL_V1'

old = "const reserve=$('holdExp').checked?clamp(n('reserveHours',34),0,36):0;"
new = "const reserve=$('holdExp')?.checked?clamp(n('reserveHours',34),0,36):0; /* S2_PROJECTION_HOLD_NULL_V1 */"

if old in s:
    s = s.replace(old, new, 1)
elif marker in s:
    print('S2 projection Bed-hold null-safety already applied')
    raise SystemExit(0)
else:
    raise SystemExit('Expected unsafe holdExp projection reference not found')

p.write_text(s, encoding='utf-8')
print('Applied S2 projection Bed-hold null-safety')
