from __future__ import annotations

from pathlib import Path
import argparse
import re

ROOT = Path('.')
INDEX = ROOT / 'index.html'
ASSETS = ROOT / 'assets'
WORKFLOWS = ROOT / '.github' / 'workflows'

KEEP_WORKFLOWS = {
    'pandarial-build-release-trigger.yml',
    'sxs-discord-feed.yml',
    'warlords-rest-roll-guide-trigger.yml',
    'site-ci.yml',
}
KEEP_SCRIPTS = {
    'fetch_discord_feed.py',
    'activate_pandarial_build_prep_v1.py',
    'validate_pandarial_build_prep_v1.py',
    'activate_warlords_rest_roll_guide_v1.py',
    'validate_warlords_rest_roll_guide_v1.py',
    'patch_build_roll_guide_v2.py',
    'check_timeline_duplicates.py',
    'site_smoke_test.mjs',
    'calculator_perf_check.mjs',
    'build_swap_smoke.mjs',
    'build_visual_stability_benchmark_v2.mjs',
}

PANDARIAL_WORKFLOW = r'''name: Activate Pandarial build prep

on:
  push:
    branches: [main]
    paths:
      - 'data/pandarial-build-prep-v1.json'
      - 'scripts/activate_pandarial_build_prep_v1.py'
      - 'scripts/validate_pandarial_build_prep_v1.py'
      - '.github/workflows/pandarial-build-release-trigger.yml'
  # Charming Glance projection: Oct 14, 2026 at the 6:00 AM PDT reset.
  schedule:
    - cron: '10 * 14-16 10 *'
  workflow_dispatch:

permissions:
  contents: write

jobs:
  activate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Validate staged Pandarial data
        run: |
          python3 -m py_compile scripts/activate_pandarial_build_prep_v1.py scripts/validate_pandarial_build_prep_v1.py
          python3 -m json.tool data/pandarial-build-prep-v1.json >/dev/null
          python3 scripts/validate_pandarial_build_prep_v1.py
      - name: Activate if release gate is live
        run: python3 scripts/activate_pandarial_build_prep_v1.py
      - name: Verify and publish activation
        run: |
          if git diff --quiet -- assets/runtime.js; then
            echo 'Pandarial is not due yet or is already active.'
            exit 0
          fi
          grep -Fq 'PANDARIAL_RELEASE_V1' assets/runtime.js
          grep -Fq "pick('Pandarial','Burst/front-load alt" assets/runtime.js
          grep -Fq "pick('Pandarial','Main aggressive Guardian lead" assets/runtime.js
          grep -Fq "pick('Pandarial','Main healer/hybrid lead" assets/runtime.js
          git config user.name 'github-actions[bot]'
          git config user.email '41898282+github-actions[bot]@users.noreply.github.com'
          git add assets/runtime.js
          git commit -m 'Activate Pandarial build recommendations'
          git pull --rebase origin main
          git push origin main
'''

WARLORD_WORKFLOW = r'''name: Activate Warlord's Rest roll guide

on:
  push:
    branches: [main]
    paths:
      - 'data/warlords-rest-roll-guide-v1.json'
      - 'scripts/activate_warlords_rest_roll_guide_v1.py'
      - 'scripts/validate_warlords_rest_roll_guide_v1.py'
      - '.github/workflows/warlords-rest-roll-guide-trigger.yml'
  # Confirmed Charming Glance unlock: Sep 12, 2026 at 6:00 AM PDT.
  schedule:
    - cron: '10 * 12 9 *'
  workflow_dispatch:

permissions:
  contents: write

jobs:
  activate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Validate staged Warlord data
        run: |
          python3 -m py_compile scripts/activate_warlords_rest_roll_guide_v1.py scripts/validate_warlords_rest_roll_guide_v1.py
          python3 -m json.tool data/warlords-rest-roll-guide-v1.json >/dev/null
          python3 scripts/validate_warlords_rest_roll_guide_v1.py
      - name: Activate if release gate is live
        run: python3 scripts/activate_warlords_rest_roll_guide_v1.py
      - name: Verify and publish activation
        run: |
          if git diff --quiet -- assets/builds.js scripts/patch_build_roll_guide_v2.py; then
            echo "Warlord's Rest is not due yet or is already active."
            exit 0
          fi
          grep -Fq 'BUILD_ROLL_GUIDE_WARLORD_V1' assets/builds.js
          grep -Fq "Warlord's Rest · Lv162" assets/builds.js
          grep -Fq 'BUILD_ROLL_GUIDE_WARLORD_V1' scripts/patch_build_roll_guide_v2.py
          git config user.name 'github-actions[bot]'
          git config user.email '41898282+github-actions[bot]@users.noreply.github.com'
          git add assets/builds.js scripts/patch_build_roll_guide_v2.py
          git commit -m "Activate Warlord's Rest roll guide"
          git pull --rebase origin main
          git push origin main
'''

SITE_CI = r'''name: Site CI

on:
  push:
    branches: [main]
    paths:
      - 'index.html'
      - 'assets/**'
      - 'data/pandarial-build-prep-v1.json'
      - 'data/warlords-rest-roll-guide-v1.json'
      - 'scripts/check_timeline_duplicates.py'
      - 'scripts/site_smoke_test.mjs'
      - 'scripts/calculator_perf_check.mjs'
      - 'scripts/build_swap_smoke.mjs'
      - 'scripts/build_visual_stability_benchmark_v2.mjs'
      - '.github/workflows/site-ci.yml'
      - '.github/workflows/pandarial-build-release-trigger.yml'
      - '.github/workflows/warlords-rest-roll-guide-trigger.yml'
  pull_request:
    paths:
      - 'index.html'
      - 'assets/**'
      - 'data/pandarial-build-prep-v1.json'
      - 'data/warlords-rest-roll-guide-v1.json'
      - 'scripts/**'
  workflow_dispatch:

permissions:
  contents: read

concurrency:
  group: site-ci-${{ github.ref }}
  cancel-in-progress: true

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Static validation
        run: |
          python3 scripts/check_timeline_duplicates.py index.html
          node --check assets/runtime.js
          node --check assets/companions.js
          node --check assets/builds.js
          node --check assets/build-layout-icons-v1.js
          python3 -m py_compile scripts/fetch_discord_feed.py scripts/activate_pandarial_build_prep_v1.py scripts/validate_pandarial_build_prep_v1.py scripts/activate_warlords_rest_roll_guide_v1.py scripts/validate_warlords_rest_roll_guide_v1.py scripts/patch_build_roll_guide_v2.py
          python3 -m json.tool data/pandarial-build-prep-v1.json >/dev/null
          python3 -m json.tool data/warlords-rest-roll-guide-v1.json >/dev/null
      - name: Install browser dependencies
        run: |
          npm init -y >/dev/null 2>&1
          npm install --no-save playwright@1.55.0 >/dev/null
          npx playwright install --with-deps chromium >/dev/null
      - name: Calculator regression/performance
        run: node scripts/calculator_perf_check.mjs
      - name: Build variant regression
        run: node scripts/build_swap_smoke.mjs
      - name: Build visual stability regression
        run: |
          node scripts/build_visual_stability_benchmark_v2.mjs | tee /tmp/build-visual.log
          python3 - <<'PY'
          import json
          line=next(x for x in open('/tmp/build-visual.log',encoding='utf-8') if x.startswith('BUILD_VISUAL_JSON='))
          row=json.loads(line.split('=',1)[1])
          n=row['switches']
          assert not row['errors'], row['errors']
          assert row['immediateFullyReady']==n, row
          assert row['firstFrameStable']==n, row
          assert row['zeroTabTransition']==n, row
          assert row['maxHeightDelta']==0, row
          print(f'Build visual stability: {n}/{n} one-paint switches, 0px shift')
          PY
      - name: Full browser smoke
        run: node scripts/site_smoke_test.mjs
'''

MAINTENANCE = r'''# Charming Glance site maintenance

## Current scope

The live guide is Season 2 / Tier 4 first. Maintain Conqueror, Guardian, Destroyer, and Dominator plus the current and next-season timeline. Do not revive retired Season 1/Tier 3 presentation code unless it is required to migrate saved data safely.

## Build requirements

- Class switching must be one-paint: no staged layout, delayed hero reflow, or animated selected-state flicker.
- Current activity tabs are Dungeon, Crucible / Conquest, Arena, and Tournament. Tournament owns its 2v2 / 4v4 selector.
- Dominator keeps one inline DPS / Heals selector beside the class title.
- Keep the compact five-slot stat priorities and full substat line.
- Keep Technique investment on the left and Charm investment on the right on desktop; stack in that order on mobile.
- Each visible build shows the equipped Techniques/Charms and exactly Main + two Alt Fantomon choices.
- Investment recommendations must be drawn from items actually equipped in a maintained loadout.
- Build notes should be player-facing guidance, not changelog/editorial copy.

## Runtime ownership

- `index.html` owns markup only.
- `assets/site.css` owns the consolidated visual cascade.
- `assets/runtime.js` owns the core timeline/calculator/build data runtime.
- `assets/companions.js` owns Companion presentation enhancements.
- `assets/builds.js` owns the rich Builds presentation/enhancers.
- `assets/build-layout-icons-v1.js` owns the final Build hero/icon layout layer.
- Avoid adding new inline `<style>` or inline `<script>` patches. Change the owning asset directly.
- Avoid broad attribute-observing `MutationObserver`s. Prefer explicit render hooks; observers should only watch boundaries that truly originate outside the owning module.

## Regression gates

`site-ci.yml` is the canonical site test workflow. It locks timeline de-duplication, calculator performance/determinism, all current build variants, one-paint class switching, desktop/mobile layout, and full browser smoke behavior.

## Scheduled content gates

- Warlord's Rest roll-guide activation is date-gated for the confirmed Sep 12 reset and updates `assets/builds.js` plus the maintained roll-guide source.
- Pandarial recommendations remain staged until the Oct 14 release gate and update `assets/runtime.js`.
- `sxs-discord-feed.yml` is the only continuous data mirror and updates only `data/sxs-official-discord-feed.json`.

## Evidence

Prefer official Global/Charming Glance evidence, then reputable current guides/databases, repeated community testing, and only then older-server cadence. Event existence does not by itself confirm a Charming Glance date.
'''


def rel(path: Path) -> str:
    return path.as_posix()


def externalize_css(text: str) -> str:
    head_match = re.search(r'<head\b[^>]*>(.*?)</head>', text, re.S | re.I)
    if not head_match:
        raise SystemExit('No <head> found')
    head = head_match.group(1)
    tag_re = re.compile(r'<style\b([^>]*)>(.*?)</style>|<link\b([^>]*\brel=["\']stylesheet["\'][^>]*)>', re.S | re.I)
    parts = []
    matches = []
    for m in tag_re.finditer(head):
        if m.group(2) is not None:
            attrs, body = m.group(1), m.group(2)
            sid = re.search(r'\bid=["\']([^"\']+)', attrs or '', re.I)
            label = sid.group(1) if sid else 'legacy-base'
            parts.append(f'\n/* ---- {label} ---- */\n{body.strip()}\n')
            matches.append(m)
        else:
            attrs = m.group(3) or ''
            href = re.search(r'\bhref=["\']([^"\']+)', attrs, re.I)
            if not href:
                raise SystemExit('Stylesheet link without href')
            href = href.group(1)
            if href != 'assets/build-layout-icons-v1.css':
                raise SystemExit(f'Unexpected stylesheet during consolidation: {href}')
            source = ROOT / href
            if not source.exists():
                raise SystemExit(f'Missing stylesheet: {href}')
            parts.append(f'\n/* ---- build layout icons ---- */\n{source.read_text(encoding="utf-8").strip()}\n')
            matches.append(m)
    style_count = sum(1 for m in matches if m.group(2) is not None)
    if style_count < 50:
        raise SystemExit(f'Expected layered legacy CSS; found only {style_count} style tags')
    ASSETS.mkdir(exist_ok=True)
    css = ''.join(parts).lstrip()
    (ASSETS / 'site.css').write_text(css, encoding='utf-8')

    first = True
    out = []
    cursor = 0
    for m in matches:
        out.append(head[cursor:m.start()])
        if first:
            out.append('<link rel="stylesheet" href="assets/site.css">')
            first = False
        cursor = m.end()
    out.append(head[cursor:])
    new_head = ''.join(out)
    return text[:head_match.start(1)] + new_head + text[head_match.end(1):]


def externalize_js(text: str) -> str:
    script_re = re.compile(r'<script\b([^>]*)>(.*?)</script>', re.S | re.I)
    matches = list(script_re.finditer(text))
    inline = [m for m in matches if not re.search(r'\bsrc\s*=', m.group(1) or '', re.I)]
    external = [m for m in matches if re.search(r'\bsrc\s*=', m.group(1) or '', re.I)]
    if len(inline) != 7:
        raise SystemExit(f'Expected 7 inline runtime scripts; found {len(inline)}')
    if len(external) != 1 or 'assets/build-layout-icons-v1.js' not in (external[0].group(1) or ''):
        raise SystemExit('Unexpected external script layout; refusing to reorder runtime')
    # Only classic scripts are safe to concatenate this way.
    for m in inline:
        attrs = m.group(1) or ''
        typ = re.search(r'\btype=["\']([^"\']+)', attrs, re.I)
        if typ and typ.group(1).lower() not in ('text/javascript', 'application/javascript'):
            raise SystemExit(f'Unexpected inline script type: {typ.group(1)}')

    bodies = [m.group(2).strip() for m in inline]
    (ASSETS / 'runtime.js').write_text(bodies[0] + '\n', encoding='utf-8')
    (ASSETS / 'companions.js').write_text(bodies[1] + '\n', encoding='utf-8')
    (ASSETS / 'builds.js').write_text('\n\n/* ---- build module boundary ---- */\n\n'.join(bodies[2:]) + '\n', encoding='utf-8')

    replacements = {
        inline[0].start(): '<script src="assets/runtime.js"></script>',
        inline[1].start(): '<script src="assets/companions.js"></script>',
        inline[2].start(): '<script src="assets/builds.js"></script>',
    }
    out = []
    cursor = 0
    inline_starts = {m.start(): m for m in inline}
    for m in matches:
        if m.start() not in inline_starts:
            continue
        out.append(text[cursor:m.start()])
        out.append(replacements.get(m.start(), ''))
        cursor = m.end()
    out.append(text[cursor:])
    return ''.join(out)


def update_delayed_activators() -> None:
    p = ROOT / 'scripts' / 'activate_pandarial_build_prep_v1.py'
    s = p.read_text(encoding='utf-8')
    old = "TARGETS = [ROOT / 'index.html', ROOT / '.github' / 'build-fantomons-inject.html']"
    new = "TARGETS = [ROOT / 'assets' / 'runtime.js']"
    if old not in s and new not in s:
        raise SystemExit('Pandarial TARGETS anchor not found')
    p.write_text(s.replace(old, new, 1), encoding='utf-8')

    p = ROOT / 'scripts' / 'activate_warlords_rest_roll_guide_v1.py'
    s = p.read_text(encoding='utf-8')
    old = "FILES = [Path('index.html'), Path('scripts/patch_build_roll_guide_v2.py')]"
    new = "FILES = [Path('assets/builds.js'), Path('scripts/patch_build_roll_guide_v2.py')]"
    if old not in s and new not in s:
        raise SystemExit('Warlord FILES anchor not found')
    p.write_text(s.replace(old, new, 1), encoding='utf-8')

    (WORKFLOWS / 'pandarial-build-release-trigger.yml').write_text(PANDARIAL_WORKFLOW, encoding='utf-8')
    (WORKFLOWS / 'warlords-rest-roll-guide-trigger.yml').write_text(WARLORD_WORKFLOW, encoding='utf-8')
    (WORKFLOWS / 'site-ci.yml').write_text(SITE_CI, encoding='utf-8')
    (ROOT / '.github' / 'build-maintenance.md').write_text(MAINTENANCE, encoding='utf-8')


def refactor() -> None:
    original = INDEX.read_text(encoding='utf-8')
    if 'assets/site.css' in original:
        print('Structural extraction already present; skipping extraction.')
    else:
        text = externalize_css(original)
        text = externalize_js(text)
        INDEX.write_text(text, encoding='utf-8')
    update_delayed_activators()

    runtime = (ASSETS / 'runtime.js').read_text(encoding='utf-8')
    builds = (ASSETS / 'builds.js').read_text(encoding='utf-8')
    if 'const FANTO={' not in runtime:
        raise SystemExit('Pandarial FANTO source did not land in assets/runtime.js')
    if 'const R={' not in builds:
        raise SystemExit('Roll guide source did not land in assets/builds.js')
    if '<style' in INDEX.read_text(encoding='utf-8').lower():
        raise SystemExit('Inline <style> remained after extraction')
    inline_scripts = [m for m in re.finditer(r'<script\b([^>]*)>(.*?)</script>', INDEX.read_text(encoding='utf-8'), re.S | re.I) if not re.search(r'\bsrc\s*=', m.group(1) or '', re.I)]
    if inline_scripts:
        raise SystemExit(f'{len(inline_scripts)} inline scripts remained after extraction')
    print('Externalized CSS and runtime modules; delayed release activators retargeted.')


def prune() -> None:
    # One-shot workflows have already baked their changes into the runtime. Keep only continuous/date-gated jobs + canonical CI.
    for p in WORKFLOWS.glob('*.y*ml'):
        if p.name not in KEEP_WORKFLOWS:
            p.unlink()

    # Historical patch/injection machinery under .github is no longer runtime source of truth.
    gh = ROOT / '.github'
    for p in list(gh.iterdir()):
        if p.is_file() and p.name != 'build-maintenance.md':
            p.unlink()
    gh_scripts = gh / 'scripts'
    if gh_scripts.exists():
        for p in sorted(gh_scripts.rglob('*'), reverse=True):
            if p.is_file(): p.unlink()
            elif p.is_dir(): p.rmdir()
        if gh_scripts.exists(): gh_scripts.rmdir()

    scripts = ROOT / 'scripts'
    for p in scripts.iterdir():
        if p.is_file() and p.name not in KEEP_SCRIPTS:
            p.unlink()

    # Temporary audit/refactor artifacts and retired trigger file.
    for p in [ROOT / 'data' / 'site-cleanup-audit.txt', ROOT / 'build-fantomons.trigger', ASSETS / 'build-layout-icons-v1.css']:
        if p.exists(): p.unlink()

    # Remove empty dirs under .github, except workflows.
    for p in sorted(gh.rglob('*'), reverse=True):
        if p.is_dir() and p != WORKFLOWS:
            try: p.rmdir()
            except OSError: pass

    workflows = sorted(WORKFLOWS.glob('*.y*ml'))
    if {p.name for p in workflows} != KEEP_WORKFLOWS:
        raise SystemExit(f'Unexpected workflow set after prune: {[p.name for p in workflows]}')
    script_names = {p.name for p in scripts.iterdir() if p.is_file()}
    missing = KEEP_SCRIPTS - script_names
    if missing:
        raise SystemExit(f'Prune removed required scripts: {sorted(missing)}')
    print(f'Pruned repository to {len(workflows)} workflows and {len(script_names)} maintained scripts.')


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--refactor', action='store_true')
    ap.add_argument('--prune', action='store_true')
    args = ap.parse_args()
    if not args.refactor and not args.prune:
        ap.error('choose --refactor or --prune')
    if args.refactor: refactor()
    if args.prune: prune()
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
