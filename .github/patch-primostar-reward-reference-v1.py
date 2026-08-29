from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
marker='PRIMOSTAR_REWARD_REFERENCE_V1'
if marker in s:
    print('already applied')
    raise SystemExit(0)

# Add the new expandable section immediately below Bonuses and score breakdown.
needle='''</div></details>\n      <p class="milestoneNote" id="milestoneNote" hidden></p>'''
insert='''</div></details>\n      <!-- PRIMOSTAR_REWARD_REFERENCE_V1 -->\n      <details class="resultDetails primostarRewardsDetails"><summary>Primostar rewards</summary><div class="primostarRewardsBody"><p class="primostarRewardsIntro" id="primostarRewardsIntro">Astral Pact reward thresholds from the same table used by the calculator.</p><div class="primostarRewardSeasons" id="primostarRewardSeasons"></div></div></details>\n      <p class="milestoneNote" id="milestoneNote" hidden></p>'''
if needle not in s:
    raise SystemExit('Could not find result-details insertion point')
s=s.replace(needle,insert,1)

# Extend the existing resultDetails styling with a compact reward table.
css_needle='''.resultDetails>div{padding-top:8px}'''
css_insert='''.resultDetails>div{padding-top:8px}\n/* PRIMOSTAR_REWARD_REFERENCE_V1 */\n.primostarRewardsBody{padding:8px 0 2px!important}\n.primostarRewardsIntro{color:var(--muted);margin:0 0 10px;font-size:9px;line-height:1.45}\n.primostarRewardSeasons{display:grid;grid-template-columns:1fr 1fr;gap:9px}\n.primostarRewardSeason{border:1px solid var(--line);border-radius:11px;overflow:hidden;min-width:0}\n.primostarRewardSeason h4{margin:0;padding:9px 10px;background:var(--bg);color:var(--muted);font-size:8px;font-weight:900;letter-spacing:.07em;text-transform:uppercase}\n.primostarRewardList{display:grid}\n.primostarRewardRow{display:grid;grid-template-columns:58px 1fr auto;align-items:center;gap:8px;min-width:0;padding:7px 9px;border-top:1px solid var(--line);font-size:9px}\n.primostarRewardRow:first-child{border-top:0}\n.primostarRewardRow .rewardThreshold{color:var(--ink);font-weight:900}\n.primostarRewardRow .rewardName{color:var(--secondary-text);min-width:0}\n.primostarRewardRow .rewardValue{color:var(--green);font-weight:900;white-space:nowrap}\n.primostarRewardRow.reached{background:color-mix(in srgb,var(--green) 7%,transparent)}\n.primostarRewardRow.reached .rewardThreshold:after{content:' ✓';color:var(--green);font-size:8px}\n.primostarRewardRow.next{background:color-mix(in srgb,var(--gold) 10%,transparent);box-shadow:inset 3px 0 0 var(--gold)}\n.primostarRewardRow.next .rewardThreshold,.primostarRewardRow.next .rewardValue{color:var(--gold)}\n.primostarRewardRow.future{opacity:.72}\n@media (max-width:760px){.primostarRewardSeasons{grid-template-columns:1fr}.primostarRewardRow{grid-template-columns:62px 1fr auto;font-size:10px;padding:8px 9px}}'''
if css_needle not in s:
    raise SystemExit('Could not find resultDetails CSS insertion point')
s=s.replace(css_needle,css_insert,1)

# Render from the canonical ASTRAL_PACT_NODES table, so the display cannot drift from scoring.
render_needle='''    if(count){\n      const s1Unlocked=ASTRAL_PACT_NODES.slice(0,40).filter(([threshold])=>threshold<=stars).length;\n      const seasonText=stars<=480?`${s1Unlocked} of 40 documented S1 nodes unlocked`:`${unlocked} of ${ASTRAL_PACT_NODES.length} documented S1–S2 nodes unlocked`;\n      const nextText=next?` · next: ${fmt(next[0])} → ${ASTRAL_LABELS[next[1]]} +${next[2]}%`:' · all documented S1–S2 nodes unlocked';\n      count.textContent=`${fmt(stars)} projected total Primostars · ${seasonText}${nextText}.`;\n    }\n  }'''
render_insert='''    if(count){\n      const s1Unlocked=ASTRAL_PACT_NODES.slice(0,40).filter(([threshold])=>threshold<=stars).length;\n      const seasonText=stars<=480?`${s1Unlocked} of 40 documented S1 nodes unlocked`:`${unlocked} of ${ASTRAL_PACT_NODES.length} documented S1–S2 nodes unlocked`;\n      const nextText=next?` · next: ${fmt(next[0])} → ${ASTRAL_LABELS[next[1]]} +${next[2]}%`:' · all documented S1–S2 nodes unlocked';\n      count.textContent=`${fmt(stars)} projected total Primostars · ${seasonText}${nextText}.`;\n    }\n    renderPrimostarRewardReference(stars);\n  }\n\n  function renderPrimostarRewardReference(totalStars){\n    const stars=Math.max(0,Math.floor(Number(totalStars)||0));\n    const host=$('primostarRewardSeasons');\n    const intro=$('primostarRewardsIntro');\n    if(!host) return;\n    const nextIndex=ASTRAL_PACT_NODES.findIndex(([threshold])=>threshold>stars);\n    const groups=[\n      {title:'Season 1 · Witching Hours',nodes:ASTRAL_PACT_NODES.slice(0,40),offset:0},\n      {title:'Season 2 · Crossed Paths',nodes:ASTRAL_PACT_NODES.slice(40),offset:40}\n    ];\n    const row=(node,index)=>{\n      const [threshold,key,value]=node;\n      const globalIndex=index;\n      const state=threshold<=stars?'reached':globalIndex===nextIndex?'next':'future';\n      return `<div class=\"primostarRewardRow ${state}\"><span class=\"rewardThreshold\">${fmt(threshold)}</span><span class=\"rewardName\">${ASTRAL_LABELS[key]||key}</span><span class=\"rewardValue\">+${fmt(value)}%</span></div>`;\n    };\n    host.innerHTML=groups.map(group=>`<section class=\"primostarRewardSeason\"><h4>${group.title}</h4><div class=\"primostarRewardList\">${group.nodes.map((node,i)=>row(node,group.offset+i)).join('')}</div></section>`).join('');\n    if(intro){\n      intro.textContent=next\n        ? `${fmt(stars)} projected Primostars · next reward at ${fmt(next[0])}: ${ASTRAL_LABELS[next[1]]} +${fmt(next[2])}%.`\n        : `${fmt(stars)} projected Primostars · all documented Season 1–2 Astral Pact rewards reached.`;\n    }\n  }'''
if render_needle not in s:
    raise SystemExit('Could not find renderAstralPact block')
s=s.replace(render_needle,render_insert,1)

p.write_text(s,encoding='utf-8')
print('added Primostar reward reference')
