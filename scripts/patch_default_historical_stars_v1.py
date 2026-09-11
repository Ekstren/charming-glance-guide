from pathlib import Path

index_path = Path('index.html')
index = index_path.read_text(encoding='utf-8')
old = '<input id="historicalStars" type="number" value="0">'
new = '<input id="historicalStars" type="number" value="128">'
if old in index:
    index = index.replace(old, new, 1)
elif new not in index:
    raise SystemExit('Could not find historicalStars input default')
index_path.write_text(index, encoding='utf-8')

runtime_path = Path('assets/runtime.js')
runtime = runtime_path.read_text(encoding='utf-8')
if 'historicalStars:128,' not in runtime:
    raise SystemExit('S2 runtime default is not 128')

print('Historical Primostars default is 128 in both fresh HTML and S2 runtime defaults.')
