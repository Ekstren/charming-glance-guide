from pathlib import Path
import re

p = Path('index.html')
s = p.read_text()
marker = '<!-- BUILD_FANTOMON_PAIRS_START -->'
head, sep, tail = s.partition(marker)
if not sep:
    raise SystemExit('build fantomon injection marker not found')

# Keep the raw/fallback build renderer aligned with .github/build-maintenance.md.
# The injected ROLE_PRESETS already use this structure; this prevents stale extra
# cards from resurfacing if the injector is unavailable or changed later.
head = head.replace('<h3>Generic / Dungeons</h3><p>Default all-content Elemental setup</p>',
                    '<h3>All-Content</h3><p>Default S2 build for almost everything</p>', 1)
head = head.replace('<h3>Boss / Dragon</h3><p>Single-target and long-fight damage</p>',
                    '<h3>Dragon</h3><p>Dedicated sustained boss damage</p>', 1)
head = head.replace('<h3>Water / AoE</h3><p>Cold stacking with real damage</p>',
                    '<h3>Water Offensive</h3><p>Cold-stacking offensive Guardian</p>', 1)
head = head.replace('<h3>Dragon / Chaos Support</h3><p>Buff, cleanse and debuff support</p>',
                    '<h3>Support / Boss</h3><p>Boss, Chaos and group support</p>', 1)

def drop_card(text, title):
    pat = re.compile(r'\n\s*<article class=\\?"buildCard\\?">(?:(?!<article class=\\?"buildCard\\?">).)*?<h3>' + re.escape(title) + r'</h3>.*?</article>', re.S)
    text2, n = pat.subn('', text, count=1)
    if n != 1:
        raise SystemExit(f'expected one fallback card for {title!r}, found {n}')
    return text2

for title in ('PvP / Mobility', 'Reflect / Solo PvE', 'Carry Support'):
    head = drop_card(head, title)

new = head + sep + tail
if new == s:
    raise SystemExit('no changes made')
p.write_text(new)

# Sanity checks for the intended fallback structure.
for wanted in ('<h3>All-Content</h3>', '<h3>Dragon</h3>', '<h3>Dungeon Tank</h3>', '<h3>Water Offensive</h3>', '<h3>Support / Boss</h3>'):
    if wanted not in head:
        raise SystemExit(f'missing expected fallback card: {wanted}')
for removed in ('<h3>PvP / Mobility</h3>', '<h3>Reflect / Solo PvE</h3>', '<h3>Carry Support</h3>'):
    if removed in head:
        raise SystemExit(f'stale fallback card remains: {removed}')
