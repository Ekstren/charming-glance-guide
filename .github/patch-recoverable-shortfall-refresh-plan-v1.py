from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
marker='RECOVERABLE_SHORTFALL_REFRESH_PLAN_V1'
if marker in s:
    print('already applied')
    raise SystemExit(0)

old="""    const line1=`${fmt(short)} ${resourceName} short`;
    let line2='';
    if(extraRuns>0 && per>0){
      line2=`Extra ${itemName} can cover requirements`;
    }
    el.innerHTML=`<span class=\"planShort\">${line1}</span>${line2?`<span class=\"realmBridge\">${line2}</span>`:''}${appendText?`<span>${appendText}</span>`:''}`;
"""
new="""    /* RECOVERABLE_SHORTFALL_REFRESH_PLAN_V1
       Recoverable resource cards show the exact material gap and additional tool count.
       Once the combined daily Realm recommendation is known later in updateCalculator(),
       the yellow bridge line is replaced with that resource's actionable refreshes/day. */
    const line1=`${fmt(short)} ${resourceName} short${runsToCover?` · ${fmt(runsToCover)} ${itemName} needed`:''}`;
    let line2='';
    if(extraRuns>0 && per>0){
      line2=`${fmt(runsToCover)} ${itemName} can cover`;
    }
    el.dataset.shortfallTools=String(runsToCover||0);
    el.dataset.shortfallItem=itemName;
    el.dataset.shortfallResource=resourceName;
    el.innerHTML=`<span class=\"planShort\">${line1}</span>${line2?`<span class=\"realmBridge\">${line2}</span>`:''}${appendText?`<span>${appendText}</span>`:''}`;
"""
if old not in s:
    raise SystemExit('Could not find recoverable shortfall renderer')
s=s.replace(old,new,1)

needle="""      const dailyPreset={ore:realmDailyValue('ore'),essence:realmDailyValue('essence'),sand:realmDailyValue('sand')};
      const dailySuggested=suggestedRealmDailyPlan(plan,cfg);
"""
insert="""      const dailyPreset={ore:realmDailyValue('ore'),essence:realmDailyValue('essence'),sand:realmDailyValue('sand')};
      const dailySuggested=suggestedRealmDailyPlan(plan,cfg);
      // RECOVERABLE_SHORTFALL_REFRESH_PLAN_V1: put the resource-specific action directly
      // on each recoverable shortage card. dailySuggested values are refreshes/day, while
      // the first line keeps the exact number of additional Realm tools needed overall.
      const applyShortfallRefreshPlan=(id,key,realmLabel)=>{
        const el=$(id);
        if(!el || !el.classList.contains('shortfallBreakdown') || el.querySelector('.hardShort')) return;
        const bridge=el.querySelector('.realmBridge');
        if(!bridge) return;
        const recommended=Math.max(0,Math.floor(Number(dailySuggested?.[key])||0));
        const current=Math.max(0,Math.floor(Number(dailyPreset?.[key])||0));
        const tools=Math.max(0,Math.ceil(Number(el.dataset.shortfallTools)||0));
        const item=el.dataset.shortfallItem||'tools';
        if(recommended>current){
          bridge.textContent=`Recommended: ${fmt(recommended)} ${realmLabel} Realm refresh${recommended===1?'':'es'}/day`;
        }else if(tools>0){
          bridge.textContent=`${fmt(tools)} ${item} can cover`;
        }
      };
      applyShortfallRefreshPlan('oreBalance','ore','Ore');
      applyShortfallRefreshPlan('essenceBalance','essence','Essence');
      applyShortfallRefreshPlan('sandBalance','sand','Sand');
"""
if needle not in s:
    raise SystemExit('Could not find daily Realm suggestion block')
s=s.replace(needle,insert,1)

old_banner="""        const recoverableBits=[];
        if(orePlanShort>0.5 && oreHardShort<=0.5) recoverableBits.push(`${fmt(Math.ceil(orePlanShort))} Ore short · extra Hammers can cover`);
        if(essPlanShort>0.5 && essHardShort<=0.5) recoverableBits.push(`${fmt(Math.ceil(essPlanShort))} Essence short · extra Knuckles can cover`);
        if(sandPlanShort>0.5 && sandHardShort<=0.5) recoverableBits.push(`${fmt(Math.ceil(sandPlanShort))} Sand short · extra Shovels can cover`);
        const recoverableText=recoverableBits.length?` ${recoverableBits.join(' · ')}.`:' Goal is achievable with additional Material Realm refreshes.';
        $('targetMessage').innerHTML=`<span class=\"targetMessageCopy\">⚠${recoverableText}${route}</span>${action}`;
"""
new_banner="""        // Resource cards now carry the exact deficit + resource-specific refresh action.
        // Keep this banner focused on the combined plan and its one-click Apply control.
        $('targetMessage').innerHTML=`<span class=\"targetMessageCopy\">⚠ Goal is achievable with the recommended Material Realm refresh plan.${route}</span>${action}`;
"""
if old_banner not in s:
    raise SystemExit('Could not find recoverable caution banner block')
s=s.replace(old_banner,new_banner,1)

p.write_text(s,encoding='utf-8')
print('applied recoverable shortfall refresh plan')
