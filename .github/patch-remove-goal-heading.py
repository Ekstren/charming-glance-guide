from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')
old = '        <h3>Goal and current character</h3>\n'
if old not in text:
    raise SystemExit('Goal/current character heading not found')
text = text.replace(old, '', 1)
path.write_text(text, encoding='utf-8')
print('Removed Goal and current character heading')
