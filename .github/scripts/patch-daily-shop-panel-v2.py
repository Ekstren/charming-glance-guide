from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

old_shop = '''          <!-- DAILY_SHOP_ESTIMATE_V1 -->
          <div class="realmDailyPlanRow shopEstimateRow">
            <div class="realmDailyCustom">
              <span class="realmDailyTitle">Daily Shop material estimate <small>S2 planning estimate · material rolls only</small></span>
              <div class="realmDailyInputs">
                <label>Shop refreshes / day<input id="shopRefreshesDaily" type="number" min="0" max="20" step="1" value="0"><small>Default S2 plan: 3/day</small></label>
              </div>
            </div>
            <div class="realmPlanSummary"><span>Estimated gain</span><b id="shopRefreshEstimate">—</b><small id="shopRefreshEstimateNote">~700 Ore · 900 Essence · 600 Sand · 50 Basic Treats per refresh</small></div>
          </div>
'''

new_shop = '''          <!-- DAILY_SHOP_ESTIMATE_V2 -->
          <div class="realmInventory shopEstimatePanel">
            <div class="realmInventoryTop"><strong>Daily Shop material estimate</strong><small>S1 / S2 planning estimate · material rolls only</small></div>
            <div class="realmDailyPlanRow shopEstimateRow">
              <div class="realmDailyCustom">
                <span class="realmDailyTitle">Shop refreshes / day <small>Estimated material value only</small></span>
                <div class="realmDailyInputs">
                  <label>Refreshes / day<input id="shopRefreshesDaily" type="number" min="0" max="20" step="1" value="3"><small>Default plan: 3/day</small></label>
                </div>
              </div>
              <div class="realmPlanSummary"><span>Estimated gain</span><b id="shopRefreshEstimate">—</b><small id="shopRefreshEstimateNote">~700 Ore · 900 Essence · 600 Sand · 50 Basic Treats per refresh</small></div>
            </div>
          </div>
'''

if old_shop not in s:
    raise SystemExit('old Daily Shop block not found')
s = s.replace(old_shop, '', 1)

realm_tail = '''          </div>
          <input id="refinedOreCurrent" type="hidden" value="">'''
if realm_tail not in s:
    raise SystemExit('Material Realm tail anchor not found')
s = s.replace(realm_tail, '''          </div>
''' + new_shop + '''          <input id="refinedOreCurrent" type="hidden" value="">''', 1)

old_model = '''    const active=cfg.key==='s2';
    const refreshes=active?clamp(Math.floor(n('shopRefreshesDaily',0)),0,20):0;
    const days=active?Math.max(0,countFuturePacificResets(Date.now(),cfg.end.getTime())):0;'''
new_model = '''    const active=cfg.key==='s1'||cfg.key==='s2';
    const refreshes=active?clamp(Math.floor(n('shopRefreshesDaily',0)),0,20):0;
    const days=active?Math.max(0,countFuturePacificResets(Date.now(),cfg.end.getTime())):0;'''
if old_model not in s:
    raise SystemExit('Daily Shop season model anchor not found')
s = s.replace(old_model, new_model, 1)

old_render = '''      if($('shopRefreshEstimateNote')){
        $('shopRefreshEstimateNote').textContent=cfg.key==='s2'
          ? (shop.refreshes?`${shop.days} future reset day${shop.days===1?'':'s'} counted · current day excluded to avoid double-counting live Saved mats`:'Set refreshes/day to include estimated Daily Shop materials in the projection.')
          : 'S2-only estimate · default becomes 3 refreshes/day after rollover.';
      }'''
new_render = '''      if($('shopRefreshEstimateNote')){
        $('shopRefreshEstimateNote').textContent=shop.refreshes
          ? `${shop.days} future reset day${shop.days===1?'':'s'} counted · current day excluded to avoid double-counting live Saved mats`
          : 'Set refreshes/day to include estimated Daily Shop materials in the projection.';
      }'''
if old_render not in s:
    raise SystemExit('Daily Shop render anchor not found')
s = s.replace(old_render, new_render, 1)

old_method = '''<p><b>S2 Daily Shop estimate:</b> until a trustworthy shop slot/drop-rate table is available, the optional shop planner uses a deliberately simple material-only estimate of <b>~700 Ore, ~900 Skill Essence, ~600 Chrono Sand and ~50 Basic Treats per refresh</b>. The S2 default is 3 refreshes/day. Only future server-reset days are projected; the current day is excluded so materials already represented in the Saved fields are not double-counted. This does not value non-material shop rolls or estimate the Rolla cost of buying them.</p>'''
new_method = '''<p><b>Daily Shop estimate:</b> in both S1 and S2, until a trustworthy shop slot/drop-rate table is available, the optional shop planner uses a deliberately simple material-only estimate of <b>~700 Ore, ~900 Skill Essence, ~600 Chrono Sand and ~50 Basic Treats per refresh</b>. The default plan is 3 refreshes/day. Only future server-reset days are projected; the current day is excluded so materials already represented in the Saved fields are not double-counted. This does not value non-material shop rolls or estimate the Rolla cost of buying them.</p>'''
if old_method not in s:
    raise SystemExit('Daily Shop method text anchor not found')
s = s.replace(old_method, new_method, 1)

# Update nearby implementation comments to avoid describing the feature as S2-only.
s = s.replace('// DAILY_SHOP_ESTIMATE_V1', '// DAILY_SHOP_ESTIMATE_V2', 1)

p.write_text(s, encoding='utf-8')

# Verification
out = p.read_text(encoding='utf-8')
assert out.count('id="shopRefreshesDaily"') == 1
assert out.index('Material Realm plan') < out.index('Daily Shop material estimate')
assert 'S2-only estimate' not in out
assert "const active=cfg.key==='s1'||cfg.key==='s2';" in out
assert 'class="realmInventory shopEstimatePanel"' in out
print('Daily Shop panel v2 applied successfully')
