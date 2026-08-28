#!/usr/bin/env python3
from pathlib import Path

PATH=Path('index.html')
text=PATH.read_text(encoding='utf-8')
MARKER='S2_PRIMO_BENCHMARK_V2'
if MARKER in text:
    print(f'{MARKER} already present; nothing to do.')
    raise SystemExit(0)

def replace_once(old,new,label):
    global text
    count=text.count(old)
    if count!=1:
        raise SystemExit(f'{label}: expected exactly 1 match, found {count}')
    text=text.replace(old,new,1)

old_meta="""    commonTargets:Object.freeze([530,680,920]),
    milestones:Object.freeze([
"""
new_meta="""    commonTargets:Object.freeze([530,680,920]),
    /* S2_PRIMO_BENCHMARK_V2
       Published S2 920 end-state: 131 carried S1 stars, Lv.190 at ~80%, Gear 195,
       Skills 180, four deployed Fantomons represented as 175/175/173/173, Relics +19.
       The prepared S2 formula must reconstruct exactly 920 total Primostars. */
    benchmark:Object.freeze({
      carriedStars:131,character:190.8,gear:Object.freeze([195,195,195,195,195]),skill:180,
      fantomons:Object.freeze([175,175,173,173]),relic:19,expectedTotalStars:920
    }),
    milestones:Object.freeze([
"""
replace_once(old_meta,new_meta,'benchmark metadata')

old_validator="""    const ok=c.scoreFloor===m.scoreFloor &&
      c.relicFloor===m.relicFloor &&
      c.starBase===m.fixedStars &&
      c.scorePerStar===m.scorePerStar &&
      w.character===mw.character && w.gear===mw.gear && w.skill===mw.skill &&
      w.relic===mw.relic && w.fanto===mw.fanto;
    if(!ok) console.warn('S2_PRIMO_READY_V1: Season 2 scoring constants drifted from the validated model.',{config:c,expected:m});
    return ok;
"""
new_validator="""    const constantsOk=c.scoreFloor===m.scoreFloor &&
      c.relicFloor===m.relicFloor &&
      c.starBase===m.fixedStars &&
      c.scorePerStar===m.scorePerStar &&
      w.character===mw.character && w.gear===mw.gear && w.skill===mw.skill &&
      w.relic===mw.relic && w.fanto===mw.fanto;
    const b=m.benchmark;
    const benchmarkScore=
      Math.floor(Math.max(0,b.character-m.scoreFloor)*m.weights.character+1e-9) +
      b.gear.reduce((sum,l)=>sum+Math.max(0,l-m.scoreFloor)*m.weights.gear,0) +
      (Math.max(0,b.skill-m.scoreFloor)*8*m.weights.skill) +
      b.fantomons.reduce((sum,l)=>sum+Math.max(0,l-m.scoreFloor)*m.weights.fanto,0) +
      (Math.max(0,b.relic-m.relicFloor)*20*m.weights.relic);
    const benchmarkTotal=b.carriedStars+m.fixedStars+Math.floor(benchmarkScore/m.scorePerStar);
    const benchmarkOk=benchmarkTotal===b.expectedTotalStars;
    if(!constantsOk) console.warn('S2_PRIMO_READY_V1: Season 2 scoring constants drifted from the validated model.',{config:c,expected:m});
    if(!benchmarkOk) console.warn('S2_PRIMO_BENCHMARK_V2: Season 2 920-star benchmark no longer reconstructs correctly.',{benchmarkScore,benchmarkTotal,expected:b.expectedTotalStars});
    return constantsOk&&benchmarkOk;
"""
replace_once(old_validator,new_validator,'benchmark validator')

old_method="""Exact Global cost/unlock data that is not independently confirmed remains conservative rather than fabricated.</p>
<p><b>S2 progression gates:</b>"""
new_method="""Exact Global cost/unlock data that is not independently confirmed remains conservative rather than fabricated. As a regression check, the formula also reproduces the published S2 920-Primostar end-state (131 carried from S1; about Lv.190.8, Gear 195, Skills 180, Fantomons 175/175/173/173 and Relics +19).</p>
<p><b>S2 progression gates:</b>"""
replace_once(old_method,new_method,'benchmark methodology note')

required=[
    'S2_PRIMO_READY_V1',MARKER,
    "scoreFloor:130,relicFloor:13,starBase:45,scorePerStar:27",
    "weights:{character:100,gear:18,skill:7,relic:33,fanto:8}",
    'expectedTotalStars:920',
    "const seasonKeyAt = (ms=Date.now()) => ms < S1_END.getTime() ? 's1' : 's2';",
    "s1:{key:'s1',name:'Season 1'"
]
for needle in required:
    if needle not in text:
        raise SystemExit(f'integrity check failed: missing {needle!r}')

PATH.write_text(text,encoding='utf-8')
print('Added S2 920-Primostar regression benchmark.')
