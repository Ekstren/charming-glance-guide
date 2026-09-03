from pathlib import Path

FILES = [
    Path('index.html'),
    Path('.github/build-fantomons-inject.html'),
    Path('scripts/patch_meta_build_modes_v1.py'),
]

OLD = """      grid.before(box);
    }
    grid.classList.add('metaModeGrid');"""
NEW = """    }
    // Keep the scenario selector immediately above the activity build card. Rich
    // role-specific investment panels (Guardian/Dominator) may be inserted later,
    // so re-anchor the selector after those panels instead of leaving it above them.
    if(box.nextElementSibling!==grid) grid.before(box);
    grid.classList.add('metaModeGrid');"""

for path in FILES:
    text = path.read_text(encoding='utf-8')
    if NEW in text:
        print(f'{path}: already patched')
        continue
    if OLD not in text:
        raise RuntimeError(f'{path}: scenario control insertion anchor not found')
    text = text.replace(OLD, NEW, 1)
    path.write_text(text, encoding='utf-8')
    print(f'{path}: moved scenario selector to immediately before build grid')
