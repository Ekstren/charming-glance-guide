# Charming Glance Guide

Sword x Staff (SxS) "Charming Glance" season planning guide and interactive calculator — a single-file static site hosted on GitHub Pages.

It projects your season score against a requested **Primostar target**, plans **Skill / Relic / Fantomon** upgrade slots, models **Material Realm** purchases and **Stamina** node allocation, applies the recommended **Bed EXP rollover** (34h hold + 2h final-reset boost = 36h banked for next season), and shows what happens **after** your target is reached through to season end.

- **Live site:** https://Ekstren.github.io/charming-glance-guide/
- **Stack:** plain HTML + CSS + JS (no build step). `index.html` + `assets/` is the entire site.

## What's in this repo

| Path | Purpose |
|------|---------|
| `index.html` | The whole site: calculator UI, S1/S2 rules, Astral Pact, breakpoints. |
| `assets/runtime.js` | Core calculator engine (scoring, stamina split, post-target gains, optimizer). |
| `assets/site.css` | Shared site styling and themes. |
| `assets/calculator-layout.css` | Scoped calculator layout and responsive overrides. |
| `assets/builds.js` | Build recommendations (Conqueror / Guardian / Destroyer / Dominator, etc.). |
| `assets/companions.js` | Companion guide section. |
| `assets/build-layout-icons-v1.js` | Build-summary layout reflow (legacy filename; decorative icons intentionally removed). |
| `scripts/` | Maintenance + CI test scripts (Playwright regression, mined-data snapshot, Discord feed fetch). |
| `data/` | Staged build data (`pandarial`, `warlords-rest`), the official Discord feed mirror, and `mined/` provenance snapshots. |
| `.github/workflows/` | CI + scheduled jobs (see below). |
| `LICENSE` | MIT License. |

## Validation / CI

`scripts/validate_site_v1.py` is a fast, dependency-light static gate (asset references resolve, `node --check` on every JS asset, CSS brace balance, data JSON parses, and the `window.__applyBuild*Now` cross-file hook contract — each hook called by `runtime.js` is defined by exactly one other file). It runs as the first step of `Site CI` before the Playwright browser tests, so a broken asset fails in seconds rather than minutes.

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

There's no build step. Serve the repo root:

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

## Notes

- Season deadlines and reset clocks render in the viewer's device timezone; the engine still uses the server reset boundary internally.
- Unknown late-S1 / out-of-range values are labeled as estimates rather than fabricated.
- Released under the MIT License (see `LICENSE`).
