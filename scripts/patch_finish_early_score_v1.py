from pathlib import Path


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected 1 match, found {count}")
    return text.replace(old, new, 1)

index_path = Path('index.html')
runtime_path = Path('assets/runtime.js')
css_path = Path('assets/site.css')

index = index_path.read_text(encoding='utf-8')
runtime = runtime_path.read_text(encoding='utf-8')
css = css_path.read_text(encoding='utf-8')

# 1) Add the compact control directly into the season-end row.
old = '<div class="seasonDeadline"><span id="seasonDeadlineLabel">Season ends</span><b id="seasonDeadlineDate">—</b><small id="seasonRemaining">—</small></div>'
new = '<div class="seasonDeadline"><span id="seasonDeadlineLabel">Season ends</span><b id="seasonDeadlineDate">—</b><label class="finishEarlyControl" title="Stop counting Character score and projected resources this many reset-days before season end"><span>Finish early</span><input id="finishEarlyDays" type="number" min="0" step="1" value="0" inputmode="numeric"><em>days</em></label><small id="seasonRemaining">—</small></div>'
index = replace_once(index, old, new, 'season deadline control')

# 2) Persist/reset the new setting like every other calculator input.
old = "    targetStars:680,\n    // QY labels 128 as an S1 F2P/Light recommendation; it is only a starter/example carry value.\n    historicalStars:128,\n    charLevel:130,charExp:0,bedExp:0,"
new = "    targetStars:680,\n    // QY labels 128 as an S1 F2P/Light recommendation; it is only a starter/example carry value.\n    historicalStars:128,\n    charLevel:130,charExp:0,bedExp:0,finishEarlyDays:0,"
runtime = replace_once(runtime, old, new, 'S2 defaults')

old = "    'targetStars','historicalStars','charLevel','charExp','bedExp','skillLevel','relicLevel','fantomonLevel','gearLevel',"
new = "    'targetStars','historicalStars','charLevel','charExp','bedExp','finishEarlyDays','skillLevel','relicLevel','fantomonLevel','gearLevel',"
runtime = replace_once(runtime, old, new, 'input ids')

# 3) Calendar-day cutoff at the 6 AM Pacific reset, so DST cannot shift the requested day count.
old = "  function upgradeFinishCutoffMs(cfg=activeCalcConfig()){\n    return cfg.end.getTime();\n  }"
new = """  function finishEarlyDaysValue(){
    const raw=Number($('finishEarlyDays')?.value);
    return Number.isFinite(raw)?Math.max(0,Math.floor(raw)):0;
  }
  function finishScoreCutoffMs(cfg=activeCalcConfig()){
    const days=finishEarlyDaysValue();
    if(days<=0) return cfg.end.getTime();
    const endIso=pacificIsoAt(cfg.end.getTime());
    const cutoff=pacificLocalMs(isoAddDays(endIso,-days),6,0);
    return Math.min(cfg.end.getTime(),cutoff);
  }
  function upgradeFinishCutoffMs(cfg=activeCalcConfig()){
    return Math.max(Date.now(),finishScoreCutoffMs(cfg));
  }"""
runtime = replace_once(runtime, old, new, 'finish cutoff functions')

# 4) Every projected resource source uses the same finish-early cutoff.
old = "  function futureRealmPurchaseDays(cfg=activeCalcConfig()){\n    const now=Date.now();\n    const cutoff=cfg.end.getTime();"
new = "  function futureRealmPurchaseDays(cfg=activeCalcConfig()){\n    const now=Date.now();\n    const cutoff=upgradeFinishCutoffMs(cfg);"
runtime = replace_once(runtime, old, new, 'future realm cutoff')

old = "  function resourceCutoffMs(cfg=activeCalcConfig()){\n    return Math.max(Date.now(),cfg.end.getTime());\n  }\n  function projectionResourceHoursAt(ms,cfg=activeCalcConfig()){\n    const cutoff=cfg.end.getTime();"
new = "  function resourceCutoffMs(cfg=activeCalcConfig()){\n    return upgradeFinishCutoffMs(cfg);\n  }\n  function projectionResourceHoursAt(ms,cfg=activeCalcConfig()){\n    const cutoff=upgradeFinishCutoffMs(cfg);"
runtime = replace_once(runtime, old, new, 'resource projection cutoff')

old = "    const realmCutoffMs=cfg.end.getTime();"
new = "    const realmCutoffMs=finishScoreCutoffMs(cfg);"
runtime = replace_once(runtime, old, new, 'aged realm cutoff')

old = "  function futureRealmPurchaseDaysUntil(targetMs,cfg=activeCalcConfig()){\n    const now=Date.now();\n    const cutoff=Math.max(now,Math.min(Number(targetMs)||cfg.end.getTime(),cfg.end.getTime()));"
new = "  function futureRealmPurchaseDaysUntil(targetMs,cfg=activeCalcConfig()){\n    const now=Date.now();\n    const plannerCutoff=upgradeFinishCutoffMs(cfg);\n    const cutoff=Math.max(now,Math.min(Number(targetMs)||plannerCutoff,plannerCutoff));"
runtime = replace_once(runtime, old, new, 'realm days until cutoff')

old = "  function projectedResourcesTo(targetMs,cfg=activeCalcConfig()){\n    const now=Date.now();\n    const cutoff=Math.max(now,Math.min(Number(targetMs)||cfg.end.getTime(),cfg.end.getTime()));"
new = "  function projectedResourcesTo(targetMs,cfg=activeCalcConfig()){\n    const now=Date.now();\n    const plannerCutoff=upgradeFinishCutoffMs(cfg);\n    const cutoff=Math.max(now,Math.min(Number(targetMs)||plannerCutoff,plannerCutoff));"
runtime = replace_once(runtime, old, new, 'projected resources cutoff')

old = "  function projectedResources(hours,cfg=activeCalcConfig()){\n    return projectedResourcesTo(cfg.end.getTime(),cfg);\n  }"
new = "  function projectedResources(hours,cfg=activeCalcConfig()){\n    return projectedResourcesTo(upgradeFinishCutoffMs(cfg),cfg);\n  }"
runtime = replace_once(runtime, old, new, 'projected resources wrapper')

old = "  function materialRealmDaysAvailable(cfg=activeCalcConfig()){\n    if(cfg.end.getTime()<=Date.now()) return 0;\n    // Current server-day window + each future 6 AM reset strictly before the cutoff.\n    return 1+futureRealmPurchaseDays(cfg);\n  }"
new = "  function materialRealmDaysAvailable(cfg=activeCalcConfig()){\n    if(upgradeFinishCutoffMs(cfg)<=Date.now()) return 0;\n    // Current server-day window + each future 6 AM reset strictly before the planner cutoff.\n    return 1+futureRealmPurchaseDays(cfg);\n  }"
runtime = replace_once(runtime, old, new, 'material realm days')

# 5) Character score uses the early cutoff, while the top Character card still shows true season-end level.
old = """    if(!p) p=projectCharacter(cfg);
    if(cfg.key==='s2' && p.level<=cfg.scoreFloor){ clearS2ProjectedAtFloor(cfg,p); return; }
    const upgradeP=projectCharacterTo(upgradeFinishCutoffMs(cfg),cfg);
    // Upgrade availability now runs through the actual season reset; there is no separate finishing cutoff.
    p.upgradeCapLevel=upgradeP.level;"""
new = """    if(!p) p=projectCharacter(cfg);
    const seasonEndP=p;
    p=projectCharacterTo(upgradeFinishCutoffMs(cfg),cfg);
    if(cfg.key==='s2' && p.level<=cfg.scoreFloor){ clearS2ProjectedAtFloor(cfg,p); return; }
    const upgradeP=p;
    // Upgrade availability and score projection stop at the optional finish-early cutoff.
    p.upgradeCapLevel=upgradeP.level;"""
runtime = replace_once(runtime, old, new, 'optimizer character cutoff')

old = """    $('seasonRemaining').textContent=formatRemaining(p.hours);
    const pc=`Lv.${p.level} · ${(p.pct*100).toFixed(1)}%`;
    $('projectedCharacter').value=pc;
    const expEstimated=cfg.key==='s1'&&s1ProjectionUsesEstimatedExp(currentCharacter.level,p.level);
    $('resultProjectedCharacter').textContent=`Lv.${p.level} (${(p.pct*100).toFixed(1)}%)`;"""
new = """    $('seasonRemaining').textContent=formatRemaining(seasonEndP.hours);
    const pc=`Lv.${seasonEndP.level} · ${(seasonEndP.pct*100).toFixed(1)}%`;
    $('projectedCharacter').value=pc;
    const expEstimated=cfg.key==='s1'&&s1ProjectionUsesEstimatedExp(currentCharacter.level,seasonEndP.level);
    $('resultProjectedCharacter').textContent=`Lv.${p.level} (${(p.pct*100).toFixed(1)}%)`;"""
runtime = replace_once(runtime, old, new, 'season end character display')

old = """  function clearS2ProjectedAtFloor(cfg,p=projectCharacter(cfg)){
    const historical=Math.max(0,Math.floor(n('historicalStars',0)));
    const carried=historical+cfg.starBase;
    $('seasonRemaining').textContent=formatRemaining(p.hours);
    $('projectedCharacter').value=`Lv.${p.level} · ${(p.pct*100).toFixed(1)}%`;
    $('resultProjectedCharacter').textContent=`Lv.${p.level} (${(p.pct*100).toFixed(1)}%)`;"""
new = """  function clearS2ProjectedAtFloor(cfg,p=projectCharacter(cfg)){
    const historical=Math.max(0,Math.floor(n('historicalStars',0)));
    const carried=historical+cfg.starBase;
    const seasonEndP=projectCharacter(cfg);
    $('seasonRemaining').textContent=formatRemaining(seasonEndP.hours);
    $('projectedCharacter').value=`Lv.${seasonEndP.level} · ${(seasonEndP.pct*100).toFixed(1)}%`;
    $('resultProjectedCharacter').textContent=`Lv.${p.level} (${(p.pct*100).toFixed(1)}%)`;"""
runtime = replace_once(runtime, old, new, 'floor display split')

# 6) Compact nested card styling beside the season end date.
marker = '/* FINISH_EARLY_SCORE_V1 */'
if marker not in css:
    css += """

/* FINISH_EARLY_SCORE_V1 */
.finishEarlyControl{
  border:1px solid var(--line);
  background:var(--surface);
  border-radius:8px;
  display:flex;
  align-items:center;
  gap:5px;
  margin-left:auto;
  padding:4px 7px;
  color:var(--muted);
  text-transform:uppercase;
  letter-spacing:.05em;
  font-size:8px;
  font-weight:850;
  white-space:nowrap;
}
.finishEarlyControl span{color:var(--muted);font:inherit;letter-spacing:inherit;text-transform:inherit}
.finishEarlyControl input{
  width:42px;
  height:26px;
  min-height:26px;
  border:1px solid var(--line)!important;
  background:var(--input-bg)!important;
  color:var(--ink)!important;
  border-radius:6px;
  padding:3px 5px;
  text-align:center;
  font-size:10px;
  font-weight:850;
  outline:0;
}
.finishEarlyControl input:focus{border-color:var(--green)!important;box-shadow:0 0 0 2px color-mix(in srgb,var(--green) 15%,transparent)!important}
.finishEarlyControl em{color:var(--muted);font-style:normal;font-size:8px;font-weight:850}
.seasonDeadline>.finishEarlyControl+small{margin-left:0}
@media(max-width:700px){
  .seasonDeadline .finishEarlyControl{order:3;margin-left:0}
  .seasonDeadline #seasonRemaining{order:4;width:auto;margin-left:auto}
}
"""

index_path.write_text(index, encoding='utf-8')
runtime_path.write_text(runtime, encoding='utf-8')
css_path.write_text(css, encoding='utf-8')

print('finish-early planner patch applied')
