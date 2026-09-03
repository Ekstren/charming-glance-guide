from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')
marker = '<!-- BUILD_HERO_LAYOUT_ICONS_V1_ASSETS -->'
assets = '''<!-- BUILD_HERO_LAYOUT_ICONS_V1_ASSETS -->
<link rel="stylesheet" href="assets/build-layout-icons-v1.css">
<script src="assets/build-layout-icons-v1.js" defer></script>'''

if marker not in text:
    if '</body>' not in text:
        raise SystemExit('index.html has no </body> insertion point')
    text = text.replace('</body>', assets + '\n</body>', 1)
    path.write_text(text, encoding='utf-8')
    print('Added build layout/icon assets to index.html')
else:
    print('Build layout/icon assets are already linked')
