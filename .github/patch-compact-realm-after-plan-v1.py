from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
marker='COMPACT_REALM_AFTER_PLAN_V1'
if marker in s:
    print('already applied')
    raise SystemExit(0)

old="""    const toolLeftEls=[['hammerAfterPlan',afterPlanTools.ore,0],['knucklesAfterPlan',afterPlanTools.essence,protectedKnuckles],['shovelAfterPlan',afterPlanTools.sand,protectedShovels]];
    toolLeftEls.forEach(([id,value,protectedCount])=>{const el=$(id);if(el){el.textContent=`After recommended plan: ${fmt(value)} spendable left${protectedCount?` · ${fmt(protectedCount)} S2 reserve`:''}`;el.classList.toggle('toolLow',value<=10);}});
"""
new="""    // COMPACT_REALM_AFTER_PLAN_V1: keep the useful post-plan balance without repeating context.
    const toolLeftEls=[['hammerAfterPlan',afterPlanTools.ore,0],['knucklesAfterPlan',afterPlanTools.essence,protectedKnuckles],['shovelAfterPlan',afterPlanTools.sand,protectedShovels]];
    toolLeftEls.forEach(([id,value,protectedCount])=>{const el=$(id);if(el){el.textContent=`After plan: ${fmt(value)} left${protectedCount?` · ${fmt(protectedCount)} reserved`:''}`;el.classList.toggle('toolLow',value<=10);}});
"""
if old not in s:
    raise SystemExit('after-plan Realm label block not found')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('compacted Realm after-plan labels')
