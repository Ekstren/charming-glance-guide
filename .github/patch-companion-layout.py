from pathlib import Path
import re

p = Path('index.html')
text = p.read_text(encoding='utf-8')

# Keep Companions visually consistent with Builds: class tabs are the first
# content immediately beneath the main section navigation.
text, n = re.subn(
    r'\n\s*<div class="companionTop">.*?</div>\s*(?=<div class="classTabs companionClassTabs")',
    '\n  ',
    text,
    count=1,
    flags=re.S,
)
if n != 1:
    raise SystemExit('Companion title/header block not found')

p.write_text(text, encoding='utf-8')
print('Removed Companion title/header block')
