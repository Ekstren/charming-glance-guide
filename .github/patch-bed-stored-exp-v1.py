from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')
marker = 'BED_STORED_EXP_V1'
if marker in text:
    print('already applied')
    raise SystemExit(0)


def replace_once(old: str, new: str, label: str):
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly one match, found {count}; refusing unsafe patch')
    text = text.replace(old, new, 1)


old_ui = '''          <label>Bed EXP per hour<input id="bedExp" type="number" value="0"></label>
          <div class="findMaxCell"><span>Maximum target</span><div class="maxTargetControl"><button id="findMaxStars" type="button">Find max achievable</button><small id="maxAchievableStatus"></small></div></div>'''
new_ui = '''          <label>Bed EXP per hour<input id="bedExp" type="number" value="0"></label>
          <label>Bed XP Stored<input id="bedStoredExp" type="number" min="0" step="1" value="0"></label>'''
replace_once(old_ui, new_ui, 'Bed stored EXP field')

replace_once(
    "    'targetStars','historicalStars','charLevel','charExp','bedExp','reserveHours','skillLevel','relicLevel','fantomonLevel',",
    "    'targetStars','historicalStars','charLevel','charExp','bedExp','bedStoredExp','reserveHours','skillLevel','relicLevel','fantomonLevel',",
    'persist Bed stored EXP'
)

replace_once(
    "  let snapshotStateLoaded = false;\n",
    "  let snapshotStateLoaded = false;\n  let committedHoldExpState = !!document.getElementById('holdExp')?.checked;\n",
    'committed Hold state'
)

helper_anchor = '''  function advanceCharacterSnapshot(deltaExp,cfg=CALC_SEASONS[snapshotSeason] || activeCalcConfig()){
'''
helper = '''  /* BED_STORED_EXP_V1
     Bed EXP is a first-class persisted balance. While Hold is active, generation before
     the reserve cutoff is claimed normally and generation after the cutoff is routed into
     Bed XP Stored. Turning Hold off claims the stored balance into the character. */
  function bedHoursInRange(startMs,endMs){
    const start=Number(startMs)||0,end=Number(endMs)||0;
    if(end<=start) return 0;
    return Math.max(0,(end-start)/3_600_000)+2*countFuturePacificResets(start,end);
  }
  function bedExpHourSplitBetween(startMs,endMs,cfg=activeCalcConfig(),holdEnabled=!!$('holdExp')?.checked){
    const start=Math.max(0,Number(startMs)||0);
    const end=Math.max(start,Math.min(Number(endMs)||start,cfg.end.getTime()));
    if(end<=start) return {claimedHours:0,storedHours:0};
    if(!holdEnabled) return {claimedHours:bedHoursInRange(start,end),storedHours:0};
    const reserve=clamp(n('reserveHours',34),0,36);
    if(reserve<=0) return {claimedHours:bedHoursInRange(start,end),storedHours:0};
    const reserveStart=cfg.end.getTime()-reserve*3_600_000;
    const claimedEnd=Math.min(end,reserveStart);
    const storedStart=Math.max(start,reserveStart);
    return {
      claimedHours:claimedEnd>start?bedHoursInRange(start,claimedEnd):0,
      storedHours:end>storedStart?bedHoursInRange(storedStart,end):0
    };
  }
  function claimStoredBedExp(cfg=activeCalcConfig()){
    const stored=Math.max(0,Math.floor(n('bedStoredExp',0)));
    if(stored<=0) return 0;
    advanceCharacterSnapshot(stored,cfg);
    if($('bedStoredExp')) $('bedStoredExp').value='0';
    return stored;
  }

'''
replace_once(helper_anchor, helper + helper_anchor, 'Bed routing helpers')

old_roll = '''    const oldExpHours = projectionExpHoursAt(snapshotAtMs,cfg);
    const newExpHours = projectionExpHoursAt(cappedNow,cfg);
    const elapsedExpHours = Math.max(0, oldExpHours-newExpHours);
    const gainedExpFloat = Math.max(0,n('bedExp',0))*elapsedExpHours + Math.max(0,Number(snapshotCarry.exp)||0);
    const gainedExp = Math.floor(gainedExpFloat + 1e-9);
    snapshotCarry.exp = Math.max(0, gainedExpFloat-gainedExp);
    if(gainedExp>0) advanceCharacterSnapshot(gainedExp,cfg);
'''
new_roll = '''    const bedSplit=bedExpHourSplitBetween(snapshotAtMs,cappedNow,cfg,!!$('holdExp')?.checked);
    const bedRate=Math.max(0,n('bedExp',0));
    let claimedExpFloat=bedRate*bedSplit.claimedHours;
    let storedExpFloat=bedRate*bedSplit.storedHours;
    const expCarry=Math.max(0,Number(snapshotCarry.exp)||0);
    // Carry the sub-EXP remainder into whichever destination is active at the end of the interval.
    if(bedSplit.storedHours>0) storedExpFloat+=expCarry;
    else claimedExpFloat+=expCarry;
    const claimedExp=Math.floor(claimedExpFloat+1e-9);
    const storedExp=Math.floor(storedExpFloat+1e-9);
    snapshotCarry.exp=Math.max(0,(claimedExpFloat-claimedExp)+(storedExpFloat-storedExp));
    if(claimedExp>0) advanceCharacterSnapshot(claimedExp,cfg);
    if(storedExp>0 && $('bedStoredExp')) $('bedStoredExp').value=String(Math.max(0,n('bedStoredExp',0))+storedExp);
'''
replace_once(old_roll, new_roll, 'snapshot Bed EXP routing')

old_project = '''    let lvl=current.level, exp=current.exp;
    const endMs=cfg.end.getTime();
'''
new_project = '''    let lvl=current.level, exp=current.exp;
    // Defensive projection: if a stored balance exists while Hold is off, it is immediately claimable.
    if(!$('holdExp')?.checked) exp+=Math.max(0,n('bedStoredExp',0));
    const endMs=cfg.end.getTime();
'''
replace_once(old_project, new_project, 'project stored Bed EXP')

old_load = '''    snapshotStateLoaded=true;
    if(hadState) rollSnapshotForward(Date.now(),false);
'''
new_load = '''    committedHoldExpState=!!$('holdExp')?.checked;
    snapshotStateLoaded=true;
    if(hadState) rollSnapshotForward(Date.now(),false);
'''
replace_once(old_load, new_load, 'load committed Hold state')

old_reset = '''    gearLocked=false; snapshotAtMs=Date.now(); snapshotSeason=cfg.key; snapshotCarry={ore:0,essence:0,sand:0,treat:0,exp:0}; snapshotStateLoaded=true;
    updateGearLockUI(); localStorage.removeItem(STORAGE_KEY); saveState(); updateCalculator();
'''
new_reset = '''    gearLocked=false; snapshotAtMs=Date.now(); snapshotSeason=cfg.key; snapshotCarry={ore:0,essence:0,sand:0,treat:0,exp:0}; snapshotStateLoaded=true;
    committedHoldExpState=!!$('holdExp')?.checked;
    updateGearLockUI(); localStorage.removeItem(STORAGE_KEY); saveState(); updateCalculator();
'''
replace_once(old_reset, new_reset, 'reset committed Hold state')

old_checks = '''    CHECK_IDS.forEach(id=>$(id)?.addEventListener('change',()=>{
      resetMaxAchievableUi();
      markManualSnapshot(id);
      // Checkbox state must be persisted before recalculation so S2 reserve toggles
      // immediately add/remove their protected resource pools.
      saveState();
      if(calculatorInitialized) updateCalculator();
      else initializeCalculatorIfNeeded();
    }));
'''
new_checks = '''    CHECK_IDS.forEach(id=>$(id)?.addEventListener('change',()=>{
      resetMaxAchievableUi();
      if(id==='holdExp'){
        const el=$('holdExp');
        const next=!!el.checked;
        const previous=committedHoldExpState;
        // Age elapsed Bed production under the state that was actually active, then commit the toggle.
        el.checked=previous;
        rollSnapshotForward(Date.now(),false);
        el.checked=next;
        committedHoldExpState=next;
        if(snapshotSeason===seasonKeyAt(Date.now())) snapshotAtMs=Date.now();
        if(previous && !next) claimStoredBedExp(activeCalcConfig());
      } else {
        markManualSnapshot(id);
      }
      // Checkbox state must be persisted before recalculation so reserve changes apply immediately.
      saveState();
      if(calculatorInitialized) updateCalculator();
      else initializeCalculatorIfNeeded();
    }));
'''
replace_once(old_checks, new_checks, 'Hold toggle claim behavior')

listener = "    $('findMaxStars')?.addEventListener('click',findMaxAchievableStars);\n"
if listener in text:
    text = text.replace(listener, '', 1)

old_method = 'A 34-hour EXP reserve is a hard current-season Bed cutoff: natural Bed accrual and reset speed-ups after the hold begins stay banked for Season 2 and do not count toward the Season 1 score.'
new_method = 'A 34-hour EXP reserve routes natural Bed accrual and reset speed-ups after the hold begins into Bed XP Stored. Unchecking Hold claims that stored EXP into the player, and the stored balance persists through season rollover.'
replace_once(old_method, new_method, 'Bed method explanation')

path.write_text(text, encoding='utf-8')
print('patched persisted Bed XP storage, routing, and claim behavior')
