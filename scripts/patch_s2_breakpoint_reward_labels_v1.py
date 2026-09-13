from pathlib import Path

index = Path('index.html')
css = Path('assets/site.css')

html = index.read_text(encoding='utf-8')
old = '''<div><button type="button" data-s2-target="680">680</button><button type="button" data-s2-target="800">800</button><button type="button" data-s2-target="920">920</button><button type="button" data-s2-target="990">990</button><button type="button" data-s2-target="1060">1060</button><button type="button" data-s2-target="1200">1200</button><button type="button" data-s2-target="1280">1280</button></div>'''
new = '''<div><button type="button" data-s2-target="680">680 <span>EXP</span></button><button type="button" data-s2-target="800">800 <span>GEM</span></button><button type="button" data-s2-target="920">920 <span>EXP</span></button><button type="button" data-s2-target="990">990 <span>ASC</span></button><button type="button" data-s2-target="1060">1060 <span>GEM</span></button><button type="button" data-s2-target="1200">1200 <span>EXP</span></button><button type="button" data-s2-target="1280">1280 <span>ASC</span></button></div>'''
if old not in html:
    raise SystemExit('S2 breakpoint button block not found')
html = html.replace(old, new, 1)
index.write_text(html, encoding='utf-8')

styles = css.read_text(encoding='utf-8')
marker = '/* S2_BREAKPOINT_REWARD_LABELS_V1 */'
if marker not in styles:
    styles += '''\n\n/* S2_BREAKPOINT_REWARD_LABELS_V1 */\n.s2TargetPresets button{display:inline-flex;align-items:center;justify-content:center;gap:5px;white-space:nowrap}\n.s2TargetPresets button span{color:var(--muted);font-size:7px;font-weight:900;letter-spacing:.06em;line-height:1}\n.s2TargetPresets button.active span{color:inherit;opacity:.82}\n@media (max-width:760px){.s2TargetPresets button{gap:3px}.s2TargetPresets button span{font-size:6.5px}}\n'''
    css.write_text(styles, encoding='utf-8')

print('Added inline reward labels to S2 breakpoint shortcuts.')
