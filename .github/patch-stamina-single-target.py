from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')
marker = 'STAMINA_AUTO_SINGLE_TARGET_V1'
if marker in text:
    print('Single-target Auto Stamina already applied.')
    raise SystemExit(0)

old = r'''    let best=null;
    // Full integer split. At a fresh long season this is ~1.3M cheap comparisons for ~1,600 nodes;
    // all Realm topups were precomputed above, so this remains much cheaper than rerunning searchPlans.
    for(let essenceNodes=0;essenceNodes<=total;essenceNodes++){
      for(let sandNodes=0;sandNodes<=total-essenceNodes;sandNodes++){
        const oreNodes=total-essenceNodes-sandNodes;
        const candidate=metricFor(oreNodes,essenceNodes,sandNodes);
        if(better(candidate,best)) best=candidate;
      }
    }
    return best?.allocation||{...empty,ore:(Number(map.ore)||0)>0?total:0,unassigned:(Number(map.ore)||0)>0?0:total};
'''

new = r'''    let best=null;
    // STAMINA_AUTO_SINGLE_TARGET_V1: Auto Stamina must recommend ONE resource only.
    // Do not split nodes across Ore / Essence / Sand; that is too easy to lose track of in-game.
    // Compare the three all-in routes and choose the best complete destination for the current plan.
    const singleTargetCandidates=[];
    if((Number(map.ore)||0)>0) singleTargetCandidates.push(metricFor(total,0,0));
    if((Number(map.essence)||0)>0) singleTargetCandidates.push(metricFor(0,total,0));
    if((Number(map.sand)||0)>0) singleTargetCandidates.push(metricFor(0,0,total));
    for(const candidate of singleTargetCandidates){
      if(better(candidate,best)) best=candidate;
    }
    return best?.allocation||{...empty,ore:(Number(map.ore)||0)>0?total:0,unassigned:(Number(map.ore)||0)>0?0:total};
'''

if text.count(old) != 1:
    raise SystemExit(f'Expected one full-split Auto Stamina block, found {text.count(old)}')
text = text.replace(old, new, 1)

path.write_text(text, encoding='utf-8')
print('Changed Auto Stamina to one-resource-only recommendations.')
