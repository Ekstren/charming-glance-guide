from pathlib import Path

FILES = [
    Path('index.html'),
    Path('scripts/patch_build_roll_guide_v2.py'),
]

REPLACEMENTS = [
    (
        '.rollGuideName{min-width:0;color:var(--body-text);font-size:8px;font-weight:760;line-height:1.2}',
        '.rollGuideRow .rollGuideName{min-width:0;color:var(--green);font-size:8px;font-weight:760;line-height:1.2}',
    ),
    (
        '.rollGuideValue{color:var(--ink);font-size:8.5px;font-weight:850;line-height:1.15;text-align:right;white-space:nowrap}',
        '.rollGuideRow .rollGuideValue{color:var(--body-text);font-size:8.5px;font-weight:850;line-height:1.15;text-align:right;white-space:nowrap}',
    ),
    (
        '.rollGuideValue.rollScaling{color:var(--secondary-text);font-size:7.5px}',
        '.rollGuideRow .rollGuideValue.rollScaling{color:var(--body-text);font-size:7.5px}',
    ),
]

for path in FILES:
    s = path.read_text(encoding='utf-8')
    changed = False
    for old, new in REPLACEMENTS:
        if new in s:
            continue
        if old not in s:
            raise SystemExit(f'{path}: expected Roll guide CSS not found: {old}')
        s = s.replace(old, new, 1)
        changed = True
    if changed:
        path.write_text(s, encoding='utf-8')
        print(f'updated {path}')
    else:
        print(f'{path} already aligned')
