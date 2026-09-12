from pathlib import Path

path = Path('assets/runtime.js')
text = path.read_text(encoding='utf-8')
old = 'Recommended refreshes/day: Ore ${dailySuggested.ore} · Essence ${dailySuggested.essence} · Sand ${dailySuggested.sand}.'
new = 'Recommended purchases/day: Ore ${dailySuggested.ore} · Essence ${dailySuggested.essence} · Sand ${dailySuggested.sand}.'
if old not in text:
    raise SystemExit('Expected recommendation wording not found')
text = text.replace(old, new, 1)
path.write_text(text, encoding='utf-8')
print('Updated Material Realm recommendation wording.')
