from pathlib import Path

path=Path('index.html')
text=path.read_text(encoding='utf-8')
marker='HIDE_RESERVE_TOOLS_WHEN_RAW_REMAINS_V1'
if marker in text:
    print('Raw-remains tool display patch already applied.')
    raise SystemExit(0)

old_sig="  function setToolBalance(id,top,hardShort,yieldVal,label,protectedRuns=0){"
new_sig="  function setToolBalance(id,top,hardShort,yieldVal,label,protectedRuns=0,rawRemaining=0){"
if text.count(old_sig)!=1:
    raise SystemExit(f'setToolBalance signature count={text.count(old_sig)}')
text=text.replace(old_sig,new_sig,1)

old_hide="""    // TOOL_DAILY_GAP_V13 · TOOLS_FIRST_S2_RESERVES_V1: reserve-only tools stay visible
    // so it is clear which entries are being held for S2. With reserves off and no S1
    // shortage, the tool row remains hidden.
    if(planRuns<=0 && reserveRuns<=0 && missing<=0){ el.innerHTML=''; el.hidden=true; return; }
"""
new_hide="""    // TOOL_DAILY_GAP_V13 · TOOLS_FIRST_S2_RESERVES_V1 · HIDE_RESERVE_TOOLS_WHEN_RAW_REMAINS_V1
    // Result cards are about what the S1 upgrade plan actually needs. If raw material still
    // remains and no Realm tool is required for the S1 spend, hide reserve-only tool counts;
    // the Material Realm panel remains the place to inspect the carried S2 tool reserve.
    // If a tool was genuinely needed to bridge a raw shortage, keep showing Use/Need even
    // when the final Realm conversion leaves a small raw overage from whole-tool rounding.
    const visibleRawRemaining=Math.max(0,Number(rawRemaining)||0);
    if(planRuns<=0 && missing<=0 && (reserveRuns<=0 || visibleRawRemaining>0.5)){ el.innerHTML=''; el.hidden=true; return; }
"""
if text.count(old_hide)!=1:
    raise SystemExit(f'tool hide block count={text.count(old_hide)}')
text=text.replace(old_hide,new_hide,1)

old_calls="""    setToolBalance('oreToolBalance',plan.realm?.ore,oreHardShort,oreYield,'Hammers');
    setToolBalance('essenceToolBalance',plan.realm?.essence,essHardShort,essenceYield,'Knuckles',resources.s2SkillReserve?.knucklesReserved||0);
    setToolBalance('sandToolBalance',plan.realm?.sand,sandHardShort,sandYield,'Shovels',resources.s2RelicSandReserve?.shovelsReserved||0);
"""
new_calls="""    const rawOreRemaining=Math.max(0,(Number(resources.ore)||0)-(Number(plan.oreCost)||0));
    const rawEssenceRemaining=Math.max(0,(Number(resources.essenceTotal??resources.essence)||0)-(Number(plan.essenceCost)||0));
    const rawSandRemaining=Math.max(0,(Number(resources.sandTotal??resources.sand)||0)-(Number(plan.sandCost)||0));
    setToolBalance('oreToolBalance',plan.realm?.ore,oreHardShort,oreYield,'Hammers',0,rawOreRemaining);
    setToolBalance('essenceToolBalance',plan.realm?.essence,essHardShort,essenceYield,'Knuckles',resources.s2SkillReserve?.knucklesReserved||0,rawEssenceRemaining);
    setToolBalance('sandToolBalance',plan.realm?.sand,sandHardShort,sandYield,'Shovels',resources.s2RelicSandReserve?.shovelsReserved||0,rawSandRemaining);
"""
if text.count(old_calls)!=1:
    raise SystemExit(f'setToolBalance call block count={text.count(old_calls)}')
text=text.replace(old_calls,new_calls,1)

path.write_text(text,encoding='utf-8')
print('Applied raw-remains tool display rule.')
