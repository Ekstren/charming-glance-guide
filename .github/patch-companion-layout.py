from pathlib import Path
import re

p = Path('index.html')
text = p.read_text(encoding='utf-8')

# Keep Companions visually consistent with Builds at both normal and wide
# desktop breakpoints, and keep class tabs as the first content beneath nav.
old_width = '.companions{max-width:1080px;margin:32px auto 80px;padding:0 20px}'
base_width = '.companions{max-width:980px;margin:32px auto 80px;padding:0 20px}'
if old_width in text:
    text = text.replace(old_width, base_width, 1)
elif base_width not in text:
    raise SystemExit('Companion base width rule not found')

wide_block = '''<!-- COMPANION_BUILD_WIDTH_START -->
<style id="companion-build-width-v1">
@media (min-width:1400px){
  .companions{max-width:1560px;margin-top:38px;padding:0 28px}
}
</style>
<!-- COMPANION_BUILD_WIDTH_END -->'''

if '<!-- COMPANION_BUILD_WIDTH_START -->' in text:
    text, n = re.subn(
        r'<!-- COMPANION_BUILD_WIDTH_START -->.*?<!-- COMPANION_BUILD_WIDTH_END -->',
        wide_block,
        text,
        count=1,
        flags=re.S,
    )
    if n != 1:
        raise SystemExit('Could not refresh Companion wide-width block')
else:
    anchor = '<!-- COMPANION_GUIDE_CSS_END -->'
    if anchor not in text:
        raise SystemExit('Companion CSS end marker not found')
    text = text.replace(anchor, wide_block + '\n' + anchor, 1)

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
print('Aligned Companion section with Builds at normal and wide desktop widths')
