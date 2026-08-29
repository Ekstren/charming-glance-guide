from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')
marker = 'BED_HOLD_STOPS_ALL_EXP_V1'
if marker in text:
    print('already applied')
    raise SystemExit(0)

old_projection = """  function projectionExpHoursAt(ms,cfg=activeCalcConfig()){
    const capped=Math.min(ms,cfg.end.getTime());
    const wallHours=Math.max(0,(cfg.end.getTime()-capped)/3_600_000);
    const reserve=$('holdExp')?.checked?clamp(n('reserveHours',34),0,36):0;
    const naturalHours=Math.max(0,wallHours-reserve);
    const boostHours=2*countFuturePacificResets(capped,cfg.end.getTime());
    return naturalHours+boostHours;
  }
"""
new_projection = """  /* BED_HOLD_STOPS_ALL_EXP_V1
     Once the Bed hold begins, all Bed-generated EXP is banked for the next season and is
     not collectible for the current-season score. This includes both natural Bed accrual
     and the free reset speed-up. */
  function projectionExpHoursAt(ms,cfg=activeCalcConfig()){
    const endMs=cfg.end.getTime();
    const reserve=$('holdExp')?.checked?clamp(n('reserveHours',34),0,36):0;
    const collectibleEnd=reserve>0?endMs-reserve*3_600_000:endMs;
    const capped=Math.min(ms,collectibleEnd);
    if(capped>=collectibleEnd) return 0;
    const naturalHours=Math.max(0,(collectibleEnd-capped)/3_600_000);
    const boostHours=2*countFuturePacificResets(capped,collectibleEnd);
    return naturalHours+boostHours;
  }
"""
if old_projection not in text:
    raise SystemExit('projectionExpHoursAt block not found; refusing unsafe patch')
text = text.replace(old_projection, new_projection, 1)

old_project = """    const reserveStart=endMs-reserve*3_600_000;
    // Natural Bed EXP stops when the reserve window starts; reset speed-ups remain usable.
    const naturalEnd=Math.min(target,reserveStart);
    const naturalHours=Math.max(0,(naturalEnd-now)/3_600_000);
    const boostResets=countFuturePacificResets(now,target);
    const boostHours=2*boostResets;
"""
new_project = """    const reserveStart=endMs-reserve*3_600_000;
    // The hold is a hard S1 collection cutoff: natural Bed EXP and reset speed-ups after
    // reserveStart stay banked for S2 and cannot increase the S1 projected score.
    const collectibleEnd=reserve>0?Math.min(target,reserveStart):target;
    const naturalHours=Math.max(0,(collectibleEnd-now)/3_600_000);
    const boostResets=collectibleEnd>now?countFuturePacificResets(now,collectibleEnd):0;
    const boostHours=2*boostResets;
"""
if old_project not in text:
    raise SystemExit('projectCharacterTo Bed block not found; refusing unsafe patch')
text = text.replace(old_project, new_project, 1)

old_method = "A 34-hour EXP reserve removes natural Bed hours only; reset boost hours inside that reserve still count."
new_method = "A 34-hour EXP reserve is a hard current-season Bed cutoff: natural Bed accrual and reset speed-ups after the hold begins stay banked for Season 2 and do not count toward the Season 1 score."
if old_method not in text:
    raise SystemExit('Bed hold method text not found; refusing unsafe patch')
text = text.replace(old_method, new_method, 1)

path.write_text(text, encoding='utf-8')
print('patched Bed hold to stop all current-season Bed EXP')
