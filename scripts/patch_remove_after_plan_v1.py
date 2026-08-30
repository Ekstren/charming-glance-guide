from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')
marker = 'REMOVE_REALM_AFTER_PLAN_V1'
if marker in s:
    print('Realm After plan rows already removed')
    raise SystemExit(0)

# Remove the three user-facing "After plan" rows from the Material Realm inventory cards.
patterns = [
    r'<small class="realmAfterPlan" id="hammerAfterPlan">After plan: —</small>',
    r'<small class="realmAfterPlan" id="knucklesAfterPlan">After plan: —</small>',
    r'<small class="realmAfterPlan" id="shovelAfterPlan">After plan: —</small>',
]
for pat in patterns:
    s, count = re.subn(pat, '', s, count=1)
    if count != 1:
        raise SystemExit(f'expected Realm After plan element not found: {pat}')

# The render logic already safely checks whether these elements exist, so no behavior change is needed.
idx = s.rfind('</style>')
if idx < 0:
    raise SystemExit('style close not found')
s = s[:idx] + f'\n/* {marker} */\n' + s[idx:]

p.write_text(s, encoding='utf-8')
print('Removed Material Realm After plan rows')
