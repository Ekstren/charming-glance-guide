from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')

build='  <div class="sectionHeading"><div><span id="buildSeasonLabel">Season build guide</span><h2>Builds</h2></div><p id="buildSeasonNote">Builds automatically follow the active Charming Glance season.</p></div>\n'
calc_open='<section id="calculatorSection" class="siteSection calculator" hidden aria-labelledby="calculator-title">\n'
calc_open_new='<section id="calculatorSection" class="siteSection calculator" hidden aria-label="Primostar Calculator">\n'
calc='  <div class="sectionHeading"><div><span id="calcSeasonEyebrow">Season 1 planning tool</span><h2 id="calculator-title">Primostar Calculator</h2></div><p id="calcSeasonHeadingNote">Enter where you are now. The calculator gives you the minimum balanced end-of-season levels needed for your goal.</p></div>\n'

for label,old in [('build heading',build),('calculator heading',calc),('calculator section opening',calc_open)]:
    if old not in s:
        raise SystemExit(f'{label} marker not found')
s=s.replace(build,'',1)
s=s.replace(calc_open,calc_open_new,1)
s=s.replace(calc,'',1)

old_js="""    $('calcSeasonEyebrow').textContent=`${cfg.name} planning tool`;
    $('calcSeasonHeadingNote').textContent=cfg.key==='s1'
      ? 'Enter where you are now. Season 2 scoring/resource rules are already preloaded and will switch on automatically at reset.'
      : 'Season 2 uses its own score weights and Lv.120 max resource yields; Nov 5 is a projected end anchor until telescope/merge timing confirms it.';
"""
if old_js not in s:
    raise SystemExit('calculator heading JS marker not found')
s=s.replace(old_js,'',1)

p.write_text(s,encoding='utf-8')
print('Removed redundant Builds and Primostar Calculator section headings.')
