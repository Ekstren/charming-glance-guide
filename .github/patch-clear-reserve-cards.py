from pathlib import Path

PATH=Path('index.html')
text=PATH.read_text(encoding='utf-8')
MARKER='CLEAR_RESERVE_CARD_ROWS_V3'
if MARKER in text:
    print('Clear reserve card rows already applied.')
    raise SystemExit(0)

start=text.find('  /* POST_PLAN_RESERVE_BALANCE_LINES_V2 */')
end=text.find('  function setRealmShortfallBreakdown(', start)
if start<0 or end<0:
    raise SystemExit('reserve balance block not found')

new_block=r'''  /* CLEAR_RESERVE_CARD_ROWS_V3
     Keep the result cards literal: show raw remaining after the S1 plan, the S2 reserve
     target, then either free raw after that reserve or the exact reserve shortfall.
     Realm tools stay on their own line and appear only when they actually cover a gap. */
  function setReserveAwareBalance(id,cost,rawBudget,reserveTarget,label){
    const el=$(id); if(!el) return;
    const raw=Math.max(0,Number(rawBudget)||0);
    const spend=Math.max(0,Number(cost)||0);
    const target=Math.max(0,Number(reserveTarget)||0);
    const rawAfterPlan=Math.max(0,raw-spend);
    const reserveFromRaw=Math.min(target,rawAfterPlan);
    const reserveGap=Math.max(0,target-reserveFromRaw);
    const freeAfterReserve=Math.max(0,rawAfterPlan-reserveFromRaw);
    const rows=[];
    rows.push(`<span class="reserveBalanceLine reserveAfterPlan"><i>After S1 plan</i><b>${fmt(rawAfterPlan)} ${label}</b></span>`);
    if(target>0){
      rows.push(`<span class="reserveBalanceLine reserveTargetLine"><i>S2 reserve target</i><b>${fmt(target)} ${label}</b></span>`);
      if(reserveGap>0){
        rows.push(`<span class="reserveBalanceLine reserveGapLine"><i>Reserve shortfall</i><b>${fmt(reserveGap)} ${label}</b></span>`);
      }else{
        rows.push(`<span class="reserveBalanceLine reserveFreeLine"><i>Free after reserve</i><b>${fmt(freeAfterReserve)} ${label}</b></span>`);
      }
    }
    el.innerHTML=rows.join('');
    el.classList.remove('shortfallCount','shortfallBreakdown');
    el.classList.toggle('reserveHasGap',reserveGap>0);
  }
  function setEssenceBalance(id,cost,resources){
    const planGenerated=Math.max(0,Number(resources?.planRealmProvided)||0);
    setReserveAwareBalance(id,cost,Math.max(0,Number(resources.essence)||0)+planGenerated,resources.s2SkillReserve?.target,'Essence');
  }
  function setSandBalance(id,cost,resources){
    const planGenerated=Math.max(0,Number(resources?.planRealmProvided)||0);
    setReserveAwareBalance(id,cost,Math.max(0,Number(resources.sand)||0)+planGenerated,resources.s2RelicSandReserve?.target,'Sand');
  }
  function setTreatBalance(id,cost,resources){
    setReserveAwareBalance(id,cost,resources.treat,resources.s2FantomonTreatReserve?.target,'basic-eq.');
  }

  function setBalance(id, cost, budget, yieldVal, itemName){
    const el=$(id);
    const diff=budget-cost;
    el.classList.remove('shortfallCount','shortfallBreakdown');
    if(diff>=-0.5){
      el.textContent=`${fmt(Math.max(0,diff))} spendable after plan`;
    } else {
      const short=Math.ceil(-diff);
      const count = yieldVal>0 ? Math.ceil(short/yieldVal) : 0;
      el.textContent=`${fmt(short)} short${count?` · ${fmt(count)} ${itemName}`:''}`;
      el.classList.add('shortfallCount');
    }
  }
  function setToolBalance(id,top,hardShort,yieldVal,label,protectedRuns=0){
    const el=$(id); if(!el) return;
    el.classList.remove('toolNeed','toolLeft');
    const materialName=label==='Hammers'?'Ore':label==='Knuckles'?'Essence':label==='Shovels'?'Sand':'materials';
    const planRuns=Math.max(0,Math.floor(Number(top?.planRuns ?? top?.runsUsed)||0));
    const reserveRuns=Math.max(0,Math.floor(Number(top?.reserveRuns)||0));
    const planPer=Math.max(0,Number(top?.planPerRun ?? yieldVal)||0);
    const reservePer=Math.max(0,Number(top?.reservePerRun)||0);
    const lines=[];
    if(planRuns>0) lines.push(`<span class="toolUsageRow toolUsedLine"><i>Cover S1 gap with</i><b>${fmt(planRuns)} ${label}</b><em>${planPer>0?`≈${fmtCompact(planRuns*planPer)} ${materialName}`:''}</em></span>`);
    if(reserveRuns>0) lines.push(`<span class="toolUsageRow toolReserveLine"><i>Cover reserve gap with</i><b>${fmt(reserveRuns)} ${label}</b><em>${reservePer>0?`≈${fmtCompact(reserveRuns*reservePer)} ${materialName}`:''}</em></span>`);
    const required=Math.max(0,planRuns+reserveRuns);
    const maxRuns=Math.max(0,Math.floor(Number(top?.maxRuns)||0));
    const missing=Math.max(0,required-maxRuns);
    if(missing>0) lines.push(`<span class="toolUsageRow toolNeedLine"><i>Still short</i><b>${fmt(missing)} ${label}</b><em></em></span>`);
    if(!lines.length){el.innerHTML='';el.hidden=true;return;}
    el.hidden=false;
    el.innerHTML=lines.join('');
    el.classList.add(missing?'toolNeed':'toolLeft');
  }
'''
text=text[:start]+new_block+text[end:]

css=r'''
<style id="clear-reserve-card-rows-v3">
/* CLEAR_RESERVE_CARD_ROWS_V3 */
.planCosts small[id$="Balance"]:has(.reserveBalanceLine){
  display:grid!important;
  gap:0!important;
  margin-top:8px!important;
  padding:0!important;
  border:0!important;
  background:none!important;
}
.planCosts .reserveBalanceLine{
  display:flex!important;
  align-items:center!important;
  justify-content:space-between!important;
  gap:12px!important;
  min-height:27px!important;
  padding:5px 0!important;
  border:0!important;
  border-bottom:1px solid color-mix(in srgb,var(--line) 62%,transparent)!important;
  border-radius:0!important;
  background:none!important;
  box-shadow:none!important;
  text-transform:none!important;
  letter-spacing:0!important;
  font-size:9px!important;
  line-height:1.3!important;
}
.planCosts .reserveBalanceLine:last-child{border-bottom:0!important}
.planCosts .reserveBalanceLine i{
  color:var(--secondary-text)!important;
  font-style:normal!important;
  font-weight:700!important;
  text-transform:none!important;
  letter-spacing:0!important;
}
.planCosts .reserveBalanceLine b{
  color:var(--status-positive)!important;
  font-size:10px!important;
  font-weight:850!important;
  text-align:right!important;
  white-space:nowrap!important;
}
.planCosts .reserveGapLine b{color:var(--status-warning)!important}
.planCosts small.toolBalance{
  display:grid!important;
  gap:0!important;
  margin-top:6px!important;
  padding-top:6px!important;
  border-top:1px solid var(--line)!important;
}
.planCosts small.toolBalance .toolUsageRow{
  display:grid!important;
  grid-template-columns:minmax(0,1fr) auto!important;
  gap:2px 10px!important;
  align-items:center!important;
  padding:4px 0!important;
}
.planCosts small.toolBalance .toolUsageRow i{
  color:var(--secondary-text)!important;
  font-style:normal!important;
  font-weight:700!important;
  text-transform:none!important;
}
.planCosts small.toolBalance .toolUsageRow b{font-weight:850!important;white-space:nowrap!important}
.planCosts small.toolBalance .toolUsageRow em{
  grid-column:2!important;
  color:var(--secondary-text)!important;
  font-style:normal!important;
  font-size:8px!important;
  text-align:right!important;
}
.planCosts small.toolBalance .toolReserveLine b{color:var(--status-warning)!important}
@media(max-width:520px){
  .planCosts .reserveBalanceLine{font-size:10px!important;min-height:30px!important}
  .planCosts .reserveBalanceLine b{font-size:10px!important}
}
</style>
'''
insert=text.rfind('</head>')
if insert<0:
    raise SystemExit('</head> not found')
text=text[:insert]+css+'\n'+text[insert:]
PATH.write_text(text,encoding='utf-8')
print('Applied clearer reserve card rows.')
