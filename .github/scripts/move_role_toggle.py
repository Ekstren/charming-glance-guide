from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
old_css=".buildRoleTabs{border:1px solid var(--line);background:var(--surface);border-radius:12px;display:grid;grid-template-columns:1fr 1fr;gap:5px;width:min(320px,100%);padding:4px;margin:0 0 10px auto}"
new_css=".buildRoleTabs{border:1px solid var(--line);background:var(--surface);border-radius:10px;display:grid;grid-template-columns:1fr 1fr;gap:4px;width:min(240px,100%);padding:3px;margin:12px 0 0}"
if old_css in s:
    s=s.replace(old_css,new_css,1)
else:
    raise SystemExit('role tab CSS marker not found')
old="if(!tabs && guide){tabs=document.createElement('div');tabs.className='buildRoleTabs';tabs.innerHTML='<button type=\"button\" data-role=\"dps\">DPS</button><button type=\"button\" data-role=\"heals\">Heals</button>';guide.before(tabs);}"
new="if(!tabs && guide){tabs=document.createElement('div');tabs.className='buildRoleTabs';tabs.innerHTML='<button type=\"button\" data-role=\"dps\">DPS</button><button type=\"button\" data-role=\"heals\">Heals</button>';const identity=guide.children[0];(identity||guide).append(tabs);}"
if old in s:
    s=s.replace(old,new,1)
else:
    raise SystemExit('role tab insertion marker not found')
# Mobile rule no longer needs auto full-width/right-margin behavior.
s=s.replace('@media(max-width:760px){.buildRoleTabs{width:100%;margin-left:0}}','@media(max-width:760px){.buildRoleTabs{width:100%}}',1)
p.write_text(s,encoding='utf-8')
print('Moved DPS/Heals toggle into class summary card.')
