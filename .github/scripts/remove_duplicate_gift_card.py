from pathlib import Path
import re

p=Path('index.html')
s=p.read_text(encoding='utf-8')
pat=r"\n  function injectCodeAlert\(\)\{.*?\n  \}\n  function run\(\)\{"
new="\n  function run(){"
s2,n=re.subn(pat,new,s,count=1,flags=re.S)
if n!=1:
    raise SystemExit(f'Expected one injectCodeAlert block, replaced {n}')
s=s2.replace('    injectCodeAlert();\n','',1)
if 'data-code-alert="4P7Y2R9M"' in s or 'function injectCodeAlert' in s:
    raise SystemExit('Gift code injection remnants still present')
p.write_text(s,encoding='utf-8')
print('Removed duplicate active gift-code injection; timeline event remains the single source.')
