from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')
marker = 'APPLY_RECOMMENDED_REALM_REFRESHES_V1'
if marker in s:
    print('already applied')
    raise SystemExit(0)

old_helper = """  function realmDailyValue(key){
    const ids={ore:'realmDailyOre',essence:'realmDailyEssence',sand:'realmDailySand'};
    const id=ids[key];
    return clamp(Math.floor(n(id,4)),0,20);
  }
"""
new_helper = """  function realmDailyValue(key){
    const ids={ore:'realmDailyOre',essence:'realmDailyEssence',sand:'realmDailySand'};
    const id=ids[key];
    return clamp(Math.floor(n(id,4)),0,10);
  }
  function applyRecommendedRealmRefreshes(button){
    const values={
      realmDailyOre:clamp(Math.floor(Number(button?.dataset?.ore)||0),0,10),
      realmDailyEssence:clamp(Math.floor(Number(button?.dataset?.essence)||0),0,10),
      realmDailySand:clamp(Math.floor(Number(button?.dataset?.sand)||0),0,10)
    };
    Object.entries(values).forEach(([id,value])=>{
      const el=$(id);
      if(!el) return;
      el.value=String(value);
      markManualSnapshot(id);
    });
    resetMaxAchievableUi();
    saveState();
    scheduleCalculatorUpdate(0);
  }
"""
if old_helper not in s:
    raise SystemExit('realmDailyValue anchor not found')
s = s.replace(old_helper, new_helper, 1)

old_warning = """        // TARGET_MESSAGE_LINES_V1: keep the status sentence and recommendation on separate lines.
        const route=dailySuggested.changed
          ? `<span class=\"targetMessageDetail\">Recommended refreshes/day: Ore ${dailySuggested.ore} · Essence ${dailySuggested.essence} · Sand ${dailySuggested.sand}.</span>`
          : '';
        $('targetMessage').innerHTML=`⚠ Goal is achievable, but your current Material Realm refresh plan is too low.${route}`;
"""
new_warning = """        // APPLY_RECOMMENDED_REALM_REFRESHES_V1: recommendation and one-click apply live inside the caution box.
        const route=dailySuggested.changed
          ? `<span class=\"targetMessageDetail\">Recommended refreshes/day: Ore ${dailySuggested.ore} · Essence ${dailySuggested.essence} · Sand ${dailySuggested.sand}.</span>`
          : '';
        const action=dailySuggested.changed
          ? `<button type=\"button\" class=\"applyRealmRecommendation\" data-ore=\"${dailySuggested.ore}\" data-essence=\"${dailySuggested.essence}\" data-sand=\"${dailySuggested.sand}\" onclick=\"applyRecommendedRealmRefreshes(this)\">Apply refreshes</button>`
          : '';
        $('targetMessage').innerHTML=`<span class=\"targetMessageCopy\">⚠ Goal is achievable, but your current Material Realm refresh plan is too low.${route}</span>${action}`;
"""
if old_warning not in s:
    raise SystemExit('warning anchor not found')
s = s.replace(old_warning, new_warning, 1)

css = """
<style id=\"apply-recommended-realm-refreshes-v1\">
/* APPLY_RECOMMENDED_REALM_REFRESHES_V1 */
#targetMessage.caution:has(.applyRealmRecommendation){display:flex!important;align-items:center;justify-content:space-between;gap:16px}
#targetMessage .targetMessageCopy{min-width:0;flex:1}
#targetMessage .applyRealmRecommendation{flex:0 0 auto;border:1px solid color-mix(in srgb,var(--status-warning) 68%,var(--line));background:color-mix(in srgb,var(--status-warning) 14%,var(--surface));color:var(--status-warning);border-radius:9px;padding:8px 11px;font-size:9px;font-weight:900;cursor:pointer;white-space:nowrap}
#targetMessage .applyRealmRecommendation:hover{background:var(--status-warning);color:var(--surface)}
@media(max-width:700px){#targetMessage.caution:has(.applyRealmRecommendation){align-items:stretch;flex-direction:column;gap:9px}#targetMessage .applyRealmRecommendation{width:100%}}
</style>
"""
if '</head>' not in s:
    raise SystemExit('head close not found')
s = s.replace('</head>', css + '</head>', 1)

p.write_text(s, encoding='utf-8')
print('applied')
