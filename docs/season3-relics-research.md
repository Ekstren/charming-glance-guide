# Season 3 relic refresh — 2026-11-08

## Verified changes

The existing catalog already contained 240 hidden Aethyris relics. All 240 IDs,
English names, rarity tiers, elements, and set-member identities match the current
public game-config extraction. No ownership IDs, local icon paths, or earlier
region records changed.

Three pools contain 80 relics apiece: 20 Mythic, 20 Legendary, 20 Epic, 20 Rare.
Each pool is now browsable. Aethyris I is the initial filter. Later pools retain
S3 Day 31/61 markers until their unlock resets; the calculation uses the shared
S2_END/S3-start anchor and Pacific reset helpers.

The extraction identifies 54 Aethyris I relics in exact Destiny Exploration areas
Aethyris I through XVIII: three targets per area. Missing exploration entries were
left unknown. The refresh adds both listed gacha routes, 60 English set names,
fixed numeric set bonuses, and base +1/zero-star/unequipped effects and affinity
stats. The detail dialog explicitly labels this baseline. Percent game values
use hundredths of one percentage point; for example, raw 120 is 1.2%.

## Sources

- https://kakotheris.neocities.org/relics — authored extractor, explains values
  are the game's English strings/config rather than fitted estimates.
- https://kakotheris.neocities.org/relic_data.js — game package 130_156581.
  Retrieved SHA-256: 13d3ccfe29160b2e83e938be1693d33c548d42410e892ec84ac0a12ecc271e3b.
  Source code/schema is AGPL; only underlying item facts were normalized into
  the pre-existing local schema. No source tool code was vendored.
- https://www.valkyrie.tips/database/relics?season=s3 — independently lists
  240 Aethyris relics across three 80-item pools, with alternate localization.
- https://www.valkyrie.tips/seasons/s3 — later pools at +30/+60 days from its
  server's S3 start. Absolute dates differ by server and were not copied.
- https://www.purrwikimania.com/relics — independent game-data reference
  explains level, star, equipped-slot scaling and the difference between pool
  acquisition and targeted exploration. Cross-check only; no UI/code copied.

## Limits

The whole catalog remains 1,130 entries: 640 visible and 490 retained hidden.
Newer regions and additional current-global event relics were not blindly imported
because their availability on Charming Glance was not established. Historical
user-verified S1/S2 effects and conflicts (including Arcane Pagoda) remain intact.
The visible local count describes the maintained through-S3 catalog, not every
current global item.

The offline Loot & Waifus import script still preserves curated records, pool
membership, acquisitions, and stable IDs. Its older live API endpoint currently
returns 404; do not treat that as a verified live refresh source.
