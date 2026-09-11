from pathlib import Path

runtime_path = Path('assets/runtime.js')
runtime = runtime_path.read_text(encoding='utf-8')
old_runtime = '    targetStars:800,'
new_runtime = '    targetStars:680,'
if runtime.count(old_runtime) != 1:
    raise SystemExit(f'Expected exactly one S2 target default, found {runtime.count(old_runtime)}')
runtime = runtime.replace(old_runtime, new_runtime, 1)
runtime_path.write_text(runtime, encoding='utf-8')

index_path = Path('index.html')
index = index_path.read_text(encoding='utf-8')
old_index = '<label>Target Primostars<input id="targetStars" type="number" value="200"></label>'
new_index = '<label>Target Primostars<input id="targetStars" type="number" value="680"></label>'
if index.count(old_index) != 1:
    raise SystemExit(f'Expected exactly one HTML target default, found {index.count(old_index)}')
index = index.replace(old_index, new_index, 1)
index_path.write_text(index, encoding='utf-8')

print('Default Primostar target set to 680.')
