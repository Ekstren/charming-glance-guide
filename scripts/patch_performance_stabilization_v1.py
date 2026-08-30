from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')
marker = 'PERFORMANCE_STABILIZATION_V1'

if marker in s:
    print('Performance stabilization already applied')
    raise SystemExit(0)


def replace_once(old: str, new: str, label: str):
    global s
    count = s.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly 1 match, found {count}')
    s = s.replace(old, new, 1)

# 1) Remove the now-dead full Season 1 build library. The live build path is hard-switched
# to S2, and this legacy function has no callers. Keeping it only makes the browser parse and
# retain a very large template-literal blob on every page load.
legacy_pattern = r"\n\s*function legacyBuildHtmlS1\(cls\)\{[\s\S]*?\n\s*// SEASONAL_BUILD_OVERRIDE_V1"
s, legacy_count = re.subn(
    legacy_pattern,
    "\n\n  // PERFORMANCE_STABILIZATION_V1\n  // Dead S1 build-template blob removed after the S2 cutover.\n\n  // SEASONAL_BUILD_OVERRIDE_V1",
    s,
    count=1,
)
if legacy_count != 1:
    raise SystemExit(f'legacy S1 build removal: expected 1 match, found {legacy_count}')

# 2) Do not launch a full optimizer solve merely because an input receives focus. We still age
# the snapshot before editing so the previous production rates are accounted for correctly; the
# already-existing change/Enter handlers perform the actual solve after the edit is committed.
replace_once(
"""    document.getElementById('calculatorSection')?.addEventListener('focusin',e=>{\n      if(e.target?.matches?.('input')){\n        if(rollSnapshotForward(Date.now(),true)) scheduleCalculatorUpdate(0);\n      }\n    });""",
"""    document.getElementById('calculatorSection')?.addEventListener('focusin',e=>{\n      if(e.target?.matches?.('input')){\n        // PERFORMANCE_STABILIZATION_V1: age under the pre-edit rates, but do not run the\n        // expensive optimizer just for tabbing/clicking between fields.\n        rollSnapshotForward(Date.now(),true);\n      }\n    });""",
'focus-only optimizer solve removal')

# 3) The S2 build override previously rebuilt the entire (large) Builds DOM every minute because
# liveBuildSeason() is always "s2" after cutover. Only rerender when the normalized class or season
# actually changes.
replace_once(
"""    renderBuilds();\n    setInterval(()=>{\n      if(buildsInitialized){\n        const before=currentClass;\n        normalizeLiveBuildClass();\n        if(before!==currentClass || liveBuildSeason()==='s2') renderBuilds();\n      }\n    },60_000);""",
"""    renderBuilds();\n    let lastBuildSeasonTick=liveBuildSeason();\n    setInterval(()=>{\n      if(!buildsInitialized) return;\n      const beforeClass=currentClass;\n      const beforeSeason=lastBuildSeasonTick;\n      normalizeLiveBuildClass();\n      const afterSeason=liveBuildSeason();\n      if(beforeClass!==currentClass || beforeSeason!==afterSeason) renderBuilds();\n      lastBuildSeasonTick=afterSeason;\n    },60_000);""",
'unconditional S2 build rerender removal')

# 4) Timeline used to reconstruct hundreds of DOM nodes every minute even when nothing changed.
# Keep the local reset clock fresh, but only rerender the timeline when the reset boundary or active
# event set actually changes.
replace_once(
"""    renderTimeline();\n    setInterval(renderTimeline,60_000);""",
"""    renderTimeline();\n    let timelineMinuteSignature='';\n    const currentTimelineSignature=()=>{\n      const boundary=currentResetIso();\n      const active=timelineData.filter(e=>eventIsActive(e,boundary)).map(e=>`${e[0]}:${e[3]}`).join('|');\n      return `${boundary}::${active}`;\n    };\n    timelineMinuteSignature=currentTimelineSignature();\n    setInterval(()=>{\n      renderLocalTimeLabels();\n      const nextSignature=currentTimelineSignature();\n      if(nextSignature!==timelineMinuteSignature){\n        timelineMinuteSignature=nextSignature;\n        renderTimeline();\n      }\n    },60_000);""",
'timeline minute DOM rebuild removal')

# 5) Reward panels are pure functions of a tiny key. Avoid replacing the same DOM trees every time
# the calculator recomputes without crossing a Primostar boundary.
replace_once(
"""  function renderAstralPact(totalStars){\n    const stars=Math.max(0,Math.floor(Number(totalStars)||0));""",
"""  let lastAstralRenderKey='';\n  let lastPrimostarRewardRenderKey='';\n  function renderAstralPact(totalStars){\n    const stars=Math.max(0,Math.floor(Number(totalStars)||0));\n    const renderKey=String(stars);\n    if(renderKey===lastAstralRenderKey) return;\n    lastAstralRenderKey=renderKey;""",
'Astral render memoization')

replace_once(
"""  function renderPrimostarRewardReference(currentTotalStars,projectedTotalStars=currentTotalStars){\n    const currentStars=Math.max(0,Math.floor(Number(currentTotalStars)||0));\n    const projectedStars=Math.max(currentStars,Math.floor(Number(projectedTotalStars)||0));\n    const host=$('primostarRewardSeasons');""",
"""  function renderPrimostarRewardReference(currentTotalStars,projectedTotalStars=currentTotalStars){\n    const currentStars=Math.max(0,Math.floor(Number(currentTotalStars)||0));\n    const projectedStars=Math.max(currentStars,Math.floor(Number(projectedTotalStars)||0));\n    const rewardRenderKey=`${activeCalcConfig().key}|${currentStars}|${projectedStars}`;\n    if(rewardRenderKey===lastPrimostarRewardRenderKey) return;\n    lastPrimostarRewardRenderKey=rewardRenderKey;\n    const host=$('primostarRewardSeasons');""",
'Primostar reward render memoization')

# 6) The acquisition cache had almost no hit rate because its key contains all four cumulative
# resource costs. In large S2 searches it could retain hundreds of thousands/millions of unique
# strings + objects until the solve completed, creating severe GC/memory pressure. Keep the small
# per-resource Realm caches, but calculate acquisition effort directly for the candidate that is
# actually being evaluated.
replace_once(
"""    const oreCache=new Map(),essCache=new Map(),sandCache=new Map(),acquisitionCache=new Map();\n    const oreFor=go=>{const k=go.oreCost;if(!oreCache.has(k))oreCache.set(k,realmTopupFor('ore',k,resources.ore,resources,cfg,p));return oreCache.get(k);};\n    const essFor=so=>{const k=so.cost;if(!essCache.has(k))essCache.set(k,realmTopupFor('essence',k,resources.essence,resources,cfg,p));return essCache.get(k);};\n    const sandFor=ro=>{const k=ro.cost;if(!sandCache.has(k))sandCache.set(k,realmTopupFor('sand',k,resources.sand,resources,cfg,p));return sandCache.get(k);};\n    const acquisitionFor=(go,so,ro,fo)=>{\n      const k=`${go.oreCost}|${so.cost}|${ro.cost}|${fo.cost}`;\n      if(!acquisitionCache.has(k)) acquisitionCache.set(k,acquisitionEffortFor({ore:go.oreCost,essence:so.cost,sand:ro.cost,treat:fo.cost},resources,cfg));\n      return acquisitionCache.get(k);\n    };""",
"""    const oreCache=new Map(),essCache=new Map(),sandCache=new Map();\n    const oreFor=go=>{const k=go.oreCost;if(!oreCache.has(k))oreCache.set(k,realmTopupFor('ore',k,resources.ore,resources,cfg,p));return oreCache.get(k);};\n    const essFor=so=>{const k=so.cost;if(!essCache.has(k))essCache.set(k,realmTopupFor('essence',k,resources.essence,resources,cfg,p));return essCache.get(k);};\n    const sandFor=ro=>{const k=ro.cost;if(!sandCache.has(k))sandCache.set(k,realmTopupFor('sand',k,resources.sand,resources,cfg,p));return sandCache.get(k);};\n    const acquisitionFor=(go,so,ro,fo)=>acquisitionEffortFor(\n      {ore:go.oreCost,essence:so.cost,sand:ro.cost,treat:fo.cost},resources,cfg\n    );""",
'unbounded acquisition cache removal')

# 7) Exact search compression: for a fixed Relic + Fantomon state, consecutive Skill options often
# choose the exact same minimum Gear option. The later Skill option is strictly dominated: same Gear,
# more Essence, more overscore. Evaluate only the first Skill option for each distinct Gear target.
replace_once(
"""      for(const fo of cats.fantoOptions){\n        const treatShortfall=Math.max(0,fo.cost-resources.treat);\n        for(const so of cats.skillOptions){\n          const fixedScore=charScore+ro.score+fo.score+so.score;\n          const go=gearLocked?(gearOptions[0].score>=Math.max(0,desired-fixedScore)?gearOptions[0]:null):firstGearOptionAtLeast(gearOptions,Math.max(0,desired-fixedScore));\n          if(!go)continue;\n          const score=fixedScore+go.score;if(score<desired)continue;""",
"""      for(const fo of cats.fantoOptions){\n        const treatShortfall=Math.max(0,fo.cost-resources.treat);\n        const fixedBeforeSkill=charScore+ro.score+fo.score;\n        let lastGearAdds=null;\n        for(const so of cats.skillOptions){\n          const fixedScore=fixedBeforeSkill+so.score;\n          const go=gearLocked?(gearOptions[0].score>=Math.max(0,desired-fixedScore)?gearOptions[0]:null):firstGearOptionAtLeast(gearOptions,Math.max(0,desired-fixedScore));\n          if(!go)continue;\n          // PERFORMANCE_STABILIZATION_V1: if Gear did not step down, this later Skill\n          // option spends more Essence for the same required Gear and cannot win.\n          if(lastGearAdds===go.adds) continue;\n          lastGearAdds=go.adds;\n          const score=fixedScore+go.score;if(score<desired)continue;""",
'exact Skill/Gear search compression')

# 8) Avoid building/evaluating a separate diagnostic candidate for every feasible route. If a plan
# is fundable it is already the diagnostic returned to callers. For infeasible routes, reject those
# that lose on the diagnostic's leading structural keys before paying for acquisition-effort math.
old_block = """          const diagOreShare=resources.ore>0?go.oreCost/resources.ore:(go.oreCost>0?go.oreCost/100000:0),diagEssenceShare=resources.essence>0?so.cost/resources.essence:(so.cost>0?so.cost/100000:0),diagSandShare=resources.sand>0?ro.cost/resources.sand:(ro.cost>0?ro.cost/100000:0),diagTreatShare=resources.treat>0?fo.cost/resources.treat:(fo.cost>0?fo.cost/10000:0);\n          const diagAcquisition=acquisitionFor(go,so,ro,fo);\n          const unknownPriceRefreshes=realms.reduce((sum,x)=>sum+Math.max(0,Number(x?.unknownPriceRefreshes)||0),0);\n          const diagnostic={gear:go.target,skill:so.avg,relic:ro.avg,fanto:fo.avg,skillLevels:so.levels,relicLevels:ro.levels,fantoLevels:fo.levels,oreCost:go.oreCost,essenceCost:so.cost,sandCost:ro.cost,treatCost:fo.cost,refinedCost:go.refinedCost,score,gearAdds:go.adds,skillAdds:so.adds,relicAdds:ro.adds,fantoAdds:fo.adds,overshoot:score-desired,dawniumCost,realmAttempts:realmPacks,realmPacks,oreShare:diagOreShare,essenceShare:diagEssenceShare,sandShare:diagSandShare,treatShare:diagTreatShare,acquisitionHours:diagAcquisition.hours,unknownPriceRefreshes,bankedHammersUsed:(oreRealm.bankedUsed||0),bankedKnucklesUsed:(essenceRealm.bankedUsed||0),bankedShovelsUsed:(sandRealm.bankedUsed||0),bankedToolsUsed:(oreRealm.bankedUsed||0)+(essenceRealm.bankedUsed||0)+(sandRealm.bankedUsed||0),realmOverflow,remainingAfterMax,treatShortfall,refinedShortfall,hardShortfall,seasonKey:cfg.key,realmFeasible:allFeasible,realm:{days:realmDays,ore:oreRealm,essence:essenceRealm,sand:sandRealm}};\n          if(betterDiagnosticCandidate(diagnostic,bestDiagnostic)) bestDiagnostic=diagnostic;\n\n          if(!allFeasible) continue;\n          const candidate=makePlanCandidate(go,so,ro,fo,score,desired,resources,[oreRealm,essenceRealm,sandRealm],diagAcquisition);\n          // makePlanCandidate already receives the once-computed resources.realmDays. Never rerun timezone/reset math per candidate.\n          candidate.realm.days=realmDays;\n          candidate.realmFeasible=true;\n          if(betterFeasibleCandidate(candidate,best)) best=candidate;"""
new_block = """          const unknownPriceRefreshes=realms.reduce((sum,x)=>sum+Math.max(0,Number(x?.unknownPriceRefreshes)||0),0);\n\n          if(allFeasible){\n            // A route that costs at least as much as the current winner in every tracked\n            // resource (and Refined Ore) is strictly dominated and cannot win later tie-breaks.\n            if(best && go.oreCost>=best.oreCost && so.cost>=best.essenceCost && ro.cost>=best.sandCost && fo.cost>=best.treatCost && go.refinedCost>=best.refinedCost) continue;\n            const acquisition=acquisitionFor(go,so,ro,fo);\n            const candidate=makePlanCandidate(go,so,ro,fo,score,desired,resources,[oreRealm,essenceRealm,sandRealm],acquisition);\n            candidate.realm.days=realmDays;\n            candidate.realmFeasible=true;\n            if(betterFeasibleCandidate(candidate,best)) best=candidate;\n            continue;\n          }\n\n          // betterDiagnosticCandidate always compares these three fields first. If this route\n          // already loses there, the expensive acquisition metric cannot rescue it.\n          if(bestDiagnostic){\n            if(hardShortfall>bestDiagnostic.hardShortfall+0.5) continue;\n            if(Math.abs(hardShortfall-bestDiagnostic.hardShortfall)<=0.5){\n              if(realmOverflow>bestDiagnostic.realmOverflow) continue;\n              if(realmOverflow===bestDiagnostic.realmOverflow && remainingAfterMax>bestDiagnostic.remainingAfterMax+0.5) continue;\n            }\n          }\n          const diagOreShare=resources.ore>0?go.oreCost/resources.ore:(go.oreCost>0?go.oreCost/100000:0),diagEssenceShare=resources.essence>0?so.cost/resources.essence:(so.cost>0?so.cost/100000:0),diagSandShare=resources.sand>0?ro.cost/resources.sand:(ro.cost>0?ro.cost/100000:0),diagTreatShare=resources.treat>0?fo.cost/resources.treat:(fo.cost>0?fo.cost/10000:0);\n          const diagAcquisition=acquisitionFor(go,so,ro,fo);\n          const diagnostic={gear:go.target,skill:so.avg,relic:ro.avg,fanto:fo.avg,skillLevels:so.levels,relicLevels:ro.levels,fantoLevels:fo.levels,oreCost:go.oreCost,essenceCost:so.cost,sandCost:ro.cost,treatCost:fo.cost,refinedCost:go.refinedCost,score,gearAdds:go.adds,skillAdds:so.adds,relicAdds:ro.adds,fantoAdds:fo.adds,overshoot:score-desired,dawniumCost,realmAttempts:realmPacks,realmPacks,oreShare:diagOreShare,essenceShare:diagEssenceShare,sandShare:diagSandShare,treatShare:diagTreatShare,acquisitionHours:diagAcquisition.hours,unknownPriceRefreshes,bankedHammersUsed:(oreRealm.bankedUsed||0),bankedKnucklesUsed:(essenceRealm.bankedUsed||0),bankedShovelsUsed:(sandRealm.bankedUsed||0),bankedToolsUsed:(oreRealm.bankedUsed||0)+(essenceRealm.bankedUsed||0)+(sandRealm.bankedUsed||0),realmOverflow,remainingAfterMax,treatShortfall,refinedShortfall,hardShortfall,seasonKey:cfg.key,realmFeasible:false,realm:{days:realmDays,ore:oreRealm,essence:essenceRealm,sand:sandRealm}};\n          if(betterDiagnosticCandidate(diagnostic,bestDiagnostic)) bestDiagnostic=diagnostic;"""
replace_once(old_block, new_block, 'feasible/diagnostic hot-path split')

replace_once(
"""    return {plan:best,diagnostic:bestDiagnostic};\n  }\n\n  function optimizer(""",
"""    return {plan:best,diagnostic:best||bestDiagnostic};\n  }\n\n  function optimizer(""",
'fundable plan as diagnostic result')

# 9) Add a lightweight visible timing hook for troubleshooting without console spam. It records only
# the last solve duration in a data attribute and console-warns if a solve is still unexpectedly slow.
replace_once(
"""  function updateCalculator(){\n    $('targetMessage')?.classList.remove('danger','caution');""",
"""  function updateCalculator(){\n    const perfStarted=performance.now();\n    $('targetMessage')?.classList.remove('danger','caution');""",
'calculator performance timer start')

# updateCalculator has several early returns, so use saveState() at the normal completed path as the
# instrumentation point rather than trying to rewrite every branch.
replace_once(
"""    $('milestoneNote').hidden=true;$('milestoneNote').textContent='';\n    saveState();\n  }\n\n  function copyPlan(){""",
"""    $('milestoneNote').hidden=true;$('milestoneNote').textContent='';\n    saveState();\n    const perfMs=performance.now()-perfStarted;\n    const calcSection=$('calculatorSection');\n    if(calcSection) calcSection.dataset.lastSolveMs=perfMs.toFixed(1);\n    if(perfMs>750) console.warn(`Primostar solve took ${perfMs.toFixed(0)} ms`,{season:cfg.key,target:targetStars});\n  }\n\n  function copyPlan(){""",
'calculator performance timer finish')

# Static safety checks.
for forbidden in (
    'function legacyBuildHtmlS1',
    'acquisitionCache=new Map()',
    "if(before!==currentClass || liveBuildSeason()==='s2') renderBuilds();",
    "if(rollSnapshotForward(Date.now(),true)) scheduleCalculatorUpdate(0);",
):
    if forbidden in s:
        raise SystemExit(f'Performance cleanup failed; stale hot-path token remains: {forbidden}')

required = [
    marker,
    'lastGearAdds===go.adds',
    'timelineMinuteSignature',
    'lastBuildSeasonTick',
    'lastPrimostarRewardRenderKey',
    'calcSection.dataset.lastSolveMs',
]
for token in required:
    if token not in s:
        raise SystemExit(f'Performance cleanup missing required marker/token: {token}')

p.write_text(s, encoding='utf-8')
print(f'Applied performance stabilization; index size is now {len(s):,} chars')
