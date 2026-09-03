from pathlib import Path
import re

FILES = [
    Path('index.html'),
    Path('scripts/patch_build_roll_guide_v2.py'),
]

NEW_NAME = '.rollGuideRow .rollGuideName{min-width:0;color:var(--green)!important;font-size:9px;font-weight:850;line-height:1.35;letter-spacing:0;text-transform:none}'
NEW_VALUE = '.rollGuideRow .rollGuideValue{color:var(--body-text)!important;font-size:9px;font-weight:650;line-height:1.35;text-align:right;white-space:nowrap;letter-spacing:0!important;text-transform:none!important}'
NEW_SCALING = '.rollGuideRow .rollGuideValue.rollScaling{color:var(--body-text)!important;font-size:9px;font-weight:650;letter-spacing:0!important;text-transform:none!important}'

PATTERNS = [
    (re.compile(r'\.rollGuideRow \.rollGuideName\{[^}]+\}'), NEW_NAME),
    (re.compile(r'\.rollGuideRow \.rollGuideValue\{[^}]+\}'), NEW_VALUE),
    (re.compile(r'\.rollGuideRow \.rollGuideValue\.rollScaling\{[^}]+\}'), NEW_SCALING),
]

for path in FILES:
    s = path.read_text(encoding='utf-8')
    for pattern, replacement in PATTERNS:
        s, count = pattern.subn(replacement, s, count=1)
        if count != 1:
            raise SystemExit(f'{path}: expected one Roll guide CSS match for {pattern.pattern}, got {count}')
    path.write_text(s, encoding='utf-8')
    print(f'updated {path}')
