# Charming Glance Guide

Sword x Staff (SxS) "Charming Glance" season planning guide and interactive calculator — a single-file static site hosted on GitHub Pages.

It projects your season score against a requested **Primostar target**, plans **Skill / Relic / Fantomon** upgrade slots, models **Material Realm** purchases and **Stamina** node allocation, applies the recommended **Bed EXP rollover** (34h hold + 2h final-reset boost = 36h banked for next season), and shows what happens **after** your target is reached through to season end.

- **Live site:** https://Ekstren.github.io/charming-glance-guide/
- **Stack:** plain HTML + CSS + JS, with an esbuild/PostCSS source build. `index.html` + `assets/` is the entire site.

## What's in this repo

| Path | Purpose |
|------|---------|
| `index.html` | The whole site: calculator UI, S1/S2 rules, Astral Pact, breakpoints. |
| `src/app.mjs` | Lightweight site shell, Timeline and section loading. |
| `src/calculator/` | Calculator model, search engine, saved state, rendering and controller. |
| `src/calculator-loader.mjs` | Load-on-demand lifecycle and retry handling. |
| `src/navigation.mjs`, `src/time.mjs`, `src/timeline-data.mjs` | Navigation, Pacific reset calculations and timeline content. |
| `assets/runtime.js` | Generated lightweight site shell. |
| `assets/calculator.js` | Generated calculator chunk, requested when its section is opened. |
| `src/styles/` | Readable legacy, calculator and shared layout rules, in explicit source order. |
| `assets/site.css` | Generated combined stylesheet. |
| `assets/builds.js` | Build recommendations (Conqueror / Guardian / Destroyer / Dominator, etc.). |
| `assets/companions.js` | Companion guide section. |
| `assets/build-layout-icons-v1.js` | Build-summary layout reflow (legacy filename; decorative icons intentionally removed). |
| `scripts/` | Maintenance + CI test scripts (Playwright regression, mined-data snapshot, Discord feed fetch). |
| `data/` | Staged build data (`pandarial`, `warlords-rest`), the official Discord feed mirror, and `mined/` provenance snapshots. |
| `.github/workflows/` | CI + scheduled jobs (see below). |
| `LICENSE` | MIT License. |

## Validation / CI

`scripts/validate_site_v1.py` is a fast, dependency-light static gate (asset references resolve, `node --check` on every JS asset, CSS brace balance, data JSON parses, and the `window.__applyBuild*Now` cross-file hook contract — each hook called by `src/builds.mjs` is defined by exactly one other file). It runs as the first step of `Site CI` before the Playwright browser tests, so a broken asset fails in seconds rather than minutes.

## Data sources

Calculator cost/EXP tables and build data are normalized from public datamine-backed sources:

- **0xNobody** — SxS loadout builder, Primo calculator, companions, Stellaris, wardrobe catalogs.
- **Mystonats** — SxS skill tables.

These are snapshotted into `data/mined/` by the `Snapshot mined SxS game data` workflow (run on demand) and cross-checked during CI. The `data/mined/` tree is a **provenance snapshot** for auditability — the live site does not fetch from it at runtime.

## CI / workflows

| Workflow | Trigger | What it does |
|----------|---------|--------------|
| `Site CI` | push/PR to `main` (site paths) | Static validation, `node --check`, plus Playwright regression: calculator perf, build-variant swap, visual stability, full smoke, mobile layout. |
| `Mirror Sword x Staff Discord feed` | every 10 min | Fetches official SxS Discord announcements → `data/sxs-official-discord-feed.json`. |
| `Snapshot mined SxS game data` | manual / data paths | Re-clones upstream datamines and refreshes `data/mined/`. |
| `Activate Pandarial build prep` | date-gated (Oct 14, 2026 reset) | Flips the staged Pandarial recommendations live. |
| `Activate Warlord's Rest roll guide` | date-gated (Sep 12, 2026 reset) | Flips the staged Warlord's Rest roll guide live. |

One-shot "patch" workflows from earlier development were deliberately **not** kept — those changes are already merged into `main`, and keeping push-triggered patch jobs only re-ran and failed on every commit.

## Running the site locally

Generated assets are committed, so serving the repo works immediately. After editing `src/`, regenerate them with `npm ci` followed by `npm run build`. CI rejects stale generated files. Serve the repo root:

```
python -m http.server 8000
```

Then open `http://localhost:8000`.

## Running the CI test suite

```
npm ci
npx playwright install --with-deps chromium
npm run test:static
npm test
```

Use `npm run test:perf` for the calculator benchmark or `npm run test:optimizer`
for allocation-cache and cancellation regression checks. Set `SXS_PERF_OUTPUT` to
a file path to save benchmark timings and result fingerprints for before/after
comparisons. Performance scenarios require a completed numeric result; the S2
missing-production placeholder is not counted as a successful solve.

`npm run test:layout` checks populated calculator results and expanded custom
settings in light and dark themes at six widths from 320 to 1440 px. Set
`SXS_LAYOUT_SCREENSHOTS` to an output directory to also capture layout screenshots.

`npm run test:readability` covers all four sections and class variants at nine
widths from 320 to 1710 px in both themes. It checks equal-width navigation,
consistent page margins, readable body text and horizontal overflow. Set
`SXS_READABILITY_SCREENSHOTS` to a directory to save section screenshots.

See [Calculator modules and loading](docs/calculator-modules.md) for module ownership, saved-state compatibility, lazy-loading tests and rollback instructions.

## Visual and performance regression checks

`npm run test:visual` renders the approved Git commit in `scripts/visual-baseline.json`
and the working tree with the same installed Chromium. It compares 88 screenshots:
all four sections plus populated calculator results and the season controls, at
390, 650 and 1440 px in both themes, plus full-section class/role variants and expanded controls at 390/1440 px. The clock, locale, timezone and external
requests are fixed. Pixel differences fail the check; expected/actual/diff images
are written to `test-results/visual/` and uploaded by CI. A full Git history is
required so the baseline commit can be archived. Update the baseline commit only
after an intentional appearance change has been reviewed; do not update it to
silence an unexplained regression. This avoids platform-specific font snapshots.

`npm run test:mobile-perf` runs the approved baseline and working tree three times
each at a 390 px viewport with 4× CPU slowdown. The report records median solve,
worst scenario, local load and first-calculator-use timings, plus the longest main-thread task. Relative
budgets allow timing noise but fail substantial regressions. Reports are in
`test-results/performance/` and CI artifacts. These are CPU simulations on the
runner, not measurements from a physical phone or a mobile network.

Source CSS retains cascade order and conditional rules. The build removes only
superseded declarations for identical selectors/properties/priorities/conditions;
it does not reorder selectors or flatten media queries. New shared styling belongs
in `src/styles/shared.css`; calculator-specific styling belongs in
`src/styles/calculator.css`. `scripts/minify_css.py` is deprecated: use the source
build so generated files stay reproducible.

## Notes

- Season deadlines and reset clocks render in the viewer's device timezone; the engine still uses the server reset boundary internally.
- Unknown late-S1 / out-of-range values are labeled as estimates rather than fabricated.
- Released under the MIT License (see `LICENSE`).

See [site loading and startup budgets](docs/site-loading.md) for guide chunk ownership, CSS cleanup, and loading regression checks.
