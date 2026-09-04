from pathlib import Path

p=Path('index.html')
text=p.read_text(encoding='utf-8')
replacements={
    "Prydwen says Guardian's long-run value":"Prydwen says the long-run value of Guardian",
    "the class's longer-term identity":"the longer-term Guardian identity",
    "demote Night's Blessing because":"demote the older Dark buff because",
    "Prophet's published T5 healer bar":"The published T5 Prophet healer bar",
    "Radiant Rhythm's bouncing heals":"bouncing heals from Radiant Rhythm",
}
for old,new in replacements.items():
    count=text.count(old)
    if count!=1:
        raise SystemExit(f'expected one emitted JS quote hazard for {old!r}, found {count}')
    text=text.replace(old,new,1)
p.write_text(text,encoding='utf-8')
print('fixed emitted apostrophes in T5 investment JS strings')
