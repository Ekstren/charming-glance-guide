from pathlib import Path

runtime=Path('assets/runtime.js')
s=runtime.read_text()

# 1) New/reset S2 snapshots should start with a realistic Bed EXP rate.
s=s.replace("charLevel:130,charExp:0,bedExp:0,", "charLevel:130,charExp:0,bedExp:400000,", 1)

# 2) Trim each progression option list to the first option that can satisfy the target
#    with every other category held at its current/base state. Anything beyond that point
#    is strictly dominated for this target: it spends more in that category and only adds
#    overshoot, because no other category can be lowered below its current state.
old="""  // Structural upgrade options do not depend on the projected resource mix. Build them once
  // and reuse them across the auto-Stamina passes instead of rebuilding thousands of arrays.
  function createPlanningContext(baseScore,desired,p,cfg=activeCalcConfig()){
    const current=characterSnapshot(cfg);
    const currentCaps=categoryInputCapsForCharacter(current.level,cfg);
    const projectedCaps=optimizerCategoryCaps(p,cfg);
    const baseGear=gearStateFromUser(cfg,currentCaps.gear,cfg.key==='s2'?130:143).levels.slice();
    const cats=planningCategoryState(cfg,currentCaps,projectedCaps);
    const gearOptions=buildGearOptions(baseGear,cfg,desired,projectedCaps.gear);
    const lastOptionCost=options=>{
      const last=Array.isArray(options)&&options.length?options[options.length-1]:null;
      return Math.max(0,Number(last?.cost)||0);
    };
    // Total material still productively spendable from the CURRENT category levels up to
    // the safe projected cap. This is independent of whichever candidate plan wins.
    const headroomCosts={
      ore:Math.max(0,Number(gearOptions?.[gearOptions.length-1]?.oreCost)||0),
      essence:lastOptionCost(cats.skillOptions),
      sand:lastOptionCost(cats.relicOptions),
      treat:lastOptionCost(cats.fantoOptions)
    };
    return {baseScore,desired,p,cfg,current,currentCaps,projectedCaps,baseGear,cats,gearOptions,headroomCosts,charScore:characterScore(p,cfg)};
  }
"""
new="""  // Structural upgrade options do not depend on the projected resource mix. Build them once
  // and reuse them across the auto-Stamina passes instead of rebuilding thousands of arrays.
  // TARGET_FRONTIER_TRIM_V1: the live S2 tables extend far beyond any one Primostar target.
  // For a specific target, options AFTER the first point where one category alone can cover
  // the remaining score gap (with every other category held at its current floor) are strictly
  // dominated: they cost more in that category and can only add overshoot. Keep the full arrays
  // only for productive-headroom/scarcity math, and search the exact target-bounded frontiers.
  function targetBoundedOptions(options,scoreNeeded){
    if(!Array.isArray(options)||options.length<=1) return options||[];
    const need=Math.max(Number(options[0]?.score)||0,Number(scoreNeeded)||0);
    let lo=0,hi=options.length-1,ans=options.length;
    while(lo<=hi){
      const mid=(lo+hi)>>1;
      if((Number(options[mid]?.score)||0)>=need-1e-9){ans=mid;hi=mid-1;}else lo=mid+1;
    }
    return ans>=options.length?options:options.slice(0,ans+1);
  }
  function createPlanningContext(baseScore,desired,p,cfg=activeCalcConfig()){
    const current=characterSnapshot(cfg);
    const currentCaps=categoryInputCapsForCharacter(current.level,cfg);
    const projectedCaps=optimizerCategoryCaps(p,cfg);
    const baseGear=gearStateFromUser(cfg,currentCaps.gear,cfg.key==='s2'?130:143).levels.slice();
    const fullCats=planningCategoryState(cfg,currentCaps,projectedCaps);
    const fullGearOptions=buildGearOptions(baseGear,cfg,desired,projectedCaps.gear);
    const lastOptionCost=options=>{
      const last=Array.isArray(options)&&options.length?options[options.length-1]:null;
      return Math.max(0,Number(last?.cost)||0);
    };
    // Total material still productively spendable from the CURRENT category levels up to
    // the safe projected cap. This stays based on the FULL legal option arrays so target
    // trimming cannot change scarcity economics or recommendation ordering.
    const headroomCosts={
      ore:Math.max(0,Number(fullGearOptions?.[fullGearOptions.length-1]?.oreCost)||0),
      essence:lastOptionCost(fullCats.skillOptions),
      sand:lastOptionCost(fullCats.relicOptions),
      treat:lastOptionCost(fullCats.fantoOptions)
    };
    const charScore=characterScore(p,cfg);
    const baseGearScore=Number(fullGearOptions?.[0]?.score)||0;
    const baseSkillScore=Number(fullCats.skill?.score)||0;
    const baseRelicScore=Number(fullCats.relic?.score)||0;
    const baseFantoScore=Number(fullCats.fanto?.score)||0;
    const gearOptions=targetBoundedOptions(fullGearOptions,desired-charScore-baseSkillScore-baseRelicScore-baseFantoScore);
    const cats={...fullCats,
      skillOptions:targetBoundedOptions(fullCats.skillOptions,desired-charScore-baseGearScore-baseRelicScore-baseFantoScore),
      relicOptions:targetBoundedOptions(fullCats.relicOptions,desired-charScore-baseGearScore-baseSkillScore-baseFantoScore),
      fantoOptions:targetBoundedOptions(fullCats.fantoOptions,desired-charScore-baseGearScore-baseSkillScore-baseRelicScore)
    };
    return {baseScore,desired,p,cfg,current,currentCaps,projectedCaps,baseGear,cats,gearOptions,headroomCosts,charScore};
  }
"""
if old not in s:
    raise SystemExit('createPlanningContext anchor not found')
s=s.replace(old,new,1)

# 3) Gate the heavy S2 optimizer by projected season-end unlock, not an arbitrary current-level preview threshold.
old="""    const cfg=activeCalcConfig();
    if(renderCalculatorSeasonChrome(cfg)){ clearCalcForRollover(cfg); return; }
    if(cfg.key==='s2' && characterSnapshot(cfg).level<S2_PLANNER_START_LEVEL){ clearS2PreScoring(cfg); return; }
    const p=projectCharacter(cfg);
"""
new="""    const cfg=activeCalcConfig();
    if(renderCalculatorSeasonChrome(cfg)){ clearCalcForRollover(cfg); return; }
    const p=projectCharacter(cfg);
    // PROJECTED_SCORING_GATE_V1: S2 progression cannot produce Primostar Season Power unless
    // the account is projected to reach the Lv.130 scoring unlock before season end. Skip the
    // expensive optimizer entirely below that point; current level alone is not the gate.
    if(cfg.key==='s2' && p.decimal<cfg.scoreFloor-1e-9){ clearS2PreScoring(cfg); return; }
"""
if old not in s:
    raise SystemExit('updateCalculator S2 gate anchor not found')
s=s.replace(old,new,1)

# Update the paused-state copy so it explains the projected-level rule rather than old Lv.120 preview behavior.
old="""    $('targetMessage').textContent=`Season Power scoring still uses the Lv.${cfg.scoreFloor} baseline, but forward planning becomes available at Lv.${S2_PLANNER_START_LEVEL}. Current Lv.${current.level} is below that planning threshold, so the calculator stays paused until Lv.${S2_PLANNER_START_LEVEL}.`;
    if($('targetStatus')){$('targetStatus').textContent='locked';$('targetStatus').classList.remove('notMet');}
    $('optimizerSummary').textContent=`Return at Lv.${S2_PLANNER_START_LEVEL} and enter your actual state. From there the calculator projects EXP and resources through the Lv.${cfg.scoreFloor} Season Power baseline and season end.`;
"""
new="""    $('targetMessage').textContent=`Projected season-end level is Lv.${p.level} (${(p.pct*100).toFixed(1)}%), below the Lv.${cfg.scoreFloor} Season Power unlock. The optimizer stays paused because no S2 progression Primostars can be earned before the season ends.`;
    if($('targetStatus')){$('targetStatus').textContent='locked';$('targetStatus').classList.remove('notMet');}
    $('optimizerSummary').textContent=`Raise the projected season-end level to Lv.${cfg.scoreFloor} or higher (for example through Bed EXP) and the optimizer will activate automatically.`;
"""
if old not in s:
    raise SystemExit('clearS2PreScoring copy anchor not found')
s=s.replace(old,new,1)

# Target-star edits should not age/rewrite the account snapshot just from focusing that goal field.
s=s.replace("if(e.target?.matches?.('input')){\n        // PERFORMANCE_STABILIZATION_V1: age under the pre-edit rates, but do not run the\n        // expensive optimizer just for tabbing/clicking between fields.\n        rollSnapshotForward(Date.now(),true);\n      }",
            "if(e.target?.matches?.('input') && e.target.id!=='targetStars'){\n        // PERFORMANCE_STABILIZATION_V1: age under the pre-edit rates, but do not run the\n        // expensive optimizer just for tabbing/clicking between account-state fields.\n        // Target Primostars is only a goal selector, so focusing it must not mutate the snapshot.\n        rollSnapshotForward(Date.now(),true);\n      }",1)

runtime.write_text(s)

# Keep the no-saved-state HTML fallback aligned with the new Bed EXP default.
index=Path('index.html')
h=index.read_text()
old='id="bedExp" type="number" value="0"'
if old not in h:
    raise SystemExit('bedExp HTML anchor not found')
h=h.replace(old,'id="bedExp" type="number" value="400000"',1)
index.write_text(h)

print('Applied TARGET_FRONTIER_TRIM_V1 + PROJECTED_SCORING_GATE_V1 + Bed EXP 400k default')
