# Season 3 build refresh evidence

Checked November 8, 2026. Current Season 3 classes are Magister (Destroyer path), Prophet (Dominator path), Ravager (Conqueror path), and Templar (Guardian path).

## Author-published class guides

- [Prydwen: Magister](https://www.prydwen.gg/sword-x-staff/guides/build-guide-magister), guide updated September 1, 2026. Four bars: Wind AOE, ST, Fire AoE, and PVP. The published bars omit Rapid Cast; the guide recommends Pandarial for most use and explains its opening cooldown benefit. Formation Breaker remains important against high-DEF targets. The guide favors Elemental Mastery secondaries and new defensive / paired affixes.
- [Prydwen: Prophet](https://www.prydwen.gg/sword-x-staff/guides/build-guide-prophet), guide updated September 4, 2026. Direct Single Target, Pure Erosion Remastered Edition, Direct AoE, and Healing Build are transcribed as named source presets. The Erosion bar is intended for long fights; the direct bar requires investment in new T5 skills. Pandarial is the lead recommendation for both damage and healing; Prismora is discussed as a later-S3 specialist rather than an already-unlocked pet.
- [Prydwen: Ravager](https://www.prydwen.gg/sword-x-staff/guides/build-guide-ravager), guide updated September 4, 2026. Stages and Dungeons, Dragon, and PVP bars retain their published slot order. Source caveats cover survival Charm substitutions, Crit sufficiency, and moving Sunset Sword last if used. T5 main-secondary priorities are Elemental Mastery before ATK on offensive pieces.
- [Prydwen: Templar](https://www.prydwen.gg/sword-x-staff/guides/build-guide-templar), guide updated September 10, 2026. Generic Dungeon/4vs4 (explicitly assumes Pandarial), Water Templar, PvP Templar, and Light Templar are published bars. Main priorities include SPD on Sword/Boots and Block on Shield. S3 weapon Auto-protect and paired Block Rate + Block Efficiency are source-rated top affixes. Prismora is a later-S3 PvP option with a single-debuff cleanse limitation.

All bars retain four Techniques and four Charm entries. Prophet healing's fourth entry remains FLEX because the author supplies conditional choices, not one universal Charm. Notes paraphrase source caveats; the site does not create its own Crucible/Conquest/Mirage/Arena adaptations or add 2v2 tournament bars.

## Other authored player sources

[SxS Companion](https://www.sxscompanion.com/builds) publishes separate T5 directories:

- [Magister](https://www.sxscompanion.com/builds/t5/magister): Max Dps (Crucible, Rezaj) and Takin’ out the Trash (Mobs) (Split Mirage, Darkstorm).
- [Prophet](https://www.sxscompanion.com/builds/t5/prophet): Dungeon DPS (Rezaj), Arena / AOE Mob clear / Exploring / Boss fight (JustinPantheon), Support (Torrent), and Heal Overload (Keshi).
- [Ravager](https://www.sxscompanion.com/builds/t5/ravager): Map (SchlorKor).
- [Templar](https://www.sxscompanion.com/builds/t5/templar): Double Taunt Dungeon Panda (Rezaj), Generic Dungeon (Useless), Split Endless / Balanced Offense / Reflect (Torrent).

Directory names and activity labels were readable, but individual detail pages repeatedly timed out. The site links to the authors' directories rather than inventing missing slot lists. A listed 2v2 entry is not promoted on this site, consistent with the user's previous exclusion.

[Purrwikimania community loadouts](https://www.purrwikimania.com/loadouts) is an additional source-owned player-build browser with Tier 5 filtering. Its dynamic bars were not transcribed without a verified individual loadout.

## Preserved data and verification

- Existing Season 2 T4 presets, source links, and community notes remain in a collapsed previous-tier archive. They are not labeled as current S3 advice.
- Current gear, substats, roll-guide and Fantomon panels are retained for every class, with Tank/DPS for Templar and DPS/Heals for Prophet.
- All user-confirmed numeric Affix Preview values in `ROLL_VALUES` remain unchanged. They are labeled a recorded baseline; no unverified numeric S3 special-affix cap is invented.
- Prior selected-class settings migrate from the S2 class name to its T5 successor. Existing mode storage keys are retained.
- `node --check` passed for both source modules. A source-only esbuild/Playwright check at 320, 390 and 1280 pixels verified all 15 current cards, four entries per group, five gear slots, Fantomon rows, collapsed historical archive, old-class migration, mode switching, and no overflowing current cards or browser errors.
