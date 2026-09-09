from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

if 'ACQUISITION_LIMIT_PRECHECK_V8' in s:
    print('Primostar acquisition limit precheck already applied.')
    raise SystemExit(0)
for marker in ('NO_PAID_PRIMARY_FAST_COMPARE_V5','REALM_OPTION_PROPERTY_CACHE_V7'):
    if marker not in s:
        raise SystemExit(f'required optimizer marker missing: {marker}')
if 'BOUNDED_COMPACT_BEST_V6' in s or 'SKILL_GEAR_BREAKPOINT_JUMP_V4' in s:
    raise SystemExit('rejected optimizer experiment present; refusing v11 patch')

old="""    const acquisitionFor=(go,so,ro,fo)=>({hours:jointHoursFast(go.__acqOreV1,so.__acqEssenceV1,ro.__acqSandV1,fo.__acqTreatV1)});
    let best=null,bestDiagnostic=null;
"""
new="""    const acquisitionFor=(go,so,ro,fo)=>({hours:jointHoursFast(go.__acqOreV1,so.__acqEssenceV1,ro.__acqSandV1,fo.__acqTreatV1)});
    /* ACQUISITION_LIMIT_PRECHECK_V8
       For the no-paid bounded search acquisition hours are the primary comparator. Before
       solving the piecewise joint-hours equation, test the current winner's time directly:
       if Treat Cart production cannot cover Treat demand by that time, or the map-node work
       still exceeds the same time budget, the candidate's exact joint root must be later and
       it cannot win. This is a necessary-condition rejection only; surviving candidates still
       run the original exact jointHoursFast() and the normal tie-break chain. */
    const acquisitionCannotBeat=(bestHours,go,so,ro,fo)=>{
      if(!Number.isFinite(bestHours)||bestHours>=1e9) return false;
      const limit=bestHours+1e-9;
      const treat=fo.__acqTreatV1;
      if(treat>0){
        if(acqCartTreat<=0) return true;
        if(treat>acqCartTreat*limit+1e-7) return true;
      }
      return nodesAtFast(limit,go.__acqOreV1,so.__acqEssenceV1,ro.__acqSandV1)>limit+1e-7;
    };
    let best=null,bestDiagnostic=null;
"""
if old not in s:
    raise SystemExit('acquisitionFor anchor not found')
s=s.replace(old,new,1)

old_block="""            const acquisition=acquisitionFor(go,so,ro,fo);
            /* NO_PAID_PRIMARY_FAST_COMPARE_V5
               boundedLast===noPaidLast means every candidate is in the same preferred owned
               tier. Acquisition is the exact primary comparator, so do not allocate a full
               candidate object for a value that is already strictly worse than boundedBest. */
            if(noPaidRoutePossible&&boundedBest&&acquisition.hours>boundedBest.acquisitionHours+1e-9) continue;
"""
new_block="""            if(noPaidRoutePossible&&boundedBest&&acquisitionCannotBeat(boundedBest.acquisitionHours,go,so,ro,fo)) continue;
            const acquisition=acquisitionFor(go,so,ro,fo);
            /* NO_PAID_PRIMARY_FAST_COMPARE_V5 · ACQUISITION_LIMIT_PRECHECK_V8
               The cheap current-winner feasibility test above rejects obvious losers before
               the full joint solve; this exact comparison remains the final numeric guard. */
            if(noPaidRoutePossible&&boundedBest&&acquisition.hours>boundedBest.acquisitionHours+1e-9) continue;
"""
count=s.count(old_block)
if count != 2:
    raise SystemExit(f'expected exactly two bounded acquisition blocks, found {count}')
s=s.replace(old_block,new_block,2)

p.write_text(s,encoding='utf-8')
print('Applied Primostar v11 exact acquisition-limit precheck to bounded seed and scan.')
