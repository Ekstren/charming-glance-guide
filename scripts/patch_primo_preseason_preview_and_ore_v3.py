from pathlib import Path

path = Path('index.html')
s = path.read_text(encoding='utf-8')


def replace_once(old: str, new: str, label: str):
    global s
    if new in s:
        return
    if old not in s:
        raise SystemExit(f'Missing expected block for {label}')
    s = s.replace(old, new, 1)


replace_once(
    "  const S2_PLANNER_START_LEVEL = 120;\n",
    "  const S2_PLANNER_START_LEVEL = 120;\n  // PRESEASON_UNLOCK_PREVIEW_V3: Lv.120-130 can preview the first fully-seasonal\n  // upgrade state without awarding any fake pre-Lv.130 Season Power. The site's\n  // conservative S2 model treats Lv.131 as the first point where >130 Gear can be\n  // planned, so this is an upgrade-availability preview only, not a scoring-floor change.\n  const S2_FULL_SEASONAL_PREVIEW_LEVEL = 131;\n",
    'preview constant'
)

replace_once(
    "  function categoryInputCapsForCharacter(characterLevel,cfg=activeCalcConfig()){\n    const caps=categoryCapsForCharacter(characterLevel,cfg);\n    if(cfg.key!=='s2') return caps;\n    // Real late-S2 records exceed Character level for Skills and exceed +21 Relics. Accept actual values without\n    // pretending we know the exact future unlock schedule; only the optimizer's NEW upgrades stay conservative.\n    return {...caps,skill:Infinity,relic:Infinity,fanto:Infinity,gear:Infinity};\n  }\n",
    "  function categoryInputCapsForCharacter(characterLevel,cfg=activeCalcConfig()){\n    const caps=categoryCapsForCharacter(characterLevel,cfg);\n    if(cfg.key!=='s2') return caps;\n    // Real late-S2 records exceed Character level for Skills and exceed +21 Relics. Accept actual values without\n    // pretending we know the exact future unlock schedule; only the optimizer's NEW upgrades stay conservative.\n    return {...caps,skill:Infinity,relic:Infinity,fanto:Infinity,gear:Infinity};\n  }\n\n  function optimizerPlanningLevel(projectedLevel,cfg=activeCalcConfig()){\n    const projected=Math.max(1,Math.floor(Number(projectedLevel)||1));\n    if(cfg.key!=='s2') return projected;\n    const current=Math.max(1,Math.floor(Number(characterSnapshot(cfg).level)||1));\n    if(current>=S2_PLANNER_START_LEVEL && current<S2_FULL_SEASONAL_PREVIEW_LEVEL){\n      return Math.max(projected,S2_FULL_SEASONAL_PREVIEW_LEVEL);\n    }\n    return projected;\n  }\n  function optimizerCategoryCaps(p,cfg=activeCalcConfig()){\n    const projectedLevel=p?.upgradeCapLevel ?? p?.level ?? 1;\n    return categoryCapsForCharacter(optimizerPlanningLevel(projectedLevel,cfg),cfg);\n  }\n",
    'preview cap helpers'
)

old_caps = "    const projectedCaps=categoryCapsForCharacter(p.upgradeCapLevel??p.level,cfg);"
count = s.count(old_caps)
if count not in (0, 2):
    raise SystemExit(f'Expected 2 projected-cap sites, found {count}')
if count == 2:
    s = s.replace(old_caps, "    const projectedCaps=optimizerCategoryCaps(p,cfg);")

replace_once(
    "      $('seasonRulesHint').innerHTML='<b>S2 scoring mode starts at Lv.130:</b> +45 fixed · 27 score / Primostar · normal floor Lv.130 / Relics above +13 · weights Character 100, Gear 18, Skill 7, Relic 33, Fantomon 8. <b>Lv.120</b> is only the max S2 Material Realm/open-map bracket. Starter profile: Lv.130 · Gear 130 · Skills 130 · Fantomons 130 · Relics +13; carried stars/resources should be replaced with your actual snapshot.';",
    "      $('seasonRulesHint').innerHTML='<b>S2 scoring still starts at Lv.130:</b> +45 fixed · 27 score / Primostar · normal floor Lv.130 / Relics above +13 · weights Character 100, Gear 18, Skill 7, Relic 33, Fantomon 8. <b>Lv.120+</b> can use the planner now; while you are Lv.120–130 it runs a clearly labeled <b>Lv.131 unlock preview</b> for upgrade availability so stockpiled resources can be evaluated before full seasonal progression opens. No pre-130 Character score is awarded. Starter floor: Gear 130 · Skills 130 · Fantomons 130 · Relics +13.';",
    'season rules hint'
)

replace_once(
    "      ? `${cfg.name} Season Power begins at Lv.${cfg.scoreFloor}; your current below-floor progression contributes 0 Season Power. The calculator is active because Lv.${S2_PLANNER_START_LEVEL}+ uses the verified max-rank S2 economy, so it can project your EXP, saved resources and future income through the scoring gate and show an attainable season-end Primostar result.`",
    "      ? `${cfg.name} Season Power begins at Lv.${cfg.scoreFloor}; your current below-floor progression contributes 0 Season Power. Because you are Lv.${S2_PLANNER_START_LEVEL}+, the optimizer uses a Lv.${optimizerPlanningLevel(p.upgradeCapLevel??p.level,cfg)} full-seasonal unlock preview for upgrade availability while keeping Character score tied to your real projection. This lets stockpiled resources produce a useful Primostar estimate before the live scoring gate opens.`",
    'preseason breakdown explanation'
)

replace_once(
    "    const lockedText=gearLocked?' Gear is locked at the five current levels.':'';\n    const capText=cfg.key==='s1'?` S1 safe-upgrade cap uses projected Lv.${p.upgradeCapLevel??p.level} at season reset: Skills ${projectedCaps.skill}, Fantomons ${projectedCaps.fanto} (next 10-level band), Relics +${projectedCaps.relic}; Gear is not Character-level capped.`:` S2 score model: floor Lv.130 / Relics above +13, +45 fixed Primostars, 27 score per Primostar, weights Character 100 / Gear 18 / Skill 7 / Relic 33 / Fantomon 8. Max Realm bracket is Lv.120; Global live values are still spot-checked at rollover before changing the model.`;",
    "    const lockedText=gearLocked?' Gear is locked at the five current levels.':'';\n    const previewText=cfg.key==='s2'&&currentCharacter.level<S2_FULL_SEASONAL_PREVIEW_LEVEL\n      ? ` Pre-season preview uses Lv.${optimizerPlanningLevel(p.upgradeCapLevel??p.level,cfg)} upgrade availability; Character score still uses the real projected level.`\n      : '';\n    const capText=cfg.key==='s1'?` S1 safe-upgrade cap uses projected Lv.${p.upgradeCapLevel??p.level} at season reset: Skills ${projectedCaps.skill}, Fantomons ${projectedCaps.fanto} (next 10-level band), Relics +${projectedCaps.relic}; Gear is not Character-level capped.`:` S2 score model: floor Lv.130 / Relics above +13, +45 fixed Primostars, 27 score per Primostar, weights Character 100 / Gear 18 / Skill 7 / Relic 33 / Fantomon 8. Max Realm bracket is Lv.120.${previewText}`;",
    'result preview note'
)

replace_once(
    "      if($('resultEyebrow')) $('resultEyebrow').textContent='Requested target';\n      if(recommendedSection) recommendedSection.hidden=true;",
    "      if($('resultEyebrow')) $('resultEyebrow').textContent='Requested target';\n      $('currentStars').textContent=fmt(targetStars);\n      if(recommendedSection) recommendedSection.hidden=true;",
    'requested target headline'
)

replace_once(
    "      setBalance('oreBalance',0,resources.ore,resources.yields.orePerHammer,'Hammers');\n      setEssenceBalance('essenceBalance',0,resources);\n      setSandBalance('sandBalance',0,resources);\n      setTreatBalance('treatBalance',0,resources);",
    "      setRawRemaining('oreBalance',0,resources.ore);\n      setEssenceBalance('essenceBalance',0,resources);\n      setSandBalance('sandBalance',0,resources);\n      setTreatBalance('treatBalance',0,resources);\n      ['oreToolBalance','essenceToolBalance','sandToolBalance'].forEach(hidePlanBalance);",
    'no-plan resource cards'
)

for old, new, label in [
    ('<small id="oreToolBalance" class="toolBalance">—</small>', '<small id="oreToolBalance" class="toolBalance" hidden>—</small>', 'ore tool initial hidden'),
    ('<small id="essenceToolBalance" class="toolBalance">—</small>', '<small id="essenceToolBalance" class="toolBalance" hidden>—</small>', 'essence tool initial hidden'),
    ('<small id="sandToolBalance" class="toolBalance">—</small>', '<small id="sandToolBalance" class="toolBalance" hidden>—</small>', 'sand tool initial hidden'),
]:
    replace_once(old, new, label)

replace_once(
    "<p><b>S2 Primostar calculator:</b> Season 2 is the active Charming Glance scoring profile. Season 1 is retained only where carry-forward history is required. <b>Planning now starts at Player Lv.120</b>, because that is the verified maximum S2 Material Realm/open-map economy bracket, while <b>Season Power scoring still starts at the Lv.130 baseline</b>. From Lv.120–129 the calculator projects Character EXP, saved resources, Cart/Shop/Realm income and legal future upgrades through Lv.130 and season end; it does not award any Season Power below the real scoring floors. Any Gear/Skill/Fantomon/Relic slot below its score floor can be entered normally, scores zero until it crosses the floor, and keeps its real catch-up resource cost.",
    "<p><b>S2 Primostar calculator:</b> Season 2 is the active Charming Glance scoring profile. Season 1 is retained only where carry-forward history is required. <b>Planning now starts at Player Lv.120</b>, because that is the verified maximum S2 Material Realm/open-map economy bracket, while <b>Season Power scoring still starts at the Lv.130 baseline</b>. From Lv.120–130 the calculator can run a <b>Lv.131 full-seasonal unlock preview</b> for upgrade availability, allowing stockpiled resources to be evaluated before the live gate opens; this preview does not award fake Character score below Lv.130. Any Gear/Skill/Fantomon/Relic slot below its score floor can be entered normally, scores zero until it crosses the floor, and keeps its real catch-up resource cost.",
    'method explanation'
)

replace_once(
    "<p><b>S2 progression gates:</b> the calculator surfaces Lv.106 T4 class, Lv.108 Adult Fantomon, Lv.116 Tower, <b>Lv.120 maximum S2 Realm/open-map material bracket and planner start</b>, and <b>Lv.130 Season Power scoring baseline / second-dungeon milestone</b>. Lv.130 is the scoring floor, not Lv.131: exactly-at-floor levels contribute 0 progression points, while progress above the floor scores normally. These gates do not override the calculator's conservative upgrade-cap logic.</p>",
    "<p><b>S2 progression gates:</b> the calculator surfaces Lv.106 T4 class, Lv.108 Adult Fantomon, Lv.116 Tower, <b>Lv.120 maximum S2 Realm/open-map material bracket and planner start</b>, <b>Lv.130 Season Power scoring baseline / second-dungeon milestone</b>, and a <b>Lv.131 full-seasonal unlock preview</b> used only for pre-gate planning. Lv.130 remains the actual scoring floor: exactly-at-floor levels contribute 0 progression points, while progress above the floor scores normally.</p>",
    'progression gates explanation'
)

path.write_text(s, encoding='utf-8')
print('patched pre-season Primostar preview, target labeling, and Ore/resource-card edge cases')
