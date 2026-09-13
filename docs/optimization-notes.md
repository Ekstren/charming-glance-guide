# Calculator optimization results

Measured locally on Windows with Node 24.19.0, Playwright 1.55.1 and Chromium 140,
against commit `f883015`. The site remains plain HTML/CSS/JavaScript with no build
step or production dependencies.

## Changes

- Cooperative search checkpoints return a promise only when a browser yield is
  actually due. Hot loops skip `await` otherwise, avoiding per-candidate promise
  allocation and microtask scheduling while retaining cancellation checks and
  the existing 8 ms yield threshold.
- Realm cost caches are cleared during the existing acquisition prepass for
  each resource allocation, in both synchronous and cooperative searches.
  Auto-Stamina shares structural options between allocations; the previous cache
  incorrectly treated those options as search-local. A new regression fails on
  the baseline when reusing a context for the second allocation, and passes after
  the fix. Direct property reads and lazy Realm calculations remain in place.
- Performance fixtures use positive, near-zero Cart rates when exercising scarce
  resources. Previously three fixtures stopped at the S2 required-input guard,
  so their apparent performance measured a placeholder rather than a search.
  Each scenario now requires a numeric result.
- `npm test` runs the browser suite. Dependencies are pinned in `package-lock.json`,
  CI uses `npm ci`, and package changes trigger CI. Playwright moves from 1.55.0
  to the certificate-verification patch in 1.55.1; npm audit reports no findings.
- The visual-stability script now exits unsuccessfully on regressions when run
  locally, matching the existing CI assertions.

## Measurements

Both versions used the corrected fixtures, the same browser, and frozen wall-clock
time. Three runs per version alternated baseline/modified ordering. Values below
are medians of the app's `lastSolveMs` measurement, not network/page-load times.
All six result fields (score, total, upgrades, gear, costs and stamina) matched
across every before/after run in this benchmark.

| Scenario | Before | After | Change |
| --- | ---: | ---: | ---: |
| Realistic mixed resources | 101.1 ms | 38.0 ms | 62% lower |
| Repeat of same inputs | 2.7 ms | 2.9 ms | 0.2 ms higher |
| Abundant raw materials | 142.8 ms | 125.8 ms | 12% lower |
| Tool-heavy resources | 106.0 ms | 85.4 ms | 19% lower |
| High target, mixed resources | 155.2 ms | 86.3 ms | 44% lower |
| Production-only low target | 17.7 ms | 11.5 ms | 35% lower |
| Near-zero Cart, low target | 30.3 ms | 40.0 ms | 9.7 ms higher |

The rapid eight-edit burst had median end-to-end times of 216 ms before and
211 ms after. These local measurements are directional, not guarantees for every
device. The small low-resource case regressed; cache correctness takes precedence
over retaining stale calculations. The benchmark outputs staying the same does
not imply all previously incorrect Auto-Stamina recommendations stay the same.

## Validation

- Static site validation, timeline duplicate checks and both staged-release data
  validators pass.
- Shared-context/fresh-context comparisons cover three resource allocations in
  both search engines; synchronous/cooperative parity is also checked.
- Checkpoint tests cover yielding, cancellation before a yield and cancellation
  during a yield.
- Calculator scenarios, deterministic repeats and rapid edits pass.
- All 30 build variants pass swap checks; all 16 visual switches are immediately
  ready with zero measured height shift.
- Full browser smoke and mobile layout audits at 320, 360, 390, 430 and 768 px pass.

Run `npm ci`, `npx playwright install chromium`, `npm run test:static`, then
`npm test`. To capture timing/result JSON, set `SXS_PERF_OUTPUT` to a destination
file and run `npm run test:perf`. Keep fixture inputs and browser versions identical
when comparing revisions.
