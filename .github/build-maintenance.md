# Build & Fantomon maintenance policy

## Charming Glance season handoff

- **Before Season 2 is live on Charming Glance:** maintain both Season 1 / Tier 3 and Season 2 / Tier 4 build and Combat Fantomon recommendations.
- **Once Season 2 is live on Charming Glance:** stop ongoing Season 1 / Tier 3 build and Fantomon maintenance. Keep the existing S1/T3 builds as a legacy snapshot unless there is a site-breaking issue.
- After the handoff, active build maintenance is **Season 2 / Tier 4 only:** Conqueror, Guardian, Destroyer, and Dominator.

## Build format

- **Do not force every class into Solo / Dungeon / Boss / PvP cards.** Show only materially distinct loadouts supported by current guides, skill mechanics, or repeated community testing.
- If one general build is best for multiple activities, keep one card and explain useful swaps instead of duplicating artificial mode cards.
- Each loadout must show exactly 4 Techniques and 4 Charms actually equipped, plus concise swaps/conditions where useful.
- **Build-card notes must read as standalone player guidance.** Describe why the equipped loadout works and give only useful optional swaps; do not narrate a previous version of the build (for example, “drop X,” “use Y instead,” “this card,” or other change-log/editorial commentary).
- **Investment recommendations must come from Techniques/Charms actually equipped in the displayed loadouts.** Do not rank wishlist, swap-only, or unrelated pieces as core investments. If an item is only a situational swap, keep it in the build note instead of the ranked investment panel.
- **Desktop investment layout is fixed:** Technique investment on the **left**, Charm investment on the **right**. On phone widths these two panels may stack vertically, Technique first then Charm.
- **Keep the compact stat-priority panel:** show the priority for each individual gear slot, then show the complete prioritized substat line underneath. Do not replace this with generic grouped cards such as “Main lines / Best substats / Gem plan.”
- Arcanist and Dominator keep one **DPS / Heals** selector. DPS/Heals filters only the role-specific PvE cards; **Arena and Tournament stay visible in both modes**. Switching roles must not destroy/recreate build data or remove Fantomon recommendations.
- **Dominator's DPS / Heals selector stays inline directly beside the “Dominator” class title** in the guide-summary header; do not move it back into a separate full-width row above the summary.
- Prefer reputable build-guide presets when available and cross-check major recommendations against another credible source/community consensus when possible.
- Avoid weaker novelty builds, including Destroyer's Water/Frozen branch, merely to increase card count.


## Public build copy

- Build notes are player-facing. Describe what to equip, why it works, and when to swap it.
- Avoid implementation/editorial language in visible copy such as “this card,” “shell,” “mode/toggle,” “published core,” or “synthesis” when a direct gameplay description works better.
- When comparing alternatives, name the actual activity or setup (for example “Tank setup” or “boss support”) rather than referring to UI controls or hidden build variants.
- Source/evidence labels may identify a guide or testing basis, but should still read naturally to a player.

## Current intended loadout structure

- **Berserker (S1/T3):** Generic PvE, Dragon, Arena, Tournament.
- **Paladin (S1/T3):** Dungeon Tank, Water Offensive, Boss DPS / Off-Tank, Arena, Tournament.
- **Archmage (S1/T3):** AoE, Single Target, Arena, Tournament.
- **Arcanist (S1/T3):** AoE DPS, Single Target DPS, Healing, Arena, Tournament.
- **Conqueror (S2/T4):** All-Content, Dragon, Arena, Tournament.
- **Guardian (S2/T4):** Dungeon Tank, Water Offensive, Support / Boss, Arena, Tournament.
- **Destroyer (S2/T4):** AoE, Single Target, Fire AoE, Arena, Tournament.
- **Dominator (S2/T4):** AoE DPS, Single Target DPS, Healing, Arena, Tournament.

Change the PvE structure only when credible current evidence supports a real meta change. **Arena and Tournament are deliberate always-visible reference cards for every class** and are maintained separately from the PvE card-count rule.

## Runtime ownership

- `ROLE_PRESETS` owns the displayed loadout data, including the maintained Arena/Tournament references. Do not overwrite it with an older reduced card set.
- The Builds presentation layer owns the compact per-slot stat table, complete substat priority, Technique-left/Charm-right investment pair, and Main+Alt Fantomon display. These are product requirements, not optional polish.
- Dominator has one DPS/Heals role control. Layout-polish code may update presentation, but must not create a second role toggle or independently destroy loadout cards.
- Build observers should watch the `#buildContent` replacement boundary or child-list changes needed for an enhancer; **do not observe broad Builds subtree attributes or an enhancer's own class/hidden writes**, which can cause redundant render loops.
- Current Realm-tool result markup uses `toolSimpleLine`. Do not revive retired `toolUsedLine`, `toolUsageRow`, or `toolCompactLine` CSS generations.

## Combat Fantomon format

- Show exactly **Main + Alt** Combat Fantomon recommendations for each displayed loadout when two credible choices are available.
- **Main** is the strongest loadout-appropriate consensus choice. **Alt** is the best practical alternative for a different constraint such as survivability, utility, availability, or account stats.
- Add a short reason under both Fantomons explaining why each fits that specific loadout.
- Do not show ranked #3/#4 choices in the default build UI.
- In **Season 1 / Tier 3**, evaluate Fantomons only from the pre-Materialization Assist kit; give zero recommendation credit for later Battle skills.
- In **Season 2 / Tier 4**, Materialization effects may be considered only once actually available for Charming Glance.

## Pandarial trigger

Pandarial releases later in Season 2. When it becomes available for Charming Glance, re-evaluate every S2/T4 **Main + Alt** Combat Fantomon pair rather than assuming pre-release recommendations remain correct.

Do not list Pandarial as currently usable before it is actually available on Charming Glance. Remove future-release wording once it becomes obtainable.

## Evidence standard

Do not replace a working build from a single unsupported post. Prefer official skill text, reputable databases/guides, repeatable mechanics, or repeated community testing/consensus. Preliminary recommendations should be labeled as such instead of presented as settled meta.
