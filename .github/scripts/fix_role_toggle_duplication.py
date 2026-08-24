from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
old="  let tabs=root.querySelector(':scope > .buildRoleTabs');\n  const guide=root.querySelector(':scope > .guideSummary');"
new="  const guide=root.querySelector(':scope > .guideSummary');\n  let tabs=guide?.querySelector('.buildRoleTabs') || root.querySelector('.buildRoleTabs');\n  const extras=[...root.querySelectorAll('.buildRoleTabs')].filter(x=>x!==tabs);\n  extras.forEach(x=>x.remove());"
if old not in s:
    raise SystemExit('applyBuildRole selector marker not found')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')
print('Fixed repeated DPS/Heals toggle creation.')
# trigger
