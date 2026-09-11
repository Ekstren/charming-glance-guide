from pathlib import Path

path = Path(__file__).resolve().parents[1] / 'assets' / 'runtime.js'
text = path.read_text(encoding='utf-8')
old = "viewer's local timezone"
new = "viewer device local timezone"
count = text.count(old)
if count < 1:
    raise SystemExit('viewer apostrophe pattern not found')
text = text.replace(old, new)
path.write_text(text, encoding='utf-8')
print(f'replaced {count} occurrence(s)')
