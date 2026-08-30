from pathlib import Path
import re

p=Path('index.html')
s=p.read_text(encoding='utf-8')
orig=s

# REMOVE_S1_RESOURCE_RESERVES_V1
# The old rollover material reserves are obsolete. S1 target planning now uses the full
# live/projected resource pool and the same acquisition-efficiency + Minimize tools policy.
# Bed EXP hold remains independent and intentionally keeps its 34-hour window.

# Remove hidden reserve controls and dead reserve hint placeholders/CSS.
for line in [
'          <input id="reserveS2Essence" checked type="checkbox" hidden>\n',
'          <input id="reserveS2Sand" checked type="checkbox" hidden>\n',
'          <input id="reserveS2Treats" checked type="checkbox" hidden>\n',
'        <div class="seasonRulesHint" id="s2SkillReserveHint">S2 Skill Essence reserve: calculating…</div>\n',
'        <div class="seasonRulesHint" id="s2RelicReserveHint">S2 Relic Sand reserve: calculating…</div>\n',
'        <div class="seasonRulesHint" id="s2TreatReserveHint">S2 Fantomon Treat reserve: calculating…</div>\n',
'#s2SkillReserveHint,#s2RelicReserveHint,#s2TreatReserveHint{display:none!important}\n',
]:
    s=s.replace(line,'')

# Remove old saved-state migration for reserve switches.
s=re.sub(r"\n      // v59 keeps the separate S2 reserve toggles, adds Premium/Deluxe Treat inventory, and preserves older Basic Treat counts\.\n      if\(hadState && \(Number\(state\.snapshotSchema\)\|\|0\)<6\)\{.*?\n      if\(hadState && state\.reserveS2Treats===undefined\) state\.reserveS2Treats=true;",'',s,flags=re.S)

# Remove all S1->S2 resource reserve construction. Bed EXP hold is outside this block.
s=re.sub(r"\n  /\* POST_PLAN_RAW_RESERVE_V2.*?\n  function relicStepSand\(level,cfg=activeCalcConfig\(\)\)\{",'\n  function relicStepSand(level,cfg=activeCalcConfig()){',s,flags=re.S)

# The resource snapshot is now used directly; nothing is withheld for rollover materials.
s=s.replace('const baseResources=applySeasonTransitionReserves(projectedResourceTotals,cfg);','const baseResources=projectedResourceTotals;')

# Auto Stamina and target search use ordinary Realm topups for all three farmable resources.
s=s.replace("      return key==='ore'\n        ? realmTopupFor(key,costs[key],budget,sim,cfg,p)\n        : reserveAwareRealmTopupFor(key,costs[key],budget,sim,cfg,p);","      return realmTopupFor(key,costs[key],budget,sim,cfg,p);")
s=s.replace("essence:reserveAwareRealmTopupFor('essence',0,resources.essence,resources,cfg,p),sand:reserveAwareRealmTopupFor('sand',0,resources.sand,resources,cfg,p)","essence:realmTopupFor('essence',0,resources.essence,resources,cfg,p),sand:realmTopupFor('sand',0,resources.sand,resources,cfg,p)")
s=s.replace("const essFor=so=>{const k=so.cost;if(!essCache.has(k))essCache.set(k,reserveAwareRealmTopupFor('essence',k,resources.essence,resources,cfg,p));return essCache.get(k);};","const essFor=so=>{const k=so.cost;if(!essCache.has(k))essCache.set(k,realmTopupFor('essence',k,resources.essence,resources,cfg,p));return essCache.get(k);};")
s=s.replace("const sandFor=ro=>{const k=ro.cost;if(!sandCache.has(k))sandCache.set(k,reserveAwareRealmTopupFor('sand',k,resources.sand,resources,cfg,p));return sandCache.get(k);};","const sandFor=ro=>{const k=ro.cost;if(!sandCache.has(k))sandCache.set(k,realmTopupFor('sand',k,resources.sand,resources,cfg,p));return sandCache.get(k);};")
s=s.replace("const treatShortfall=Math.max(0,fo.cost+reserveTargetFor('treat',resources,cfg)-resources.treat);","const treatShortfall=Math.max(0,fo.cost-resources.treat);")

# Remove reserve topup helpers entirely; plain realmTopupFor is the only path now.
s=re.sub(r"\n  function reserveTargetFor\(key,resources,cfg=activeCalcConfig\(\)\)\{.*?\n  function formatRealmSchedule\(topup,label\)\{",'\n  function formatRealmSchedule(topup,label){',s,flags=re.S)

# Raw acquisition supply is simply the full available pool.
s=re.sub(r"  function rawOnlyAcquisitionSupply\(key,resources,cfg=activeCalcConfig\(\)\)\{.*?\n  \}","  function rawOnlyAcquisitionSupply(key,resources,cfg=activeCalcConfig()){\n    return Math.max(0,Number(resources?.[key])||0);\n  }",s,count=1,flags=re.S)

# Remove reserve-aware balance renderer and use normal remaining balances.
s=re.sub(r"\n  // RESERVE_REQUIREMENT_DISPLAY_V1:.*?\n  function setEssenceBalance\(id,cost,resources\)\{ setReservedRawRemaining\(id,cost,resources,'essence'\); \}\n  function setSandBalance\(id,cost,resources\)\{ setReservedRawRemaining\(id,cost,resources,'sand'\); \}\n  function setTreatBalance\(id,cost,resources\)\{ setReservedRawRemaining\(id,cost,resources,'treat','basic-eq\\.'\); \}","\n  function setEssenceBalance(id,cost,resources){ setRawRemaining(id,cost,resources.essence); }\n  function setSandBalance(id,cost,resources){ setRawRemaining(id,cost,resources.sand); }\n  function setTreatBalance(id,cost,resources){ setRawRemaining(id,cost,resources.treat,'basic-eq.'); }",s,flags=re.S)

# Simplify projected-material rendering so no reserve metadata is referenced.
s=s.replace("const displayedEssence=Number(resources.essenceTotal??resources.essence)||0;","const displayedEssence=Number(resources.essence)||0;")
s=s.replace("    const sr=resources.s2SkillReserve||season2SkillEssenceReserve(cfg);\n    const reserveSuffix='';\n    $('essenceProjected').textContent=`Projected: ${fmtCompact(displayedEssence)}${essStam}${reserveSuffix}`;","    $('essenceProjected').textContent=`Projected: ${fmtCompact(displayedEssence)}${essStam}`;")
s=re.sub(r"\n    const reserveHint=\$\('s2SkillReserveHint'\);.*?\n    const displayedSand=Number\(resources\.sandTotal\?\?resources\.sand\)\|\|0;",'\n    const displayedSand=Number(resources.sand)||0;',s,flags=re.S)
s=s.replace("    const sandReserveSuffix='';\n    $('sandProjected').textContent=`Projected: ${fmtCompact(displayedSand)}${sandStam}${sandReserveSuffix}`;","    $('sandProjected').textContent=`Projected: ${fmtCompact(displayedSand)}${sandStam}`;")
s=re.sub(r"\n    const tr=resources\.s2FantomonTreatReserve\|\|season2FantomonTreatReserve\(cfg\);.*?\n    const displayedTreats=Number\(resources\.treatTotal\?\?resources\.treat\)\|\|0;",'\n    const displayedTreats=Number(resources.treat)||0;',s,flags=re.S)
s=s.replace("    const treatReserveSuffix='';\n    $('treatProjected').textContent=`Projected: ${fmtCompact(displayedTreats)} basic-eq.${treatReserveSuffix}`;","    $('treatProjected').textContent=`Projected: ${fmtCompact(displayedTreats)} basic-eq.`;")

# Remove season-chrome logic for controls that no longer exist.
s=re.sub(r"\n    \['reserveS2Essence','reserveS2Sand','reserveS2Treats'\]\.forEach\(id=>\{.*?\n    \}\);",'',s,flags=re.S)

# Update the optimizer explanation: same method in S1/S2, but each season keeps its own scoring constants.
s=s.replace('<p><b>1 · Protect enabled rollover reserves during Season 1.</b> Raw Essence/Sand cover those reserves first; Knuckles/Shovels are reserved only for any uncovered remainder. Once S2 scoring is active, the old S1→S2 reserve toggles are hidden and the planner uses your live S2 inventory directly.</p>','<p><b>1 · Use the active season’s scoring rules.</b> Season 1 keeps its own Primostar formula and S1 score weights; Season 2 keeps its separate S2 formula. The optimizer method is shared, but scoring values are never mixed between seasons.</p>')
s=s.replace('<p><b>2 · Find the most acquisition-efficient score route.</b>','<p><b>2 · Find the most acquisition-efficient score route.</b>')

# Add an explicit guard comment near the S1 config so future cleanup cannot import S2 weights.
needle="s1:{key:'s1',name:'Season 1',nextName:'Season 2',end:S1_END,deadline:'device-local',scoreFloor:100,relicFloor:10,starBase:10,scorePerStar:100,weights:{character:100,gear:38,skill:13,relic:57,fanto:14}"
if needle not in s:
    raise SystemExit('S1 scoring constants not found')
s=s.replace('  const CALC_SEASONS = {','  const CALC_SEASONS = {\n    // S1_SCORING_METHOD_REFRESH_V1: use the shared acquisition optimizer, but preserve S1 scoring constants exactly.')

# Verification: no rollover resource reserve machinery remains; S1 scoring stays S1.
for banned in ['reserveS2Essence','reserveS2Sand','reserveS2Treats','season2SkillEssenceReserve','season2RelicSandReserve','season2FantomonTreatReserve','applySeasonTransitionReserves','reserveTargetFor','reserveAwareRealmTopupFor','rawFirstReserveSplit','S2 Skill reserve:','S2 Relic Sand reserve:','S2 Fantomon Treat reserve:']:
    if banned in s:
        raise SystemExit(f'obsolete reserve token remains: {banned}')
for required in [
"scoreFloor:100,relicFloor:10,starBase:10,scorePerStar:100,weights:{character:100,gear:38,skill:13,relic:57,fanto:14}",
'REALM_SAVED_TOOL_EFFICIENCY_HURDLE=0.10',
'REALM_PAID_REFRESH_EFFICIENCY_HURDLE=0.20',
"reserveHours'",
'34',
'S1_SCORING_METHOD_REFRESH_V1'
]:
    if required not in s:
        raise SystemExit(f'required guard missing: {required}')

if s==orig:
    raise SystemExit('patch made no changes')
p.write_text(s,encoding='utf-8')
print('REMOVE_S1_RESOURCE_RESERVES_V1 applied')
