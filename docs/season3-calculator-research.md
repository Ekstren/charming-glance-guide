# Season 3 calculator research

Checked November 8, 2026. These changes update numerical season facts in the existing planner; they do not copy another site's interface or optimizer.

## Sources

- [0xNobody multi-season planner](https://0xnobodyyt.github.io/sxs-primo-calculator/) and its [published source data](https://raw.githubusercontent.com/0xNobodyYT/0xNobodyYT.github.io/main/sxs-primo-calculator/index.html): Season 3 rule row, character and Fantomon EXP arrays, seasonal upgrade coefficients, Realm rank multipliers and object/damage probabilities. The fetched source is retained locally under `test-results/season3-research/index.html` for this update's review. Numeric EXP entries in our data module are decoded facts, not upstream executable code.
- [Purrwikimania Primostar planner](https://www.purrwikimania.com/primostars): independently corroborates score weights, floors, conversion, character-gated seasonal progression caps and Master III multiplier. Its published `PRIMO.pact` data supplies the 40 Season 3 thresholds.
- [Purrwikimania Material Realms and Relic Costs](https://www.purrwikimania.com/realms): corroborates normal relic ranks, Purple Sand conversion, the +13/+14/+15 catch-up costs and seasonal upgrade tables.

## Implemented facts

Season 3's score baseline is character/gear/skills/Fantomon level 160; relic scoring starts above +17. The normal relic upgrade baseline is +16, which is intentionally distinct from that scoring floor. Score weights are character 100, each gear 14, each skill 5, each Fantomon 6 and each relic 26, with 65 fixed Primostars and 13 score per additional Primostar.

The data module contains 150 exact character EXP requirements from level 160 (first 44,969,859; late plateau 114,649,996) and 180 Fantomon requirements from level 160 (first 177,320; last 583,380). Unsupported levels return Infinity instead of reusing an older season's curve.

Gear starts at 26,000 Ore, increases by 260 through the 150th seasonal increment, then plateaus; the supported maximum is 300 seasonal increments. Every fifth increment uses 540 Refined Ore. Skills start at 19,225 Essence, increase by 192.25 per seasonal increment, and support 180 increments. Both resource costs retain the established nearest-five rounding. Relics start at 2,300 Purple Sand, increase by 230 per increment, and support 18 increments above normal +16. Purple Sand is 25 Basic Sand equivalent. Fantomon costs divide the exact EXP requirement by 50 to express Basic Treat equivalents.

Planning caps follow the published Season 3 character gates: seasonal character levels 0/1/10/20/30/40/50/60/70/80 permit gear increments 0/20/40/60/80/100/120/140/160/300, skills and Fantomon 0/30/40/50/60/70/80/90/100/180, and relics 0/3/4/5/6/7/8/9/10/18 above normal +16. Actual entered levels remain accepted without clamping. Unverified pre-160 gear, skill and Fantomon upgrade costs remain unsupported; verified relic catch-up +13 to +16 is retained.

Realm Master III is available at character level 150 and uses multiplier 20. Our Realm yields were evaluated independently with a renewal/dynamic-programming expectation using the published damage outcomes (9/10/11 with probabilities .2/.4/.2; 14/15/16 each 1/15), object weights, break rewards and free-box facts. Average per tool: Ore 2,032.525409516654; Essence 2,826.2589137307145; Basic-equivalent Sand 1,937.4186678046894; Rolla 20,617.245605362954. These are expectations, not guaranteed individual drops. Purr's rounded Master III yield table differs slightly (2,048/2,848/1,954/20,790), so it is corroboration for rank and multiplier, not a claim of exact agreement with our independently evaluated expectation. Historical S1/S2 constants are unchanged.

## Conservative unknowns

- Open-map Stamina node yields default to zero and use only actual user-entered node yields; each known resource can be enabled independently; no Season 2 node yields are carried forward. Realm readiness is independent of map-yield readiness.
- No observed Season 3 shop sample is available, so shop projection returns zero rather than extrapolating the Season 2 sample.
- Forty verified Season 3 Astral Pact thresholds are exported separately. Their bonus types are not guessed, and the historical 80-node effect table remains unchanged.
- The February 25, 2027 end date is an editable estimate supplied by the shared season clock, not an asserted confirmed server deadline.
- Starter progression levels are examples of the season floor, not the user's actual progress. Carried Primostars start blank and must be entered by the user. Target 2,360 is a verified threshold, without an unverified bonus label.

## Validation

Both modules pass Node syntax checks. Numeric assertions cover exact EXP bounds, first/last upgrade costs, unsupported catch-up and cap boundaries, Refined Ore cadence, relic catch-up and seasonal costs, all-zero unknown shop projections, unknown/known map yields, independent Realm readiness, character gates, actual-input caps, and the separate 40-threshold/80-effect tables. Existing S2 model and zero-score starter-profile regression validators both pass. Integration, rendering and generated bundles are validated by the coordinating agent.
