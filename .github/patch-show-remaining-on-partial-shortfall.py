from pathlib import Path

path=Path('index.html')
text=path.read_text(encoding='utf-8')
marker='PARTIAL_SHORTFALL_SHOW_REMAINING_V1'
if marker in text:
    print('Partial-shortfall remaining display already applied.')
    raise SystemExit(0)

old="""    if(resourceBlocked){
      setRealmShortfallBreakdown('oreBalance',orePlanShort,oreYield,'Hammers',plan.realm?.ore?.maxPurchasedRuns,oreHardShort,'Ore');
      setRealmShortfallBreakdown('essenceBalance',essPlanShort,essenceYield,'Knuckles',plan.realm?.essence?.maxPurchasedRuns,essHardShort,'Essence',(resources.s2SkillReserve?.rawEssence||0)>0?` · S2 raw reserve: ${fmt(resources.s2SkillReserve.rawEssence)} Essence`:'');
      setRealmShortfallBreakdown('sandBalance',sandPlanShort,sandYield,'Shovels',plan.realm?.sand?.maxPurchasedRuns,sandHardShort,'Sand',(resources.s2RelicSandReserve?.rawSand||0)>0?` · S2 raw reserve: ${fmt(resources.s2RelicSandReserve.rawSand)} Sand`:'');
      setTreatBalance('treatBalance',plan.treatCost,resources);
"""
new="""    if(resourceBlocked){
      /* PARTIAL_SHORTFALL_SHOW_REMAINING_V1
         A target can be impossible because ONE resource is exhausted while the other cards
         still have plenty left. Only show a shortage breakdown on resources that are actually
         short under the selected daily plan; otherwise keep the normal Remaining display. */
      if(orePlanShort>0.5) setRealmShortfallBreakdown('oreBalance',orePlanShort,oreYield,'Hammers',plan.realm?.ore?.maxPurchasedRuns,oreHardShort,'Ore');
      else setRawRemaining('oreBalance',plan.oreCost,resources.ore);
      if(essPlanShort>0.5) setRealmShortfallBreakdown('essenceBalance',essPlanShort,essenceYield,'Knuckles',plan.realm?.essence?.maxPurchasedRuns,essHardShort,'Essence',(resources.s2SkillReserve?.rawEssence||0)>0?` · S2 raw reserve: ${fmt(resources.s2SkillReserve.rawEssence)} Essence`:'');
      else setEssenceBalance('essenceBalance',plan.essenceCost,{...resources,planRealmProvided:plan.realm?.essence?.planProvided||0});
      if(sandPlanShort>0.5) setRealmShortfallBreakdown('sandBalance',sandPlanShort,sandYield,'Shovels',plan.realm?.sand?.maxPurchasedRuns,sandHardShort,'Sand',(resources.s2RelicSandReserve?.rawSand||0)>0?` · S2 raw reserve: ${fmt(resources.s2RelicSandReserve.rawSand)} Sand`:'');
      else setSandBalance('sandBalance',plan.sandCost,{...resources,planRealmProvided:plan.realm?.sand?.planProvided||0});
      setTreatBalance('treatBalance',plan.treatCost,resources);
"""
if text.count(old)!=1:
    raise SystemExit(f'Expected one resourceBlocked card anchor, found {text.count(old)}')
text=text.replace(old,new,1)
path.write_text(text,encoding='utf-8')
print('Show Remaining on non-short resource cards even when another resource blocks the target.')
