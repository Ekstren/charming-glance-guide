from pathlib import Path

p = Path('assets/runtime.js')
s = p.read_text()

old = """  function postTargetCarryAt(reached,plan,pEnd,cfg=activeCalcConfig()){
    const emptyCarry={ore:0,essence:0,sand:0,treat:0,hammers:0,knuckles:0,shovels:0,staminaUnused:0};
"""
new = """  function postTargetCarryAt(reached,plan,pEnd,cfg=activeCalcConfig()){
    const emptyCarry={ore:0,essence:0,sand:0,treat:0,hammers:0,knuckles:0,shovels:0,staminaUnused:0,valid:false,resourceSnapshot:null,oreTop:null,essenceTop:null,sandTop:null};
"""
if old not in s:
    raise SystemExit('emptyCarry pattern not found')
s = s.replace(old, new, 1)

old = """        shovels:Math.max(0,Math.floor(Number(sandTop.bankedRemaining)||0)+Math.floor(Number(sandTop.sparePurchasedRuns)||0)),
        staminaUnused:Math.max(0,Number(resources.staminaUnused)||0)
      };
"""
new = """        shovels:Math.max(0,Math.floor(Number(sandTop.bankedRemaining)||0)+Math.floor(Number(sandTop.sparePurchasedRuns)||0)),
        staminaUnused:Math.max(0,Number(resources.staminaUnused)||0),
        valid:true,
        resourceSnapshot:resources,
        oreTop,essenceTop,sandTop
      };
"""
if old not in s:
    raise SystemExit('carry return pattern not found')
s = s.replace(old, new, 1)

marker = """  function postTargetRawGains(reached,cfg,state=selectedPostTargetToolState(),staminaCarry=0){
"""
helper = """  function renderTargetResourceSnapshot(reached,plan,pEnd,cfg=activeCalcConfig()){
    if(!Number.isFinite(Number(reached)) || !plan) return;
    const carry=postTargetCarryAt(reached,plan,pEnd,cfg);
    const r=carry?.resourceSnapshot;
    if(!carry?.valid || !r) return;

    const added=r.staminaAdded||{ore:0,essence:0,sand:0,rolla:0};
    const allocation=r.staminaAllocation||{ore:0,essence:0,sand:0,rolla:0,unassigned:r.staminaNodes||0};
    renderStaminaCurrentPlan(allocation,added,r);
    const oreStam=added.ore?` · Stamina +${fmtCompact(added.ore)}`:'';
    const essStam=added.essence?` · Stamina +${fmtCompact(added.essence)}`:'';
    const sandStam=added.sand?` · Stamina +${fmtCompact(added.sand)}`:'';
    if($('oreProjected')) $('oreProjected').textContent=`Projected to target: ${fmtCompact(Number(r.ore)||0)}${oreStam}`;
    if($('essenceProjected')) $('essenceProjected').textContent=`Projected to target: ${fmtCompact(Number(r.essence)||0)}${essStam}`;
    if($('sandProjected')) $('sandProjected').textContent=`Projected to target: ${fmtCompact(Number(r.sand)||0)}${sandStam}`;
    if($('treatProjected')) $('treatProjected').textContent=`Projected to target: ${fmtCompact(Number(r.treat)||0)} basic-eq.`;

    // The upper cards are the inventory snapshot at the instant the requested score is reached.
    // Everything after that instant belongs only in the post-target season-end totals below.
    setRawRemaining('oreBalance',0,carry.ore);
    setRawRemaining('essenceBalance',0,carry.essence);
    setRawRemaining('sandBalance',0,carry.sand);
    setRawRemaining('treatBalance',0,carry.treat,'basic-eq.');

    const yields=r.yields||automaticResourceYields(n('charLevel',cfg.key==='s2'?100:122),cfg);
    const oreYield=Math.max(0,Number(yields.orePerHammer)||0);
    const essenceYield=Math.max(0,Number(yields.essencePerKnuckles)||0);
    const sandYield=Math.max(0,Number(yields.sandPerShovel)||0);
    setToolBalance('oreToolBalance',carry.oreTop,0,oreYield,'Hammers',0,carry.ore);
    setToolBalance('essenceToolBalance',carry.essenceTop,0,essenceYield,'Knuckles',0,carry.essence);
    setToolBalance('sandToolBalance',carry.sandTop,0,sandYield,'Shovels',0,carry.sand);
    appendStaminaProjection('oreToolBalance',allocation.ore,added.ore,'Ore');
    appendStaminaProjection('essenceToolBalance',allocation.essence,added.essence,'Essence');
    appendStaminaProjection('sandToolBalance',allocation.sand,added.sand,'Sand');
  }

"""
if marker not in s:
    raise SystemExit('postTargetRawGains marker not found')
s = s.replace(marker, helper + marker, 1)

old = """    appendStaminaProjection('oreToolBalance',allocation.ore,added.ore,'Ore');
    appendStaminaProjection('essenceToolBalance',allocation.essence,added.essence,'Essence');
    appendStaminaProjection('sandToolBalance',allocation.sand,added.sand,'Sand');

    renderRealmDailyRecommendations(plan,resources,cfg);
"""
new = """    appendStaminaProjection('oreToolBalance',allocation.ore,added.ore,'Ore');
    appendStaminaProjection('essenceToolBalance',allocation.essence,added.essence,'Essence');
    appendStaminaProjection('sandToolBalance',allocation.sand,added.sand,'Sand');

    // TARGET_SNAPSHOT_SPLIT_V1: once target timing is known, the upper resource cards stop
    // at that exact target moment. The lower post-target section alone continues to season end.
    if(Number.isFinite(postTargetLastReachMs) && !resourceBlocked){
      renderTargetResourceSnapshot(postTargetLastReachMs,plan,p,cfg);
    }

    renderRealmDailyRecommendations(plan,resources,cfg);
"""
if old not in s:
    raise SystemExit('top render insertion pattern not found')
s = s.replace(old, new, 1)

p.write_text(s)
