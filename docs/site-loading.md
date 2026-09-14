# Site loading and startup budgets

Only `assets/runtime.js` loads with the page. It owns navigation, theme restoration,
Timeline rendering, and Timeline corrections. The latter live in
`src/timeline-patches.mjs`; they must not depend on opening Builds.

`src/guide-loader.mjs` loads each guide once on its first visit:

| Section | Source entry | Generated asset |
| --- | --- | --- |
| Builds | `src/builds.mjs` | `assets/builds-section.js` |
| Companions | `src/companions.mjs` | `assets/companions-section.js` |
| Calculator | `src/calculator/controller.mjs` | `assets/calculator.js` |

Chunks use content-derived version queries. Downloads are shared across repeated
clicks, expose an accessible loading/retry message, and leave the current tab alone
if the user navigates away. Controls stay inert until their section is ready.
Classic script bundles preserve local `file://` previews.

Build recommendation data and presentation helpers remain in `assets/builds.js`
and `assets/build-layout-icons-v1.js`, which are imported by the build entry rather
than loaded by HTML. Edit those maintained sources and run `npm run build`.
The scheduled recommendation activation workflows also rebuild and commit the
generated chunk and its versioned shell.

## Build updates

The controller mounts the selected template, then runs one synchronous enhancement
pipeline: meta content, rich layout, meta placement, roll guide, hero layout, and
tooltip preparation. The second meta pass positions controls after newly created
priority panels. Class and role changes call this pipeline directly. Build DOM
observers and delayed enhancement queues are removed, preventing observer echoes
and intermediate layouts. Responsive roll disclosures still update on a breakpoint
change, and tooltips still close when their source element is removed.

## CSS maintenance

The cleanup removed 488 selector branches in 61 retired markup families, including
old projection callouts, stamina controls, accuracy grids, resource summaries,
Timeline detail panels, and companion season controls. None of those class names
appeared in the maintained HTML or JavaScript. Selectors with live branches retain
those branches in their original cascade order. Dynamic category classes, active
states, media queries, and differing-value fallback declarations are retained.
This is a reviewed source cleanup, not automatic runtime coverage-based purging.

## Verification

- `npm run test:guides`: no eager guide/calculator downloads, one request per guide,
  saved-tab restoration, retry, navigation races, and blocked storage. Startup
  budgets are 60 KB of uncompressed JavaScript, 220 KB of CSS, and no individual
  startup task over one second with a 4x CPU slowdown. These allow some machine
  variance; browser/CPU simulations do not represent every phone.
- `npm run test:visual`: the original 36 approved viewport comparisons plus 52
  full-section comparisons for Build/Companion class and role variants, expanded
  Calculator controls, and the complete Timeline, in light/dark at 390/1440 px.
- Existing optimizer, layout, readability, build switch, and mobile performance
  regressions remain required by CI.

Release as a merge commit so `git revert -m 1 <merge-commit>` restores the previous
implementation and all matching generated assets without rewriting main history.
