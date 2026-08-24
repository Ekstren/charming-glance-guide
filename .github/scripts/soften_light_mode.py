from pathlib import Path
import re

p=Path('index.html')
s=p.read_text(encoding='utf-8')

m=re.search(r':root\{(--lightningcss-light:initial;--lightningcss-dark: ;color-scheme:light;.*?--footer:#fff)\}:root\[data-theme=dark\]', s, re.S)
if not m:
    raise SystemExit('light theme root block not found')
block=m.group(1)
repls={
    '--bg:#f5f3ef':'--bg:#e9e6e0',
    '--surface:#fff':'--surface:#f4f1ec',
    '--surface-glass:#ffffffbd':'--surface-glass:#f4f1ece0',
    '--topbar:#ffffffe8':'--topbar:#efebe5ee',
    '--body-text:#4f5457':'--body-text:#464b4e',
    '--secondary-text:#7a7f82':'--secondary-text:#686e71',
    '--muted:#777b80':'--muted:#6b7074',
    '--line:#e5e2dc':'--line:#d2cdc5',
    '--green-soft:#dff1ea':'--green-soft:#d5e8e1',
    '--filter-bg:#ffffffb8':'--filter-bg:#f1eee8d6',
    '--today-bg:#edf8f4':'--today-bg:#e1eee9',
    '--today-border:#aad3c4':'--today-border:#94c1b1',
    '--footer:#fff':'--footer:#efebe5',
}
for old,new in repls.items():
    if old not in block:
        raise SystemExit(f'missing light theme token: {old}')
    block=block.replace(old,new,1)

s=s[:m.start(1)] + block + s[m.end(1):]
p.write_text(s,encoding='utf-8')
print('Softened light mode brightness without changing dark mode.')
