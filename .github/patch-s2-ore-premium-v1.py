from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')
marker = 'S2_ORE_PREMIUM_V1'
if marker in s:
    print('already applied')
    raise SystemExit(0)

old = '''          <label class="holdExpOption"><input id="holdExp" checked type="checkbox"> <span id="holdExpLabel">Hold Bed EXP for Season 2</span><small class="bedReserveStartNote">Start <b>Aug 28, 8:00 PM PDT</b></small></label>\n          <label><input id="reserveS2Essence" checked type="checkbox"> Reserve S2 Essence</label>'''
new = '''          <label class="holdExpOption"><input id="holdExp" checked type="checkbox"> <span id="holdExpLabel">Hold Bed EXP for Season 2</span><small class="bedReserveStartNote">Start <b>Aug 28, 8:00 PM PDT</b></small></label>\n          <label><input id="reserveS2Ore" checked type="checkbox"> Reserve S2 Ore</label>\n          <label><input id="reserveS2Essence" checked type="checkbox"> Reserve S2 Essence</label>'''
assert old in s, 'season controls anchor not found'
s = s.replace(old, new, 1)

old = '''        </div>\n        <small class="seasonPlanningNote" id="graceText">Cart income, Stamina generation, Realm purchase availability, and upgrade timing run through the season reset.</small>'''
new = '''        </div>\n        <small class="seasonPlanningNote" id="oreReserveNote"><b>Ore preservation:</b> Ore gets a 50% premium in optimizer comparisons, so comparable non-Ore routes are preferred. It is a soft preference, not a hard reserve—the planner will still spend Ore when preserving it would sacrifice overall efficiency.</small>\n        <small class="seasonPlanningNote" id="graceText">Cart income, Stamina generation, Realm purchase availability, and upgrade timing run through the season reset.</small>'''
assert old in s, 'season planning note anchor not found'
s = s.replace(old, new, 1)

old = "  const CHECK_IDS = ['holdExp','reserveS2Essence','reserveS2Sand','reserveS2Treats'];"
new = "  const CHECK_IDS = ['holdExp','reserveS2Ore','reserveS2Essence','reserveS2Sand','reserveS2Treats'];"
assert old in s, 'CHECK_IDS anchor not found'
s = s.replace(old, new, 1)

old = '''      if(hadState && state.reserveS2Treats===undefined) state.reserveS2Treats=true;'''
new = '''      if(hadState && state.reserveS2Treats===undefined) state.reserveS2Treats=true;\n      // S2_ORE_PREMIUM_V1: existing saved states opt into the new soft Ore-preservation preference.\n      if(hadState && state.reserveS2Ore===undefined) state.reserveS2Ore=true;'''
assert old in s, 'state migration anchor not found'
s = s.replace(old, new, 1)

old = '''  function marginalWeightedCosts(costs,resources){\n    return {\n      ore:Math.max(0,Number(costs?.ore)||0),'''
new = '''  /* S2_ORE_PREMIUM_V1\n     Soft S2 Ore preservation: within the optimizer's existing efficiency stage, spending Ore\n     is valued at 1.5x. Hard efficiency gates still win first, so this cannot force extra Realm\n     tool use or paid refreshes merely to save Ore. */\n  function marginalWeightedCosts(costs,resources,cfg=activeCalcConfig()){\n    const orePremium=(cfg.key==='s1' && $('reserveS2Ore')?.checked)?1.5:1;\n    return {\n      ore:Math.max(0,Number(costs?.ore)||0)*orePremium,'''
assert old in s, 'marginalWeightedCosts anchor not found'
s = s.replace(old, new, 1)

old = '''  function acquisitionEffortFor(costs,resources,cfg=activeCalcConfig()){\n    const marginalCosts=marginalWeightedCosts(costs,resources);'''
new = '''  function acquisitionEffortFor(costs,resources,cfg=activeCalcConfig()){\n    const marginalCosts=marginalWeightedCosts(costs,resources,cfg);'''
assert old in s, 'acquisitionEffortFor anchor not found'
s = s.replace(old, new, 1)

old = '''      $('holdExp').checked=true; $('reserveS2Essence').checked=true; $('reserveS2Sand').checked=true; $('reserveS2Treats').checked=true;'''
new = '''      $('holdExp').checked=true; $('reserveS2Ore').checked=true; $('reserveS2Essence').checked=true; $('reserveS2Sand').checked=true; $('reserveS2Treats').checked=true;'''
assert old in s, 'S2 reset defaults anchor not found'
s = s.replace(old, new, 1)

old = '''    const cfg=activeCalcConfig();\n    if(renderCalculatorSeasonChrome(cfg)){ clearCalcForRollover(cfg); return; }'''
new = '''    const cfg=activeCalcConfig();\n    if($('oreReserveNote')) $('oreReserveNote').hidden=!(cfg.key==='s1' && $('reserveS2Ore')?.checked);\n    if(renderCalculatorSeasonChrome(cfg)){ clearCalcForRollover(cfg); return; }'''
assert old in s, 'updateCalculator anchor not found'
s = s.replace(old, new, 1)

# Add a concise method-note sentence so the behavior remains documented after S1 rollover work is cleaned up.
old = '''<p><b>S2 Skill reserve / Automatic Stamina:</b> During S1, an enabled rollover reserve is protected before S1 Realm tools become spendable.'''
new = '''<p><b>S2 Ore preservation:</b> When Reserve S2 Ore is enabled during S1, Ore carries a 50% soft premium in resource-efficiency comparisons. Existing optimizer stage rules remain stricter, so the preference will not burn Realm tools or paid refreshes merely to save Ore; it only favors comparable non-Ore upgrade routes.</p>\n<p><b>S2 Skill reserve / Automatic Stamina:</b> During S1, an enabled rollover reserve is protected before S1 Realm tools become spendable.'''
assert old in s, 'method note anchor not found'
s = s.replace(old, new, 1)

p.write_text(s, encoding='utf-8')
print('applied', marker)
