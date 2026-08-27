from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
marker='MAX_HELPER_TEXT_V2'
if marker in s:
    print('already applied')
    raise SystemExit(0)

old='<div class="findMaxCell"><span>Maximum target</span><button id="findMaxStars" type="button">Find max achievable</button><small id="maxAchievableStatus">Checks your selected daily Realm plan and the hard Realm-cap ceiling.</small></div>'
new='<div class="findMaxCell"><span>Maximum target</span><button id="findMaxStars" type="button">Find max achievable</button><small id="maxAchievableStatus"></small></div>'
assert old in s, 'find max helper text anchor missing'
s=s.replace(old,new,1)

s=s.replace('</head>','<style id="max-helper-text-v2">/* MAX_HELPER_TEXT_V2 */ .findMaxCell #maxAchievableStatus:empty{display:none}</style>\n</head>',1)

p.write_text(s,encoding='utf-8')
print('patched')
