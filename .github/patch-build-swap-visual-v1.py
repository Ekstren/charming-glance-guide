from pathlib import Path

paths = [Path('index.html'), Path('.github/build-fantomons-inject.html')]

old_css = '''.buildCard .buildSwapRows{grid-column:1/-1;border-top:1px solid var(--line);padding:8px 0 1px;margin-top:0;display:grid;gap:5px;min-width:0}\n.buildCard .buildSwapRows p{margin:0;color:var(--muted);font-size:9px;line-height:1.4}\n.buildCard .buildSwapRows p>strong{color:var(--muted);font-size:8px;font-weight:900;letter-spacing:.06em;text-transform:uppercase;margin-right:5px}\n.buildCard .buildSwapRows .swapNames{color:var(--ink);font-weight:800}\n'''
new_css = '''.buildCard .buildSwapRows{grid-column:1/-1;border-top:1px solid var(--line);padding:11px 0 2px;margin-top:9px;display:grid;gap:7px;min-width:0}\n.buildCard .buildSwapRows p{margin:0;display:grid;grid-template-columns:96px minmax(0,1fr);column-gap:9px;align-items:start;color:var(--muted);font-size:10px;line-height:1.5;min-width:0}\n.buildCard .buildSwapRows p>strong{color:var(--muted);font-size:9px;font-weight:850;letter-spacing:.04em;text-transform:uppercase;line-height:1.5}\n.buildCard .buildSwapRows .swapText{min-width:0;color:var(--muted)}\n.buildCard .buildSwapRows .swapNames{color:var(--ink);font-weight:750}\n@media(max-width:620px){.buildCard .buildSwapRows{margin-top:8px;padding-top:10px;gap:8px}.buildCard .buildSwapRows p{grid-template-columns:1fr;gap:2px;font-size:10px}.buildCard .buildSwapRows p>strong{font-size:9px}}\n'''

old_render = """        +techniqueSwaps.map(s=>'<p><strong>Technique Swap:</strong> '+esc(s[0])+' — <span class=\"swapNames\">'+esc(s[1])+' → '+esc(s[2])+'</span></p>').join('')\n        +charmSwaps.map(s=>'<p><strong>Charm Swap:</strong> '+esc(s[0])+' — <span class=\"swapNames\">'+esc(s[1])+' → '+esc(s[2])+'</span></p>').join('')\n"""
new_render = """        +techniqueSwaps.map(s=>'<p><strong>Technique Swap:</strong><span class=\"swapText\">'+esc(s[0])+' — <span class=\"swapNames\">'+esc(s[1])+' → '+esc(s[2])+'</span></span></p>').join('')\n        +charmSwaps.map(s=>'<p><strong>Charm Swap:</strong><span class=\"swapText\">'+esc(s[0])+' — <span class=\"swapNames\">'+esc(s[1])+' → '+esc(s[2])+'</span></span></p>').join('')\n"""

for path in paths:
    text = path.read_text(encoding='utf-8')
    if text.count(old_css) != 1:
        raise SystemExit(f'{path}: old CSS match count {text.count(old_css)}')
    text = text.replace(old_css, new_css, 1)
    if text.count(old_render) != 1:
        raise SystemExit(f'{path}: old render match count {text.count(old_render)}')
    text = text.replace(old_render, new_render, 1)
    path.write_text(text, encoding='utf-8')

print('improved build swap spacing and readability')
