from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

v2 = '''          <!-- DAILY_SHOP_ESTIMATE_V2 -->
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
          </div>'''

v4 = '''          <!-- DAILY_SHOP_ESTIMATE_V4 -->
          <div class="realmInventory shopEstimatePanel">
            <div class="realmInventoryTop"><strong>Daily Shop material estimate</strong><small>Extremely conservative estimate · material rolls only</small></div>
            <div class="shopEstimateCompact">
              <div class="shopRefreshControl">
                <label>Shop refreshes / day<input id="shopRefreshesDaily" type="number" min="0" max="20" step="1" value="3"><small>Default plan: 3/day</small></label>
              </div>
              <div class="shopGainSummary" aria-label="Estimated shop material gain per day">
                <div><span>Raw Ore</span><b id="shopGainOre">—</b></div>
                <div><span>Skill Essence</span><b id="shopGainEssence">—</b></div>
                <div><span>Chrono Sand</span><b id="shopGainSand">—</b></div>
                <div><span>Basic Treats</span><b id="shopGainTreat">—</b></div>
              </div>
            </div>
            <small id="shopRefreshEstimateNote" class="shopEstimateNote">Current day excluded to avoid double-counting materials already entered under Saved.</small>
            <span id="shopRefreshEstimate" hidden>—</span>
          </div>'''

v3 = '''          <!-- DAILY_SHOP_ESTIMATE_V3 -->
          <div class="realmInventory shopEstimatePanel">
            <div class="realmInventoryTop"><strong>Daily Shop material estimate</strong><small>S1 / S2 planning estimate · material rolls only</small></div>
            <div class="shopEstimateCompact">
              <div class="shopRefreshControl">
                <label>Shop refreshes / day<input id="shopRefreshesDaily" type="number" min="0" max="20" step="1" value="3"><small>Default plan: 3/day</small></label>
              </div>
              <div class="shopGainSummary" aria-label="Estimated shop material gain per day">
                <div><span>Raw Ore</span><b id="shopGainOre">—</b></div>
                <div><span>Skill Essence</span><b id="shopGainEssence">—</b></div>
                <div><span>Chrono Sand</span><b id="shopGainSand">—</b></div>
                <div><span>Basic Treats</span><b id="shopGainTreat">—</b></div>
              </div>
            </div>
            <small id="shopRefreshEstimateNote" class="shopEstimateNote">~700 Ore · 900 Essence · 600 Sand · 50 Basic Treats per refresh</small>
            <span id="shopRefreshEstimate" hidden>—</span>
          </div>'''

if v2 in s:
    s = s.replace(v2, v4, 1)
elif v3 in s:
    s = s.replace(v3, v4, 1)
elif 'DAILY_SHOP_ESTIMATE_V4' not in s:
    raise SystemExit('shop panel block not found')

js_v2 = '''    if($('shopRefreshEstimate')){
      const shop=resources.shopEstimate||dailyShopMaterialEstimate(cfg);
      $('shopRefreshEstimate').textContent=shop.refreshes
        ? `+${fmtCompact(shop.perDay.ore)} Ore · +${fmtCompact(shop.perDay.essence)} Essence · +${fmtCompact(shop.perDay.sand)} Sand · +${fmtCompact(shop.perDay.treat)} Treats / day`
        : 'Off';
      if($('shopRefreshEstimateNote')){
        $('shopRefreshEstimateNote').textContent=cfg.key==='s2'
          ? (shop.refreshes?`${shop.days} future reset day${shop.days===1?'':'s'} counted · current day excluded to avoid double-counting live Saved mats`:'Set refreshes/day to include estimated Daily Shop materials in the projection.')
          : 'S2-only estimate · default becomes 3 refreshes/day after rollover.';
      }
    }'''

js_v3 = '''    if($('shopRefreshEstimate')){
      const shop=resources.shopEstimate||dailyShopMaterialEstimate(cfg);
      const gain=(id,value,label)=>{ const el=$(id); if(el) el.textContent=shop.refreshes?`+${fmtCompact(value)} / day`:'Off'; };
      gain('shopGainOre',shop.perDay.ore,'Ore');
      gain('shopGainEssence',shop.perDay.essence,'Essence');
      gain('shopGainSand',shop.perDay.sand,'Sand');
      gain('shopGainTreat',shop.perDay.treat,'Treats');
      $('shopRefreshEstimate').textContent=shop.refreshes
        ? `+${fmtCompact(shop.perDay.ore)} Ore · +${fmtCompact(shop.perDay.essence)} Essence · +${fmtCompact(shop.perDay.sand)} Sand · +${fmtCompact(shop.perDay.treat)} Treats / day`
        : 'Off';
      if($('shopRefreshEstimateNote')){
        $('shopRefreshEstimateNote').textContent=shop.refreshes
          ? `${shop.days} future reset day${shop.days===1?'':'s'} counted · current day excluded to avoid double-counting live Saved mats · per-refresh estimate: ~700 Ore / 900 Essence / 600 Sand / 50 Treats`
          : 'Set refreshes/day to include estimated Daily Shop materials in the projection.';
      }
    }'''

js_v4 = '''    if($('shopRefreshEstimate')){
      const shop=resources.shopEstimate||dailyShopMaterialEstimate(cfg);
      const gain=(id,value)=>{ const el=$(id); if(el) el.textContent=shop.refreshes?`+${fmtCompact(value)} / day`:'Off'; };
      gain('shopGainOre',shop.perDay.ore);
      gain('shopGainEssence',shop.perDay.essence);
      gain('shopGainSand',shop.perDay.sand);
      gain('shopGainTreat',shop.perDay.treat);
      $('shopRefreshEstimate').textContent=shop.refreshes
        ? `+${fmtCompact(shop.perDay.ore)} Ore · +${fmtCompact(shop.perDay.essence)} Essence · +${fmtCompact(shop.perDay.sand)} Sand · +${fmtCompact(shop.perDay.treat)} Treats / day`
        : 'Off';
      if($('shopRefreshEstimateNote')){
        $('shopRefreshEstimateNote').textContent=shop.refreshes
          ? `${shop.days} future reset day${shop.days===1?'':'s'} counted · current day excluded to avoid double-counting materials already entered under Saved.`
          : 'Set refreshes/day to include the extremely conservative Daily Shop material estimate.';
      }
    }'''

if js_v2 in s:
    s = s.replace(js_v2, js_v4, 1)
elif js_v3 in s:
    s = s.replace(js_v3, js_v4, 1)
elif js_v4 not in s:
    raise SystemExit('shop render block not found')

css = '''
/* DAILY_SHOP_ESTIMATE_V4: compact two-column shop planner */
.shopEstimatePanel{margin-top:14px}
.shopEstimateCompact{display:grid;grid-template-columns:minmax(210px,.72fr) minmax(260px,1.28fr);gap:18px;align-items:stretch;padding:12px 14px 10px}
.shopRefreshControl{display:flex;align-items:center}
.shopRefreshControl label{display:flex;flex-direction:column;gap:7px;width:100%;font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:.04em}
.shopRefreshControl input{width:100%;min-height:44px}
.shopRefreshControl small{font-size:10px;font-weight:600;text-transform:none;letter-spacing:0;color:var(--muted)}
.shopGainSummary{display:grid;grid-template-columns:1fr;gap:5px;border-left:1px solid var(--line);padding-left:18px}
.shopGainSummary>div{display:flex;align-items:center;justify-content:space-between;gap:16px;min-height:26px}
.shopGainSummary span{font-size:11px;color:var(--muted);font-weight:700}
.shopGainSummary b{font-size:12px;color:var(--accent2);white-space:nowrap}
.shopEstimateNote{display:block;padding:0 14px 12px;color:var(--muted);font-size:9px;line-height:1.35}
@media(max-width:700px){.shopEstimateCompact{grid-template-columns:1fr}.shopGainSummary{border-left:0;border-top:1px solid var(--line);padding-left:0;padding-top:10px}}
'''

if 'DAILY_SHOP_ESTIMATE_V4: compact two-column shop planner' not in s:
    needle = '</style>'
    idx = s.rfind(needle)
    if idx < 0:
        raise SystemExit('style close not found')
    s = s[:idx] + css + '\n' + s[idx:]

p.write_text(s, encoding='utf-8')
print('patched Daily Shop panel to compact V4')
