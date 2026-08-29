from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
marker='RAW_FIRST_S2_TOOL_RESERVE_V1'
if marker in s:
    print('already applied')
    raise SystemExit(0)

old=r'''  function toolsFirstReserveSplit(key,reserveTarget,rawAvailable,resources,cfg=activeCalcConfig()){
    const target=Math.max(0,Number(reserveTarget)||0);
    const raw=Math.max(0,Number(rawAvailable)||0);
    if(target<=0 || (key!=='essence'&&key!=='sand')) return {target,toolRuns:0,toolValue:0,rawHeld:Math.min(raw,target),shortfall:Math.max(0,target-raw),reservePerRun:0,toolsAvailable:0};
    const inv=realmInventoryFor(key,cfg);
    const tools=Math.max(0,Math.floor(Number(inv?.banked)||0));
    const reservePerRun=Math.max(0,reserveYieldFor(key,cfg));
    if(reservePerRun<=0) return {target,toolRuns:0,toolValue:0,rawHeld:Math.min(raw,target),shortfall:Math.max(0,target-raw),reservePerRun,toolsAvailable:tools};
    const toolRuns=Math.min(tools,Math.ceil(target/reservePerRun));
    const toolValue=Math.min(target,toolRuns*reservePerRun);
    const rawNeed=Math.max(0,target-toolValue);
    const rawHeld=Math.min(raw,rawNeed);
    const shortfall=Math.max(0,rawNeed-rawHeld);
    return {target,toolRuns,toolValue,rawHeld,shortfall,reservePerRun,toolsAvailable:tools};
  }
'''
new=r'''  /* RAW_FIRST_S2_TOOL_RESERVE_V1
     Protect the S2 raw-material requirement with raw material first. Realm tools are
     reserved only for the uncovered remainder. This prevents Knuckles/Shovels (and any
     future Ore-tool reserve) from being needlessly locked when raw stock already covers
     the rollover target. */
  function rawFirstReserveSplit(key,reserveTarget,rawAvailable,resources,cfg=activeCalcConfig()){
    const target=Math.max(0,Number(reserveTarget)||0);
    const raw=Math.max(0,Number(rawAvailable)||0);
    const rawHeld=Math.min(raw,target);
    const uncovered=Math.max(0,target-rawHeld);
    if(target<=0 || (key!=='ore'&&key!=='essence'&&key!=='sand')){
      return {target,toolRuns:0,toolValue:0,rawHeld,shortfall:uncovered,reservePerRun:0,toolsAvailable:0};
    }
    const inv=realmInventoryFor(key,cfg);
    const tools=Math.max(0,Math.floor(Number(inv?.banked)||0));
    const reservePerRun=Math.max(0,reserveYieldFor(key,cfg));
    if(reservePerRun<=0 || uncovered<=0){
      return {target,toolRuns:0,toolValue:0,rawHeld,shortfall:uncovered,reservePerRun,toolsAvailable:tools};
    }
    const toolRuns=Math.min(tools,Math.ceil(uncovered/reservePerRun));
    const toolValue=Math.min(uncovered,toolRuns*reservePerRun);
    const shortfall=Math.max(0,uncovered-toolValue);
    return {target,toolRuns,toolValue,rawHeld,shortfall,reservePerRun,toolsAvailable:tools};
  }
'''
if old not in s:
    raise SystemExit('tools-first reserve helper not found')
s=s.replace(old,new,1)

# Route every reserve calculation/display through the new raw-first helper.
s=s.replace('toolsFirstReserveSplit(', 'rawFirstReserveSplit(')

# Keep comments and user-facing reserve hints consistent with the corrected logic.
repls={
    'Existing/planned Realm tools cover the enabled S2 reserve first. Only the raw\n      // remainder is withheld from the current-season raw-only optimizer.':
    'Raw material covers the enabled S2 reserve first. Realm tools are reserved only\n      // for any uncovered remainder; the protected raw amount is withheld from S1 spending.',
    'Material Realm tools cover the reserve first; raw Essence is held only for any remainder.':
    'Raw Essence covers the reserve first; Knuckles are reserved only for any uncovered remainder.',
    'Material Realm tools cover the reserve first; raw Sand is held only for any remainder.':
    'Raw Sand covers the reserve first; Shovels are reserved only for any uncovered remainder.',
    "`${fmt(split.toolRuns)} Knuckles first`": "`${fmt(split.toolRuns)} Knuckles reserved`",
    "`${fmt(split.toolRuns)} Shovels first`": "`${fmt(split.toolRuns)} Shovels reserved`",
}
for a,b in repls.items():
    s=s.replace(a,b)

p.write_text(s,encoding='utf-8')
print('changed S2 reserve coverage to raw-first, tools-only-for-gap')
