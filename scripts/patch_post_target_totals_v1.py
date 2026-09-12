from pathlib import Path

index = Path('index.html')
runtime = Path('assets/runtime.js')

html = index.read_text(encoding='utf-8')
js = runtime.read_text(encoding='utf-8')

# UI wording: this section is now a season-end total, not just incremental gains.
html = html.replace(
    '<div><span>Estimated gains after target</span><small id="postTargetWindow">—</small></div>',
    '<div><span>Estimated post-target totals</span><small id="postTargetWindow">—</small></div>',
    1,
)
html = html.replace(
    '<div><span>Fantomon Treats</span><b id="postTargetTreatGain">—</b><small>Basic-equivalent gained</small></div>',
    '<div><span>Fantomon Treats</span><b id="postTargetTreatGain">—</b><small>Basic-equivalent total</small></div>',
    1,
)

# Keep enough context so live radio/input changes can recalculate totals without rerunning the optimizer.
js = js.replace(
    "  let postTargetLastReachMs=NaN;\n  let postTargetLastCfg=null;",
    "  let postTargetLastReachMs=NaN;\n  let postTargetLastCfg=null;\n  let postTargetLastPlan=null;\n  let postTargetLastPEnd=null;",
    1,
)
js = js.replace(
    "      if(Number.isFinite(postTargetLastReachMs) && postTargetLastCfg) renderPostTargetGains(postTargetLastReachMs,postTargetLastCfg);",
    "      if(Number.isFinite(postTargetLastReachMs) && postTargetLastCfg && postTargetLastPlan && postTargetLastPEnd) renderPostTargetGains(postTargetLastReachMs,postTargetLastPlan,postTargetLastPEnd,postTargetLastCfg);",
    1,
)
js = js.replace(
    "    postTargetLastReachMs=NaN;\n    postTargetLastCfg=null;",
    "    postTargetLastReachMs=NaN;\n    postTargetLastCfg=null;\n    postTargetLastPlan=null;\n    postTargetLastPEnd=null;",
    1,
)

# Insert a target-moment carry calculation. This mirrors the target-fundability stamina/tool logic,
# then reports what is actually left AFTER paying for the recommended route at the target moment.
anchor = "  function postTargetRawGains(reached,cfg,state=selectedPostTargetToolState()){"
if anchor not in js:
    raise SystemExit('postTargetRawGains anchor missing')
helper = r'''  function postTargetCarryAt(reached,plan,pEnd,cfg=activeCalcConfig()){
    const emptyCarry={ore:0,essence:0,sand:0,treat:0,hammers:0,knuckles:0,shovels:0};
    if(!plan || !Number.isFinite(Number(reached))) return emptyCarry;
    const pAt=projectCharacterTo(reached,cfg);
    const base=projectedResourcesTo(reached,cfg);
    const total=Math.max(0,Math.floor(base.staminaNodes||0));
    const empty={ore:0,essence:0,sand:0,rolla:0,unassigned:0};
    const map=base.yields?.map||{};
    const allocationCandidates=[];
    if(!base.yields?.mapReady || total<=0){
      allocationCandidates.push({...empty,unassigned:total});
    }else if(staminaMode()==='auto'){
      for(const key of ['ore','essence','sand']) if((Number(map[key])||0)>0) allocationCandidates.push({...empty,[key]:total});
    }else{
      const key=staminaMode();
      allocationCandidates.push((Number(map[key])||0)>0?{...empty,[key]:total}:{...empty,unassigned:total});
    }
    if(!allocationCandidates.length) allocationCandidates.push({...empty,unassigned:total});

    for(const allocation of allocationCandidates){
      const resources=applyStaminaAllocation(base,allocation,cfg);
      if((Number(plan.treatCost)||0)>(Number(resources.treat)||0)+0.5) continue;
      if(resources.refinedTracked && (Number(plan.refinedCost)||0)>(Number(resources.refined)||0)+0.5) continue;
      const oreTop=realmTopupForMoment('ore',plan.oreCost,resources,reached,pAt,cfg);
      const essenceTop=realmTopupForMoment('essence',plan.essenceCost,resources,reached,pAt,cfg);
      const sandTop=realmTopupForMoment('sand',plan.sandCost,resources,reached,pAt,cfg);
      if(!(oreTop.feasible&&essenceTop.feasible&&sandTop.feasible)) continue;
      return {
        ore:Math.max(0,(Number(resources.ore)||0)-(Number(plan.oreCost)||0)),
        essence:Math.max(0,(Number(resources.essence)||0)-(Number(plan.essenceCost)||0)),
        sand:Math.max(0,(Number(resources.sand)||0)-(Number(plan.sandCost)||0)),
        treat:Math.max(0,(Number(resources.treat)||0)-(Number(plan.treatCost)||0)),
        hammers:Math.max(0,Math.floor(Number(oreTop.bankedRemaining)||0)+Math.floor(Number(oreTop.sparePurchasedRuns)||0)),
        knuckles:Math.max(0,Math.floor(Number(essenceTop.bankedRemaining)||0)+Math.floor(Number(essenceTop.sparePurchasedRuns)||0)),
        shovels:Math.max(0,Math.floor(Number(sandTop.bankedRemaining)||0)+Math.floor(Number(sandTop.sparePurchasedRuns)||0))
      };
    }
    return emptyCarry;
  }

'''
js = js.replace(anchor, helper + anchor, 1)

# Replace the renderer with total math = carry remaining at target + gains acquired after target.
old_sig = "  function renderPostTargetGains(reached,cfg=activeCalcConfig()){"
if old_sig not in js:
    raise SystemExit('renderPostTargetGains signature missing')
js = js.replace(old_sig, "  function renderPostTargetGains(reached,plan,pEnd,cfg=activeCalcConfig()){", 1)
js = js.replace(
    "    postTargetLastReachMs=reached;\n    postTargetLastCfg=cfg;",
    "    postTargetLastReachMs=reached;\n    postTargetLastCfg=cfg;\n    postTargetLastPlan=plan;\n    postTargetLastPEnd=pEnd;",
    1,
)
js = js.replace(
    "    const gains=postTargetRawGains(reached,cfg,state);",
    "    const carry=postTargetCarryAt(reached,plan,pEnd,cfg);\n    const gains=postTargetRawGains(reached,cfg,state);",
    1,
)
js = js.replace(
    "    const tools={ore:daily.ore*toolMultiplier,essence:daily.essence*toolMultiplier,sand:daily.sand*toolMultiplier};",
    "    const tools={\n      ore:carry.hammers+daily.ore*toolMultiplier,\n      essence:carry.knuckles+daily.essence*toolMultiplier,\n      sand:carry.shovels+daily.sand*toolMultiplier\n    };\n    const totals={\n      ore:carry.ore+gains.ore,\n      essence:carry.essence+gains.essence,\n      sand:carry.sand+gains.sand,\n      treat:carry.treat+gains.treat\n    };",
    1,
)
js = js.replace(
    "    if($('postTargetWindow')) $('postTargetWindow').textContent=`${compactDurationMs(Math.max(0,end-reached))} from target to season end`;\n    if($('postTargetOreGain')) $('postTargetOreGain').textContent=`+${fmt(Math.floor(gains.ore))}`;\n    if($('postTargetEssenceGain')) $('postTargetEssenceGain').textContent=`+${fmt(Math.floor(gains.essence))}`;\n    if($('postTargetSandGain')) $('postTargetSandGain').textContent=`+${fmt(Math.floor(gains.sand))}`;\n    if($('postTargetTreatGain')) $('postTargetTreatGain').textContent=`+${fmt(Math.floor(gains.treat))}`;\n    if($('postTargetHammerGain')) $('postTargetHammerGain').textContent=`+${fmt(tools.ore)} Hammers`;\n    if($('postTargetKnuckleGain')) $('postTargetKnuckleGain').textContent=`+${fmt(tools.essence)} Knuckles`;\n    if($('postTargetShovelGain')) $('postTargetShovelGain').textContent=`+${fmt(tools.sand)} Shovels`;",
    "    if($('postTargetWindow')) $('postTargetWindow').textContent=`${compactDurationMs(Math.max(0,end-reached))} after target · season-end totals`;\n    if($('postTargetOreGain')) $('postTargetOreGain').textContent=fmt(Math.floor(totals.ore));\n    if($('postTargetEssenceGain')) $('postTargetEssenceGain').textContent=fmt(Math.floor(totals.essence));\n    if($('postTargetSandGain')) $('postTargetSandGain').textContent=fmt(Math.floor(totals.sand));\n    if($('postTargetTreatGain')) $('postTargetTreatGain').textContent=fmt(Math.floor(totals.treat));\n    if($('postTargetHammerGain')) $('postTargetHammerGain').textContent=`${fmt(tools.ore)} Hammers total`;\n    if($('postTargetKnuckleGain')) $('postTargetKnuckleGain').textContent=`${fmt(tools.essence)} Knuckles total`;\n    if($('postTargetShovelGain')) $('postTargetShovelGain').textContent=`${fmt(tools.sand)} Shovels total`;",
    1,
)

# Target timing now passes the fixed target route so carry-at-target can be calculated accurately.
js = js.replace("    renderPostTargetGains(reached,cfg);", "    renderPostTargetGains(reached,plan,pEnd,cfg);", 1)

# Safety checks.
required = [
    'Estimated post-target totals',
    'Basic-equivalent total',
]
for text in required:
    if text not in html:
        raise SystemExit(f'missing HTML marker: {text}')
for text in [
    'function postTargetCarryAt(',
    'const totals={',
    'Hammers total',
    'renderPostTargetGains(reached,plan,pEnd,cfg)',
]:
    if text not in js:
        raise SystemExit(f'missing JS marker: {text}')
if 'value="save"> Save Stamina' in html:
    raise SystemExit('Save Stamina unexpectedly present')

index.write_text(html, encoding='utf-8')
runtime.write_text(js, encoding='utf-8')
