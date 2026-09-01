from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

old = """      const b=e.target.closest('button[data-class]');\n      if(!b)return;\n      currentClass=b.dataset.class;"""
new = """      const b=e.target.closest('button[data-class]');\n      if(!b)return;\n      if(b.dataset.class===currentClass)return;\n      currentClass=b.dataset.class;"""

if new in s:
    print('Same-class build click guard already present')
    raise SystemExit(0)

count = s.count(old)
if count < 1:
    raise SystemExit('Build class click handler anchor not found')

s = s.replace(old, new)
p.write_text(s, encoding='utf-8')
print(f'Added same-class no-op guard to {count} build class click handler(s)')
