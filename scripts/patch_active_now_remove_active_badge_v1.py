from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

old = "const cards=activeEvents.map(e=>`<div class=\"timelineNowCard\"><strong>${e[3]}<span class=\"activePill\">ACTIVE</span></strong><small>${timelineSummaryText(e)}</small></div>`).join('');"
new = "const cards=activeEvents.map(e=>`<div class=\"timelineNowCard\"><strong>${e[3]}</strong><small>${timelineSummaryText(e)}</small></div>`).join('');"

if old in s:
    s = s.replace(old, new, 1)
elif new in s:
    print('Active now badge already removed')
    raise SystemExit(0)
else:
    raise SystemExit('Active now render anchor not found')

p.write_text(s, encoding='utf-8')
print('Removed redundant ACTIVE badge from Active now cards')
