from pathlib import Path

PATH = Path('index.html')
s = PATH.read_text(encoding='utf-8')

CSS_MARKER = 'RESULT_STAMINA_PROJECTION_V1'
JS_MARKER = 'RESULT_STAMINA_PROJECTION_V1'

css = r'''<style id="result-stamina-projection-v1">
/* RESULT_STAMINA_PROJECTION_V1
   Mirror the optimizer's Stamina allocation inside the right-side material result cards,
   directly below the Material Realm tool actions. This keeps the recommended farming
   target visible even when Material Realm is closed. */
.planCosts small.toolBalance .toolSimpleLine.staminaProjectionLine,
.planCosts small.toolBalance .toolSimpleLine.staminaProjectionLine i,
.planCosts small.toolBalance .toolSimpleLine.staminaProjectionLine b,
.planCosts small.toolBalance .toolSimpleLine.staminaProjectionLine b em{
  color:var(--status-info,var(--blue))!important;
}
.planCosts small.toolBalance .toolSimpleLine.staminaProjectionLine{
  margin-top:4px!important;
  padding-top:4px!important;
  border-top:1px dashed color-mix(in srgb,var(--line) 78%,transparent)!important;
}
</style>
'''

if CSS_MARKER not in s:
    head_anchor = '</head>'
    if s.count(head_anchor) != 1:
        raise SystemExit(f'Expected one </head> anchor, found {s.count(head_anchor)}')
    s = s.replace(head_anchor, css + head_anchor, 1)

helper_anchor = """    el.innerHTML=lines.join('');
    el.classList.add((missing>0||dailyGapRuns>0)?'toolNeed':'toolLeft');
  }
  /* RICH_RESOURCE_SHORTFALL_NO_DUPLICATE_V1
"""
helper_replacement = """    el.innerHTML=lines.join('');
    el.classList.add((missing>0||dailyGapRuns>0)?'toolNeed':'toolLeft');
  }

  // RESULT_STAMINA_PROJECTION_V1: repeat the optimizer's Stamina target in the
  // right-side resource cards so the next farming target remains obvious when Realm is closed.
  function appendStaminaProjection(id,nodes,gain,materialName){
    const el=$(id); if(!el) return;
    const count=Math.max(0,Math.floor(Number(nodes)||0));
    const value=Math.max(0,Number(gain)||0);
    if(count<=0) return;
    const line=document.createElement('div');
    line.className='toolSimpleLine staminaProjectionLine';
    line.innerHTML=`<i>Stamina:</i><b>${fmt(count)}${value>0?` <em>→ +${fmtCompact(value)} ${materialName}</em>`:''}</b>`;
    el.appendChild(line);
    el.hidden=false;
    if(!el.classList.contains('toolNeed')) el.classList.add('toolLeft');
  }
  /* RICH_RESOURCE_SHORTFALL_NO_DUPLICATE_V1
"""

if 'function appendStaminaProjection' not in s:
    if s.count(helper_anchor) != 1:
        raise SystemExit(f'Expected one helper anchor, found {s.count(helper_anchor)}')
    s = s.replace(helper_anchor, helper_replacement, 1)

call_anchor = """    setToolBalance('oreToolBalance',plan.realm?.ore,oreHardShort,oreYield,'Hammers',0,rawOreRemaining);
    setToolBalance('essenceToolBalance',plan.realm?.essence,essHardShort,essenceYield,'Knuckles',resources.s2SkillReserve?.knucklesReserved||0,rawEssenceRemaining);
    setToolBalance('sandToolBalance',plan.realm?.sand,sandHardShort,sandYield,'Shovels',resources.s2RelicSandReserve?.shovelsReserved||0,rawSandRemaining);

    renderRealmDailyRecommendations(plan,resources,cfg);
"""
call_replacement = """    setToolBalance('oreToolBalance',plan.realm?.ore,oreHardShort,oreYield,'Hammers',0,rawOreRemaining);
    setToolBalance('essenceToolBalance',plan.realm?.essence,essHardShort,essenceYield,'Knuckles',resources.s2SkillReserve?.knucklesReserved||0,rawEssenceRemaining);
    setToolBalance('sandToolBalance',plan.realm?.sand,sandHardShort,sandYield,'Shovels',resources.s2RelicSandReserve?.shovelsReserved||0,rawSandRemaining);
    appendStaminaProjection('oreToolBalance',allocation.ore,added.ore,'Ore');
    appendStaminaProjection('essenceToolBalance',allocation.essence,added.essence,'Essence');
    appendStaminaProjection('sandToolBalance',allocation.sand,added.sand,'Sand');

    renderRealmDailyRecommendations(plan,resources,cfg);
"""

if "appendStaminaProjection('oreToolBalance'" not in s:
    if s.count(call_anchor) != 1:
        raise SystemExit(f'Expected one call anchor, found {s.count(call_anchor)}')
    s = s.replace(call_anchor, call_replacement, 1)

required = [
    CSS_MARKER,
    'function appendStaminaProjection',
    "appendStaminaProjection('oreToolBalance',allocation.ore,added.ore,'Ore')",
    "appendStaminaProjection('essenceToolBalance',allocation.essence,added.essence,'Essence')",
    "appendStaminaProjection('sandToolBalance',allocation.sand,added.sand,'Sand')",
    '<i>Stamina:</i>',
]
missing = [x for x in required if x not in s]
if missing:
    raise SystemExit(f'Missing expected result stamina projection pieces: {missing}')

PATH.write_text(s, encoding='utf-8')
print('Applied right-side Stamina projection lines to Ore, Essence, and Sand result cards.')
