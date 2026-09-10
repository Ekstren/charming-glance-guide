from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
import re

ROOT = Path('.')
INDEX = ROOT / 'index.html'
text = INDEX.read_text(encoding='utf-8')

style_re = re.compile(r'<style(?:\s+id="([^"]+)")?[^>]*>(.*?)</style>', re.S | re.I)
script_re = re.compile(r'<script([^>]*)>(.*?)</script>', re.S | re.I)
styles = style_re.findall(text)
scripts = script_re.findall(text)

print('=== INDEX ===')
print('bytes', len(text.encode('utf-8')))
print('lines', text.count('\n') + 1)
print('style_tags', len(styles), 'style_bytes', sum(len(x[1].encode('utf-8')) for x in styles))
print('script_tags', len(scripts), 'inline_script_bytes', sum(len(body.encode('utf-8')) for attrs, body in scripts if 'src=' not in attrs.lower()))
print('html_comments', len(re.findall(r'<!--.*?-->', text, re.S)))
print('mutation_observers', text.count('MutationObserver'))
print('raf_calls', text.count('requestAnimationFrame'))
print('settimeout_calls', text.count('setTimeout('))
print('important_rules', text.count('!important'))

print('\nSTYLE IDS:')
for i, (sid, body) in enumerate(styles):
    print(f'{i:02d} {sid or "<anonymous>"} {len(body.encode("utf-8"))}B')

print('\nSCRIPT IDS/SRC:')
for i, (attrs, body) in enumerate(scripts):
    sid = re.search(r'\bid="([^"]+)"', attrs)
    src = re.search(r'\bsrc="([^"]+)"', attrs)
    print(f'{i:02d} id={sid.group(1) if sid else "-"} src={src.group(1) if src else "-"} {len(body.encode("utf-8"))}B')

# Approximate duplicate selector hotspots. This is intentionally diagnostic only.
selector_hits = Counter()
for _, body in styles:
    cleaned = re.sub(r'/\*.*?\*/', '', body, flags=re.S)
    for selector in re.findall(r'(?:^|})([^@}{][^{]+)\{', cleaned):
        selector = ' '.join(selector.split())
        if selector:
            selector_hits[selector] += 1
print('\nDUPLICATE CSS SELECTOR HOTSPOTS:')
for selector, count in selector_hits.most_common(40):
    if count > 1:
        print(count, selector[:180])

markers = Counter(re.findall(r'\b[A-Z][A-Z0-9]*(?:_[A-Z0-9]+){2,}_V\d+\b', text))
print('\nVERSION/PATCH MARKERS IN INDEX:', len(markers))
for marker, count in markers.most_common():
    print(count, marker)

workflows = sorted((ROOT / '.github' / 'workflows').glob('*.y*ml'))
print('\n=== WORKFLOWS ===')
print('count', len(workflows))
active = []
oneshot = []
for wf in workflows:
    w = wf.read_text(encoding='utf-8', errors='replace')
    scheduled = bool(re.search(r'^\s*schedule\s*:', w, re.M)) or 'cron:' in w
    durable = scheduled or 'workflow_call:' in w or 'repository_dispatch:' in w or 'workflow_run:' in w
    if durable:
        active.append(wf)
    else:
        oneshot.append(wf)
    print(('KEEP ' if durable else 'SHOT '), wf.as_posix(), 'schedule' if scheduled else '')
print('durable', len(active), 'one_shot', len(oneshot))

# Files that look like historical patch machinery.
patchish = []
for base in [ROOT / '.github', ROOT / 'scripts']:
    for p in base.rglob('*'):
        if not p.is_file():
            continue
        n = p.name.lower()
        if n.startswith(('patch-', 'patch_', 'apply-', 'apply_', 'optimize-', 'optimize_', 'polish_', 'left_align_', 'fix-optimizer')):
            patchish.append(p)
print('\nPATCH-LIKE FILES', len(patchish))
for p in sorted(patchish):
    print(p.as_posix())

# Which patch-like files are still referenced by a durable workflow?
durable_text = '\n'.join(p.read_text(encoding='utf-8', errors='replace') for p in active)
referenced = []
unreferenced = []
for p in patchish:
    if p.as_posix() in durable_text or p.name in durable_text:
        referenced.append(p)
    else:
        unreferenced.append(p)
print('\nPATCH-LIKE REFERENCED BY DURABLE WORKFLOW', len(referenced))
for p in sorted(referenced): print(p.as_posix())
print('\nPATCH-LIKE UNREFERENCED', len(unreferenced))
for p in sorted(unreferenced): print(p.as_posix())

# Version families make obsolete predecessors obvious.
families = defaultdict(list)
for p in patchish:
    stem = p.stem.lower()
    stem = re.sub(r'[-_]v\d+(?:[-_]?[a-z0-9]+)?$', '', stem)
    stem = re.sub(r'[-_]n\d+(?:[-_]v\d+)?$', '', stem)
    families[(p.parent.as_posix(), stem)].append(p)
print('\nVERSION FAMILIES:')
for _, members in sorted(families.items()):
    if len(members) > 1:
        print(' | '.join(p.name for p in sorted(members)))

# Non-runtime .github files are especially suspect.
print('\nTOP-LEVEL .github NON-WORKFLOW FILES:')
for p in sorted((ROOT / '.github').iterdir()):
    if p.is_file():
        print(p.as_posix(), p.stat().st_size)

print('\n=== CORE TESTS PRESENT ===')
for name in ['scripts/check_timeline_duplicates.py','scripts/site_smoke_test.mjs','scripts/calculator_perf_check.mjs','scripts/build_swap_smoke.mjs']:
    print(name, Path(name).exists())
