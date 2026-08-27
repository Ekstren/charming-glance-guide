from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
marker='MAX_LAYOUT_SPEED_REALM_CAP_V1'
if marker in s:
    print('already applied')
    raise SystemExit(0)

old='''          <label class="freeSpeedToggle">Daily free speed-up<span class="freeSpeedCheck"><input id="freeSpeed" type="checkbox" checked> Use free 2-hour boost every reset</span></label>\n        </div>\n        <div class="maxAchievableBar"><button id="findMaxStars" type="button">Find max achievable</button><small id="maxAchievableStatus">Shows the maximum with your selected daily Realm plan and the hard maximum using all remaining Realm capacity.</small></div>'''
new='''          <div class="findMaxCell"><span>Maximum target</span><button id="findMaxStars" type="button">Find max achievable</button><small id="maxAchievableStatus">Checks your selected daily Realm plan and the hard Realm-cap ceiling.</small></div>\n        </div>'''
assert old in s, 'goal-grid/free-speed anchor missing'
s=s.replace(old,new,1)

# Daily free 2-hour boost is now an always-on assumption rather than a user toggle.
s=s.replace("  const CHECK_IDS = ['freeSpeed','holdExp','grace12','reserveS2Essence','reserveS2Sand','reserveS2Treats'];",
            "  const CHECK_IDS = ['holdExp','grace12','reserveS2Essence','reserveS2Sand','reserveS2Treats'];",1)
s=s.replace("    const boostHours=($('freeSpeed')?.checked ? 2 : 0)*countFuturePacificResets(capped,cfg.end.getTime());",
            "    const boostHours=2*countFuturePacificResets(capped,cfg.end.getTime());",1)
s=s.replace("    const boostHours=($('freeSpeed')?.checked ? 2 : 0)*countFuturePacificResets(capped,cutoff);",
            "    const boostHours=2*countFuturePacificResets(capped,cutoff);",1)
s=s.replace("    const boostHours=($('freeSpeed')?.checked ? 2 : 0)*boostResets;",
            "    const boostHours=2*boostResets;",1)
s=s.replace("      if(hadState && state.freeSpeed!==undefined && typeof state.freeSpeed!=='boolean') state.freeSpeed=Number(state.freeSpeed)>0;\n",'',1)
s=s.replace("      $('freeSpeed').checked=true; $('holdExp').checked=true; $('grace12').checked=true; $('reserveS2Essence').checked=true; $('reserveS2Sand').checked=true; $('reserveS2Treats').checked=true;",
            "      $('holdExp').checked=true; $('grace12').checked=true; $('reserveS2Essence').checked=true; $('reserveS2Sand').checked=true; $('reserveS2Treats').checked=true;",1)

# Public/community references consistently document 10 paid refresh purchases per Realm/day.
old_const='''  // Live-server correction: up to 20 paid Material Realm purchases per resource per server day.\n  // Public references currently publish Dawnium prices only for purchases 1-10. Purchases 11-20\n  // are treated as valid capacity but get a conservative planning penalty until their exact prices are verified.\n  const MATERIAL_REALM_BUY_COSTS = [60,60,100,100,150,150,200,200,250,300];\n  const MAX_REALM_REFRESHES_PER_DAY=20;'''
new_const='''  // Verified public/community curve: 10 paid Material Realm refresh purchases per Realm/day.\n  // Each purchase grants 5 Realm tools/entries.\n  const MATERIAL_REALM_BUY_COSTS = [60,60,100,100,150,150,200,200,250,300];\n  const MAX_REALM_REFRESHES_PER_DAY=MATERIAL_REALM_BUY_COSTS.length;'''
assert old_const in s, 'realm cap constants anchor missing'
s=s.replace(old_const,new_const,1)

s=s.replace('Each refresh = 5 tools · max 20/day per Realm','Each refresh = 5 tools · max 10/day per Realm',1)
s=s.replace('id="realmDailyOre" type="number" min="0" max="20"','id="realmDailyOre" type="number" min="0" max="10"',1)
s=s.replace('id="realmDailyEssence" type="number" min="0" max="20"','id="realmDailyEssence" type="number" min="0" max="10"',1)
s=s.replace('id="realmDailySand" type="number" min="0" max="20"','id="realmDailySand" type="number" min="0" max="10"',1)

old_time='''<p><b>Time projection:</b> Season deadlines and reset clocks are displayed in the timezone of the device opening this HTML. Internally the calculator still follows the Charming Glance server reset boundary, so travel/timezone changes do not alter the underlying server day. The free speed-up is a discrete 2-hour reset event, not a fractional daily rate: when enabled, every actual reset before the cutoff contributes 2 boost hours to Bed EXP, Cart production and Stamina regeneration. A 36-hour EXP reserve removes natural Bed hours only; boost hours that occur inside that reserve still count.</p>'''
new_time='''<p><b>Time projection:</b> Season deadlines and reset clocks are displayed in the timezone of the device opening this HTML. Internally the calculator still follows the Charming Glance server reset boundary, so travel/timezone changes do not alter the underlying server day. The planner assumes the free 2-hour speed-up is used at every reset and counts it as a discrete event for Bed EXP, Cart production and Stamina regeneration. A 36-hour EXP reserve removes natural Bed hours only; reset boost hours inside that reserve still count.</p>'''
assert old_time in s, 'time projection text anchor missing'
s=s.replace(old_time,new_time,1)

old_realm='''<p><b>Material Realm buys:</b> one paid refresh grants <b>5 actual Realm entries/tools</b>. Live-server correction: the daily purchase cap is treated as <b>20 per resource per server day</b>. Public references currently publish the Dawnium curve only for purchases 1–10 (60, 60, 100, 100, 150, 150, 200, 200, 250, 300), so purchases 11–20 count toward real capacity and feasibility but their Dawnium price is intentionally not fabricated. The optimizer ranks routes using fewer unknown-price 11–20 purchases ahead of routes using more, then compares only the Dawnium cost that is actually known. Existing plus routine-purchased Hammers/Knuckles/Shovels are treated as a reserve and, among otherwise equal routes, the optimizer preserves the route with more tools left. Your recurring daily purchase plan is added after future server resets; extra purchases consume the same 20-purchase daily cap. Resource-card shortfalls are shown after your selected recurring plan, while the top warning shows the hard remainder after every remaining extra slot is exhausted. The requested Primostar target is never lowered.</p>'''
new_realm='''<p><b>Material Realm buys:</b> one paid refresh grants <b>5 actual Realm entries/tools</b>. Current public guides and community planners consistently document a maximum of <b>10 paid refresh purchases per Realm per server day</b>, with the full Dawnium curve 60, 60, 100, 100, 150, 150, 200, 200, 250, 300. No verified 11–20 purchase tier was found, so the planner no longer invents extra capacity beyond 10. Existing plus routine-purchased Hammers/Knuckles/Shovels are treated as a reserve and, among otherwise equal routes, the optimizer preserves the route with more tools left. Your recurring daily purchase plan is added after future server resets; extra purchases consume the same 10-purchase daily cap. Resource-card shortfalls are shown after your selected recurring plan, while the top warning shows the hard remainder after every remaining extra slot is exhausted. The requested Primostar target is never lowered.</p>'''
assert old_realm in s, 'material realm method text anchor missing'
s=s.replace(old_realm,new_realm,1)

# The hard-max result no longer needs an unpriced-tier warning now that the cap is verified at 10.
old_status="""        const hardPlan=solveStars(hard).plan;\n        const unknown=Math.max(0,Number(hardPlan?.unknownPriceRefreshes)||0);\n        maxAchievableState={fingerprint,routine,hard};\n        status.innerHTML=`Selected daily plan max: <strong>${fmt(routine)}</strong> · Hard Realm-cap max: <strong>${fmt(hard)}</strong>${unknown?` · ${fmt(unknown)} unpriced tier 11–20 purchase${unknown===1?'':'s'} at hard max`:''}`;"""
new_status="""        maxAchievableState={fingerprint,routine,hard};\n        status.innerHTML=`Selected daily plan max: <strong>${fmt(routine)}</strong> · Hard Realm-cap max: <strong>${fmt(hard)}</strong>`;"""
assert old_status in s, 'max achievable status anchor missing'
s=s.replace(old_status,new_status,1)

# Place the max-target control in the former speed-up cell and make it visually match the grid.
css='''\n<style id="max-layout-speed-realm-cap-v1">\n/* MAX_LAYOUT_SPEED_REALM_CAP_V1 */\n.calcGrid .findMaxCell{display:grid;gap:4px;align-content:start;min-width:0}\n.calcGrid .findMaxCell>span{color:var(--muted);letter-spacing:.06em;text-transform:uppercase;font-size:9px;font-weight:850}\n.calcGrid .findMaxCell button{border:1px solid var(--today-border);background:var(--today-bg);color:var(--ink);border-radius:10px;cursor:pointer;min-height:38px;padding:7px 10px;font-size:10px;font-weight:850;text-align:left}\n.calcGrid .findMaxCell button:hover{border-color:var(--green);color:var(--green)}\n.calcGrid .findMaxCell button:disabled{cursor:wait;opacity:.65}\n.calcGrid .findMaxCell small{color:var(--muted);font-size:8px;line-height:1.35;min-width:0}\n.calcGrid .findMaxCell small strong{color:var(--green)}\n@media(max-width:700px){.calcGrid .findMaxCell button{text-align:center}}\n</style>\n'''
assert '</head>' in s
s=s.replace('</head>',css+'</head>',1)

# Safety: no live code should depend on the removed checkbox.
assert "$('freeSpeed')" not in s, 'freeSpeed runtime reference remains'
assert 'max 20/day per Realm' not in s
assert 'max="20"' not in s[s.find('realmDailyPlanRow'):s.find('realmDailyPlanRow')+3000]

p.write_text(s,encoding='utf-8')
print('patched')
