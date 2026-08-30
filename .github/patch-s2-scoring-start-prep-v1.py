from pathlib import Path
import re

p=Path('index.html')
s=p.read_text(encoding='utf-8')
marker='S2_SCORING_START_PREP_V1'
if marker in s:
    print('already applied')
    raise SystemExit(0)

# 1) Use QY's actually useful S2 recommendation thresholds instead of an early 530 filler.
old='<div class="s2TargetPresets" id="s2TargetPresets" hidden aria-label="Season 2 common planning targets"><span>S2 planning targets</span><div><button type="button" data-s2-target="530">530</button><button type="button" data-s2-target="680">680</button><button type="button" data-s2-target="920">920</button></div><small>Quick-fill only — your target can still be any value.</small></div>'
new='<div class="s2TargetPresets" id="s2TargetPresets" hidden aria-label="Season 2 common planning targets"><span>S2 planning targets</span><div><button type="button" data-s2-target="680" title="QY: Basic">680 · Basic</button><button type="button" data-s2-target="800" title="QY: F2P / Light">800 · F2P/Light</button><button type="button" data-s2-target="920" title="QY: Light / Mid spender">920 · Light/Mid</button><button type="button" data-s2-target="1060" title="QY: Stop point">1060 · Stop</button></div><small>QY recommendation tiers · any total still works.</small></div>'
if old not in s:
    raise SystemExit('S2 target preset block not found')
s=s.replace(old,new,1)

s=s.replace("commonTargets:Object.freeze([530,680,920]),","commonTargets:Object.freeze([680,800,920,1060]),",1)

# 2) Add a documented scoring-start profile. Economy fields deliberately stay zero-safe;
#    the profile only assumes progression that a player can plausibly have when Season Power opens.
needle="  function validateS2PrimoModel(){\n"
insert="""  /* S2_SCORING_START_PREP_V1
     This calculator is a Season Power / Primostar planner, not a Lv.100→130 launch-day simulator.
     QY's current Global timeline puts S2 Season Power at Player Lv.130; Lv.120 is only the
     maximum S2 Material Realm / open-map bracket. New S2 calculator states therefore begin
     from a representative scoring-unlock profile. Account-specific rates/materials remain 0
     until the player enters them so the optimizer never fabricates spendable resources. */
  const S2_SCORING_START_DEFAULTS=Object.freeze({
    targetStars:800,
    // QY labels 128 as an S1 F2P/Light recommendation; it is only a starter/example carry value.
    historicalStars:128,
    charLevel:130,charExp:0,bedExp:0,reserveHours:34,
    skillLevel:130,relicLevel:14,fantomonLevel:130,
    gearWeapon:130,gearOffhand:130,gearHelmet:130,gearArmor:130,gearBoots:130,
    oreCurrent:0,oreRate:0,essenceCurrent:0,essenceRate:0,
    sandCurrent:0,sandBlueCurrent:0,sandRate:0,
    treatCurrent:0,treatPremiumCurrent:0,treatDeluxeCurrent:0,treatRate:0,
    hammerCurrent:0,knucklesCurrent:0,shovelCurrent:0,
    staminaMode:'auto',realmDailyOre:4,realmDailyEssence:4,realmDailySand:4,
    refinedOreCurrent:'',exactSkillLevels:'',exactRelicLevels:'',exactFantoLevels:''
  });
  const S2_SCORING_START_CHECKS=Object.freeze({
    holdExp:true,reserveS2Ore:false,reserveS2Essence:false,reserveS2Sand:false,reserveS2Treats:false
  });

"""
if needle not in s:
    raise SystemExit('validateS2PrimoModel anchor not found')
s=s.replace(needle,insert+needle,1)

# 3) Apply S2 starter defaults for new/reset S2 profiles.
needle="""  function savedTreatEquivalent(){
    return Math.max(0,n('treatCurrent')) + Math.max(0,n('treatPremiumCurrent'))*TREAT_PREMIUM_EQ + Math.max(0,n('treatDeluxeCurrent'))*TREAT_DELUXE_EQ;
  }
"""
insert="""  function savedTreatEquivalent(){
    return Math.max(0,n('treatCurrent')) + Math.max(0,n('treatPremiumCurrent'))*TREAT_PREMIUM_EQ + Math.max(0,n('treatDeluxeCurrent'))*TREAT_DELUXE_EQ;
  }
  function applyS2ScoringStartDefaults(){
    Object.entries(S2_SCORING_START_DEFAULTS).forEach(([id,value])=>{ if($(id)) $(id).value=String(value); });
    Object.entries(S2_SCORING_START_CHECKS).forEach(([id,value])=>{ if($(id)) $(id).checked=!!value; });
  }
"""
if needle not in s:
    raise SystemExit('savedTreatEquivalent anchor not found')
s=s.replace(needle,insert,1)

old="      if(!hadState && activeCalcConfig().key==='s2' && $('targetStars')) $('targetStars').value='680';"
new="      if(!hadState && activeCalcConfig().key==='s2') applyS2ScoringStartDefaults();"
if old not in s:
    raise SystemExit('no-state S2 target default anchor not found')
s=s.replace(old,new,1)

# 4) Season chrome: scoring floor is 130; old S1→S2 reserve controls disappear in S2.
old="""    if(cfg.key==='s2'){
      $('seasonRulesHint').innerHTML='<b>S2 score:</b> +45 fixed · 27 score / Primostar · floor Lv.130 / Relics above +13 · weights Character 100, Gear 18, Skill 7, Relic 33, Fantomon 8. <b>Lv.120</b> is the max S2 Material Realm/open-map resource bracket. Late-S2 upgrade gates stay conservative where an exact unlock rule is not verified.';
      const currentCaps=categoryInputCapsForCharacter(characterSnapshot(cfg).level,cfg);
      $('skillLevel').min='100'; setInputMax('skillLevel',currentCaps.skill); $('skillLevel').step='0.125';
      $('relicLevel').min='10'; setInputMax('relicLevel',currentCaps.relic); $('relicLevel').step='0.05';
      $('fantomonLevel').min='100'; setInputMax('fantomonLevel',currentCaps.fanto); $('fantomonLevel').step='0.25';
    } else {
"""
new="""    if(cfg.key==='s2'){
      $('seasonRulesHint').innerHTML='<b>S2 scoring mode starts at Lv.130:</b> +45 fixed · 27 score / Primostar · normal floor Lv.130 / Relics above +13 · weights Character 100, Gear 18, Skill 7, Relic 33, Fantomon 8. <b>Lv.120</b> is only the max S2 Material Realm/open-map bracket. Starter profile: Lv.130 · Gear 130 · Skills 130 · Fantomons 130 · Relics +14; carried stars/resources should be replaced with your actual snapshot.';
      const currentCaps=categoryInputCapsForCharacter(characterSnapshot(cfg).level,cfg);
      $('skillLevel').min=String(cfg.scoreFloor); setInputMax('skillLevel',currentCaps.skill); $('skillLevel').step='0.125';
      $('relicLevel').min=String(cfg.relicFloor); setInputMax('relicLevel',currentCaps.relic); $('relicLevel').step='0.05';
      $('fantomonLevel').min=String(cfg.scoreFloor); setInputMax('fantomonLevel',currentCaps.fanto); $('fantomonLevel').step='0.25';
      GEAR_IDS.forEach(id=>{if($(id)) $(id).min=String(cfg.scoreFloor);});
    } else {
"""
if old not in s:
    raise SystemExit('S2 season chrome block not found')
s=s.replace(old,new,1)

# Restore S1 mins if the season is S1.
old="""      $('skillLevel').min='100'; setInputMax('skillLevel',currentCaps.skill); $('skillLevel').step='0.125';
      $('relicLevel').min='10'; setInputMax('relicLevel',currentCaps.relic); $('relicLevel').step='0.05';
      $('fantomonLevel').min='100'; setInputMax('fantomonLevel',currentCaps.fanto); $('fantomonLevel').step='0.25';
    }
    const mismatch=snapshotSeason!==cfg.key;
"""
new="""      $('skillLevel').min='100'; setInputMax('skillLevel',currentCaps.skill); $('skillLevel').step='0.125';
      $('relicLevel').min='10'; setInputMax('relicLevel',currentCaps.relic); $('relicLevel').step='0.05';
      $('fantomonLevel').min='100'; setInputMax('fantomonLevel',currentCaps.fanto); $('fantomonLevel').step='0.25';
      GEAR_IDS.forEach(id=>{if($(id)) $(id).min='100';});
    }
    ['reserveS2Ore','reserveS2Essence','reserveS2Sand','reserveS2Treats'].forEach(id=>{
      const label=$(id)?.closest('label'); if(label) label.hidden=cfg.key==='s2';
    });
    const mismatch=snapshotSeason!==cfg.key;
"""
if old not in s:
    raise SystemExit('season chrome end anchor not found')
s=s.replace(old,new,1)

# Rollover wording: it is okay to ignore calculator until Lv130.
old="""      $('calcSeasonNoticeText').textContent=`Your saved calculator state is from ${CALC_SEASONS[snapshotSeason]?.name||'the prior season'}. Update Character level/EXP, Gear, Skills, Relics, Fantomons, resources/Cart rates and carried Primostars, then confirm. The site intentionally refuses to assume how the seasonal reset changed your account.`;
"""
new="""      $('calcSeasonNoticeText').textContent=cfg.key==='s2'
        ? `Your saved calculator state is from ${CALC_SEASONS[snapshotSeason]?.name||'the prior season'}. S2 Season Power does not unlock until Lv.130, so this scoring planner intentionally ignores the Lv.100→130 catch-up phase. At Lv.130, enter your actual carried Primostars/resources and current progression, then confirm the S2 snapshot.`
        : `Your saved calculator state is from ${CALC_SEASONS[snapshotSeason]?.name||'the prior season'}. Update Character level/EXP, Gear, Skills, Relics, Fantomons, resources/Cart rates and carried Primostars, then confirm. The site intentionally refuses to assume how the seasonal reset changed your account.`;
"""
if old not in s:
    raise SystemExit('rollover text anchor not found')
s=s.replace(old,new,1)

# 5) Pre-scoring gate. The scoring calculator is intentionally paused below 130.
needle="""  function clearCalcForRollover(cfg){
"""
insert="""  function clearS2PreScoring(cfg){
    const current=characterSnapshot(cfg),p=projectCharacter(cfg);
    $('seasonRemaining').textContent=formatRemaining(remainingHoursAt(Date.now(),cfg));
    $('projectedCharacter').textContent=`Lv.${p.level} · ${(p.pct*100).toFixed(1)}%`;
    $('resultProjectedCharacter').textContent=`Lv.${p.level} (${(p.pct*100).toFixed(1)}%)`;
    $('currentStars').textContent='—'; $('currentScoreNow').textContent='—'; $('summaryOptimizedScore').textContent='—'; $('desiredScore').textContent='—';
    $('targetMessage').hidden=false; $('targetMessage').classList.remove('danger'); $('targetMessage').classList.add('warning','caution');
    $('targetMessage').textContent=`Season Power scoring unlocks at Lv.${cfg.scoreFloor}. Current Lv.${current.level} is still in the S2 catch-up phase, so 100→${cfg.scoreFloor} upgrade costs are intentionally excluded from this Primostar planner.`;
    if($('targetStatus')){$('targetStatus').textContent='locked';$('targetStatus').classList.remove('notMet');}
    $('optimizerSummary').textContent=`Return at Lv.${cfg.scoreFloor} and enter your actual scoring-start snapshot. The default S2 profile is Lv.130 / Gear 130 / Skills 130 / Fantomons 130 / Relics +14.`;
    $('optimizedScore').textContent='—';
    $('materialRealmRecommendation').hidden=true;
    renderRealmToolProjection(cfg);
  }

"""
if needle not in s:
    raise SystemExit('clearCalcForRollover anchor not found')
s=s.replace(needle,insert+needle,1)

old="""    if(renderCalculatorSeasonChrome(cfg)){ clearCalcForRollover(cfg); return; }
    const p=projectCharacter(cfg);
"""
new="""    if(renderCalculatorSeasonChrome(cfg)){ clearCalcForRollover(cfg); return; }
    if(cfg.key==='s2' && characterSnapshot(cfg).level<cfg.scoreFloor){ clearS2PreScoring(cfg); return; }
    const p=projectCharacter(cfg);
"""
if old not in s:
    raise SystemExit('updateCalculator gate anchor not found')
s=s.replace(old,new,1)

# 6) Score/cost scope starts at the scoring floor. This prevents below-130 catch-up costs
#    from leaking into an S2 Primostar plan if stale/odd inputs are present.
def replace_progression_block(text, count_expected):
    old="""    const gear=GEAR_IDS.map(id=>Math.max(100,Math.floor(n(id,143))));
    const skillState=categoryStateFromUser('skillLevel','exactSkillLevels',8,100,currentCaps.skill,cfg.scoreFloor,cfg.weights.skill,cfg.key==='s2'?100:122);
    const relicState=categoryStateFromUser('relicLevel','exactRelicLevels',20,10,currentCaps.relic,cfg.relicFloor,cfg.weights.relic,cfg.key==='s2'?10:13);
    const fantoState=categoryStateFromUser('fantomonLevel','exactFantoLevels',4,100,currentCaps.fanto,cfg.scoreFloor,cfg.weights.fanto,cfg.key==='s2'?100:130);
"""
    new="""    const normalInputFloor=cfg.key==='s2'?cfg.scoreFloor:100;
    const relicInputFloor=cfg.key==='s2'?cfg.relicFloor:10;
    const gear=GEAR_IDS.map(id=>Math.max(normalInputFloor,Math.floor(n(id,cfg.key==='s2'?130:143))));
    const skillState=categoryStateFromUser('skillLevel','exactSkillLevels',8,normalInputFloor,currentCaps.skill,cfg.scoreFloor,cfg.weights.skill,cfg.key==='s2'?130:122);
    const relicState=categoryStateFromUser('relicLevel','exactRelicLevels',20,relicInputFloor,currentCaps.relic,cfg.relicFloor,cfg.weights.relic,cfg.key==='s2'?14:13);
    const fantoState=categoryStateFromUser('fantomonLevel','exactFantoLevels',4,normalInputFloor,currentCaps.fanto,cfg.scoreFloor,cfg.weights.fanto,cfg.key==='s2'?130:130);
"""
    n=text.count(old)
    if n!=count_expected:
        raise SystemExit(f'progression block count {n}, expected {count_expected}')
    return text.replace(old,new,count_expected)

# One copy in max-achievable snapshot, one in updateCalculator.
s=replace_progression_block(s,2)

old="""      ['exactSkillLevels',8,100,currentCaps.skill,'Skills'],
      ['exactRelicLevels',20,10,currentCaps.relic,'Relics'],
      ['exactFantoLevels',4,100,currentCaps.fanto,'Fantomons']
"""
new="""      ['exactSkillLevels',8,normalInputFloor,currentCaps.skill,'Skills'],
      ['exactRelicLevels',20,relicInputFloor,currentCaps.relic,'Relics'],
      ['exactFantoLevels',4,normalInputFloor,currentCaps.fanto,'Fantomons']
"""
if old not in s:
    raise SystemExit('exact progression input block not found')
s=s.replace(old,new,1)

# Max-achievable should also refuse to solve before S2 scoring exists.
old="""    const currentCharacter=p.current||characterSnapshot(cfg);
    const projectedResourceTotals=projectedResources(p.hours,cfg);
"""
new="""    const currentCharacter=p.current||characterSnapshot(cfg);
    if(cfg.key==='s2' && currentCharacter.level<cfg.scoreFloor) return null;
    const projectedResourceTotals=projectedResources(p.hours,cfg);
"""
if s.count(old)<1:
    raise SystemExit('max achievable currentCharacter anchor not found')
s=s.replace(old,new,1)

# 7) S2 reset now means "scoring-start profile", not fresh-season Lv100.
pattern=re.compile(r"    } else \{\n      const s2Defaults=\{targetStars:680,historicalStars:0,charLevel:100,charExp:0,bedExp:0,reserveHours:34,skillLevel:100,relicLevel:10,fantomonLevel:100,gearWeapon:100,gearOffhand:100,gearHelmet:100,gearArmor:100,gearBoots:100,oreCurrent:0,oreRate:0,essenceCurrent:0,essenceRate:0,sandCurrent:0,sandBlueCurrent:0,sandRate:0,treatCurrent:0,treatPremiumCurrent:0,treatDeluxeCurrent:0,treatRate:0,hammerCurrent:0,knucklesCurrent:0,shovelCurrent:0,staminaMode:'auto',realmDailyOre:0,realmDailyEssence:0,realmDailySand:0,refinedOreCurrent:'',exactSkillLevels:'',exactRelicLevels:'',exactFantoLevels:''\};\n      INPUT_IDS\.forEach\(id=>\{if\(\$\(id\)\) \$\(id\)\.value=String\(s2Defaults\[id\]\?\?''\);\}\);\n      \$\('holdExp'\)\.checked=true; \$\('reserveS2Ore'\)\.checked=true; \$\('reserveS2Essence'\)\.checked=true; \$\('reserveS2Sand'\)\.checked=true; \$\('reserveS2Treats'\)\.checked=true;\n    }",re.M)
replacement="""    } else {
      applyS2ScoringStartDefaults();
    }"""
s,n=pattern.subn(replacement,s,count=1)
if n!=1:
    raise SystemExit(f'S2 reset block replacement count {n}')

# Existing low S1 target becomes the useful S2 default at explicit rollover confirmation.
s=s.replace("if(!Number.isFinite(target) || target<=230) $('targetStars').value='680';","if(!Number.isFinite(target) || target<=480) $('targetStars').value=String(S2_SCORING_START_DEFAULTS.targetStars);",1)

# 8) Fix stale wording in the optimizer explanation and method notes.
s=s.replace(
"<p><b>1 · Protect enabled Season 2 reserves.</b> Skill Essence and Chrono Sand reserves assign carried/projected Realm tools first, then hold raw material only for any reserve amount those tools cannot cover. Fantomon Treats have no Realm-tool conversion, so an enabled Treat reserve stays raw.</p>",
"<p><b>1 · Protect enabled rollover reserves during Season 1.</b> Raw Essence/Sand cover those reserves first; Knuckles/Shovels are reserved only for any uncovered remainder. Once S2 scoring is active, the old S1→S2 reserve toggles are hidden and the planner uses your live S2 inventory directly.</p>",1)

s=s.replace(
"<p><b>S2 Primostar calculator readiness:</b> Season 2 is preloaded as a separate profile and does not replace Season 1. The scoring model uses the cross-region S2 consensus: normal progression scores only above Lv.130, Relics score above +13, the season contributes 45 fixed Primostars, and every 27 progression score adds one more Primostar after flooring. Per-level weights are Character 100, Gear 18, Skill 7, Fantomon 8 and Relic 33. The rollover guard still requires a fresh S2 account snapshot before calculations resume, so stale S1 levels/resources cannot silently contaminate the S2 plan. Exact Global cost/unlock data that is not independently confirmed remains conservative rather than fabricated. As a regression check, the formula also reproduces the published S2 920-Primostar end-state (131 carried from S1; about Lv.190.8, Gear 195, Skills 180, Fantomons 175/175/173/173 and Relics +19).</p>",
"<p><b>S2 Primostar calculator readiness:</b> Season 2 is preloaded as a separate scoring-only profile and does not replace Season 1. QY's current timeline confirms Season Power at Player Lv.130; Lv.120 is only the maximum S2 Material Realm bracket. The calculator therefore starts score planning at Lv.130 and intentionally excludes the Lv.100→130 catch-up costs. Normal progression scores only above Lv.130, Relics score above +13, the season contributes 45 fixed Primostars, and every 27 progression score adds one more Primostar after flooring. Per-level weights are Character 100, Gear 18, Skill 7, Fantomon 8 and Relic 33. S2 cost curves are used only for score-relevant upgrades from that floor forward: Gear/Ore and Skill Essence use the current late-S2 tables, Relic Sand uses the known +13-and-up steps, and Fantomon Treats use the S2 level curve. Exact data that is not independently confirmed stays conservative rather than fabricated. As a regression check, the formula still reproduces the published S2 920-Primostar end-state (131 carried from S1; about Lv.190.8, Gear 195, Skills 180, Fantomons 175/175/173/173 and Relics +19).</p>",1)

# Small CSS adjustment for four descriptive preset buttons.
css="""
<style id="s2-scoring-start-prep-v1-style">
/* S2_SCORING_START_PREP_V1 */
.s2TargetPresets>div{gap:6px!important}
.s2TargetPresets button{white-space:nowrap!important}
@media(max-width:760px){.s2TargetPresets>div{display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))}.s2TargetPresets button{width:100%;white-space:normal!important}}
</style>
"""
anchor='</head>'
if anchor not in s:
    raise SystemExit('head close not found')
s=s.replace(anchor,css+'\n'+anchor,1)

p.write_text(s,encoding='utf-8')
print('prepared S2 scoring-start calculator profile')
