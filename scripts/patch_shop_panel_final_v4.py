from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

old='''          <!-- DAILY_SHOP_ESTIMATE_V2 -->
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
new='''          <!-- DAILY_SHOP_ESTIMATE_V4 -->
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
if old not in s: raise SystemExit('V2 shop panel not found')
s=s.replace(old,new,1)

oldjs='''    if($('shopRefreshEstimate')){
      const shop=resources.shopEstimate||dailyShopMaterialEstimate(cfg);
      $('shopRefreshEstimate').textContent=shop.refreshes
        ? `+${fmtCompact(shop.perDay.ore)} Ore · +${fmtCompact(shop.perDay.essence)} Essence · +${fmtCompact(shop.perDay.sand)} Sand · +${fmtCompact(shop.perDay.treat)} Treats / day`
        : 'Off';
      if($('shopRefreshEstimateNote')){
        $('shopRefreshEstimateNote').textContent=shop.refreshes
          ? `${shop.days} future reset day${shop.days===1?'':'s'} counted · current day excluded to avoid double-counting live Saved mats`
          : 'Set refreshes/day to include estimated Daily Shop materials in the projection.';
      }
    }'''
newjs='''    if($('shopRefreshEstimate')){
      const shop=resources.shopEstimate||dailyShopMaterialEstimate(cfg);
      const gain=(id,value)=>{const el=$(id);if(el)el.textContent=shop.refreshes?`+${fmtCompact(value)} / day`:'Off';};
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
if oldjs not in s: raise SystemExit('V2 shop render block not found')
s=s.replace(oldjs,newjs,1)

css='''
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
needle='</style>'
pos=s.rfind(needle)
if pos<0: raise SystemExit('style close not found')
s=s[:pos]+css+'\n'+s[pos:]
p.write_text(s,encoding='utf-8')
print('Daily Shop V4 applied')
