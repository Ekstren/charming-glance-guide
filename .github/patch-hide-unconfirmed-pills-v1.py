from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

old_entry = "${e[7]==='unconfirmed'?'<span class=\"unconfirmedPill\">UNCONFIRMED</span>':''}"
old_now = "${e[7]==='unconfirmed'?'<span class=\"unconfirmedPill\">UNCONFIRMED</span>':''}"

count = s.count(old_entry)
if count != 2:
    raise SystemExit(f'expected 2 visible unconfirmed pill renderers, found {count}')

s = s.replace(old_entry, '')

p.write_text(s, encoding='utf-8')
print('Removed visible UNCONFIRMED pills from timeline cards and Active now cards; status metadata/details remain intact.')
