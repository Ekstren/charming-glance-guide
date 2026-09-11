// v62 audit: preserve rollover resources, exact uneven slot levels, seasonal Fantomon +10 ceilings, device-local reset display, and Material Realm tools on equal-cost routes.
  // Keeps the v24 single-pass cached Primostar search and lazy-loading performance fixes.
(() => {
  'use strict';

  const STORAGE_KEY = 'charmingGlanceCloneV1';
  const PANEL_OPEN_IDS = ['characterDetails','materialsDetails'];
  const S1_END = new Date('2026-08-30T06:00:00-07:00');
  const S2_END = new Date('2026-11-05T06:00:00-08:00');
  const SERVER_START = new Date('2026-07-15T06:00:00-07:00');
/* S2_MINED_REALM_YIELDS_V1
     S2 max-bracket (Champion III / client Saint III) Material Realm averages are precomputed
     from factual live-client tables: rank multiplier 19.5 plus object weights, durability,
     hit-damage probabilities, break rewards and free-box rules. Values are long-run expected
     resources per actual Realm run/tool. Sand is Basic/White equivalent (Blue x5, Purple x25). */
  const CALC_SEASONS = {
    // S1_SCORING_METHOD_REFRESH_V1: shared acquisition optimizer; S1 scoring constants remain unchanged.
    // S1: Skills follow Character level, Relics unlock +11/+12/+13/+14 at Lv.100/110/120/130,
    // Fantomons unlock to the next 10-level band (so Character Lv.130 opens Fantomons through Lv.140), while Gear can continue above Character level.
    s1:{key:'s1',name:'Season 1',nextName:'Season 2',end:S1_END,deadline:'device-local',scoreFloor:100,relicFloor:10,starBase:10,scorePerStar:100,weights:{character:100,gear:38,skill:13,relic:57,fanto:14},skillCap:null,relicCap:null,fantoCap:null,gearCap:null,realmMaxLevel:90,realm:{ore:610,essence:1000,sand:568,rolla:9000},map:{ore:900,essence:1475,sand:838,rolla:9000,bigRate:0},optimizeRelic:true,optimizeFanto:true},
    // S2 scoring constants are well-established. Live Global evidence confirms Gear, Skills and Relic ranks can advance above Character level.
    // The optimizer therefore treats those three systems as resource/table-limited rather than Character-level gated.
    // Fantomon growth uses a resonance-style 10-level soft gate: the next decade opens only after all four scoring Fantomons reach the current decade boundary.
    s2:{key:'s2',name:'Season 2',nextName:'Season 3',end:S2_END,deadline:'device-local',scoreFloor:130,relicFloor:13,starBase:45,scorePerStar:27,weights:{character:100,gear:18,skill:7,relic:33,fanto:8},skillCap:null,relicCap:null,fantoCap:null,gearCap:null,realmMaxLevel:120,realm:{ore:1888.455092195316,essence:2645.717313492359,sand:1797.432822048046,rolla:19169.242644394664},map:{ore:1400,essence:1770,sand:1180,rolla:14000,bigRate:0.0932},optimizeRelic:true,optimizeFanto:true}
  };

  /* S2_SCORING_SOURCE_CONFIRM_V1
     Cross-checked against live-player CN/TW S2 references: scoring begins above Lv.130
     (Relics above +13), weights are Character 100 / Gear 18 / Skill 7 / Fantomon 8 /
     Relic 33, S2 contributes 45 fixed Primostars, and progression converts at 27 score
     per Primostar. Existing 920-star benchmark remains the regression check. */
  /* S2_PRIMO_READY_V1
     Season 2 is prepared in parallel; Season 1 remains the active calculator until the
     existing season boundary switches activeCalcConfig() to S2.
     Cross-region S2 scoring references agree on:
       - Character/Gear/Skill/Fantomon floor: Lv.130
       - Relic scoring starts above +13
       - +45 fixed Primostars
       - 27 progression score per Primostar
       - Character 100 / Gear 18 / Skill 7 / Relic 33 / Fantomon 8 per level
     Global live UI should still be spot-checked at rollover before changing any constants. */
  const S2_PLANNER_START_LEVEL = 120;
  // PRESEASON_UNLOCK_PREVIEW_V4: Lv.120-130 may preview the first post-floor Fantomon
  // planning state without awarding fake pre-Lv.130 Season Power. Gear, Skills and Relic
  // ranks are not Character-level gated in S2; this preview now applies only to the
  // resonance-gated Fantomon planning rule.
  const S2_FULL_SEASONAL_PREVIEW_LEVEL = 131;

  const S2_PRIMO_META = Object.freeze({
    modelStatus:'cross-region-confirmed-global-spotcheck',
    scoreFloor:130,
    relicFloor:13,
    fixedStars:45,
    scorePerStar:27,
    weights:Object.freeze({character:100,gear:18,skill:7,relic:33,fanto:8}),
    commonTargets:Object.freeze([680,800,920,1060]),
    /* S2_PRIMO_BENCHMARK_V2
       Published S2 920 end-state: 131 carried S1 stars, Lv.190 at ~80%, Gear 195,
       Skills 180, four deployed Fantomons represented as 175/175/173/173, Relics +19.
       The prepared S2 formula must reconstruct exactly 920 total Primostars. */
    benchmark:Object.freeze({
      carriedStars:131,character:190.8,gear:Object.freeze([195,195,195,195,195]),skill:180,
      fantomons:Object.freeze([175,175,173,173]),relic:19,expectedTotalStars:920
    }),
    milestones:Object.freeze([
      Object.freeze({level:106,label:'T4 class'}),
      Object.freeze({level:108,label:'Adult Fantomon'}),
      Object.freeze({level:116,label:'Tower'}),
      Object.freeze({level:120,label:'Max S2 Realm bracket'}),
      Object.freeze({level:130,label:'Season Power scoring / second dungeon'})
    ])
  });
  /* S2_SCORING_START_PREP_V1
     This calculator is a Season Power / Primostar planner, not a Lv.100→130 launch-day simulator.
     QY's current Global timeline puts S2 Season Power at Player Lv.130; Lv.120 is only the
     maximum S2 Material Realm / open-map bracket. New S2 calculator states therefore begin
     from a representative scoring-unlock profile. Saved materials, Cart rates and Bed EXP start at 0 so the player must enter real production values.
     The heavy optimizer stays paused until Bed EXP and all four Cart/hr rates are provided. */
  const S2_SCORING_START_DEFAULTS=Object.freeze({
    targetStars:680,
    // QY labels 128 as an S1 F2P/Light recommendation; it is only a starter/example carry value.
    historicalStars:128,
    charLevel:130,charExp:0,bedExp:0,finishEarlyDays:0,
    skillLevel:130,relicLevel:13,fantomonLevel:130,gearLevel:130,
    exactGearLevels:'',
    // S2_REQUIRED_INPUT_DEFAULTS_V1: never guess production. Saved materials, Cart rates and Bed EXP start at zero.
    oreCurrent:0,oreRate:0,essenceCurrent:0,essenceRate:0,
    sandCurrent:0,sandBlueCurrent:0,sandEpicCurrent:0,sandRate:0,
    treatCurrent:0,treatPremiumCurrent:0,treatDeluxeCurrent:0,treatRate:0,
    // ROUTINE_SPEND_DEFAULTS_V1: safe baseline routine plan for a fresh/reset S2 calculator.
    shopRefreshesDaily:1,
    hammerCurrent:0,knucklesCurrent:0,shovelCurrent:0,
    staminaMode:'auto',realmDailyOre:2,realmDailyEssence:2,realmDailySand:2,
    refinedOreCurrent:'',exactSkillLevels:'',exactRelicLevels:'',exactFantoLevels:''
  });
  const S2_SCORING_START_CHECKS=Object.freeze({});
  /* S2_ZERO_SCORE_DEFAULTS_V1
     The assumed scoring-start profile sits exactly on every S2 scoring floor. It is a
     neutral starting snapshot: carried/fixed Primostars may exist, but assumed progression
     itself must contribute exactly 0 Season Power before the optimizer recommends upgrades. */
  function validateS2ScoringStartDefaults(){
    const d=S2_SCORING_START_DEFAULTS,c=CALC_SEASONS.s2,w=c.weights;
    const gear=Array(5).fill(Number(d.gearLevel)||0);
    const score=
      Math.max(0,(Number(d.charLevel)||0)-c.scoreFloor)*w.character +
      gear.reduce((sum,l)=>sum+Math.max(0,(Number(l)||0)-c.scoreFloor)*w.gear,0) +
      Math.max(0,(Number(d.skillLevel)||0)-c.scoreFloor)*8*w.skill +
      Math.max(0,(Number(d.relicLevel)||0)-c.relicFloor)*20*w.relic +
      Math.max(0,(Number(d.fantomonLevel)||0)-c.scoreFloor)*4*w.fanto;
    if(score!==0) console.warn('S2_ZERO_SCORE_DEFAULTS_V1: assumed scoring-start progression must contribute 0 Season Power.',{score,defaults:d});
    return score===0;
  }
  validateS2ScoringStartDefaults();
  if(!(S2_PLANNER_START_LEVEL < CALC_SEASONS.s2.scoreFloor)){
    console.warn('S2_PLANNER_START_V1: planning start must remain below the Season Power score floor.',{plannerStart:S2_PLANNER_START_LEVEL,scoreFloor:CALC_SEASONS.s2.scoreFloor});
  }

  function validateS2PrimoModel(){
    const c=CALC_SEASONS.s2,m=S2_PRIMO_META,w=c.weights||{},mw=m.weights;
    const constantsOk=c.scoreFloor===m.scoreFloor &&
      c.relicFloor===m.relicFloor &&
      c.starBase===m.fixedStars &&
      c.scorePerStar===m.scorePerStar &&
      w.character===mw.character && w.gear===mw.gear && w.skill===mw.skill &&
      w.relic===mw.relic && w.fanto===mw.fanto;
    const b=m.benchmark;
    const benchmarkScore=
      Math.floor(Math.max(0,b.character-m.scoreFloor)*m.weights.character+1e-9) +
      b.gear.reduce((sum,l)=>sum+Math.max(0,l-m.scoreFloor)*m.weights.gear,0) +
      (Math.max(0,b.skill-m.scoreFloor)*8*m.weights.skill) +
      b.fantomons.reduce((sum,l)=>sum+Math.max(0,l-m.scoreFloor)*m.weights.fanto,0) +
      (Math.max(0,b.relic-m.relicFloor)*20*m.weights.relic);
    const benchmarkTotal=b.carriedStars+m.fixedStars+Math.floor(benchmarkScore/m.scorePerStar);
    const benchmarkOk=benchmarkTotal===b.expectedTotalStars;
    if(!constantsOk) console.warn('S2_PRIMO_READY_V1: Season 2 scoring constants drifted from the validated model.',{config:c,expected:m});
    if(!benchmarkOk) console.warn('S2_PRIMO_BENCHMARK_V2: Season 2 920-star benchmark no longer reconstructs correctly.',{benchmarkScore,benchmarkTotal,expected:b.expectedTotalStars});
    return constantsOk&&benchmarkOk;
  }
  validateS2PrimoModel();

  // QY Maple Astral Pact thresholds. Primostars are cumulative across seasons; S2 continues after S1.
  const ASTRAL_PACT_NODES = [
    // Season 1 · Witching Hours
    [5,'atk',1],[10,'ascension',3],[15,'def',1],[20,'gem',5],[25,'hp',1],[30,'dungeon',2],[35,'spd',1],[40,'exp',2],
    [48,'atk',1],[56,'ascension',3],[64,'def',1],[72,'dungeon',2],[80,'hp',1],[88,'gem',5],[96,'spd',1],[104,'exp',2],
    [116,'atk',1],[128,'ascension',3],[140,'def',1],[152,'gem',5],[164,'hp',1],[176,'dungeon',2],[188,'spd',1],[200,'exp',2],
    [215,'atk',1],[230,'ascension',3],[245,'def',1],[260,'gem',5],[275,'hp',1],[290,'dungeon',2],[305,'spd',1],[320,'exp',2],
    [340,'atk',1],[360,'ascension',3],[380,'def',1],[400,'gem',5],[420,'hp',1],[440,'dungeon',2],[460,'spd',1],[480,'exp',2],
    // Season 2 · Crossed Paths
    [505,'atk',1],[530,'ascension',3],[555,'def',1],[580,'gem',5],[605,'hp',1],[630,'dungeon',2],[655,'spd',1],[680,'exp',2],
    [710,'atk',1],[740,'ascension',3],[770,'def',1],[800,'gem',5],[830,'hp',1],[860,'dungeon',2],[890,'spd',1],[920,'exp',2],
    [955,'atk',1],[990,'ascension',3],[1025,'def',1],[1060,'gem',5],[1095,'hp',1],[1130,'dungeon',2],[1165,'spd',1],[1200,'exp',2],
    [1240,'atk',1],[1280,'ascension',3],[1320,'def',1],[1360,'gem',5],[1400,'hp',1],[1440,'dungeon',2],[1480,'spd',1],[1520,'exp',2],
    [1565,'atk',1],[1610,'ascension',3],[1655,'def',1],[1700,'gem',5],[1745,'hp',1],[1790,'dungeon',2],[1835,'spd',1],[1880,'exp',2]
  ];
  const ASTRAL_LABELS={atk:'ATK',def:'DEF',hp:'HP',spd:'SPD',ascension:'Ascension drop rate',gem:'Gem acquisition',dungeon:'Dungeon double reward',exp:'EXP gain'};
  const ASTRAL_ORDER=['atk','def','hp','spd','ascension','gem','dungeon','exp'];

  const LEGACY_GEAR_IDS = ['gearWeapon','gearOffhand','gearHelmet','gearArmor','gearBoots'];
  const GEAR_OUTPUT_IDS = ['targetGearWeapon','targetGearOffhand','targetGearHelmet','targetGearArmor','targetGearBoots'];
  const INPUT_IDS = [
    'targetStars','historicalStars','charLevel','charExp','bedExp','finishEarlyDays','skillLevel','relicLevel','fantomonLevel','gearLevel',
    'oreCurrent','oreRate','essenceCurrent','essenceRate','sandCurrent','sandBlueCurrent','sandEpicCurrent','sandRate','treatCurrent','treatPremiumCurrent','treatDeluxeCurrent','treatRate','shopRefreshesDaily',
    'hammerCurrent','knucklesCurrent','shovelCurrent','staminaMode','realmDailyOre','realmDailyEssence','realmDailySand','refinedOreCurrent','exactSkillLevels','exactRelicLevels','exactFantoLevels','exactGearLevels'
  ];
  const CHECK_IDS = [];
  const defaults = Object.create(null);
  INPUT_IDS.forEach(id => defaults[id] = document.getElementById(id)?.value ?? '');
  CHECK_IDS.forEach(id => defaults[id] = document.getElementById(id)?.checked ?? false);
  defaults.gearLocked = false;
  defaults.theme = 'dark';
  if(!defaults.staminaMode) defaults.staminaMode = 'auto'; // STAMINA_AUTO_DEFAULT_V1

  const $ = id => document.getElementById(id);

  /* COMPACT_NUMBER_INPUTS_V1
     High-volume calculator fields accept shorthand such as 22.7k, 1.3m, and 2b.
     Values are expanded to their full numeric form on commit so persisted state stays plain. */
  const COMPACT_NUMBER_INPUT_IDS = new Set([
    'charExp','bedExp',
    'oreCurrent','oreRate','essenceCurrent','essenceRate',
    'sandCurrent','sandBlueCurrent','sandEpicCurrent','sandRate',
    'treatCurrent','treatPremiumCurrent','treatDeluxeCurrent','treatRate',
    'hammerCurrent','knucklesCurrent','shovelCurrent','refinedOreCurrent'
  ]);
  function parseCompactNumber(raw,fallback=0){
    if(typeof raw==='number') return Number.isFinite(raw)?raw:fallback;
    const s=String(raw ?? '').trim().replace(/,/g,'');
    if(!s) return fallback;
    const match=s.match(/^([+-]?(?:\d+(?:\.\d*)?|\.\d+))\s*([kmb])?$/i);
    if(!match) return fallback;
    const multiplier=match[2]?({k:1e3,m:1e6,b:1e9})[match[2].toLowerCase()]:1;
    const value=Number(match[1])*multiplier;
    return Number.isFinite(value)?value:fallback;
  }
  function normalizeCompactNumberInput(id){
    if(!COMPACT_NUMBER_INPUT_IDS.has(id)) return;
    const el=$(id);
    if(!el) return;
    const raw=String(el.value ?? '').trim();
    if(!raw) return;
    const value=parseCompactNumber(raw,NaN);
    if(Number.isFinite(value)) el.value=String(value);
  }
  function enableCompactNumberInputs(){
    COMPACT_NUMBER_INPUT_IDS.forEach(id=>{
      const el=$(id);
      if(!el) return;
      if(el.type==='number') el.type='text';
      el.inputMode='decimal';
      el.autocomplete='off';
      el.dataset.compactNumber='1';
      const hint='Supports k/m/b shorthand (example: 22.7k = 22700, 1.3m = 1300000).';
      el.title=el.title?`${el.title} ${hint}`:hint;
    });
  }
  enableCompactNumberInputs();
  const n = (id, fallback=0) => parseCompactNumber($(id)?.value,fallback);
  const staminaMode = () => {
    const raw = $('staminaMode')?.value || 'auto';
    return ['auto','ore','essence','sand'].includes(raw) ? raw : 'auto';
  };
  const staminaModeLabel = (mode = staminaMode()) => ({ore:'Ore',auto:'Auto',essence:'Skill Essence',sand:'Chrono Sand'})[mode] || 'Ore';
  /* OPTIMIZER_CLEANUP_V5: one optimizer policy only — raw-first, acquisition-efficient. */
  /* EPIC_CHRONO_SAND_SAVED_V1: Rare/Blue = 5 Basic; Epic/Purple = 25 Basic. Shop average stays unchanged until an Epic shop roll is observed. */
  const SAND_BLUE_EQ=5, SAND_EPIC_EQ=25;
  function savedSandEquivalent(){
    return Math.max(0,n('sandCurrent')) + Math.max(0,n('sandBlueCurrent'))*SAND_BLUE_EQ + Math.max(0,n('sandEpicCurrent'))*SAND_EPIC_EQ;
  }
  const TREAT_BASIC_EXP=50, TREAT_PREMIUM_EQ=8, TREAT_DELUXE_EQ=40;
  function savedTreatEquivalent(){
    return Math.max(0,n('treatCurrent')) + Math.max(0,n('treatPremiumCurrent'))*TREAT_PREMIUM_EQ + Math.max(0,n('treatDeluxeCurrent'))*TREAT_DELUXE_EQ;
  }

  // CG_S2_SHOP_OBSERVED_N19_V1
  // Charming Glance S2 shop averages measured from nineteen observed shop pages.
  // Sep. 10 screenshots add four more observed pages (refreshes 7-10).
  // Keep regular Chrono Sand and Rare Chrono Sand separate in the raw sample data.
  // The optimizer converts Rare Chrono Sand at the same 5:1 ratio used by saved inventory.
  const S2_SHOP_OBSERVED_PAGES=Object.freeze([
    Object.freeze({ore:3450,essence:1200,sand:1500,rareSand:270,treat:180}),
    Object.freeze({ore:5250,essence:1650,sand:0,rareSand:330,treat:110}),
    Object.freeze({ore:3000,essence:3000,sand:1500,rareSand:0,treat:135}),
    Object.freeze({ore:1650,essence:1800,sand:1800,rareSand:270,treat:245}),
    Object.freeze({ore:3000,essence:3150,sand:1650,rareSand:0,treat:110}),
    Object.freeze({ore:1350,essence:4950,sand:0,rareSand:270,treat:180}),
    Object.freeze({ore:4050,essence:1200,sand:1350,rareSand:0,treat:135}),
    Object.freeze({ore:1350,essence:1800,sand:0,rareSand:330,treat:510}),
    Object.freeze({ore:1650,essence:2850,sand:0,rareSand:600,treat:180}),
    Object.freeze({ore:3000,essence:2400,sand:1500,rareSand:0,treat:135}),
    Object.freeze({ore:1350,essence:3150,sand:2850,rareSand:0,treat:110}),
    // Sep. 9 · Vendor refresh 7.
    Object.freeze({ore:1650,essence:0,sand:3000,rareSand:600,treat:180}),
    // Sep. 9 · Vendor refresh 8.
    Object.freeze({ore:1350,essence:1650,sand:2850,rareSand:270,treat:180}),
    // Sep. 9 · Vendor refresh 9.
    Object.freeze({ore:3000,essence:1200,sand:1650,rareSand:0,treat:345}),
    // Sep. 9 · Vendor refresh 10.
    Object.freeze({ore:3000,essence:1350,sand:2850,rareSand:0,treat:110}),
    // Sep. 10 · Vendor refresh 7: Ore 1,200+1,650+1,650; no Battle Essence;
    // regular Chrono Sand 1,200; Rare Chrono Sand 330; Basic Treats 180.
    Object.freeze({ore:4500,essence:0,sand:1200,rareSand:330,treat:180}),
    // Sep. 10 · Vendor refresh 8: Ore 1,200+1,200; Battle Essence 1,200;
    // regular Chrono Sand 1,800; no Rare Chrono Sand; Basic Treats 150+180.
    Object.freeze({ore:2400,essence:1200,sand:1800,rareSand:0,treat:330}),
    // Sep. 10 · Vendor refresh 9: Ore 1,800; Battle Essence 1,500;
    // regular Chrono Sand 1,500+1,500+1,500; no Rare Chrono Sand; Basic Treats 165.
    Object.freeze({ore:1800,essence:1500,sand:4500,rareSand:0,treat:165}),
    // Sep. 10 · Vendor refresh 10: Ore 1,350; no Battle Essence;
    // regular Chrono Sand 1,350+1,800; Rare Chrono Sand 300; Basic Treats 110+135.
    Object.freeze({ore:1350,essence:0,sand:3150,rareSand:300,treat:245})
  ]);
  function s2ShopObservedAverage(){
    const pages=S2_SHOP_OBSERVED_PAGES;
    const n=pages.length||1;
    const total=pages.reduce((a,p)=>({
      ore:a.ore+p.ore,
      essence:a.essence+p.essence,
      sand:a.sand+p.sand,
      rareSand:a.rareSand+p.rareSand,
      treat:a.treat+p.treat
    }),{ore:0,essence:0,sand:0,rareSand:0,treat:0});
    return Object.fromEntries(Object.entries(total).map(([k,v])=>[k,v/n]));
  }

  // S1 keeps the older conservative fallback because the observed pages above are S2-only.
  const DAILY_SHOP_CORE_BUNDLE_FACTOR=2/3;
  const DAILY_SHOP_TREAT_EQ_PER_REFRESH=35;
  function dailyShopMatsPerRefresh(cfg=activeCalcConfig()){
    if(cfg?.key==='s2' && S2_SHOP_OBSERVED_PAGES.length){
      const a=s2ShopObservedAverage();
      return {
        ore:a.ore,
        essence:a.essence,
        sand:a.sand+a.rareSand*SAND_BLUE_EQ,
        treat:a.treat,
        sandRegular:a.sand,
        sandRare:a.rareSand
      };
    }
    const roundDown25=v=>Math.max(0,Math.floor((Number(v)||0)/25)*25);
    const map=cfg?.map||{};
    return {
      ore:roundDown25((Number(map.ore)||0)*DAILY_SHOP_CORE_BUNDLE_FACTOR),
      essence:roundDown25((Number(map.essence)||0)*DAILY_SHOP_CORE_BUNDLE_FACTOR),
      sand:roundDown25((Number(map.sand)||0)*DAILY_SHOP_CORE_BUNDLE_FACTOR),
      treat:DAILY_SHOP_TREAT_EQ_PER_REFRESH
    };
  }
  function dailyShopMaterialEstimate(cfg=activeCalcConfig(),daysOverride=null){
    const active=cfg.key==='s1'||cfg.key==='s2';
    // SHOP_BUYOUTS_V1: input counts full shop pages purchased, not refresh presses.
    // 0 = off; 1 = base page only; 2 = base page + one restock + second full-page buyout.
    const buyouts=active?clamp(Math.floor(n('shopRefreshesDaily',0)),0,20):0;
    const days=active?Math.max(0,Number.isFinite(Number(daysOverride))?Math.floor(Number(daysOverride)):futureRealmPurchaseDays(cfg)):0;
    const perBuyout=dailyShopMatsPerRefresh(cfg);
    const perDay=Object.fromEntries(Object.entries(perBuyout).map(([k,v])=>[k,v*buyouts]));
    const total=Object.fromEntries(Object.entries(perDay).map(([k,v])=>[k,v*days]));
    return {
      active,refreshes:buyouts,buyouts,days,perRefresh:perBuyout,perBuyout,perDay,total,
      sampleCount:cfg.key==='s2'?S2_SHOP_OBSERVED_PAGES.length:0
    };
  }
  function applyS2ScoringStartDefaults(){
    Object.entries(S2_SCORING_START_DEFAULTS).forEach(([id,value])=>{ if($(id)) $(id).value=String(value); });
    Object.entries(S2_SCORING_START_CHECKS).forEach(([id,value])=>{ if($(id)) $(id).checked=!!value; });
  }
  function realmDailyValue(key){
    const ids={ore:'realmDailyOre',essence:'realmDailyEssence',sand:'realmDailySand'};
    const id=ids[key];
    return clamp(Math.floor(n(id,4)),0,MAX_REALM_REFRESHES_PER_DAY);
  }
  function applyRecommendedRealmRefreshes(button){
    const values={
      realmDailyOre:clamp(Math.floor(Number(button?.dataset?.ore)||0),0,MAX_REALM_REFRESHES_PER_DAY),
      realmDailyEssence:clamp(Math.floor(Number(button?.dataset?.essence)||0),0,MAX_REALM_REFRESHES_PER_DAY),
      realmDailySand:clamp(Math.floor(Number(button?.dataset?.sand)||0),0,MAX_REALM_REFRESHES_PER_DAY)
    };
    Object.entries(values).forEach(([id,value])=>{
      const el=$(id);
      if(!el) return;
      el.value=String(value);
      markManualSnapshot(id);
    });
    resetMaxAchievableUi();
    saveState();
    scheduleCalculatorUpdate(0);
  }
  function futureRealmPurchaseDays(cfg=activeCalcConfig()){
    const now=Date.now();
    const cutoff=upgradeFinishCutoffMs(cfg);
    if(cutoff<=now) return 0;
    const key=`${cfg.key}|${cutoff}`;
    if(FUTURE_REALM_DAY_CACHE.key===key && now<FUTURE_REALM_DAY_CACHE.validUntil) return FUTURE_REALM_DAY_CACHE.value;
    const nextReset=nextPacificResetMs(now);
    const value=countFuturePacificResets(now,cutoff);
    FUTURE_REALM_DAY_CACHE={key,value,validUntil:Math.min(nextReset,now+60_000)};
    return value;
  }
  function plannedRealmRunsFor(key,cfg=activeCalcConfig()){
    return futureRealmPurchaseDays(cfg)*realmDailyValue(key)*REALM_RUNS_PER_REFRESH;
  }
  function renderRealmToolProjection(cfg=activeCalcConfig()){
    const days=Math.max(0,Math.floor(futureRealmPurchaseDays(cfg)||0));
    const daily={ore:realmDailyValue('ore'),essence:realmDailyValue('essence'),sand:realmDailyValue('sand')};
    const added={ore:days*daily.ore*REALM_RUNS_PER_REFRESH,essence:days*daily.essence*REALM_RUNS_PER_REFRESH,sand:days*daily.sand*REALM_RUNS_PER_REFRESH};
    const totals={
      hammer:Math.max(0,Math.floor(n('hammerCurrent',0)))+added.ore,
      knuckles:Math.max(0,Math.floor(n('knucklesCurrent',0)))+added.essence,
      shovel:Math.max(0,Math.floor(n('shovelCurrent',0)))+added.sand
    };
    const onHand={
      hammer:Math.max(0,Math.floor(n('hammerCurrent',0))),
      knuckles:Math.max(0,Math.floor(n('knucklesCurrent',0))),
      shovel:Math.max(0,Math.floor(n('shovelCurrent',0)))
    };
    const realmYield=cfg.realm||{};
    const currentLevel=Math.max(1,Math.floor(n('charLevel',cfg.key==='s2'?100:122)));
    const worthLabel=currentLevel<cfg.realmMaxLevel?`Worth at Lv.${cfg.realmMaxLevel} max`:'Worth now';
    if($('hammerMaterialValue')) $('hammerMaterialValue').textContent=`${worthLabel}: ~${fmtCompact(onHand.hammer*(Number(realmYield.ore)||0))} Raw Ore`;
    if($('knucklesMaterialValue')) $('knucklesMaterialValue').textContent=`${worthLabel}: ~${fmtCompact(onHand.knuckles*(Number(realmYield.essence)||0))} Skill Essence`;
    if($('shovelMaterialValue')) $('shovelMaterialValue').textContent=`${worthLabel}: ~${fmtCompact(onHand.shovel*(Number(realmYield.sand)||0))} Chrono Sand`;
    if($('hammerProjected')) $('hammerProjected').textContent=`Season-end estimate: ${fmt(totals.hammer)}`;
    if($('knucklesProjected')) $('knucklesProjected').textContent=`Season-end estimate: ${fmt(totals.knuckles)}`;
    if($('shovelProjected')) $('shovelProjected').textContent=`Season-end estimate: ${fmt(totals.shovel)}`;
    if($('realmDailyGain')) $('realmDailyGain').textContent=`+${fmt(daily.ore*REALM_RUNS_PER_REFRESH)} Hammers · +${fmt(daily.essence*REALM_RUNS_PER_REFRESH)} Knuckles · +${fmt(daily.sand*REALM_RUNS_PER_REFRESH)} Shovels per reset`;
    if($('realmDaysRemaining')) $('realmDaysRemaining').textContent=`${fmt(days)} future purchase day${days===1?'':'s'} · plan adds ${fmt(added.ore)} Hammers · ${fmt(added.essence)} Knuckles · ${fmt(added.sand)} Shovels`;
  }
  function suggestedRealmDailyPlan(plan,cfg=activeCalcConfig()){
    const current={ore:realmDailyValue('ore'),essence:realmDailyValue('essence'),sand:realmDailyValue('sand')};
    const out={...current,changed:false,needsExtra:false,impossible:false,futureDays:Math.max(0,Math.floor(futureRealmPurchaseDays(cfg)||0))};
    if(!plan?.realm) return out;
    for(const key of ['ore','essence','sand']){
      const top=plan.realm?.[key];
      if(!top) continue;
      const packs=Number(top.packs);
      if(Number.isFinite(packs)&&packs>0&&out.futureDays>0&&top.feasible!==false){
        const counts=Array.isArray(top.dailyCounts)?top.dailyCounts.slice(1).map(v=>Math.max(0,Math.floor(Number(v)||0))):[];
        const maxExtra=counts.length?Math.max(0,...counts):Math.ceil(packs/out.futureDays);
        out[key]=clamp(current[key]+maxExtra,0,MAX_REALM_REFRESHES_PER_DAY);
        out.needsExtra=true;
        if(out[key]!==current[key]) out.changed=true;
      }else if(top.feasible===false && Number(top.remainingAfterMax)>0 && Number(top.maxPacks)>0){
        out[key]=MAX_REALM_REFRESHES_PER_DAY;
        out.impossible=true;
        if(out[key]!==current[key]) out.changed=true;
      }
    }
    return out;
  }
  function renderRealmDailyRecommendations(plan,resources,cfg=activeCalcConfig()){
    const defs=[
      {key:'ore',out:'realmDailyOreRec'},
      {key:'essence',out:'realmDailyEssenceRec'},
      {key:'sand',out:'realmDailySandRec'}
    ];
    const suggested=suggestedRealmDailyPlan(plan,cfg);
    for(const d of defs){
      const el=$(d.out); if(!el) continue;
      el.classList.remove('realmRecommendUp','realmRecommendMax');
      if(!plan){ el.textContent='Recommended: —'; continue; }
      const selected=realmDailyValue(d.key);
      const top=plan.realm?.[d.key];
      if(top?.feasible===false && Number(top.remainingAfterMax)>0){
        el.textContent=`20/day max · still ${fmt(Math.ceil(Number(top.remainingAfterMax)||0))} short`;
        el.classList.add('realmRecommendMax');
      }else if(suggested[d.key]>selected){
        el.textContent=`Suggested: up to ${suggested[d.key]}/day`;
        el.classList.add('realmRecommendUp');
      }else if(Number(top?.packs)>0){
        el.textContent='Extra Realm entries required';
        el.classList.add('realmRecommendUp');
      }else{
        el.textContent='Covers target';
      }
    }
  }
  const fmt = x => Math.round(x).toLocaleString('en-US');
  const fmtCompact = x => {
    const a = Math.abs(x);
    if (a >= 1_000_000) return `${(x/1_000_000).toFixed(a >= 10_000_000 ? 1 : 2).replace(/\.0+$/,'')}M`;
    if (a >= 1000) return `${(x/1000).toFixed(a >= 100_000 ? 1 : 1).replace(/\.0$/,'')}K`;
    return fmt(x);
  };
  const clamp = (x,a,b) => Math.min(b, Math.max(a,x));
  const seasonKeyAt = (ms=Date.now()) => ms < S1_END.getTime() ? 's1' : 's2';
  const activeCalcConfig = () => CALC_SEASONS[seasonKeyAt(Date.now())];

  let gearLocked = false;
  let snapshotAtMs = Date.now();
  let snapshotSeason = seasonKeyAt(snapshotAtMs);
  let snapshotCarry = {ore:0, essence:0, sand:0, treat:0, exp:0};
  let snapshotStateLoaded = false;
  const numberFromState = (state,id,fallback=0) => {
    const v = Number(state?.[id]);
    return Number.isFinite(v) ? v : fallback;
  };

  function remainingHoursAt(ms, cfg=activeCalcConfig()){ return Math.max(0, (cfg.end.getTime() - ms) / 3_600_000); }

  // BUILD_DOMINATOR_RESET_PERF_V1
  // Pacific reset math is hot in S2: Realm/tool/resource projection asks the same
  // question many times during a solve. Reuse Intl formatters and memoize each
  // first-reset/cutoff pair while preserving exact PDT/PST behavior.
  const PACIFIC_DATE_TIME_DTF=new Intl.DateTimeFormat('en-US',{timeZone:'America/Los_Angeles',year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',second:'2-digit',hourCycle:'h23'});
  const PACIFIC_DATE_DTF=new Intl.DateTimeFormat('en-US',{timeZone:'America/Los_Angeles',year:'numeric',month:'2-digit',day:'2-digit'});
  const FUTURE_RESET_COUNT_CACHE=new Map();
  let FUTURE_REALM_DAY_CACHE={key:'',value:0,validUntil:0};
  function pacificLocalMs(iso,hour=6,minute=0){
    const [y,m,d]=iso.split('-').map(Number);
    const desiredAsUtc=Date.UTC(y,m-1,d,hour,minute,0);
    let guess=desiredAsUtc;
    for(let i=0;i<4;i++){
      const parts=Object.fromEntries(PACIFIC_DATE_TIME_DTF.formatToParts(new Date(guess)).filter(x=>x.type!=='literal').map(x=>[x.type,x.value]));
      const shownAsUtc=Date.UTC(Number(parts.year),Number(parts.month)-1,Number(parts.day),Number(parts.hour),Number(parts.minute),Number(parts.second));
      const delta=desiredAsUtc-shownAsUtc;
      guess+=delta;
      if(Math.abs(delta)<1000) break;
    }
    return guess;
  }
  function pacificIsoAt(ms){
    const parts=Object.fromEntries(PACIFIC_DATE_DTF.formatToParts(new Date(ms)).filter(x=>x.type!=='literal').map(x=>[x.type,x.value]));
    return `${parts.year}-${parts.month}-${parts.day}`;
  }
  function nextPacificResetMs(afterMs){
    const iso=pacificIsoAt(afterMs);
    const sameDay=pacificLocalMs(iso,6,0);
    return sameDay>afterMs ? sameDay : pacificLocalMs(isoAddDays(iso,1),6,0);
  }
  function countFuturePacificResets(startMs,cutoffMs){
    if(!(cutoffMs>startMs)) return 0;
    const first=nextPacificResetMs(startMs);
    if(!(first<cutoffMs)) return 0;
    const key=`${first}|${cutoffMs}`;
    if(FUTURE_RESET_COUNT_CACHE.has(key)) return FUTURE_RESET_COUNT_CACHE.get(key);
    let t=first,count=0,safety=0;
    while(t<cutoffMs && safety++<500){
      count++;
      t=pacificLocalMs(isoAddDays(pacificIsoAt(t),1),6,0);
    }
    FUTURE_RESET_COUNT_CACHE.set(key,count);
    if(FUTURE_RESET_COUNT_CACHE.size>64) FUTURE_RESET_COUNT_CACHE.delete(FUTURE_RESET_COUNT_CACHE.keys().next().value);
    return count;
  }
  /* VIEWER_DEVICE_TIMEZONE_V2
     Server/reset calculations stay anchored to Pacific internally. Every visible clock/date
     is formatted in the timezone reported by the device viewing the page. */
  function viewerTimeZone(){
    try{return Intl.DateTimeFormat().resolvedOptions().timeZone||undefined;}catch(_){return undefined;}
  }
  function viewerDateTimeFormatter(options){
    const timeZone=viewerTimeZone();
    return new Intl.DateTimeFormat(undefined,timeZone?{...options,timeZone}:options);
  }
  function localClockLabel(ms){
    return viewerDateTimeFormatter({hour:'numeric',minute:'2-digit',timeZoneName:'short'}).format(new Date(ms));
  }
  function localDeadlineLabel(date,projected=false){
    const text=viewerDateTimeFormatter({month:'long',day:'numeric',year:'numeric',hour:'numeric',minute:'2-digit',timeZoneName:'short'}).format(date).replace(' at ',' · ');
    return `${projected?'Projected · ':''}${text}`;
  }
  function localShortDateTimeLabel(value){
    const date=value instanceof Date?value:new Date(value);
    if(!Number.isFinite(date.getTime())) return '—';
    return viewerDateTimeFormatter({month:'short',day:'numeric',hour:'numeric',minute:'2-digit',timeZoneName:'short'}).format(date).replace(' at ',' · ');
  }
  function nextResetLocalLabel(){ return localClockLabel(nextPacificResetMs(Date.now())); }
  function renderLocalTimeLabels(){
    const reset=nextResetLocalLabel();
    if($('headerResetLocal')) $('headerResetLocal').textContent=`Reset: ${reset}`;
    if($('timelineResetLocal')) $('timelineResetLocal').textContent=reset;
  }
  function resourceCutoffMs(cfg=activeCalcConfig()){
    return upgradeFinishCutoffMs(cfg);
  }
  function projectionResourceHoursAt(ms,cfg=activeCalcConfig()){
    const cutoff=upgradeFinishCutoffMs(cfg);
    const capped=Math.min(ms,cutoff);
    if(capped>=cutoff) return 0;
    const wallHours=(cutoff-capped)/3_600_000;
    const boostHours=2*countFuturePacificResets(capped,cutoff);
    return Math.max(0,wallHours+boostHours);
  }

  function advanceCharacterSnapshot(deltaExp,cfg=CALC_SEASONS[snapshotSeason] || activeCalcConfig()){
    let lvl = Math.max(1, Math.floor(n('charLevel',cfg.key==='s2'?100:122)));
    let exp = Math.max(0,n('charExp',0)) + Math.max(0,deltaExp);
    let safety=0;
    while(safety++ < 400){
      const req = expRequiredForLevel(lvl,cfg);
      if(exp < req) break;
      exp -= req;
      lvl++;
    }
    if($('charLevel')) $('charLevel').value = String(lvl);
    if($('charExp')) $('charExp').value = String(Math.max(0,Math.floor(exp)));
  }

  function rollSnapshotForward(nowMs=Date.now(), persist=true){
    if(!snapshotStateLoaded) return false;
    if(!Number.isFinite(snapshotAtMs) || snapshotAtMs <= 0){ snapshotAtMs=nowMs; return false; }
    const cfg=CALC_SEASONS[snapshotSeason] || activeCalcConfig();
    const cappedNow=Math.min(nowMs,cfg.end.getTime());
    if(cappedNow <= snapshotAtMs + 1000) return false;

    // Deterministic values age only inside the season that produced this snapshot.
    // This prevents a stale S1 state from silently becoming an S2 state after reset.
    const oldResourceHours = projectionResourceHoursAt(snapshotAtMs,cfg);
    const newResourceHours = projectionResourceHoursAt(cappedNow,cfg);
    const elapsedResourceHours = Math.max(0, oldResourceHours-newResourceHours);

    /* AUTO_AGE_REALM_TOOLS_V1
       Treat the saved Daily purchase plan like Cart production: once a planned 6 AM
       reset has actually passed, move those purchased entries into the on-hand tool counts.
       Future projection then loses that reset at the same time, so season-end tool totals stay
       stable instead of requiring the user to manually add Hammers/Knuckles/Shovels each day.
       Match futureRealmPurchaseDays(): purchases stop at the optional finishing-window cutoff. */
    const realmCutoffMs=finishScoreCutoffMs(cfg);
    const realmAgeEnd=Math.min(cappedNow,realmCutoffMs);
    const elapsedRealmResets=realmAgeEnd>snapshotAtMs
      ? countFuturePacificResets(snapshotAtMs,realmAgeEnd)
      : 0;
    if(elapsedRealmResets>0){
      const toolDefs=[
        ['hammerCurrent','ore'],
        ['knucklesCurrent','essence'],
        ['shovelCurrent','sand']
      ];
      toolDefs.forEach(([currentId,key])=>{
        const gained=elapsedRealmResets*realmDailyValue(key)*REALM_RUNS_PER_REFRESH;
        if(gained>0 && $(currentId)) $(currentId).value=String(Math.max(0,Math.floor(n(currentId,0)))+gained);
      });
    }

    const resourceDefs = [
      ['oreCurrent','oreRate','ore'],
      ['essenceCurrent','essenceRate','essence'],
      ['sandCurrent','sandRate','sand'],
      ['treatCurrent','treatRate','treat']
    ];
    resourceDefs.forEach(([currentId,rateId,key])=>{
      const produced = Math.max(0,n(rateId,0))*elapsedResourceHours + Math.max(0,Number(snapshotCarry[key])||0);
      const whole = Math.floor(produced + 1e-9);
      snapshotCarry[key] = Math.max(0, produced-whole);
      if(whole>0 && $(currentId)) $(currentId).value = String(Math.max(0,n(currentId,0))+whole);
    });

    const bedRate=Math.max(0,n('bedExp',0));
    const producedExp=bedRate*elapsedResourceHours + Math.max(0,Number(snapshotCarry.exp)||0);
    const wholeExp=Math.floor(producedExp+1e-9);
    snapshotCarry.exp=Math.max(0,producedExp-wholeExp);
    if(wholeExp>0) advanceCharacterSnapshot(wholeExp,cfg);

    // Already-held Stamina is intentionally not snapshot-aged because the calculator tracks only future regenerated Stamina.
    snapshotAtMs = cappedNow;
    if(persist) saveState();
    return elapsedResourceHours>0 || elapsedRealmResets>0;
  }

  function markManualSnapshot(id){
    // Do not silently approve a season rollover just because one field was edited.
    // The dedicated rollover button confirms that the whole snapshot has been refreshed.
    if(snapshotSeason===seasonKeyAt(Date.now())) snapshotAtMs = Date.now();
    if(id==='oreCurrent') snapshotCarry.ore=0;
    if(id==='essenceCurrent') snapshotCarry.essence=0;
    if(id==='sandCurrent' || id==='sandBlueCurrent' || id==='sandEpicCurrent') snapshotCarry.sand=0;
    if(id==='treatCurrent' || id==='treatPremiumCurrent' || id==='treatDeluxeCurrent') snapshotCarry.treat=0;
    if(id==='charLevel' || id==='charExp') snapshotCarry.exp=0;
  }

  function saveState(){
    const state = {
      gearLocked,
      theme: document.documentElement.dataset.theme || 'dark',
      snapshotSchema: 8,
      snapshotAt: snapshotAtMs,
      snapshotSeason,
      snapshotCarry: {...snapshotCarry},
      panelOpen: Object.fromEntries(PANEL_OPEN_IDS.map(id => [id, !!$(id)?.open]))
    };
    INPUT_IDS.forEach(id => state[id] = $(id)?.value ?? '');
    CHECK_IDS.forEach(id => state[id] = !!$(id)?.checked);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  }
  function loadState(){
    let hadState=false;
    try{
      const state = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
      hadState = Object.keys(state).length>0;
      // SHOP_REFRESH_DEFAULT_ZERO_V1: the shop estimator is opt-in. Migrate the old inherited 3/day once.
      if(hadState && localStorage.getItem('sxs-shop-refresh-default-zero-v1')!=='1'){
        if(Number(state.shopRefreshesDaily)===3) state.shopRefreshesDaily=0;
        localStorage.setItem('sxs-shop-refresh-default-zero-v1','1');
      }
      // v39 replaces the old single Realm preset with independent per-resource daily inputs.
      // Preserve the user's prior shared preset when migrating; otherwise default each Realm to 4/day.
      if(hadState && (Number(state.snapshotSchema)||0)<5){
        const oldDaily = /^\d+$/.test(String(state.realmDailyPreset??'')) ? clamp(parseInt(state.realmDailyPreset,10),0,20) : 4;
        if(state.realmDailyOre===undefined) state.realmDailyOre=String(oldDaily);
        if(state.realmDailyEssence===undefined) state.realmDailyEssence=String(oldDaily);
        if(state.realmDailySand===undefined) state.realmDailySand=String(oldDaily);
      }
      if(hadState && state.gearLevel===undefined){
        const legacy=LEGACY_GEAR_IDS.map(id=>Number(state[id])).filter(Number.isFinite);
        if(legacy.length===5){
          state.gearLevel=String(legacy.reduce((a,b)=>a+b,0)/legacy.length);
          if(state.exactGearLevels===undefined && new Set(legacy).size>1) state.exactGearLevels=legacy.join(', ');
        }
      }
      INPUT_IDS.forEach(id => { if (state[id] !== undefined && $(id)) $(id).value = state[id]; });
      CHECK_IDS.forEach(id => { if (state[id] !== undefined && $(id)) $(id).checked = !!state[id]; });
      if(!hadState && activeCalcConfig().key==='s2') applyS2ScoringStartDefaults();
      gearLocked = false; // gear lock UI removed; optimizer always considers Gear
      document.documentElement.dataset.theme = (state.theme === 'light' || state.theme === 'dark') ? state.theme : 'dark';
      // Main calculator editors default closed, then remember the user's last open/collapsed state.
      PANEL_OPEN_IDS.forEach(id => {
        const panel=$(id);
        if(!panel) return;
        const hasSavedPanelState=state.panelOpen && typeof state.panelOpen==='object' && Object.prototype.hasOwnProperty.call(state.panelOpen,id);
        panel.open = hasSavedPanelState ? state.panelOpen[id]===true : id==='characterDetails';
      });
      if(Number.isFinite(Number(state.snapshotAt)) && Number(state.snapshotAt)>0){
        snapshotAtMs = Number(state.snapshotAt);
      } else {
        // v10 and earlier did not store a timestamp, so their values cannot be safely
        // back-filled. Treat first v11 load as the baseline rather than guessing.
        snapshotAtMs = Date.now();
      }
      snapshotSeason = (state.snapshotSeason && CALC_SEASONS[state.snapshotSeason]) ? state.snapshotSeason : seasonKeyAt(snapshotAtMs);
      if(state.snapshotCarry && typeof state.snapshotCarry==='object'){
        for(const k of Object.keys(snapshotCarry)){
          const v=Number(state.snapshotCarry[k]);
          snapshotCarry[k]=Number.isFinite(v) && v>=0 ? v : 0;
        }
      }
    } catch (_) {
      snapshotAtMs=Date.now();
      snapshotSeason=seasonKeyAt(snapshotAtMs);
      snapshotCarry={ore:0, essence:0, sand:0, treat:0, exp:0};
    }
    snapshotStateLoaded=true;
    if(hadState) rollSnapshotForward(Date.now(),false);
    updateGearLockUI();
    saveState();
  }

  function remainingHours(){ return remainingHoursAt(Date.now(),activeCalcConfig()); }
  function formatRemaining(hours){
    const mins = Math.max(0, Math.floor(hours*60));
    const d = Math.floor(mins/1440), h = Math.floor((mins%1440)/60), m = mins%60;
    return `${d}d ${h}h ${m}m remaining`;
  }

  // Exact EXP-to-next-level data keyed by CURRENT level.
  const S1_EXP_REQUIREMENTS = {
    100:886086,101:888547,102:926501,103:964086,104:1012164,105:1054111,
    106:1096529,107:1135645,108:1174997,109:1214584,110:1258533,
    111:1303677,112:1348574,113:1393941,114:1439780,115:1486091,
    116:1532872,117:1580125,118:1627849,119:1676044,120:1730017,
    121:1783360,122:1833196,124:1830000
  };
  const S2_EXP_REQUIREMENTS = {
    100:886000,101:3027527,102:3032011,103:3117883,104:3191855,105:3220513,
    106:3258763,107:3346658,108:3389858,109:3548753,110:3631694,111:3771824,
    112:3796167,113:3866624,114:3924404,115:4029348,116:4101565,117:4245434,
    118:4245686,119:4514881,120:4566377,121:4752888,122:4860000,123:5012377,
    124:5016341,125:5178619,126:5229563,127:5423881,128:5459728,129:6335318,
    130:6342809,131:6791971,132:7349165,133:7896724,134:8431041,135:8948504,
    136:9536985,137:10062872,138:10591166,139:11201308,140:11280750,141:11334730,
    142:11387696,143:11440662,144:11493628,145:11546594,146:11599560,147:11652526,
    148:11679009,149:11731975,150:11784941,151:11811613,152:11838097,153:11864580,
    154:11917547,155:11970514,156:12049964,157:12155898,158:12208865,159:12261832,
    160:12314799,161:12394079,162:12447046,163:12500012,164:12500012,165:12526495,
    166:12579461,167:12632427,168:12658910,169:12711876,170:12764842,171:12817637,
    172:12870602,173:12950050,174:13029499,175:13082464,176:13135429,177:13188395,
    178:13214878,179:13267843,180:13320809,181:13372809,182:13399290,183:13425771,
    184:13452251,185:13478732,186:13478732,187:13478732,188:13478732,189:13478732,
    190:13478732,191:13478732,192:13478732,193:13478732,194:13478732,195:13478732,
    196:13478732,197:13478732,198:13478732,199:13478732,200:13478732,201:13478732,
    202:13478732,203:13478732,204:13478732,205:13478732,206:13478732,207:13478732,
    208:13478732,209:13478732,210:13478732
  };
  /* EXACT_S2_UPGRADE_COSTS_V5
     Season-2 scoring-floor-and-above upgrade economics are sourced from the extracted live-client
     season tables used by the public multi-season calculator, rather than hand-fit extrapolations.
     Character EXP is exact from Lv.130 through the extracted table range; Fantomon feed EXP is
     exact from Lv.130 upward through its extracted range. Gear/Skill use the client season base/rate
     with game rounding to the nearest 5. S2 Relics use the Purple-Sand blessing table, and every
     fifth S2 Gear blessing costs a fixed 510 Refined Ore. Existing pre-Lv.130 catch-up curves are
     intentionally retained because the extracted seasonal table begins at the S2 scoring floor. */
  const S2_EXACT_CHARACTER_EXP_FROM_130='3ry55.41kpv.4dinh.4p95g.50pfl.5bspk.5oes9.5zok8.6b072.6o2zg.6psa6.6qxxm.6s2sw.6t7o6.6ucjg.6vheq.6wma0.6xr5a.6ybkx.6zgg7.70lbh.715wd.71qc1.72aro.73fmz.74kia.769t8.78jju.79of5.7atag.7by5r.7dnbz.7es7a.7fx2k.7fx2k.7ghi7.7hmdh.7ir8r.7jboe.7kgjo.7lley.7mq5h.7nv0q.7pkbm.7r9mj.7sehs.7tjd1.7uo8b.7v8ny.7wdj7.7xieh.7ymix.7z6yi.7zre3.80btn.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98'.split('.').map(v=>parseInt(v,36));
  const S2_EXACT_FANTOMON_EXP_FROM_130='189m.195k.1a18.1ax6.1bt4.1cp2.1dkq.1ego.1fcm.1g8k.1h48.1i06.1iw4.1js2.1knq.1ljo.1mfm.1nbk.1o78.1p36.1pz4.1qv2.1rqq.1smo.1tim.1uek.1va8.1w66.1x24.1xxs.1ytq.1zpo.20lm.21ha.22d8.2396.2454.250s.25wq.26so.27om.28ka.29g8.2ac6.2b84.2c3s.2czq.2dvo.2erm.2fna.2gj8.2hf6.2iau.2j6s.2k2q.2kyo.2luc.2mqa.2nm8.2oi6.2pdu.2q9s.2r5q.2s1o.2sxc.2tta.2up8.2vl6.2wgu.2xcs.2y8q.2z4o.300c.30wa.31s8.32o6.33ju.34fs.35bq.367e.373c.37za.38v8.39qw.3amu.3bis.3ceq.3dae.3e6c.3f2a.3fy8.3gtw.3hpu.3ils.3jhq.3kde.3l9c.3m5a.3n18.3nww.3osu.3pos.3qkg.3rge.3scc.3t8a.3u3y.3uzw.3vvu.3wrs.3xng.3yje.3zfc.40ba.416y.422w.42yu.43us.44qg.45me.46ic.47ea.489y.495w.4a1u.4axs.4btg.4cpe.4dlc.4eh0.4fcy.4g8w.4h4u.4i0i.4iwg.4jse.4koc.4lk0.4mfy.4nbw.4o7u.4p3i.4pzg.4qve.4rrc.4sn0.4tiy.4uew.4vau.4w6i'.split('.').map(v=>parseInt(v,36));
  const S2_EXACT_UPGRADE_RULES=Object.freeze({
    floor:130,gearBase:16630,gearRate:166.3,gearBlessingLimit:300,gearScaleCap:150,
    skillBase:12025,skillRate:120.25,skillBlessingLimit:150,
    relicBase:13,relicPurpleBase:1350,relicPurpleRate:135,relicBlessingLimit:15,
    refinedOreEvery5:510,rollaPerOre:2
  });

  // Late-S1 community method: use confirmed checkpoints first, then the nearest accepted late-S1 plateau.
  // 122→123 is confirmed at 1,833,196 and the user's live 124→125 value is 1.83M, so unknown 123+ steps
  // use 1.83M rather than extrapolating an artificial rising curve.
  const S1_LATE_EXP_PLATEAU = 1_830_000;
  function isEstimatedS1ExpLevel(level){
    const l=Math.floor(Number(level)||0);
    return l>=123 && !S1_EXP_REQUIREMENTS[l];
  }
  function expRequiredForLevel(level,cfg=activeCalcConfig()){
    const l=Math.max(1,Math.floor(Number(level)||1));
    if(cfg.key==='s2'){
      if(l>=S2_EXACT_UPGRADE_RULES.floor){
        const exact=S2_EXACT_CHARACTER_EXP_FROM_130[l-S2_EXACT_UPGRADE_RULES.floor];
        return Number.isFinite(exact)&&exact>0 ? exact : Infinity;
      }
      return S2_EXP_REQUIREMENTS[l] || S1_EXP_REQUIREMENTS[l] || 886_000;
    }
    if(S1_EXP_REQUIREMENTS[l]) return S1_EXP_REQUIREMENTS[l];
    if(l>=123) return S1_LATE_EXP_PLATEAU;
    return 886_086;
  }
  function s1ProjectionUsesEstimatedExp(fromLevel,toLevel){
    if(activeCalcConfig().key!=='s1') return false;
    const a=Math.max(1,Math.floor(Number(fromLevel)||1)),b=Math.max(a,Math.floor(Number(toLevel)||a));
    for(let l=a;l<=b;l++) if(isEstimatedS1ExpLevel(l)) return true;
    return false;
  }
  function characterSnapshot(cfg=activeCalcConfig()){
    let lvl=Math.max(1,Math.floor(n('charLevel',cfg.key==='s2'?100:122)));
    let exp=Math.max(0,n('charExp',0));
    let safety=0;
    while(safety++<400){
      const req=expRequiredForLevel(lvl,cfg);
      if(exp<req) break;
      exp-=req; lvl++;
    }
    const req=expRequiredForLevel(lvl,cfg);
    const pct=req>0?clamp(exp/req,0,0.999999999):0;
    return {level:lvl,exp,req,pct,decimal:lvl+pct};
  }
  /* BED_STORAGE_DISABLED_V1
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
  function projectCharacter(cfg=activeCalcConfig()){
    return projectCharacterTo(cfg.end.getTime(),cfg);
  }
  function finishEarlyDaysValue(){
    const raw=Number($('finishEarlyDays')?.value);
    // FINISH_EARLY_HALF_DAY_V1: planner cutoff supports 0.5-day increments.
    return Number.isFinite(raw)?Math.max(0,Math.round(raw*2)/2):0;
  }
  function finishScoreCutoffMs(cfg=activeCalcConfig()){
    const days=finishEarlyDaysValue();
    if(days<=0) return cfg.end.getTime();
    // FINISH_EARLY_DEVICE_LOCAL_V1: "days early" is an elapsed duration from the
    // actual season-end instant. Server/reset math remains Pacific internally, while
    // any displayed cutoff/deadline is formatted in the viewer device's local zone.
    const cutoff=cfg.end.getTime()-(days*24*60*60*1000);
    return Math.min(cfg.end.getTime(),cutoff);
  }
  function upgradeFinishCutoffMs(cfg=activeCalcConfig()){
    return Math.max(Date.now(),finishScoreCutoffMs(cfg));
  }

  const gearScore = (levels,cfg=activeCalcConfig()) => levels.reduce((s,l) => s + Math.max(0,l-cfg.scoreFloor)*cfg.weights.gear, 0);
  const skillScore = (lvl,cfg=activeCalcConfig()) => Math.max(0,lvl-cfg.scoreFloor) * 8 * cfg.weights.skill;
  const relicScore = (lvl,cfg=activeCalcConfig()) => Math.max(0,lvl-cfg.relicFloor) * 20 * cfg.weights.relic;
  const fantoScore = (lvl,cfg=activeCalcConfig()) => Math.max(0,lvl-cfg.scoreFloor) * 4 * cfg.weights.fanto;
  const characterScore = (p,cfg=activeCalcConfig()) => Math.max(0, Math.floor((p.decimal-cfg.scoreFloor)*100 + 1e-9));

  // Skills (8), Relics (20) and deployed Fantomons (4) score per INDIVIDUAL slot.
  // The compact UI accepts an average; internally it is converted to the closest balanced
  // integer-slot distribution (e.g. Relic 13.20 = four +14 slots + sixteen +13 slots).
  function levelsFromAverage(avg,count,minLevel,maxLevel=Infinity){
    const min=Math.floor(Number(minLevel)||0);
    const max=Number.isFinite(maxLevel)?Math.floor(maxLevel):Infinity;
    const raw=Number(avg);
    const totalMin=min*count;
    const totalMax=Number.isFinite(max)?max*count:Infinity;
    const total=clamp(Math.round((Number.isFinite(raw)?raw:min)*count),totalMin,totalMax);
    const base=Math.floor(total/count),rem=total-base*count;
    const levels=Array(count).fill(base);
    // Put the partial increments first only for deterministic display; all slots are equivalent for score.
    for(let i=0;i<rem;i++) levels[i]++;
    return levels;
  }
  function averageLevels(levels){ return levels.length?levels.reduce((a,b)=>a+b,0)/levels.length:0; }
  function categoryScoreFromLevels(levels,floor,weight){ return levels.reduce((sum,l)=>sum+Math.max(0,l-floor)*weight,0); }
  function formatAverage(x,precision=3){
    const v=Number(x)||0;
    return v.toFixed(precision).replace(/\.0+$/,'').replace(/(\.\d*?)0+$/,'$1');
  }
  function formatLevelMix(levels,{plus=false}={}){
    const counts=new Map();
    levels.forEach(l=>counts.set(l,(counts.get(l)||0)+1));
    const parts=[...counts.entries()].sort((a,b)=>b[0]-a[0]).map(([lvl,count])=>{
      const tag=plus?`+${lvl}`:`Lv.${lvl}`;
      return counts.size===1?tag:`${count}×${tag}`;
    });
    return parts.join(' · ');
  }
  function parseExactLevelInput(id,count,minLevel,maxLevel){
    const raw=String($(id)?.value||'').trim();
    if(!raw) return {active:false,valid:true,levels:null};
    const levels=[];
    const tokens=raw.split(/[,;\n]+/).map(x=>x.trim()).filter(Boolean);
    for(const token of tokens){
      let m=token.match(/^(\d+)\s*[x×]\s*(\d+)$/i);
      if(m){
        const qty=parseInt(m[1],10),lvl=parseInt(m[2],10);
        for(let i=0;i<qty&&levels.length<=count;i++) levels.push(lvl);
        continue;
      }
      if(/^\d+$/.test(token)){levels.push(parseInt(token,10));continue;}
      return {active:true,valid:false,levels:null,reason:'format'};
    }
    const min=Math.floor(minLevel),max=Math.floor(maxLevel);
    if(levels.length!==count) return {active:true,valid:false,levels:null,reason:`needs ${count} slots`};
    if(levels.some(l=>!Number.isFinite(l)||l<min||l>max)) return {active:true,valid:false,levels:null,reason:`levels must be ${min}–${max}`};
    return {active:true,valid:true,levels};
  }
  function categoryStateFromAverage(avg,count,minLevel,maxLevel,floor,weight){
    const levels=levelsFromAverage(avg,count,minLevel,maxLevel);
    return {levels,avg:averageLevels(levels),score:categoryScoreFromLevels(levels,floor,weight),exact:false};
  }
  function categoryStateFromUser(avgId,exactId,count,minLevel,maxLevel,floor,weight,fallback){
    const parsed=parseExactLevelInput(exactId,count,minLevel,maxLevel);
    if(parsed.active&&parsed.valid){
      const levels=parsed.levels.slice();
      return {levels,avg:averageLevels(levels),score:categoryScoreFromLevels(levels,floor,weight),exact:true};
    }
    return categoryStateFromAverage(n(avgId,fallback),count,minLevel,maxLevel,floor,weight);
  }
  function gearStateFromUser(cfg,maxLevel,fallback){
    return categoryStateFromUser('gearLevel','exactGearLevels',5,100,maxLevel,cfg.scoreFloor,cfg.weights.gear,fallback);
  }
  function buildCategoryOptionsFromLevels(baseLevels,cap,floor,weight,stepCost,gateSpan=0){
    const levels=baseLevels.slice();
    let score=categoryScoreFromLevels(levels,floor,weight),cost=0,adds=0;
    const out=[{levels:levels.slice(),avg:averageLevels(levels),score,cost,adds}];
    const hardCap=Math.floor(cap);
    const gate=Math.max(0,Math.floor(Number(gateSpan)||0));
    let safety=0;
    while(safety++<10000){
      const minLevel=gate?Math.min(...levels):-Infinity;
      const gateCeiling=gate?(Math.floor(minLevel/gate)*gate+gate):Infinity;
      let bestIdx=-1,bestCost=Infinity,bestLevel=Infinity;
      for(let i=0;i<levels.length;i++){
        const lvl=levels[i];
        if(lvl>=hardCap) continue;
        if(gate && lvl+1>gateCeiling) continue;
        const c=Number(stepCost(lvl));
        if(!Number.isFinite(c)) continue;
        if(c<bestCost-1e-9 || (Math.abs(c-bestCost)<1e-9 && lvl<bestLevel)){
          bestIdx=i;bestCost=c;bestLevel=lvl;
        }
      }
      if(bestIdx<0) break;
      const before=levels[bestIdx];levels[bestIdx]++;cost+=bestCost;adds++;
      if(before>=floor) score+=weight;
      out.push({levels:levels.slice(),avg:averageLevels(levels),score,cost,adds});
    }
    return out;
  }
  function buildCategoryOptions(baseAvg,count,cap,minLevel,floor,weight,stepCost){
    const levels=levelsFromAverage(baseAvg,count,minLevel,cap);
    let score=categoryScoreFromLevels(levels,floor,weight),cost=0,adds=0;
    const out=[{levels:levels.slice(),avg:averageLevels(levels),score,cost,adds}];
    const hardCap=Math.floor(cap);
    let safety=0;
    while(safety++<10000){
      let bestIdx=-1,bestCost=Infinity,bestLevel=Infinity;
      for(let i=0;i<levels.length;i++){
        const lvl=levels[i];
        if(lvl>=hardCap) continue;
        const c=Number(stepCost(lvl));
        if(!Number.isFinite(c)) continue;
        if(c<bestCost-1e-9 || (Math.abs(c-bestCost)<1e-9 && lvl<bestLevel)){
          bestIdx=i;bestCost=c;bestLevel=lvl;
        }
      }
      if(bestIdx<0) break;
      const before=levels[bestIdx];
      levels[bestIdx]++;
      cost+=bestCost;adds++;
      if(before>=floor) score+=weight;
      out.push({levels:levels.slice(),avg:averageLevels(levels),score,cost,adds});
    }
    return out;
  }

  function relicCapForCharacter(characterLevel,cfg=activeCalcConfig()){
    const lvl=Math.max(1,Math.floor(Number(characterLevel)||1));
    // S2_ABOVE_CHARACTER_UPGRADES_V1: live Global evidence at Character Lv.131 includes
    // 18 Relics at +14 with enough material to push two slots to +15. Relic rank is not
    // Character-level capped; use the extracted S2 blessing table as the planning ceiling.
    if(cfg.key==='s2') return S2_EXACT_UPGRADE_RULES.relicBase + S2_EXACT_UPGRADE_RULES.relicBlessingLimit;
    return lvl<100 ? 10 : Math.max(10,Math.floor(lvl/10)+1);
  }
  function categoryCapsForCharacter(characterLevel,cfg=activeCalcConfig()){
    const lvl=Math.max(1,Math.floor(Number(characterLevel)||1));
    if(cfg.key==='s1'){
      return {
        skill:Math.max(100,lvl),
        relic:relicCapForCharacter(lvl,cfg),
        // Seasonal Fantomon progression sits one 10-level band ahead: Lv.120–129 → Fantomon 130, Lv.130–139 → Fantomon 140.
        fanto:Math.max(100,(Math.floor(lvl/10)+1)*10),
        gear:Infinity
      };
    }
    return {
      // S2_ABOVE_CHARACTER_UPGRADES_V1: Gear, Skills and Relic ranks are material-limited,
      // not Character-level limited. The extracted seasonal tables provide safe supported
      // planning ceilings; user-entered actual values remain uncapped below.
      skill:S2_EXACT_UPGRADE_RULES.floor + S2_EXACT_UPGRADE_RULES.skillBlessingLimit,
      relic:relicCapForCharacter(lvl,cfg),
      fanto:S2_EXACT_UPGRADE_RULES.floor + S2_EXACT_FANTOMON_EXP_FROM_130.length,
      gear:S2_EXACT_UPGRADE_RULES.floor + S2_EXACT_UPGRADE_RULES.gearBlessingLimit
    };
  }
  function categoryInputCapsForCharacter(characterLevel,cfg=activeCalcConfig()){
    const caps=categoryCapsForCharacter(characterLevel,cfg);
    if(cfg.key!=='s2') return caps;
    // Accept actual S2 values without Character-level clamping. The optimizer also allows new Gear/Skill/Relic
    // upgrades above Character level, bounded only by the supported seasonal cost tables; Fantomon remains conservative.
    return {...caps,skill:Infinity,relic:Infinity,fanto:Infinity,gear:Infinity};
  }

  function optimizerPlanningLevel(projectedLevel,cfg=activeCalcConfig()){
    const projected=Math.max(1,Math.floor(Number(projectedLevel)||1));
    if(cfg.key!=='s2') return projected;
    const current=Math.max(1,Math.floor(Number(characterSnapshot(cfg).level)||1));
    if(current>=S2_PLANNER_START_LEVEL && current<S2_FULL_SEASONAL_PREVIEW_LEVEL){
      return Math.max(projected,S2_FULL_SEASONAL_PREVIEW_LEVEL);
    }
    return projected;
  }
  function optimizerCategoryCaps(p,cfg=activeCalcConfig()){
    const projectedLevel=p?.upgradeCapLevel ?? p?.level ?? 1;
    return categoryCapsForCharacter(optimizerPlanningLevel(projectedLevel,cfg),cfg);
  }
  window.__sxsPlannerCapProbeV1=(characterLevel=131)=>({...categoryCapsForCharacter(characterLevel,CALC_SEASONS.s2)});
  window.__sxsResonanceGateProbeV1=()=>{
    const cfg=CALC_SEASONS.s2;
    const relicBase=[15,15,...Array(18).fill(14)];
    const relic=buildCategoryOptionsFromLevels(relicBase,18,cfg.relicFloor,cfg.weights.relic,l=>relicStepSand(l,cfg),1);
    const relicAll15=relic.findIndex(o=>Math.min(...o.levels)>=15);
    const relicFirst16=relic.findIndex(o=>Math.max(...o.levels)>=16);
    const relicLegal=relic.every(o=>Math.max(...o.levels)<=Math.min(...o.levels)+1);
    const fantoBase=[150,150,150,140];
    const fanto=buildCategoryOptionsFromLevels(fantoBase,170,cfg.scoreFloor,cfg.weights.fanto,l=>fantoStepTreatCost(l,cfg),10);
    const fantoAll150=fanto.findIndex(o=>Math.min(...o.levels)>=150);
    const fantoFirst151=fanto.findIndex(o=>Math.max(...o.levels)>=151);
    const fantoLegal=fanto.every(o=>{
      const min=Math.min(...o.levels),max=Math.max(...o.levels);
      return max<=Math.floor(min/10)*10+10;
    });
    return {relicLegal,relicAll15,relicFirst16,fantoLegal,fantoAll150,fantoFirst151};
  };

  function gearStepCost(level,cfg=activeCalcConfig()){
    const l=Math.floor(level);
    if(cfg.key==='s1') return 90*l + 310;
    // Pre-floor catch-up costs stay on the existing Global curve. The extracted S2 blessing
    // table begins at target Lv.131 (first level above the Lv.130 Season-Power floor).
    if(l<=109) return 9520 + 240*(l-100);
    if(l<=119) return 11925 + 245*(l-110);
    if(l<=129) return 14380 + 250*(l-120);
    const r=S2_EXACT_UPGRADE_RULES;
    const blessing=(l+1)-r.floor;
    if(blessing<1||blessing>r.gearBlessingLimit) return Infinity;
    const scaled=Math.min(blessing,r.gearScaleCap);
    return Math.round((r.gearBase+(scaled-1)*r.gearRate)/5)*5;
  }
  function gearStepRefined(level,cfg=activeCalcConfig()){
    const l=Math.floor(level);
    if(cfg.key==='s2' && l>=S2_EXACT_UPGRADE_RULES.floor){
      const blessing=(l+1)-S2_EXACT_UPGRADE_RULES.floor;
      return blessing>=1 && blessing<=S2_EXACT_UPGRADE_RULES.gearBlessingLimit && blessing%5===0
        ? S2_EXACT_UPGRADE_RULES.refinedOreEvery5 : 0;
    }
    // Preserve the legacy pre-floor/S1 catch-up model where the S2 extracted blessing table does not apply.
    return ((l+1)%5===0) ? l+381 : 0;
  }
  function gearRefinedCost(fromLevels,toLevels){
    let total=0;
    for(let i=0;i<5;i++) for(let l=fromLevels[i];l<toLevels[i];l++) total+=gearStepRefined(l);
    return total;
  }

  function gearCost(fromLevels,toLevels,cfg=activeCalcConfig()){
    let total=0;
    for(let i=0;i<5;i++) for(let l=fromLevels[i];l<toLevels[i];l++) total+=gearStepCost(l,cfg);
    return total;
  }
  function skillStepCost(level,cfg=activeCalcConfig()){
    const l=Math.floor(level);
    if(cfg.key==='s1') return l<=109 ? 60*l+25 : 60*l+30;
    // Keep the pre-floor catch-up curve; exact seasonal blessing costs begin above Lv.130.
    if(l===100) return 6025;
    if(l===101) return 6205;
    if(l<=109) return 6565 + 180*(l-102);
    if(l<=119) return 8025 + 200*(l-110);
    if(l<=129) return 10045 + 220*(l-120);
    const r=S2_EXACT_UPGRADE_RULES;
    const blessing=(l+1)-r.floor;
    if(blessing<1||blessing>r.skillBlessingLimit) return Infinity;
    return Math.round((r.skillBase+(blessing-1)*r.skillRate)/5)*5;
  }
  function skillCost(from,to,cfg=activeCalcConfig()){
    let each=0;
    for(let l=from;l<to;l++) each+=skillStepCost(l,cfg);
    return each*8;
  }

  function relicStepSand(level,cfg=activeCalcConfig()){
    const l=Math.floor(level);
    if(cfg.key==='s1'){
      const table={10:16000,11:17600,12:19200,13:33750};
      return table[l] ?? Infinity;
    }
    // Catch-up to +13 remains Blue/Basic-equivalent. From the S2 +13 floor onward the
    // extracted blessing table is Purple Sand: 1,350, +135 per step, converted at 25×.
    const catchup={10:16000,11:17600,12:19200};
    if(l<S2_EXACT_UPGRADE_RULES.relicBase) return catchup[l] ?? Infinity;
    const r=S2_EXACT_UPGRADE_RULES;
    const blessing=(l+1)-r.relicBase;
    if(blessing<1||blessing>r.relicBlessingLimit) return Infinity;
    return (r.relicPurpleBase+(blessing-1)*r.relicPurpleRate)*SAND_EPIC_EQ;
  }
  function relicCost(from,to,cfg=activeCalcConfig()){
    if(to<=from) return 0;
    let total=0;
    for(let l=from;l<to;l++){ const c=relicStepSand(l,cfg); if(!Number.isFinite(c)) return Infinity; total+=c; }
    return total*20;
  }
  function fantoStepTreatCost(level,cfg=activeCalcConfig()){
    const l=Math.floor(level);
    if(cfg.key==='s1'){
      if(l>=100 && l<=114) return 526 + 10*(l-100);
      if(l>=115 && l<=119) return 678 + 10*(l-115);
      if(l===120) return 730;
      if(l===121) return 740;
      if(l>=122 && l<=199) return 962 + 23*(l-122);
      return Infinity;
    }
    if(l<S2_EXACT_UPGRADE_RULES.floor){
      if(l>=100 && l<=114) return 526 + 10*(l-100);
      if(l>=115 && l<=119) return 678 + 10*(l-115);
      if(l>=120 && l<=129) return 916 + 23*(l-120);
      return Infinity;
    }
    const exp=S2_EXACT_FANTOMON_EXP_FROM_130[l-S2_EXACT_UPGRADE_RULES.floor];
    return Number.isFinite(exp)&&exp>0 ? exp/TREAT_BASIC_EXP : Infinity;
  }
  function fantoCost(from,to,cfg=activeCalcConfig()){
    if(to<=from) return 0;
    let each=0;
    for(let l=from;l<to;l++){ const c=fantoStepTreatCost(l,cfg); if(!Number.isFinite(c)) return Infinity; each+=c; }
    return each*4;
  }

  /* Read-only internal regression probe for the extracted S2 cost tables. */
  window.__sxsExactCostProbeV5=()=>{
    const cfg=CALC_SEASONS.s2;
    return {
      charLen:S2_EXACT_CHARACTER_EXP_FROM_130.length,
      fantoLen:S2_EXACT_FANTOMON_EXP_FROM_130.length,
      gear130:gearStepCost(130,cfg),gear131:gearStepCost(131,cfg),gear160:gearStepCost(160,cfg),gear188:gearStepCost(188,cfg),
      skill130:skillStepCost(130,cfg),skill140:skillStepCost(140,cfg),skill160:skillStepCost(160,cfg),skill180:skillStepCost(180,cfg),
      relic13:relicStepSand(13,cfg),relic18:relicStepSand(18,cfg),relic27:relicStepSand(27,cfg),
      fanto130:fantoStepTreatCost(130,cfg),fanto160:fantoStepTreatCost(160,cfg),
      xp130:expRequiredForLevel(130,cfg),xp210:expRequiredForLevel(210,cfg),xp281:expRequiredForLevel(281,cfg),xp287:expRequiredForLevel(287,cfg),xp288:expRequiredForLevel(288,cfg),
      refined134:gearStepRefined(134,cfg),refined139:gearStepRefined(139,cfg),refined135:gearStepRefined(135,cfg),
      preGear121:gearStepCost(121,cfg),preSkill121:skillStepCost(121,cfg)
    };
  };

  function balancedGearTarget(base, increments){
    const t = base.slice();
    for(let k=0;k<increments;k++){
      let idx=0;
      for(let i=1;i<t.length;i++) if(t[i]<t[idx]) idx=i;
      t[idx]++;
    }
    return t;
  }

  // Season-aware Realm / open-map data. S2 reaches its maximum resource bracket at Lv.120;
  // Lv.130 is a different milestone: that is the Season Power scoring floor/unlock.
  // S1 has a supported late-season Ore node value (900). Rolla remains in the data table, but the auto planner intentionally banks surplus nodes as Ore.
  // S1 open-map Ore is verified at 900 per 5 Stamina. Essence/Sand use a community-style late-S1 estimate derived from the same Ore:Realm scaling: ~1,475 Essence / ~838 Sand per 5 Stamina.
  function automaticResourceYields(characterLevel,cfg=activeCalcConfig()){
    const level=Math.max(1,Math.floor(Number(characterLevel)||1));
    const mapReady=cfg.key!=='s2' || level>=cfg.realmMaxLevel;
    const map=mapReady ? {
      ore:Number(cfg.map.ore)||0,
      essence:Number(cfg.map.essence)||0,
      sand:Number(cfg.map.sand)||0,
      rolla:Number(cfg.map.rolla)||0
    } : {ore:0,essence:0,sand:0,rolla:0};
    return {
      level,mapReady,realmMaxReady:mapReady,realmMaxLevel:cfg.realmMaxLevel,map,
      orePerHammer:cfg.realm.ore,essencePerKnuckles:cfg.realm.essence,sandPerShovel:cfg.realm.sand,rollaPerAttempt:cfg.realm.rolla,
      treatExp:50,staminaPerNode:5
    };
  }

  // Build a resource snapshot up to an arbitrary point in the active season.
  // Season-end projection calls this with cfg.end; target ETA reuses it without rerunning the optimizer.
  function futureRealmPurchaseDaysUntil(targetMs,cfg=activeCalcConfig()){
    const now=Date.now();
    const plannerCutoff=upgradeFinishCutoffMs(cfg);
    const cutoff=Math.max(now,Math.min(Number(targetMs)||plannerCutoff,plannerCutoff));
    return cutoff>now?countFuturePacificResets(now,cutoff):0;
  }
  function projectedResourcesTo(targetMs,cfg=activeCalcConfig()){
    const now=Date.now();
    const plannerCutoff=upgradeFinishCutoffMs(cfg);
    const cutoff=Math.max(now,Math.min(Number(targetMs)||plannerCutoff,plannerCutoff));
    const fullRemaining=projectionResourceHoursAt(now,cfg);
    const afterCutoffRemaining=projectionResourceHoursAt(cutoff,cfg);
    const resourceHours=Math.max(0,fullRemaining-afterCutoffRemaining);
    const wallResourceHours=Math.max(0,(cutoff-now)/3_600_000);
    const boostResets=countFuturePacificResets(now,cutoff);
    const futureDays=futureRealmPurchaseDaysUntil(cutoff,cfg);
    const staminaStart=0;
    const yields=automaticResourceYields(n('charLevel',cfg.key==='s2'?100:122),cfg);
    const staminaGenerated=Math.max(0,Math.floor(resourceHours*5));
    const staminaSpendable=staminaStart+staminaGenerated;
    const staminaNodes=Math.floor(staminaSpendable/yields.staminaPerNode);
    const staminaUnused=staminaSpendable-staminaNodes*yields.staminaPerNode;
    const cartOre=Math.max(0,n('oreRate'))*resourceHours;
    const shopEstimate=dailyShopMaterialEstimate(cfg,futureDays);
    const refinedRaw=$('refinedOreCurrent')?.value?.trim?.() ?? '';
    const refinedTracked=refinedRaw!=='';
    const refined=refinedTracked?Math.max(0,Number(refinedRaw)||0):0;
    return {
      cartHours:resourceHours,wallResourceHours,boostResets,resourceCutoffMs:cutoff,realmDays:1+futureDays,
      staminaHours:resourceHours,staminaStart,staminaGenerated,staminaSpendable,staminaNodes,staminaUnused,
      yields,cartOre,shopEstimate,
      ore:Math.max(0,n('oreCurrent'))+cartOre+shopEstimate.total.ore,
      essence:Math.max(0,n('essenceCurrent'))+Math.max(0,n('essenceRate'))*resourceHours+shopEstimate.total.essence,
      sand:savedSandEquivalent()+Math.max(0,n('sandRate'))*resourceHours+shopEstimate.total.sand,
      treat:savedTreatEquivalent()+Math.max(0,n('treatRate'))*resourceHours+shopEstimate.total.treat,
      refinedTracked,refined,
      staminaAllocation:{ore:0,essence:0,sand:0,rolla:0,unassigned:staminaNodes},
      staminaAdded:{ore:0,essence:0,sand:0,rolla:0}
    };
  }
  function projectedResources(hours,cfg=activeCalcConfig()){
    return projectedResourcesTo(upgradeFinishCutoffMs(cfg),cfg);
  }

  function applyStaminaAllocation(base,allocation,cfg=activeCalcConfig()){
    const total=Math.max(0,Math.floor(base.staminaNodes||0));
    const map=base.yields?.map||{};
    const a={ore:0,essence:0,sand:0,rolla:0,unassigned:0};
    let used=0;
    for(const key of ['ore','essence','sand','rolla']){
      const available=Number(map[key])>0;
      const requested=available?Math.max(0,Math.floor(Number(allocation?.[key])||0)):0;
      const count=Math.min(requested,Math.max(0,total-used));
      a[key]=count; used+=count;
    }
    a.unassigned=Math.max(0,total-used);
    const added={
      ore:a.ore*(Number(map.ore)||0),
      essence:a.essence*(Number(map.essence)||0),
      sand:a.sand*(Number(map.sand)||0),
      rolla:a.rolla*(Number(map.rolla)||0)
    };
    return {...base,
      ore:base.ore+added.ore,
      essence:base.essence+added.essence,
      essenceTotal:(Number(base.essenceTotal??base.essence)||0)+added.essence,
      sand:base.sand+added.sand,
      staminaAllocation:a,staminaAdded:added
    };
  }

  function staminaPlanCost(plan,key){
    if(!plan) return 0;
    return key==='ore'?plan.oreCost:key==='essence'?plan.essenceCost:key==='sand'?plan.sandCost:0;
  }
  function staminaPlanBudget(resources,key){ return Number(resources?.[key])||0; }
  function staminaRealmYield(resources,key){
    if(key==='ore') return Number(resources?.yields?.orePerHammer)||0;
    if(key==='essence') return Number(resources?.yields?.essencePerKnuckles)||0;
    if(key==='sand') return Number(resources?.yields?.sandPerShovel)||0;
    return 0;
  }

  // AUTO_STAMINA_THREE_WAY_V2: Auto intentionally recommends ONE destination.
  // Evaluate exactly the three actionable states (all Ore / all Essence / all Sand),
  // including S2 reserve-aware tool usage, instead of building O(nodes) tables that are
  // never consulted by the single-target UI.
  function allocateStaminaForPlan(plan,base,cfg=activeCalcConfig(),p=null){
    const total=Math.max(0,Math.floor(base.staminaNodes||0));
    const empty={ore:0,essence:0,sand:0,rolla:0,unassigned:0};
    if(total<=0) return empty;
    const map=base.yields?.map||{};
    if(!base.yields?.mapReady) return {...empty,unassigned:total};

    const mode=staminaMode();
    if(mode!=='auto'){
      const allocation={...empty};
      if((Number(map[mode])||0)>0) allocation[mode]=total;
      else allocation.unassigned=total;
      return allocation;
    }

    if(!plan){
      if((Number(map.ore)||0)>0) return {...empty,ore:total};
      return {...empty,unassigned:total};
    }

    const keys=['ore','essence','sand'];
    const costs={ore:staminaPlanCost(plan,'ore'),essence:staminaPlanCost(plan,'essence'),sand:staminaPlanCost(plan,'sand')};
    const yields={ore:Number(map.ore)||0,essence:Number(map.essence)||0,sand:Number(map.sand)||0};
    const finiteOr=(v,fallback)=>Number.isFinite(Number(v))?Number(v):fallback;

    const topupFor=(key,nodes)=>{
      const budget=(Number(base[key])||0)+Math.max(0,nodes)*yields[key];
      const sim={...base,[key]:budget};
      return realmTopupFor(key,costs[key],budget,sim,cfg,p);
    };

    const topupStates=Object.fromEntries(keys.map(key=>[key,{base:topupFor(key,0),full:topupFor(key,total)}]));
    const metricFor=targetKey=>{
      const allocation={...empty,[targetKey]:total};
      const tops=keys.map(key=>topupStates[key][key===targetKey?'full':'base']);
      const feasible=tops.every(x=>!!x?.feasible);
      const remainingAfterMax=tops.reduce((sum,x)=>sum+Math.max(0,finiteOr(x?.remainingAfterMax,1e15)),0);
      const realmOverflow=tops.reduce((sum,x)=>sum+Math.max(0,finiteOr(x?.packs,1e9)-finiteOr(x?.maxPacks,0)),0);
      const unknownPriceRefreshes=tops.reduce((sum,x)=>sum+Math.max(0,finiteOr(x?.unknownPriceRefreshes,0)),0);
      const dawnium=feasible?tops.reduce((sum,x)=>sum+finiteOr(x?.dawnium,1e15),0):Infinity;
      const realmPacks=tops.reduce((sum,x)=>sum+finiteOr(x?.packs,1e9),0);
      const bankedToolsUsed=tops.reduce((sum,x)=>sum+Math.max(0,finiteOr(x?.bankedUsed,0)),0);
      const rawShortfall=tops.reduce((sum,x)=>sum+Math.max(0,finiteOr(x?.planShortfall,x?.shortfall||0)),0);
      return {allocation,feasible,remainingAfterMax,realmOverflow,unknownPriceRefreshes,dawnium,realmPacks,bankedToolsUsed,rawShortfall};
    };

    const better=(c,b)=>{
      if(!b) return true;
      if(c.feasible!==b.feasible) return c.feasible;
      if(c.feasible){
        if(c.unknownPriceRefreshes<b.unknownPriceRefreshes) return true;
        if(c.unknownPriceRefreshes>b.unknownPriceRefreshes) return false;
        if(c.dawnium<b.dawnium-1e-9) return true;
        if(c.dawnium>b.dawnium+1e-9) return false;
        if(c.realmPacks<b.realmPacks) return true;
        if(c.realmPacks>b.realmPacks) return false;
      }else{
        if(c.remainingAfterMax<b.remainingAfterMax-0.5) return true;
        if(c.remainingAfterMax>b.remainingAfterMax+0.5) return false;
        if(c.realmOverflow<b.realmOverflow) return true;
        if(c.realmOverflow>b.realmOverflow) return false;
        if(c.rawShortfall<b.rawShortfall-0.5) return true;
        if(c.rawShortfall>b.rawShortfall+0.5) return false;
      }
      if(c.bankedToolsUsed<b.bankedToolsUsed) return true;
      if(c.bankedToolsUsed>b.bankedToolsUsed) return false;
      // Stable tie-break: bank surplus Stamina as Ore, then Essence, then Sand.
      if(c.allocation.ore>b.allocation.ore) return true;
      if(c.allocation.ore<b.allocation.ore) return false;
      if(c.allocation.essence>b.allocation.essence) return true;
      return false;
    };

    let best=null;
    for(const key of keys){
      if((Number(map[key])||0)<=0) continue;
      const candidate=metricFor(key);
      if(better(candidate,best)) best=candidate;
    }
    return best?.allocation||{...empty,ore:(Number(map.ore)||0)>0?total:0,unassigned:(Number(map.ore)||0)>0?0:total};
  }

  function staminaAllocationSignature(a){ return ['ore','essence','sand','rolla','unassigned'].map(k=>Math.floor(a?.[k]||0)).join('/'); }


  /* TARGET_REACH_ETA_V1
     Estimate WHEN the already-selected goal route becomes executable. This deliberately does
     not rerun the expensive optimizer at every timestamp. Instead it binary-searches time using
     the recommended route's exact costs, current Character growth, Cart/shop production,
     Stamina, owned/planned Realm tools, and remaining Realm purchase capacity. */
  function targetMomentLabel(ms){
    return new Intl.DateTimeFormat(undefined,{month:'short',day:'numeric',hour:'numeric',minute:'2-digit'}).format(new Date(ms)).replace(' at ',' · ');
  }
  function compactDurationMs(ms){
    const mins=Math.max(0,Math.floor((Number(ms)||0)/60_000));
    const d=Math.floor(mins/1440),h=Math.floor((mins%1440)/60),m=mins%60;
    return d>0?`${d}d ${h}h`:h>0?`${h}h ${m}m`:`${m}m`;
  }
  function realmTopupForMoment(key,cost,resources,targetMs,pAt,cfg=activeCalcConfig()){
    const ids={ore:'hammerCurrent',essence:'knucklesCurrent',sand:'shovelCurrent'};
    const futureDays=futureRealmPurchaseDaysUntil(targetMs,cfg);
    const baseline=realmDailyValue(key);
    const manual=Math.max(0,Math.floor(n(ids[key],0)));
    const planned=futureDays*baseline*REALM_RUNS_PER_REFRESH;
    let perRun=realmYieldFor(resources,key);
    if(cfg.key==='s2' && Math.floor((pAt?.decimal??pAt?.level??n('charLevel',100)))<cfg.realmMaxLevel) perRun=0;
    return realmTopup(Math.max(0,Number(cost)||0),Math.max(0,Number(resources?.[key])||0),perRun,1+futureDays,manual+planned,baseline);
  }
  function fixedTargetRouteFundableAt(plan,requestedDesired,targetMs,pEnd,cfg=activeCalcConfig()){
    if(!plan) return false;
    const pAt=projectCharacterTo(targetMs,cfg);
    const nonCharacterScore=Math.max(0,(Number(plan.score)||0)-characterScore(pEnd,cfg));
    if(nonCharacterScore+characterScore(pAt,cfg)<requestedDesired-1e-9) return false;

    if(cfg.key==='s1'){
      const caps=categoryCapsForCharacter(pAt.level,cfg);
      if((plan.skillLevels||[]).some(x=>x>caps.skill)) return false;
      if((plan.relicLevels||[]).some(x=>x>caps.relic)) return false;
      if((plan.fantoLevels||[]).some(x=>x>caps.fanto)) return false;
    }

    const base=projectedResourcesTo(targetMs,cfg);
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
      const ore=realmTopupForMoment('ore',plan.oreCost,resources,targetMs,pAt,cfg);
      const essence=realmTopupForMoment('essence',plan.essenceCost,resources,targetMs,pAt,cfg);
      const sand=realmTopupForMoment('sand',plan.sandCost,resources,targetMs,pAt,cfg);
      if(ore.feasible&&essence.feasible&&sand.feasible) return true;
    }
    return false;
  }
  function estimateTargetReachMoment(plan,resourceBlocked,requestedDesired,pEnd,cfg=activeCalcConfig()){
    if(!plan||resourceBlocked) return null;
    const now=Date.now(),end=cfg.end.getTime();
    if(end<=now) return null;
    if(fixedTargetRouteFundableAt(plan,requestedDesired,now,pEnd,cfg)) return now;
    if(!fixedTargetRouteFundableAt(plan,requestedDesired,end,pEnd,cfg)) return null;
    let lo=now,hi=end;
    for(let i=0;i<18 && hi-lo>60_000;i++){
      const mid=Math.floor((lo+hi)/2);
      if(fixedTargetRouteFundableAt(plan,requestedDesired,mid,pEnd,cfg)) hi=mid;
      else lo=mid+1;
    }
    return hi;
  }
  function renderTargetTiming(plan,resourceBlocked,requestedDesired,pEnd,cfg=activeCalcConfig()){
    const host=$('targetTiming'),dateEl=$('targetReachedDate'),leftEl=$('targetSeasonLeft');
    if(!host||!dateEl||!leftEl) return;
    const reached=estimateTargetReachMoment(plan,resourceBlocked,requestedDesired,pEnd,cfg);
    host.classList.toggle('isUnreachable',!Number.isFinite(reached));
    if(!Number.isFinite(reached)){
      dateEl.textContent='Not projected';
      leftEl.textContent='—';
      return;
    }
    const now=Date.now();
    dateEl.textContent=reached<=now+60_000?'Now':targetMomentLabel(reached);
    leftEl.textContent=compactDurationMs(Math.max(0,cfg.end.getTime()-reached));
  }

  function renderStaminaCurrentPlan(allocation,added,resources){
    const el=$('staminaCurrentPlan');
    if(!el) return;
    const a=allocation||{ore:0,essence:0,sand:0,rolla:0,unassigned:0};
    const gain=added||{ore:0,essence:0,sand:0,rolla:0};
    const labels={ore:'Ore',essence:'Essence',sand:'Sand',rolla:'Rolla'};
    const active=['ore','essence','sand','rolla'].filter(k=>(Number(a[k])||0)>0);
    const mode=staminaMode();
    if(!resources?.yields?.mapReady){
      const bracket=activeCalcConfig().realmMaxLevel;
      el.innerHTML=`Current plan: waiting for the Lv.${bracket} map bracket`;
      return;
    }
    if(!active.length){
      const unassigned=Math.max(0,Math.floor(Number(a.unassigned)||0));
      el.textContent=unassigned?`Current plan: ${fmt(unassigned)} node${unassigned===1?'':'s'} unassigned`:'Current plan: no projected Stamina nodes';
      return;
    }
    const prefix=mode==='auto'?'Auto allocation:':'Current allocation:';
    const allocText=active.map(k=>`${labels[k]} ${fmt(Math.floor(Number(a[k])||0))}`).join(' · ');
    const gainText=active.map(k=>`+${fmtCompact(Number(gain[k])||0)} ${labels[k]}`).join(' · ');
    el.innerHTML=`${prefix} ${allocText}<span class="staminaGain"><br>Projected gain: ${gainText}</span>`;
  }

  /* AUTO_STAMINA_EXACT_THREE_V1
     Auto Stamina has exactly three legal strategies: all Ore, all Essence, or all Sand.
     Solve each legal resource state directly and compare the globally optimal score plan
     from each state. This is both more exact and cheaper than the old alternating solver,
     which could run the full optimizer up to six times while chasing a fixed point.

     If safe raw inventory already funds every reachable Ore/Essence/Sand upgrade through
     the projected cap, Stamina cannot change feasibility or marginal scarcity. In that
     common surplus case solve once and bank the otherwise-unused nodes as Ore. */
  function solveTargetWithAutoStamina(baseScore,desired,p,baseResources,cfg=activeCalcConfig()){
    const ctx=createPlanningContext(baseScore,desired,p,cfg);

    // Below the verified S2 Lv.120 map bracket, keep Stamina out of the numeric budget rather than guessing yields.
    if(!baseResources.yields?.mapReady){
      const allocation={ore:0,essence:0,sand:0,rolla:0,unassigned:baseResources.staminaNodes||0};
      const resources=applyStaminaAllocation(baseResources,allocation,cfg);
      const result=searchPlans(baseScore,desired,p,resources,cfg,ctx);
      return {plan:result.plan,diagnostic:result.plan||result.diagnostic,resources,allocation};
    }

    // Manual Stamina destinations do not depend on a score plan; apply them once and solve normally.
    if(staminaMode()!=='auto'){
      const allocation=allocateStaminaForPlan(null,baseResources,cfg,p);
      const resources=applyStaminaAllocation(baseResources,allocation,cfg);
      const result=searchPlans(baseScore,desired,p,resources,cfg,ctx);
      return {plan:result.plan,diagnostic:result.plan||result.diagnostic,resources,allocation};
    }

    const total=Math.max(0,Math.floor(baseResources.staminaNodes||0));
    const map=baseResources.yields?.map||{};
    const empty={ore:0,essence:0,sand:0,rolla:0,unassigned:0};
    const resultState=(allocation)=>{
      const resources=applyStaminaAllocation(baseResources,allocation,cfg);
      const result=searchPlans(baseScore,desired,p,resources,cfg,ctx);
      return {plan:result.plan,diagnostic:result.plan||result.diagnostic,resources,allocation,result};
    };
    const betterState=(state,best)=>{
      if(!best) return true;
      const cp=state.result.plan,bp=best.result.plan;
      if(!!cp!==!!bp) return !!cp;
      if(cp&&bp){
        if(betterFeasibleCandidate(cp,bp)) return true;
        if(betterFeasibleCandidate(bp,cp)) return false;
        return false;
      }
      const cd=state.result.diagnostic,bd=best.result.diagnostic;
      if(cd&&bd){
        if(betterDiagnosticCandidate(cd,bd)) return true;
        if(betterDiagnosticCandidate(bd,cd)) return false;
      }
      return !!cd&&!bd;
    };

    // Surplus fast path: every reachable raw-material category is already fully funded.
    // Extra Stamina cannot alter candidate feasibility or the marginal scarcity weights.
    const maxGearOre=Math.max(0,Number(ctx.gearOptions?.[ctx.gearOptions.length-1]?.oreCost)||0);
    const fullyRawFunded=
      (Number(baseResources.ore)||0)>=maxGearOre-0.5 &&
      (Number(baseResources.essence)||0)>=Math.max(0,Number(ctx.headroomCosts?.essence)||0)-0.5 &&
      (Number(baseResources.sand)||0)>=Math.max(0,Number(ctx.headroomCosts?.sand)||0)-0.5;
    if(fullyRawFunded){
      const allocation=(Number(map.ore)||0)>0?{...empty,ore:total}:{...empty,unassigned:total};
      const state=resultState(allocation);
      return {plan:state.result.plan,diagnostic:state.result.plan||state.result.diagnostic,resources:state.resources,allocation:state.allocation};
    }

    // Evaluate the complete legal Auto-Stamina state space directly: at most three searches.
    let bestState=null;
    for(const key of ['ore','essence','sand']){
      if((Number(map[key])||0)<=0) continue;
      const state=resultState({...empty,[key]:total});
      if(betterState(state,bestState)) bestState=state;
    }
    if(bestState){
      return {plan:bestState.result.plan,diagnostic:bestState.result.plan||bestState.result.diagnostic,resources:bestState.resources,allocation:bestState.allocation};
    }

    const allocation={...empty,unassigned:total};
    const state=resultState(allocation);
    return {plan:state.result.plan,diagnostic:state.result.plan||state.result.diagnostic,resources:state.resources,allocation};
  }

  // REALM_20_REFRESH_TOOL_COUNT_V1
  // One refresh grants 5 Realm tools/entries. The first 10 Dawnium prices are known;
  // refreshes 11–20 remain usable capacity but their Dawnium prices are intentionally unknown.
  const MATERIAL_REALM_BUY_COSTS = [60,60,100,100,150,150,200,200,250,300];
  const MAX_REALM_REFRESHES_PER_DAY=20;
  const REALM_RUNS_PER_REFRESH=5;
  const REALM_CHOICE_CACHE=new Map();
  function realmPurchaseChoices(days,baselinePerDay){
    const d=Math.max(0,Math.floor(days||0)),baseline=clamp(Math.floor(baselinePerDay||0),0,MAX_REALM_REFRESHES_PER_DAY);
    const key=`${d}|${baseline}`;
    if(REALM_CHOICE_CACHE.has(key)) return REALM_CHOICE_CACHE.get(key);
    const choices=[];
    for(let day=1;day<d;day++){
      for(let idx=baseline;idx<MAX_REALM_REFRESHES_PER_DAY;idx++){
        const known=idx<MATERIAL_REALM_BUY_COSTS.length;
        const knownCost=known?MATERIAL_REALM_BUY_COSTS[idx]:0;
        choices.push({knownCost,known,day,idx});
      }
    }
    // Never compare an invented price. Exhaust known-price opportunities first, then
    // minimize how deep into the unknown 11–20 band a route must go.
    choices.sort((a,b)=>{
      if(a.known!==b.known) return a.known?-1:1;
      if(a.known && a.knownCost!==b.knownCost) return a.knownCost-b.knownCost;
      if(!a.known && a.idx!==b.idx) return a.idx-b.idx;
      return a.day-b.day||a.idx-b.idx;
    });
    const knownPrefix=[0],unknownPrefix=[0];
    for(const x of choices){
      knownPrefix.push(knownPrefix[knownPrefix.length-1]+x.knownCost);
      unknownPrefix.push(unknownPrefix[unknownPrefix.length-1]+(x.known?0:1));
    }
    // prefix is retained for realmTopup compatibility, but now means VERIFIED Dawnium only.
    const out={choices,prefix:knownPrefix,knownPrefix,unknownPrefix}; REALM_CHOICE_CACHE.set(key,out); return out;
  }

  function materialRealmDaysAvailable(cfg=activeCalcConfig()){
    if(upgradeFinishCutoffMs(cfg)<=Date.now()) return 0;
    // Current server-day window + each future 6 AM reset strictly before the planner cutoff.
    return 1+futureRealmPurchaseDays(cfg);
  }
  function realmInventoryFor(key,cfg=activeCalcConfig()){
    const ids={ore:'hammerCurrent',essence:'knucklesCurrent',sand:'shovelCurrent'};
    const id=ids[key];
    const manualBanked=id?Math.max(0,Math.floor(n(id,0))):0;
    const plannedRuns=plannedRealmRunsFor(key,cfg);
    return {banked:Math.max(0,manualBanked+plannedRuns),manualBanked,plannedRuns,protectedRuns:0,baselineRefreshes:realmDailyValue(key)};
  }
  function realmYieldFor(resources,key){
    if(key==='ore') return Number(resources?.yields?.orePerHammer)||0;
    if(key==='essence') return Number(resources?.yields?.essencePerKnuckles)||0;
    if(key==='sand') return Number(resources?.yields?.sandPerShovel)||0;
    return 0;
  }

  // A paid Material Realm refresh is a PACK of five actual Realm runs/tools.
  // Banked tools are consumed first; Dawnium is charged only for newly purchased refresh packs.
  function realmTopup(resourceCost,projectedBudget,yieldPerRun,days,bankedRuns=0,baselinePerDay=0){
    const shortfall=Math.max(0,resourceCost-projectedBudget);
    const perRun=Math.max(0,Number(yieldPerRun)||0);
    const d=Math.max(0,Math.floor(days||0));
    const banked=Math.max(0,Math.floor(bankedRuns||0));
    const baseline=clamp(Math.floor(baselinePerDay||0),0,MAX_REALM_REFRESHES_PER_DAY);
    const futureDays=Math.max(0,d-1);
    const maxPacks=futureDays*Math.max(0,MAX_REALM_REFRESHES_PER_DAY-baseline);
    const maxPurchasedRuns=maxPacks*REALM_RUNS_PER_REFRESH;
    const maxRuns=banked+maxPurchasedRuns;
    const futureDayKnownCost=MATERIAL_REALM_BUY_COSTS.slice(Math.min(baseline,MATERIAL_REALM_BUY_COSTS.length)).reduce((a,b)=>a+b,0);
    const maxDawnium=futureDays*futureDayKnownCost;
    const maxUnknownPriceRefreshes=futureDays*Math.max(0,MAX_REALM_REFRESHES_PER_DAY-Math.max(baseline,MATERIAL_REALM_BUY_COSTS.length));
    if(shortfall<=0.5) return {feasible:true,shortfall:0,runsNeeded:0,runsUsed:0,bankedUsed:0,bankedRemaining:banked,packs:0,attempts:0,purchasedRuns:0,paidRunsUsed:0,sparePurchasedRuns:0,dawnium:0,days:d,dailyCounts:Array(d).fill(0),provided:0,maxPacks,maxAttempts:maxPacks,maxRuns,maxProvided:maxRuns*perRun,remainingAfterMax:0,maxDawnium,maxUnknownPriceRefreshes,baselinePerDay:baseline};
    if(perRun<=0) return {feasible:false,unsupported:true,shortfall,runsNeeded:Infinity,bankedUsed:0,bankedRemaining:banked,packs:Infinity,attempts:Infinity,purchasedRuns:0,sparePurchasedRuns:0,dawnium:Infinity,days:d,dailyCounts:Array(d).fill(0),provided:0,maxPacks:0,maxAttempts:0,maxRuns:banked,maxProvided:0,remainingAfterMax:shortfall,maxDawnium:0,maxUnknownPriceRefreshes:0,baselinePerDay:baseline};

    const runsNeeded=Math.ceil(shortfall/perRun);
    const bankedUsed=Math.min(banked,runsNeeded);
    const paidRunsNeeded=Math.max(0,runsNeeded-bankedUsed);
    const packs=Math.ceil(paidRunsNeeded/REALM_RUNS_PER_REFRESH);
    const maxProvided=maxRuns*perRun;
    const remainingAfterMax=Math.max(0,shortfall-maxProvided);
    if(packs>maxPacks){
      return {feasible:false,shortfall,runsNeeded,bankedUsed,packs,attempts:packs,purchasedRuns:maxPurchasedRuns,dawnium:Infinity,days:d,dailyCounts:Array(d).fill(0),provided:maxProvided,maxPacks,maxAttempts:maxPacks,maxRuns,maxProvided,remainingAfterMax,maxDawnium,maxUnknownPriceRefreshes,baselinePerDay:baseline};
    }

    // Pick the cheapest remaining marginal refreshes across all server-day windows.
    // The marginal-price list is cached because the optimizer evaluates hundreds of candidate Gear totals.
    const purchaseTable=realmPurchaseChoices(d,baseline);
    const picked=purchaseTable.choices.slice(0,packs);
    const dailyCounts=Array(d).fill(0);
    const dawnium=purchaseTable.prefix[packs]??Infinity;
    const knownDawnium=purchaseTable.knownPrefix?.[packs]??0;
    const unknownPriceRefreshes=purchaseTable.unknownPrefix?.[packs]??0;
    for(const x of picked) dailyCounts[x.day]++;
    const purchasedRuns=packs*REALM_RUNS_PER_REFRESH;
    const paidRunsUsed=Math.max(0,runsNeeded-bankedUsed);
    const sparePurchasedRuns=Math.max(0,purchasedRuns-paidRunsUsed);
    const bankedRemaining=Math.max(0,banked-bankedUsed);
    // Only the runs actually needed for this target are converted into current-season resources.
    // Spare entries from the final 5-run refresh can remain banked for the next season.
    const runsUsed=runsNeeded;
    const provided=runsUsed*perRun;
    return {feasible:true,shortfall,runsNeeded,runsUsed,bankedUsed,bankedRemaining,packs,attempts:packs,purchasedRuns,paidRunsUsed,sparePurchasedRuns,dawnium,knownDawnium,unknownPriceRefreshes,days:d,dailyCounts,provided,maxPacks,maxAttempts:maxPacks,maxRuns,maxProvided,remainingAfterMax:0,maxDawnium,maxUnknownPriceRefreshes,baselinePerDay:baseline};
  }

  function realmTopupFor(key,resourceCost,projectedBudget,resources,cfg=activeCalcConfig(),p=null){
    const inv=realmInventoryFor(key,cfg);
    let perRun=realmYieldFor(resources,key);
    // S2 tools can be bought/banked before Lv.120 and spent once the max bracket is reached.
    // If the projection never reaches Lv.120, do not invent a lower-bracket yield.
    if(cfg.key==='s2' && Math.floor((p?.decimal??p?.level??n('charLevel',100)))<cfg.realmMaxLevel) perRun=0;
    return realmTopup(resourceCost,projectedBudget,perRun,Number.isFinite(resources?.realmDays)?resources.realmDays:materialRealmDaysAvailable(cfg),inv.banked,inv.baselineRefreshes);
  }

  function formatRealmSchedule(topup,label){
    if(!topup || !Number.isFinite(topup.packs) || topup.packs<=0){
      return topup?.bankedUsed?`${label}: use ${fmt(topup.bankedUsed)} banked runs/tools`:'';
    }
    const parts=[];
    if(topup.bankedUsed) parts.push(`use ${fmt(topup.bankedUsed)} banked`);
    const counts=topup.dailyCounts||[];
    const summary=new Map();
    counts.forEach(c=>{if(c>0) summary.set(c,(summary.get(c)||0)+1);});
    const sched=[...summary.entries()].sort((a,b)=>a[0]-b[0]).map(([count,days])=>`${count} refresh${count===1?'':'es'} on ${days} day${days===1?'':'s'}`).join(', ');
    parts.push(`${fmt(topup.packs)} paid refresh${topup.packs===1?'':'es'} = ${fmt(topup.purchasedRuns)} entries${sched?` (${sched})`:''}`);
    if(topup.sparePurchasedRuns) parts.push(`${fmt(topup.sparePurchasedRuns)} spare entr${topup.sparePurchasedRuns===1?'y':'ies'} can stay banked`);
    return `${label}: ${parts.join(' + ')}`;
  }

  function realmDailyRoute(topup){
    if(!topup || !Number.isFinite(topup.packs) || topup.packs<=0) return '';
    const counts=(topup.dailyCounts||[]).map(x=>Math.max(0,Math.floor(Number(x)||0)));
    let last=counts.length-1;
    while(last>=0&&counts[last]===0) last--;
    if(last<0) return '';
    return counts.slice(0,last+1).join('/');
  }
  function realmToolPurchaseText(topup,label){
    if(!topup) return '';
    const purchased=Number.isFinite(topup.purchasedRuns)?Math.max(0,Math.floor(topup.purchasedRuns)):0;
    const banked=Number.isFinite(topup.bankedUsed)?Math.max(0,Math.floor(topup.bankedUsed)):0;
    if(purchased>0) return `${fmt(purchased)} ${label}${banked?` + ${fmt(banked)} banked`:''}`;
    if(banked>0) return `${fmt(banked)} banked ${label}`;
    return '';
  }


  function buildGearOptions(baseGear,cfg,scoreTarget=0,hardCap=cfg.gearCap){
    const out=[{adds:0,target:baseGear.slice(),score:gearScore(baseGear,cfg),oreCost:0,refinedCost:0}];
    if(gearLocked) return out;
    const t=baseGear.slice();
    let oreCost=0,refinedCost=0,adds=0;
    const effectiveCap=Number.isFinite(hardCap)?Math.floor(hardCap):Infinity;
    const scoreGap=Math.max(0,(Number(scoreTarget)||0)-gearScore(baseGear,cfg));
    const targetLimited=Math.min(2500,Math.max(40,Math.ceil(scoreGap/Math.max(1,cfg.weights.gear))+80));
    const maxAdds=Number.isFinite(effectiveCap)
      ? t.reduce((sum,l)=>sum+Math.max(0,effectiveCap-l),0)
      : targetLimited;
    for(let k=0;k<maxAdds;k++){
      let idx=0;
      for(let i=1;i<t.length;i++) if(t[i]<t[idx]) idx=i;
      if(Number.isFinite(effectiveCap) && t[idx]>=effectiveCap) break;
      oreCost+=gearStepCost(t[idx],cfg);
      refinedCost+=gearStepRefined(t[idx]);
      t[idx]++; adds++;
      out.push({adds,target:t.slice(),score:gearScore(t,cfg),oreCost,refinedCost});
    }
    return out;
  }
  function firstGearOptionAtLeast(options,scoreNeeded){
    let lo=0,hi=options.length-1,ans=null;
    while(lo<=hi){
      const mid=(lo+hi)>>1;
      if(options[mid].score>=scoreNeeded){ans=options[mid];hi=mid-1;} else lo=mid+1;
    }
    return ans;
  }

  function planningCategoryState(cfg,currentCaps,projectedCaps){
    const skill=categoryStateFromUser('skillLevel','exactSkillLevels',8,100,currentCaps.skill,cfg.scoreFloor,cfg.weights.skill,cfg.key==='s2'?100:122);
    const relic=categoryStateFromUser('relicLevel','exactRelicLevels',20,10,currentCaps.relic,cfg.relicFloor,cfg.weights.relic,cfg.key==='s2'?10:13);
    const fanto=categoryStateFromUser('fantomonLevel','exactFantoLevels',4,100,currentCaps.fanto,cfg.scoreFloor,cfg.weights.fanto,cfg.key==='s2'?100:130);
    return {
      skill,relic,fanto,
      skillOptions:buildCategoryOptionsFromLevels(skill.levels,Math.max(Math.ceil(skill.avg),projectedCaps.skill),cfg.scoreFloor,cfg.weights.skill,l=>skillStepCost(l,cfg)),
      relicOptions:cfg.optimizeRelic?buildCategoryOptionsFromLevels(relic.levels,Math.max(Math.ceil(relic.avg),projectedCaps.relic),cfg.relicFloor,cfg.weights.relic,l=>relicStepSand(l,cfg),1):[{...relic,cost:0,adds:0}],
      fantoOptions:cfg.optimizeFanto?buildCategoryOptionsFromLevels(fanto.levels,Math.max(Math.ceil(fanto.avg),projectedCaps.fanto),cfg.scoreFloor,cfg.weights.fanto,l=>fantoStepTreatCost(l,cfg),10):[{...fanto,cost:0,adds:0}]
    };
  }

  // Structural upgrade options do not depend on the projected resource mix. Build them once
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

  /* SCARCITY_ADJUSTED_ACQUISITION_V1 · POST_PLAN_SCARCITY_V4 · TOTAL_POOL_SMART_BALANCE_V1
     Smart Balance now treats each owned/projected progression family as ONE economic pool:
       Ore = projected raw Ore + saved/already-planned Hammers at full material value;
       Essence = projected raw Essence + saved/already-planned Knuckles at full material value;
       Sand = projected raw Sand + saved/already-planned Shovels at full material value.
     This pool decides which category mix is healthiest. Actual funding still spends raw material
     first inside each family and consumes tools only for the remaining shortfall. Tool preservation
     is a tie-breaker, not a hard preference. Extra Realm purchases are NOT included in starting
     abundance and remain the last-resort sourcing tier. */
  // TREAT_MARGINAL_SCARCITY_V1: Treats use the same marginal depletion curve as the
  // other score-material families; their only economic difference is no Realm-tool supply.
  const SURPLUS_ACQUISITION_FLOORS={ore:0.25,essence:0.25,sand:0.25,treat:0.25};
  const TOOL_SCARCITY_CREDIT=1.00;
  // MARGINAL_INTEGRATED_SCARCITY_V5: these shape the price of the NEXT unit consumed.
  // The optimizer integrates this curve over the candidate spend instead of applying the
  // final depletion multiplier retroactively to the entire spend.
  const POST_PLAN_SCARCITY_MAX=3.50;
  const POST_PLAN_SCARCITY_EXPONENT=2.40;

  /* OPTIMIZER_AUDIT_V3 · TOOLS_FIRST_S2_RESERVES_V1
     Enabled S2 Essence/Sand reserves hold carried/planned Realm tools first. Raw material
     is reserved only for the portion those tools cannot cover. If a reserve is disabled,
     raw remains the first current-season spend source and Realm tools stay untouched until
     the raw material is genuinely exhausted. */
  function rawOnlyAcquisitionSupply(key,resources,cfg=activeCalcConfig()){
    return Math.max(0,Number(resources?.[key])||0);
  }
  function plannedToolAcquisitionSupply(key,resources,cfg=activeCalcConfig()){
    if(key==='treat') return rawOnlyAcquisitionSupply(key,resources,cfg);
    const inv=realmInventoryFor(key,cfg);
    const perRun=Math.max(0,realmYieldFor(resources,key));
    const bankedMaterial=Math.max(0,Number(inv?.banked)||0)*perRun;
    // Saved + already-configured future tools are real owned/projected capacity, so they
    // enter scarcity at full material equivalent. Candidate-invented extra purchases are
    // intentionally absent from realmInventoryFor() and therefore cannot inflate this pool.
    return rawOnlyAcquisitionSupply(key,resources,cfg)+bankedMaterial*TOOL_SCARCITY_CREDIT;
  }

  /* POST_PLAN_SCARCITY_V4 · TOTAL_POOL_SMART_BALANCE_V1 · MARGINAL_INTEGRATED_SCARCITY_V5
     Rank plans by the reserve they leave in the TOTAL owned/projected resource family.
     Raw and saved/already-planned tools are economically interchangeable for scarcity, while
     realmTopupFor() still enforces the physical spend order: raw first, then banked/planned tools.
     Extra candidate purchases never add starting supply, so a paid route cannot make itself look
     abundant by counting tools it has not bought yet.

     V5 prices Ore / Essence / Sand / Treats MARGINALLY as each pool is consumed. The scarcity
     multiplier for the next unit is floor + (max-floor) * consumedFraction^exponent, and candidate
     cost is the analytic integral of that curve from the pre-plan state through the candidate spend.
     Therefore early surplus units stay cheap and only later units become strongly scarce; the last
     unit no longer retroactively reprices every earlier unit. Any spend beyond the projected
     owned/planned pool is priced at the maximum scarcity multiplier. Treats use projected raw/
     acquired Treat-equivalent supply only; unlike Ore/Essence/Sand they have no Realm-tool credit. */
  function marginalWeightedSpend(amount,key,resources){
    const amountTotal=Math.max(0,Number(amount)||0);
    if(amountTotal<=0) return 0;

    const floor=Math.max(0,Math.min(1,Number(SURPLUS_ACQUISITION_FLOORS[key])||0));
    const usefulNeed=Math.max(0,Number(resources?.acquisitionHeadroomCosts?.[key])||0);
    const available=Math.max(0,Number(resources?.acquisitionSupplyEquiv?.[key])||0);
    if(usefulNeed<=0) return amountTotal*floor;

    const productive=Math.min(amountTotal,usefulNeed);

    // TREAT_MARGINAL_SCARCITY_V1: all four score-material families now use this same
    // integrated depletion curve. Treats differ only in acquisitionSupplyEquiv construction:
    // they have no Hammer/Knuckle/Shovel-style Realm-tool capacity added to their pool.
    let effective=0;
    if(available<=1e-9){
      effective=productive*POST_PLAN_SCARCITY_MAX;
    }else{
      const withinPool=Math.min(productive,available);
      const fraction=Math.max(0,Math.min(1,withinPool/available));
      const power=POST_PLAN_SCARCITY_EXPONENT+1;
      // Integral from x=0 to x=fraction of:
      //   floor + (max-floor) * x^exponent
      // multiplied by the pool size to return material-equivalent weighted cost.
      effective=
        floor*withinPool+
        (POST_PLAN_SCARCITY_MAX-floor)*available/power*Math.pow(fraction,power);

      if(productive>available){
        effective+=(productive-available)*POST_PLAN_SCARCITY_MAX;
      }
    }

    // Progression beyond productive headroom is never treated as cheap surplus.
    if(amountTotal>productive) effective+=(amountTotal-productive)*POST_PLAN_SCARCITY_MAX;
    return effective;
  }

  function marginalWeightedCosts(costs,resources,cfg=activeCalcConfig()){
    return {
      ore:marginalWeightedSpend(costs?.ore,'ore',resources),
      essence:marginalWeightedSpend(costs?.essence,'essence',resources),
      sand:marginalWeightedSpend(costs?.sand,'sand',resources),
      treat:marginalWeightedSpend(costs?.treat,'treat',resources)
    };
  }

  function jointReacquisitionHours(costs,resources,cfg=activeCalcConfig()){
    const map=resources?.yields?.map||cfg.map||{};
    const enteredTreatRate=Math.max(0,n('treatRate'));
    const cart={
      ore:Math.max(0,n('oreRate')),
      essence:Math.max(0,n('essenceRate')),
      sand:Math.max(0,n('sandRate')),
      treat:enteredTreatRate
    };
    const nodeYield={
      ore:Math.max(0,Number(map.ore)||0),
      essence:Math.max(0,Number(map.essence)||0),
      sand:Math.max(0,Number(map.sand)||0)
    };
    const demand={
      ore:Math.max(0,Number(costs?.ore)||0),
      essence:Math.max(0,Number(costs?.essence)||0),
      sand:Math.max(0,Number(costs?.sand)||0),
      treat:Math.max(0,Number(costs?.treat)||0)
    };

    let floor=0;
    if(demand.treat>0){
      if(cart.treat<=0) return 1e9;
      floor=Math.max(floor,demand.treat/cart.treat);
    }
    const keys=['ore','essence','sand'];
    for(const key of keys){
      if(demand[key]<=0) continue;
      if(nodeYield[key]<=0){
        if(cart[key]<=0) return 1e9;
        floor=Math.max(floor,demand[key]/cart[key]);
      }
    }

    const nodesNeededAt=hours=>{
      let total=0;
      for(const key of keys){
        const remaining=Math.max(0,demand[key]-cart[key]*hours);
        if(remaining<=0) continue;
        if(nodeYield[key]<=0) return Infinity;
        total+=remaining/nodeYield[key];
      }
      return total;
    };
    if(nodesNeededAt(floor)<=floor+1e-9) return floor;

    let active=keys.filter(key=>demand[key]>cart[key]*floor+1e-9 && nodeYield[key]>0);
    let hours=floor;
    for(let pass=0;pass<4;pass++){
      let numerator=0,denominator=1;
      for(const key of active){
        numerator+=demand[key]/nodeYield[key];
        denominator+=cart[key]/nodeYield[key];
      }
      hours=Math.max(floor,numerator/denominator);
      const next=active.filter(key=>demand[key]>cart[key]*hours+1e-9);
      if(next.length===active.length){
        if(nodesNeededAt(hours)<=hours+1e-7) return hours;
        break;
      }
      active=next;
      if(!active.length) return floor;
    }

    let lo=floor,hi=Math.max(1,hours,floor);
    while(nodesNeededAt(hi)>hi+1e-9 && hi<1e9) hi*=2;
    if(hi>=1e9 && nodesNeededAt(hi)>hi+1e-9) return 1e9;
    for(let i=0;i<48;i++){
      const mid=(lo+hi)/2;
      if(nodesNeededAt(mid)<=mid) hi=mid; else lo=mid;
    }
    return hi;
  }

  function acquisitionEffortFor(costs,resources,cfg=activeCalcConfig()){
    const marginalCosts=marginalWeightedCosts(costs,resources,cfg);
    return {hours:jointReacquisitionHours(marginalCosts,resources,cfg)};
  }
  function candidateResourceMetric(candidate){
    const base=Number(candidate?.acquisitionHours);
    return Number.isFinite(base)?base:1e18;
  }
  /* S2_ACQUISITION_OPTIMIZER_V1
     Compare target plans by the time-equivalent burden of reacquiring the marginal
     resources they consume. This is season-agnostic: S2 uses its Lv.120 Realm/open-map
     yields and its own scoring/cost curves. GLOBAL_ACQUISITION_PRIORITY_V2 makes this
     metric primary across raw, existing-tool and paid-refresh sourcing instead of only
     comparing plans after Realm-stage gates are satisfied. */
  function compareAcquisitionEffort(candidate,best){
    const cm=candidateResourceMetric(candidate),bm=candidateResourceMetric(best);
    if(cm<bm-1e-9) return true;
    if(cm>bm+1e-9) return false;
    return null;
  }
  function makePlanCandidate(go,so,ro,fo,score,desired,resources,realms,acquisitionResult=null){
    const oreRealm=realms[0],essenceRealm=realms[1],sandRealm=realms[2];
    const dawniumCost=oreRealm.dawnium+essenceRealm.dawnium+sandRealm.dawnium;
    const realmPacks=oreRealm.packs+essenceRealm.packs+sandRealm.packs;
    const oreShare=resources.ore>0?go.oreCost/resources.ore:(go.oreCost>0?go.oreCost/100000:0);
    const essenceShare=resources.essence>0?so.cost/resources.essence:(so.cost>0?so.cost/100000:0);
    const sandShare=resources.sand>0?ro.cost/resources.sand:(ro.cost>0?ro.cost/100000:0);
    const treatShare=resources.treat>0?fo.cost/resources.treat:(fo.cost>0?fo.cost/10000:0);
    const refinedShare=resources.refinedTracked&&resources.refined>0?go.refinedCost/resources.refined:0;
    const maxShare=Math.max(oreShare,essenceShare,sandShare,treatShare,refinedShare);
    const sumShare=oreShare+essenceShare+sandShare+treatShare+refinedShare;
    /* ACQUISITION_KERNEL_V2 · TOTAL_POOL_SMART_BALANCE_V1 · CANDIDATE_SCALAR_FASTPATH_V5
       Candidate creation is in the hottest optimizer path. Keep the exact same economics and
       public result fields, but avoid per-candidate temporary share/Realm arrays, reduce()
       callbacks and repeated activeCalcConfig() lookups. */
    const cfg=activeCalcConfig();
    const acquisition=acquisitionResult||acquisitionEffortFor({ore:go.oreCost,essence:so.cost,sand:ro.cost,treat:fo.cost},resources,cfg);
    const unknownPriceRefreshes=
      Math.max(0,Number(oreRealm?.unknownPriceRefreshes)||0)+
      Math.max(0,Number(essenceRealm?.unknownPriceRefreshes)||0)+
      Math.max(0,Number(sandRealm?.unknownPriceRefreshes)||0);
    const bankedHammersUsed=oreRealm.bankedUsed||0;
    const bankedKnucklesUsed=essenceRealm.bankedUsed||0;
    const bankedShovelsUsed=sandRealm.bankedUsed||0;
    return {
      gear:go.target,skill:so.avg,relic:ro.avg,fanto:fo.avg,
      skillLevels:so.levels,relicLevels:ro.levels,fantoLevels:fo.levels,
      oreCost:go.oreCost,essenceCost:so.cost,sandCost:ro.cost,treatCost:fo.cost,refinedCost:go.refinedCost,
      score,gearAdds:go.adds,skillAdds:so.adds,relicAdds:ro.adds,fantoAdds:fo.adds,
      oreShare,essenceShare,sandShare,treatShare,refinedShare,
      acquisitionHours:acquisition.hours,unknownPriceRefreshes,
      maxShare,sumShare,overshoot:score-desired,
      dawniumCost,realmAttempts:realmPacks,realmPacks,
      bankedHammersUsed,bankedKnucklesUsed,bankedShovelsUsed,
      bankedToolsUsed:bankedHammersUsed+bankedKnucklesUsed+bankedShovelsUsed,seasonKey:cfg.key,
      realm:{days:Number.isFinite(resources?.realmDays)?resources.realmDays:materialRealmDaysAvailable(cfg),ore:oreRealm,essence:essenceRealm,sand:sandRealm}
    };
  }

  /* REALM_TOOL_TIEBREAK_V2
     Source tier is a hard priority. Inside the same tier, material acquisition weighting
     ranks the route first; literal Realm-tool counts only break a weighted-material tie. */
  function candidateRealmToolBurden(candidate){
    const realms=['ore','essence','sand'].map(k=>candidate?.realm?.[k]).filter(Boolean);
    return {
      paidRuns:realms.reduce((sum,x)=>sum+Math.max(0,Number(x?.paidRunsUsed)||0),0),
      totalRuns:realms.reduce((sum,x)=>sum+Math.max(0,Number(x?.runsNeeded)||0),0),
      bankedUsed:realms.reduce((sum,x)=>sum+Math.max(0,Number(x?.bankedUsed)||0),0)
    };
  }
  function betterToolBurden(candidate,best){
    const c=candidateRealmToolBurden(candidate),b=candidateRealmToolBurden(best);
    if(c.paidRuns<b.paidRuns) return true;
    if(c.paidRuns>b.paidRuns) return false;
    if(c.totalRuns<b.totalRuns) return true;
    if(c.totalRuns>b.totalRuns) return false;
    if(c.bankedUsed<b.bankedUsed) return true;
    if(c.bankedUsed>b.bankedUsed) return false;
    return null;
  }

  function candidateRealmStage(candidate){
    const realms=['ore','essence','sand'].map(k=>candidate?.realm?.[k]).filter(Boolean);
    // A Treat shortage is a hard resource failure because there is no Fantomon-Treat
    // Material Realm tool. Diagnostics therefore rank it after all actually fundable stages.
    if(Math.max(0,Number(candidate?.treatShortfall)||0)>0.5) return 3;
    if(realms.some(x=>Math.max(0,Number(x?.packs)||0)>0 || Math.max(0,Number(x?.paidRunsUsed)||0)>0)) return 2;
    const usesRealmTools=realms.some(x=>{
      const planRuns=Number.isFinite(Number(x?.planRuns)) ? Number(x.planRuns) : Number(x?.runsUsed)||0;
      return planRuns>0;
    });
    return usesRealmTools?1:0;
  }

  function betterFeasibleCandidate(candidate,best){
    if(!best) return true;

    /* TOTAL_POOL_SMART_BALANCE_V1 · FEASIBLE_COMPARE_SCALAR_V5
       Feasible candidates never carry Treat/Realm-overflow diagnostics. Their paid-source
       tier is therefore exactly `realmPacks > 0`; avoid candidateRealmStage() array creation
       on every comparison. Inline the acquisition metric's two scalar reads as well. */
    const cPaid=(Number(candidate.realmPacks)||0)>0,bPaid=(Number(best.realmPacks)||0)>0;
    if(cPaid!==bPaid) return !cPaid;

    if(cPaid&&bPaid){
      const cu=Math.max(0,Number(candidate.unknownPriceRefreshes)||0),bu=Math.max(0,Number(best.unknownPriceRefreshes)||0);
      if(cu<bu) return true;
      if(cu>bu) return false;
      if(candidate.dawniumCost<best.dawniumCost-1e-9) return true;
      if(candidate.dawniumCost>best.dawniumCost+1e-9) return false;
    }

    const cm0=Number(candidate.acquisitionHours),bm0=Number(best.acquisitionHours);
    const cm=Number.isFinite(cm0)?cm0:1e18,bm=Number.isFinite(bm0)?bm0:1e18;
    if(cm<bm-1e-9) return true;
    if(cm>bm+1e-9) return false;

    // Tool preservation remains ONLY a tie-breaker after exact acquisition equality.
    const toolCmp=betterToolBurden(candidate,best);
    if(toolCmp!==null) return toolCmp;

    return candidate.overshoot<best.overshoot-1e-9||
      (Math.abs(candidate.overshoot-best.overshoot)<1e-9&&candidate.maxShare<best.maxShare-1e-9)||
      (Math.abs(candidate.overshoot-best.overshoot)<1e-9&&Math.abs(candidate.maxShare-best.maxShare)<1e-9&&candidate.sumShare<best.sumShare-1e-9);
  }

  function betterDiagnosticCandidate(candidate,best){
    if(!best) return true;
    if(candidate.hardShortfall<best.hardShortfall-0.5) return true;
    if(Math.abs(candidate.hardShortfall-best.hardShortfall)>0.5) return false;
    if(candidate.realmOverflow<best.realmOverflow) return true;
    if(candidate.realmOverflow!==best.realmOverflow) return false;
    if(candidate.remainingAfterMax<best.remainingAfterMax-0.5) return true;
    if(Math.abs(candidate.remainingAfterMax-best.remainingAfterMax)>0.5) return false;

    // Diagnostics use the same owned/projected-pool vs extra-purchase boundary as funded plans.
    const cStage=candidateRealmStage(candidate),bStage=candidateRealmStage(best);
    const cPaid=cStage>=2,bPaid=bStage>=2;
    if(cPaid!==bPaid) return !cPaid;
    if(cPaid&&bPaid){
      const cu=Math.max(0,Number(candidate.unknownPriceRefreshes)||0),bu=Math.max(0,Number(best.unknownPriceRefreshes)||0);
      if(cu<bu) return true;
      if(cu>bu) return false;
      if(candidate.dawniumCost<best.dawniumCost-1e-9) return true;
      if(candidate.dawniumCost>best.dawniumCost+1e-9) return false;
    }
    const effortCmp=compareAcquisitionEffort(candidate,best);
    if(effortCmp!==null) return effortCmp;
    const toolCmp=betterToolBurden(candidate,best);
    if(toolCmp!==null) return toolCmp;
    return candidate.overshoot<best.overshoot;
  }

  // Find both the cheapest fundable plan and the best score-capable shortfall plan in ONE scan.
  // v22/v23 performed almost the same triple-nested search separately, sometimes many times per refresh.
  function searchPlans(baseScore,desired,p,resources,cfg=activeCalcConfig(),ctx=null){
    const context=ctx||createPlanningContext(baseScore,desired,p,cfg);
    const {baseGear,cats,gearOptions,charScore,headroomCosts}=context;
    const realmDays=Number.isFinite(resources?.realmDays)?resources.realmDays:materialRealmDaysAvailable(cfg);

    // TOTAL_POOL_SMART_BALANCE_V1: scarcity/efficiency sees projected raw + saved/already-
    // planned tools at full material equivalent. realmTopupFor() separately preserves the
    // physical consumption order (raw first). Extra candidate purchases never enter this pool.
    resources.acquisitionHeadroomCosts=headroomCosts||{};
    resources.acquisitionSupplyEquiv={
      ore:plannedToolAcquisitionSupply('ore',resources,cfg),
      essence:plannedToolAcquisitionSupply('essence',resources,cfg),
      sand:plannedToolAcquisitionSupply('sand',resources,cfg),
      treat:rawOnlyAcquisitionSupply('treat',resources,cfg)
    };

    if(baseScore>=desired){
      const zero={gear:baseGear,skill:cats.skill.avg,relic:cats.relic.avg,fanto:cats.fanto.avg,skillLevels:cats.skill.levels,relicLevels:cats.relic.levels,fantoLevels:cats.fanto.levels,oreCost:0,essenceCost:0,sandCost:0,treatCost:0,refinedCost:0,score:baseScore,gearAdds:0,skillAdds:0,relicAdds:0,fantoAdds:0,dawniumCost:0,realmAttempts:0,realmPacks:0,seasonKey:cfg.key,realmFeasible:true,realm:{days:realmDays,ore:realmTopupFor('ore',0,resources.ore,resources,cfg,p),essence:realmTopupFor('essence',0,resources.essence,resources,cfg,p),sand:realmTopupFor('sand',0,resources.sand,resources,cfg,p)}};
      return {plan:zero,diagnostic:zero};
    }

    /* RAW_FUNDED_SEARCH_FAST_V1 is intentionally disabled under
       SCARCITY_ADJUSTED_ACQUISITION_V1. Its dimensional collapse was exact only when fully
       funded non-Ore material had zero marginal value and Ore was always fixed at 1.00.
       With continuous nonzero scarcity floors, different Gear/Skill/Relic mixes retain
       different economic costs and must stay in the general exact search. */
    const nonOreRawFunded=false;
    if(nonOreRawFunded){
      const skillMax=cats.skillOptions[cats.skillOptions.length-1];
      const relicMax=cats.relicOptions[cats.relicOptions.length-1];
      const fantoMax=cats.fantoOptions[cats.fantoOptions.length-1];
      const maxNonGearScore=(skillMax?.score||0)+(relicMax?.score||0)+(fantoMax?.score||0);
      const go=gearLocked
        ? (gearOptions[0].score>=Math.max(0,desired-charScore-maxNonGearScore)?gearOptions[0]:null)
        : firstGearOptionAtLeast(gearOptions,Math.max(0,desired-charScore-maxNonGearScore));
      if(go){
        const firstSkillAtLeast=scoreNeeded=>{
          let lo=0,hi=cats.skillOptions.length-1,ans=null;
          while(lo<=hi){
            const mid=(lo+hi)>>1;
            if(cats.skillOptions[mid].score>=scoreNeeded){ans=cats.skillOptions[mid];hi=mid-1;}else lo=mid+1;
          }
          return ans;
        };
        const oreRealm=realmTopupFor('ore',go.oreCost,resources.ore,resources,cfg,p);
        const zeroEssence=realmTopupFor('essence',0,resources.essence,resources,cfg,p);
        const zeroSand=realmTopupFor('sand',0,resources.sand,resources,cfg,p);
        const sharedAcquisition=acquisitionEffortFor({ore:go.oreCost,essence:0,sand:0,treat:0},resources,cfg);
        let fastBest=null;
        for(const ro of cats.relicOptions){
          for(const fo of cats.fantoOptions){
            const neededSkill=Math.max(0,desired-charScore-go.score-ro.score-fo.score);
            const so=firstSkillAtLeast(neededSkill);
            if(!so) continue;
            const score=charScore+go.score+so.score+ro.score+fo.score;
            if(score<desired) continue;
            const candidate=makePlanCandidate(go,so,ro,fo,score,desired,resources,[oreRealm,zeroEssence,zeroSand],sharedAcquisition);
            candidate.realm.days=realmDays;
            candidate.realmFeasible=oreRealm.feasible;
            if(!oreRealm.feasible) continue;
            if(betterFeasibleCandidate(candidate,fastBest)) fastBest=candidate;
          }
        }
        if(fastBest && candidateRealmStage(fastBest)<2) return {plan:fastBest,diagnostic:fastBest};
      }
    }

    /* REALM_OPTION_PROPERTY_CACHE_V7
       Realm top-up results are immutable for one search snapshot and every option object is
       search-local. Cache the result directly on the option instead of doing Map.has()+Map.set()
       +Map.get() on every hot-loop access. This preserves lazy evaluation (unused options still
       cost nothing) while turning repeat Gear/Skill/Relic lookups into one property read. */
    const oreFor=go=>go.__realmOreV7||(go.__realmOreV7=realmTopupFor('ore',go.oreCost,resources.ore,resources,cfg,p));
    const essFor=so=>so.__realmEssenceV7||(so.__realmEssenceV7=realmTopupFor('essence',so.cost,resources.essence,resources,cfg,p));
    const sandFor=ro=>ro.__realmSandV7||(ro.__realmSandV7=realmTopupFor('sand',ro.cost,resources.sand,resources,cfg,p));
    /* ACQUISITION_KERNEL_V2 · TOTAL_POOL_SMART_BALANCE_V1
       This metric is evaluated in the hottest optimizer loop. Precompute each category's
       scarcity-adjusted spend ONCE against the full owned/projected resource-family pool,
       read Cart/map rates once, and run the joint-reacquisition equation with scalar locals.
       Raw-funded and tool-backed candidates therefore use the same economic kernel. */
    for(const go of gearOptions) go.__acqOreV1=marginalWeightedSpend(go.oreCost,'ore',resources);
    for(const so of cats.skillOptions) so.__acqEssenceV1=marginalWeightedSpend(so.cost,'essence',resources);
    for(const ro of cats.relicOptions) ro.__acqSandV1=marginalWeightedSpend(ro.cost,'sand',resources);
    for(const fo of cats.fantoOptions) fo.__acqTreatV1=marginalWeightedSpend(fo.cost,'treat',resources);
    const acqMap=resources?.yields?.map||cfg.map||{};
    const acqCartOre=Math.max(0,n('oreRate'));
    const acqCartEssence=Math.max(0,n('essenceRate'));
    const acqCartSand=Math.max(0,n('sandRate'));
    const acqCartTreat=Math.max(0,n('treatRate'));
    const acqNodeOre=Math.max(0,Number(acqMap.ore)||0);
    const acqNodeEssence=Math.max(0,Number(acqMap.essence)||0);
    const acqNodeSand=Math.max(0,Number(acqMap.sand)||0);
    /* JOINT_HOURS_NO_CLOSURE_V2 · JOINT_HOURS_ACTIVE_SET_V9
       The acquisition equation is a three-term piecewise-linear fixed point:
         sum(max(0, demand - CartRate * hours) / nodeYield) <= hours.
       Active resources can only DROP OUT as hours rises. Precompute reciprocal node yields,
       fold the floor residual check into active-set construction, then solve each active set
       directly. With only Ore/Essence/Sand, at most three active-set solves are possible.
       This removes repeated division, the stable-set verification pass and the 48-step binary
       fallback while preserving the same mathematical root and tolerance boundaries. */
    const acqInvNodeOre=acqNodeOre>0?1/acqNodeOre:0;
    const acqInvNodeEssence=acqNodeEssence>0?1/acqNodeEssence:0;
    const acqInvNodeSand=acqNodeSand>0?1/acqNodeSand:0;
    const acqCartNodeOre=acqCartOre*acqInvNodeOre;
    const acqCartNodeEssence=acqCartEssence*acqInvNodeEssence;
    const acqCartNodeSand=acqCartSand*acqInvNodeSand;
    const nodesAtFast=(hours,ore,essence,sand)=>{
      let total=0,rem=0;
      rem=ore-acqCartOre*hours;if(rem>0){if(acqInvNodeOre<=0)return Infinity;total+=rem*acqInvNodeOre;}
      rem=essence-acqCartEssence*hours;if(rem>0){if(acqInvNodeEssence<=0)return Infinity;total+=rem*acqInvNodeEssence;}
      rem=sand-acqCartSand*hours;if(rem>0){if(acqInvNodeSand<=0)return Infinity;total+=rem*acqInvNodeSand;}
      return total;
    };
    const jointHoursFast=(oreRaw,essRaw,sandRaw,treatRaw)=>{
      const ore=oreRaw>0?oreRaw:0;
      const essence=essRaw>0?essRaw:0;
      const sand=sandRaw>0?sandRaw:0;
      const treat=treatRaw>0?treatRaw:0;
      let floor=0;
      if(treat>0){
        if(acqCartTreat<=0) return 1e9;
        floor=treat/acqCartTreat;
      }
      if(ore>0&&acqInvNodeOre<=0){if(acqCartOre<=0)return 1e9;floor=Math.max(floor,ore/acqCartOre);}
      if(essence>0&&acqInvNodeEssence<=0){if(acqCartEssence<=0)return 1e9;floor=Math.max(floor,essence/acqCartEssence);}
      if(sand>0&&acqInvNodeSand<=0){if(acqCartSand<=0)return 1e9;floor=Math.max(floor,sand/acqCartSand);}

      let mask=0,floorNodes=0,rem=0;
      rem=ore-acqCartOre*floor;
      if(rem>1e-9&&acqInvNodeOre>0){mask|=1;floorNodes+=rem*acqInvNodeOre;}
      rem=essence-acqCartEssence*floor;
      if(rem>1e-9&&acqInvNodeEssence>0){mask|=2;floorNodes+=rem*acqInvNodeEssence;}
      rem=sand-acqCartSand*floor;
      if(rem>1e-9&&acqInvNodeSand>0){mask|=4;floorNodes+=rem*acqInvNodeSand;}
      if(!mask||floorNodes<=floor+1e-9) return floor;

      let hours=floor;
      for(let pass=0;pass<3;pass++){
        let numerator=0,denominator=1;
        if(mask&1){numerator+=ore*acqInvNodeOre;denominator+=acqCartNodeOre;}
        if(mask&2){numerator+=essence*acqInvNodeEssence;denominator+=acqCartNodeEssence;}
        if(mask&4){numerator+=sand*acqInvNodeSand;denominator+=acqCartNodeSand;}
        hours=Math.max(floor,numerator/denominator);
        let next=0;
        if((mask&1)&&ore>acqCartOre*hours+1e-9) next|=1;
        if((mask&2)&&essence>acqCartEssence*hours+1e-9) next|=2;
        if((mask&4)&&sand>acqCartSand*hours+1e-9) next|=4;
        if(next===mask) return hours;
        mask=next;
        if(!mask) return floor;
      }
      // Three resources means a non-empty active set must stabilize within three passes.
      return hours;
    };
    const acquisitionFor=(go,so,ro,fo)=>({hours:jointHoursFast(go.__acqOreV1,so.__acqEssenceV1,ro.__acqSandV1,fo.__acqTreatV1)});
    /* ACQUISITION_LIMIT_PRECHECK_V8
       For the no-paid bounded search acquisition hours are the primary comparator. Before
       solving the piecewise joint-hours equation, test the current winner's time directly:
       if Treat Cart production cannot cover Treat demand by that time, or the map-node work
       still exceeds the same time budget, the candidate's exact joint root must be later and
       it cannot win. This is a necessary-condition rejection only; surviving candidates still
       run the original exact jointHoursFast() and the normal tie-break chain. */
    const acquisitionCannotBeat=(bestHours,go,so,ro,fo)=>{
      if(!Number.isFinite(bestHours)||bestHours>=1e9) return false;
      const limit=bestHours+1e-9;
      const treat=fo.__acqTreatV1;
      if(treat>0){
        if(acqCartTreat<=0) return true;
        if(treat>acqCartTreat*limit+1e-7) return true;
      }
      return nodesAtFast(limit,go.__acqOreV1,so.__acqEssenceV1,ro.__acqSandV1)>limit+1e-7;
    };
    let best=null,bestDiagnostic=null;

    /* OWNED_POOL_IMPOSSIBILITY_FASTPATH_V4 · TOTAL_POOL_SMART_BALANCE_V1
       Prove whether ANY route using projected raw + saved/already-planned tools can reach the
       target before deciding whether a paid-refresh fast-path result needs the expensive scan.
       Extra candidate purchases are excluded from these budgets. */
    const highestAffordable=(options,budget,costKey='cost',secondaryBudget=Infinity,secondaryKey='')=>{
      let bestOption=Array.isArray(options)&&options.length?options[0]:null;
      for(const option of (options||[])){
        const primary=Math.max(0,Number(option?.[costKey])||0);
        const secondary=secondaryKey?Math.max(0,Number(option?.[secondaryKey])||0):0;
        if(primary<=budget+0.5 && secondary<=secondaryBudget+0.5) bestOption=option;
        else if(primary>budget+0.5) break;
      }
      return bestOption;
    };
    const poolRefinedBudget=resources.refinedTracked?Math.max(0,Number(resources.refined)||0):Infinity;
    const poolMaxGear=highestAffordable(gearOptions,plannedToolAcquisitionSupply('ore',resources,cfg),'oreCost',poolRefinedBudget,'refinedCost');
    const poolMaxSkill=highestAffordable(cats.skillOptions,plannedToolAcquisitionSupply('essence',resources,cfg));
    const poolMaxRelic=highestAffordable(cats.relicOptions,plannedToolAcquisitionSupply('sand',resources,cfg));
    const poolMaxFanto=highestAffordable(cats.fantoOptions,Math.max(0,Number(resources.treat)||0));
    const ownedPoolMaxScore=charScore+(poolMaxGear?.score||0)+(poolMaxSkill?.score||0)+(poolMaxRelic?.score||0)+(poolMaxFanto?.score||0);
    const ownedPoolRoutePossible=ownedPoolMaxScore>=desired-1e-9;

    /* TREAT_FUNDED_SEARCH_FAST_V1
       Exact dimensional collapse when raw Treats already fund every reachable Fantomon
       upgrade. In that state the configured fully-funded Treat acquisition floor is zero,
       so Fantomon score is free in the PRIMARY acquisition metric.

       For each Skill+Relic choice, the best acquisition route therefore uses enough free
       Fantomon score to force Gear to its lowest possible option. Once that Gear option is
       fixed, extra Fantomon upgrades cannot improve acquisition and only worsen/equal the
       normal overscore/share tie-breaks, so select the first Fantomon option that reaches
       target. This replaces Relic x Fantomon x Skill with Relic x Skill while preserving
       the exact candidate comparator. */
    /* REFINED_FASTPATH_GUARD_V3
       Keep the Treat-funded dimensional collapse disabled whenever Refined Ore tracking is
       active. Even a numerically funded Refined pool still participates in downstream share/
       tie-break semantics, so collapsing that dimension changes the exact chosen plan. */
    const treatFullyFunded=!resources.refinedTracked &&
      (Number(resources.treat)||0)>=Math.max(0,Number(headroomCosts?.treat)||0)-0.5;
    if(treatFullyFunded && cats.fantoOptions.length>1){
      const fantoMax=cats.fantoOptions[cats.fantoOptions.length-1];
      const firstFantoAtLeast=scoreNeeded=>{
        let lo=0,hi=cats.fantoOptions.length-1,ans=null;
        while(lo<=hi){
          const mid=(lo+hi)>>1;
          if(cats.fantoOptions[mid].score>=scoreNeeded){ans=cats.fantoOptions[mid];hi=mid-1;}else lo=mid+1;
        }
        return ans;
      };
      let fastBest=null,fastDiagnostic=null;
      for(const ro of cats.relicOptions){
        const sandRealm=sandFor(ro);
        for(const so of cats.skillOptions){
          const fixedScore=charScore+ro.score+so.score;
          const go=gearLocked
            ? (gearOptions[0].score+fantoMax.score>=Math.max(0,desired-fixedScore)?gearOptions[0]:null)
            : firstGearOptionAtLeast(gearOptions,Math.max(0,desired-fixedScore-fantoMax.score));
          if(!go) continue;
          const neededFanto=Math.max(0,desired-fixedScore-go.score);
          const fo=firstFantoAtLeast(neededFanto);
          if(!fo) continue;
          const score=fixedScore+go.score+fo.score;
          if(score<desired) continue;

          const oreRealm=oreFor(go),essenceRealm=essFor(so);
          const refinedShortfall=0;
          const hardShortfall=0;
          const realms=[oreRealm,essenceRealm,sandRealm];
          const realmOverflow=realms.reduce((sum,x)=>sum+Math.max(0,(Number.isFinite(x.packs)?x.packs:1e9)-(x.maxPacks||0)),0);
          const remainingAfterMax=realms.reduce((sum,x)=>sum+Math.max(0,x.remainingAfterMax||0),0);
          const realmPacks=realms.reduce((sum,x)=>sum+(Number.isFinite(x.packs)?x.packs:1e9),0);
          const allFeasible=realms.every(x=>x.feasible);
          const dawniumCost=allFeasible?realms.reduce((sum,x)=>sum+x.dawnium,0):Infinity;
          const unknownPriceRefreshes=realms.reduce((sum,x)=>sum+Math.max(0,Number(x?.unknownPriceRefreshes)||0),0);
          const acquisition=acquisitionFor(go,so,ro,fo);

          if(allFeasible){
            const candidate=makePlanCandidate(go,so,ro,fo,score,desired,resources,realms,acquisition);
            candidate.realm.days=realmDays;
            candidate.realmFeasible=true;
            if(betterFeasibleCandidate(candidate,fastBest)) fastBest=candidate;
            continue;
          }

          const treatShortfall=0;
          const diagOreShare=resources.ore>0?go.oreCost/resources.ore:(go.oreCost>0?go.oreCost/100000:0);
          const diagEssenceShare=resources.essence>0?so.cost/resources.essence:(so.cost>0?so.cost/100000:0);
          const diagSandShare=resources.sand>0?ro.cost/resources.sand:(ro.cost>0?ro.cost/100000:0);
          const diagTreatShare=resources.treat>0?fo.cost/resources.treat:0;
          const diagnostic={gear:go.target,skill:so.avg,relic:ro.avg,fanto:fo.avg,skillLevels:so.levels,relicLevels:ro.levels,fantoLevels:fo.levels,oreCost:go.oreCost,essenceCost:so.cost,sandCost:ro.cost,treatCost:fo.cost,refinedCost:go.refinedCost,score,gearAdds:go.adds,skillAdds:so.adds,relicAdds:ro.adds,fantoAdds:fo.adds,overshoot:score-desired,dawniumCost,realmAttempts:realmPacks,realmPacks,oreShare:diagOreShare,essenceShare:diagEssenceShare,sandShare:diagSandShare,treatShare:diagTreatShare,acquisitionHours:acquisition.hours,unknownPriceRefreshes,bankedHammersUsed:(oreRealm.bankedUsed||0),bankedKnucklesUsed:(essenceRealm.bankedUsed||0),bankedShovelsUsed:(sandRealm.bankedUsed||0),bankedToolsUsed:(oreRealm.bankedUsed||0)+(essenceRealm.bankedUsed||0)+(sandRealm.bankedUsed||0),realmOverflow,remainingAfterMax,treatShortfall,refinedShortfall,hardShortfall,seasonKey:cfg.key,realmFeasible:false,realm:{days:realmDays,ore:oreRealm,essence:essenceRealm,sand:sandRealm}};
          if(betterDiagnosticCandidate(diagnostic,fastDiagnostic)) fastDiagnostic=diagnostic;
        }
      }
      if(fastBest && (candidateRealmStage(fastBest)<2 || !ownedPoolRoutePossible)) return {plan:fastBest,diagnostic:fastBest};
      // If the owned/projected pool can still reach the target without extra purchases, keep
      // scanning before accepting a paid-refresh route because extra purchases are last resort.
    }

    /* BOUNDED_FEASIBLE_SEARCH_V1
       Before the expensive diagnostic scan, prove the largest independently fundable
       option in each resource family. Because Gear/Ore, Skills/Essence, Relics/Sand and
       Fantomons/Treats use separate budgets in this model, the sum of those maxima proves
       whether at least one fully fundable target route exists.

       If a route exists without EXTRA Realm purchases, paid-refresh candidates are
       categorically worse under betterFeasibleCandidate(), so search only the owned/raw+
       banked-tool prefixes. Otherwise, if a route exists within maximum legal Realm
       capacity, search only the individually feasible prefixes. This cannot change the
       winner: every excluded option is either physically impossible or belongs to a
       sourcing tier that loses before acquisition-effort tie-breaks are considered.

       The bounded scan also starts each monotone category at the first score that could
       possibly reach the target even with all remaining categories maxed. That removes
       millions of low-score combinations that previously called the Gear binary search
       only to discover that no Gear option could make them reach target. */
    const lastTrueIndex=(options,predicate)=>{
      let lo=0,hi=(options?.length||0)-1,ans=-1;
      while(lo<=hi){
        const mid=(lo+hi)>>1;
        if(predicate(options[mid],mid)){ans=mid;lo=mid+1;}else hi=mid-1;
      }
      return ans;
    };
    const firstScoreIndex=(options,scoreNeeded)=>{
      const need=Math.max(0,Number(scoreNeeded)||0);
      let lo=0,hi=(options?.length||0)-1,ans=options?.length||0;
      while(lo<=hi){
        const mid=(lo+hi)>>1;
        if((Number(options[mid]?.score)||0)>=need){ans=mid;hi=mid-1;}else lo=mid+1;
      }
      return ans;
    };
    const refinedFunded=go=>!resources.refinedTracked || (Number(go?.refinedCost)||0)<=(Number(resources.refined)||0)+0.5;
    const noPaidRealm=x=>!!x?.feasible && Math.max(0,Number(x?.packs)||0)<=0;

    const feasibleLast={
      gear:lastTrueIndex(gearOptions,go=>refinedFunded(go)&&!!oreFor(go)?.feasible),
      skill:lastTrueIndex(cats.skillOptions,so=>!!essFor(so)?.feasible),
      relic:lastTrueIndex(cats.relicOptions,ro=>!!sandFor(ro)?.feasible),
      fanto:lastTrueIndex(cats.fantoOptions,fo=>(Number(fo?.cost)||0)<=(Number(resources.treat)||0)+0.5)
    };
    const noPaidLast={
      gear:lastTrueIndex(gearOptions,go=>refinedFunded(go)&&noPaidRealm(oreFor(go))),
      skill:lastTrueIndex(cats.skillOptions,so=>noPaidRealm(essFor(so))),
      relic:lastTrueIndex(cats.relicOptions,ro=>noPaidRealm(sandFor(ro))),
      fanto:feasibleLast.fanto
    };
    const scoreAt=(options,index)=>index>=0?(Number(options[index]?.score)||0):-Infinity;
    const maxRouteScore=last=>charScore+
      scoreAt(gearOptions,last.gear)+scoreAt(cats.skillOptions,last.skill)+
      scoreAt(cats.relicOptions,last.relic)+scoreAt(cats.fantoOptions,last.fanto);
    const noPaidRoutePossible=Object.values(noPaidLast).every(i=>i>=0) && maxRouteScore(noPaidLast)>=desired-1e-9;
    const feasibleRoutePossible=Object.values(feasibleLast).every(i=>i>=0) && maxRouteScore(feasibleLast)>=desired-1e-9;
    const boundedLast=noPaidRoutePossible?noPaidLast:(feasibleRoutePossible?feasibleLast:null);

    if(boundedLast){
      const boundedGear=gearOptions.slice(0,boundedLast.gear+1);
      const boundedSkill=cats.skillOptions.slice(0,boundedLast.skill+1);
      const boundedRelic=cats.relicOptions.slice(0,boundedLast.relic+1);

      /* ZERO_RATE_FANTO_PRUNE_V1
         Treats have no map/Realm reacquisition path. If Treat Cart income is zero, any
         Fantomon upgrade has the optimizer's 1e9 acquisition penalty. When the target is
         already reachable in the same preferred no-paid sourcing tier with the current
         Fantomon level, every positive-Treat Fantomon option is strictly worse before
         overscore/share tie-breaks are consulted. Keep only the zero-cost base option.

         This is especially important for well-funded accounts: the old exact scan still
         walked hundreds of Fantomon states even though none could beat a finite-acquisition
         base-Fantomon route. */
      let boundedFantoLast=boundedLast.fanto;
      if(noPaidRoutePossible && acqCartTreat<=0 && (Number(cats.fantoOptions[0]?.__acqTreatV1)||0)<=1e-9){
        const baseFantoScore=Number(cats.fantoOptions[0]?.score)||0;
        const noPaidBaseFantoMax=charScore+
          scoreAt(gearOptions,noPaidLast.gear)+scoreAt(cats.skillOptions,noPaidLast.skill)+
          scoreAt(cats.relicOptions,noPaidLast.relic)+baseFantoScore;
        if(noPaidBaseFantoMax>=desired-1e-9) boundedFantoLast=0;
      }
      const boundedFanto=cats.fantoOptions.slice(0,boundedFantoLast+1);
      const maxGearScore=Number(boundedGear[boundedGear.length-1]?.score)||0;
      const maxSkillScore=Number(boundedSkill[boundedSkill.length-1]?.score)||0;
      const maxFantoScore=Number(boundedFanto[boundedFanto.length-1]?.score)||0;

      /* BOUNDED_EAGER_REALM_V12
         The exact bounded scan revisits the same Gear/Skill/Relic options thousands of times.
         Materialize each immutable Realm result once for this search snapshot and store the
         refined-funding bit on Gear. The hot loops then use direct property reads instead of
         repeatedly entering oreFor()/essFor()/sandFor()/refinedFunded() wrappers. */
      for(const go of boundedGear){ go.__realmOreV7=oreFor(go); go.__refinedFundedV12=refinedFunded(go); }
      for(const so of boundedSkill) so.__realmEssenceV7=essFor(so);
      for(const ro of boundedRelic) ro.__realmSandV7=sandFor(ro);

      const relicStart=firstScoreIndex(boundedRelic,desired-charScore-maxGearScore-maxSkillScore-maxFantoScore);
      let boundedBest=null;

      /* COARSE_EXACT_SEED_V1
         Give branch-and-bound a strong VALID upper bound before the exhaustive scan.
         Sample a small evenly-spaced set of Relic/Fantomon states, but search the complete
         monotone Skill->minimum-Gear frontier inside each sampled state. Every seed is a
         normal exact candidate scored by the same comparator; it can only make later
         lower-bound pruning stronger, never alter correctness. */
      const sampledIndices=(start,length,count=10)=>{
        const out=new Set();
        const first=Math.max(0,Math.min(length-1,start));
        const last=Math.max(first,length-1);
        if(length<=0) return [];
        if(last===first) return [first];
        for(let i=0;i<count;i++) out.add(Math.round(first+(last-first)*(i/(count-1))));
        return [...out].sort((a,b)=>a-b);
      };
      for(const ri of sampledIndices(relicStart,boundedRelic.length,10)){
        const ro=boundedRelic[ri],sandRealm=ro.__realmSandV7;
        const fantoStart=firstScoreIndex(boundedFanto,desired-charScore-ro.score-maxGearScore-maxSkillScore);
        for(const fi of sampledIndices(fantoStart,boundedFanto.length,10)){
          const fo=boundedFanto[fi];
          const fixedBeforeSkill=charScore+ro.score+fo.score;
          const skillStart=firstScoreIndex(boundedSkill,desired-fixedBeforeSkill-maxGearScore);
          if(skillStart>=boundedSkill.length) continue;
          /* SKILL_GEAR_TWO_POINTER_V10
             The old loop walked every Skill option and binary-searched Gear each time, then
             discarded all but the FIRST Skill state mapping to each minimum Gear step. Keep
             that exact candidate frontier/order, but walk it with monotone Skill/Gear cursors:
             one Gear binary search to enter the frontier, then a linear scan only until the
             next lower Gear step becomes sufficient. No per-Skill Gear binary searches. */
          let si=skillStart;
          let gi=gearLocked?0:firstScoreIndex(boundedGear,desired-fixedBeforeSkill-boundedSkill[si].score);
          while(si<boundedSkill.length&&gi<boundedGear.length){
            const so=boundedSkill[si],go=boundedGear[gi];
            const score=fixedBeforeSkill+so.score+go.score;
            if(score>=desired&&go.__refinedFundedV12){
              const oreRealm=go.__realmOreV7,essenceRealm=so.__realmEssenceV7;
              if(oreRealm.feasible&&essenceRealm.feasible&&sandRealm.feasible &&
                 !(noPaidRoutePossible&&boundedBest&&acquisitionCannotBeat(boundedBest.acquisitionHours,go,so,ro,fo))){
                const acquisition=acquisitionFor(go,so,ro,fo);
                if(!(noPaidRoutePossible&&boundedBest&&acquisition.hours>boundedBest.acquisitionHours+1e-9)){
                  const candidate=makePlanCandidate(go,so,ro,fo,score,desired,resources,[oreRealm,essenceRealm,sandRealm],acquisition);
                  candidate.realm.days=realmDays;
                  candidate.realmFeasible=true;
                  if(noPaidRoutePossible&&boundedBest&&acquisition.hours<boundedBest.acquisitionHours-1e-9){
                    boundedBest=candidate;
                  }else if(betterFeasibleCandidate(candidate,boundedBest)) boundedBest=candidate;
                }
              }
            }
            if(gearLocked||gi===0) break;
            const nextGearScore=Number(boundedGear[gi-1]?.score)||0;
            do{si++;}while(si<boundedSkill.length &&
              fixedBeforeSkill+(Number(boundedSkill[si]?.score)||0)+nextGearScore<desired-1e-9);
            if(si>=boundedSkill.length) break;
            const need=desired-fixedBeforeSkill-(Number(boundedSkill[si]?.score)||0);
            while(gi>0&&(Number(boundedGear[gi-1]?.score)||0)>=need-1e-9) gi--;
          }
        }
      }

      /* ACQUISITION_LOWER_BOUND_PRUNE_V1 · MONOTONE_BOUND_BINARY_PRUNE_V2
         jointHoursFast() is monotone in every resource demand. Instead of evaluating the
         same lower-bound equation once for every Relic/Fantomon/Skill iteration, binary-search
         the first option that is already worse than the current exact seed. This preserves the
         identical candidate set: only a monotone suffix that the old loop would immediately
         break on is skipped. A later/improved best can only make these precomputed ends loose,
         never incorrectly exclude a winner. */
      const firstWorseIndex=(options,start,hoursFor)=>{
        if(!boundedBest) return options.length;
        const limit=boundedBest.acquisitionHours+1e-9;
        let lo=Math.max(0,start),hi=options.length-1,ans=options.length;
        while(lo<=hi){
          const mid=(lo+hi)>>1;
          if(hoursFor(options[mid])>limit){ans=mid;hi=mid-1;}else lo=mid+1;
        }
        return ans;
      };

      const relicEnd=firstWorseIndex(boundedRelic,relicStart,ro=>jointHoursFast(0,0,ro.__acqSandV1,0));
      for(let ri=relicStart;ri<relicEnd;ri++){
        const ro=boundedRelic[ri];
        /* DYNAMIC_OUTER_BOUND_V12
           relicEnd/fantoEnd are based on the seed winner. If the exact scan finds a faster
           winner, refresh the cheap monotone subset bound inline so we can stop the now-dead
           Relic/Fantomon suffix immediately. */
        if(noPaidRoutePossible&&boundedBest&&
           jointHoursFast(0,0,ro.__acqSandV1,0)>boundedBest.acquisitionHours+1e-9) break;
        const sandRealm=ro.__realmSandV7;
        const fantoStart=firstScoreIndex(boundedFanto,desired-charScore-ro.score-maxGearScore-maxSkillScore);
        const fantoEnd=firstWorseIndex(boundedFanto,fantoStart,fo=>jointHoursFast(0,0,ro.__acqSandV1,fo.__acqTreatV1));
        for(let fi=fantoStart;fi<fantoEnd;fi++){
          const fo=boundedFanto[fi];
          if(noPaidRoutePossible&&boundedBest&&
             jointHoursFast(0,0,ro.__acqSandV1,fo.__acqTreatV1)>boundedBest.acquisitionHours+1e-9) break;
          const fixedBeforeSkill=charScore+ro.score+fo.score;
          const skillStart=firstScoreIndex(boundedSkill,desired-fixedBeforeSkill-maxGearScore);
          if(skillStart>=boundedSkill.length) continue;
          const skillEnd=firstWorseIndex(boundedSkill,skillStart,so=>jointHoursFast(0,so.__acqEssenceV1,ro.__acqSandV1,fo.__acqTreatV1));
          if(skillStart>=skillEnd) continue;

          /* SKILL_GEAR_TWO_POINTER_V10
             Same exact frontier as the legacy duplicate-skip loop, but without a Gear binary
             search for every skipped Skill state. Skill only rises and required Gear only
             falls, so a pair of monotone cursors visits the first Skill state of each Gear
             step in identical order. */
          let si=skillStart;
          let gi=gearLocked?0:firstScoreIndex(boundedGear,desired-fixedBeforeSkill-boundedSkill[si].score);
          while(si<skillEnd&&gi<boundedGear.length){
            const so=boundedSkill[si],go=boundedGear[gi];
            const score=fixedBeforeSkill+so.score+go.score;
            if(score>=desired&&go.__refinedFundedV12){
              const oreRealm=go.__realmOreV7,essenceRealm=so.__realmEssenceV7;
              if(oreRealm.feasible&&essenceRealm.feasible&&sandRealm.feasible){
                const dominated=boundedBest && go.oreCost>=boundedBest.oreCost &&
                  so.cost>=boundedBest.essenceCost && ro.cost>=boundedBest.sandCost &&
                  fo.cost>=boundedBest.treatCost && go.refinedCost>=boundedBest.refinedCost;
                if(!dominated &&
                   !(noPaidRoutePossible&&boundedBest&&acquisitionCannotBeat(boundedBest.acquisitionHours,go,so,ro,fo))){
                  const acquisition=acquisitionFor(go,so,ro,fo);
                  if(!(noPaidRoutePossible&&boundedBest&&acquisition.hours>boundedBest.acquisitionHours+1e-9)){
                    const candidate=makePlanCandidate(go,so,ro,fo,score,desired,resources,[oreRealm,essenceRealm,sandRealm],acquisition);
                    candidate.realm.days=realmDays;
                    candidate.realmFeasible=true;
                    if(noPaidRoutePossible&&boundedBest&&acquisition.hours<boundedBest.acquisitionHours-1e-9){
                      boundedBest=candidate;
                    }else if(betterFeasibleCandidate(candidate,boundedBest)) boundedBest=candidate;
                  }
                }
              }
            }
            if(gearLocked||gi===0) break;
            const nextGearScore=Number(boundedGear[gi-1]?.score)||0;
            do{si++;}while(si<skillEnd &&
              fixedBeforeSkill+(Number(boundedSkill[si]?.score)||0)+nextGearScore<desired-1e-9);
            if(si>=skillEnd) break;
            const need=desired-fixedBeforeSkill-(Number(boundedSkill[si]?.score)||0);
            while(gi>0&&(Number(boundedGear[gi-1]?.score)||0)>=need-1e-9) gi--;
          }
        }
      }
      if(boundedBest) return {plan:boundedBest,diagnostic:boundedBest};
      // Defensive fall-through: if future rule changes violate one of the monotonic
      // assumptions above, the legacy full scan below still preserves correctness.
    }

    /* AFFORDABLE_TREAT_FEASIBLE_V1
       Treats have no Material-Realm top-up path. Any actually FUNDABLE plan must therefore
       choose a Fantomon option whose Treat cost is already covered by projected Treat
       inventory. When that affordable slice is much smaller than the full Fantomon search
       range, do a cheap feasible-only pass first. If it finds a plan, every excluded
       Fantomon option is provably infeasible and the expensive diagnostic scan is unnecessary.
       If it finds nothing, fall through to the complete scan so shortfall diagnostics remain exact. */
    const affordableFantoOptions=cats.fantoOptions.filter(fo=>fo.cost<=(Number(resources.treat)||0)+0.5);
    if(affordableFantoOptions.length>0 && affordableFantoOptions.length*1.25<cats.fantoOptions.length){
      let affordableBest=null;
      for(const ro of cats.relicOptions){
        const sandRealm=sandFor(ro);
        for(const fo of affordableFantoOptions){
          const fixedBeforeSkill=charScore+ro.score+fo.score;
          let lastGearAdds=null;
          for(const so of cats.skillOptions){
            const fixedScore=fixedBeforeSkill+so.score;
            const go=gearLocked?(gearOptions[0].score>=Math.max(0,desired-fixedScore)?gearOptions[0]:null):firstGearOptionAtLeast(gearOptions,Math.max(0,desired-fixedScore));
            if(!go) continue;
            if(lastGearAdds===go.adds) continue;
            lastGearAdds=go.adds;
            const score=fixedScore+go.score;
            if(score<desired) continue;
            const refinedShortfall=resources.refinedTracked?Math.max(0,go.refinedCost-resources.refined):0;
            if(refinedShortfall>0.5) continue;
            const oreRealm=oreFor(go),essenceRealm=essFor(so);
            const realms=[oreRealm,essenceRealm,sandRealm];
            if(!realms.every(x=>x.feasible)) continue;
            if(affordableBest && go.oreCost>=affordableBest.oreCost && so.cost>=affordableBest.essenceCost && ro.cost>=affordableBest.sandCost && fo.cost>=affordableBest.treatCost && go.refinedCost>=affordableBest.refinedCost) continue;
            const acquisition=acquisitionFor(go,so,ro,fo);
            const candidate=makePlanCandidate(go,so,ro,fo,score,desired,resources,realms,acquisition);
            candidate.realm.days=realmDays;
            candidate.realmFeasible=true;
            if(betterFeasibleCandidate(candidate,affordableBest)) affordableBest=candidate;
          }
        }
      }
      if(affordableBest) return {plan:affordableBest,diagnostic:affordableBest};
    }

    for(const ro of cats.relicOptions){
      const sandRealm=sandFor(ro);
      for(const fo of cats.fantoOptions){
        const treatShortfall=Math.max(0,fo.cost-resources.treat);
        const fixedBeforeSkill=charScore+ro.score+fo.score;
        let lastGearAdds=null;
        for(const so of cats.skillOptions){
          const fixedScore=fixedBeforeSkill+so.score;
          const go=gearLocked?(gearOptions[0].score>=Math.max(0,desired-fixedScore)?gearOptions[0]:null):firstGearOptionAtLeast(gearOptions,Math.max(0,desired-fixedScore));
          if(!go)continue;
          // PERFORMANCE_STABILIZATION_V1: if Gear did not step down, this later Skill
          // option spends more Essence for the same required Gear and cannot win.
          if(lastGearAdds===go.adds) continue;
          lastGearAdds=go.adds;
          const score=fixedScore+go.score;if(score<desired)continue;

          const oreRealm=oreFor(go),essenceRealm=essFor(so);
          const refinedShortfall=resources.refinedTracked?Math.max(0,go.refinedCost-resources.refined):0;
          const hardShortfall=treatShortfall+refinedShortfall;
          const realms=[oreRealm,essenceRealm,sandRealm];
          const realmOverflow=realms.reduce((sum,x)=>sum+Math.max(0,(Number.isFinite(x.packs)?x.packs:1e9)-(x.maxPacks||0)),0);
          const remainingAfterMax=realms.reduce((sum,x)=>sum+Math.max(0,x.remainingAfterMax||0),0);
          const realmPacks=realms.reduce((sum,x)=>sum+(Number.isFinite(x.packs)?x.packs:1e9),0);
          const allFeasible=realms.every(x=>x.feasible)&&hardShortfall<=0.5;
          const dawniumCost=allFeasible?realms.reduce((sum,x)=>sum+x.dawnium,0):Infinity;

          const unknownPriceRefreshes=realms.reduce((sum,x)=>sum+Math.max(0,Number(x?.unknownPriceRefreshes)||0),0);

          if(allFeasible){
            // A route that costs at least as much as the current winner in every tracked
            // resource (and Refined Ore) is strictly dominated and cannot win later tie-breaks.
            if(best && go.oreCost>=best.oreCost && so.cost>=best.essenceCost && ro.cost>=best.sandCost && fo.cost>=best.treatCost && go.refinedCost>=best.refinedCost) continue;
            const acquisition=acquisitionFor(go,so,ro,fo);
            const candidate=makePlanCandidate(go,so,ro,fo,score,desired,resources,[oreRealm,essenceRealm,sandRealm],acquisition);
            candidate.realm.days=realmDays;
            candidate.realmFeasible=true;
            if(betterFeasibleCandidate(candidate,best)) best=candidate;
            continue;
          }

          // betterDiagnosticCandidate always compares these three fields first. If this route
          // already loses there, the expensive acquisition metric cannot rescue it.
          if(bestDiagnostic){
            if(hardShortfall>bestDiagnostic.hardShortfall+0.5) continue;
            if(Math.abs(hardShortfall-bestDiagnostic.hardShortfall)<=0.5){
              if(realmOverflow>bestDiagnostic.realmOverflow) continue;
              if(realmOverflow===bestDiagnostic.realmOverflow && remainingAfterMax>bestDiagnostic.remainingAfterMax+0.5) continue;
            }
          }
          const diagOreShare=resources.ore>0?go.oreCost/resources.ore:(go.oreCost>0?go.oreCost/100000:0),diagEssenceShare=resources.essence>0?so.cost/resources.essence:(so.cost>0?so.cost/100000:0),diagSandShare=resources.sand>0?ro.cost/resources.sand:(ro.cost>0?ro.cost/100000:0),diagTreatShare=resources.treat>0?fo.cost/resources.treat:(fo.cost>0?fo.cost/10000:0);
          const diagAcquisition=acquisitionFor(go,so,ro,fo);
          const diagnostic={gear:go.target,skill:so.avg,relic:ro.avg,fanto:fo.avg,skillLevels:so.levels,relicLevels:ro.levels,fantoLevels:fo.levels,oreCost:go.oreCost,essenceCost:so.cost,sandCost:ro.cost,treatCost:fo.cost,refinedCost:go.refinedCost,score,gearAdds:go.adds,skillAdds:so.adds,relicAdds:ro.adds,fantoAdds:fo.adds,overshoot:score-desired,dawniumCost,realmAttempts:realmPacks,realmPacks,oreShare:diagOreShare,essenceShare:diagEssenceShare,sandShare:diagSandShare,treatShare:diagTreatShare,acquisitionHours:diagAcquisition.hours,unknownPriceRefreshes,bankedHammersUsed:(oreRealm.bankedUsed||0),bankedKnucklesUsed:(essenceRealm.bankedUsed||0),bankedShovelsUsed:(sandRealm.bankedUsed||0),bankedToolsUsed:(oreRealm.bankedUsed||0)+(essenceRealm.bankedUsed||0)+(sandRealm.bankedUsed||0),realmOverflow,remainingAfterMax,treatShortfall,refinedShortfall,hardShortfall,seasonKey:cfg.key,realmFeasible:false,realm:{days:realmDays,ore:oreRealm,essence:essenceRealm,sand:sandRealm}};
          if(betterDiagnosticCandidate(diagnostic,bestDiagnostic)) bestDiagnostic=diagnostic;
        }
      }
    }
    return {plan:best,diagnostic:best||bestDiagnostic};
  }

  function optimizer(baseScore,desired,p,resources,cfg=activeCalcConfig(),ctx=null){
    return searchPlans(baseScore,desired,p,resources,cfg,ctx).plan;
  }

  // Find the lowest-shortfall score-capable route for the ORIGINAL requested target.
  function diagnoseTarget(baseScore,desired,p,resources,cfg=activeCalcConfig(),ctx=null){
    return searchPlans(baseScore,desired,p,resources,cfg,ctx).diagnostic;
  }


  /* TOOL_ONLY_RESOURCE_GAPS_V4
     S2 reserve math stays internal. On a feasible plan, result cards show no leftover or
     reserve bookkeeping. If Realm tools are actually consumed, show only total tools used,
     their approximate material value, and the tools left afterward with approximate value. */
  function hidePlanBalance(id){
    const el=$(id); if(!el) return;
    el.textContent=''; el.innerHTML=''; el.hidden=true;
    el.classList.remove('shortfallCount','shortfallBreakdown','reserveHasGap');
  }
  /* RAW_REMAINING_DISPLAY_V1: visible balance is only material-equivalent left
     after the S1 upgrade spend. Reserve bookkeeping stays internal.
     RAW_REMAINING_NO_RAW_LABEL_V2 */
  function setRawRemaining(id,cost,available,unitLabel=''){
    const el=$(id); if(!el) return;
    el.classList.remove('shortfallCount','shortfallBreakdown','reserveHasGap');
    el.classList.add('rawRemaining');
    const left=Math.max(0,Math.floor((Number(available)||0)-(Number(cost)||0)+1e-9));
    el.hidden=false;
    el.innerHTML=`<span class="resourceRemainingLine">Remaining: <b>${fmt(left)}${unitLabel?` ${unitLabel}`:''}</b></span>`;
  }
  function setEssenceBalance(id,cost,resources){ setRawRemaining(id,cost,resources.essence); }
  function setSandBalance(id,cost,resources){ setRawRemaining(id,cost,resources.sand); }
  function setTreatBalance(id,cost,resources){ setRawRemaining(id,cost,resources.treat,'basic-eq.'); }

  function setBalance(id, cost, budget, yieldVal, itemName){
    const el=$(id); if(!el) return;
    const diff=budget-cost;
    el.classList.remove('shortfallCount','shortfallBreakdown');
    if(diff>=-0.5){ hidePlanBalance(id); return; }
    const short=Math.ceil(-diff);
    const count = yieldVal>0 ? Math.ceil(short/yieldVal) : 0;
    el.hidden=false;
    el.textContent=`${fmt(short)} short${count?` · ${fmt(count)} ${itemName}`:''}`;
    el.classList.add('shortfallCount');
  }

  function setToolBalance(id,top,hardShort,yieldVal,label,protectedRuns=0,rawRemaining=0){
    const el=$(id); if(!el) return;
    el.classList.remove('toolNeed','toolLeft');
    const materialName=label==='Hammers'?'Ore':label==='Knuckles'?'Essence':label==='Shovels'?'Sand':'materials';
    const planRuns=Math.max(0,Math.floor(Number(top?.planRuns ?? top?.runsUsed)||0));
    const reserveRuns=Math.max(0,Math.floor(Number(top?.reserveRuns)||0));
    const totalRuns=Math.max(0,planRuns+reserveRuns);
    const planPer=Math.max(0,Number(top?.planPerRun ?? yieldVal)||0);
    const reservePer=Math.max(0,Number(top?.reservePerRun)||0);
    const left=Math.max(0,Math.floor(Number(top?.bankedRemaining)||0)+Math.floor(Number(top?.sparePurchasedRuns)||0));
    // TOOL_VALUE_DISPLAY_V6: Use one display value per tool for BOTH Used and Left.
    // This applies to Hammers, Knuckles and Shovels, so a card can never mix S1 and S2
    // rates between the two rows. If any of the tools are fulfilling the season-transition
    // requirement, the whole card uses that carried-forward value; otherwise it uses the
    // current plan yield.
    // TOOL_RESERVE_HOLD_LABEL_V7: distinguish tools actually consumed for the
    // current-season plan from tools merely allocated to the S2 reserve. This keeps the
    // card from telling the player to "Use" tools that should stay banked for rollover.
    const planDisplayPer=Math.max(0,Number(planPer||yieldVal)||0);
    const reserveDisplayPer=Math.max(0,Number(reservePer)||0);
    const leftDisplayPer=reserveRuns>0&&reserveDisplayPer>0
      ? reserveDisplayPer
      : planDisplayPer;
    const planGained=planRuns*planDisplayPer;
    const reserveValue=reserveRuns*reserveDisplayPer;
    const leftValue=left*leftDisplayPer;
    const required=Math.max(0,Math.floor(Number(top?.runsNeeded)||totalRuns));
    const maxRuns=Math.max(0,Math.floor(Number(top?.maxRuns)||0));
    const missing=Math.max(0,required-maxRuns);

    // REMAINING_REALM_TOOLS_VISIBLE_V1
    // Keep the cards compact: never print Use: 0, but always preserve useful inventory context
    // by showing remaining Hammers/Knuckles/Shovels when any are still available.
    const remainingTools=Math.max(0,left+reserveRuns);
    const dailyGapRuns=Math.max(0,Math.floor(Number(top?.paidRunsUsed)||0));
    const toolSingular=label==='Hammers'?'Hammer':label==='Knuckles'?'Knuckle':label==='Shovels'?'Shovel':'tool';
    const toolNeedLabel=dailyGapRuns===1?toolSingular:label;
    // TOOL_NEED_VALUE_V14: show the material-equivalent value beside Need, matching Use.
    // If the gap exists to preserve an enabled rollover reserve, value those tools at the
    // reserve yield; otherwise use the current-season Material Realm yield.
    const dailyGapDisplayPer=reserveRuns>0&&reserveDisplayPer>0?reserveDisplayPer:planDisplayPer;
    const dailyGapValue=dailyGapRuns*dailyGapDisplayPer;
    // TOOL_COUNT_LABELS_V15: Use / Need / Remaining are Material Realm TOOL counts.
    // RAW_MATERIAL_SHORTFALL_DISPLAY_V1: once Realm capacity is exhausted, stop expressing
    // the unresolved gap as a tool count. Show the exact raw material still missing instead.
    const lines=[];
    const planToolLabel=planRuns===1?toolSingular:label;
    const remainingToolLabel=remainingTools===1?toolSingular:label;
    if(planRuns>0){
      lines.push(`<div class="toolSimpleLine toolUseLine"><i>Use:</i><b>${fmt(planRuns)} ${planToolLabel}${planGained>0?` <em>≈ ${fmtCompact(planGained)} ${materialName}</em>`:''}</b></div>`);
      if(dailyGapRuns>0){
        lines.push(`<div class="toolSimpleLine toolNeedLine"><i>Need:</i><b>${fmt(dailyGapRuns)} ${toolNeedLabel}${dailyGapValue>0?` <em>≈ ${fmtCompact(dailyGapValue)} ${materialName}</em>`:''}</b></div>`);
      }
    }
    // CONDITIONAL_TOOL_REMAINING_V1:
    // Show a remainder only when no additional Realm tools are required. If the plan
    // still has a Need line, suppress the tiny remainder created by whole-tool purchase
    // rounding so the result does not read as Need -> Remaining.
    if(dailyGapRuns<=0 && remainingTools>0){
      lines.push(`<div class="toolSimpleLine toolRemainingLine"><i>Remaining:</i><b>${fmt(remainingTools)} ${remainingToolLabel}${reserveRuns>0?` <em>(${fmt(reserveRuns)} reserved)</em>`:''}</b></div>`);
    }
    // Hard/recoverable material shortages are already communicated by the resource card above.
    // Do not resurrect the old duplicate "Still short" tool footer.
    if(!lines.length){ el.innerHTML=''; el.hidden=true; return; }
    el.hidden=false;
    el.innerHTML=lines.join('');
    el.classList.add((missing>0||dailyGapRuns>0)?'toolNeed':'toolLeft');
  }

  // RESULT_STAMINA_PROJECTION_V1: repeat the optimizer's Stamina target in the
  // right-side resource cards so the next farming target remains obvious when Realm is closed.
  function appendStaminaProjection(id,nodes,gain,materialName){
    const el=$(id); if(!el) return;
    const count=Math.max(0,Math.floor(Number(nodes)||0));
    const value=Math.max(0,Number(gain)||0);
    if(count<=0) return;
    const line=document.createElement('div');
    line.className='toolSimpleLine staminaProjectionLine';
    line.innerHTML=`<i>Stamina:</i><b>${fmt(count)}${value>0?` <em>→ +${fmtCompact(value)} ${materialName}</em>`:''}</b>`;
    el.appendChild(line);
    el.hidden=false;
    if(!el.classList.contains('toolNeed')) el.classList.add('toolLeft');
  }
  /* RICH_RESOURCE_SHORTFALL_NO_DUPLICATE_V1
     Keep the richer daily-plan / hard-cap presentation in the resource card itself.
     The separate Material Realm tool footer no longer repeats a "Still short" line. */
  function setRealmShortfallBreakdown(id,planShort,yieldVal,itemName,maxExtraRuns,hardShort,resourceName='resource',appendText=''){
    const el=$(id); if(!el) return;
    const short=Math.max(0,Math.ceil(Number(planShort)||0));
    const per=Math.max(0,Number(yieldVal)||0);
    const runsToCover=per>0?Math.ceil(short/per):0;
    const extraRuns=Math.max(0,Math.floor(Number(maxExtraRuns)||0));
    const usableExtra=Math.min(runsToCover,extraRuns);
    const extraResource=usableExtra*per;
    const hard=Math.max(0,Math.ceil(Number(hardShort)||0));
    el.classList.remove('shortfallCount','rawRemaining','reserveHasGap');
    el.classList.add('shortfallBreakdown');
    el.hidden=false;
    if(short<=0){
      el.textContent=`0 short${appendText}`;
      return;
    }
    /* SHORTFALL_MESSAGING_V2
       Hard shorts collapse to one red failure line; don't show a theoretical daily-plan
       bridge that cannot actually succeed. Recoverable shortages keep a concise red+yellow
       two-line pattern with the exact raw-material deficit. */
    if(hard>0){
      const hardLine=`${fmt(hard)} ${resourceName} still missing · max Realm capacity exhausted`;
      el.innerHTML=`<span class="hardShort">${hardLine}</span>${appendText?`<span>${appendText}</span>`:''}`;
      return;
    }
    /* RECOVERABLE_SHORTFALL_REFRESH_PLAN_V1
       Recoverable resource cards show the exact material gap and additional tool count.
       Once the combined daily Realm recommendation is known later in updateCalculator(),
       the yellow bridge line is replaced with that resource's actionable refreshes/day. */
    const line1=`${fmt(short)} ${resourceName} short${runsToCover?` · +${fmt(runsToCover)} ${itemName}`:''}`;
    let line2='';
    if(extraRuns>0 && per>0){
      line2=`${fmt(runsToCover)} ${itemName} can cover`;
    }
    el.dataset.shortfallTools=String(runsToCover||0);
    el.dataset.shortfallItem=itemName;
    el.dataset.shortfallResource=resourceName;
    el.innerHTML=`<span class="planShort">${line1}</span>${line2?`<span class="realmBridge">${line2}</span>`:''}${appendText?`<span>${appendText}</span>`:''}`;
  }

  let lastAstralRenderKey='';
  let lastPrimostarRewardRenderKey='';
  function renderAstralPact(totalStars){
    const stars=Math.max(0,Math.floor(Number(totalStars)||0));
    const renderKey=String(stars);
    if(renderKey===lastAstralRenderKey) return;
    lastAstralRenderKey=renderKey;
    const totals=Object.fromEntries(ASTRAL_ORDER.map(k=>[k,0]));
    let unlocked=0;
    for(const [threshold,key,value] of ASTRAL_PACT_NODES){
      if(threshold>stars) break;
      totals[key]=(totals[key]||0)+value;
      unlocked++;
    }
    const box=$('astralRewardTotals');
    if(box){
      box.innerHTML=ASTRAL_ORDER.map(key=>`<span>${ASTRAL_LABELS[key]}<b>+${fmt(totals[key]||0)}%</b></span>`).join('');
    }
    const next=ASTRAL_PACT_NODES.find(([threshold])=>threshold>stars);
    const count=$('astralRewardCount');
    if(count){
      const s1Unlocked=ASTRAL_PACT_NODES.slice(0,40).filter(([threshold])=>threshold<=stars).length;
      const seasonText=stars<=480?`${s1Unlocked} of 40 documented S1 nodes unlocked`:`${unlocked} of ${ASTRAL_PACT_NODES.length} documented S1–S2 nodes unlocked`;
      const nextText=next?` · next: ${fmt(next[0])} → ${ASTRAL_LABELS[next[1]]} +${next[2]}%`:' · all documented S1–S2 nodes unlocked';
      count.textContent=`${fmt(stars)} projected total Primostars · ${seasonText}${nextText}.`;
    }
  }

  /* PRIMOSTAR_REWARD_REFERENCE_V2
     Checkmarks mean actually reached now, never merely targeted/projected.
     Season 2 rows stay hidden until the live calculator season is actually S2. */
  function renderPrimostarRewardReference(currentTotalStars,projectedTotalStars=currentTotalStars){
    const currentStars=Math.max(0,Math.floor(Number(currentTotalStars)||0));
    const projectedStars=Math.max(currentStars,Math.floor(Number(projectedTotalStars)||0));
    const rewardRenderKey=`${activeCalcConfig().key}|${currentStars}|${projectedStars}`;
    if(rewardRenderKey===lastPrimostarRewardRenderKey) return;
    lastPrimostarRewardRenderKey=rewardRenderKey;
    const host=$('primostarRewardSeasons');
    const intro=$('primostarRewardsIntro');
    if(!host) return;
    const cfg=activeCalcConfig();
    const s1Nodes=ASTRAL_PACT_NODES.slice(0,40);
    const visibleNodes=cfg.key==='s2'?ASTRAL_PACT_NODES:s1Nodes;
    // The result card is a season-end projection, so the highlighted "next" reward must
    // be the first threshold AFTER the projected total, not merely the next reward after
    // today's current total. Otherwise a 920 projection could misleadingly say "next 305".
    const nextIndex=visibleNodes.findIndex(([threshold])=>threshold>projectedStars);
    const nextReward=visibleNodes.find(([threshold])=>threshold>projectedStars);
    const groups=[{title:'Witching Hours',nodes:s1Nodes,offset:0}];
    if(cfg.key==='s2') groups.push({title:'Crossed Paths',nodes:ASTRAL_PACT_NODES.slice(40),offset:40});
    const row=(node,index)=>{
      const [threshold,key,value]=node;
      const projected=threshold>currentStars&&threshold<=projectedStars;
      const state=threshold<=currentStars?'reached':projected?'projected':index===nextIndex?'next':'future';
      return `<div class="primostarRewardRow ${state}"><span class="rewardThreshold">${fmt(threshold)}</span><span class="rewardName">${ASTRAL_LABELS[key]||key}</span><span class="rewardValue">+${fmt(value)}%</span></div>`;
    };
    // RESOURCE_TOOLS_REWARD_LAYOUT_V1: long reward tables use two vertical columns on desktop.
    const rewardLists=(group)=>{
      if(group.nodes.length<=20) return `<div class="primostarRewardList">${group.nodes.map((node,i)=>row(node,group.offset+i)).join('')}</div>`;
      const split=Math.ceil(group.nodes.length/2);
      const left=group.nodes.slice(0,split);
      const right=group.nodes.slice(split);
      return `<div class="primostarRewardColumns"><div class="primostarRewardList">${left.map((node,i)=>row(node,group.offset+i)).join('')}</div><div class="primostarRewardList">${right.map((node,i)=>row(node,group.offset+split+i)).join('')}</div></div>`;
    };
    host.innerHTML=groups.map(group=>`<section class="primostarRewardSeason"><h4>${group.title}</h4>${rewardLists(group)}</section>`).join('');
    if(intro){
      const projectedCount=visibleNodes.filter(([threshold])=>threshold>currentStars&&threshold<=projectedStars).length;
      if(projectedStars>currentStars){
        const projectionText=`${fmt(currentStars)} current · ${fmt(projectedStars)} projected`;
        intro.textContent=nextReward
          ? `${projectionText} · ${fmt(projectedCount)} more reward${projectedCount===1?'':'s'} projected · next after projection at ${fmt(nextReward[0])}: ${ASTRAL_LABELS[nextReward[1]]} +${fmt(nextReward[2])}%.`
          : `${projectionText} · ${fmt(projectedCount)} more reward${projectedCount===1?'':'s'} projected · all currently available Astral Pact rewards covered.`;
      }else{
        intro.textContent=nextReward
          ? `${fmt(currentStars)} current · next reward at ${fmt(nextReward[0])}: ${ASTRAL_LABELS[nextReward[1]]} +${fmt(nextReward[2])}%.`
          : `${fmt(currentStars)} current · all currently available Astral Pact rewards reached.`;
      }
    }
  }

  function optimizerReserveSummary(resources,cfg){
    if(cfg.key!=='s1') return '';
    const reserveKinds=[];
    if((resources?.s2SkillReserve?.target||0)>0) reserveKinds.push('Skill');
    if((resources?.s2RelicSandReserve?.target||0)>0) reserveKinds.push('Relic');
    if((resources?.s2FantomonTreatReserve?.target||0)>0) reserveKinds.push('Fantomon');
    return reserveKinds.length
      ? `Spend surplus first · minimize reacquisition effort · S2 ${reserveKinds.join(' + ')} reserve${reserveKinds.length>1?'s':''} protected`
      : 'Spend surplus first · minimize reacquisition effort · no S2 resource reserve';
  }

  function renderCalculatorSeasonChrome(cfg){
    renderLocalTimeLabels();
    $('seasonDeadlineLabel').textContent=`${cfg.name} ends`;
    $('seasonDeadlineDate').textContent=localDeadlineLabel(cfg.end,cfg.key==='s2');
    $('historicalStarsLabel').textContent='Season 1 Primostars';
    $('projectionNote').textContent=`Uses exact server resets (${nextResetLocalLabel()} on this device); future free 2-hour reset boosts are included automatically.`;
    if($('astralBonusReference')) $('astralBonusReference').hidden=false;
    const s2Presets=$('s2TargetPresets'),s2Gates=$('s2ProgressionGates'),seasonHint=$('seasonRulesHint');
    if(s2Presets) s2Presets.hidden=cfg.key!=='s2';
    if(s2Gates) s2Gates.hidden=cfg.key!=='s2';
    if(seasonHint) seasonHint.hidden=cfg.key!=='s2';
    if(s2Presets){
      const currentTarget=Math.floor(n('targetStars',cfg.key==='s2'?680:200));
      s2Presets.querySelectorAll('[data-s2-target]').forEach(btn=>btn.classList.toggle('active',Number(btn.dataset.s2Target)===currentTarget));
    }
    const setInputMax=(id,max)=>{const el=$(id);if(!el)return;if(Number.isFinite(max))el.max=String(max);else el.removeAttribute('max');};
    if(cfg.key==='s2'){
      $('seasonRulesHint').innerHTML='<b>S2 scoring still starts at Lv.130:</b> +45 fixed · 27 score / Primostar · normal floor Lv.130 / Relics above +13 · weights Character 100, Gear 18, Skill 7, Relic 33, Fantomon 8. <b>Lv.120+</b> can use the planner now; while you are Lv.120–130 it runs a clearly labeled <b>Lv.131 unlock preview</b> for upgrade availability so stockpiled resources can be evaluated before full seasonal progression opens. No pre-130 Character score is awarded. Starter floor: Gear 130 · Skills 130 · Fantomons 130 · Relics +13.';
      const currentCaps=categoryInputCapsForCharacter(characterSnapshot(cfg).level,cfg);
      /* S2_SCORING_INPUT_FLOOR_V2: Character Lv.130 unlocks the planner; actual category
         inputs may still be below their score floors and must retain their real catch-up costs. */
      $('skillLevel').min='100'; setInputMax('skillLevel',currentCaps.skill); $('skillLevel').step='0.125';
      $('relicLevel').min='10'; setInputMax('relicLevel',currentCaps.relic); $('relicLevel').step='0.05';
      $('fantomonLevel').min='100'; setInputMax('fantomonLevel',currentCaps.fanto); $('fantomonLevel').step='0.25';
      if($('gearLevel')){$('gearLevel').min='100';setInputMax('gearLevel',currentCaps.gear);$('gearLevel').step='0.2';}
    } else {
      $('seasonRulesHint').innerHTML='Season 2 data is preloaded: <b>Material Realm reaches its S2 max at Lv.120</b>; Season Power scoring starts at Lv.130.';
      const currentCaps=categoryInputCapsForCharacter(characterSnapshot(cfg).level,cfg);
      $('skillLevel').min='100'; setInputMax('skillLevel',currentCaps.skill); $('skillLevel').step='0.125';
      $('relicLevel').min='10'; setInputMax('relicLevel',currentCaps.relic); $('relicLevel').step='0.05';
      $('fantomonLevel').min='100'; setInputMax('fantomonLevel',currentCaps.fanto); $('fantomonLevel').step='0.25';
      if($('gearLevel')){$('gearLevel').min='100';setInputMax('gearLevel',currentCaps.gear);$('gearLevel').step='0.2';}
    }
    // S2_AUTO_RESET_STALE_SNAPSHOT_V1: stale pre-S2 calculator state is never offered for reuse.
    // Load clean S2 defaults immediately so old seasonal levels/resources cannot leak into the new season.
    if(cfg.key==='s2' && snapshotSeason!==cfg.key){
      applyS2ScoringStartDefaults();
      snapshotSeason=cfg.key;
      snapshotAtMs=Date.now();
      snapshotCarry={ore:0,essence:0,sand:0,treat:0,exp:0};
      snapshotStateLoaded=true;
      saveState();
    }
    const mismatch=snapshotSeason!==cfg.key;
    $('calcSeasonNotice').hidden=!mismatch;
    $('calcResults').classList.toggle('rolloverBlocked',mismatch);
    if(mismatch){
      $('calcSeasonNoticeTitle').textContent=`${cfg.name} is live — refresh the saved snapshot`;
      $('calcSeasonNoticeText').textContent=cfg.key==='s2'
        ? `Your saved calculator state is from ${CALC_SEASONS[snapshotSeason]?.name||'the prior season'}. S2 Season Power does not unlock until Lv.130, so this scoring planner intentionally ignores the Lv.100→130 catch-up phase. At Lv.130, enter your actual carried Primostars/resources and current progression, then confirm the S2 snapshot.`
        : `Your saved calculator state is from ${CALC_SEASONS[snapshotSeason]?.name||'the prior season'}. Update Character level/EXP, Gear, Skills, Relics, Fantomons, resources/Cart rates and carried Primostars, then confirm. The site intentionally refuses to assume how the seasonal reset changed your account.`;
      $('confirmSeasonSnapshot').textContent=`Use entries as ${cfg.name} snapshot`;
    }
    return mismatch;
  }
  function clearS2PreScoring(cfg){
    const current=characterSnapshot(cfg),p=projectCharacter(cfg);
    $('seasonRemaining').textContent=formatRemaining(remainingHoursAt(Date.now(),cfg));
    $('projectedCharacter').value=`Lv.${p.level} · ${(p.pct*100).toFixed(1)}%`;
    $('resultProjectedCharacter').textContent=`Lv.${p.level} (${(p.pct*100).toFixed(1)}%)`;
    $('currentStars').textContent='—'; $('currentScoreNow').textContent='—'; $('summaryOptimizedScore').textContent='—'; $('desiredScore').textContent='—';
    $('targetMessage').hidden=false; $('targetMessage').classList.remove('danger'); $('targetMessage').classList.add('warning','caution');
    $('targetMessage').textContent=`Season Power scoring still uses the Lv.${cfg.scoreFloor} baseline, but forward planning becomes available at Lv.${S2_PLANNER_START_LEVEL}. Current Lv.${current.level} is below that planning threshold, so the calculator stays paused until Lv.${S2_PLANNER_START_LEVEL}.`;
    if($('targetStatus')){$('targetStatus').textContent='locked';$('targetStatus').classList.remove('notMet');}
    $('optimizerSummary').textContent=`Return at Lv.${S2_PLANNER_START_LEVEL} and enter your actual state. From there the calculator projects EXP and resources through the Lv.${cfg.scoreFloor} Season Power baseline and season end.`;
    $('optimizedScore').textContent='—';
    $('materialRealmRecommendation').hidden=true;
    renderRealmToolProjection(cfg);
  }

  function clearS2ProjectedAtFloor(cfg,p=projectCharacter(cfg)){
    const historical=Math.max(0,Math.floor(n('historicalStars',0)));
    const carried=historical+cfg.starBase;
    const seasonEndP=projectCharacter(cfg);
    $('seasonRemaining').textContent=formatRemaining(seasonEndP.hours);
    $('projectedCharacter').value=`Lv.${seasonEndP.level} · ${(seasonEndP.pct*100).toFixed(1)}%`;
    $('resultProjectedCharacter').textContent=`Lv.${p.level} (${(p.pct*100).toFixed(1)}%)`;
    $('currentStars').textContent=fmt(carried);
    $('currentScoreNow').textContent='0';
    $('summaryOptimizedScore').textContent='—';
    $('desiredScore').textContent='—';
    if($('recommendedBreakdownSection')) $('recommendedBreakdownSection').hidden=true;
    $('targetMessage').hidden=false;
    $('targetMessage').classList.remove('danger');
    $('targetMessage').classList.add('warning','caution');
    $('targetMessage').textContent=`Projected season-end Character is Lv.${p.level}. The S2 optimizer stays paused until the projection reaches Lv.131, so a Lv.130-or-lower projection never runs the heavy upgrade search.`;
    if($('targetStatus')){$('targetStatus').textContent='waiting for Lv.131';$('targetStatus').classList.remove('notMet');}
    $('optimizerSummary').textContent='No Gear / Skill / Relic / Fantomon optimization runs while projected season-end Character remains Lv.130 or lower.';
    $('optimizedScore').textContent='—';
    ['targetSkills','targetRelics','targetFantomons'].forEach(id=>{if($(id))$(id).textContent='—';});
    GEAR_OUTPUT_IDS.forEach(id=>{if($(id))$(id).textContent='—';});
    ['oreCost','essenceCost','sandCost','treatCost'].forEach(id=>{if($(id))$(id).textContent='0';});
    ['oreBalance','essenceBalance','sandBalance','treatBalance','oreToolBalance','essenceToolBalance','sandToolBalance'].forEach(hidePlanBalance);
    $('materialRealmRecommendation').hidden=true;$('materialRealmRecommendation').textContent='';
    $('secondaryCostNote').hidden=true;$('secondaryCostNote').textContent='';
    $('milestoneNote').hidden=true;$('milestoneNote').textContent='';
    renderAstralPact(carried);
    renderPrimostarRewardReference(carried,carried);
    saveState();
    const calcSection=$('calculatorSection');
    if(calcSection) calcSection.dataset.lastSolveMs='0.0';
  }

  function clearCalcForRollover(cfg){
    $('seasonRemaining').textContent=formatRemaining(remainingHoursAt(Date.now(),cfg));
    $('projectedCharacter').value='Update snapshot';
    $('resultProjectedCharacter').textContent='Update snapshot';
    $('currentStars').textContent='—'; $('currentScoreNow').textContent='—'; $('summaryOptimizedScore').textContent='—'; $('desiredScore').textContent='—';
    $('targetMessage').hidden=false; $('targetMessage').classList.add('warning');
    $('targetMessage').textContent=`${cfg.name} rules are ready, but the calculator is paused until you confirm a fresh ${cfg.name} snapshot.`;
    if($('targetStatus')){$('targetStatus').textContent='—';$('targetStatus').classList.remove('notMet');}
    $('optimizerSummary').textContent='Update all current-state fields above, then use the season snapshot button.';
    $('optimizedScore').textContent='—';
    $('materialRealmRecommendation').hidden=true;
  }
  function confirmCurrentSeasonSnapshot(){
    const cfg=activeCalcConfig();
    // A persisted 200-ish S1 target is not useful in S2. Change it only at explicit rollover confirmation;
    // preserve any target the user already raised for S2.
    if(cfg.key==='s2' && $('targetStars')){
      const target=Number($('targetStars').value);
      if(!Number.isFinite(target) || target<=480) $('targetStars').value=String(S2_SCORING_START_DEFAULTS.targetStars);
    }
    snapshotSeason=cfg.key; snapshotAtMs=Date.now(); snapshotCarry={ore:0,essence:0,sand:0,treat:0,exp:0}; snapshotStateLoaded=true;
    saveState(); renderCalculatorSeasonChrome(cfg); updateCalculator();
  }

  function updateGearLockUI(){
    const btn=$('gearLockButton');
    if(!btn) return;
    btn.classList.toggle('locked',gearLocked);
    btn.setAttribute('aria-pressed', String(gearLocked));
    btn.textContent = gearLocked ? '🔒 Gear Locked' : '🔓 Lock Gear';
    $('gearLockNote').textContent = gearLocked
      ? 'Gear is locked at the current five slot levels. The optimizer cannot recommend any Gear increase; it must solve the target through other available progression.'
      : 'Gear is unlocked. The optimizer can raise Gear when it is the most resource-efficient path.';
  }


  let maxAchievableState={fingerprint:'',routine:null,hard:null};
  function maxAchievableFingerprint(){
    return JSON.stringify({
      inputs:INPUT_IDS.filter(id=>id!=='targetStars').map(id=>$(id)?.value??''),
      checks:CHECK_IDS.map(id=>!!$(id)?.checked),
      gearLocked,snapshotSeason
    });
  }
  function resetMaxAchievableUi(){
    maxAchievableState={fingerprint:'',routine:null,hard:null};
    const btn=$('findMaxStars'),status=$('maxAchievableStatus');
    if(btn){btn.disabled=false;btn.textContent='Find max achievable';}
    if(status) status.textContent='Shows the maximum with your selected daily Realm plan and the hard maximum using all remaining Realm capacity.';
  }
  function buildMaxAchievableSnapshot(){
    const cfg=activeCalcConfig();
    if(snapshotSeason!==cfg.key) return null;
    const p=projectCharacter(cfg);
    const upgradeP=projectCharacterTo(upgradeFinishCutoffMs(cfg),cfg);
    p.upgradeCapLevel=upgradeP.level;p.upgradeCapPct=upgradeP.pct;
    const currentCharacter=p.current||characterSnapshot(cfg);
    if(cfg.key==='s2' && currentCharacter.level<S2_PLANNER_START_LEVEL) return null;
    const projectedResourceTotals=projectedResources(p.hours,cfg);
    const baseResources=projectedResourceTotals;
    const currentCaps=categoryInputCapsForCharacter(currentCharacter.level,cfg);
    const normalInputFloor=100;
    const relicInputFloor=10;
    const gearState=gearStateFromUser(cfg,currentCaps.gear,cfg.key==='s2'?130:143);
    const gear=gearState.levels;
    const skillState=categoryStateFromUser('skillLevel','exactSkillLevels',8,normalInputFloor,currentCaps.skill,cfg.scoreFloor,cfg.weights.skill,cfg.key==='s2'?130:122);
    const relicState=categoryStateFromUser('relicLevel','exactRelicLevels',20,relicInputFloor,currentCaps.relic,cfg.relicFloor,cfg.weights.relic,cfg.key==='s2'?13:13);
    const fantoState=categoryStateFromUser('fantomonLevel','exactFantoLevels',4,normalInputFloor,currentCaps.fanto,cfg.scoreFloor,cfg.weights.fanto,cfg.key==='s2'?130:130);
    const baselineScore=characterScore(p,cfg)+gearScore(gear,cfg)+skillState.score+relicState.score+fantoState.score;
    const historical=Math.max(0,Math.floor(n('historicalStars',0)));
    return {cfg,p,baseResources,baselineScore,historical,baselineStars:historical+cfg.starBase+Math.floor(baselineScore/cfg.scorePerStar)};
  }
  function findMaxAchievableStars(){
    const btn=$('findMaxStars'),status=$('maxAchievableStatus');
    if(!btn||!status) return;
    const fingerprint=maxAchievableFingerprint();
    if(maxAchievableState.fingerprint===fingerprint && Number.isFinite(maxAchievableState.hard)){
      $('targetStars').value=String(maxAchievableState.hard);
      markManualSnapshot('targetStars');
      scheduleCalculatorUpdate(0);
      return;
    }
    const snap=buildMaxAchievableSnapshot();
    if(!snap){ status.textContent='Confirm the current-season snapshot first.'; return; }
    btn.disabled=true;btn.textContent='Calculating…';status.textContent='Searching reachable Primostar breakpoints…';
    setTimeout(()=>{
      try{
        const solveCache=new Map();
        const solveStars=stars=>{
          const key=Math.max(snap.baselineStars,Math.floor(stars));
          if(solveCache.has(key)) return solveCache.get(key);
          const desired=Math.max(0,(key-snap.historical-snap.cfg.starBase)*snap.cfg.scorePerStar);
          const result=solveTargetWithAutoStamina(snap.baselineScore,desired,snap.p,snap.baseResources,snap.cfg);
          solveCache.set(key,result);
          return result;
        };
        const hardFundable=stars=>!!solveStars(stars).plan;
        const routineFundable=stars=>{
          const plan=solveStars(stars).plan;
          return !!plan && candidateRealmStage(plan)<=1;
        };
        const upperLimit=snap.cfg.key==='s1'?1200:5000;
        let hardLo=snap.baselineStars,hardHi=Math.max(hardLo+1,Math.floor(n('targetStars',hardLo))+1),step=Math.max(8,hardHi-hardLo);
        while(hardHi<upperLimit && hardFundable(hardHi)){
          hardLo=hardHi;step*=2;hardHi=Math.min(upperLimit,hardHi+step);
        }
        if(hardHi===upperLimit && hardFundable(hardHi)) hardLo=hardHi;
        else{
          let lo=hardLo+1,hi=hardHi-1;
          while(lo<=hi){const mid=(lo+hi)>>1;if(hardFundable(mid)){hardLo=mid;lo=mid+1;}else hi=mid-1;}
        }
        const hard=hardLo;
        let routineLo=snap.baselineStars,routineHi=hard;
        while(routineLo<routineHi){
          const mid=Math.ceil((routineLo+routineHi)/2);
          if(routineFundable(mid)) routineLo=mid; else routineHi=mid-1;
        }
        const routine=routineLo;
        maxAchievableState={fingerprint,routine,hard};
        status.innerHTML=`Selected daily plan max: <strong>${fmt(routine)}</strong> · Hard Realm-cap max: <strong>${fmt(hard)}</strong>`;
        btn.disabled=false;btn.textContent=`Use ${fmt(hard)} target`;
      }catch(err){
        console.error(err);resetMaxAchievableUi();status.textContent='Could not calculate the ceiling from the current inputs.';
      }
    },0);
  }

  /* FINISH_EARLY_MAX_FAST_NOEXTRA_V3
     Max answers: how early can the selected target be secured WITHOUT any additional
     Realm purchases beyond the user's already-configured daily Realm plan. Configured
     Shop Buyouts/day and configured daily Realm purchases remain part of the user's normal
     projection; candidate-invented extra Realm refreshes are not allowed.

     This uses the same exact owned/projected-pool feasibility proof already used inside
     searchPlans(), but skips the expensive nested optimizer scan. Each half-day probe only
     builds the reachable option lists and checks the independently affordable maxima for
     Gear / Skills / Relics / Fantomons across the calculator's legal Stamina strategies.
     After binary search finds the final half-day value, the full optimizer runs ONCE to
     render the normal result card. */
  function finishEarlyNoExtraPossible(){
    const cfg=activeCalcConfig();
    if(snapshotSeason!==cfg.key) return false;
    if(cfg.key==='s2'){
      const required=s2RequiredPlannerInputs();
      if(!required.hasBed||!required.hasAllCart) return false;
    }

    const p=projectCharacterTo(upgradeFinishCutoffMs(cfg),cfg);
    if(cfg.key==='s2' && p.level<=cfg.scoreFloor) return false;
    p.upgradeCapLevel=p.level;
    p.upgradeCapPct=p.pct;

    const currentCharacter=p.current||characterSnapshot(cfg);
    const currentCaps=categoryInputCapsForCharacter(currentCharacter.level,cfg);
    const gearState=gearStateFromUser(cfg,currentCaps.gear,cfg.key==='s2'?130:143);
    const skillState=categoryStateFromUser('skillLevel','exactSkillLevels',8,100,currentCaps.skill,cfg.scoreFloor,cfg.weights.skill,cfg.key==='s2'?130:122);
    const relicState=categoryStateFromUser('relicLevel','exactRelicLevels',20,10,currentCaps.relic,cfg.relicFloor,cfg.weights.relic,cfg.key==='s2'?13:13);
    const fantoState=categoryStateFromUser('fantomonLevel','exactFantoLevels',4,100,currentCaps.fanto,cfg.scoreFloor,cfg.weights.fanto,cfg.key==='s2'?130:130);
    const baselineScore=characterScore(p,cfg)+gearScore(gearState.levels,cfg)+skillState.score+relicState.score+fantoState.score;
    const historical=Math.max(0,Math.floor(n('historicalStars',0)));
    const targetStars=Math.max(cfg.starBase+historical,Math.floor(n('targetStars',cfg.key==='s2'?680:200)));
    const desired=Math.max(0,(targetStars-historical-cfg.starBase)*cfg.scorePerStar);
    if(baselineScore>=desired-1e-9) return true;

    const ctx=createPlanningContext(baselineScore,desired,p,cfg);
    const baseResources=projectedResources(p.hours,cfg);
    const total=Math.max(0,Math.floor(baseResources.staminaNodes||0));
    const map=baseResources.yields?.map||{};
    const empty={ore:0,essence:0,sand:0,rolla:0,unassigned:0};
    const allocations=[];
    if(!baseResources.yields?.mapReady||total<=0){
      allocations.push({...empty,unassigned:total});
    }else if(staminaMode()==='auto'){
      for(const key of ['ore','essence','sand']){
        if((Number(map[key])||0)>0) allocations.push({...empty,[key]:total});
      }
    }else{
      const key=staminaMode();
      allocations.push((Number(map[key])||0)>0?{...empty,[key]:total}:{...empty,unassigned:total});
    }
    if(!allocations.length) allocations.push({...empty,unassigned:total});

    const highestAffordable=(options,budget,costKey='cost',secondaryBudget=Infinity,secondaryKey='')=>{
      let best=Array.isArray(options)&&options.length?options[0]:null;
      for(const option of (options||[])){
        const primary=Math.max(0,Number(option?.[costKey])||0);
        const secondary=secondaryKey?Math.max(0,Number(option?.[secondaryKey])||0):0;
        if(primary<=budget+0.5 && secondary<=secondaryBudget+0.5) best=option;
        else if(primary>budget+0.5) break;
      }
      return best;
    };

    for(const allocation of allocations){
      const resources=applyStaminaAllocation(baseResources,allocation,cfg);
      const refinedBudget=resources.refinedTracked?Math.max(0,Number(resources.refined)||0):Infinity;
      const go=highestAffordable(ctx.gearOptions,plannedToolAcquisitionSupply('ore',resources,cfg),'oreCost',refinedBudget,'refinedCost');
      const so=highestAffordable(ctx.cats.skillOptions,plannedToolAcquisitionSupply('essence',resources,cfg));
      const ro=highestAffordable(ctx.cats.relicOptions,plannedToolAcquisitionSupply('sand',resources,cfg));
      const fo=highestAffordable(ctx.cats.fantoOptions,Math.max(0,Number(resources.treat)||0));
      if(!go||!so||!ro||!fo) continue;
      const maxScore=ctx.charScore+(Number(go.score)||0)+(Number(so.score)||0)+(Number(ro.score)||0)+(Number(fo.score)||0);
      if(maxScore>=desired-1e-9) return true;
    }
    return false;
  }

  function findMaxFinishEarly(){
    const btn=$('finishEarlyMax'),input=$('finishEarlyDays');
    if(!btn||!input||btn.disabled) return;
    const cfg=activeCalcConfig();
    const original=String(input.value||'0');
    const halfDayMs=12*60*60*1000;
    const maxHalfSteps=Math.max(0,Math.floor((cfg.end.getTime()-Date.now())/halfDayMs));
    btn.disabled=true;
    btn.textContent='…';
    btn.setAttribute('aria-busy','true');
    clearTimeout(calculatorUpdateTimer);
    calculatorUpdateTimer=null;
    setTimeout(()=>{
      try{
        input.value='0';
        if(!finishEarlyNoExtraPossible()){
          input.value=original;
          updateCalculator();
          btn.title='The selected target is not reachable without extra Realm purchases beyond your configured routine.';
          return;
        }
        let lo=0,hi=maxHalfSteps;
        while(lo<hi){
          const mid=Math.ceil((lo+hi)/2);
          input.value=String(mid/2);
          if(finishEarlyNoExtraPossible()) lo=mid;
          else hi=mid-1;
        }
        input.value=String(lo/2);
        resetMaxAchievableUi();
        saveState();
        // One full solve only, after the fast feasibility search has found the cutoff.
        updateCalculator();
        btn.title=lo>0
          ? `Maximum no-extra-purchase finish-early value: ${lo/2} days. Uses your configured Realm/Shop routine but no additional recommended Realm purchases.`
          : 'The current target needs the full remaining season without extra Realm purchases.';
      }catch(err){
        console.error('FINISH_EARLY_MAX_FAST_NOEXTRA_V3',err);
        input.value=original;
        updateCalculator();
        btn.title='Could not calculate the no-extra-purchase maximum from the current inputs.';
      }finally{
        btn.disabled=false;
        btn.textContent='Max';
        btn.removeAttribute('aria-busy');
      }
    },0);
  }

  /* SMART_BALANCE_RAW_CEILING_V1
     The requested Primostar value is a minimum goal. If projected RAW income alone can
     reach a higher whole-Primostar breakpoint, recommend that higher breakpoint without
     touching Realm tools. Tools are only unlocked when raw cannot reach the requested goal. */
  function smartBalanceHighestAffordable(options,budget,costKey='cost',secondaryBudget=Infinity,secondaryKey=''){
    let best=Array.isArray(options)&&options.length?options[0]:null;
    for(const option of (options||[])){
      const primary=Math.max(0,Number(option?.[costKey])||0);
      const secondary=secondaryKey?Math.max(0,Number(option?.[secondaryKey])||0):0;
      if(primary<=budget+0.5 && secondary<=secondaryBudget+0.5) best=option;
      else if(primary>budget+0.5) break;
    }
    return best;
  }
  function smartBalanceRawCeiling(baseScore,p,baseResources,cfg,historical){
    // Large structural target only expands Gear options; actual affordability below is
    // still limited strictly by projected raw resources and verified progression gates.
    const ctx=createPlanningContext(baseScore,1_000_000,p,cfg);
    const total=Math.max(0,Math.floor(baseResources?.staminaNodes||0));
    const empty={ore:0,essence:0,sand:0,rolla:0,unassigned:0};
    const map=baseResources?.yields?.map||{};
    const allocations=[];
    if(total<=0 || !baseResources?.yields?.mapReady){
      allocations.push({...empty,unassigned:total});
    }else if(staminaMode()==='auto'){
      for(const key of ['ore','essence','sand']) if((Number(map[key])||0)>0) allocations.push({...empty,[key]:total});
      if(!allocations.length) allocations.push({...empty,unassigned:total});
    }else{
      allocations.push(allocateStaminaForPlan(null,baseResources,cfg,p));
    }

    let best=null;
    for(const allocation of allocations){
      const resources=applyStaminaAllocation(baseResources,allocation,cfg);
      const refinedBudget=resources.refinedTracked?Math.max(0,Number(resources.refined)||0):Infinity;
      const go=smartBalanceHighestAffordable(ctx.gearOptions,Math.max(0,Number(resources.ore)||0),'oreCost',refinedBudget,'refinedCost');
      const so=smartBalanceHighestAffordable(ctx.cats.skillOptions,Math.max(0,Number(resources.essence)||0));
      const ro=smartBalanceHighestAffordable(ctx.cats.relicOptions,Math.max(0,Number(resources.sand)||0));
      const fo=smartBalanceHighestAffordable(ctx.cats.fantoOptions,Math.max(0,Number(resources.treat)||0));
      if(!go||!so||!ro||!fo) continue;
      const score=ctx.charScore+go.score+so.score+ro.score+fo.score;
      const stars=Math.max(0,Math.floor(historical))+cfg.starBase+Math.floor(score/cfg.scorePerStar);
      const candidate={stars,score,allocation,resources};
      if(!best || candidate.stars>best.stars || (candidate.stars===best.stars && candidate.score>best.score)) best=candidate;
    }
    return best||{stars:Math.max(0,Math.floor(historical))+cfg.starBase+Math.floor(baseScore/cfg.scorePerStar),score:baseScore,allocation:{...empty,unassigned:total},resources:baseResources};
  }

  let lastRequestedTargetStars=null;
  let lastEffectiveTargetStars=null;

  /* GOAL_SWITCH_CACHE_V2
     Changing Target Primostars does not change the account snapshot. Reuse the expensive
     raw-only ceiling and any exact target solution already computed while every non-target
     input remains identical. New goals still build their normal target-specific context. */
  let goalSwitchCache={fingerprint:'',rawCeiling:null,solutions:new Map()};
  function goalSwitchFingerprint(cfg,baseScore){
    return JSON.stringify({
      season:cfg.key,
      snapshotAtMs,
      gearLocked,
      baseScore:Math.round((Number(baseScore)||0)*1000)/1000,
      inputs:INPUT_IDS.filter(id=>id!=='targetStars').map(id=>$(id)?.value??''),
      checks:CHECK_IDS.map(id=>!!$(id)?.checked)
    });
  }
  function goalSwitchPlanningState(baseScore,p,baseResources,cfg,historical){
    const fingerprint=goalSwitchFingerprint(cfg,baseScore);
    if(goalSwitchCache.fingerprint===fingerprint) return goalSwitchCache;
    const rawCeiling=smartBalanceRawCeiling(baseScore,p,baseResources,cfg,historical);
    goalSwitchCache={fingerprint,rawCeiling,solutions:new Map()};
    return goalSwitchCache;
  }

  /* S2_REQUIRED_INPUT_GUARD_V1
     Avoid launching the expensive target search from an empty production snapshot.
     Saved materials and Material Realm purchases are allowed to remain zero, but the
     S2 optimizer needs real Bed EXP plus all four Cart/hr production rates. */
  function s2RequiredPlannerInputs(){
    const bed=Math.max(0,parseCompactNumber($('bedExp')?.value,0));
    const cartInputs=[['oreRate','Raw Ore Cart/hr'],['essenceRate','Skill Essence Cart/hr'],['sandRate','Chrono Sand Cart/hr'],['treatRate','Fantomon Treats Cart/hr']];
    const cartRates=cartInputs.map(([id])=>Math.max(0,parseCompactNumber($(id)?.value,0)));
    const missingCart=cartInputs.filter((_,i)=>cartRates[i]<=0).map(([,label])=>label);
    return {bed,cartRates,missingCart,hasBed:bed>0,hasAllCart:missingCart.length===0};
  }
  function clearS2ForRequiredPlannerInputs(cfg,requirements,p=null){
    const missing=[];
    if(!requirements.hasBed) missing.push('Bed EXP/hr');
    missing.push(...requirements.missingCart);
    // Character projection is lightweight and only needs Bed EXP; keep it available while
    // the material-production guard continues to block the expensive Primostar optimizer.
    if(requirements.hasBed && p){
      if($('seasonRemaining')) $('seasonRemaining').textContent=formatRemaining(p.hours);
      if($('projectedCharacter')) $('projectedCharacter').value=`Lv.${p.level} · ${(p.pct*100).toFixed(1)}%`;
      if($('resultProjectedCharacter')) $('resultProjectedCharacter').textContent=`Lv.${p.level} (${(p.pct*100).toFixed(1)}%)`;
    }else{
      if($('projectedCharacter')) $('projectedCharacter').value='Enter Bed EXP';
      if($('resultProjectedCharacter')) $('resultProjectedCharacter').textContent='—';
    }
    ['currentStars','currentScoreNow','summaryOptimizedScore','desiredScore','optimizedScore'].forEach(id=>{if($(id))$(id).textContent='—';});
    if($('targetStatus')){
      $('targetStatus').textContent='waiting for production inputs';
      $('targetStatus').classList.remove('notMet');
    }
    if($('targetMessage')){
      $('targetMessage').hidden=false;
      $('targetMessage').classList.remove('danger');
      $('targetMessage').classList.add('warning','caution');
      $('targetMessage').textContent=`Enter ${missing.join(' and ')} to run the S2 optimizer. Saved materials and Material Realm purchases can stay at 0.`;
    }
    if($('optimizerSummary')){
      $('optimizerSummary').hidden=false;
      $('optimizerSummary').textContent='The heavy Primostar search is paused until Bed EXP and all four Cart production rates are entered.';
    }
    if($('recommendedBreakdownSection')) $('recommendedBreakdownSection').hidden=true;
    ['targetSkills','targetRelics','targetFantomons'].forEach(id=>{if($(id))$(id).textContent='—';});
    GEAR_OUTPUT_IDS.forEach(id=>{if($(id))$(id).textContent='—';});
    ['oreCost','essenceCost','sandCost','treatCost'].forEach(id=>{if($(id))$(id).textContent='0';});
    ['oreBalance','essenceBalance','sandBalance','treatBalance','oreToolBalance','essenceToolBalance','sandToolBalance'].forEach(hidePlanBalance);
    if($('materialRealmRecommendation')){$('materialRealmRecommendation').hidden=true;$('materialRealmRecommendation').textContent='';}
    if($('secondaryCostNote')){$('secondaryCostNote').hidden=true;$('secondaryCostNote').textContent='';}
    if($('milestoneNote')){$('milestoneNote').hidden=true;$('milestoneNote').textContent='';}
    const calcSection=$('calculatorSection');
    if(calcSection) calcSection.dataset.lastSolveMs='0.0';
    saveState();
  }

  function updateCalculator(){
    const perfStarted=performance.now();
    $('targetMessage')?.classList.remove('danger','caution');
    const cfg=activeCalcConfig();
    if(renderCalculatorSeasonChrome(cfg)){ clearCalcForRollover(cfg); return; }
    let p=null;
    if(cfg.key==='s2'){
      const required=s2RequiredPlannerInputs();
      // Bed EXP is the only production input required for Character level projection.
      if(!required.hasBed){ clearS2ForRequiredPlannerInputs(cfg,required); return; }
      p=projectCharacter(cfg);
      // Do not run the full Primostar/material optimizer until every Cart rate exists.
      if(!required.hasAllCart){ clearS2ForRequiredPlannerInputs(cfg,required,p); return; }
    }
    if(!p) p=projectCharacter(cfg);
    const seasonEndP=p;
    p=projectCharacterTo(upgradeFinishCutoffMs(cfg),cfg);
    if(cfg.key==='s2' && p.level<=cfg.scoreFloor){ clearS2ProjectedAtFloor(cfg,p); return; }
    const upgradeP=p;
    // Upgrade availability and score projection stop at the optional finish-early cutoff.
    p.upgradeCapLevel=upgradeP.level;
    p.upgradeCapPct=upgradeP.pct;
    const currentCharacter=p.current||characterSnapshot(cfg);
    const projectedResourceTotals=projectedResources(p.hours,cfg);
    renderRealmToolProjection(cfg);
    const baseResources=projectedResourceTotals;
    let resources=baseResources;
    const currentCaps=categoryInputCapsForCharacter(currentCharacter.level,cfg);
    const projectedCaps=optimizerCategoryCaps(p,cfg);
    const normalInputFloor=100;
    const relicInputFloor=10;
    const gearState=gearStateFromUser(cfg,currentCaps.gear,cfg.key==='s2'?130:143);
    const gear=gearState.levels;
    const skillState=categoryStateFromUser('skillLevel','exactSkillLevels',8,normalInputFloor,currentCaps.skill,cfg.scoreFloor,cfg.weights.skill,cfg.key==='s2'?130:122);
    const relicState=categoryStateFromUser('relicLevel','exactRelicLevels',20,relicInputFloor,currentCaps.relic,cfg.relicFloor,cfg.weights.relic,cfg.key==='s2'?13:13);
    const fantoState=categoryStateFromUser('fantomonLevel','exactFantoLevels',4,normalInputFloor,currentCaps.fanto,cfg.scoreFloor,cfg.weights.fanto,cfg.key==='s2'?130:130);
    const skill=skillState.avg,relic=relicState.avg,fanto=fantoState.avg;
    const exactChecks=[
      ['exactSkillLevels',8,normalInputFloor,currentCaps.skill,'Skills'],
      ['exactRelicLevels',20,relicInputFloor,currentCaps.relic,'Relics'],
      ['exactFantoLevels',4,normalInputFloor,currentCaps.fanto,'Fantomons'],
      ['exactGearLevels',5,normalInputFloor,currentCaps.gear,'Gear']
    ].map(([id,count,min,max,label])=>({label,...parseExactLevelInput(id,count,min,max)}));
    const exactStatus=$('exactProgressStatus');
    if(exactStatus){
      const invalid=exactChecks.filter(x=>x.active&&!x.valid),active=exactChecks.filter(x=>x.active&&x.valid);
      exactStatus.classList.toggle('inputWarning',invalid.length>0);exactStatus.classList.toggle('inputGood',invalid.length===0&&active.length>0);
      exactStatus.textContent=invalid.length?`Invalid exact input: ${invalid.map(x=>`${x.label} (${x.reason})`).join(' · ')}. Falling back to the averages above.`:active.length?`Using exact slot levels for: ${active.map(x=>x.label).join(', ')}.`:'Leave blank to keep using the balanced average model.';
    }
    const sharedParts={gear:gearScore(gear,cfg),skills:skillState.score,relics:relicState.score,fantomons:fantoState.score};
    const currentParts={character:characterScore(currentCharacter,cfg),...sharedParts};
    const projectedParts={character:characterScore(p,cfg),...sharedParts};
    const currentScoreNow=Object.values(currentParts).reduce((a,b)=>a+b,0);
    const baselineScore=Object.values(projectedParts).reduce((a,b)=>a+b,0);
    const historical=Math.max(0,Math.floor(n('historicalStars',0)));
    const targetStars=Math.max(cfg.starBase+historical,Math.floor(n('targetStars',cfg.key==='s2'?680:200)));
    const currentStarsNow=historical+cfg.starBase+Math.floor(currentScoreNow/cfg.scorePerStar);
    const baselineStars=historical+cfg.starBase+Math.floor(baselineScore/cfg.scorePerStar);
    const requestedDesired=Math.max(0,(targetStars-historical-cfg.starBase)*cfg.scorePerStar);
    // SMART_BALANCE_GOAL_STOP_V2: calculate raw-only upside for INFORMATION only.
    // The recommendation itself stops at the entered goal instead of spending surplus raw
    // materials merely because a higher raw-only ceiling exists.
    const goalState=goalSwitchPlanningState(baselineScore,p,baseResources,cfg,historical);
    const rawCeiling=goalState.rawCeiling;
    const projectedRawCeilingStars=Math.max(baselineStars,Math.floor(Number(rawCeiling?.stars)||baselineStars));
    const desired=requestedDesired;
    let solution=goalState.solutions.get(desired);
    if(!solution){
      solution=solveTargetWithAutoStamina(baselineScore,desired,p,baseResources,cfg);
      goalState.solutions.set(desired,solution);
    }
    let plan=solution.plan;
    const diagnosticPlan=solution.diagnostic||null;
    let resourceBlocked=false;
    resources=solution.resources;
    const staminaPlan=solution.allocation;
    // Strict sourcing still applies inside solveTargetWithAutoStamina/searchPlans:
    // raw first -> saved/already-planned Realm tools if needed -> extra purchases last.
    if(!plan&&diagnosticPlan){plan=diagnosticPlan;resourceBlocked=!diagnosticPlan.realmFeasible;}
    lastRequestedTargetStars=targetStars; lastEffectiveTargetStars=targetStars;

    $('seasonRemaining').textContent=formatRemaining(seasonEndP.hours);
    const pc=`Lv.${seasonEndP.level} · ${(seasonEndP.pct*100).toFixed(1)}%`;
    $('projectedCharacter').value=pc;
    const expEstimated=cfg.key==='s1'&&s1ProjectionUsesEstimatedExp(currentCharacter.level,seasonEndP.level);
    $('resultProjectedCharacter').textContent=`Lv.${p.level} (${(p.pct*100).toFixed(1)}%)`;
    $('projectionNote').textContent=expEstimated?`Exact reset timing (${nextResetLocalLabel()} locally) · late-S1 unknown EXP steps use the community-style ~1.83M/level plateau.`:`Uses exact server resets (${nextResetLocalLabel()} on this device); the free 2-hour speed-up is counted only when its checkbox is enabled and an actual reset occurs.`;
    if($('levelSummary')) $('levelSummary').textContent=`Skills ${formatAverage(skill)} · Relics +${formatAverage(relic)} · Fantomons ${formatAverage(fanto)} · Gear avg ${(gear.reduce((a,b)=>a+b,0)/5).toFixed(0)}`;

    const allocation=staminaPlan||resources.staminaAllocation||{ore:0,essence:0,sand:0,rolla:0,unassigned:resources.staminaNodes||0};
    const added=resources.staminaAdded||{ore:0,essence:0,sand:0,rolla:0};
    renderStaminaCurrentPlan(allocation,added,resources);
    const oreStam=added.ore?` · Stamina +${fmtCompact(added.ore)}`:'';
    const essStam=added.essence?` · Stamina +${fmtCompact(added.essence)}`:'';
    const sandStam=added.sand?` · Stamina +${fmtCompact(added.sand)}`:'';
    $('oreProjected').textContent=`Projected: ${fmtCompact(resources.ore)}${oreStam}`;
    const displayedEssence=Number(resources.essence)||0;
    $('essenceProjected').textContent=`Projected: ${fmtCompact(displayedEssence)}${essStam}`;
    const displayedSand=Number(resources.sand)||0;
    $('sandProjected').textContent=`Projected: ${fmtCompact(displayedSand)}${sandStam}`;
    const savedSandEq=savedSandEquivalent();
    /* BLUE_SAND_LABEL_CLEANUP_V1: the planner still applies the canonical Blue Sand conversion internally; the UI no longer repeats the x5 note. */
    if($('sandEquivalentNow')) $('sandEquivalentNow').textContent=`Saved total: ${fmtCompact(savedSandEq)} basic-equivalent`;
    const savedTreatEq=savedTreatEquivalent();
    if($('treatEquivalentNow')) $('treatEquivalentNow').textContent=`Saved total: ${fmtCompact(savedTreatEq)} basic-equivalent · ≈${fmtCompact(savedTreatEq*TREAT_BASIC_EXP)} Fantomon EXP`;
    const displayedTreats=Number(resources.treat)||0;
    $('treatProjected').textContent=`Projected: ${fmtCompact(displayedTreats)} basic-eq.`;
    if($('shopRefreshEstimate')){
      const shop=resources.shopEstimate||dailyShopMaterialEstimate(cfg);
      const gain=(id,value)=>{const el=$(id);if(el)el.textContent=shop.refreshes?`+${fmtCompact(value)}/day`:'Off';};
      gain('shopGainOre',shop.perDay.ore);
      gain('shopGainEssence',shop.perDay.essence);
      gain('shopGainSand',shop.perDay.sand);
      gain('shopGainTreat',shop.perDay.treat);
      $('shopRefreshEstimate').textContent=shop.refreshes
        ? `+${fmtCompact(shop.perDay.ore)} Ore · +${fmtCompact(shop.perDay.essence)} Essence · +${fmtCompact(shop.perDay.sand)} Sand-eq · +${fmtCompact(shop.perDay.treat)} Treats / day`
        : 'Off';
      if($('shopRefreshEstimateNote')){
        const observed=shop.sampleCount>0;
        const perPage=shop.perBuyout||{};
        $('shopRefreshEstimateNote').textContent=shop.refreshes
          ? observed
            ? `Observed Charming Glance S2 average from ${shop.sampleCount} untouched shop pages · ${shop.days} future reset day${shop.days===1?'':'s'} counted · Sand-eq includes ${fmtCompact(shop.perDay.sandRegular)} regular + ${fmtCompact(shop.perDay.sandRare)} Rare Chrono Sand/day (Rare ×${SAND_BLUE_EQ}).`
            : `${shop.days} future reset day${shop.days===1?'':'s'} counted · current day excluded to avoid double-counting materials already entered under Saved.`
          : observed
            ? `Observed CG S2 sample n=${shop.sampleCount}: ${fmtCompact(perPage.ore)} Ore · ${fmtCompact(perPage.essence)} Essence · ${fmtCompact(perPage.sandRegular)} regular Sand + ${fmtCompact(perPage.sandRare)} Rare Sand · ${fmtCompact(perPage.treat)} Treats per page. Rare Sand counts ×${SAND_BLUE_EQ} toward Sand-equivalent.`
            : 'Set Shop Buyouts/day: 1 counts the base page with no refresh; 2 counts the base page plus one restock and a second full-page buyout.';
      }
    }



    $('currentStars').textContent=fmt(baselineStars);
    $('currentScoreNow').textContent=fmt(currentScoreNow);
    $('desiredScore').textContent=fmt(requestedDesired);
    $('targetMessage').hidden=true;
    $('targetMessage').classList.remove('warning');

    $('currentBreakCharacter').textContent=fmt(currentParts.character);
    $('currentBreakGear').textContent=fmt(currentParts.gear);
    $('currentBreakSkills').textContent=fmt(currentParts.skills);
    $('currentBreakRelics').textContent=fmt(currentParts.relics);
    $('currentBreakFantomons').textContent=fmt(currentParts.fantomons);
    $('currentCharacterLabel').textContent=`Character · Lv.${currentCharacter.level} + ${Math.floor(currentCharacter.pct*100)}%`;
    $('currentGearLabel').textContent=`Gear · ${gear.join(' / ')}`;
    $('currentSkillsLabel').textContent=`Skills · ${formatLevelMix(skillState.levels)}`;
    $('currentRelicsLabel').textContent=`Relics · ${formatLevelMix(relicState.levels,{plus:true})}`;
    $('currentFantomonsLabel').textContent=`Fantomons · ${formatLevelMix(fantoState.levels)}`;
    $('currentBreakdownExplain').textContent=currentCharacter.decimal<cfg.scoreFloor
      ? `${cfg.name} Season Power begins at Lv.${cfg.scoreFloor}; your current below-floor progression contributes 0 Season Power. Because you are Lv.${S2_PLANNER_START_LEVEL}+, the optimizer uses a Lv.${optimizerPlanningLevel(p.upgradeCapLevel??p.level,cfg)} full-seasonal unlock preview for upgrade availability while keeping Character score tied to your real projection. This lets stockpiled resources produce a useful Primostar estimate before the live scoring gate opens.`
      : `Character is Lv.${currentCharacter.level} at ${(currentCharacter.pct*100).toFixed(1)}% EXP. ${cfg.name} awards 1 point per completed 1% above the Lv.${cfg.scoreFloor} floor, so this contributes ${fmt(currentParts.character)} points.`;

    const recommendedSection=$('recommendedBreakdownSection');
    if(!plan){
      if($('resultEyebrow')) $('resultEyebrow').textContent='Requested target';
      $('currentStars').textContent=fmt(targetStars);
      if(recommendedSection) recommendedSection.hidden=true;
      $('targetSkills').textContent=formatLevelMix(skillState.levels); $('targetRelics').textContent=formatLevelMix(relicState.levels,{plus:true}); $('targetFantomons').textContent=formatLevelMix(fantoState.levels);
      GEAR_OUTPUT_IDS.forEach((id,i)=>$(id).textContent=gear[i]);
      $('optimizerSummary').textContent=gearLocked?'The requested score cannot be reached while Gear is locked under the current season caps.':'The requested score exceeds the currently supported progression caps/level gates; this is a score-cap issue, not a Material Realm shortage.';
      $('optimizedScore').textContent=`${fmt(baselineScore)} / ${fmt(desired)} score · target stays ${fmt(targetStars)} Primostars`;
      $('summaryOptimizedScore').textContent='—'; if($('targetStatus')){$('targetStatus').textContent='cap';$('targetStatus').classList.add('notMet');}
      $('targetMessage').hidden=false;$('targetMessage').classList.add('warning');
      $('targetMessage').textContent=`⚠ Target remains ${fmt(targetStars)} Primostars. No upgrade combination under the current lock/season caps reaches ${fmt(desired)} score, even with unlimited Ore/Essence/Sand.`;
      ['oreCost','essenceCost','sandCost','treatCost'].forEach(id=>$(id).textContent='0');
      setRawRemaining('oreBalance',0,resources.ore);
      setEssenceBalance('essenceBalance',0,resources);
      setSandBalance('sandBalance',0,resources);
      setTreatBalance('treatBalance',0,resources);
      ['oreToolBalance','essenceToolBalance','sandToolBalance'].forEach(hidePlanBalance);
      $('materialRealmRecommendation').hidden=true;$('materialRealmRecommendation').textContent='';
      $('secondaryCostNote').hidden=true;$('secondaryCostNote').textContent='';
      $('milestoneNote').hidden=true;$('milestoneNote').textContent='';
      renderAstralPact(baselineStars);
      renderPrimostarRewardReference(currentStarsNow,baselineStars);
      saveState();return;
    }

    $('targetSkills').textContent=formatLevelMix(plan.skillLevels||levelsFromAverage(plan.skill,8,100,projectedCaps.skill)); $('targetRelics').textContent=formatLevelMix(plan.relicLevels||levelsFromAverage(plan.relic,20,10,projectedCaps.relic),{plus:true}); $('targetFantomons').textContent=formatLevelMix(plan.fantoLevels||levelsFromAverage(plan.fanto,4,100,projectedCaps.fanto));
    ['targetGearWeapon','targetGearOffhand','targetGearHelmet','targetGearArmor','targetGearBoots'].forEach((id,i)=>$(id).textContent=plan.gear[i]);
    if(recommendedSection) recommendedSection.hidden=false;
    const planSkillLevels=plan.skillLevels||levelsFromAverage(plan.skill,8,100,projectedCaps.skill);
    const planRelicLevels=plan.relicLevels||levelsFromAverage(plan.relic,20,10,projectedCaps.relic);
    const planFantoLevels=plan.fantoLevels||levelsFromAverage(plan.fanto,4,100,projectedCaps.fanto);
    const recommendedParts={character:characterScore(p,cfg),gear:gearScore(plan.gear,cfg),skills:categoryScoreFromLevels(planSkillLevels,cfg.scoreFloor,cfg.weights.skill),relics:categoryScoreFromLevels(planRelicLevels,cfg.relicFloor,cfg.weights.relic),fantomons:categoryScoreFromLevels(planFantoLevels,cfg.scoreFloor,cfg.weights.fanto)};
    $('recommendedBreakCharacter').textContent=fmt(recommendedParts.character); $('recommendedBreakGear').textContent=fmt(recommendedParts.gear); $('recommendedBreakSkills').textContent=fmt(recommendedParts.skills); $('recommendedBreakRelics').textContent=fmt(recommendedParts.relics); $('recommendedBreakFantomons').textContent=fmt(recommendedParts.fantomons);
    $('recommendedCharacterLabel').textContent=`Character · Lv.${p.level} + ${Math.floor(p.pct*100)}%`; $('recommendedGearLabel').textContent=`Gear · ${plan.gear.join(' / ')}`; $('recommendedSkillsLabel').textContent=`Skills · ${formatLevelMix(planSkillLevels)} recommended`; $('recommendedRelicsLabel').textContent=`Relics · ${formatLevelMix(planRelicLevels,{plus:true})} recommended`; $('recommendedFantomonsLabel').textContent=`Fantomons · ${formatLevelMix(planFantoLevels)} recommended`;
    const recommendationDelta=plan.score-baselineScore;
    const planStars=historical+cfg.starBase+Math.floor(plan.score/cfg.scorePerStar);
    const projectedAboveGoal=!resourceBlocked && planStars>targetStars;
    const rawPotentialAboveGoal=!resourceBlocked && projectedRawCeilingStars>targetStars;
    const planSourceStage=candidateRealmStage(plan);
    $('recommendedBreakdownExplain').textContent=resourceBlocked?`This is the score-capable upgrade route for your ORIGINAL ${fmt(targetStars)}-Primostar target. It is not being downgraded; the resource cards below show what still needs funding.`:rawPotentialAboveGoal?`Smart Balance stops the recommended spend once the ${fmt(targetStars)}-Primostar goal is funded. Projected raw materials alone could reach about ${fmt(projectedRawCeilingStars)} Primostars if you intentionally spend farther, but that upside is informational and does not raise the recommendation above your entered goal.`:`Actual ${cfg.name} season-end score used by the recommendation: projected Character plus every suggested upgrade, adding ${fmt(Math.max(0,recommendationDelta))} progression points over the no-upgrade baseline.`;

    const lockedText=gearLocked?' Gear is locked at the five current levels.':'';
    const previewText=cfg.key==='s2'&&currentCharacter.level<S2_FULL_SEASONAL_PREVIEW_LEVEL
      ? ` Fantomon planning uses a conservative Lv.${optimizerPlanningLevel(p.upgradeCapLevel??p.level,cfg)} availability preview; Gear, Skills and Relic ranks are not Character-level capped.`
      : (cfg.key==='s2'?' Gear, Skills and Relic ranks are not Character-level capped; recommendations are limited by resources and the supported S2 blessing tables.':'');
    const capText=cfg.key==='s1'?` S1 safe-upgrade cap uses projected Lv.${p.upgradeCapLevel??p.level} at season reset: Skills ${projectedCaps.skill}, Fantomons ${projectedCaps.fanto} (next 10-level band), Relics +${projectedCaps.relic}; Gear is not Character-level capped.`:` S2 score model: floor Lv.130 / Relics above +13, +45 fixed Primostars, 27 score per Primostar, weights Character 100 / Gear 18 / Skill 7 / Relic 33 / Fantomon 8. Max Realm bracket is Lv.120.${previewText}`;
    const achievableRewardStars=resourceBlocked?baselineStars:planStars;
    renderAstralPact(achievableRewardStars);
    renderPrimostarRewardReference(currentStarsNow,achievableRewardStars);
    if($('resultEyebrow')) $('resultEyebrow').textContent=resourceBlocked?'Target plan · resource shortfall':'Smart Balance goal plan';
    // TARGET_PLAN_HEADER_COMPLETE_V1: reward-reference rendering must never prevent the target-plan score/status from populating.
    $('currentStars').textContent=fmt(resourceBlocked?targetStars:planStars);$('summaryOptimizedScore').textContent=fmt(plan.score);
    if($('targetStatus')){$('targetStatus').textContent=resourceBlocked?'shortfall':'✓';$('targetStatus').classList.toggle('notMet',resourceBlocked);}
    $('optimizedScore').textContent=resourceBlocked?`${fmt(plan.score)} / ${fmt(requestedDesired)} score · ${fmt(targetStars)} Primostars target plan`:`${fmt(plan.score)} / ${fmt(requestedDesired)} score · ${fmt(planStars)} Primostars · goal ${fmt(targetStars)} ✓`;
    renderTargetTiming(plan,resourceBlocked,requestedDesired,p,cfg);
    $('oreCost').textContent=fmt(plan.oreCost);$('essenceCost').textContent=fmt(plan.essenceCost);$('sandCost').textContent=fmt(plan.sandCost);$('treatCost').textContent=fmt(plan.treatCost);

    const secondary=$('secondaryCostNote');
    const refinedShort=resources.refinedTracked?Math.max(0,(plan.refinedCost||0)-resources.refined):0;
    const secondaryBits=[];
    if((plan.refinedCost||0)>0){
      if(resources.refinedTracked) secondaryBits.push(`<b>Refined Ore:</b> ${fmt(plan.refinedCost)} required · ${refinedShort>0.5?`${fmt(Math.ceil(refinedShort))} short`:`${fmt(Math.max(0,resources.refined-plan.refinedCost))} left`}`);
      else secondaryBits.push(`<b>Refined Ore:</b> ${fmt(plan.refinedCost)} needed at +5 milestones`);
    }
    if((plan.gearAdds||0)>0) secondaryBits.push(`<b>Rolla:</b> ${fmt((Number(plan.oreCost)||0)*S2_EXACT_UPGRADE_RULES.rollaPerOre)} required · inventory not tracked`);
    secondary.hidden=secondaryBits.length===0;secondary.innerHTML=secondaryBits.join(' · ');

    // Two shortage views are intentional:
    // 1) Normal Resource-card Remaining = RAW material only after the recommended spend.
    //    Realm tools enter the card only once raw material is exhausted and a shortage must be bridged.
    // 2) Top warning = hard residual after EVERY remaining extra Realm refresh slot is also exhausted.
    //    This is the true physical season-end impossibility amount.
    const oreYield=Math.max(0,Number(resources.yields.orePerHammer)||0);
    const essenceYield=Math.max(0,Number(resources.yields.essencePerKnuckles)||0);
    const sandYield=Math.max(0,Number(resources.yields.sandPerShovel)||0);
    const oreCommittedRealm=(Math.max(0,Number(plan.realm?.ore?.bankedUsed)||0))*oreYield;
    const essenceCommittedRealm=(Math.max(0,Number(plan.realm?.essence?.bankedUsed)||0))*essenceYield;
    const sandCommittedRealm=(Math.max(0,Number(plan.realm?.sand?.bankedUsed)||0))*sandYield;
    const oreCommittedBudget=resources.ore+oreCommittedRealm;
    const essenceCommittedBudget=resources.essence+essenceCommittedRealm;
    const sandCommittedBudget=resources.sand+sandCommittedRealm;
    const orePlanShort=Math.max(0,plan.oreCost-oreCommittedBudget),essPlanShort=Math.max(0,plan.essenceCost-essenceCommittedBudget),sandPlanShort=Math.max(0,plan.sandCost-sandCommittedBudget),treatShort=Math.max(0,plan.treatCost-resources.treat);

    const oreMaxRealm=Math.max(0,Number(plan.realm?.ore?.provided)||0);
    const essenceMaxRealm=Math.max(0,Number(plan.realm?.essence?.provided)||0);
    const sandMaxRealm=Math.max(0,Number(plan.realm?.sand?.provided)||0);
    const oreHardShort=Math.max(0,plan.oreCost-(resources.ore+oreMaxRealm));
    const essHardShort=Math.max(0,plan.essenceCost-(resources.essence+essenceMaxRealm));
    const sandHardShort=Math.max(0,plan.sandCost-(resources.sand+sandMaxRealm));
    if(resourceBlocked){
      /* PARTIAL_SHORTFALL_SHOW_REMAINING_V1
         A target can be impossible because ONE resource is exhausted while the other cards
         still have plenty left. Only show a shortage breakdown on resources that are actually
         short under the selected daily plan; otherwise keep the normal Remaining display. */
      if(orePlanShort>0.5) setRealmShortfallBreakdown('oreBalance',orePlanShort,oreYield,'Hammers',plan.realm?.ore?.maxPurchasedRuns,oreHardShort,'Ore');
      else setRawRemaining('oreBalance',plan.oreCost,resources.ore);
      if(essPlanShort>0.5) setRealmShortfallBreakdown('essenceBalance',essPlanShort,essenceYield,'Knuckles',plan.realm?.essence?.maxPurchasedRuns,essHardShort,'Essence',(resources.s2SkillReserve?.rawEssence||0)>0?` · S2 raw reserve: ${fmt(resources.s2SkillReserve.rawEssence)} Essence`:'');
      else setEssenceBalance('essenceBalance',plan.essenceCost,{...resources,planRealmProvided:plan.realm?.essence?.planProvided||0});
      if(sandPlanShort>0.5) setRealmShortfallBreakdown('sandBalance',sandPlanShort,sandYield,'Shovels',plan.realm?.sand?.maxPurchasedRuns,sandHardShort,'Sand',(resources.s2RelicSandReserve?.rawSand||0)>0?` · S2 raw reserve: ${fmt(resources.s2RelicSandReserve.rawSand)} Sand`:'');
      else setSandBalance('sandBalance',plan.sandCost,{...resources,planRealmProvided:plan.realm?.sand?.planProvided||0});
      setTreatBalance('treatBalance',plan.treatCost,resources);
      const shortageBits=[];if(oreHardShort>0.5)shortageBits.push(`${fmt(Math.ceil(oreHardShort))} Ore`);if(essHardShort>0.5)shortageBits.push(`${fmt(Math.ceil(essHardShort))} Essence`);if(sandHardShort>0.5)shortageBits.push(`${fmt(Math.ceil(sandHardShort))} Sand`);if(treatShort>0.5)shortageBits.push(`${fmt(Math.ceil(treatShort))} Treats`);if(refinedShort>0.5)shortageBits.push(`${fmt(Math.ceil(refinedShort))} Refined Ore`);
      const dailyShortBits=[];if(orePlanShort>0.5)dailyShortBits.push(`${fmt(Math.ceil(orePlanShort))} Ore`);if(essPlanShort>0.5)dailyShortBits.push(`${fmt(Math.ceil(essPlanShort))} Essence`);if(sandPlanShort>0.5)dailyShortBits.push(`${fmt(Math.ceil(sandPlanShort))} Sand`);
      $('targetMessage').hidden=false;$('targetMessage').classList.add('warning','danger');
      $('targetMessage').innerHTML=`⚠ Goal exceeds remaining Realm capacity.<span class="targetMessageDetail">Still short after maxing Realm purchases: ${shortageBits.join(' · ')||'resources'}.</span>`;
      const brief=[];
      /* TOOL_ONLY_RESOURCE_GAPS_V4: reserve math intentionally hidden from result summary */
      if((resources.s2SkillReserve?.target||0)>0) brief.push(`${fmt(resources.s2SkillReserve.target)} S2 skill reserve`);
      if(gearLocked) brief.push('Gear locked');
      brief.push('Resource totals include the selected daily Realm plan');
      $('optimizerSummary').textContent=brief.join(' · ');
    }else{
      const brief=[];
      /* TOOL_ONLY_RESOURCE_GAPS_V4: reserve math intentionally hidden from result summary */
      brief.push(`Goal ${fmt(targetStars)} ✓`);
      if(rawPotentialAboveGoal) brief.push(`projected raw-only potential ${fmt(projectedRawCeilingStars)}`);
      if(planSourceStage===0) brief.push('goal plan happened to use raw only');
      else if(planSourceStage===1) brief.push('raw + saved/planned Realm tools optimized as one pool · raw consumed first');
      else if(planSourceStage===2) brief.push('extra Realm purchases required as final fallback');
      if((resources.s2SkillReserve?.target||0)>0) brief.push(`${fmt(resources.s2SkillReserve.target)} S2 skill reserve`);
      if(gearLocked) brief.push('Gear locked');
      $('optimizerSummary').hidden=false;
      $('optimizerSummary').textContent=brief.join(' · ');
      setRawRemaining('oreBalance',plan.oreCost,resources.ore);
      setEssenceBalance('essenceBalance',plan.essenceCost,{...resources,planRealmProvided:plan.realm?.essence?.planProvided||0});
      setSandBalance('sandBalance',plan.sandCost,{...resources,planRealmProvided:plan.realm?.sand?.planProvided||0});
      setTreatBalance('treatBalance',plan.treatCost,resources);
    }

    const rawOreRemaining=Math.max(0,(Number(resources.ore)||0)-(Number(plan.oreCost)||0));
    const rawEssenceRemaining=Math.max(0,(Number(resources.essenceTotal??resources.essence)||0)-(Number(plan.essenceCost)||0));
    const rawSandRemaining=Math.max(0,(Number(resources.sandTotal??resources.sand)||0)-(Number(plan.sandCost)||0));
    setToolBalance('oreToolBalance',plan.realm?.ore,oreHardShort,oreYield,'Hammers',0,rawOreRemaining);
    setToolBalance('essenceToolBalance',plan.realm?.essence,essHardShort,essenceYield,'Knuckles',resources.s2SkillReserve?.knucklesReserved||0,rawEssenceRemaining);
    setToolBalance('sandToolBalance',plan.realm?.sand,sandHardShort,sandYield,'Shovels',resources.s2RelicSandReserve?.shovelsReserved||0,rawSandRemaining);
    appendStaminaProjection('oreToolBalance',allocation.ore,added.ore,'Ore');
    appendStaminaProjection('essenceToolBalance',allocation.essence,added.essence,'Essence');
    appendStaminaProjection('sandToolBalance',allocation.sand,added.sand,'Sand');

    renderRealmDailyRecommendations(plan,resources,cfg);

    const realmRec=$('materialRealmRecommendation'),realmDetailParts=[];
    const realmEntries=[
      {key:'ore',label:'Hammers',top:plan.realm?.ore},
      {key:'essence',label:'Knuckles',top:plan.realm?.essence},
      {key:'sand',label:'Shovels',top:plan.realm?.sand}
    ];
    const extraRealmBits=[];
    let hasRealmNeed=false;
    for(const entry of realmEntries){
      const top=entry.top;
      if(!top) continue;
      const detail=formatRealmSchedule(top,entry.label); if(detail) realmDetailParts.push(detail);
      if(Number.isFinite(top.packs)&&top.packs>0){
        hasRealmNeed=true;
        const extraTools=Math.max(0,Math.floor(Number(top.purchasedRuns)||0));
        if(extraTools>0) extraRealmBits.push(`${entry.label} +${fmt(extraTools)}`);
      }
    }
    const protectedKnuckles=Math.max(0,Math.floor(Number(plan.realm?.essence?.reserveRuns)||0));
    const protectedShovels=Math.max(0,Math.floor(Number(plan.realm?.sand?.reserveRuns)||0));
    const afterPlanTools={
      ore:Math.max(0,(plan.realm?.ore?.bankedRemaining||0)+(plan.realm?.ore?.sparePurchasedRuns||0)),
      essence:Math.max(0,(plan.realm?.essence?.bankedRemaining||0)+(plan.realm?.essence?.sparePurchasedRuns||0)),
      sand:Math.max(0,(plan.realm?.sand?.bankedRemaining||0)+(plan.realm?.sand?.sparePurchasedRuns||0))
    };
    // COMPACT_REALM_AFTER_PLAN_V1: keep the useful post-plan balance without repeating context.
    const toolLeftEls=[['hammerAfterPlan',afterPlanTools.ore,0],['knucklesAfterPlan',afterPlanTools.essence,protectedKnuckles],['shovelAfterPlan',afterPlanTools.sand,protectedShovels]];
    toolLeftEls.forEach(([id,value,protectedCount])=>{const el=$(id);if(el){el.textContent=`After plan: ${fmt(value)} left${protectedCount?` · ${fmt(protectedCount)} reserved`:''}`;el.classList.toggle('toolLow',value<=10);}});
    if(hasRealmNeed||resourceBlocked){
      realmRec.hidden=false;
      const hardNotes=[];
      if(treatShort>0.5) hardNotes.push(`Treats short ${fmt(Math.ceil(treatShort))}`);
      if(refinedShort>0.5) hardNotes.push(`Refined Ore short ${fmt(Math.ceil(refinedShort))}`);
      const realmCan=!resourceBlocked||!!plan.realmFeasible;
      realmRec.classList.toggle('realmFeasible',realmCan);
      realmRec.classList.toggle('realmImpossible',!realmCan);
      const extraText=extraRealmBits.length?`Goal achievable with extra Realm entries · ${extraRealmBits.join(' · ')} beyond daily plan`:(realmCan?'Goal achievable · selected daily Realm plan covers it':'Goal not achievable through remaining Realm capacity');
      const dailyPreset={ore:realmDailyValue('ore'),essence:realmDailyValue('essence'),sand:realmDailyValue('sand')};
      const dailySuggested=suggestedRealmDailyPlan(plan,cfg);
      // RECOVERABLE_SHORTFALL_REFRESH_PLAN_V1: put the resource-specific action directly
      // on each recoverable shortage card. dailySuggested values are refreshes/day, while
      // the first line keeps the exact number of additional Realm tools needed overall.
      const applyShortfallRefreshPlan=(id,key,realmLabel)=>{
        const el=$(id);
        if(!el || !el.classList.contains('shortfallBreakdown') || el.querySelector('.hardShort')) return;
        const bridge=el.querySelector('.realmBridge');
        if(!bridge) return;
        const recommended=Math.max(0,Math.floor(Number(dailySuggested?.[key])||0));
        const current=Math.max(0,Math.floor(Number(dailyPreset?.[key])||0));
        const tools=Math.max(0,Math.ceil(Number(el.dataset.shortfallTools)||0));
        const item=el.dataset.shortfallItem||'tools';
        if(recommended>current){
          bridge.textContent=`Recommended: ${fmt(recommended)} ${realmLabel} Realm purchase${recommended===1?'':'s'}/day`;
        }else if(tools>0){
          bridge.textContent=`${fmt(tools)} ${item} can cover`;
        }
      };
      applyShortfallRefreshPlan('oreBalance','ore','Ore');
      applyShortfallRefreshPlan('essenceBalance','essence','Essence');
      applyShortfallRefreshPlan('sandBalance','sand','Sand');
      const unknownTierCount=realmEntries.reduce((sum,e)=>sum+Math.max(0,Number(e.top?.unknownPriceRefreshes)||0),0);
      const priceNote=unknownTierCount>0?` · ${fmt(unknownTierCount)} extra purchase${unknownTierCount===1?'':'s'} use unverified 11–20 pricing`:'';
      const suggestionLine=realmCan&&dailySuggested.changed&&dailySuggested.needsExtra
        ? `<div class="realmBuyRoute"><b>Suggested daily plan:</b> ${dailySuggested.ore} H / ${dailySuggested.essence} K / ${dailySuggested.sand} S for ${fmt(dailySuggested.futureDays)} remaining reset${dailySuggested.futureDays===1?'':'s'}</div>`
        : (!realmCan&&dailySuggested.changed&&dailySuggested.impossible
          ? `<div class="realmBuyRoute"><b>Best available daily plan:</b> ${dailySuggested.ore} H / ${dailySuggested.essence} K / ${dailySuggested.sand} S · target still has a hard shortfall</div>`
          : '');
      realmRec.innerHTML=`<b>Material Realm:</b> ${extraText} · daily ${dailyPreset.ore}/${dailyPreset.essence}/${dailyPreset.sand} already included${priceNote}${hardNotes.length?` · ${hardNotes.join(' · ')}`:''}${suggestionLine}`;
      if(!resourceBlocked && hasRealmNeed){
        $('targetMessage').hidden=false;
        $('targetMessage').classList.add('warning','caution');
        // APPLY_RECOMMENDED_REALM_REFRESHES_V1: recommendation and one-click apply live inside the caution box.
        const route=dailySuggested.changed
          ? `<span class="targetMessageDetail">Recommended refreshes/day: Ore ${dailySuggested.ore} · Essence ${dailySuggested.essence} · Sand ${dailySuggested.sand}.</span>`
          : '';
        const action=dailySuggested.changed
          ? `<button type="button" class="applyRealmRecommendation" data-ore="${dailySuggested.ore}" data-essence="${dailySuggested.essence}" data-sand="${dailySuggested.sand}">Apply purchases</button>`
          : '';
        // Resource cards now carry the exact deficit + resource-specific refresh action.
        // Keep this banner focused on the combined plan and its one-click Apply control.
        $('targetMessage').innerHTML=`<span class="targetMessageCopy">⚠ Goal is achievable with the recommended Material Realm purchase plan.${route}</span>${action}`;
      }
      realmRec.title=realmDetailParts.join(' · ');
    }else{realmRec.hidden=true;realmRec.textContent='';realmRec.classList.remove('realmFeasible','realmImpossible');realmRec.removeAttribute('title');}
    $('milestoneNote').hidden=true;$('milestoneNote').textContent='';
    saveState();
    const perfMs=performance.now()-perfStarted;
    const calcSection=$('calculatorSection');
    if(calcSection) calcSection.dataset.lastSolveMs=perfMs.toFixed(1);
    if(perfMs>750) console.warn(`Primostar solve took ${perfMs.toFixed(0)} ms`,{season:cfg.key,target:targetStars});
  }

  function copyPlan(){
    updateCalculator();
    const text=[
      `Charming Glance ${activeCalcConfig().name} plan`,
      `Current score now: ${$('currentScoreNow').textContent}`,
      `After recommended upgrades: ${$('optimizedScore').textContent}`,
      `Projected character: ${$('resultProjectedCharacter').textContent}`,
      `Target: ${$('targetStars').value} Primostars`,
      `Skills: ${$('targetSkills').textContent}`,
      `Relics: ${$('targetRelics').textContent}`,
      `Fantomons: ${$('targetFantomons').textContent}`,
      `Gear: W ${$('targetGearWeapon').textContent} / OH ${$('targetGearOffhand').textContent} / H ${$('targetGearHelmet').textContent} / A ${$('targetGearArmor').textContent} / B ${$('targetGearBoots').textContent}`,
      `Projected Stamina focus: ${staminaModeLabel(staminaMode())}${staminaMode()==='auto'&&$('staminaCurrentPlan')?` · ${$('staminaCurrentPlan').innerText.replace(/\n+/g,' · ')}`:''}`,
      `Ore: ${$('oreCost').textContent} (${ $('oreBalance').textContent })`,
      `Essence: ${$('essenceCost').textContent} (${ $('essenceBalance').textContent })`,
      `Sand: ${$('sandCost').textContent} (${ $('sandBalance').textContent })`,
      `Treats: ${$('treatCost').textContent} (${ $('treatBalance').textContent })`,
      ...(!$('secondaryCostNote').hidden?[`Other costs: ${$('secondaryCostNote').textContent}`]:[]),
      ...(!$('materialRealmRecommendation').hidden?[`Material Realm: ${$('materialRealmRecommendation').innerText.replace(/^Material Realm today:\s*/,'Today: ').replace(/^Material Realm:\s*/,'').replace(/\n+/g,' · ')}`]:[]),
    ].join('\n');
    navigator.clipboard?.writeText(text).then(()=>{
      $('saveStatus').textContent='Plan copied.'; $('saveStatus').classList.add('copyFlash');
      setTimeout(()=>{$('saveStatus').textContent='Saved snapshot auto-ages Cart + character EXP; future Stamina regen is projected automatically.';$('saveStatus').classList.remove('copyFlash');},1400);
    }).catch(()=>{});
  }

  function resetCalculator(){
    const cfg=activeCalcConfig();
    if(cfg.key==='s1'){
      INPUT_IDS.forEach(id=>{if($(id)) $(id).value=defaults[id];});
      CHECK_IDS.forEach(id=>{if($(id)) $(id).checked=defaults[id];});
    } else {
      applyS2ScoringStartDefaults();
    }
    gearLocked=false; snapshotAtMs=Date.now(); snapshotSeason=cfg.key; snapshotCarry={ore:0,essence:0,sand:0,treat:0,exp:0}; snapshotStateLoaded=true;
    updateGearLockUI(); localStorage.removeItem(STORAGE_KEY); saveState(); updateCalculator();
  }

  // ---------- Timeline ----------
  const timelineData = [
    // ---- Season 1 · Charming Glance / Qenu anchor + QY Maple details ----

    // ---- Season 2 · Loong Haven ----
    ['2026-08-30',47,'Region','Loong Haven opens','CONFIRMED for Charming Glance: Season 2 Day 1 begins at the Aug 30 server reset. On Aug 26, the in-game season countdown showed 3d 21h remaining, aligning with this reset; Prydwen independently places T4 at Server Day 47. Once S2 is live: Lv.106 = T4 class advancement + Loong Haven Five; Fantomon Adult / Materialization requires Lv.108, Numbuville unlocked, and Mythic rarity (duplicate); Lv.116 = Demonbind Tower.','region'],
    ['2026-08-30',47,'Feature','Gear Refinement & Affix Transfer','Season 2 feature confirmed by Prydwen: Mythic-or-better S2+ gear can reroll affixes, and affixes can transfer to same-type Mythic-or-better gear. Same-season Affix Transfer is free; carrying chosen affixes across later seasons uses Divinecraft Stones. S1 gear is not eligible for Affix Transfer, even at Mythic rarity, so do not save S1 gear expecting to move its stats into S2. Charming Glance Season 2 is confirmed for the Aug 30 server reset by the in-game season countdown.','feature'],
    ['2026-08-30',47,'Feature','Season 2 Day 1 checklist','<span class="launchChecklist"><span><b>1.</b><strong>Start with rollover rewards.</strong><em>Season 2 is live; collect the new-season rewards before spending progression resources.</em></span><span><b>2.</b><strong>Claim Astral / season rewards.</strong><em>Grab rollover, Astral Pact, and other immediately available season rewards.</em></span><span><b>3.</b><strong>Rank up as far as possible.</strong><em>Do this before spending Stamina or Material Realm resources so later rewards use your higher rank where applicable.</em></span><span><b>4.</b><strong>Claim your saved Bed EXP.</strong><em>Collect the banked 34 hours now. Current community testing says waiting for statues does not increase EXP already stored.</em></span><span><b>5.</b><strong>Push the new map and activate reachable statues.</strong><em>Explore as far as your level allows and activate every Goddess / Lost Goddess Statue you can reach.</em></span><span><b>6.</b><strong>Use Bed boosts after statue progress.</strong><em>Use the free 2-hour Bed boost and other Bed speed-ups after pushing statues so the new rate applies to the boosted time.</em></span><span><b>7.</b><strong>Spend Stamina and Material Realm resources.</strong><em>Once rank and early map progress are set, start using saved Realm tools, refreshes, and Stamina.</em></span><span><b>8.</b><strong>Finish progression cleanup.</strong><em>Do class advancement, relics, gear, Fantomons, and other upgrades as the new level gates open.</em></span></span>','feature'],
    // TOURNAMENT_TIMING_SEP9_V1: direct Charming Glance screenshots taken just after midnight Sep. 9 PDT.
    // Standard Tournament registration showed ~2d 5h remaining (Friday reset); Nexus itself showed ~3d 19h to start (Saturday evening).
    ['2026-09-05',53,'Event','Server Tournament','The weekly Server Tournament runs Saturday; registration opens the day before.','event'],
    ['2026-09-12',60,'Event','Server Tournament','Registration opens Friday Sep. 11 · tournament Saturday Sep. 12.','event'],
    ['2026-09-12',60,'Event','Nexus Tournament · 4v4','Direct Charming Glance countdown just after midnight Sep. 9 showed 3d 19h to start, placing Nexus on Saturday evening Sep. 12.','event'],
    ['2026-09-26',74,'Event','Nexus Tournament · 4v4','14-day Nexus cadence following the Saturday Sep. 12 tournament. Recheck the in-game timer as the date approaches.','event'],
    ['2026-10-10',88,'Event','Nexus Tournament · 4v4','14-day Nexus cadence following the Saturday Sep. 12 tournament. Recheck the in-game timer as the date approaches.','event'],
    ['2026-10-24',102,'Event','Nexus Tournament · 4v4','14-day Nexus cadence following the Saturday Sep. 12 tournament; likely the final S2 Nexus before rollover.','event'],
    ['2026-09-01',49,'Collab','Vegetables Fairy Pt. 2 · free emoticons','CONFIRMED by the official Sword x Staff Global announcements channel on Sep. 1: 8 limited-time collaboration Emoticons are free. The notice says 4 come from sign-in, 4 from Shop exchange, and the remaining 4 can be obtained from the prize wheel. This is a pre-launch/reward announcement only; it does not confirm the full Vegetables Fairy Part Two collab is live or provide an exact collab start/end date.','event'],

    ['2026-08-30',47,'Class Advancement','Tier 4 class advancement','Level-gated in Season 2: unlocks at Player Lv.106 · Class Lv.89 · Tier 3 class Lv.19 · Loong Haven Five. Date is shown at the S2 start only as a timeline reference; actual unlock happens when Lv.106 is reached.','class-advancement'],
    ['2026-08-30',47,'Fantomon','Fantomon Adult / Materialization unlock','Season 2 gate: Player Lv.108 + Numbuville unlocked + Mythic rarity; Mythic evolution requires a duplicate copy. Date is shown at S2 start only as a timeline reference; the unlock occurs when all requirements are met.','fantomon'],
    ['2026-08-30',47,'Feature','Demonbind Tower unlock','Level-gated in Season 2 at Player Lv.116 · Gem Tower / gem-harvest feature. Date is shown at the S2 start only as a timeline reference; actual unlock happens when Lv.116 is reached.','feature'],
    ['2026-08-30',47,'Dungeon','Demonseal Gorge','Season 2 Day 1 · Normal · Hard 2.35M · Global-first/QY English name','dungeon'],
    ['2026-09-01',49,'Event','Gift code · VEGGIE','Confirmed by the official Sword x Staff Global Discord gift-code announcement: 10 Rare Auroral Badges + 80 Dawnium. Active now. Official validity ends Sep. 8 at 00:00 (UTC-5), with its stored expiry timestamp converted to the viewer device local timezone.','event','2026-09-08',null,'2026-09-08T05:00:00Z'],
    // CRYSTAL_EXPIRY_SEP9_V1: current code trackers agree on Sep. 15 00:00 UTC-5; official mirror has not carried CRYSTAL yet.
    // This resolves to Sep. 14 10:00 PM PDT for Charming Glance, eight hours before the Sep. 15 server reset.
    ['2026-09-08',56,'Event','Gift code · CRYSTAL','Current reports list CRYSTAL as the Community Weekly Gift Code: 300 Raw Ore + 1 Stellatie. Reported expiry is Sep. 15 at 00:00 UTC-5, with its stored expiry timestamp converted to the viewer device local timezone. The mirrored official Global feed has not carried this code yet.','event','2026-09-15','unconfirmed','2026-09-15T05:00:00Z'],
    ['2026-09-06',54,'Event','Official Top-Up Platform events open','CONFIRMED by the official Sword x Staff Global announcements feed on Sep. 4. The Official Top-Up Platform launches two reward events at Sep. 7, 00:00 (UTC-5), with the stored start timestamp converted to the viewer device local timezone: Cumulative Top-up Lottery runs through Oct. 4, 23:59:59 (UTC-5), awarding 1 draw per 9,999 Vouchers topped up with prizes including 29,999 / 9,999 / 4,999 / 999 Vouchers; Daily Top-up Sign-in runs through Sep. 6, 2027 and gives 1 daily draw after any official-platform top-up, with prizes including Vouchers, Bond Trinket, and Covenite. These are paid top-up promotions, not a Charming Glance progression unlock, and they begin about 8 hours before the Sep. 7 server reset.','event','2026-10-05',null,'2026-09-07T05:00:00Z'],
    ['2026-09-07',55,'Collab','Vegetables Fairy Collab Pt. 2','CONFIRMED GLOBAL DATE from the official Sword x Staff announcements feed on Sep. 4: the official reward preview says only 3 days remain until the collab begins, placing the launch on Sep. 7. The post does not give an exact clock time or say it starts at Charming Glance reset, so this row confirms the calendar date without claiming a server-reset start time. Confirmed Pt. 2 rewards/activities include daily sign-in rewards (Eggplant Mallet, Vegetable Cuddle Hairpin, Wheel Tickets and collab Emoticons), Golden Veggie Coins from event quests for the Veggie Shop, daily Veggie Shuffle stages toward the Violet Kitty Suit, and Lemon Whale purification 3 times for the Lemon Whale Plushie. Earlier official Global previews also confirmed the Cabbage Dog Fantomon and Pt. 2 Visages. TIME-LIMITED GIFT CODE: VEGGIE — 10 Rare Auroral Badges + 80 Dawnium. Multiple current code trackers report it active through Sep. 8; this expiry is community/secondary-source reported rather than confirmed by the mirrored official feed, so redeem it promptly. Exact event end date remains unannounced.','event'],
    // S2_EVENT_ROTATION_DAY57_64_V1
    ['2026-09-12',60,'Dungeon','Warlord’s Rest','Player Lv.130 · Normal 3.55M · Hard 5M · Nightmare 6M','dungeon'],
    ['2026-09-12',60,'Feature','Season Power unlock','Player Lv.130','feature'],
    // ACME_NEXUS_DAY71_CORRECTION_SEP9_V1
    // Official Global confirms the Global-English name Acme Nexus and its gateway role before Aethyris.
    // Limitless Gaming's live older-server schedule places the Loong Haven seasonal map at Server Day 71.
    // That same schedule matches Charming Glance's established S2 milestones at Days 60, 73, 78, 86, 92 and 99,
    // so Day 71 is stronger cadence evidence than the earlier QY-derived Day 61 projection.
    ['2026-09-23',71,'Seasonal Map','Acme Nexus','Official Global name: Acme Nexus. Current older-server cadence places the Loong Haven seasonal map on Server Day 71, mapping to Sep. 23 for Charming Glance. It is the gateway immediately before Aethyris.','seasonal-map',null,'unconfirmed'],
    ['2026-09-25',73,'Dungeon','Cloudcrest Temple','Normal 6.2M · Hard 7.7M · Nightmare 9.8M','dungeon'],
    ['2026-09-30',78,'Ancient Relic','Ethereal Oracle','Loong Haven Relic II · second Loong Haven relic gacha','ancient-relic'],
    ['2026-10-08',86,'Dungeon','Bladeshire','Normal 10M · Hard 12.5M · Nightmare 15.8M','dungeon'],
    ['2026-10-14',92,'Fantomon','Pandarial','Global Fantomon name · older translated calendars may call it Bamboo Immortal. UNCONFIRMED FOR CHARMING GLANCE: recent community reports that say either ‘S2 Day 46’ or ‘Server Day 92’ are describing the same server-age unlock, because Season 2 begins on Server Day 47. For Charming Glance that maps to Oct. 14. General-Global guides also report Pandarial appearing in the wider Summon Crystal exchange from Aug. 18, so do not treat it as usable here until Charming Glance’s in-game exchange confirms it.','fantomon'],
    ['2026-10-21',99,'Dungeon','Celestship','Normal 16.5M · Hard 20M · Nightmare 24.5M · Purgatory 40M · QY: lasts around three weeks','dungeon'],



    // ---- Season 3 · Aethyris ----
    // S3_SUMMARY_ONLY_CLEANUP_SEP9_V1: visible S3 cards were stripped of confidence/source-audit prose; provenance remains in comments and maintained research notes.
    // S3_AETHYRIS_SEP9_RESEARCH_V1: LDShop's Sep. 9 Season 3 guide independently names the Aethyris subzones Skyrend Cliff, Unbroken Camp, and Harmonic Crystal. Keep these names as current secondary-source localization until Global in-game text or an official announcement supersedes them.
    // S3_DUNGEON_LOCALIZATION_SEP9_V1: the same current Sep. 9 guide names Crystal Spiral Tree's Sylvan Set and the second Aethyris dungeon Eternal Garden with the Lifespring Set. This supersedes the older pre-release label Eternal Blossom Courtyard while preserving the existing Day-127 cadence placement.
    ['2026-11-05',114,'Region','Aethyris opens','Skyrend Cliff · Unbroken Camp · Harmonic Crystal · Tier 5 era begins','region',null,'unconfirmed'],
    ['2026-11-05',114,'Dungeon','Crystal Spiral Tree','First Aethyris dungeon · Sylvan Set · Hard 9M','dungeon'],
    // S3_T5_GUIDE_STATUS_SEP9_V1: Prydwen now publishes dedicated Ravager, Magister, and Prophet T5 guides; Templar remains the only T5 path without a dedicated guide on its current guide index.
    ['2026-11-05',114,'Class Advancement','Tier 5 class advancement','Player Lv.136 · Class Lv.180 · Tier 4 class Lv.40 · Conqueror → Ravager · Guardian → Templar · Destroyer → Magister · Dominator → Prophet','class-advancement'],
    // S3_BOND_ODYSSEY_STONE_SYMPHONY_SEP9_V1: LDShop's Sep. 9 Season 3 guide identifies Bond Odyssey/Vista Dispatch and Stone Symphony as Aethyris systems, with timed companion expeditions and souvenir rewards. The visible row stays summary-only; the Nov. 5 placement follows the maintained S3 Day-114 rollover model.
    ['2026-11-05',114,'Feature','Bond Odyssey + Stone Symphony','Season 3 passive progression · Vista Dispatch milestones · timed companion expeditions · souvenir rewards','feature'],
    // S3_COMPANIONS_SEP9_V1: LDShop's Sep. 9 Season 3 guide names Isla and Astrid as new Aethyris companions.
    ['2026-11-05',114,'Companions','Isla + Astrid','New Season 3 companions joining in Aethyris','companions'],
    ['2026-11-05',114,'Feature','Aethyris area-unlock stockpile','Gateway Key ×5 · Magic Drill ×2 · Water Mine ×2 · “cloud key” ×2 · hammer ×5 (last two use QY labels; exact future Global item names unverified)','feature'],
    ['2026-11-18',127,'Dungeon','Eternal Garden','Normal 12.5M + Player Lv.160 · Hard 15M · Nightmare 18M · Purgatory 28.5M · Lifespring Set','dungeon'],
    ['2026-11-18',127,'Feature','Season Power unlock','Player Lv.160','feature'],
    ['2026-11-19',128,'Seasonal Map','Astral Odyssey','Aethyris season map · pre-release English/data name','seasonal-map'],
    ['2026-12-02',141,'Dungeon','Abyssal Bastion','Normal 20M · Hard 26M · Nightmare 30M · Purgatory 46M · pre-release English/data name','dungeon'],
    ['2026-12-05',144,'Ancient Relic','Aethyris Relic II','Second Aethyris relic gacha · final Global banner title not yet verified','ancient-relic'],
    ['2026-12-16',155,'Dungeon','Courtyard of Purification','Normal 32.5M · Hard 43M · Nightmare 50.5M · Purgatory 75M · pre-release English/data name','dungeon'],
    ['2026-12-20',159,'Fantomon','Prismora','Aethyris Fantomon · S3 Day 46','fantomon',null,'unconfirmed'],
    ['2026-12-30',169,'Dungeon','Temple of Order','Normal 55M · Hard 65M · Nightmare 82M · Purgatory 115M · pre-release English/data name','dungeon'],
    ['2027-01-04',174,'Ancient Relic','Aethyris Relic III','Third Aethyris relic gacha · final Global banner title not yet verified','ancient-relic'],
    ['2027-01-13',183,'Dungeon','Solar Spire','Normal 84.5M · Hard 100M · Nightmare 120M · Purgatory 180M · pre-release English/data name','dungeon'],
    ['2027-01-27',197,'Dungeon','Sovereign’s Nest','Normal 125M · Hard 145M · Nightmare 180M · Purgatory 250M · Abyss 350M. Current QY groups Abyss at S3 Day 84; the old separate Feb 2 legacy row has been retired.','dungeon'],

    // ---- Season 4 · Hapadi ----
    // QY currently lists S3 at ~112 days. With the projected Nov 5 Aethyris anchor, that places Hapadi on Feb 25 / Server Day 226.
    // These absolute dates remain merger-sensitive; the season-day offsets are the stronger reference.
    ['2027-02-25',226,'Region','Hapadi opens','UNCONFIRMED Charming Glance Season 4 projection. Current QY scheduling uses an ~112-day S3 and places Hapadi at Server Day 226 / Feb. 25. A separate fixed older-server calendar points to a Tier 6 boundary at Server Day 215 / Feb. 14, so the exact rollover remains unresolved; Feb. 25 stays the lead projection until the Charming Glance telescope/countdown or official Global notice confirms it. “Hapadi” is already present in current Global relic data.','region',null,'unconfirmed'],
    ['2027-02-25',226,'Dungeon','Ingenious Clocktower','Hapadi Day 1 · Normal · Hard 27M · pre-release English/data name','dungeon'],
    ['2027-02-25',226,'Class Advancement','Tier 6 class advancement','Level-gated in Hapadi: Player Lv.172 · Class Lv.280 · Tier 5 class Lv.50 · Hapadi Nine. Date is the projected Hapadi Day 1 reference; actual unlock requires the listed levels.','class-advancement'],
    ['2027-02-25',226,'Feature','Hapadi area-unlock stockpile','Gateway Key ×5 · Magic Drill ×2 · Water Mine ×2 · season item ×5 (QY calls it “lego”; final Global item name unverified)','feature'],
    ['2027-02-25',226,'Fantomon','Fantomon Resonance unlock','Level-gated at Player Lv.180 during Hapadi; Day 1 date is only the projected season reference.','fantomon'],
    ['2027-03-10',239,'Dungeon','Pirate Galleon','Hapadi Day 14 · Normal 35M + Player Lv.190 · Hard 48M · Nightmare 57M · Purgatory 84M · pre-release English/data name','dungeon'],
    ['2027-03-10',239,'Feature','Season Power unlock','Hapadi Day 14 · Player Lv.190','feature'],
    ['2027-03-11',240,'Seasonal Map','Grotesque Fairground','Hapadi Day 15 season map · pre-release English/data name','seasonal-map'],
    ['2027-03-24',253,'Dungeon','Leviathan Submersible','Hapadi Day 28 · Normal 62M · Hard 72M · Nightmare 87M · Purgatory 130M · pre-release English/data name','dungeon'],
    ['2027-03-27',256,'Ancient Relic','Hapadi Relic II','Hapadi Day 31 · second Hapadi relic gacha · English localization name TBD','ancient-relic'],
    ['2027-04-07',267,'Dungeon','Clockwork Fortress','Hapadi Day 42 · Normal 91M · Hard 110M · Nightmare 135M · Purgatory 190M','dungeon'],
    ['2027-04-21',281,'Dungeon','Celestial Observatory','Hapadi Day 56 · Normal 145M · Hard 175M · Nightmare 210M · Purgatory 305M','dungeon'],
    ['2027-04-26',286,'Ancient Relic','Hapadi Relic III','Hapadi Day 61 · third Hapadi relic gacha · English localization name TBD','ancient-relic'],
    ['2027-05-05',295,'Dungeon','Titan Hot-Air Balloon','Hapadi Day 70 · Normal 220M · Hard 256M · Nightmare 300M · Purgatory 460M','dungeon'],
    ['2027-05-19',309,'Dungeon','Astral Citadel','Hapadi Day 84 · Normal 315M · Hard 365M · Nightmare 435M · Purgatory 630M · Abyss 880M · pre-release English/data name · current QY values.','dungeon'],
  ];

  // Server-age recurring events. Limitless Gaming confirms the weekly dates/cycle;
  // QY Maple confirms Grand Treasure Hunt Phase 1-15 Lv.5 rewards.
  function isoAddDays(iso,days){
    const [y,m,d]=iso.split('-').map(Number);
    const dt=new Date(Date.UTC(y,m-1,d)); dt.setUTCDate(dt.getUTCDate()+days);
    return dt.toISOString().slice(0,10);
  }
  function isoForServerDay(serverDay){ return isoAddDays('2026-07-15',serverDay-1); }
  function treasureHuntReward(phase){
    const fixed={
      1:'Selectable Cinder Ridge Mythic Relic',2:'Lucky Statue',3:'Selectable Tier 3 class skill shards ×180',4:'Primal Gem',
      5:'Selectable Aqualis Mythic Relic',6:'Lucky Statue',7:'Selectable Tier 4 class skill shards ×180',8:'Primal Gem',
      9:'Selectable Loong Haven I Mythic Relic',10:'Lucky Statue',11:'Selectable Tier 4 class skill shards ×180',12:'Primal Gem',
      13:'Selectable Loong Haven II Mythic Relic',14:'Lucky Statue',15:'Selectable Tier 4 class skill shards ×180'
    };
    if(fixed[phase]) return fixed[phase];
    const cycle=(phase-16)%4;
    if(cycle===0){
      if(phase>=32) return 'Primal Gem / Philosopher’s Stone / Treasure Detector';
      if(phase>=20) return 'Primal Gem / Philosopher’s Stone';
      return 'Primal Gem';
    }
    if(cycle===1) return 'Selectable Miracle Relic Box';
    if(cycle===2){
      if(phase>=34) return 'Lucky Statue / Golden Divine Tree / Endless Hourglass';
      return 'Lucky Statue / Golden Divine Tree';
    }
    const tier=phase>=47?7:phase>=31?6:5;
    return `Selectable Tier ${tier} class skill shards`;
  }
  function addRecurringEvents(){
    // Grand Treasure Hunt: Phase 1 on server day 8, then weekly.
    for(let phase=1;phase<=57;phase++){
      const serverDay=8+(phase-1)*7;
      const start=isoForServerDay(serverDay), end=isoAddDays(start,7);
      const reward=treasureHuntReward(phase);
      let strategy='Auroradrasil Energy carries over; check the Lv.5 reward before spending.';
      if(/Lucky Statue/.test(reward)) strategy='High-priority farming relic: chance to double dungeon chest rewards. Energy carries over.';
      else if(/Primal Gem/.test(reward)) strategy='High-priority farming relic: improves Gem acquisition. Energy carries over.';
      else if(/skill shards/.test(reward)) strategy='Class-skill phase; useful when you still need the current Tier skill investment.';
      else if(/Mythic Relic/.test(reward)||/Miracle Relic/.test(reward)) strategy='Relic-focused phase; compare against your current collection before spending saved Energy.';
      timelineData.push([start,serverDay,'Treasure Hunt',`Grand Treasure Hunt · Phase ${phase}`,`UNCONFIRMED recurring server-age projection · Lv.5: ${reward} · ${strategy}`,'event',end,'unconfirmed']);
    }
    // STALE_OCEANIC_EVENT_REFS_V2: recurring future rows contain only event-specific guidance;
    // expired limited-event overlaps are kept only on their historical runs.
    // Normal rotating mini-events: Bingo -> Lucky Scratch -> Feneck, each one week.
    const defs=[
      {base:15,name:'Bingo Draw',prep:'Destiny Fruits',note:'Rewards: board and milestone prizes (the exact item grid can vary). Complete every daily mission first. Global players report roughly 60–80 Destiny Fruits is usually enough to finish the normal board.'},
      {base:22,name:'Lucky Scratch',prep:'Material Realm tools',note:'Rewards: scratch-card RNG and milestone prizes. Use saved Material Realm consumables while this event is active to generate more scratch cards. This is the week to cash in the tools you banked during Feneck.'},
      {base:29,name:"Feneck's Puzzle",prep:'No major stockpile',note:'Rewards: puzzle and daily-track prizes. Do the event rewards and start banking Material Realm tools for the next Lucky Scratch.'}
    ];
    defs.forEach(def=>{
      let count=1;
      for(let serverDay=def.base;serverDay<=400;serverDay+=21,count++){
        const start=isoForServerDay(serverDay), end=isoAddDays(start,7);
        let note=def.note;
        if(def.name==='Bingo Draw' && count===2) note += ' Charming Glance: this run overlaps Oceanic Festival Aug 19–26, so Fruit spending can advance both events.';
        if(def.name==='Lucky Scratch' && count===2) note += ' Charming Glance: starts Aug 26 while Oceanic is still active; Material Realm activity can also advance Oceanic Beach Shovel objectives.';
        timelineData.push([start,serverDay,def.name,`${def.name} · ${count}`,`UNCONFIRMED recurring server-age projection · ${def.prep} · ${note}`,'event',end,'unconfirmed']);
      }
    });
    timelineData.sort((a,b)=>a[0].localeCompare(b[0]) || a[1]-b[1] || a[2].localeCompare(b[2]));
  }
  addRecurringEvents();

  let timelineFilter='all';
  const SERVER_START_ISO='2026-07-15';
  const PACIFIC_TZ='America/Los_Angeles';
  function isoDayNumber(iso){
    const [y,m,d]=iso.split('-').map(Number);
    return Math.floor(Date.UTC(y,m-1,d)/86400000);
  }
  function isoDayDiff(a,b){ return isoDayNumber(b)-isoDayNumber(a); }
  function displayDate(iso){
    const [y,m,d]=iso.split('-').map(Number);
    return new Date(Date.UTC(y,m-1,d,12));
  }

  function pacificClockParts(date=new Date()){
    const parts=Object.fromEntries(new Intl.DateTimeFormat('en-US',{timeZone:PACIFIC_TZ,year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',hourCycle:'h23'}).formatToParts(date).filter(p=>p.type!=='literal').map(p=>[p.type,p.value]));
    return {year:Number(parts.year),month:Number(parts.month),day:Number(parts.day),hour:Number(parts.hour)};
  }
  function currentResetIso(date=new Date()){
    const p=pacificClockParts(date);
    const iso=`${p.year}-${String(p.month).padStart(2,'0')}-${String(p.day).padStart(2,'0')}`;
    return p.hour>=6 ? iso : isoAddDays(iso,-1);
  }
  function eventIsActive(e,boundaryIso){
  if(e[5]!=='event' || !e[6] || e[0]>boundaryIso) return false;
  const exactExpiry=e[8];
  if(exactExpiry){
    const ms=Date.parse(exactExpiry);
    if(Number.isFinite(ms)) return Date.now()<ms;
  }
  return boundaryIso<e[6];
}
  function timelineFilterMatches(e){
    if(timelineFilter==='all') return true;
    if(timelineFilter==='maps') return e[5]==='region' || e[5]==='seasonal-map';
    return e[5]===timelineFilter;
  }

  function timelineSummaryText(e){
    const text=String((e&&e[4])||'').trim();
    const title=String((e&&e[3])||'');
    const type=String((e&&e[2])||'');
    // TIMELINE_PLAIN_EVENT_COPY_V1: user-facing cards summarize the event itself.
    // Research confidence/source prose stays in the maintained raw row when useful,
    // but CONFIRMED / UNCONFIRMED / PROJECTED-style audit language is not shown on cards.
    if(title==='Warlord’s Rest') return 'Player Lv.130 · Normal 3.55M · Hard 5M · Nightmare 6M';
    if(title==='Server Tournament') return e[0]==='2026-09-12' ? 'Registration opens Friday Sep. 11 · tournament Saturday Sep. 12.' : 'Registration opens the day before · tournament Saturday.';
    if(title==='Nexus Tournament · 4v4') return '4v4 Nexus Tournament · Top-4 qualification format; brackets and prediction phases are handled in game.';
    if(title==='Acme Nexus') return 'Loong Haven seasonal map · gateway to Aethyris.';
    if(title==='Aethyris opens') return 'Season 3 · Aethyris · Tier 5 · Skyrend Cliff, Unbroken Camp and Harmonic Crystal · Nexus grouping expands from 4 servers to an 8-server pool.';
    // TIMELINE_SUMMARY_PROVENANCE_CLEAN_V2: keep source/confidence wording in raw rows/comments only.
    if(title==='Aethyris area-unlock stockpile') return 'Gateway Key ×5 · Magic Drill ×2 · Water Mine ×2 · cloud key ×2 · hammer ×5';
    if(title==='Astral Odyssey') return 'Aethyris season map';
    if(title==='Abyssal Bastion') return 'Normal 20M · Hard 26M · Nightmare 30M · Purgatory 46M';
    if(title==='Aethyris Relic II') return 'Second Aethyris relic gacha';
    if(title==='Courtyard of Purification') return 'Normal 32.5M · Hard 43M · Nightmare 50.5M · Purgatory 75M';
    if(title==='Temple of Order') return 'Normal 55M · Hard 65M · Nightmare 82M · Purgatory 115M';
    if(title==='Aethyris Relic III') return 'Third Aethyris relic gacha';
    if(title==='Solar Spire') return 'Normal 84.5M · Hard 100M · Nightmare 120M · Purgatory 180M';
    if(title==='Sovereign’s Nest') return 'Normal 125M · Hard 145M · Nightmare 180M · Purgatory 250M · Abyss 350M';
    if(title==='Hapadi opens') return 'Season 4 · Hapadi';
    if(title==='Ingenious Clocktower') return 'Hapadi Day 1 · Normal · Hard 27M';
    if(title==='Tier 6 class advancement') return 'Player Lv.172 · Class Lv.280 · Tier 5 class Lv.50 · Hapadi Nine';
    if(title==='Hapadi area-unlock stockpile') return 'Gateway Key ×5 · Magic Drill ×2 · Water Mine ×2 · season item ×5';
    if(title==='Fantomon Resonance unlock') return 'Player Lv.180';
    if(title==='Pirate Galleon') return 'Hapadi Day 14 · Normal 35M · Hard 48M · Nightmare 57M · Purgatory 84M';
    if(title==='Grotesque Fairground') return 'Hapadi Day 15 season map';
    if(title==='Leviathan Submersible') return 'Hapadi Day 28 · Normal 62M · Hard 72M · Nightmare 87M · Purgatory 130M';
    if(title==='Crystal Spiral Tree') return 'Aethyris’s first dungeon · Sylvan Set · current older-server guidance lists Hard at 9M.';
    if(title==='Gift code · CRYSTAL'){const t=Date.parse(String((e&&e[8])||''));return `300 Raw Ore + 1 Stellatie · reported cutoff ${Number.isFinite(t)?localShortDateTimeLabel(t):'Sep. 15 source cutoff'}.`;}
    if(title==='Official Top-Up Platform events open') return 'Cumulative Top-up Lottery + Daily Top-up Sign-in open on the official top-up platform.';
    if(title==='Vegetables Fairy Collab Pt. 2') return 'Daily sign-in, Veggie Shop, Veggie Shuffle, Lemon Whale purification, Cabbage Dog Fantomon and Part 2 Visages.';
    if(title.startsWith('Oceanic Festival')) return 'Global Aug 18–31. Prioritize Beach Shovels; Bingo Draw 2 overlaps on Charming Glance, so Destiny Fruit spending can progress both events.';
    if(title.startsWith('Bingo Draw')) return 'Do dailies first; roughly 60–80 Destiny Fruits usually clears the normal board. Save extra Fruits for the next Bingo run if you finish early.';
    if(title.startsWith('Lucky Scratch')) return 'Spend saved Material Realm tools while Lucky Scratch is active to generate more scratch cards; bank tools during Feneck week for the next run.';
    if(title.startsWith('Weekly gift code')) return `2,000 Rolla + 120 Dawnium. Expired ${localShortDateTimeLabel('2026-08-25T05:00:00Z')}.`;
    if(title==='Gift code · Summer') return 'UNCONFIRMED cutoff: Summer gives 160 Dawnium and is reported valid through Sep 1; redeem promptly.';
    if(title==='Gift code · VEGGIE'){const t=Date.parse(String((e&&e[8])||''));return `Official Global Discord: 10 Rare Auroral Badges + 80 Dawnium. Expires ${Number.isFinite(t)?localShortDateTimeLabel(t):'at the stored source cutoff'}; redeem before then.`;}
    if(title.startsWith('Grand Treasure Hunt')){
      const reward=(text.match(/Lv\.5:\s*([^·.]+)/)||[])[1];
      return reward ? `Lv.5 reward: ${reward.trim()}. Auroradrasil Energy carries over.` : 'Check the Lv.5 reward before spending saved Auroradrasil Energy; unused Energy carries over.';
    }
    if(title==='Season 2 final-day prep') return 'Historical rollover note: the Bed EXP hold used 34 hours of natural accumulation plus the single 2-hour reset boost, filling the 36-hour Bed capacity.';
    if(title==='Loong Haven opens') return `Confirmed ${localShortDateTimeLabel(S1_END)}. Gates: Lv.106 T4; Lv.108 + Numbuville + Mythic duplicate for Fantomon Adult; Lv.116 Demonbind Tower.`;
    if(title==='Gear Refinement & Affix Transfer') return 'S2 feature: Mythic+ S2 gear can reroll or transfer affixes; S1 gear cannot transfer forward. Same-season transfer is free.';
    if(title==='Season 2 Day 1 checklist') return 'At S2 reset: claim rollover rewards, rank up first, push reachable statues, then spend saved Bed boosts, Stamina and Material Realm resources.';
    if(title==='Vegetable Fairy Part Two') return 'Vegetable Fairy Part Two event.';
    let displayText=text;
    if(/^(?:CONFIRMED|UNCONFIRMED|PROJECTED|EXPECTED|STRONGLY SUPPORTED|OFFICIAL GLOBAL NAME)/i.test(displayText)){
      const colon=displayText.indexOf(':');
      if(colon>=0 && colon<180) displayText=displayText.slice(colon+1).trim();
      displayText=displayText
        .replace(/^(?:CONFIRMED|UNCONFIRMED|PROJECTED|EXPECTED|STRONGLY SUPPORTED)\b[^.]{0,180}\.\s*/i,'')
        .replace(/\b(?:CONFIRMED|UNCONFIRMED|PROJECTED|STRONGLY SUPPORTED)\b/gi,'')
        .replace(/\s{2,}/g,' ')
        .trim();
    }
    if(displayText.length<=170) return displayText;
    const sentences=displayText.split(/\.\s+/).filter(Boolean);
    let summary=sentences[0]||displayText;
    if(summary.length<95 && sentences.length>1) summary += '. ' + sentences[1];
    if(summary.length>170) summary=summary.slice(0,167).replace(/\s+\S*$/,'')+'…';
    if(summary && !/[.!?…]$/.test(summary)) summary+='.';
    return summary;
  }
  // TIMELINE_SUMMARY_ONLY_V1: timeline cards never expose expandable research/details UI.
  // Full source/research text remains in timelineData for maintenance, while cards show only the concise summary.
  function timelineDetailHtml(e){
    const summary=timelineSummaryText(e);
    return `<p>${summary}</p>`;
  }
  function dedupeTimelineDetails(){
    const timeline=$('timeline');
    if(!timeline) return;
    timeline.querySelectorAll('.entry').forEach(entry=>{
      const details=[...entry.querySelectorAll('details.entryMore')];
      details.slice(1).forEach(el=>el.remove());
    });
  }
  /* TIMELINE_CURRENT_NEXT_SEASONS_V1
     Keep the visible roadmap focused: only the current season and the immediately
     following season are eligible for timeline cards. Historical seasons never come
     back through Show past; when a season rolls over, the window advances automatically. */
  const TIMELINE_SEASON_WINDOWS=[
    {key:'s1',label:'Season 1',start:1,end:46},
    {key:'s2',label:'Season 2 · Crossed Paths',start:47,end:113},
    {key:'s3',label:'Season 3 · Aethyris',start:114,end:225},
    {key:'s4',label:'Season 4 · Hapadi',start:226,end:334},
    {key:'s5',label:'Season 5 · Ignis',start:335,end:Infinity}
  ];
  function timelineSeasonScope(boundaryIso=currentResetIso()){
    const serverDay=Math.max(1,isoDayDiff(SERVER_START_ISO,boundaryIso)+1);
    let index=TIMELINE_SEASON_WINDOWS.findIndex(x=>serverDay>=x.start&&serverDay<=x.end);
    if(index<0) index=TIMELINE_SEASON_WINDOWS.length-1;
    const current=TIMELINE_SEASON_WINDOWS[index];
    const next=TIMELINE_SEASON_WINDOWS[index+1]||null;
    return {serverDay,current,next,minDay:current.start,maxDay:next?next.end:current.end};
  }
  function timelineDataForScope(boundaryIso=currentResetIso()){
    const scope=timelineSeasonScope(boundaryIso);
    return {scope,data:timelineData.filter(e=>{
      const day=Number(e?.[1]);
      return Number.isFinite(day)&&day>=scope.minDay&&day<=scope.maxDay;
    })};
  }

  function renderTimeline(){
    renderLocalTimeLabels();
    const boundaryIso=currentResetIso();
    const {scope,data:scopedTimelineData}=timelineDataForScope(boundaryIso);
    const showPast=$('showPast').checked;
    const filtered=scopedTimelineData.filter(e=>{
      const active=eventIsActive(e,boundaryIso);
      if(!showPast && e[0]<boundaryIso && !active) return false;
      return timelineFilterMatches(e);
    });
    const grouped=new Map(); filtered.forEach(e=>{if(!grouped.has(e[0])) grouped.set(e[0],[]); grouped.get(e[0]).push(e);});
    $('timeline').innerHTML=[...grouped.entries()].map(([date,entries])=>{
      const dt=displayDate(date); const first=entries[0];
      const month=dt.toLocaleString('en-US',{month:'short',timeZone:'UTC'}); const day=dt.getUTCDate(); const weekday=dt.toLocaleString('en-US',{weekday:'short',timeZone:'UTC'});
      const today=date===boundaryIso;
      const groupActive=entries.some(e=>eventIsActive(e,boundaryIso));
      const entrySeason=TIMELINE_SEASON_WINDOWS.find(x=>Number(first[1])>=x.start&&Number(first[1])<=x.end);
      const seasonDay=entrySeason?Math.max(1,Number(first[1])-entrySeason.start+1):1;
      const seasonNumber=entrySeason?TIMELINE_SEASON_WINDOWS.indexOf(entrySeason)+1:1;
      return `<article class="dayGroup${today?' today':''}${groupActive?' activeEvent':''}" data-date="${date}"><div class="dayMarker"><span>Server Day ${first[1]}</span><small class="seasonDayLabel">Season ${seasonNumber} Day ${seasonDay}</small><b>${today?'CURRENT RESET':groupActive?'ACTIVE EVENT':''}</b></div><div class="dateBlock"><span>${month}</span><strong>${day}</strong><small>${weekday}</small></div><div class="entryStack">${entries.map(e=>{const active=eventIsActive(e,boundaryIso);return `<div class="entry${active?' entry-active':''}"><span class="category category-${e[5]}">${e[2]}</span><div><p><b>${e[3]}</b>${active?'<span class="activePill">ACTIVE</span>':''}</p>${timelineDetailHtml(e)}</div></div>`;}).join('')}</div></article>`;
    }).join('') || '<div class="emptyBuild">No timeline entries match this filter.</div>';
    dedupeTimelineDetails();

    const serverDay=scope.serverDay;
    const fixedUpcoming=scopedTimelineData.find(e=>e[0]>=boundaryIso && e[5]!=='event') || scopedTimelineData.filter(e=>e[5]!=='event').at(-1) || null;
    const seasonDay=Math.max(1,serverDay-scope.current.start+1);
    const seasonNumber=Math.max(1,TIMELINE_SEASON_WINDOWS.indexOf(scope.current)+1);
    const milestoneName=fixedUpcoming?String(fixedUpcoming[3]):'No fixed milestone loaded';
    const milestoneDays=fixedUpcoming?Math.max(0,isoDayDiff(boundaryIso,fixedUpcoming[0])):null;
    const milestoneWhen=milestoneDays===null?'':milestoneDays===0?'today':milestoneDays===1?'1 day to go':`${milestoneDays} days to go`;
    $('timelineSummary').innerHTML=`<div><span>Server day</span><strong class="summaryNumber">${serverDay}</strong></div><div><span>Season ${seasonNumber} day</span><strong class="summaryNumber">${seasonDay}</strong></div><div><span>Next milestone</span><strong>${milestoneName}</strong>${milestoneWhen?`<small class="summaryMeta">${milestoneWhen}</small>`:''}</div>`;

    const activeEvents=timelineData.filter(e=>eventIsActive(e,boundaryIso));
    const live=$('timelineNow');
    if(live){
      const cards=activeEvents.map(e=>`<div class="timelineNowCard"><strong>${String(e[3]).replace(/\s*ACTIVE\s*$/i,'')}</strong><small>${timelineSummaryText(e)}</small></div>`).join('');
      live.innerHTML=`<div class="timelineNowInner"><div class="timelineNowHead"><b>Active now</b><span>Auto-updates at the ${nextResetLocalLabel()} local reset</span></div>${cards?`<div class="timelineNowGrid">${cards}</div>`:'<div class="timelineNowEmpty">No tracked multi-day events are active right now.</div>'}</div>`;
    }
  }
  function setupTimeline(){
    renderLocalTimeLabels();
    const timelinePanelState=[
      ['timelineCoverageDetails','sxs-timeline-panel-coverage'],
      ['recurringEventsDetails','sxs-timeline-panel-events'],
      ['ignisReferenceDetails','sxs-timeline-panel-ignis']
    ];
    timelinePanelState.forEach(([id,key])=>{
      const panel=$(id);
      if(!panel) return;
      let saved=null;
      try{ saved=localStorage.getItem(key); }catch(_){}
      panel.open=saved==='1';
      panel.addEventListener('toggle',()=>{try{localStorage.setItem(key,panel.open?'1':'0');}catch(_){}});
    });
    const filters=[['all','All'],['dungeon','Dungeons'],['class-advancement','Class'],['maps','Maps / Regions'],['fantomon','Fantomons'],['ancient-relic','Relics'],['feature','Features'],['event','Events']];
    $('timelineFilters').innerHTML=filters.map(([k,l])=>`<button data-filter="${k}" class="${k==='all'?'active':''}">${l}</button>`).join('');
    $('timelineFilters').addEventListener('click',e=>{const b=e.target.closest('button[data-filter]');if(!b)return;timelineFilter=b.dataset.filter;[...$('timelineFilters').children].forEach(x=>x.classList.toggle('active',x===b));renderTimeline();});
    $('showPast').addEventListener('change',renderTimeline);
    $('todayButton').addEventListener('click',()=>{const groups=[...$('timeline').querySelectorAll('.dayGroup')];const reset=currentResetIso();const target=groups.find(g=>g.classList.contains('today'))||groups.find(g=>g.dataset.date>=reset)||groups[0];if(target)target.scrollIntoView({behavior:'smooth',block:'center'});});
    renderTimeline();
    let timelineMinuteSignature='';
    const currentTimelineSignature=()=>{
      const boundary=currentResetIso();
      const active=timelineData.filter(e=>eventIsActive(e,boundary)).map(e=>`${e[0]}:${e[3]}`).join('|');
      return `${boundary}::${active}`;
    };
    timelineMinuteSignature=currentTimelineSignature();
    setInterval(()=>{
      if(document.hidden) return;
      renderLocalTimeLabels();
      const nextSignature=currentTimelineSignature();
      if(nextSignature!==timelineMinuteSignature){
        timelineMinuteSignature=nextSignature;
        renderTimeline();
      }
    },60_000);
  }


  // ---------- Builds ----------
  // Build library follows the live Charming Glance season boundary at the 6:00 AM Pacific reset.
  // S1 uses the current Tier III classes; S2 switches automatically to the existing Tier IV library.
  const S1_BUILD_CLASSES=['Berserker','Paladin','Archmage','Arcanist'];
  const S2_BUILD_CLASSES=['Destroyer','Dominator','Conqueror','Guardian'];
  const BUILD_CLASS_STORAGE_KEYS={s1:'sxs-build-class-s1',s2:'sxs-build-class-s2'};
  const BUILD_SEASON_VIEW_STORAGE_KEY='sxs-build-season-view';
  function buildSeasonKey(){ return 's2'; }
  function buildClassesForSeason(){ return S2_BUILD_CLASSES; }
  let currentBuildSeason='s2';
  try{
    if(currentBuildSeason==='s1'){
      const savedSeason=localStorage.getItem(BUILD_SEASON_VIEW_STORAGE_KEY);
      if(savedSeason==='s1'||savedSeason==='s2') currentBuildSeason=savedSeason;
    }
  }catch(_){}
  let currentClass='Conqueror';
  try{
    const classes=buildClassesForSeason(currentBuildSeason);
    const savedClass=localStorage.getItem(BUILD_CLASS_STORAGE_KEYS[currentBuildSeason]) || (currentBuildSeason==='s2'?localStorage.getItem('sxs-build-class'):null);
    if(classes.includes(savedClass)) currentClass=savedClass;
  }catch(_){}

    function buildHtmlS2(cls){
    if(cls==='Conqueror') return `
      <div class="guideSummary"><div><span>Elemental melee DPS</span><strong>Conqueror</strong><p>T4 pivots from the old Physical-first Berserker plan into Elemental damage, DEF ignore and repeatable attacks. Excellent in both bosses and dungeons.</p></div><p><b>Stat priority</b>ATK ≥ Elemental Mastery &gt; SPD on offensive main lines. Crit Rate → Crit DMG are the premium substats. Aim past 100% Crit because S2 PvE enemies carry Crit RES.</p></div>
      <div class="gearPanel"><div class="gearIntro"><span>Season 2 gearing</span><strong>Gear & stat priorities</strong><p>Keep large power upgrades, but protect excellent rolls for S2 affix inheritance. Physical Mastery becomes a niche old-build stat rather than the default.</p></div><div class="gearGrid"><div class="gearItem"><span>Main lines</span><p>Sword / Gauntlets / Boots: ATK ≥ Elemental Mastery &gt; SPD. Helmet / Chest: DEF ≥ Physical RES = Elemental RES &gt; HP.</p></div><div class="gearItem"><span>Best substats</span><p>Crit Rate% → Crit DMG% → Elemental Mastery / Accuracy% → SPD or HP/SPD-to-ATK conversion. ATK is useful but less scarce.</p></div><div class="gearItem"><span>Gem plan</span><p>Weapon: Obsidian &gt; Amethyst ≥ Ruby. Off-hand: Obsidian &gt; Amethyst ≥ Citrine. Boots: Amethyst &gt; Citrine. Armor: Moonstone. Helm: Citrine.</p></div><div class="gearItem"><span>Important breakpoint</span><p>S2 PvE enemies have about 18% Crit RES, so roughly 118% displayed Crit Rate is the practical 100%-crit target before dropping Crit support.</p></div></div></div>
      <div class="priorityPanel"><div class="priorityIntro"><span>Technique investment</span><strong>Only equipped Techniques</strong><p>Rank the techniques that actually occupy your standard Conqueror loadouts; swap-only utility stays in the build notes.</p></div><ol class="priorityList"><li><b>1</b><div><strong>Flickering Blade</strong><p>No cooldown, very high single-target ceiling, and it is equipped in every listed Conqueror build.</p></div></li><li><b>2</b><div><strong>Blade Storm</strong><p>Core T4 AoE and also equipped across every listed build.</p></div></li><li><b>3</b><div><strong>Flash Fire</strong><p>Reliable Elemental damage and a main-slot technique in dungeon, boss and PvP setups.</p></div></li><li><b>4</b><div><strong>Flame Aura</strong><p>Main-slot damage for the generic and boss builds. Darkness Descends remains the PvP/utility replacement shown below.</p></div></li></ol></div>
      <div class="priorityPanel"><div class="priorityIntro"><span>Charm investment</span><strong>Piercing Assault first</strong><p>These are all actually equipped in the listed builds. Soul Breaker and Soul Splash remain optional swaps, not core upgrade recommendations.</p></div><ol class="priorityList"><li><b>1</b><div><strong>Piercing Assault</strong><p>Primary T4 investment and equipped in every Conqueror build below.</p></div></li><li><b>2</b><div><strong>Tactical Adaptation</strong><p>Universal offensive/defensive value and equipped in every listed build.</p></div></li><li><b>3</b><div><strong>Insightful Eye</strong><p>Actually occupies a slot in every listed build until your S2 gear solves the Crit requirement.</p></div></li><li><b>4</b><div><strong>Indomitable Will / Blazing Clash</strong><p>Indomitable is the equipped dungeon/PvP safety slot; Blazing Clash is the equipped boss damage slot.</p></div></li></ol></div>
      <div class="buildGrid">
        <article class="buildCard"><header><div><h3>Generic / Dungeons</h3><p>Default all-content Elemental setup</p></div></header><div class="skillGroup"><span>Techniques</span><div><b>Flash Fire</b><b>Flame Aura</b><b>Flickering Blade</b><b>Blade Storm</b></div></div><div class="skillGroup"><span>Charms</span><div><b>Insightful Eye</b><b>Piercing Assault</b><b>Tactical Adaptation</b><b>Indomitable Will</b></div></div><ul><li><b>Offensive:</b> Indomitable Will → Soul Splash</li><li><b>Defensive/utility:</b> Flame Aura → Darkness Descends when mobility/dispel keeps you safer</li><li>Once Crit is solved, Insightful Eye → Soul Breaker</li></ul></article>
        <article class="buildCard"><header><div><h3>Boss / Dragon</h3><p>Single-target and long-fight damage</p></div></header><div class="skillGroup"><span>Techniques</span><div><b>Flame Aura</b><b>Blade Storm</b><b>Flash Fire</b><b>Flickering Blade</b></div></div><div class="skillGroup"><span>Charms</span><div><b>Insightful Eye</b><b>Piercing Assault</b><b>Tactical Adaptation</b><b>Blazing Clash</b></div></div><ul><li><b>Offensive:</b> high Crit → Insightful Eye → Crit Mastery</li><li><b>Defensive:</b> Blazing Clash → Indomitable Will</li><li>Nyxarchon is the safest raw-DPS lead Fantomon; Pandarial can front-load cooldowns later in S2</li></ul></article>
        <article class="buildCard"><header><div><h3>PvP / Mobility</h3><p>Dispel, reach and cheat-death</p></div></header><div class="skillGroup"><span>Techniques</span><div><b>Flash Fire</b><b>Darkness Descends</b><b>Flickering Blade</b><b>Blade Storm</b></div></div><div class="skillGroup"><span>Charms</span><div><b>Insightful Eye</b><b>Piercing Assault</b><b>Tactical Adaptation</b><b>Indomitable Will</b></div></div><ul><li><b>Offensive:</b> Crit-capped Insightful Eye → Soul Breaker</li><li><b>Defensive:</b> keep Indomitable Will; do not greed it away in serious PvP</li><li>Darkness Descends is preferred here over Flame Aura for movement + dispel</li></ul></article>
      </div><p class="buildSource">Research snapshot Aug 21, 2026 · <a href="https://www.prydwen.gg/sword-x-staff/guides/build-guide-conqueror" rel="noreferrer" target="_blank">Prydwen Conqueror ↗</a> · <a href="https://lootandwaifus.com/guides/sword-x-staff-how-to-play-duelist/" rel="noreferrer" target="_blank">Loot &amp; Waifus Duelist/Conqueror ↗</a></p>`;

    if(cls==='Guardian') return `
      <div class="guideSummary"><div><span>Tank / support / bruiser</span><strong>Guardian</strong><p>T4 finally gives Knight real taunt tools plus stronger Water/Light offense. The long-term identity is still protection: Block, DEF, shields, taunt control and party support.</p></div><p><b>Stat priority</b>Block is the premium substat. Sword/Boots value SPD heavily; defensive slots prioritize DEF, then HP/RES. Build damage only after the tank loop is stable.</p></div>
      <div class="gearPanel"><div class="gearIntro"><span>Season 2 gearing</span><strong>Gear & stat priorities</strong><p>Guardian has very different offensive and defensive slots. Do not flatten everything into one generic tank stat.</p></div><div class="gearGrid"><div class="gearItem"><span>Main lines</span><p>Sword: SPD &gt; ATK &gt; Physical Mastery &gt; Elemental Mastery. Gauntlets: DEF &gt; HP &gt; Physical/Elemental RES. Boots: SPD &gt; ATK &gt; Elemental/Physical Mastery.</p></div><div class="gearItem"><span>Best substats</span><p>Block Rate% → Block Rate + Block Efficiency → PvE/PvP DMG + DMG RES. Then flat DEF / SPD / HP and useful Crit.</p></div><div class="gearItem"><span>Gem plan</span><p>Weapon: Obsidian &gt; Amethyst ≥ Ruby. Off-hand: Moonstone &gt; Sapphire &gt; Citrine. Boots: Amethyst &gt; Citrine. Armor: Moonstone &gt; Sapphire/Beryl. Helm: Sapphire &gt; Citrine &gt; Beryl.</p></div><div class="gearItem"><span>Fantomon focus</span><p>Adult Aegiswing is the Guardian priority for tanking. Kels is excellent support (DEF down + dispel). Nyx adds damage/debuffs; Pandarial later adds opening-CD reduction and healing.</p></div></div></div>
      <div class="priorityPanel"><div class="priorityIntro"><span>Technique investment</span><strong>Swirling Blade first</strong><p>Current S2 Guardian testing consistently elevates Swirling Blade as the best T4 Technique investment because it works in the Water shell, shield builds and general PvE while still giving a shield.</p></div><ol class="priorityList"><li><b>1</b><div><strong>Swirling Blade</strong><p>The most reusable T4 damage Technique: strong single-target damage, Water synergy and a self-shield. It is also the first offensive flex into the dungeon tank bar.</p></div></li><li><b>2</b><div><strong>Valor Surge</strong><p>Long-lived party damage and cleanse utility; equipped in dungeon and Dragon/Chaos support.</p></div></li><li><b>3</b><div><strong>Heart of Challenge</strong><p>The core group-taunt slot in the default dungeon tank build.</p></div></li><li><b>4</b><div><strong>Luminous Shield</strong><p>Still central to the dungeon and reflect shells, though high-Block accounts can flex it more aggressively later.</p></div></li></ol></div>
      <div class="priorityPanel"><div class="priorityIntro"><span>Charm investment</span><strong>Soul Protection first</strong><p>Fresh S2 Guardian feedback is unusually consistent here: Soul Protection is the standout T4 Charm and remains useful across dungeons, Arena and Nexus-style team PvP.</p></div><ol class="priorityList"><li><b>1</b><div><strong>Soul Protection</strong><p>The best T4 Guardian investment: a massive opening shield that scales the whole shield/DEF loop and works in essentially every mode.</p></div></li><li><b>2</b><div><strong>Holy Aegis</strong><p>Universal DEF plus stronger DEF-based shields; excellent wherever Guardian is actually tanking.</p></div></li><li><b>3</b><div><strong>Iron Will</strong><p>Excellent damage reduction once Taunt is active, especially in dungeon and team-PvP tank bars.</p></div></li><li><b>4</b><div><strong>Oath of Vigil</strong><p>High-value group/PvP protection. One copy is already useful, so it ranks below the more universal personal-core investments.</p></div></li></ol></div>
      <div class="buildGrid">
        <article class="buildCard"><header><div><h3>Dungeon Tank</h3><p>Safest default party grid</p></div></header><div class="skillGroup"><span>Techniques</span><div><b>Valor Surge</b><b>Heart of Challenge</b><b>Luminous Shield</b><b>Desperate Protection</b></div></div><div class="skillGroup"><span>Charms</span><div><b>Iron Will</b><b>Holy Aegis</b><b>Block Awareness</b><b>Soul Protection</b></div></div><ul><li><b>Offensive:</b> Desperate Protection → Swirling Blade or Star Shattering Slash</li><li><b>Defensive:</b> Desperate Protection → Hamper Strike for more taunt uptime</li><li>If the party still folds, add Iron Fortress</li></ul></article>
        <article class="buildCard"><header><div><h3>Water / AoE</h3><p>Cold stacking with real damage</p></div></header><div class="skillGroup"><span>Techniques</span><div><b>Valor Surge</b><b>Swirling Blade</b><b>Lunarwater Threads</b><b>Raging Maelstrom</b></div></div><div class="skillGroup"><span>Charms</span><div><b>Frigid Aura</b><b>Defensive Assault</b><b>Frigid Glint</b><b>Potential Rebirth</b></div></div><ul><li><b>Offensive:</b> Potential Rebirth → Pursuit of Victory / high-investment Blade of Lament</li><li><b>Defensive:</b> keep Potential Rebirth or add a stronger tank charm when pushing deficits</li><li>Mostly AoE, but still respectable single-target damage</li></ul></article>
        <article class="buildCard"><header><div><h3>Dragon / Chaos Support</h3><p>Buff, cleanse and debuff support</p></div></header><div class="skillGroup"><span>Techniques</span><div><b>Valor Surge</b><b>Leap Attack</b><b>Holy Purification</b><b>Lunarwater Threads</b></div></div><div class="skillGroup"><span>Charms</span><div><b>Frigid Aura</b><b>Frigid Glint</b><b>Iron Fortress</b><b>Oath of Vigil</b></div></div><ul><li><b>Offensive:</b> no dispel needed → Holy Purification → Seismic Tide</li><li><b>Defensive:</b> retain Iron Fortress + Oath; Terragon lead if the team needs DMG reduction</li><li>Kels (adult) is excellent here for DEF down + dispel</li></ul></article>
        <article class="buildCard"><header><div><h3>Reflect / Solo PvE</h3><p>Old Tank &amp; Spank, still useful</p></div></header><div class="skillGroup"><span>Techniques</span><div><b>Valor Surge</b><b>Luminous Shield</b><b>Star Shattering Slash</b><b>Desperate Protection</b></div></div><div class="skillGroup"><span>Charms</span><div><b>Rebound</b><b>Holy Aegis</b><b>Block Mastery</b><b>Block Awareness</b></div></div><ul><li><b>Offensive:</b> enough Block → Block Awareness → Eye for an Eye</li><li><b>Defensive:</b> Luminous Shield → Guardian Ring / add Potential Rebirth</li><li>Pandarial can enable a more aggressive Light Sword Array variant later</li></ul></article>
      </div><p class="buildSource">Research snapshot Sep 2, 2026 · <a href="https://www.prydwen.gg/sword-x-staff/guides/build-guide-guardian" rel="noreferrer" target="_blank">Prydwen Guardian ↗</a></p>`;

    if(cls==='Destroyer') return `
      <div class="guideSummary"><div><span>Ranged elemental DPS</span><strong>Destroyer</strong><p>T4 is more specialized than Archmage: mixed Light/Wind/Fire handles general and boss content, pure Fire is the horde specialist, and Wind remains strong in PvP. Freeze is playable but less reliable.</p></div><p><b>Stat priority</b>ATK ≈ Elemental Mastery &gt; Crit &gt; SPD on Staff/Codex. Keep enough EM to avoid an underbuilt multiplier, but once EM is healthy, developed S2 accounts often gain more from flat ATK. Dummy-test close swaps.</p></div>
      <div class="gearPanel"><div class="gearIntro"><span>Season 2 gearing</span><strong>Gear & stat priorities</strong><p>Destroyer wants a balanced damage profile. EM supplies the elemental multiplier, but flat ATK keeps scaling every damaging Technique and becomes increasingly competitive once your EM pool is already strong.</p></div><div class="gearGrid"><div class="gearItem"><span>Main lines</span><p>Staff/Codex: ATK ≈ Elemental Mastery &gt; Crit &gt; SPD. Helmet/Chest: DEF/RES &gt; HP. Boots: ATK ≈ Elemental Mastery &gt; SPD. If two pieces are close, use the 50-round dummy test.</p></div><div class="gearItem"><span>Best substats</span><p>Crit Rate / Crit DMG &gt; ATK ≈ Elemental Mastery &gt; Accuracy &gt; SPD.</p></div><div class="gearItem"><span>Gem plan</span><p>Weapon &amp; Off-hand: Obsidian / Amethyst. Boots: Amethyst. Armor: Moonstone. Helm: Citrine; use Beryl/Sapphire mainly for conversion or power padding.</p></div><div class="gearItem"><span>Relic elements</span><p>Light is the safest general priority, Fire is excellent for horde content, and Wind is especially strong for PvP/control. Favor Affinity over Aegis on offensive relic slots.</p></div></div></div>
      <div class="priorityPanel"><div class="priorityIntro"><span>Technique investment</span><strong>Formation Breaker is #1</strong><p>Every ranked technique here is equipped in at least one listed Destroyer build; swap-only options stay in the card notes.</p></div><ol class="priorityList"><li><b>1</b><div><strong>Formation Breaker</strong><p>Universal party ATK support plus a chance to accelerate allies; appears in essentially every serious T4 setup.</p></div></li><li><b>2</b><div><strong>Thunder of Judgment</strong><p>Destroyer’s best T4 single-target nuke and it prioritizes large targets.</p></div></li><li><b>3</b><div><strong>Wind Blade Spiral</strong><p>Fast-cycling Wind damage; more efficient than older Hurricane-style options in sustained fights.</p></div></li><li><b>4</b><div><strong>Meteoric Flames</strong><p>Still a workhorse for both mixed AoE and pure Fire compositions.</p></div></li></ol></div>
      <div class="priorityPanel"><div class="priorityIntro"><span>Charm investment</span><strong>Universal first, Fire second</strong><p>Every ranked charm here is equipped in the builds below; Fire-specific pieces are ranked because they occupy the Fire Horde loadout.</p></div><ol class="priorityList"><li><b>1</b><div><strong>Rapid Cast</strong><p>Elemental Mastery plus opening cooldown acceleration—excellent across multiple Destroyer builds.</p></div></li><li><b>2</b><div><strong>Radiant Sear</strong><p>Core generic Destroyer damage proc and a staple of the Light/mixed setups.</p></div></li><li><b>3</b><div><strong>Fiery Burst</strong><p>The damage engine of the pure Fire horde build; scales hard with Crit frequency.</p></div></li><li><b>4</b><div><strong>Explosive Spirit</strong><p>Stacks Crit from Fire techniques and helps Fiery Burst trigger consistently. Mana Surge is the fallback.</p></div></li></ol></div>
      <div class="buildGrid">
        <article class="buildCard"><header><div><h3>General AoE</h3><p>Mixed Wind/Fire wave clear</p></div></header><div class="skillGroup"><span>Techniques</span><div><b>Formation Breaker</b><b>Howling Hurricane</b><b>Meteoric Flames</b><b>Wind Blade Spiral</b></div></div><div class="skillGroup"><span>Charms</span><div><b>Rapid Cast</b><b>Void Bubble</b><b>Cyclone Lament</b><b>Radiant Sear</b></div></div><ul><li><b>Offensive:</b> safe content → Void Bubble → Mana Surge / another damage charm</li><li><b>Defensive:</b> keep Void Bubble when pushing deficits</li><li>Cyclone Lament benefits from running two Wind techniques here</li></ul></article>
        <article class="buildCard"><header><div><h3>Boss / Single Target</h3><p>Default S2 boss setup</p></div></header><div class="skillGroup"><span>Techniques</span><div><b>Formation Breaker</b><b>Divine Wrath</b><b>Wind Blade Spiral</b><b>Thunder of Judgment</b></div></div><div class="skillGroup"><span>Charms</span><div><b>Rapid Cast</b><b>Void Bubble</b><b>Mana Surge</b><b>Radiant Sear</b></div></div><ul><li><b>Offensive:</b> Void Bubble → another damage charm when survival is irrelevant</li><li><b>Defensive:</b> Mana Surge → Overload Protection</li><li><b>Test slot:</b> Wind Blade Spiral, Meteoric Flames, or Wind's Delight can win depending on ranks and Radiant Sear proc rate; use a long dummy test</li></ul></article>
        <article class="buildCard"><header><div><h3>Fire Horde</h3><p>Best when enemy count is the problem</p></div></header><div class="skillGroup"><span>Techniques</span><div><b>Formation Breaker</b><b>Fiery Star Trail</b><b>Fireball</b><b>Meteoric Flames</b></div></div><div class="skillGroup"><span>Charms</span><div><b>Rapid Cast</b><b>Void Bubble</b><b>Explosive Spirit</b><b>Fiery Burst</b></div></div><ul><li><b>Offensive:</b> strong gear → Void Bubble → Radiant Sear / extra Fire offense</li><li><b>Defensive:</b> retain Void Bubble; Fiery Rejuvenation is a sustain alternative in long Fire fights</li><li>Crit Rate is especially important because Fiery Burst procs from Fire crits</li></ul></article>
        <article class="buildCard"><header><div><h3>Freeze / Water</h3><p>Playable control variant, not the boss meta</p></div></header><div class="skillGroup"><span>Techniques</span><div><b>Flowing Doom</b><b>Water Assault</b><b>Frosty Nova</b><b>Ice Spike</b></div></div><div class="skillGroup"><span>Charms</span><div><b>Rapid Cast</b><b>Void Bubble</b><b>Shattering Ice</b><b>Water to Ice</b></div></div><ul><li><b>Offensive/control:</b> Ice Spike → Aqua Vortex first slot for more Freeze setup</li><li><b>Defensive:</b> keep Void Bubble</li><li>Boss Freeze is limited until the white gauge is broken, so do not over-invest just for bosses</li></ul></article>
      </div><p class="buildSource">Research snapshot Aug 31, 2026 · <a href="https://www.prydwen.gg/sword-x-staff/guides/build-guide-destroyer" rel="noreferrer" target="_blank">Prydwen Destroyer ↗</a> · <a href="https://www.reddit.com/r/SwordxStaff_Official/comments/1vdjbo4/better_destroyer_builds/" rel="noreferrer" target="_blank">S2 community testing ↗</a> · <a href="https://lootandwaifus.com/guides/sword-x-staff-how-to-play-sorcerer/" rel="noreferrer" target="_blank">Loot &amp; Waifus ↗</a></p>`;

    if(cls==='Dominator') return `
      <div class="guideSummary dominatorGuideSummary"><div><span>Dark DPS / healer / support</span><div class="dominatorHeadingRow"><strong>Dominator</strong><div class="dominatorModeTabs" role="group" aria-label="Dominator build role"><button type="button" data-dominator-mode="dps">DPS</button><button type="button" data-dominator-mode="heals">Heals</button></div></div><p>T4 is a difficult DPS tier for Sage because Erosion needs high Effect Hit Rate and summons are easier to kill. Healing/support gets meaningful upgrades and remains the most reliable role.</p></div><p><b>Stat priority</b>DPS: Effect Hit Rate ≥ Elemental Mastery ≥ ATK &gt; SPD. Healer: SPD &gt; Effect Hit Rate &gt; Elemental Mastery &gt; ATK. Do not use one gear priority for both jobs.</p></div>
      <div class="gearPanel"><div class="gearIntro"><span>Season 2 gearing</span><strong>Two gear profiles</strong><p>Dominator is the class where a DPS preset and a healer preset are genuinely worth maintaining.</p></div><div class="gearGrid"><div class="gearItem"><span>DPS main lines</span><p>Staff/Orb: Effect Hit Rate ≥ Elemental Mastery ≥ ATK &gt; SPD. Boots: Elemental Mastery &gt; ATK &gt; SPD. Defensive slots: DEF/RES &gt; HP.</p></div><div class="gearItem"><span>Healer main lines</span><p>Staff/Orb: SPD &gt; Effect Hit Rate &gt; Elemental Mastery &gt; ATK. Helmet/Chest favor HP first, then DEF/RES. Boots: SPD &gt; Elemental Mastery &gt; ATK.</p></div><div class="gearItem"><span>Substats</span><p>DPS: Crit+Accuracy / Crit+Crit DMG / ailment damage, then EHR and conversions. Healer: DMG RES + Healing, Block packages, Healing Boost, then SPD/HP.</p></div><div class="gearItem"><span>Gem plan</span><p>Healer: Amethyst weapon, Amber off-hand/helm/boots, Moonstone armor. DPS: Obsidian weapon/off-hand, Citrine helm, Moonstone armor, Amethyst boots.</p></div></div></div>
      <div class="priorityPanel" data-dominator-role="heals"><div class="priorityIntro"><span>Core support investment</span><strong>Phantom Light is mandatory</strong><p>These are all equipped in the Healing/Group or Carry Support builds below, not standalone wishlist recommendations.</p></div><ol class="priorityList"><li><b>1</b><div><strong>Phantom Light</strong><p>Healing boost plus overheal-to-shield conversion. The must-have Dominator healer Charm.</p></div></li><li><b>2</b><div><strong>Rejuvenating Rain</strong><p>Repeatable single-target heal and a clean answer to low-HP allies.</p></div></li><li><b>3</b><div><strong>Mantra of Blessings</strong><p>High-value carry buff for co-op and scoring content when raw survival is already handled.</p></div></li><li><b>4</b><div><strong>Decoy Clone</strong><p>Excellent hypercarry/scoring utility when your team can exploit the clone connection and positioning.</p></div></li></ol></div>
      <div class="priorityPanel" data-dominator-role="dps"><div class="priorityIntro"><span>Core DPS investment</span><strong>EHR decides the build</strong><p>These are all equipped in the listed Single Target or AoE/Erosion builds; situational alternates remain in the build notes.</p></div><ol class="priorityList"><li><b>1</b><div><strong>Dark Starburst</strong><p>Reliable multi-hit single-target damage that does not require Erosion stacks to function.</p></div></li><li><b>2</b><div><strong>Shadow of Termination</strong><p>Key single-target Dark finisher/core technique.</p></div></li><li><b>3</b><div><strong>Shadow Erosion</strong><p>Core DPS Charm when your Effect Hit Rate is high enough to land the status reliably.</p></div></li><li><b>4</b><div><strong>Linked Misfortune</strong><p>Standard Erosion/Dark damage package piece across both ST and AoE builds.</p></div></li></ol></div>
      <div class="buildGrid">
        <article class="buildCard" data-dominator-role="dps"><header><div><h3>Single Target</h3><p>Reliable hybrid before perfect EHR</p></div></header><div class="skillGroup"><span>Techniques</span><div><b>Dark Bullet</b><b>Dark Starburst</b><b>Chaos Rune</b><b>Shadow of Termination</b></div></div><div class="skillGroup"><span>Charms</span><div><b>Shadow Vengeance</b><b>Night's Blessing</b><b>Shadow Erosion</b><b>Linked Misfortune</b></div></div><ul><li><b>Offensive:</b> high EHR → Chaos Rune → Mana Blast</li><li><b>Defensive:</b> retain Shadow Vengeance</li><li>Frenzy Totem + Soul Pact Resonance is another offensive variant depending on rarity/stats</li></ul></article>
        <article class="buildCard" data-dominator-role="dps"><header><div><h3>AoE / Erosion</h3><p>Still the old Arcanist AoE core</p></div></header><div class="skillGroup"><span>Techniques</span><div><b>Mana Blast</b><b>Dark Bullet</b><b>Abyssal Hand</b><b>Shadow Impact</b></div></div><div class="skillGroup"><span>Charms</span><div><b>Shadow Vengeance</b><b>Night's Blessing</b><b>Shadow Erosion</b><b>Linked Misfortune</b></div></div><ul><li><b>Offensive:</b> once survival is safe, Shadow Vengeance → Soul Pact Resonance / offense</li><li><b>Defensive:</b> keep Shadow Vengeance</li><li>T4 adds no new dedicated AoE technique/charm package for Dominator</li></ul></article>
        <article class="buildCard" data-dominator-role="heals"><header><div><h3>Healing / Group</h3><p>Best all-around Dominator role</p></div></header><div class="skillGroup"><span>Techniques</span><div><b>Waterling Summon</b><b>Rejuvenating Rain</b><b>Radiant Restoration</b><b>Frenzy Totem</b></div></div><div class="skillGroup"><span>Charms</span><div><b>Phantom Light</b><b>Healing Mastery</b><b>Overhealing</b><b>FLEX</b></div></div><ul><li><b>Offensive/support:</b> FLEX → Mantra of Blessings when the party is stable</li><li><b>Defensive:</b> FLEX → Resurrection if allies die, or Shadow Vengeance if you die</li><li>Need more healing: Frenzy Totem → Healing Touch</li></ul></article>
        <article class="buildCard" data-dominator-role="heals"><header><div><h3>Carry Support</h3><p>Scoring / hypercarry utility</p></div></header><div class="skillGroup"><span>Core pieces</span><div><b>Mantra of Blessings</b><b>Decoy Clone</b><b>Rejuvenating Rain</b><b>Radiant Restoration</b></div></div><div class="skillGroup"><span>Support shell</span><div><b>Phantom Light</b><b>Healing Mastery</b><b>Resurrection / Overhealing</b><b>Flex</b></div></div><ul><li><b>Offensive/support:</b> favor Mantra + Decoy when a stronger DPS is carrying score</li><li><b>Defensive:</b> remove the greed slot for Resurrection / Shadow Vengeance</li><li>Pandarial later in S2 is a strong hybrid lead because opening CD reduction can enable earlier healing</li></ul></article>
      </div><p class="buildSource">Research snapshot Aug 21, 2026 · <a href="https://www.prydwen.gg/sword-x-staff/guides/build-guide-dominator" rel="noreferrer" target="_blank">Prydwen Dominator ↗</a> · <a href="https://lootandwaifus.com/guides/sword-x-staff-how-to-play-sage/" rel="noreferrer" target="_blank">Loot &amp; Waifus Sage/Dominator ↗</a></p>`;

    return '';
  }

  const DOMINATOR_BUILD_MODE_KEY='sxs-build-dominator-mode';
  let dominatorBuildMode='dps';
  try{
    const saved=localStorage.getItem(DOMINATOR_BUILD_MODE_KEY);
    if(saved==='dps'||saved==='heals') dominatorBuildMode=saved;
  }catch(_){}
  function applyDominatorBuildMode(){
    const root=$('buildContent');
    if(!root || currentClass!=='Dominator') return;
    root.querySelectorAll('[data-dominator-mode]').forEach(btn=>{
      const active=btn.dataset.dominatorMode===dominatorBuildMode;
      btn.classList.toggle('active',active);
      btn.setAttribute('aria-pressed',String(active));
    });
    root.querySelectorAll('[data-dominator-role]').forEach(el=>{
      el.hidden=el.dataset.dominatorRole!==dominatorBuildMode;
    });
  }

  function buildHtml(cls){ return buildSeasonKey()==='s1'?buildHtmlS1(cls):buildHtmlS2(cls); }
  function syncBuildSeason(){
    const nextSeason=buildSeasonKey();
    const classes=buildClassesForSeason(nextSeason);
    if(nextSeason!==currentBuildSeason || !classes.includes(currentClass)){
      currentBuildSeason=nextSeason;
      let saved=null;
      try{ saved=localStorage.getItem(BUILD_CLASS_STORAGE_KEYS[nextSeason]) || (nextSeason==='s2'?localStorage.getItem('sxs-build-class'):null); }catch(_){}
      currentClass=classes.includes(saved)?saved:classes[0];
    }
    return classes;
  }
  function renderBuilds(){
    const classes=syncBuildSeason();
    const s1=currentBuildSeason==='s1';
    if($('buildSeasonLabel')) $('buildSeasonLabel').textContent=s1?'Season 1 · Tier III build guide':'Season 2 · Tier IV build guide';
    if($('buildSeasonNote')) $('buildSeasonNote').textContent=s1
      ? 'Showing the live Season 1 / Tier III meta. This section switches to Tier IV automatically at the Aug 30, 6:00 AM Pacific reset.'
      : 'Season 2 / Tier IV is live. Your selected class tab is remembered separately for each season.';
    $('classTabs').innerHTML=classes.map(c=>`<button class="${c===currentClass?'active':''}" data-class="${c}">${c}</button>`).join('');
    $('buildContent').innerHTML=buildHtml(currentClass);
    applyDominatorBuildMode();
  }
  let buildsInitialized=false;
  function setupBuilds(){
    $('classTabs').addEventListener('click',e=>{
      const b=e.target.closest('button[data-class]');
      if(!b)return;
      if(b.dataset.class===currentClass)return;
      currentClass=b.dataset.class;
      try{localStorage.setItem(BUILD_CLASS_STORAGE_KEYS[currentBuildSeason],currentClass);}catch(_){}
      renderBuilds();
    });
    renderBuilds();
    buildsInitialized=true;
    setInterval(()=>{ if(!document.hidden && buildsInitialized && buildSeasonKey()!==currentBuildSeason) renderBuilds(); },60_000);
  }

  // PERFORMANCE_STABILIZATION_V1
  // Dead S1 build-template blob removed after the S2 cutover.

  // SEASONAL_BUILD_OVERRIDE_V1
  // Keep the live Builds section on T3/S1 until the Aug 30 6:00 AM Pacific reset,
  // then switch automatically to the existing T4/S2 library.
  const S1_BUILD_CLASSES_LIVE=['Berserker','Paladin','Archmage','Arcanist'];
  const S2_BUILD_CLASSES_LIVE=['Destroyer','Dominator','Conqueror','Guardian'];
  const BUILD_SEASON_STORAGE_KEYS={s1:'sxs-build-class-s1',s2:'sxs-build-class-s2'};
  const buildHtmlT4Live=buildHtmlS2;
  function liveBuildSeason(){ return 's2'; }
  function liveBuildClasses(){ return S2_BUILD_CLASSES_LIVE; }
  function liveBuildStorageKey(){ return BUILD_SEASON_STORAGE_KEYS[liveBuildSeason()]; }
  function renderBuildSeasonToggle(){
    const toggle=$('buildSeasonToggle');
    if(!toggle) return;
    const forcedS2=buildSeasonKey()==='s2';
    const season=liveBuildSeason();
    toggle.classList.toggle('s2Only',forcedS2);
    toggle.querySelectorAll('button[data-build-season]').forEach(btn=>{
      const key=btn.dataset.buildSeason;
      btn.hidden=forcedS2&&key==='s1';
      const active=key===season;
      btn.classList.toggle('active',active);
      btn.setAttribute('aria-pressed',String(active));
    });
  }
  function selectBuildSeason(key){
    if(buildSeasonKey()==='s2') key='s2';
    if(key!=='s1'&&key!=='s2') return;
    currentBuildSeason=key;
    try{localStorage.setItem(BUILD_SEASON_VIEW_STORAGE_KEY,key);}catch(_){}
    currentClass='';
    normalizeLiveBuildClass();
    renderBuilds();
    setSection('builds');
  }
  function normalizeLiveBuildClass(){
    const list=liveBuildClasses();
    if(list.includes(currentClass)) return;
    let saved=null;
    try{
      saved=localStorage.getItem(liveBuildStorageKey());
      if(!saved && liveBuildSeason()==='s2') saved=localStorage.getItem('sxs-build-class');
    }catch(_){}
    currentClass=list.includes(saved)?saved:list[0];
  }
  buildHtml=function(cls){ return liveBuildSeason()==='s1'?buildHtmlS1(cls):buildHtmlT4Live(cls); };
  /* BUILD_SWITCH_NO_FLICKER_V1
     Class switching used to destroy/recreate BOTH the class tabs and the full build tree, then
     a later requestAnimationFrame performed the META transform. That produced a visible repaint:
     raw build -> activity/role build. Keep the tab nodes stable, cache parsed class templates,
     mount one detached clone atomically, and ask the META layer to finish synchronously before
     the browser gets a chance to paint the new class. */
  const BUILD_TEMPLATE_CACHE=new Map();
  let buildTemplateWarmKey='';
  function buildTemplateForClass(cls){
    const key=`${liveBuildSeason()}|${cls}`;
    let template=BUILD_TEMPLATE_CACHE.get(key);
    if(!template){
      template=document.createElement('template');
      template.innerHTML=buildHtml(cls);
      BUILD_TEMPLATE_CACHE.set(key,template);
    }
    return template;
  }
  function syncBuildClassTabs(list){
    const tabs=$('classTabs');
    const signature=`${liveBuildSeason()}|${list.join('|')}`;
    if(tabs.dataset.buildClassSignature!==signature){
      tabs.innerHTML=list.map(c=>`<button type="button" role="tab" aria-selected="${c===currentClass}" class="${c===currentClass?'active':''}" data-class="${c}">${c}</button>`).join('');
      tabs.dataset.buildClassSignature=signature;
    }else{
      tabs.querySelectorAll('button[data-class]').forEach(btn=>{
        const active=btn.dataset.class===currentClass;
        btn.classList.toggle('active',active);
        btn.setAttribute('aria-selected',String(active));
      });
    }
  }
  function warmBuildTemplates(list){
    const key=`${liveBuildSeason()}|${list.join('|')}`;
    if(buildTemplateWarmKey===key) return;
    buildTemplateWarmKey=key;
    const work=()=>list.forEach(cls=>buildTemplateForClass(cls));
    if('requestIdleCallback' in window) requestIdleCallback(work,{timeout:500});
    else setTimeout(work,0);
  }
  renderBuilds=function(){
    if(buildSeasonKey()==='s2') currentBuildSeason='s2';
    normalizeLiveBuildClass();
    renderBuildSeasonToggle();
    const list=liveBuildClasses();
    const s1=liveBuildSeason()==='s1';
    const label=document.querySelector('#buildsSection .sectionHeading span');
    const note=document.querySelector('#buildsSection .sectionHeading>p');
    if(label) label.textContent=s1?'Season 1 · Tier III build guide':'Season 2 · Tier IV build guide';
    if(note) note.textContent=s1
      ? 'Showing the live Season 1 / Tier III meta. This switches to Tier IV automatically at the Aug 30, 6:00 AM Pacific reset.'
      : 'Season 2 / Tier IV is live. Your selected class tab is remembered separately for each season.';
    syncBuildClassTabs(list);
    const host=$('buildContent');
    const template=buildTemplateForClass(currentClass);
    host.replaceChildren(template.content.cloneNode(true));
    applyDominatorBuildMode();
    /* BUILD_VISUAL_STABILITY_V2
       The recording exposed several post-render stages after a class click. Finish all of them
       synchronously so the browser gets only the final class layout. META first creates the final
       activity cards. Rich fingerprints those headings and creates the priority pair/stats panel.
       META then runs once more to re-anchor its activity selector after the newly-created priority
       pair for Guardian/Dominator. Roll populates the stats panel and Hero performs the final
       two-column summary/reflow last. */
    if(typeof window.__applyBuildMetaNow==='function') window.__applyBuildMetaNow();
    if(typeof window.__applyBuildRichNow==='function') window.__applyBuildRichNow();
    if(typeof window.__applyBuildMetaNow==='function') window.__applyBuildMetaNow();
    if(typeof window.__applyBuildRollNow==='function') window.__applyBuildRollNow();
    if(typeof window.__applyBuildHeroNow==='function') window.__applyBuildHeroNow();
    warmBuildTemplates(list);
  };
  setupBuilds=function(){
    null?.addEventListener?.('click',e=>{
      const b=e.target.closest('button[data-build-season]');
      if(!b)return;
      e.preventDefault();
      e.stopPropagation();
      selectBuildSeason(b.dataset.buildSeason);
    });
    $('classTabs').addEventListener('click',e=>{
      const b=e.target.closest('button[data-class]');
      if(!b)return;
      if(b.dataset.class===currentClass)return;
      currentClass=b.dataset.class;
      try{localStorage.setItem(liveBuildStorageKey(),currentClass);}catch(_){}
      renderBuilds();
    });
    $('buildContent').addEventListener('click',e=>{
      const b=e.target.closest('button[data-dominator-mode]');
      if(!b || currentClass!=='Dominator') return;
      dominatorBuildMode=b.dataset.dominatorMode==='heals'?'heals':'dps';
      try{localStorage.setItem(DOMINATOR_BUILD_MODE_KEY,dominatorBuildMode);}catch(_){}
      applyDominatorBuildMode();
    });
    renderBuilds();
    let lastBuildSeasonTick=liveBuildSeason();
    setInterval(()=>{
      if(document.hidden||!buildsInitialized) return;
      const beforeClass=currentClass;
      const beforeSeason=lastBuildSeasonTick;
      normalizeLiveBuildClass();
      const afterSeason=liveBuildSeason();
      if(beforeClass!==currentClass || beforeSeason!==afterSeason) renderBuilds();
      lastBuildSeasonTick=afterSeason;
    },60_000);
  };

  // ---------- Navigation/theme ----------
  let calculatorInitialized=false;
  let calculatorUpdateTimer=null;
  function initializeBuildsIfNeeded(){
    if(buildsInitialized) return;
    buildsInitialized=true;
    renderBuilds();
  }
  function initializeCalculatorIfNeeded(){
    if(calculatorInitialized) return;
    // Paint the lightweight season-specific chrome immediately on refresh before
    // the optimizer starts. This prevents stale S1 fallback text from flashing
    // while a saved S2 plan is being restored and solved.
    renderCalculatorSeasonChrome(activeCalcConfig());
    const status=$('optimizerSummary');
    if(status) status.textContent='Calculating your saved season plan…';
    // Let the Calculator tab paint before the expensive optimizer starts.
    requestAnimationFrame(()=>setTimeout(()=>{
      if(calculatorInitialized) return;
      calculatorInitialized=true;
      updateCalculator();
    },0));
  }
  function scheduleCalculatorUpdate(delay=120){
    if(!calculatorInitialized) return;
    clearTimeout(calculatorUpdateTimer);
    calculatorUpdateTimer=setTimeout(()=>{calculatorUpdateTimer=null;updateCalculator();},delay);
  }
  const SECTION_STORAGE_KEY='sxs-active-section';
  function setSection(name){
    const map={timeline:'timelineSection',builds:'buildsSection',companions:'companionsSection',calculator:'calculatorSection'};
    if(!map[name]) name='timeline';
    const activeSection=document.querySelector('.sectionSwitch button[data-section].active')?.dataset.section;
    if(activeSection===name && !$(map[name]).hidden) return;
    document.querySelectorAll('.siteSection').forEach(s=>s.hidden=true);
    $(map[name]).hidden=false;
    document.querySelectorAll('.sectionSwitch button[data-section]').forEach(b=>{const active=b.dataset.section===name;b.classList.toggle('active',active);b.setAttribute('aria-selected',String(active));});
    try{ localStorage.setItem(SECTION_STORAGE_KEY,name); }catch(_){}
    window.scrollTo({top:0,behavior:'smooth'});
    if(name==='builds') initializeBuildsIfNeeded();
    if(name==='calculator') initializeCalculatorIfNeeded();
  }
  function updateThemeButton(){ $('themeToggle').textContent=document.documentElement.dataset.theme==='dark'?'☀':'☾'; }
  function setupNavigation(){
    document.querySelector('.sectionSwitch').addEventListener('click',e=>{const b=e.target.closest('button[data-section]');if(b)setSection(b.dataset.section);});
    document.querySelectorAll('[data-open-section]').forEach(b=>b.addEventListener('click',()=>setSection(b.dataset.openSection)));
    $('themeToggle').addEventListener('click',()=>{document.documentElement.dataset.theme=document.documentElement.dataset.theme==='dark'?'light':'dark';updateThemeButton();saveState();});
    updateThemeButton();
  }

  function setupCalculator(){
    document.getElementById('calculatorSection')?.addEventListener('focusin',e=>{
      if(e.target?.matches?.('input') && e.target.id!=='targetStars' && e.target.id!=='finishEarlyDays'){
        // PERFORMANCE_STABILIZATION_V1: age under the pre-edit rates, but do not run the
        // expensive optimizer just for tabbing/clicking between account-state fields.
        // Target Primostars is only a goal selector and must not mutate the snapshot clock.
        rollSnapshotForward(Date.now(),true);
      }
    });
    // Heavy optimizer work only commits after the user finishes editing a field.
    // Clicking/Tabbing out fires `change`; Enter deliberately blurs the field so it commits too.
    // Discrete selectors/toggles still update immediately.
    INPUT_IDS.forEach(id=>{
      const el=$(id);
      if(!el) return;
      if(id==='finishEarlyDays'){
        /* FINISH_EARLY_COMMIT_ON_BLUR_V1
           Finish Early can trigger an expensive optimizer solve, so never recalculate while
           the user is still typing or clicking the number spinner. Commit only when editing
           is explicitly finished: Enter blurs the field; Tab and clicking/tapping elsewhere
           naturally fire blur. This is a planning preference and never moves snapshot time. */
        const commitFinishEarly=()=>{
          const value=finishEarlyDaysValue();
          el.value=String(value);
          resetMaxAchievableUi();
          saveState();
          scheduleCalculatorUpdate(0);
        };
        el.addEventListener('blur',commitFinishEarly);
        el.addEventListener('keydown',ev=>{
          if(ev.key==='Enter'){
            ev.preventDefault();
            el.blur();
          }
        });
        return;
      }
      if(id==='staminaMode'){
        el.addEventListener('change',()=>{resetMaxAchievableUi();markManualSnapshot(id);scheduleCalculatorUpdate(0);});
        return;
      }
      el.addEventListener('change',()=>{
        normalizeCompactNumberInput(id);
        if(id==='targetStars'){
          saveState();
          if($('optimizerSummary')) $('optimizerSummary').textContent='Updating goal…';
          requestAnimationFrame(()=>scheduleCalculatorUpdate(0));
          return;
        }
        resetMaxAchievableUi();
        markManualSnapshot(id);
        scheduleCalculatorUpdate(0);
      });
      el.addEventListener('keydown',e=>{
        if(e.key==='Enter'){
          e.preventDefault();
          el.blur();
        }
      });
    });
    /* MAIN_RUNTIME_REPAIR_V1
       Restore the calculator setup tail and startup sequence. A build-role patch had
       accidentally replaced this block, preventing navigation/timeline initialization. */
    CHECK_IDS.forEach(id=>$(id)?.addEventListener('change',()=>{
      resetMaxAchievableUi();
      markManualSnapshot(id);
      saveState();
      if(calculatorInitialized) scheduleCalculatorUpdate(0);
      else initializeCalculatorIfNeeded();
    }));
    PANEL_OPEN_IDS.forEach(id=>$(id)?.addEventListener('toggle',saveState));
    $('s2TargetPresets')?.addEventListener('click',e=>{
      const btn=e.target.closest?.('[data-s2-target]');
      if(!btn || activeCalcConfig().key!=='s2') return;
      $('targetStars').value=btn.dataset.s2Target;
      resetMaxAchievableUi();
      saveState();
      $('s2TargetPresets')?.querySelectorAll('[data-s2-target]').forEach(x=>x.classList.toggle('active',x===btn));
      if($('optimizerSummary')) $('optimizerSummary').textContent='Updating goal…';
      requestAnimationFrame(()=>scheduleCalculatorUpdate(0));
    });
    /* S2_ROLLOVER_HEADER_RESET_V1 */
    $('confirmSeasonSnapshot')?.addEventListener('click',()=>{resetMaxAchievableUi();confirmCurrentSeasonSnapshot();});
    $('resetSeasonSnapshot')?.addEventListener('click',()=>{resetMaxAchievableUi();resetCalculator();});
    $('findMaxStars')?.addEventListener('click',findMaxAchievableStars);
    $('finishEarlyMax')?.addEventListener('click',findMaxFinishEarly);
    $('targetMessage')?.addEventListener('click',e=>{
      const btn=e.target.closest?.('.applyRealmRecommendation');
      if(btn) applyRecommendedRealmRefreshes(btn);
    });
    $('copyPlan')?.addEventListener('click',copyPlan);
    $('resetCalc')?.addEventListener('click',()=>{resetMaxAchievableUi();resetCalculator();});
    setInterval(()=>{
      if(document.hidden||!calculatorInitialized) return;
      rollSnapshotForward(Date.now(),true);
      if(!document.getElementById('calculatorSection')?.hidden) scheduleCalculatorUpdate(0);
    },60_000);
  }

  loadState();
  setupNavigation();
  let initialSection='timeline';
  try{
    const savedSection=localStorage.getItem(SECTION_STORAGE_KEY);
    if(['timeline','builds','companions','calculator'].includes(savedSection)) initialSection=savedSection;
  }catch(_){}
  setSection(initialSection);
  setupTimeline();
  setupBuilds();
  setupCalculator();
})();
