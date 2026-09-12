from pathlib import Path

path = Path('assets/runtime.js')
s = path.read_text(encoding='utf-8')

# 1) Add the universal preseason Bed hold model immediately after Pacific reset counting.
anchor = '''  function countFuturePacificResets(startMs,cutoffMs){
    if(!(cutoffMs>startMs)) return 0;
    const first=nextPacificResetMs(startMs);
    if(!(first<cutoffMs)) return 0;
    const key=`${first}|${cutoffMs}`;
    if(FUTURE_RESET_COUNT_CACHE.has(key)) return FUTURE_RESET_COUNT_CACHE.get(key);
    let t=first,count=0,safety=0;
    while(t<cutoffMs && safety++<500){
      count++;
      t=pacificLocalMs(isoAddDays(pacificIsoAt(t),1),6,0);
    }
    FUTURE_RESET_COUNT_CACHE.set(key,count);
    if(FUTURE_RESET_COUNT_CACHE.size>64) FUTURE_RESET_COUNT_CACHE.delete(FUTURE_RESET_COUNT_CACHE.keys().next().value);
    return count;
  }
'''
insert = anchor + '''  /* PRESEASON_BED_RESERVE_V1
     Universal rollover strategy: stop CLAIMING Bed EXP 34 wall-clock hours before a season ends.
     The final daily reset inside that hold window still uses its free 2-hour speed-up, but that
     accelerated EXP stays in the Bed. Result at rollover: 34 natural hours + 2 boosted hours =
     36 hours of Bed EXP banked for the next season. Other Cart/material production is unaffected. */
  const PRESEASON_BED_HOLD_WALL_HOURS=34;
  const PRESEASON_BED_FINAL_RESET_BOOST_HOURS=2;
  function characterExpCollectionCutoffMs(cfg=activeCalcConfig()){
    return cfg.end.getTime()-(PRESEASON_BED_HOLD_WALL_HOURS*3_600_000);
  }
  function projectionBedClaimableHoursAt(ms,cfg=activeCalcConfig()){
    const cutoff=characterExpCollectionCutoffMs(cfg);
    const capped=Math.min(ms,cutoff);
    if(capped>=cutoff) return 0;
    const wallHours=Math.max(0,(cutoff-capped)/3_600_000);
    const boostHours=2*countFuturePacificResets(capped,cutoff);
    return Math.max(0,wallHours+boostHours);
  }
'''
if 'PRESEASON_BED_RESERVE_V1' not in s:
    if s.count(anchor) != 1:
        raise SystemExit(f'Expected one reset-count anchor, found {s.count(anchor)}')
    s = s.replace(anchor, insert, 1)

# 2) Snapshot aging must stop auto-claiming Character EXP at the 34-hour hold boundary,
# while Cart/material resources keep aging through their normal cutoff.
old_elapsed = '''    const oldResourceHours = projectionResourceHoursAt(snapshotAtMs,cfg);
    const newResourceHours = projectionResourceHoursAt(cappedNow,cfg);
    const elapsedResourceHours = Math.max(0, oldResourceHours-newResourceHours);
'''
new_elapsed = '''    const oldResourceHours = projectionResourceHoursAt(snapshotAtMs,cfg);
    const newResourceHours = projectionResourceHoursAt(cappedNow,cfg);
    const elapsedResourceHours = Math.max(0, oldResourceHours-newResourceHours);
    const oldBedClaimableHours = projectionBedClaimableHoursAt(snapshotAtMs,cfg);
    const newBedClaimableHours = projectionBedClaimableHoursAt(cappedNow,cfg);
    const elapsedBedClaimableHours = Math.max(0,oldBedClaimableHours-newBedClaimableHours);
'''
if 'elapsedBedClaimableHours' not in s:
    if s.count(old_elapsed) != 1:
        raise SystemExit(f'Expected one snapshot elapsed-hours block, found {s.count(old_elapsed)}')
    s = s.replace(old_elapsed, new_elapsed, 1)

old_exp = '''    const bedRate=Math.max(0,n('bedExp',0));
    const producedExp=bedRate*elapsedResourceHours + Math.max(0,Number(snapshotCarry.exp)||0);
'''
new_exp = '''    const bedRate=Math.max(0,n('bedExp',0));
    const producedExp=bedRate*elapsedBedClaimableHours + Math.max(0,Number(snapshotCarry.exp)||0);
'''
if s.count(old_exp) == 1:
    s = s.replace(old_exp, new_exp, 1)
elif new_exp not in s:
    raise SystemExit('Could not patch snapshot Bed EXP aging.')

old_return = '''    return elapsedResourceHours>0 || elapsedRealmResets>0;
'''
new_return = '''    return elapsedResourceHours>0 || elapsedBedClaimableHours>0 || elapsedRealmResets>0;
'''
if s.count(old_return) == 1:
    s = s.replace(old_return, new_return, 1)
elif new_return not in s:
    raise SystemExit('Could not patch snapshot aging return condition.')

# 3) Character projection keeps the FULL requested wall-clock horizon in p.hours so resource
# projections are unchanged, but Character EXP itself is capped at the universal Bed hold start.
old_project = '''  /* BED_STORAGE_DISABLED_V1
     Stored/hold Bed automation is temporarily disabled. The planner still uses the entered
     Bed EXP/hour for ordinary season-end projection, including the free 2-hour reset boosts. */
  function projectCharacterTo(targetMs,cfg=activeCalcConfig()){
    const now=Date.now();
    const current=characterSnapshot(cfg);
    let lvl=current.level, exp=current.exp;
    const endMs=cfg.end.getTime();
    const target=Math.max(now,Math.min(Number(targetMs)||endMs,endMs));
    const naturalHours=Math.max(0,(target-now)/3_600_000);
    const boostResets=target>now?countFuturePacificResets(now,target):0;
    const boostHours=2*boostResets;
    const acceleratedHours=naturalHours+boostHours;
    exp += Math.max(0,n('bedExp',0))*acceleratedHours;
    let safety=0;
    while(safety++<400){
      const req=expRequiredForLevel(lvl,cfg);
      if(exp<req) break;
      exp-=req; lvl++;
    }
    const req=expRequiredForLevel(lvl,cfg);
    const pct=req>0?clamp(exp/req,0,0.999999999):0;
    return {level:lvl,exp,req,pct,decimal:lvl+pct,hours:naturalHours,reserve:0,acceleratedHours,naturalHours,boostHours,boostResets,current,targetMs:target};
  }
'''
new_project = '''  /* PRESEASON_BED_RESERVE_V1
     Character progression assumes the recommended rollover strategy by default: stop claiming
     Bed EXP 34 hours before season end, then use the final reset's 2-hour speed-up without
     claiming it. That leaves 36 hours of Bed EXP ready for the next season. The returned
     `hours` remains the full requested wall-clock horizon so Cart/material projections do not
     inherit this Character-only hold. */
  function projectCharacterTo(targetMs,cfg=activeCalcConfig()){
    const now=Date.now();
    const current=characterSnapshot(cfg);
    let lvl=current.level, exp=current.exp;
    const endMs=cfg.end.getTime();
    const target=Math.max(now,Math.min(Number(targetMs)||endMs,endMs));
    const expTarget=Math.min(target,characterExpCollectionCutoffMs(cfg));
    const naturalHours=Math.max(0,(target-now)/3_600_000);
    const expNaturalHours=Math.max(0,(expTarget-now)/3_600_000);
    const boostResets=expTarget>now?countFuturePacificResets(now,expTarget):0;
    const boostHours=2*boostResets;
    const acceleratedHours=expNaturalHours+boostHours;
    exp += Math.max(0,n('bedExp',0))*acceleratedHours;
    let safety=0;
    while(safety++<400){
      const req=expRequiredForLevel(lvl,cfg);
      if(exp<req) break;
      exp-=req; lvl++;
    }
    const req=expRequiredForLevel(lvl,cfg);
    const pct=req>0?clamp(exp/req,0,0.999999999):0;
    return {level:lvl,exp,req,pct,decimal:lvl+pct,hours:naturalHours,reserve:0,acceleratedHours,naturalHours,expNaturalHours,boostHours,boostResets,current,targetMs:target,expTargetMs:expTarget,preseasonBedReserveHours:PRESEASON_BED_HOLD_WALL_HOURS+PRESEASON_BED_FINAL_RESET_BOOST_HOURS};
  }
'''
if 'preseasonBedReserveHours' not in s:
    if s.count(old_project) != 1:
        raise SystemExit(f'Expected one Character projection block, found {s.count(old_project)}')
    s = s.replace(old_project, new_project, 1)

path.write_text(s, encoding='utf-8')

check = path.read_text(encoding='utf-8')
assert 'PRESEASON_BED_HOLD_WALL_HOURS=34' in check
assert 'PRESEASON_BED_FINAL_RESET_BOOST_HOURS=2' in check
assert 'elapsedBedClaimableHours' in check
assert 'const expTarget=Math.min(target,characterExpCollectionCutoffMs(cfg));' in check
assert 'const expNaturalHours=Math.max(0,(expTarget-now)/3_600_000);' in check
assert 'hours:naturalHours' in check
assert 'preseasonBedReserveHours:PRESEASON_BED_HOLD_WALL_HOURS+PRESEASON_BED_FINAL_RESET_BOOST_HOURS' in check
print('Preseason Bed reserve patch applied: stop claims 34h early, reserve final +2h reset boost for 36h rollover Bed EXP.')
