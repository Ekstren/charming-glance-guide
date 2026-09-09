from pathlib import Path

path = Path('index.html')
s = path.read_text(encoding='utf-8')

old = """    if(boundedLast){
      const boundedGear=gearOptions.slice(0,boundedLast.gear+1);
      const boundedSkill=cats.skillOptions.slice(0,boundedLast.skill+1);
      const boundedRelic=cats.relicOptions.slice(0,boundedLast.relic+1);
      const boundedFanto=cats.fantoOptions.slice(0,boundedLast.fanto+1);
"""
new = """    if(boundedLast){
      const boundedGear=gearOptions.slice(0,boundedLast.gear+1);
      const boundedSkill=cats.skillOptions.slice(0,boundedLast.skill+1);
      const boundedRelic=cats.relicOptions.slice(0,boundedLast.relic+1);

      /* ZERO_RATE_FANTO_PRUNE_V1
         Treats have no map/Realm reacquisition path. If Treat Cart income is zero, any
         Fantomon upgrade has the optimizer's 1e9 acquisition penalty. When the target is
         already reachable in the same preferred no-paid sourcing tier with the current
         Fantomon level, every positive-Treat Fantomon option is strictly worse before
         overscore/share tie-breaks are consulted. Keep only the zero-cost base option.

         This is especially important for well-funded accounts: the old exact scan still
         walked hundreds of Fantomon states even though none could beat a finite-acquisition
         base-Fantomon route. */
      let boundedFantoLast=boundedLast.fanto;
      if(noPaidRoutePossible && acqCartTreat<=0 && (Number(cats.fantoOptions[0]?.__acqTreatV1)||0)<=1e-9){
        const baseFantoScore=Number(cats.fantoOptions[0]?.score)||0;
        const noPaidBaseFantoMax=charScore+
          scoreAt(gearOptions,noPaidLast.gear)+scoreAt(cats.skillOptions,noPaidLast.skill)+
          scoreAt(cats.relicOptions,noPaidLast.relic)+baseFantoScore;
        if(noPaidBaseFantoMax>=desired-1e-9) boundedFantoLast=0;
      }
      const boundedFanto=cats.fantoOptions.slice(0,boundedFantoLast+1);
"""

count=s.count(old)
if count != 1:
    raise SystemExit(f'expected one bounded-search insertion point, found {count}')
s=s.replace(old,new,1)
path.write_text(s,encoding='utf-8')
print('Added exact zero-Treat-rate Fantomon pruning to bounded optimizer search.')
