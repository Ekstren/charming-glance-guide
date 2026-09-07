from pathlib import Path

path = Path('index.html')
s = path.read_text(encoding='utf-8')


def replace_once(old: str, new: str, label: str) -> None:
    global s
    count = s.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly 1 match, found {count}')
    s = s.replace(old, new, 1)

# Keep the actual S2 scoring floor at 130. This is only the earliest level where
# the calculator has verified max-rank S2 Realm/open-map yields and can make a
# useful forward projection without inventing lower-rank economy values.
replace_once(
    "  const S2_PRIMO_META = Object.freeze({\n",
    "  const S2_PLANNER_START_LEVEL = 120;\n\n  const S2_PRIMO_META = Object.freeze({\n",
    'planner start constant',
)

# The max-achievable solver must be callable before Season Power itself unlocks.
replace_once(
    "    if(cfg.key==='s2' && currentCharacter.level<cfg.scoreFloor) return null;",
    "    if(cfg.key==='s2' && currentCharacter.level<S2_PLANNER_START_LEVEL) return null;",
    'max-achievable pre-score gate',
)

# Main calculator: pause only below 120, not below the 130 scoring baseline.
replace_once(
    "    if(cfg.key==='s2' && characterSnapshot(cfg).level<cfg.scoreFloor){ clearS2PreScoring(cfg); return; }",
    "    if(cfg.key==='s2' && characterSnapshot(cfg).level<S2_PLANNER_START_LEVEL){ clearS2PreScoring(cfg); return; }",
    'main pre-score gate',
)

# Reword the remaining hard lock (<120) so it describes the new behavior accurately.
replace_once(
    "    $('targetMessage').textContent=`Season Power scoring unlocks at Lv.${cfg.scoreFloor}. Current Lv.${current.level} is still in the pre-Season-Power catch-up phase, so the planner stays paused until Character Lv.${cfg.scoreFloor}. Once unlocked, enter your actual Gear/Skill/Relic/Fantomon levels; lagging slots are allowed and their future catch-up costs are counted.`;",
    "    $('targetMessage').textContent=`Season Power scoring still uses the Lv.${cfg.scoreFloor} baseline, but forward planning becomes available at Lv.${S2_PLANNER_START_LEVEL}. Current Lv.${current.level} is below that planning threshold, so the calculator stays paused until Lv.${S2_PLANNER_START_LEVEL}.`;",
    'locked message',
)
replace_once(
    "    $('optimizerSummary').textContent=`Return at Lv.${cfg.scoreFloor} and enter your actual scoring-start snapshot. The default S2 profile is Lv.130 / Gear 130 / Skills 130 / Fantomons 130 / Relics +13, so assumed progression contributes 0 Season Power.`;",
    "    $('optimizerSummary').textContent=`Return at Lv.${S2_PLANNER_START_LEVEL} and enter your actual state. From there the calculator projects EXP and resources through the Lv.${cfg.scoreFloor} Season Power baseline and season end.`;",
    'locked optimizer summary',
)

# Explain the pre-130 state in the normal, now-active calculator instead of pretending
# current below-floor progression is already Season Power.
old = """    $('currentBreakdownExplain').textContent=currentCharacter.decimal<cfg.scoreFloor
      ? `${cfg.name} Season Power begins at Lv.${cfg.scoreFloor}; Character progress below that floor contributes 0 Season Power points. Everything in this table is your current entered state.`
      : `Character is Lv.${currentCharacter.level} at ${(currentCharacter.pct*100).toFixed(1)}% EXP. ${cfg.name} awards 1 point per completed 1% above the Lv.${cfg.scoreFloor} floor, so this contributes ${fmt(currentParts.character)} points.`;"""
new = """    $('currentBreakdownExplain').textContent=currentCharacter.decimal<cfg.scoreFloor
      ? `${cfg.name} Season Power begins at Lv.${cfg.scoreFloor}; your current below-floor progression contributes 0 Season Power. The calculator is active because Lv.${S2_PLANNER_START_LEVEL}+ uses the verified max-rank S2 economy, so it can project your EXP, saved resources and future income through the scoring gate and show an attainable season-end Primostar result.`
      : `Character is Lv.${currentCharacter.level} at ${(currentCharacter.pct*100).toFixed(1)}% EXP. ${cfg.name} awards 1 point per completed 1% above the Lv.${cfg.scoreFloor} floor, so this contributes ${fmt(currentParts.character)} points.`;"""
replace_once(old, new, 'pre-score breakdown explanation')

# Formula/source text: separate planning availability from scoring eligibility.
replace_once(
    "<p><b>S2 Primostar calculator:</b> Season 2 is the active Charming Glance scoring profile. Season 1 is retained only where carry-forward history is required. QY's current timeline confirms Season Power at Player Lv.130; Lv.120 is only the maximum S2 Material Realm bracket. The calculator therefore starts planning only once Character Lv.130 unlocks Season Power. Progression already spent before that snapshot is outside the plan; however, any Gear/Skill/Fantomon/Relic slot that is still below its score floor at Lv.130 can be entered normally, scores zero until it crosses the floor, and keeps its real catch-up resource cost.",
    "<p><b>S2 Primostar calculator:</b> Season 2 is the active Charming Glance scoring profile. Season 1 is retained only where carry-forward history is required. <b>Planning now starts at Player Lv.120</b>, because that is the verified maximum S2 Material Realm/open-map economy bracket, while <b>Season Power scoring still starts at the Lv.130 baseline</b>. From Lv.120–129 the calculator projects Character EXP, saved resources, Cart/Shop/Realm income and legal future upgrades through Lv.130 and season end; it does not award any Season Power below the real scoring floors. Any Gear/Skill/Fantomon/Relic slot below its score floor can be entered normally, scores zero until it crosses the floor, and keeps its real catch-up resource cost.",
    'method planner description',
)
replace_once(
    "<p><b>S2 progression gates:</b> the prepared calculator surfaces Lv.106 T4 class, Lv.108 Adult Fantomon, Lv.116 Tower, Lv.120 maximum S2 Realm/open-map material bracket and Lv.130 Season Power scoring/second-dungeon milestone. These gates are informational; they do not override the calculator's conservative upgrade-cap logic.</p>",
    "<p><b>S2 progression gates:</b> the calculator surfaces Lv.106 T4 class, Lv.108 Adult Fantomon, Lv.116 Tower, <b>Lv.120 maximum S2 Realm/open-map material bracket and planner start</b>, and <b>Lv.130 Season Power scoring baseline / second-dungeon milestone</b>. Lv.130 is the scoring floor, not Lv.131: exactly-at-floor levels contribute 0 progression points, while progress above the floor scores normally. These gates do not override the calculator's conservative upgrade-cap logic.</p>",
    'method progression gates',
)

# Add a source-level invariant so future edits cannot silently collapse plannerStart into scoreFloor.
needle = "  validateS2ScoringStartDefaults();\n"
insert = """  validateS2ScoringStartDefaults();
  if(!(S2_PLANNER_START_LEVEL < CALC_SEASONS.s2.scoreFloor)){
    console.warn('S2_PLANNER_START_V1: planning start must remain below the Season Power score floor.',{plannerStart:S2_PLANNER_START_LEVEL,scoreFloor:CALC_SEASONS.s2.scoreFloor});
  }
"""
replace_once(needle, insert, 'planner/scoring invariant')

path.write_text(s, encoding='utf-8')
print('Patched S2 Primostar calculator: Lv120 planning start, Lv130 scoring floor preserved.')
