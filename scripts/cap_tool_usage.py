from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')
start = s.index('  function setToolBalance(id,top,hardShort,yieldVal,label,protectedRuns=0){')
end = s.index('  function setRealmShortfallBreakdown', start)
replacement = '''  function setToolBalance(id,top,hardShort,yieldVal,label,protectedRuns=0){
    const el=$(id); if(!el) return;
    el.classList.remove('toolNeed','toolLeft');
    const per=Math.max(0,Number(yieldVal)||0);
    const hard=Math.max(0,Number(hardShort)||0);
    const key=label==='Hammers'?'ore':label==='Knuckles'?'essence':label==='Shovels'?'sand':null;
    const inv=key?realmInventoryFor(key,activeCalcConfig()):null;
    const protectedCount=Math.max(0,Math.floor(Number(inv?.protectedRuns??protectedRuns)||0));
    const materialName=label==='Hammers'?'Ore':label==='Knuckles'?'Essence':label==='Shovels'?'Sand':'materials';
    const finiteRuns=Number(top?.runsUsed);
    const maxRuns=Math.max(0,Math.floor(Number(top?.maxRuns)||0));
    const hardNeedRuns=hard>0.5&&per>0?Math.ceil(hard/per):0;
    const desiredRuns=Math.max(0,Math.floor(Number.isFinite(finiteRuns)?finiteRuns:(hard>0.5?maxRuns+hardNeedRuns:0)));
    const projectedSpendable=Math.max(0,Math.floor(Number(inv?.banked)||0));
    const used=Math.min(desiredRuns,projectedSpendable);
    const gained=used*per;
    const spendableRemaining=Math.max(0,projectedSpendable-used);
    const remaining=spendableRemaining+protectedCount;
    const remainingMaterial=remaining*per;
    const needed=Math.max(0,desiredRuns-used);
    const neededMaterial=needed*per;
    const protectedText=protectedCount?` · ${fmt(protectedCount)} S2-protected`:'';
    const usedLine=`<span class="toolUsageRow toolUsedLine"><i>${label} used</i><b>${fmt(used)}</b><em>${per>0?`≈${fmtCompact(gained)} ${materialName} gained`:''}</em></span>`;
    const remainingLine=`<span class="toolUsageRow toolRemainingLine"><i>${label} remaining</i><b>${fmt(remaining)}</b><em>${per>0?`≈${fmtCompact(remainingMaterial)} ${materialName}`:''}${protectedText}</em></span>`;
    const needLine=needed?`<span class="toolUsageRow toolNeedLine"><i>Need more</i><b>${fmt(needed)}</b><em>≈${fmtCompact(neededMaterial)} ${materialName}</em></span>`:'';
    el.innerHTML=usedLine+remainingLine+needLine;
    el.classList.add(needed?'toolNeed':'toolLeft');
  }
'''
s = s[:start] + replacement + s[end:]
p.write_text(s, encoding='utf-8')
