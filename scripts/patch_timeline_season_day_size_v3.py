from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
old='.dayMarker .seasonDayLabel{display:block;margin-top:3px;font-size:11px;font-weight:750;line-height:1.15;color:var(--muted);letter-spacing:.02em}\n@media(max-width:620px){.dayMarker .seasonDayLabel{font-size:10px}}'
new='.dayMarker .seasonDayLabel{display:block;margin-top:3px;font-size:12px;font-weight:750;line-height:1.15;color:var(--muted);letter-spacing:.02em}\n@media(max-width:620px){.dayMarker .seasonDayLabel{font-size:11px}}'
if old not in s:
    if new in s:
        print('already applied')
        raise SystemExit(0)
    raise SystemExit('season day CSS anchor not found')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')
print('increased season day label size to 12px/11px')
