from pathlib import Path

old = 'Used in the dedicated solo-control setup where surviving and maintaining spacing matter.'
new = 'Used in the dedicated solo-control setup where surviving and maintaining spacing matter.'
paths = [Path('index.html'), Path('.github/build-fantomons-inject.html')] + sorted(Path('scripts').glob('*.py')) + sorted(Path('.github').glob('*.py'))
count = 0
for path in paths:
    if not path.exists():
        continue
    text = path.read_text(encoding='utf-8')
    if old in text:
        count += text.count(old)
        path.write_text(text.replace(old, new), encoding='utf-8')

live = Path('.github/build-fantomons-inject.html').read_text(encoding='utf-8')
if 'shell' in live.lower():
    raise RuntimeError('player-facing build injection still contains shell wording')
if 'synthesis' in live.lower():
    raise RuntimeError('player-facing build injection still contains synthesis wording')
if count == 0:
    raise RuntimeError('final public-copy cleanup found nothing to replace')
print('final build-copy cleanup replacements:', count)
