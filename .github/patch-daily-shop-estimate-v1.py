from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')
marker = 'DAILY_SHOP_ESTIMATE_V1'
if marker in text:
    print('already applied')
    raise SystemExit(0)

# 1) Add a separate Daily Shop planning control beneath the resource cards.
old_ui = '''          </div>\n          <div class="realmInventory">\n            <div class="realmInventoryTop"><strong>Material Realm plan</strong><small>Saved tools + daily purchases</small></div>'''
new_ui = '''          </div>\n          <!-- DAILY_SHOP_ESTIMATE_V1 -->\n          <div class="realmDailyPlanRow shopEstimateRow">\n            <div class="realmDailyCustom">\n              <span class="realmDailyTitle">Daily Shop material estimate <small>S2 planning estimate · material rolls only</small></span>\n              <div class="realmDailyInputs">\n                <label>Shop refreshes / day<input id="shopRefreshesDaily" type="number" min="0" max="20" step="1" value="0"><small>Default S2 plan: 3/day</small></label>\n              </div>\n            </div>\n            <div class="realmPlanSummary"><span>Estimated gain</span><b id="shopRefreshEstimate">—</b><small id="shopRefreshEstimateNote">~700 Ore · 900 Essence · 600 Sand · 50 Basic Treats per refresh</small></div>\n          </div>\n          <div class="realmInventory">\n            <div class="realmInventoryTop"><strong>Material Realm plan</strong><small>Saved tools + daily purchases</small></div>'''
if old_ui not in text:
    raise SystemExit('resource card / realm inventory anchor not found')
text = text.replace(old_ui, new_ui, 1)

# 2) Make 3/day the conservative S2 default while leaving normal/S1 HTML default at zero.
old_defaults = '''    sandCurrent:0,sandBlueCurrent:0,sandRate:800,\n    treatCurrent:0,treatPremiumCurrent:0,treatDeluxeCurrent:0,treatRate:80,\n    hammerCurrent:0,knucklesCurrent:0,shovelCurrent:0,'''
new_defaults = '''    sandCurrent:0,sandBlueCurrent:0,sandRate:800,\n    treatCurrent:0,treatPremiumCurrent:0,treatDeluxeCurrent:0,treatRate:80,\n    shopRefreshesDaily:3,\n    hammerCurrent:0,knucklesCurrent:0,shovelCurrent:0,'''
if old_defaults not in text:
    raise SystemExit('S2 rate defaults anchor not found')
text = text.replace(old_defaults, new_defaults, 1)

# 3) Persist the new field.
old_inputs = '''    ...GEAR_IDS,'oreCurrent','oreRate','essenceCurrent','essenceRate','sandCurrent','sandBlueCurrent','sandRate','treatCurrent','treatPremiumCurrent','treatDeluxeCurrent','treatRate',\n    'hammerCurrent','knucklesCurrent','shovelCurrent','staminaMode','realmDailyOre','realmDailyEssence','realmDailySand','refinedOreCurrent','exactSkillLevels','exactRelicLevels','exactFantoLevels'\n  ];'''
new_inputs = '''    ...GEAR_IDS,'oreCurrent','oreRate','essenceCurrent','essenceRate','sandCurrent','sandBlueCurrent','sandRate','treatCurrent','treatPremiumCurrent','treatDeluxeCurrent','treatRate','shopRefreshesDaily',\n    'hammerCurrent','knucklesCurrent','shovelCurrent','staminaMode','realmDailyOre','realmDailyEssence','realmDailySand','refinedOreCurrent','exactSkillLevels','exactRelicLevels','exactFantoLevels'\n  ];'''
if old_inputs not in text:
    raise SystemExit('INPUT_IDS anchor not found')
text = text.replace(old_inputs, new_inputs, 1)

# 4) Add the explicit estimate model. It counts only future server resets, not the current day,
# so manually-entered current inventories are not silently double-counted.
old_treat_fn = '''  function savedTreatEquivalent(){\n    return Math.max(0,n('treatCurrent')) + Math.max(0,n('treatPremiumCurrent'))*TREAT_PREMIUM_EQ + Math.max(0,n('treatDeluxeCurrent'))*TREAT_DELUXE_EQ;\n  }\n  function applyS2ScoringStartDefaults(){'''
new_treat_fn = '''  function savedTreatEquivalent(){\n    return Math.max(0,n('treatCurrent')) + Math.max(0,n('treatPremiumCurrent'))*TREAT_PREMIUM_EQ + Math.max(0,n('treatDeluxeCurrent'))*TREAT_DELUXE_EQ;\n  }\n\n  // DAILY_SHOP_ESTIMATE_V1\n  // Planning-only EV until a trustworthy shop slot/drop-rate table is available.\n  // The estimate intentionally excludes the current server day so a user's live Saved\n  // inventory can represent anything already bought today without being double-counted.\n  const DAILY_SHOP_MATS_PER_REFRESH=Object.freeze({ore:700,essence:900,sand:600,treat:50});\n  function dailyShopMaterialEstimate(cfg=activeCalcConfig()){\n    const active=cfg.key==='s2';\n    const refreshes=active?clamp(Math.floor(n('shopRefreshesDaily',0)),0,20):0;\n    const days=active?Math.max(0,countFuturePacificResets(Date.now(),cfg.end.getTime())):0;\n    const perDay=Object.fromEntries(Object.entries(DAILY_SHOP_MATS_PER_REFRESH).map(([k,v])=>[k,v*refreshes]));\n    const total=Object.fromEntries(Object.entries(perDay).map(([k,v])=>[k,v*days]));\n    return {active,refreshes,days,perRefresh:DAILY_SHOP_MATS_PER_REFRESH,perDay,total};\n  }\n\n  function applyS2ScoringStartDefaults(){'''
if old_treat_fn not in text:
    raise SystemExit('savedTreatEquivalent anchor not found')
text = text.replace(old_treat_fn, new_treat_fn, 1)

# 5) Add future shop gains to the actual projected resource budget.
old_projection_head = '''    const staminaUnused=staminaSpendable-staminaNodes*yields.staminaPerNode;\n    const cartOre=Math.max(0,n('oreRate'))*resourceHours;\n    const refinedRaw=$('refinedOreCurrent')?.value?.trim?.() ?? '';'''
new_projection_head = '''    const staminaUnused=staminaSpendable-staminaNodes*yields.staminaPerNode;\n    const cartOre=Math.max(0,n('oreRate'))*resourceHours;\n    const shopEstimate=dailyShopMaterialEstimate(cfg);\n    const refinedRaw=$('refinedOreCurrent')?.value?.trim?.() ?? '';'''
if old_projection_head not in text:
    raise SystemExit('projectedResources head anchor not found')
text = text.replace(old_projection_head, new_projection_head, 1)

old_projection_return = '''      yields,cartOre,\n      ore:Math.max(0,n('oreCurrent'))+cartOre,\n      essence:Math.max(0,n('essenceCurrent'))+Math.max(0,n('essenceRate'))*resourceHours,\n      sand:savedSandEquivalent()+Math.max(0,n('sandRate'))*resourceHours,\n      treat:savedTreatEquivalent()+Math.max(0,n('treatRate'))*resourceHours,\n      refinedTracked,refined,'''
new_projection_return = '''      yields,cartOre,shopEstimate,\n      ore:Math.max(0,n('oreCurrent'))+cartOre+shopEstimate.total.ore,\n      essence:Math.max(0,n('essenceCurrent'))+Math.max(0,n('essenceRate'))*resourceHours+shopEstimate.total.essence,\n      sand:savedSandEquivalent()+Math.max(0,n('sandRate'))*resourceHours+shopEstimate.total.sand,\n      treat:savedTreatEquivalent()+Math.max(0,n('treatRate'))*resourceHours+shopEstimate.total.treat,\n      refinedTracked,refined,'''
if old_projection_return not in text:
    raise SystemExit('projectedResources return anchor not found')
text = text.replace(old_projection_return, new_projection_return, 1)

# 6) Render the estimate separately so it is obvious these gains are not Cart production.
old_render = '''    const displayedTreats=Number(resources.treat)||0;\n    $('treatProjected').textContent=`Projected: ${fmtCompact(displayedTreats)} basic-eq.`;\n\n\n\n    $('currentStars').textContent=fmt(baselineStars);'''
new_render = '''    const displayedTreats=Number(resources.treat)||0;\n    $('treatProjected').textContent=`Projected: ${fmtCompact(displayedTreats)} basic-eq.`;\n    if($('shopRefreshEstimate')){\n      const shop=resources.shopEstimate||dailyShopMaterialEstimate(cfg);\n      $('shopRefreshEstimate').textContent=shop.refreshes\n        ? `+${fmtCompact(shop.perDay.ore)} Ore · +${fmtCompact(shop.perDay.essence)} Essence · +${fmtCompact(shop.perDay.sand)} Sand · +${fmtCompact(shop.perDay.treat)} Treats / day`\n        : 'Off';\n      if($('shopRefreshEstimateNote')){\n        $('shopRefreshEstimateNote').textContent=cfg.key==='s2'\n          ? (shop.refreshes?`${shop.days} future reset day${shop.days===1?'':'s'} counted · current day excluded to avoid double-counting live Saved mats`:'Set refreshes/day to include estimated Daily Shop materials in the projection.')\n          : 'S2-only estimate · default becomes 3 refreshes/day after rollover.';\n      }\n    }\n\n\n\n    $('currentStars').textContent=fmt(baselineStars);'''
if old_render not in text:
    raise SystemExit('resource projection render anchor not found')
text = text.replace(old_render, new_render, 1)

# 7) Document the assumption prominently in the method/source panel.
old_method = '''<p><b>S2 open-map Ore:</b> the planner budgets the conservative base value of <b>1,400 Ore per 5-Stamina node</b>. QY's empirical large-mine rate is 9.32% and large nodes pay 2×, which gives a long-run expected value of about <b>1,530 Ore/node</b>; that bonus is displayed as reference but is not silently counted in the resource budget.</p>'''
new_method = '''<p><b>S2 open-map Ore:</b> the planner budgets the conservative base value of <b>1,400 Ore per 5-Stamina node</b>. QY's empirical large-mine rate is 9.32% and large nodes pay 2×, which gives a long-run expected value of about <b>1,530 Ore/node</b>; that bonus is displayed as reference but is not silently counted in the resource budget.</p>\n<p><b>S2 Daily Shop estimate:</b> until a trustworthy shop slot/drop-rate table is available, the optional shop planner uses a deliberately simple material-only estimate of <b>~700 Ore, ~900 Skill Essence, ~600 Chrono Sand and ~50 Basic Treats per refresh</b>. The S2 default is 3 refreshes/day. Only future server-reset days are projected; the current day is excluded so materials already represented in the Saved fields are not double-counted. This does not value non-material shop rolls or estimate the Rolla cost of buying them.</p>'''
if old_method not in text:
    raise SystemExit('method panel shop anchor not found')
text = text.replace(old_method, new_method, 1)

path.write_text(text, encoding='utf-8')
print('added separate S2 Daily Shop material estimate')
