from pathlib import Path
import re

p = Path('index.html')
text = p.read_text(encoding='utf-8')

# Keep Companions visually consistent with Builds: same 980px section width
# and class tabs as the first content beneath the main section navigation.
old_width = '.companions{max-width:1080px;margin:32px auto 80px;padding:0 20px}'
new_width = '.companions{max-width:980px;margin:32px auto 80px;padding:0 20px}'
if old_width in text:
    text = text.replace(old_width, new_width, 1)
elif new_width not in text:
    raise SystemExit('Companion width rule not found')

text, n = re.subn(
    r'\n\s*<div class="companionTop">.*?</div>\s*(?=<div class="classTabs companionClassTabs")',
    '\n  ',
    text,
    count=1,
    flags=re.S,
)
if n == 0 and '<div class="classTabs companionClassTabs" id="companionClassTabs"></div>' not in text:
    raise SystemExit('Companion class tabs not found')

p.write_text(text, encoding='utf-8')
print('Aligned Companion section width and header layout with Builds')
