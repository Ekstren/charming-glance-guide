from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
old=' · Berserker → Conqueror'
if old not in s:
    raise SystemExit('Expected class-specific suffix not found')
s=s.replace(old,'',1)
p.write_text(s,encoding='utf-8')
