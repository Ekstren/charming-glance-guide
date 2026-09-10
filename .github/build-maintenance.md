# Charming Glance site maintenance

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
- Pandarial recommendations remain staged until the Oct 14 release gate and update `assets/builds.js`.
- `sxs-discord-feed.yml` is the only continuous data mirror and updates only `data/sxs-official-discord-feed.json`.

## Evidence

Prefer official Global/Charming Glance evidence, then reputable current guides/databases, repeated community testing, and only then older-server cadence. Event existence does not by itself confirm a Charming Glance date.
