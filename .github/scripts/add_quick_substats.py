from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')

css='''.quickSubstats{border-top:1px solid color-mix(in srgb,var(--line) 72%,transparent);padding-top:7px;display:grid;grid-template-columns:max-content 1fr;gap:8px;align-items:baseline}\n.quickSubstats b{color:var(--gold);font-size:9px;white-space:nowrap}\n.quickSubstats span{color:var(--body-text);font-size:9px;line-height:1.4}\n'''
if '.quickSubstats{' not in s:
    marker='.priorityPair{display:grid'
    pos=s.find(marker)
    if pos<0: raise SystemExit('priorityPair CSS marker not found')
    s=s[:pos]+css+s[pos:]

old="""    const items=[...gear.querySelectorAll('.gearItem')];
    const main=items.find(x=>/^Main lines$/i.test(x.querySelector('span')?.textContent.trim()||''));
    const rows=parseGearRows(main?.querySelector('p')?.textContent.trim()||'');
    const quick=document.createElement('div');
    quick.className='buildQuickStats';
    quick.innerHTML=`<div class=\"quickTitle\">Quick stats</div>${rule?`<p class=\"quickRule\">${rule}</p>`:''}<div class=\"quickGearGrid\">${rows.map(r=>`<div class=\"quickGearRow\"><b>${r[0]}</b><span>${r[1]}</span></div>`).join('')}</div>`;
"""
new="""    const items=[...gear.querySelectorAll('.gearItem')];
    const main=items.find(x=>/^Main lines$/i.test(x.querySelector('span')?.textContent.trim()||''));
    const subs=items.find(x=>/^Best substats$/i.test(x.querySelector('span')?.textContent.trim()||''));
    const rows=parseGearRows(main?.querySelector('p')?.textContent.trim()||'');
    const substats=subs?.querySelector('p')?.textContent.trim()||'';
    const quick=document.createElement('div');
    quick.className='buildQuickStats';
    quick.innerHTML=`<div class=\"quickTitle\">Quick stats</div>${rule?`<p class=\"quickRule\">${rule}</p>`:''}<div class=\"quickGearGrid\">${rows.map(r=>`<div class=\"quickGearRow\"><b>${r[0]}</b><span>${r[1]}</span></div>`).join('')}</div>${substats?`<div class=\"quickSubstats\"><b>Substats</b><span>${substats}</span></div>`:''}`;
"""
if old in s:
    s=s.replace(old,new,1)
elif 'const substats=subs?.querySelector' not in s:
    raise SystemExit('build quick-stats renderer marker not found')

p.write_text(s,encoding='utf-8')
print('Added Best substats to Quick Stats for S1 and S2 builds.')
