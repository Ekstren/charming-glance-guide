from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')
marker = 'BED_STORAGE_DISABLED_V1'

if marker in s:
    print('Bed storage/hold automation already disabled')
    raise SystemExit(0)

# Remove the temporary stored-Bed field and all now-obsolete hold/reserve UI.
s = s.replace('          <label>Bed XP Stored<input id="bedStoredExp" type="number" min="0" step="1" value="0"></label>\n', '')
s = s.replace('          <input id="reserveHours" min="0" max="36" type="number" value="34" hidden>\n', '')
s = re.sub(r'\n<style id="bed-exp-hold-layout-v4">[\s\S]*?</style>\n', '\n', s, count=1)

# Keep Bed EXP / hour, but remove stored/hold state from defaults and persisted calculator inputs.
s = s.replace('    charLevel:130,charExp:0,bedExp:0,reserveHours:34,', '    charLevel:130,charExp:0,bedExp:0,')
s = s.replace("  const S2_SCORING_START_CHECKS=Object.freeze({\n    holdExp:false,preserveRealmTools:true\n  });",
              "  const S2_SCORING_START_CHECKS=Object.freeze({\n    preserveRealmTools:true\n  });")
s = s.replace("    'targetStars','historicalStars','charLevel','charExp','bedExp','bedStoredExp','reserveHours','skillLevel','relicLevel','fantomonLevel',",
              "    'targetStars','historicalStars','charLevel','charExp','bedExp','skillLevel','relicLevel','fantomonLevel',")
s = s.replace("  const CHECK_IDS = ['holdExp','preserveRealmTools'];", "  const CHECK_IDS = ['preserveRealmTools'];")
s = s.replace("    'charExp','bedExp','bedStoredExp',", "    'charExp','bedExp',")
s = s.replace("  let committedHoldExpState = !!document.getElementById('holdExp')?.checked;\n", '')

# Remove old hold-only helpers. Bed generation now ages directly like the other deterministic resources.
s = re.sub(
    r"\n  /\* BED_HOLD_STOPS_ALL_EXP_V1[\s\S]*?\n  function projectionResourceHoursAt",
    "\n  function projectionResourceHoursAt",
    s,
    count=1,
)
s = re.sub(
    r"\n  /\* BED_STORED_EXP_V1[\s\S]*?\n  function advanceCharacterSnapshot",
    "\n  function advanceCharacterSnapshot",
    s,
    count=1,
)

# Replace character projection with the simple model: current EXP + future Bed production.
project_pattern = r"  function projectCharacterTo\(targetMs,cfg=activeCalcConfig\(\)\)\{[\s\S]*?\n  \}\n  function projectCharacter\(cfg=activeCalcConfig\(\)\)\{"
project_replacement = '''  /* BED_STORAGE_DISABLED_V1
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
  function projectCharacter(cfg=activeCalcConfig()){'''
s, project_count = re.subn(project_pattern, project_replacement, s, count=1)
if project_count != 1:
    raise SystemExit(f'Expected to replace projectCharacterTo once, replaced {project_count}')

# Replace the stored/claimed Bed split in snapshot aging with one direct Bed EXP stream.
bed_age_pattern = r"    const bedSplit=bedExpHourSplitBetween\(snapshotAtMs,cappedNow,cfg,!!\$\('holdExp'\)\?\.checked\);[\s\S]*?    if\(storedExp>0 && \$\('bedStoredExp'\)\) \$\('bedStoredExp'\)\.value=String\(Math\.max\(0,n\('bedStoredExp',0\)\)\+storedExp\);"
bed_age_replacement = '''    const bedRate=Math.max(0,n('bedExp',0));
    const producedExp=bedRate*elapsedResourceHours + Math.max(0,Number(snapshotCarry.exp)||0);
    const wholeExp=Math.floor(producedExp+1e-9);
    snapshotCarry.exp=Math.max(0,producedExp-wholeExp);
    if(wholeExp>0) advanceCharacterSnapshot(wholeExp,cfg);'''
s, bed_age_count = re.subn(bed_age_pattern, bed_age_replacement, s, count=1)
if bed_age_count != 1:
    raise SystemExit(f'Expected to replace Bed snapshot aging once, replaced {bed_age_count}')

# Fix the old return expression, whose elapsedExpHours symbol belonged to the removed hold path.
s = s.replace('    return elapsedResourceHours>0 || elapsedExpHours>0 || elapsedRealmResets>0;',
              '    return elapsedResourceHours>0 || elapsedRealmResets>0;')

# Remove stale storage migration/state synchronization and reset handling.
s = s.replace("      if(Number(state.reserveHours)===36) state.reserveHours='34'; // BED_HOLD_34H_V1 migrate old hidden default\n", '')
s = s.replace("    committedHoldExpState=!!$('holdExp')?.checked;\n", '')
s = s.replace("    if($('holdExpLabel')) $('holdExpLabel').textContent=`Hold Bed EXP for ${cfg.nextName}`;\n", '')
s = s.replace("    $('projectionNote').textContent=`Uses exact server resets (${nextResetLocalLabel()} on this device); the free 2-hour speed-up is counted only when its checkbox is enabled and an actual reset occurs.`;",
              "    $('projectionNote').textContent=`Uses exact server resets (${nextResetLocalLabel()} on this device); future free 2-hour reset boosts are included automatically.`;")
s = s.replace("      : `Uses exact server resets (${nextResetLocalLabel()} on this device); the free 2-hour speed-up is counted only when its checkbox is enabled and an actual reset occurs.`;",
              "      : `Uses exact server resets (${nextResetLocalLabel()} on this device); future free 2-hour reset boosts are included automatically.`;")
s = s.replace("    committedHoldExpState=!!$('holdExp')?.checked;\n    updateGearLockUI(); localStorage.removeItem(STORAGE_KEY); saveState(); updateCalculator();",
              "    updateGearLockUI(); localStorage.removeItem(STORAGE_KEY); saveState(); updateCalculator();")

# CHECK_IDS no longer contains holdExp, so remove the dead special-case branch from its generic listener.
s = re.sub(
    r"\n      if\(id==='holdExp'\)\{[\s\S]*?\n        return;\n      \}",
    '',
    s,
    count=1,
)

# Replace the old method note so the UI does not describe a feature that is intentionally disabled.
s = re.sub(
    r'<p><b>Time projection:</b>[\s\S]*?</p>',
    '<p><b>Time projection:</b> Season deadlines and reset clocks are displayed in the timezone of the device opening this HTML. Internally the calculator still follows the Charming Glance server reset boundary, so travel/timezone changes do not alter the underlying server day. For now, Bed storage/hold automation is disabled; the planner uses the entered <b>Bed EXP per hour</b> directly through the season reset and includes the free 2-hour speed-up at each future reset.</p>',
    s,
    count=1,
)

# Diagnostics if any reserve-hours reference survived the targeted cleanup.
if 'reserveHours' in s:
    for m in re.finditer(r'reserveHours', s):
        a=max(0,m.start()-240); b=min(len(s),m.end()+360)
        print('--- reserveHours context ---')
        print(s[a:b].replace('\n','\\n'))

# Old saved fields are automatically dropped on the next save because they are no longer INPUT/CHECK ids.
for forbidden in ("bedStoredExp", "'holdExp'", '"holdExp"', 'reserveHours', 'committedHoldExpState', 'elapsedExpHours', '#holdExp', 'holdExpOption', 'holdExpLabel'):
    if forbidden in s:
        raise SystemExit(f'Removed Bed-storage token still present: {forbidden}')

if "id=\"bedExp\"" not in s:
    raise SystemExit('Bed EXP/hour input was accidentally removed')

p.write_text(s, encoding='utf-8')
print('Disabled Bed storage/hold automation while keeping ordinary Bed EXP/hour projection')
