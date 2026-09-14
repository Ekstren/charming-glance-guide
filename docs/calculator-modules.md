# Calculator modules and loading

The shell in `src/app.mjs` handles Timeline and navigation without importing calculator
modules. `src/calculator-loader.mjs` requests `assets/calculator.js` on the first
Calculator visit. The content-derived version query avoids using an old cached
calculator chunk with a new shell. Classic scripts preserve direct file:// use.

## Ownership

- `src/calculator/model.mjs`: progression tables, scoring and resource costs.
- `src/calculator/engine.mjs`: synchronous/cooperative search and allocation.
  Its input adapters come from the controller; it never accesses DOM or storage.
- `src/calculator/state.mjs`: saved-plan schema, snapshot aging, legacy migration
  and post-target preferences. The existing storage keys and schema are preserved.
- `src/calculator/render.mjs`: result cards, resource summaries and season UI.
- `src/calculator/controller.mjs`: input events, shared session values,
  cancellation, scheduling and the initialize/activate lifecycle.
- `src/preferences.mjs`: lightweight theme restoration without loading or
  overwriting a calculator profile.

The adapters expose live controller bindings so cancellation and snapshot state
are not copied into competing module-local versions. Existing solver formulas and
comparison rules are retained. Run `npm run build` after editing source; it builds
both browser chunks and the combined stylesheet. Never edit generated assets.

## Loading behavior

Concurrent opens share one promise and controller. Inputs are inert until saved
state and event handlers are restored. A failed download shows a retry button;
other sections remain usable. Finishing a download after leaving the tab neither
switches tabs nor starts a hidden solve. A saved Calculator tab loads automatically
on refresh. Theme selection works before and after loading, including storage
failure, without writing blank defaults into a saved profile.

## Verification

- `npm run test:lazy`: cold/warm visits, saved-tab reload, saved input/theme,
  delayed download, protected early clicks, retry, rapid navigation and unavailable
  storage.
- `npm run test:boundaries`: no DOM/storage access in the model or engine; storage
  I/O belongs to the state module rather than the controller.
- `npm run test:build`: generated assets match source; the shell bundle cannot
  contain calculator modules.
- Existing optimizer, screenshot, layout and smoke checks remain in CI. Tests wait
  for the readiness boundary before programmatically setting calculator inputs.
- Mobile comparisons include local startup, first calculator use, subsequent
  solves, long tasks and recommendation fingerprints against the approved baseline.

## Release and rollback

Ship this refactor as a separate merge commit after CI passes. If deployment or
live calculator checks fail, revert that merge with `git revert -m 1 <merge-sha>`
and push the revert. This restores both the old shell and calculator implementation.
The saved-plan schema is unchanged, so a code rollback does not require migrating
user profiles. The new theme preference key is harmless to older versions.
