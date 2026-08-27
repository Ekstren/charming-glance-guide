from pathlib import Path

p=Path('index.html')
text=p.read_text(encoding='utf-8')
old='<i>Used:</i>'
new='<i>Use:</i>'
if new in text and old not in text:
    print('Use label already applied.')
    raise SystemExit(0)
if text.count(old)!=1:
    raise SystemExit(f'Expected one Used label, found {text.count(old)}')
text=text.replace(old,new,1)
p.write_text(text,encoding='utf-8')
print('Changed Used to Use.')
