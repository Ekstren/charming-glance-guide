# Relic database

`relics.json` is the maintained, reusable database. The UI imports it at build time;
the browser never queries another site's database. Edit this file, then run
`npm run build` and `npm run test:relics`.

## Coverage, checked 2026-09-23

- 1,130 catalog entries with 1,130 local icons.
- 30 exact Destiny Exploration locations verified in named guides or an in-game screenshot.
- Six named Mythics have a guide-supported exclusion from targeted Destiny Exploration.
- Two additional relics have verified event acquisition routes.
- All other source lists and Destiny Fruit availability remain unverified. An empty source
  list does not mean there is no way to acquire a relic.
- This is the full public catalog snapshot, not a verified list of relics currently
  released on every Global server. Unknown catalog regions/elements remain null.

## Site visibility: through Loong Haven Relic II

The full catalog is retained. An explicit per-entry `visible` flag limits the UI,
collection denominator, filters and target mode to 377 entries: Verdantglade (71),
Cinder Ridge (72), Aqualis (71), Loong Haven (161), Lucky Statue and Primal Gem.
753 later-region or release-unverified special relics are hidden. New imports
default to hidden; changing visibility never deletes saved ownership.

The [EOG database](https://eog.gg/games/sword-x-staff/) has Dragon I and Dragon II
rosters of 80 each and no Dragon III tier. The catalog's Loong Haven pool has 160
set relics plus Golden Loong Token. The cutoff uses this current regional pool;
an individual I/II classification is not claimed for every relic, and the token's
exact release phase is not independently established. It remains included as a
Loong Haven regional relic. This is a frozen allowlist, so future catalog additions
cannot silently extend the cutoff. The two visible event relics have early-region
event evidence; other special relics stay hidden pending release verification.

## Sources and decisions

1. [Loot & Waifus public relic export](https://lootandwaifus.com/api/swordxstaff/treasures.json)
   supplies stable IDs, names, rarity codes, elements, regions, and icon names.
   [API documentation](https://lootandwaifus.com/guides/sword-x-staff-api/).
   R = Rare, SR = Epic, SSR = Legendary, Rainbow = Mythic, cross-checked against
   named relics in Prydwen. The export does **not** contain acquisition sources.
2. Prydwen [Duelist](https://www.prydwen.gg/sword-x-staff/guides/build-guide-duelist),
   [Archmage](https://www.prydwen.gg/sword-x-staff/guides/build-guide-archmage), and
   [Knight](https://www.prydwen.gg/sword-x-staff/guides/build-guide-knight) guides
   supply explicit locations. Clear typos `Cindy Ridge` and `Verdantglate` were
   normalized; `Mirror of Reflection` was matched to `Mirror of Reflections`.
3. EOG's [Destiny Fruit guide](https://eog.gg/games/sword-x-staff/guides/destiny-fruit/)
   includes an [in-game source screenshot](https://eog.gg/assets/games/sword-x-staff/guides/destiny-fruit-step2-source.webp)
   confirming Blade Saw, Cinder Ridge V, Kingdom Gacha, and Element Gacha.
   Its [Grand Treasure Hunt guide](https://eog.gg/games/sword-x-staff/guides/grand-treasure-hunt/)
   documents Lucky Statue and Primal Gem event sources. The recorded phases are
   guide-specific and may differ across servers or later rotations.
4. [SXS Codex's detailed relic wiki](https://sxs.olegendary.ru/index.php?page=wiki-category&slug=relics&lang=en)
   was checked. Its visible source fields supplied regions rather than exact zones,
   and its Zephyr Headband rarity disagreed with both Prydwen and Loot & Waifus.
   Those conflicting rarity values were not imported.

Mythic exclusions are limited to the six named recommendations supported by the
Knight guide. They are not extrapolated to all Mythics. `destinyFruit` describes
targeted Destiny Exploration; it does not promise exhaustive coverage of indirect
merchant/event rewards triggered while spending fruits. Hero's Guide in EOG has
not been conclusively matched to Hero's Handbook in the catalog and was not merged.

## Schema and corrections

Each entry has a stable `id` (also the ownership key), `name`, local `image`, `rarity`,
`element`, `region`, `zone`, `destinyFruit`, `sources`, `sourceUrl`, and `verifiedAt`.
Verified acquisition entries also have `evidenceUrls`. Each source has `type`,
`location`, `url`, and optional `notes`.

- Use the full exact zone, e.g. `Cinder Ridge XVIII`; do not substitute a region.
- `destinyFruit: true` needs positive location/acquisition evidence.
- `destinyFruit: false` needs explicit exclusion evidence. Missing data is `null`.
- Preserve stable IDs across spelling corrections so saved collections survive.
- Do not merge by name: two catalog entries are called Ancient Tablet.
- Add every verified acquisition source; one route does not exclude other routes.
- For a relic with multiple exact exploration zones, extend the model and UI before
  importing it; the current dataset has one verified exact zone per target.

`scripts/import_relic_catalog.mjs snapshot.json` adds new catalog entries while
preserving identity corrections and researched acquisitions. It does not remove
existing relics or download images. Review the diff and add local icons before building.

## Images

Icons were downloaded from `https://lootandwaifus.com/treasures/swordxstaff/<icon>`
into `assets/relics/`. They are game artwork, retained with original filenames;
no ownership of the artwork is claimed. UI and collection features are implemented
locally. Icons lazy-load; no third-party image host is contacted by this page.
