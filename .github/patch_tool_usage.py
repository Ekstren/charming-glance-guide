from pathlib import Path

p = Path("index.html")
s = p.read_text(encoding="utf-8")

start_marker = "  function setToolBalance(id,top,hardShort,yieldVal,label,protectedRuns=0){"
end_marker = "  function setRealmShortfallBreakdown"
start = s.index(start_marker)
end = s.index(end_marker, start)
replacement = r'''  function setToolBalance(id,top,hardShort,yieldVal,label,protectedRuns=0){
    const el=$(id); if(!el) return;
    el.classList.remove('toolNeed','toolLeft');
    const per=Math.max(0,Number(yieldVal)||0);
    const hard=Math.max(0,Number(hardShort)||0);
    const protectedCount=Math.max(0,Math.floor(Number(protectedRuns)||0));
    const materialName=label==='Hammers'?'Ore':label==='Knuckles'?'Essence':label==='Shovels'?'Sand':'materials';
    const requestedRuns=Number(top?.runsUsed);
    const maxRuns=Math.max(0,Math.floor(Number(top?.maxRuns)||0));
    let used=Math.max(0,Math.floor(Number.isFinite(requestedRuns)?requestedRuns:(hard>0.5?maxRuns:0)));
    if(maxRuns>0) used=Math.min(used,maxRuns);
    const gained=used*per;
    const bankedRemaining=Math.max(0,Math.floor(Number(top?.bankedRemaining)||0));
    const sparePurchased=Math.max(0,Math.floor(Number(top?.sparePurchasedRuns)||0));
    const remaining=bankedRemaining+sparePurchased+protectedCount;
    const remainingMaterial=remaining*per;
    const needed=hard>0.5&&per>0?Math.ceil(hard/per):0;
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

if 'id="tool-usage-alignment-v2"' not in s:
    css = r'''
<style id="tool-usage-alignment-v2">
.realmDailyInputs{align-items:start!important}
.realmDailyInputs label{display:grid!important;grid-template-rows:30px 46px auto!important;gap:5px!important;align-content:start!important}
.realmDailyInputs input{margin-top:0!important;height:46px!important}
.realmDailyInputs small{margin-top:0!important}
.planCosts small.toolBalance{display:grid!important;gap:4px!important;border-top:1px solid var(--line)!important;margin-top:3px!important;padding-top:7px!important}
.planCosts small.toolBalance>.toolUsageRow{display:grid!important;grid-template-columns:minmax(105px,1fr) minmax(38px,auto) minmax(100px,1.15fr)!important;align-items:baseline!important;gap:8px!important;border:0!important;background:transparent!important;border-radius:0!important;padding:0!important;min-height:0!important;text-transform:none!important}
.planCosts small.toolBalance>.toolUsageRow i,.planCosts small.toolBalance>.toolUsageRow em{font-style:normal!important}
.planCosts small.toolBalance>.toolUsageRow i{color:var(--secondary-text)!important;font-weight:750!important}
.planCosts small.toolBalance>.toolUsageRow b{font-size:9px!important;line-height:1.35!important;color:inherit!important;text-align:right!important}
.planCosts small.toolBalance>.toolUsageRow em{color:inherit!important;font-size:8.5px!important;font-weight:750!important;text-align:left!important}
.planCosts small.toolBalance>.toolRemainingLine{color:var(--status-positive)!important}
.planCosts small.toolBalance>.toolNeedLine{color:var(--status-negative)!important;font-weight:850!important;margin-top:2px!important}
@media(max-width:700px){.planCosts small.toolBalance>.toolUsageRow{grid-template-columns:minmax(110px,1fr) auto minmax(110px,1.2fr)!important}.realmDailyInputs label{grid-template-rows:32px 46px auto!important}}
</style>
'''
    s = s.replace("</head>", css + "</head>", 1)

p.write_text(s, encoding="utf-8")
