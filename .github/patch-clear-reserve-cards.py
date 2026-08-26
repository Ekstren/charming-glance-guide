from pathlib import Path

PATH=Path('index.html')
text=PATH.read_text(encoding='utf-8')
MARKER='TOOL_ONLY_RESOURCE_GAPS_V4'
if MARKER in text:
    print('Tool-only resource cards already applied.')
    raise SystemExit(0)

start=text.find('  /* POST_PLAN_RESERVE_BALANCE_LINES_V2 */')
end=text.find('  function setRealmShortfallBreakdown(', start)
if start<0 or end<0:
    raise SystemExit('reserve balance block not found')

new_block=r'''  /* TOOL_ONLY_RESOURCE_GAPS_V4
     S2 reserve math stays internal. On a feasible plan, result cards show no leftover or
     reserve bookkeeping. If Realm tools are actually consumed, show only total tools used,
     their approximate material value, and the tools left afterward with approximate value. */
  function hidePlanBalance(id){
    const el=$(id); if(!el) return;
    el.textContent=''; el.innerHTML=''; el.hidden=true;
    el.classList.remove('shortfallCount','shortfallBreakdown','reserveHasGap');
  }
  function setEssenceBalance(id,cost,resources){ hidePlanBalance(id); }
  function setSandBalance(id,cost,resources){ hidePlanBalance(id); }
  function setTreatBalance(id,cost,resources){
    const totalNeed=Math.max(0,Number(cost)||0)+Math.max(0,Number(resources?.s2FantomonTreatReserve?.target)||0);
    const available=Math.max(0,Number(resources?.treat)||0);
    const el=$(id); if(!el) return;
    if(totalNeed<=available+0.5){ hidePlanBalance(id); return; }
    const short=Math.ceil(totalNeed-available);
    el.hidden=false; el.textContent=`${fmt(short)} Treats short`; el.classList.add('shortfallCount');
  }

  function setBalance(id, cost, budget, yieldVal, itemName){
    const el=$(id); if(!el) return;
    const diff=budget-cost;
    el.classList.remove('shortfallCount','shortfallBreakdown');
    if(diff>=-0.5){ hidePlanBalance(id); return; }
    const short=Math.ceil(-diff);
    const count = yieldVal>0 ? Math.ceil(short/yieldVal) : 0;
    el.hidden=false;
    el.textContent=`${fmt(short)} short${count?` · ${fmt(count)} ${itemName}`:''}`;
    el.classList.add('shortfallCount');
  }

  function setToolBalance(id,top,hardShort,yieldVal,label,protectedRuns=0){
    const el=$(id); if(!el) return;
    el.classList.remove('toolNeed','toolLeft');
    const materialName=label==='Hammers'?'Ore':label==='Knuckles'?'Essence':label==='Shovels'?'Sand':'materials';
    const planRuns=Math.max(0,Math.floor(Number(top?.planRuns ?? top?.runsUsed)||0));
    const reserveRuns=Math.max(0,Math.floor(Number(top?.reserveRuns)||0));
    const totalRuns=Math.max(0,planRuns+reserveRuns);
    const planPer=Math.max(0,Number(top?.planPerRun ?? yieldVal)||0);
    const reservePer=Math.max(0,Number(top?.reservePerRun)||0);
    const gained=Math.max(0,planRuns*planPer+reserveRuns*reservePer);
    const left=Math.max(0,Math.floor(Number(top?.bankedRemaining)||0)+Math.floor(Number(top?.sparePurchasedRuns)||0));
    const leftPer=Math.max(0,Number(yieldVal)||0);
    const leftValue=left*leftPer;
    const required=Math.max(0,Math.floor(Number(top?.runsNeeded)||totalRuns));
    const maxRuns=Math.max(0,Math.floor(Number(top?.maxRuns)||0));
    const missing=Math.max(0,required-maxRuns);

    if(totalRuns<=0 && missing<=0){ el.innerHTML=''; el.hidden=true; return; }
    const lines=[];
    if(totalRuns>0){
      lines.push(`<span class="toolUsageRow toolUsedLine"><i>Use</i><b>${fmt(totalRuns)} ${label}</b><em>${gained>0?`≈${fmtCompact(gained)} ${materialName}`:''}</em></span>`);
      lines.push(`<span class="toolUsageRow toolRemainingLine"><i>Left</i><b>${fmt(left)} ${label}</b><em>${leftValue>0?`≈${fmtCompact(leftValue)} ${materialName}`:'≈0'}</em></span>`);
    }
    if(missing>0) lines.push(`<span class="toolUsageRow toolNeedLine"><i>Still short</i><b>${fmt(missing)} ${label}</b><em></em></span>`);
    el.hidden=false; el.innerHTML=lines.join('');
    el.classList.add(missing?'toolNeed':'toolLeft');
  }
'''
text=text[:start]+new_block+text[end:]

# Keep reserves controllable, but remove reserve bookkeeping from the visible calculator UI.
text=text.replace("if(cfg.key==='s1') brief.push(optimizerReserveSummary(resources,cfg));", "/* TOOL_ONLY_RESOURCE_GAPS_V4: reserve math intentionally hidden from result summary */")
text=text.replace("const reserveSuffix=(sr?.target||0)>0?` · ${fmtCompact(sr.target)} S2 skill reserve`:'';", "const reserveSuffix='';")
text=text.replace("const sandReserveSuffix=(resources.s2RelicSandReserve?.target||0)>0?` · ${fmtCompact(resources.s2RelicSandReserve.target)} S2 relic reserve`:'';", "const sandReserveSuffix='';")
text=text.replace("const treatReserveSuffix=(tr?.target||0)>0?` · ${fmtCompact(tr.target)} S2 pet reserve`:'';", "const treatReserveSuffix='';")

css=r'''
<style id="tool-only-resource-gaps-v4">
/* TOOL_ONLY_RESOURCE_GAPS_V4 */
#s2SkillReserveHint,#s2RelicReserveHint,#s2TreatReserveHint{display:none!important}
.planCosts small[id$="Balance"]:empty{display:none!important}
.planCosts small.toolBalance{
  display:grid!important;gap:0!important;margin-top:7px!important;padding-top:7px!important;
  border-top:1px solid var(--line)!important;color:var(--secondary-text)!important
}
.planCosts small.toolBalance[hidden]{display:none!important}
.planCosts small.toolBalance .toolUsageRow{
  display:grid!important;grid-template-columns:minmax(0,1fr) auto!important;
  gap:2px 10px!important;align-items:center!important;padding:4px 0!important
}
.planCosts small.toolBalance .toolUsageRow i{
  color:var(--secondary-text)!important;font-style:normal!important;font-weight:700!important;
  text-transform:none!important;letter-spacing:0!important
}
.planCosts small.toolBalance .toolUsageRow b{font-weight:850!important;white-space:nowrap!important}
.planCosts small.toolBalance .toolUsageRow em{
  grid-column:2!important;color:var(--secondary-text)!important;font-style:normal!important;
  font-size:8px!important;text-align:right!important
}
.planCosts small.toolBalance .toolUsedLine b{color:var(--status-info)!important}
.planCosts small.toolBalance .toolRemainingLine b{color:var(--status-positive)!important}
.planCosts small.toolBalance .toolNeedLine b{color:var(--status-negative)!important}
@media(max-width:520px){.planCosts small.toolBalance .toolUsageRow{font-size:10px!important}.planCosts small.toolBalance .toolUsageRow em{font-size:9px!important}}
</style>
'''
insert=text.rfind('</head>')
if insert<0: raise SystemExit('</head> not found')
text=text[:insert]+css+'\n'+text[insert:]
PATH.write_text(text,encoding='utf-8')
print('Applied tool-only resource cards; reserve math remains internal.')
