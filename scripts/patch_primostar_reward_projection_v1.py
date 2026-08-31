from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
MARK='PRIMOSTAR_REWARD_PROJECTION_V1'
if MARK in s:
    print('Primostar reward projection display already fixed')
    raise SystemExit(0)

old_css=""".primostarRewardRow.reached{background:color-mix(in srgb,var(--green) 7%,transparent)}
.primostarRewardRow.reached .rewardThreshold:after{content:' ✓';color:var(--green);font-size:8px}
.primostarRewardRow.next{background:color-mix(in srgb,var(--gold) 10%,transparent);box-shadow:inset 3px 0 0 var(--gold)}
.primostarRewardRow.next .rewardThreshold,.primostarRewardRow.next .rewardValue{color:var(--gold)}
.primostarRewardRow.future{opacity:.72}
.primostarRewardRow.projected:not(.next){background:color-mix(in srgb,var(--blue) 6%,transparent)}
"""
new_css="""/* PRIMOSTAR_REWARD_PROJECTION_V1
   Green/check = actually earned now. Blue/arrow = projected by the recommended end-state.
   Gold = the first reward still beyond that projection. */
.primostarRewardRow.reached{background:color-mix(in srgb,var(--green) 7%,transparent)}
.primostarRewardRow.reached .rewardThreshold:after{content:' ✓';color:var(--green);font-size:8px}
.primostarRewardRow.projected{background:color-mix(in srgb,var(--blue) 11%,transparent)}
.primostarRewardRow.projected .rewardThreshold:after{content:' ↗';color:var(--blue);font-size:8px}
.primostarRewardRow.next{background:color-mix(in srgb,var(--gold) 10%,transparent);box-shadow:inset 3px 0 0 var(--gold)}
.primostarRewardRow.next .rewardThreshold,.primostarRewardRow.next .rewardValue{color:var(--gold)}
.primostarRewardRow.future{opacity:.72}
"""
if old_css not in s:
    raise SystemExit('reward CSS anchor not found')
s=s.replace(old_css,new_css,1)

old_js="""    const nextIndex=visibleNodes.findIndex(([threshold])=>threshold>currentStars);
    const nextReward=visibleNodes.find(([threshold])=>threshold>currentStars);
    const groups=[{title:'Witching Hours',nodes:s1Nodes,offset:0}];
    if(cfg.key==='s2') groups.push({title:'Crossed Paths',nodes:ASTRAL_PACT_NODES.slice(40),offset:40});
    const row=(node,index)=>{
      const [threshold,key,value]=node;
      const state=threshold<=currentStars?'reached':index===nextIndex?'next':'future';
      const projected=threshold>currentStars&&threshold<=projectedStars?' projected':'';
      return `<div class=\"primostarRewardRow ${state}${projected}\"><span class=\"rewardThreshold\">${fmt(threshold)}</span><span class=\"rewardName\">${ASTRAL_LABELS[key]||key}</span><span class=\"rewardValue\">+${fmt(value)}%</span></div>`;
    };
"""
new_js="""    // The result card is a season-end projection, so the highlighted \"next\" reward must
    // be the first threshold AFTER the projected total, not merely the next reward after
    // today's current total. Otherwise a 920 projection could misleadingly say \"next 305\".
    const nextIndex=visibleNodes.findIndex(([threshold])=>threshold>projectedStars);
    const nextReward=visibleNodes.find(([threshold])=>threshold>projectedStars);
    const groups=[{title:'Witching Hours',nodes:s1Nodes,offset:0}];
    if(cfg.key==='s2') groups.push({title:'Crossed Paths',nodes:ASTRAL_PACT_NODES.slice(40),offset:40});
    const row=(node,index)=>{
      const [threshold,key,value]=node;
      const projected=threshold>currentStars&&threshold<=projectedStars;
      const state=threshold<=currentStars?'reached':projected?'projected':index===nextIndex?'next':'future';
      return `<div class=\"primostarRewardRow ${state}\"><span class=\"rewardThreshold\">${fmt(threshold)}</span><span class=\"rewardName\">${ASTRAL_LABELS[key]||key}</span><span class=\"rewardValue\">+${fmt(value)}%</span></div>`;
    };
"""
if old_js not in s:
    raise SystemExit('reward row-state anchor not found')
s=s.replace(old_js,new_js,1)

old_intro="""    if(intro){
      const projectionText=projectedStars!==currentStars?` · projected ${fmt(projectedStars)}`:'';
      intro.textContent=nextReward
        ? `${fmt(currentStars)} reached${projectionText} · next reward at ${fmt(nextReward[0])}: ${ASTRAL_LABELS[nextReward[1]]} +${fmt(nextReward[2])}%.`
        : `${fmt(currentStars)} reached${projectionText} · all currently available Astral Pact rewards reached.`;
    }
"""
new_intro="""    if(intro){
      const projectedCount=visibleNodes.filter(([threshold])=>threshold>currentStars&&threshold<=projectedStars).length;
      if(projectedStars>currentStars){
        const projectionText=`${fmt(currentStars)} current · ${fmt(projectedStars)} projected`;
        intro.textContent=nextReward
          ? `${projectionText} · ${fmt(projectedCount)} more reward${projectedCount===1?'':'s'} projected · next after projection at ${fmt(nextReward[0])}: ${ASTRAL_LABELS[nextReward[1]]} +${fmt(nextReward[2])}%.`
          : `${projectionText} · ${fmt(projectedCount)} more reward${projectedCount===1?'':'s'} projected · all currently available Astral Pact rewards covered.`;
      }else{
        intro.textContent=nextReward
          ? `${fmt(currentStars)} current · next reward at ${fmt(nextReward[0])}: ${ASTRAL_LABELS[nextReward[1]]} +${fmt(nextReward[2])}%.`
          : `${fmt(currentStars)} current · all currently available Astral Pact rewards reached.`;
      }
    }
"""
if old_intro not in s:
    raise SystemExit('reward intro anchor not found')
s=s.replace(old_intro,new_intro,1)

p.write_text(s,encoding='utf-8')
print('fixed current/projected/next reward-state display')
