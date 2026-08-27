from pathlib import Path

path=Path('index.html')
s=path.read_text(encoding='utf-8')
marker='REALM_20_REFRESH_TOOL_COUNT_V1'
if marker in s:
    print('already applied')
    raise SystemExit(0)

repls={
'''function realmDailyValue(key){
    const ids={ore:'realmDailyOre',essence:'realmDailyEssence',sand:'realmDailySand'};
    const id=ids[key];
    return clamp(Math.floor(n(id,4)),0,10);
  }''':'''function realmDailyValue(key){
    const ids={ore:'realmDailyOre',essence:'realmDailyEssence',sand:'realmDailySand'};
    const id=ids[key];
    return clamp(Math.floor(n(id,4)),0,MAX_REALM_REFRESHES_PER_DAY);
  }''',
'''realmDailyOre:clamp(Math.floor(Number(button?.dataset?.ore)||0),0,10),
      realmDailyEssence:clamp(Math.floor(Number(button?.dataset?.essence)||0),0,10),
      realmDailySand:clamp(Math.floor(Number(button?.dataset?.sand)||0),0,10)''':'''realmDailyOre:clamp(Math.floor(Number(button?.dataset?.ore)||0),0,MAX_REALM_REFRESHES_PER_DAY),
      realmDailyEssence:clamp(Math.floor(Number(button?.dataset?.essence)||0),0,MAX_REALM_REFRESHES_PER_DAY),
      realmDailySand:clamp(Math.floor(Number(button?.dataset?.sand)||0),0,MAX_REALM_REFRESHES_PER_DAY)''',
'''// Verified public/community curve: 10 paid Material Realm refresh purchases per Realm/day.
  // Each purchase grants 5 Realm tools/entries.
  const MATERIAL_REALM_BUY_COSTS = [60,60,100,100,150,150,200,200,250,300];
  const MAX_REALM_REFRESHES_PER_DAY=MATERIAL_REALM_BUY_COSTS.length;
  const REALM_RUNS_PER_REFRESH=5;''':'''// REALM_20_REFRESH_TOOL_COUNT_V1
  // One refresh grants 5 Realm tools/entries. The first 10 Dawnium prices are known;
  // refreshes 11–20 remain usable capacity but their Dawnium prices are intentionally unknown.
  const MATERIAL_REALM_BUY_COSTS = [60,60,100,100,150,150,200,200,250,300];
  const MAX_REALM_REFRESHES_PER_DAY=20;
  const REALM_RUNS_PER_REFRESH=5;''',
'''Each refresh = 5 tools · max 10/day per Realm''':'''Each refresh = 5 tools · max 20/day per Realm''',
'''type="number" min="0" max="10" step="1" value="0"''':'''type="number" min="0" max="20" step="1" value="0"''',
'''Current public guides and community planners consistently document a maximum of <b>10 paid refresh purchases per Realm per server day</b>, with the full Dawnium curve 60, 60, 100, 100, 150, 150, 200, 200, 250, 300. No verified 11–20 purchase tier was found, so the planner no longer invents extra capacity beyond 10.''':'''Each paid refresh grants <b>5 actual Realm entries/tools</b>, and the planner allows up to <b>20 refreshes per Realm per server day</b> (100 tools). The verified Dawnium curve currently covers refreshes 1–10: 60, 60, 100, 100, 150, 150, 200, 200, 250, 300. Refreshes 11–20 count fully toward tool capacity, but their Dawnium prices remain unknown and are not fabricated.'''
}

for old,new in repls.items():
    if old not in s:
        if old.startswith('type="number"'):
            continue
        raise SystemExit('missing expected block: '+old[:90])
    if old.startswith('type="number"'):
        s=s.replace(old,new,3)
    else:
        s=s.replace(old,new,1)

# The formula paragraph replacement above may have duplicated its opening sentence because
# the original paragraph already begins with it; normalize if needed.
s=s.replace('<p><b>Material Realm buys:</b> one paid refresh grants <b>5 actual Realm entries/tools</b>. Each paid refresh grants <b>5 actual Realm entries/tools</b>,',
            '<p><b>Material Realm buys:</b> Each paid refresh grants <b>5 actual Realm entries/tools</b>,')

path.write_text(s,encoding='utf-8')
print('fixed 20-refresh tool accounting for Ore, Essence, and Sand')
