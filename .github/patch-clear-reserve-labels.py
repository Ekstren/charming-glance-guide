from pathlib import Path

PATH = Path('index.html')
text = PATH.read_text(encoding='utf-8')
MARKER = 'CLEAR_RESERVE_BALANCE_LABELS_V1'
if MARKER in text:
    print('Reserve balance labels already clarified.')
    raise SystemExit(0)

# 1) Clarify normal raw-resource balances and show only ACTUAL raw reserve, not the total
# reserve target when tools are covering it.
start = text.find('  function setEssenceBalance(id,cost,resources){')
end = text.find('  function setBalance(id, cost, budget, yieldVal, itemName){', start)
if start < 0 or end < 0:
    raise SystemExit('balance helper block not found')

new_helpers = r'''  /* CLEAR_RESERVE_BALANCE_LABELS_V1
     Result cards distinguish S1-spendable raw material from actual raw S2 reserve.
     Tool-covered reserve is shown on the tool rows instead of being repeated as if raw
     Essence/Sand were locked. */
  function appendActualRawReserve(id,amount,label){
    const value=Math.max(0,Number(amount)||0);
    if(value<=0) return;
    const el=$(id); if(!el) return;
    el.textContent += ` · S2 raw reserve: ${fmt(value)} ${label}`;
  }
  function setEssenceBalance(id,cost,resources){
    setBalance(id,cost,resources.essence,resources.yields.essencePerKnuckles,'Knuckles');
    appendActualRawReserve(id,resources.s2SkillReserve?.rawEssence,'Essence');
  }
  function setSandBalance(id,cost,resources){
    setBalance(id,cost,resources.sand,resources.yields.sandPerShovel,'Shovels');
    appendActualRawReserve(id,resources.s2RelicSandReserve?.rawSand,'Sand');
  }
  function setTreatBalance(id,cost,resources){
    setBalance(id,cost,resources.treat,1,'basic-eq.');
    appendActualRawReserve(id,resources.s2FantomonTreatReserve?.rawTreats,'basic-eq.');
  }

'''
text = text[:start] + new_helpers + text[end:]

old = "      el.textContent=`${fmt(Math.max(0,diff))} left`;"
new = "      el.textContent=`${fmt(Math.max(0,diff))} spendable after plan`;"
if text.count(old) != 1:
    raise SystemExit(f'setBalance normal label count={text.count(old)}')
text = text.replace(old,new,1)

# 2) Split tool inventory into S1-available and S2-reserved rows.
old_tool = r'''    const spendableRemaining=Math.max(0,projectedSpendable-used);
    const remaining=spendableRemaining+protectedCount;
    const remainingMaterial=remaining*per;
    const needed=Math.max(0,desiredRuns-used);
    const neededMaterial=needed*per;
    const protectedText=protectedCount?` · ${fmt(protectedCount)} S2-protected`:'';
    const usedLine=`<span class="toolUsageRow toolUsedLine"><i>${label} used</i><b>${fmt(used)}</b><em>${per>0?`≈${fmtCompact(gained)} ${materialName} gained`:''}</em></span>`;
    const remainingLine=`<span class="toolUsageRow toolRemainingLine"><i>${label} remaining</i><b>${fmt(remaining)}</b><em>${per>0?`≈${fmtCompact(remainingMaterial)} ${materialName}`:''}${protectedText}</em></span>`;
    const needLine=needed?`<span class="toolUsageRow toolNeedLine"><i>Need more</i><b>${fmt(needed)}</b><em>≈${fmtCompact(neededMaterial)} ${materialName}</em></span>`:'';
    el.innerHTML=usedLine+remainingLine+needLine;
'''
new_tool = r'''    const spendableRemaining=Math.max(0,projectedSpendable-used);
    const spendableMaterial=spendableRemaining*per;
    const protectedMaterial=protectedCount*per;
    const needed=Math.max(0,desiredRuns-used);
    const neededMaterial=needed*per;
    const usedLine=`<span class="toolUsageRow toolUsedLine"><i>${label} used</i><b>${fmt(used)}</b><em>${per>0?`≈${fmtCompact(gained)} ${materialName} gained`:''}</em></span>`;
    const remainingLabel=protectedCount?'S1 available':`${label} remaining`;
    const remainingLine=`<span class="toolUsageRow toolRemainingLine"><i>${remainingLabel}</i><b>${fmt(spendableRemaining)}</b><em>${per>0?`≈${fmtCompact(spendableMaterial)} ${materialName}`:''}</em></span>`;
    const reserveLine=protectedCount?`<span class="toolUsageRow toolReserveLine"><i>S2 reserved</i><b>${fmt(protectedCount)}</b><em>${per>0?`≈${fmtCompact(protectedMaterial)} ${materialName}`:''}</em></span>`:'';
    const needLine=needed?`<span class="toolUsageRow toolNeedLine"><i>Need more</i><b>${fmt(needed)}</b><em>≈${fmtCompact(neededMaterial)} ${materialName}</em></span>`:'';
    el.innerHTML=usedLine+remainingLine+reserveLine+needLine;
'''
if text.count(old_tool) != 1:
    raise SystemExit(f'tool balance block count={text.count(old_tool)}')
text = text.replace(old_tool,new_tool,1)

# 3) Shortfall cards should also reference only actual raw reserve.
old_ess = "setRealmShortfallBreakdown('essenceBalance',essPlanShort,essenceYield,'Knuckles',plan.realm?.essence?.maxPurchasedRuns,essHardShort,'Essence',(resources.s2SkillReserve?.target||0)>0?`${fmt(resources.s2SkillReserve.target)} S2 skill reserve protected`:'');"
new_ess = "setRealmShortfallBreakdown('essenceBalance',essPlanShort,essenceYield,'Knuckles',plan.realm?.essence?.maxPurchasedRuns,essHardShort,'Essence',(resources.s2SkillReserve?.rawEssence||0)>0?` · S2 raw reserve: ${fmt(resources.s2SkillReserve.rawEssence)} Essence`:'');"
if text.count(old_ess) != 1:
    raise SystemExit(f'ess shortfall label count={text.count(old_ess)}')
text = text.replace(old_ess,new_ess,1)

old_sand = "setRealmShortfallBreakdown('sandBalance',sandPlanShort,sandYield,'Shovels',plan.realm?.sand?.maxPurchasedRuns,sandHardShort,'Sand',resources.s2RelicSandReserve?.target?` · ${fmt(resources.s2RelicSandReserve.target)} S2 relic reserve protected`:'');"
new_sand = "setRealmShortfallBreakdown('sandBalance',sandPlanShort,sandYield,'Shovels',plan.realm?.sand?.maxPurchasedRuns,sandHardShort,'Sand',(resources.s2RelicSandReserve?.rawSand||0)>0?` · S2 raw reserve: ${fmt(resources.s2RelicSandReserve.rawSand)} Sand`:'');"
if text.count(old_sand) != 1:
    raise SystemExit(f'sand shortfall label count={text.count(old_sand)}')
text = text.replace(old_sand,new_sand,1)

PATH.write_text(text,encoding='utf-8')
print('Clarified raw reserve and tool availability labels.')
