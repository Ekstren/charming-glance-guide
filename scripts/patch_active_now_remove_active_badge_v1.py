from pathlib import Path

# Active-now cards live inside an already-labeled section, so strip any redundant trailing ACTIVE text from their titles.
p = Path('index.html')
s = p.read_text(encoding='utf-8')

old_badge = "const cards=activeEvents.map(e=>`<div class=\"timelineNowCard\"><strong>${e[3]}<span class=\"activePill\">ACTIVE</span></strong><small>${timelineSummaryText(e)}</small></div>`).join('');"
old_plain = "const cards=activeEvents.map(e=>`<div class=\"timelineNowCard\"><strong>${e[3]}</strong><small>${timelineSummaryText(e)}</small></div>`).join('');"
new = "const cards=activeEvents.map(e=>`<div class=\"timelineNowCard\"><strong>${String(e[3]).replace(/\\s*ACTIVE\\s*$/i,'')}</strong><small>${timelineSummaryText(e)}</small></div>`).join('');"

if new in s:
    print('Active now titles already strip trailing ACTIVE')
    raise SystemExit(0)
if old_badge in s:
    s = s.replace(old_badge, new, 1)
elif old_plain in s:
    s = s.replace(old_plain, new, 1)
else:
    raise SystemExit('Active now render anchor not found')

p.write_text(s, encoding='utf-8')
print('Removed redundant trailing ACTIVE text from Active now titles')
