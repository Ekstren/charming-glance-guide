from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

old='''  // DAILY_SHOP_ESTIMATE_V2
  // Planning-only EV until a trustworthy shop slot/drop-rate table is available.
  // The estimate intentionally excludes the current server day so a user's live Saved
  // inventory can represent anything already bought today without being double-counted.
  const DAILY_SHOP_MATS_PER_REFRESH=Object.freeze({ore:700,essence:900,sand:600,treat:50});
  function dailyShopMaterialEstimate(cfg=activeCalcConfig()){
    const active=cfg.key==='s1'||cfg.key==='s2';
    const refreshes=active?clamp(Math.floor(n('shopRefreshesDaily',0)),0,20):0;
    const days=active?Math.max(0,countFuturePacificResets(Date.now(),cfg.end.getTime())):0;
    const perDay=Object.fromEntries(Object.entries(DAILY_SHOP_MATS_PER_REFRESH).map(([k,v])=>[k,v*refreshes]));
    const total=Object.fromEntries(Object.entries(perDay).map(([k,v])=>[k,v*days]));
    return {active,refreshes,days,perRefresh:DAILY_SHOP_MATS_PER_REFRESH,perDay,total};
  }'''

new='''  // DAILY_SHOP_ESTIMATE_V5
  // No trustworthy public slot/drop-rate table exists. Community evidence does show that
  // shop material stack sizes rise with progression and broadly track map-gathering amounts.
  // To avoid optimistic planning, count only 2/3 of one current-season map bundle per paid
  // refresh for Ore / Essence / Sand, rounded DOWN to 25. Treats stay at a deliberately low
  // 35 Basic-equivalent per refresh because their appearance rate and quality mix are less certain.
  // The current server day is excluded so Saved inventory can include anything already bought today.
  const DAILY_SHOP_CORE_BUNDLE_FACTOR=2/3;
  const DAILY_SHOP_TREAT_EQ_PER_REFRESH=35;
  function dailyShopMatsPerRefresh(cfg=activeCalcConfig()){
    const roundDown25=v=>Math.max(0,Math.floor((Number(v)||0)/25)*25);
    const map=cfg?.map||{};
    return {
      ore:roundDown25((Number(map.ore)||0)*DAILY_SHOP_CORE_BUNDLE_FACTOR),
      essence:roundDown25((Number(map.essence)||0)*DAILY_SHOP_CORE_BUNDLE_FACTOR),
      sand:roundDown25((Number(map.sand)||0)*DAILY_SHOP_CORE_BUNDLE_FACTOR),
      treat:DAILY_SHOP_TREAT_EQ_PER_REFRESH
    };
  }
  function dailyShopMaterialEstimate(cfg=activeCalcConfig()){
    const active=cfg.key==='s1'||cfg.key==='s2';
    const refreshes=active?clamp(Math.floor(n('shopRefreshesDaily',0)),0,20):0;
    const days=active?Math.max(0,countFuturePacificResets(Date.now(),cfg.end.getTime())):0;
    const perRefresh=dailyShopMatsPerRefresh(cfg);
    const perDay=Object.fromEntries(Object.entries(perRefresh).map(([k,v])=>[k,v*refreshes]));
    const total=Object.fromEntries(Object.entries(perDay).map(([k,v])=>[k,v*days]));
    return {active,refreshes,days,perRefresh,perDay,total};
  }'''

if old not in s: raise SystemExit('old Daily Shop model block not found')
s=s.replace(old,new,1)

oldp='''<p><b>Daily Shop estimate:</b> in both S1 and S2, until a trustworthy shop slot/drop-rate table is available, the optional shop planner uses a deliberately simple material-only estimate of <b>~700 Ore, ~900 Skill Essence, ~600 Chrono Sand and ~50 Basic Treats per refresh</b>. The default plan is 3 refreshes/day. Only future server-reset days are projected; the current day is excluded so materials already represented in the Saved fields are not double-counted. This does not value non-material shop rolls or estimate the Rolla cost of buying them.</p>'''
newp='''<p><b>Daily Shop estimate:</b> public guides do not expose a trustworthy slot/drop-rate table, but community reports and shop screenshots consistently show that material stacks increase with progression; one long-running CN guide explicitly notes that shop material quantities track map-gathering quantities. The planner therefore uses an <b>extremely conservative low-end model</b>: each paid refresh counts only <b>2/3 of one current-season map bundle</b> for Ore, Skill Essence and Chrono Sand (rounded down), plus <b>35 Basic-Treat equivalents</b>. With the currently loaded late-S1 map values this is about <b>600 Ore / 975 Essence / 550 Sand / 35 Treats</b> per refresh; at the S2 max-map bracket it is about <b>925 Ore / 1,175 Essence / 775 Sand / 35 Treats</b>. The default plan is 3 refreshes/day. Only future server-reset days are projected; the current day is excluded so materials already represented in Saved are not double-counted. Non-material rolls, premium shop items and the Rolla purchase cost are deliberately not valued.</p>'''
if oldp not in s: raise SystemExit('old Daily Shop method paragraph not found')
s=s.replace(oldp,newp,1)

p.write_text(s,encoding='utf-8')
print('grounded Daily Shop estimate V5 applied')
