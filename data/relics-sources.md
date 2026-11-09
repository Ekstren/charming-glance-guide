# Relic database

`relics.json` is the maintained, reusable database. The UI imports it at build time;
the browser never queries another site's database. Edit this file, then run
`npm run build` and `npm run test:relics`.

## Coverage, checked 2026-11-08

- 1,130 retained catalog entries and local icons; saved ownership IDs are unchanged.
- 640 entries visible through Aethyris Relic III: the previous 400 plus all 240
  Aethyris relics, divided into three pools of 80 (20 of each rarity per pool).
- 83 relics have positive targeted Destiny Exploration evidence, including 54
  Aethyris I relics across 18 numbered Aethyris areas.
- All 60 Aethyris sets now have game-data English names and numeric bonuses.
- Aethyris effects and elemental stats use the current game-config baseline:
  relic +1, zero stars, before the equipped-slot bonus. That reference is shown
  in the detail dialog. Earlier-region effects and all in-game verification
  overrides are retained unchanged.
- An empty acquisition list or missing numbered exploration area remains unknown,
  rather than becoming a claim that the relic is unobtainable.

## Site visibility: through Aethyris Relic III

Visibility covers Verdantglade 70, Cinder Ridge 70, Aqualis 70, Loong Haven I 80,
Loong Haven II 80, Aethyris I/II/III 80 each, and Other 30. The initial filter is
Aethyris I for the current Season 3 guide. Loong Haven II no longer says upcoming.
Aethyris II/III are catalog previews until their Season 3 Day 31/61 unlocks;
the tab markers disappear after those reset dates, using the maintained
`S2_END` rollover anchor rather than permanent upcoming labels.

Six user-provided in-game Other screenshots (19/30), dated 2026-09-23, confirm
all 30 names and rarities: 15 Mythics, 14 Legendaries, one Epic. Every entry maps
to an existing catalog ID and local icon. Elements and acquisition locations
are not shown and remain subject to the existing source limitations.

EOG independently lists the first three pools as 70 each and Dragon I/II as 80 each.
The screenshots confirm the five catalog regional extras belong in Other:
Hero's Arbor Emblem, Ancient Tablet, Aquorigin Charm, Golden Loong Token, and
Portable Air Temperature Controller I. Their catalog/EOG elemental conflicts
remain unresolved. Ancient Tablet uses ID treasure_61925; a later relic shares its name.

490 later or release-unverified records remain hidden. New imports default to hidden.
Visibility changes preserve saved ownership. Loong assignments carry per-record evidence.

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

5. [Relic Inspector](https://kakotheris.neocities.org/relics) and its public
   [extracted relic tables](https://kakotheris.neocities.org/relic_data.js), checked
   2026-11-08, game package `130_156581`, supply the Aethyris pool membership,
   exact exploration areas, base stats, English set names, and numeric set bonuses.
   All 240 IDs, names, rarities, and elements match the retained catalog. Only
   selected underlying game facts were normalized into this repository's existing
   schema; the Inspector's AGPL tool code and extraction schema were not copied.
   [Valkyrie's Season 3 relic catalog](https://www.valkyrie.tips/database/relics?season=s3)
   independently corroborates three 80-relic pools. Its
   [Season 3 roadmap](https://www.valkyrie.tips/seasons/s3) supplies the +30/+60-day
   later-pool cadence; its absolute dates are for that site's server, not Charming
   Glance. The game data alone does not establish a player's pool-unlock date.

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

## Gallery and detail reference

The user-provided gallery screenshots (9224.png and 9225.png) guide the compact,
image-first, rarity-grouped cards. Region/pool tabs sit above the gallery. A Fruit zone dropdown consolidates
the numbered locations into the filter panel. Destiny Fruit Targets retains exact-zone groups. The detail dialog follows
9226.png: title/icon, effect, set members, set bonuses, then acquisition rows.
Set membership ownership is computed from this browser's saved collection; the
example account's stars, 35 shards, and 3/4 progress are not copied into user state.

`effect`, `set`, and `setBonuses` originate in the retained catalog unless an explicit
verification overrides them; Aethyris uses the November 8 game-data refresh above. Most catalog set bonuses provide stat names without
numeric magnitudes; those numbers are not guessed. Arcane Pagoda is a documented
conflict: the screenshot shows Crit RES 5%, whereas the export lists 6%. The visible
value follows the supplied in-game reference, with the catalog value retained in
`verification.catalogEffect`. Its screenshot lists Kingdom Gacha and Element Gacha;
the absence of an exploration row alone does not establish universal unavailability.

Twilight Teacup has a conflicting location (Prydwen: Cinder Ridge XIII; catalog: Verdantglade). Its exact zone and availability are null pending in-game confirmation; it is excluded from targets.

The September 23 location recheck covered Prydwen Duelist, Sorcerer, Archmage and tips, EOG Destiny Fruit guidance, and SXS Codex. No additional independently confirmed numbered zones were found; the Twilight Teacup conflict remains excluded.
