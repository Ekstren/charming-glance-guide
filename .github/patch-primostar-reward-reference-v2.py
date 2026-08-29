from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
marker='PRIMOSTAR_REWARD_REFERENCE_V2'
if marker in s:
    print('already applied')
    raise SystemExit(0)

old_func="""  function renderPrimostarRewardReference(totalStars){
    const stars=Math.max(0,Math.floor(Number(totalStars)||0));
    const host=$('primostarRewardSeasons');
    const intro=$('primostarRewardsIntro');
    if(!host) return;
    const nextIndex=ASTRAL_PACT_NODES.findIndex(([threshold])=>threshold>stars);
    const groups=[
      {title:'Season 1 · Witching Hours',nodes:ASTRAL_PACT_NODES.slice(0,40),offset:0},
      {title:'Season 2 · Crossed Paths',nodes:ASTRAL_PACT_NODES.slice(40),offset:40}
    ];
    const row=(node,index)=>{
      const [threshold,key,value]=node;
      const globalIndex=index;
      const state=threshold<=stars?'reached':globalIndex===nextIndex?'next':'future';
      return `<div class=\"primostarRewardRow ${state}\"><span class=\"rewardThreshold\">${fmt(threshold)}</span><span class=\"rewardName\">${ASTRAL_LABELS[key]||key}</span><span class=\"rewardValue\">+${fmt(value)}%</span></div>`;
    };
    host.innerHTML=groups.map(group=>`<section class=\"primostarRewardSeason\"><h4>${group.title}</h4><div class=\"primostarRewardList\">${group.nodes.map((node,i)=>row(node,group.offset+i)).join('')}</div></section>`).join('');
    if(intro){
      intro.textContent=next
        ? `${fmt(stars)} projected Primostars · next reward at ${fmt(next[0])}: ${ASTRAL_LABELS[next[1]]} +${fmt(next[2])}%.`
        : `${fmt(stars)} projected Primostars · all documented Season 1–2 Astral Pact rewards reached.`;
    }
  }
"""
new_func="""  /* PRIMOSTAR_REWARD_REFERENCE_V2
     Checkmarks mean actually reached now, never merely targeted/projected.
     Season 2 rows stay hidden until the live calculator season is actually S2. */
  function renderPrimostarRewardReference(currentTotalStars,projectedTotalStars=currentTotalStars){
    const currentStars=Math.max(0,Math.floor(Number(currentTotalStars)||0));
    const projectedStars=Math.max(currentStars,Math.floor(Number(projectedTotalStars)||0));
    const host=$('primostarRewardSeasons');
    const intro=$('primostarRewardsIntro');
    if(!host) return;
    const cfg=activeCalcConfig();
    const s1Nodes=ASTRAL_PACT_NODES.slice(0,40);
    const visibleNodes=cfg.key==='s2'?ASTRAL_PACT_NODES:s1Nodes;
    const nextIndex=visibleNodes.findIndex(([threshold])=>threshold>currentStars);
    const nextReward=visibleNodes.find(([threshold])=>threshold>currentStars);
    const groups=[{title:'Season 1 · Witching Hours',nodes:s1Nodes,offset:0}];
    if(cfg.key==='s2') groups.push({title:'Season 2 · Crossed Paths',nodes:ASTRAL_PACT_NODES.slice(40),offset:40});
    const row=(node,index)=>{
      const [threshold,key,value]=node;
      const state=threshold<=currentStars?'reached':index===nextIndex?'next':'future';
      const projected=threshold>currentStars&&threshold<=projectedStars?' projected':'';
      return `<div class=\"primostarRewardRow ${state}${projected}\"><span class=\"rewardThreshold\">${fmt(threshold)}</span><span class=\"rewardName\">${ASTRAL_LABELS[key]||key}</span><span class=\"rewardValue\">+${fmt(value)}%</span></div>`;
    };
    host.innerHTML=groups.map(group=>`<section class=\"primostarRewardSeason\"><h4>${group.title}</h4><div class=\"primostarRewardList\">${group.nodes.map((node,i)=>row(node,group.offset+i)).join('')}</div></section>`).join('');
    if(intro){
      const projectionText=projectedStars!==currentStars?` · projected ${fmt(projectedStars)}`:'';
      intro.textContent=nextReward
        ? `${fmt(currentStars)} reached${projectionText} · next reward at ${fmt(nextReward[0])}: ${ASTRAL_LABELS[nextReward[1]]} +${fmt(nextReward[2])}%.`
        : `${fmt(currentStars)} reached${projectionText} · all currently available Astral Pact rewards reached.`;
    }
  }
"""
if old_func not in s:
    raise SystemExit('Could not find Primostar reward reference v1 function')
s=s.replace(old_func,new_func,1)

# renderAstralPact should only render the cumulative bonus totals; reward-status rows
# are now rendered explicitly with current + achievable projected values.
s=s.replace('    renderPrimostarRewardReference(stars);\n  }','  }',1)

old_no_plan="""      renderAstralPact(baselineStars);
      saveState();return;
"""
new_no_plan="""      renderAstralPact(baselineStars);
      renderPrimostarRewardReference(currentStarsNow,baselineStars);
      saveState();return;
"""
if old_no_plan not in s:
    raise SystemExit('Could not find baseline Astral render call')
s=s.replace(old_no_plan,new_no_plan,1)

old_plan="""    const planStars=historical+cfg.starBase+Math.floor(plan.score/cfg.scorePerStar);
    renderAstralPact(resourceBlocked?targetStars:planStars);
"""
new_plan="""    const planStars=historical+cfg.starBase+Math.floor(plan.score/cfg.scorePerStar);
    const achievableRewardStars=resourceBlocked?baselineStars:planStars;
    renderAstralPact(achievableRewardStars);
    renderPrimostarRewardReference(currentStarsNow,achievableRewardStars);
"""
if old_plan not in s:
    raise SystemExit('Could not find plan Astral render call')
s=s.replace(old_plan,new_plan,1)

# Subtle projected status without implying receipt; next reward highlighting remains stronger.
css_needle=""".primostarRewardRow.future{opacity:.72}
"""
css_new=""".primostarRewardRow.future{opacity:.72}
.primostarRewardRow.projected:not(.next){background:color-mix(in srgb,var(--blue) 6%,transparent)}
"""
if css_needle not in s:
    raise SystemExit('Could not find Primostar reward future CSS')
s=s.replace(css_needle,css_new,1)

p.write_text(s,encoding='utf-8')
print('fixed Primostar reward statuses and season visibility')
