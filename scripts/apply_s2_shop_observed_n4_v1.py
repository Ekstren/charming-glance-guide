from pathlib import Path
import re

path = Path('index.html')
s = path.read_text(encoding='utf-8')

new_block = r'''  // CG_S2_SHOP_OBSERVED_N4_V1
  // Charming Glance S2 shop averages measured from four untouched full shop pages.
  // Keep regular Chrono Sand and Rare Chrono Sand separate in the raw sample data.
  // The optimizer converts Rare Chrono Sand at the same 5:1 ratio used by saved inventory.
  const S2_SHOP_OBSERVED_PAGES=Object.freeze([
    Object.freeze({ore:3450,essence:1200,sand:1500,rareSand:270,treat:180}),
    Object.freeze({ore:5250,essence:1650,sand:0,rareSand:330,treat:110}),
    Object.freeze({ore:3000,essence:3000,sand:1500,rareSand:0,treat:135}),
    Object.freeze({ore:1650,essence:1800,sand:1800,rareSand:270,treat:245})
  ]);
  function s2ShopObservedAverage(){
    const pages=S2_SHOP_OBSERVED_PAGES;
    const n=pages.length||1;
    const total=pages.reduce((a,p)=>({
      ore:a.ore+p.ore,
      essence:a.essence+p.essence,
      sand:a.sand+p.sand,
      rareSand:a.rareSand+p.rareSand,
      treat:a.treat+p.treat
    }),{ore:0,essence:0,sand:0,rareSand:0,treat:0});
    return Object.fromEntries(Object.entries(total).map(([k,v])=>[k,v/n]));
  }

  // S1 keeps the older conservative fallback because the observed pages above are S2-only.
  const DAILY_SHOP_CORE_BUNDLE_FACTOR=2/3;
  const DAILY_SHOP_TREAT_EQ_PER_REFRESH=35;
  function dailyShopMatsPerRefresh(cfg=activeCalcConfig()){
    if(cfg?.key==='s2' && S2_SHOP_OBSERVED_PAGES.length){
      const a=s2ShopObservedAverage();
      return {
        ore:a.ore,
        essence:a.essence,
        sand:a.sand+a.rareSand*SAND_BLUE_EQ,
        treat:a.treat,
        sandRegular:a.sand,
        sandRare:a.rareSand
      };
    }
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
    // SHOP_BUYOUTS_V1: input counts full shop pages purchased, not refresh presses.
    // 0 = off; 1 = base page only; 2 = base page + one restock + second full-page buyout.
    const buyouts=active?clamp(Math.floor(n('shopRefreshesDaily',0)),0,20):0;
    const days=active?Math.max(0,futureRealmPurchaseDays(cfg)):0;
    const perBuyout=dailyShopMatsPerRefresh(cfg);
    const perDay=Object.fromEntries(Object.entries(perBuyout).map(([k,v])=>[k,v*buyouts]));
    const total=Object.fromEntries(Object.entries(perDay).map(([k,v])=>[k,v*days]));
    return {
      active,refreshes:buyouts,buyouts,days,perRefresh:perBuyout,perBuyout,perDay,total,
      sampleCount:cfg.key==='s2'?S2_SHOP_OBSERVED_PAGES.length:0
    };
  }
'''

pattern = r"  // DAILY_SHOP_ESTIMATE_V5\n.*?(?=\n  function applyS2ScoringStartDefaults\(\))"
s, count = re.subn(pattern, new_block.rstrip(), s, flags=re.S)
if count != 1:
    raise SystemExit(f'Expected one DAILY_SHOP_ESTIMATE_V5 block, found {count}')

old_label = '<div><span>Chrono Sand</span><b id="shopGainSand">—</b></div>'
new_label = '<div><span>Chrono Sand eq.</span><b id="shopGainSand">—</b></div>'
if old_label not in s:
    raise SystemExit('Shop Chrono Sand summary label not found')
s = s.replace(old_label, new_label)

old_render = r'''      gain('shopGainSand',shop.perDay.sand);
      gain('shopGainTreat',shop.perDay.treat);
      $('shopRefreshEstimate').textContent=shop.refreshes
        ? `+${fmtCompact(shop.perDay.ore)} Ore · +${fmtCompact(shop.perDay.essence)} Essence · +${fmtCompact(shop.perDay.sand)} Sand · +${fmtCompact(shop.perDay.treat)} Treats / day`
        : 'Off';
      if($('shopRefreshEstimateNote')){
        $('shopRefreshEstimateNote').textContent=shop.refreshes
          ? `${shop.days} future reset day${shop.days===1?'':'s'} counted · current day excluded to avoid double-counting materials already entered under Saved.`
          : 'Set Shop Buyouts/day: 1 counts the base page with no refresh; 2 counts the base page plus one restock and a second full-page buyout.';
      }
'''
new_render = r'''      gain('shopGainSand',shop.perDay.sand);
      gain('shopGainTreat',shop.perDay.treat);
      $('shopRefreshEstimate').textContent=shop.refreshes
        ? `+${fmtCompact(shop.perDay.ore)} Ore · +${fmtCompact(shop.perDay.essence)} Essence · +${fmtCompact(shop.perDay.sand)} Sand-eq · +${fmtCompact(shop.perDay.treat)} Treats / day`
        : 'Off';
      if($('shopRefreshEstimateNote')){
        const observed=shop.sampleCount>0;
        const perPage=shop.perBuyout||{};
        $('shopRefreshEstimateNote').textContent=shop.refreshes
          ? observed
            ? `Observed Charming Glance S2 average from ${shop.sampleCount} untouched shop pages · ${shop.days} future reset day${shop.days===1?'':'s'} counted · Sand-eq includes ${fmtCompact(shop.perDay.sandRegular)} regular + ${fmtCompact(shop.perDay.sandRare)} Rare Chrono Sand/day (Rare ×${SAND_BLUE_EQ}).`
            : `${shop.days} future reset day${shop.days===1?'':'s'} counted · current day excluded to avoid double-counting materials already entered under Saved.`
          : observed
            ? `Observed CG S2 sample n=${shop.sampleCount}: ${fmtCompact(perPage.ore)} Ore · ${fmtCompact(perPage.essence)} Essence · ${fmtCompact(perPage.sandRegular)} regular Sand + ${fmtCompact(perPage.sandRare)} Rare Sand · ${fmtCompact(perPage.treat)} Treats per page. Rare Sand counts ×${SAND_BLUE_EQ} toward Sand-equivalent.`
            : 'Set Shop Buyouts/day: 1 counts the base page with no refresh; 2 counts the base page plus one restock and a second full-page buyout.';
      }
'''
if old_render not in s:
    raise SystemExit('Shop render block not found')
s = s.replace(old_render, new_render, 1)

method_pattern = r'<p><b>Shop Buyouts:</b>.*?</p>'
method_replacement = (
    '<p><b>Shop Buyouts:</b> Season 2 shop income now uses a direct Charming Glance sample rather than the old map-yield proxy. '
    'The current sample is <b>4 untouched full shop pages</b>: average <b>3,337.5 Raw Ore</b>, <b>1,912.5 Battle Essence</b>, '
    '<b>1,200 regular Chrono Sand</b>, <b>217.5 Rare Chrono Sand</b>, and <b>167.5 Basic Treats</b> per page. '
    'Rare Chrono Sand remains separate in the sample data and is converted at <b>5 regular Sand per Rare Sand</b> only when the optimizer needs a single Sand-equivalent total, giving <b>2,287.5 Sand-equivalent per page</b> at the current n=4 average. '
    'Enter <b>0</b> for no shop stats, <b>1</b> for the base page only, <b>2</b> for the base page plus one restock and a second full-page buyout, and so on. '
    'Only future server-reset days are projected; the current day is excluded so materials already entered under Saved are not double-counted. '
    'This sample will be expanded as more untouched Charming Glance shop screenshots are collected.</p>'
)
s, count = re.subn(method_pattern, method_replacement, s, count=1, flags=re.S)
if count != 1:
    raise SystemExit(f'Expected one Shop Buyouts method paragraph, found {count}')

# Regression guards for the exact n=4 data set and Rare-Sand handling.
for needle in [
    'Object.freeze({ore:3450,essence:1200,sand:1500,rareSand:270,treat:180})',
    'Object.freeze({ore:5250,essence:1650,sand:0,rareSand:330,treat:110})',
    'Object.freeze({ore:3000,essence:3000,sand:1500,rareSand:0,treat:135})',
    'Object.freeze({ore:1650,essence:1800,sand:1800,rareSand:270,treat:245})',
    'sand:a.sand+a.rareSand*SAND_BLUE_EQ',
    'Observed CG S2 sample n=${shop.sampleCount}',
    '<span>Chrono Sand eq.</span>'
]:
    if needle not in s:
        raise SystemExit(f'Missing expected shop patch marker: {needle}')

path.write_text(s, encoding='utf-8')
print('Applied Charming Glance S2 observed shop averages (n=4).')
