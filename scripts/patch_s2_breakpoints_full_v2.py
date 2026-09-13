from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')

old = '''<div class="s2TargetPresets" id="s2TargetPresets" hidden aria-label="Season 2 Primostar breakpoints"><span>S2 breakpoints</span><div><button type="button" data-s2-target="680">680 <span>EXP</span></button><button type="button" data-s2-target="800">800 <span>GEM</span></button><button type="button" data-s2-target="920">920 <span>EXP</span></button><button type="button" data-s2-target="990">990 <span>ASC</span></button><button type="button" data-s2-target="1060">1060 <span>GEM</span></button><button type="button" data-s2-target="1200">1200 <span>EXP</span></button><button type="button" data-s2-target="1280">1280 <span>ASC</span></button></div><small>S2 breakpoint shortcuts · any total still works.</small></div>'''
new = '''<div class="s2TargetPresets" id="s2TargetPresets" hidden aria-label="Season 2 Primostar breakpoints"><span>S2 breakpoints</span><div><button type="button" data-s2-target="680">680 <span>EXP</span></button><button type="button" data-s2-target="740">740 <span>ASC</span></button><button type="button" data-s2-target="800">800 <span>GEM</span></button><button type="button" data-s2-target="860">860 <span>2X</span></button><button type="button" data-s2-target="920">920 <span>EXP</span></button><button type="button" data-s2-target="990">990 <span>ASC</span></button><button type="button" data-s2-target="1060">1060 <span>GEM</span></button><button type="button" data-s2-target="1130">1130 <span>2X</span></button><button type="button" data-s2-target="1200">1200 <span>EXP</span></button><button type="button" data-s2-target="1280">1280 <span>ASC</span></button></div><small>S2 breakpoint shortcuts · any total still works.</small></div>'''

if old not in text:
    raise SystemExit('Current S2 breakpoint block not found; refusing unsafe patch')

text = text.replace(old, new, 1)
path.write_text(text, encoding='utf-8')
print('Replaced S2 shortcut row with full EXP/ASC/GEM/2X breakpoint set from 680 through 1280.')
