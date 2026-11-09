# Season 3 Companion evidence

Checked November 8, 2026. Scope: Companions page only. No new server-specific unlock day, dispatch duration, or success percentage is assumed.

## Sources and method

- [0xNobody's current Companion archive](https://0xnobodyyt.github.io/sxs-companions/) and its [authored client-data payload](https://0xnobodyyt.github.io/sxs-companions/data.js): live payload fetched during this update; the complete source SHA-256 is recorded in `data/season3-companions.json`. Only factual fields for the seven Aethyris companions and five established Loong Haven companions are retained locally. The page declares percentage values cumulative and explains that a companion's native combat class is not an account-bonus restriction.
- [Purrwikimania NPC friendship catalog](https://www.purrwikimania.com/npcs): independent authored roster/gift/stat cross-check. It groups seven companions in Aethyris and lists favorite gifts, journal requirements, and cumulative level-100 specialties. Its “Practical gifts” and “Precious gifts” labels correspond to the upstream payload's Furniture and Jewelry categories.
- [Prydwen Companion basics](https://www.prydwen.gg/sword-x-staff/guides/beginner-guide): affinity affects permanent account stats, investment should follow relevant breakpoints and desired stats, and gold outlines are a tie-breaker for passive stat value.
- [Prydwen Magister guide](https://www.prydwen.gg/sword-x-staff/guides/build-guide-magister) and [Templar guide](https://www.prydwen.gg/sword-x-staff/guides/build-guide-templar): corroborate continued Crit/Accuracy offensive relevance and Block-focused tank play in T5. The Companion priority ladders remain editorial guidance inherited from the existing permanent-stat paths, not newly invented activity builds.
- [WishGM's Season 3 feature overview](https://www.wishgm.com/en-US/blog/sword-x-staff/sword-staff-season-3-update): secondary source for the Bond Odyssey/Vista Dispatch and Stone Symphony companion-expedition systems. The page only summarizes checking displayed challenge/role requirements and collecting resources/souvenirs; example power, six-hour timer, and bonus percentages are deliberately not promoted into universal rules.

## Verified Aethyris roster

All are World catalog records marked Global client. Journals below are the companion's own unlock journals, from each record's unlock label.

| Companion | Native class | Favorite gifts | Journals to meet | Specialty at affinity 50 / 100 | Damage bonus at 20 / 70 |
|---|---|---|---|---|---|
| Freya | Duelist, gold | Practical gifts | 3 | Crit Rate +1% / +2% | DMG Boost +1% / +2% |
| Sylvia | Sorcerer, gold | Precious gifts | 3 | Crit Rate +1% / +2% | DMG Boost +1% / +2% |
| Ophelia | Sorcerer | Books | 1 | Accuracy +1% / +2% | DMG Boost +1% / +2% |
| Vigard | Knight, gold | Books | 3 | Block Rate +1% / +2% | DMG RES +1% / +2% |
| Gerald | Knight | Practical gifts | 1 | Block Rate +1% / +2% | DMG RES +1% / +2% |
| Astrid | Sage | Flowers | 1 | Crit RES +1% / +2% | DMG RES +1% / +2% |
| Isla | Sage | Flowers | 1 | Crit RES +1% / +2% | DMG RES +1% / +2% |

Pairs are cumulative totals at those affinity levels, not an additional +2% on top of +1%. Astrid and Isla have HP +19% at affinity 100 but **no Healing Boost** in their current curves. The existing guide wrongly placed them among Sage-native offensive candidates; the update explicitly places them in defensive/survival guidance.

Loong Haven carryover retains Ming (Crit), Wuji (Crit), Jiangwang (Accuracy), Hui (Block), and Suimo (Crit RES / Healing Boost at 100). Aqua/Suimo/Suzu remain the existing healer targets; none of the seven Aethyris records replaces them as a Healing Boost target. The source's TW/future Loong variants are excluded because their presence in the payload does not establish current Charming Glance availability.

## Implementation and verification

- `src/companions.mjs` now contains the previously legacy-asset-backed renderer and exports an idempotent initializer. The legacy `assets/companions.js` is not edited or loaded by the new source.
- Current class tabs: Magister, Prophet, Ravager, Templar. A saved T4 class migrates to its T5 counterpart; existing DPS/Heals preference is retained for Prophet.
- The compact Aethyris reference and Loong Haven carryover use local structured facts. Expanded details provide gifts, journal requirements, and exact specialty milestones without overwhelming the main guide.
- An isolated esbuild bundle injected into Playwright passed at 320, 390, and 1200 pixels: all four T5 tabs, Prophet Heals, reference availability, no page overflow, and no browser errors. This check did not rewrite shared generated assets.

## Timeline and shell follow-up

The current shell now names Season 3 / Aethyris while keeping the maintained November 5 / Server Day 114 anchor and later unlock dates as projections. Content availability on older Global servers does not establish Charming Glance's dates. Historical Season 2 entries remain in place. The local Discord mirror is stale through October 24; its disabled workflow was not enabled or represented as a fresh check.

- [Purrwiki area-unlock data](https://www.purrwikimania.com/area-unlocks), checked November 8: Aethyris has 16 item-gated blockers requiring 5 Gateway Keys, 2 Magic Drills, 2 Water Mines, 2 Cloud Jades and 5 Purifying Hammers. Remaining blockers have other gates. This resolves the old untranslated cloud-key / hammer placeholders without changing the quantities.
- [Valkyrie's authored Global localization changelog](https://www.valkyrie.tips/changelog?c=fix), October 1: the in-game Season 3 map is **Cosmic Voyage**, replacing the older Astral Odyssey label. Independently, [Purrwiki cosmetics](https://www.purrwikimania.com/cosmetics) lists the Haven Among Stars title for 80% Cosmic Voyage exploration. The existing Day-128 map date remains projected.
- The stored [official Court of Purification preview](https://discord.com/channels/1410146553573802088/1427172679521407056/1560523971177218138) verifies that dungeon's English name and Soulbinder Set, not the maintained Charming Glance December 16 projection. Fixed the shell summary's mismatched “Courtyard” name so the existing correct row receives its summary.
- [LDShop's Season 3 overview](https://www.ldshop.gg/blog/sword-x-staff/sword-staff-season-3-update.html) and [WishGM's overview](https://www.wishgm.com/en-US/blog/sword-x-staff/sword-staff-season-3-update) support Bond Odyssey / Vista Dispatch and Stone Symphony, companion expedition requirements and souvenir rewards. The guide deliberately avoids making the screenshots' individual power, duration or success rates universal requirements.
- The all-seven-companion timeline row uses the same researched roster as the Companion section. The new Season 3 checklist is generic progression guidance, not an official launch notice or a newly invented Bed EXP strategy.
- Recurring 4v4 dates continue the existing observed Sunday fortnightly cadence after October 25 and are explicitly stored as unconfirmed projections. No 2v2 tournament was introduced.
