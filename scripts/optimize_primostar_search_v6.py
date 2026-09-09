from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

if 'REFINED_FASTPATH_GUARD_V3' in s:
    print('Refined fast-path guard already restored.')
    raise SystemExit(0)

old="""    /* FULLY_FUNDED_TREAT_REFINED_V2
       Refined tracking only blocks the Treat-funded dimensional collapse when Refined Ore
       can actually constrain Gear. If the projected Refined pool covers the maximum reachable
       Gear option, the constraint is inactive and the same exact Relic x Skill collapse applies. */
    const maxReachableRefined=Math.max(0,Number(gearOptions[gearOptions.length-1]?.refinedCost)||0);
    const refinedFullyFunded=!resources.refinedTracked || (Number(resources.refined)||0)>=maxReachableRefined-0.5;
    const treatFullyFunded=refinedFullyFunded &&
      (Number(resources.treat)||0)>=Math.max(0,Number(headroomCosts?.treat)||0)-0.5;
"""
new="""    /* REFINED_FASTPATH_GUARD_V3
       Keep the Treat-funded dimensional collapse disabled whenever Refined Ore tracking is
       active. Even a numerically funded Refined pool still participates in downstream share/
       tie-break semantics, so collapsing that dimension changes the exact chosen plan. */
    const treatFullyFunded=!resources.refinedTracked &&
      (Number(resources.treat)||0)>=Math.max(0,Number(headroomCosts?.treat)||0)-0.5;
"""
if old not in s:
    raise SystemExit('v5 Refined fast-path block not found')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('Restored exact Refined guard while retaining v5 hot-loop optimizations.')
