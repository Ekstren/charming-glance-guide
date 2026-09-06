from pathlib import Path

SITE = Path("index.html")
text = SITE.read_text(encoding="utf-8")
original = text

replacements = [
    (
        '<div class="realmInventoryTop"><strong>Daily Shop material estimate</strong><small>Extremely conservative estimate · materials only</small></div>',
        '<div class="realmInventoryTop"><strong>Shop Buyouts</strong><small>Extremely conservative estimate · materials only</small></div>',
    ),
    (
        '<label>Shop restocks / day<input id="shopRefreshesDaily" type="number" min="0" max="20" step="1" value="0"><small>Planner default: 0/day</small></label>',
        '<label>Full-page buyouts / day<input id="shopRefreshesDaily" type="number" min="0" max="20" step="1" value="0"><small>0 = off · 1 = base page · 2 = base page + 1 restock</small></label>',
    ),
    (
        '<small id="shopRefreshEstimateNote" class="shopEstimateNote">Today excluded to avoid double-counting Saved materials.</small>',
        '<small id="shopRefreshEstimateNote" class="shopEstimateNote">0 = no shop stats · 1 = buy out the base page with no refresh · 2 = buy out the base page, restock once, then buy out the full page again.</small>',
    ),
    (
        ": 'Set restocks/day to include the extremely conservative Daily Shop material estimate.';",
        ": 'Set Shop Buyouts/day: 1 counts the base page with no refresh; 2 counts the base page plus one restock and a second full-page buyout.';",
    ),
]

for old, new in replacements:
    if new in text:
        continue
    if old not in text:
        raise SystemExit(f"Shop Buyouts anchor not found: {old[:80]}")
    text = text.replace(old, new, 1)

old_help = """<p><b>Daily Shop estimate:</b> public guides do not expose a trustworthy slot/drop-rate table, but community reports and shop screenshots consistently show that material stacks increase with progression; one long-running CN guide explicitly notes that shop material quantities track map-gathering quantities. The planner therefore uses an <b>extremely conservative low-end model</b>: each restock counts only <b>2/3 of one current-season map bundle</b> for Ore, Skill Essence and Chrono Sand (rounded down), plus <b>35 Basic-Treat equivalents</b>. With the currently loaded late-S1 map values this is about <b>600 Ore / 975 Essence / 550 Sand / 35 Treats</b> per restock; at the S2 max-map bracket it is about <b>925 Ore / 1,175 Essence / 775 Sand / 35 Treats</b>. The default is 0 refreshes/day; users opt in to the number they actually buy. Only future server-reset days are projected; the current day is excluded so materials already represented in Saved are not double-counted. Non-material rolls, premium shop items and the Rolla purchase cost are deliberately not valued.</p>"""
new_help = """<p><b>Shop Buyouts:</b> public guides do not expose a trustworthy slot/drop-rate table, but community reports and shop screenshots consistently show that material stacks increase with progression; one long-running CN guide explicitly notes that shop material quantities track map-gathering quantities. The planner therefore uses an <b>extremely conservative low-end model</b> for each full-page buyout: <b>2/3 of one current-season map bundle</b> for Ore, Skill Essence and Chrono Sand (rounded down), plus <b>35 Basic-Treat equivalents</b>. With the currently loaded late-S1 map values this is about <b>600 Ore / 975 Essence / 550 Sand / 35 Treats</b> per full-page buyout; at the S2 max-map bracket it is about <b>925 Ore / 1,175 Essence / 775 Sand / 35 Treats</b>. Enter <b>0</b> for no shop stats, <b>1</b> to buy out the base page with no refresh, <b>2</b> to buy out the base page, restock once, then buy out that full page again, and so on. Only future server-reset days are projected; the current day is excluded so materials already represented in Saved are not double-counted. Non-material rolls, premium shop items and the Rolla purchase cost are deliberately not valued.</p>"""

if new_help not in text:
    if old_help not in text:
        raise SystemExit("Shop Buyouts help paragraph anchor not found")
    text = text.replace(old_help, new_help, 1)

# Keep the existing storage/input id for backwards compatibility, but document the
# new semantics where the estimator is calculated: the value is full pages bought,
# not the number of refresh button presses.
old_calc = """  function dailyShopMaterialEstimate(cfg=activeCalcConfig()){
    const active=cfg.key==='s1'||cfg.key==='s2';
    const refreshes=active?clamp(Math.floor(n('shopRefreshesDaily',0)),0,20):0;
    const days=active?Math.max(0,futureRealmPurchaseDays(cfg)):0;
    const perRefresh=dailyShopMatsPerRefresh(cfg);
    const perDay=Object.fromEntries(Object.entries(perRefresh).map(([k,v])=>[k,v*refreshes]));
    const total=Object.fromEntries(Object.entries(perDay).map(([k,v])=>[k,v*days]));
    return {active,refreshes,days,perRefresh,perDay,total};
  }"""
new_calc = """  function dailyShopMaterialEstimate(cfg=activeCalcConfig()){
    const active=cfg.key==='s1'||cfg.key==='s2';
    // SHOP_BUYOUTS_V1: input counts full shop pages purchased, not refresh presses.
    // 0 = off; 1 = base page only; 2 = base page + one restock + second full-page buyout.
    const buyouts=active?clamp(Math.floor(n('shopRefreshesDaily',0)),0,20):0;
    const days=active?Math.max(0,futureRealmPurchaseDays(cfg)):0;
    const perBuyout=dailyShopMatsPerRefresh(cfg);
    const perDay=Object.fromEntries(Object.entries(perBuyout).map(([k,v])=>[k,v*buyouts]));
    const total=Object.fromEntries(Object.entries(perDay).map(([k,v])=>[k,v*days]));
    return {active,refreshes:buyouts,buyouts,days,perRefresh:perBuyout,perBuyout,perDay,total};
  }"""

if new_calc not in text:
    if old_calc not in text:
        raise SystemExit("Shop Buyouts calculation anchor not found")
    text = text.replace(old_calc, new_calc, 1)

if text == original:
    print("Shop Buyouts semantics are already applied.")
else:
    SITE.write_text(text, encoding="utf-8")
    print("Applied Shop Buyouts labels and full-page semantics.")
