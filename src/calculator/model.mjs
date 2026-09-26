// Scoring, progression tables and resource-cost calculations. No DOM or storage.
import { countFuturePacificResets } from '../time.mjs';
import { S1_END, S2_END, seasonKeyAt } from '../season-clock.mjs';

export const STORAGE_KEY = 'charmingGlanceCloneV1';

export const PANEL_OPEN_IDS = ['characterDetails','materialsDetails'];

/* MINED_REALM_AND_OPEN_MAP_PROVENANCE_V1
     Material Realm values below are long-run expectations computed from published client-derived
     object weights, durability, damage probabilities, break rewards, free-box rules and each
     season's max rank multiplier. Open-map `map` values are a SEPARATE 5-Stamina-node model.
     The current public mined snapshot does not expose the gathering-node reward table, so S2
     1400 Ore / 1770 Essence / 1180 Sand / 14000 Rolla per 5 Stamina remain live-observed model
     values and are deliberately NOT relabeled or altered as mined data. */
/* S2_MINED_REALM_YIELDS_V1
     S2 max-bracket (Champion III / client Saint III) Material Realm averages are precomputed
     from factual live-client tables: rank multiplier 19.5 plus object weights, durability,
     hit-damage probabilities, break rewards and free-box rules. Values are long-run expected
     resources per actual Realm run/tool. Sand is Basic/White equivalent (Blue x5, Purple x25). */
export const CALC_SEASONS = {
    // S1_SCORING_METHOD_REFRESH_V1: shared acquisition optimizer; S1 scoring constants remain unchanged.
    // S1: Skills follow Character level, Relics unlock +11/+12/+13/+14 at Lv.100/110/120/130,
    // Fantomons unlock to the next 10-level band (so Character Lv.130 opens Fantomons through Lv.140), while Gear can continue above Character level.
    s1:{key:'s1',name:'Season 1',nextName:'Season 2',end:S1_END,deadline:'device-local',scoreFloor:100,relicFloor:10,starBase:10,scorePerStar:100,weights:{character:100,gear:38,skill:13,relic:57,fanto:14},skillCap:null,relicCap:null,fantoCap:null,gearCap:null,realmMaxLevel:90,realm:{ore:1041.7527105032607,essence:1466.093120963844,sand:987.7707800556983,rolla:10616.811310741661},map:{ore:900,essence:1475,sand:838,rolla:9000,bigRate:0},optimizeRelic:true,optimizeFanto:true},
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
export const S2_PLANNER_START_LEVEL = 120;

// PRESEASON_UNLOCK_PREVIEW_V4: Lv.120-130 may preview the first post-floor Fantomon
  // planning state without awarding fake pre-Lv.130 Season Power. Gear, Skills and Relic
  // ranks are not Character-level gated in S2; this preview now applies only to the
  // resonance-gated Fantomon planning rule.
export const S2_FULL_SEASONAL_PREVIEW_LEVEL = 131;

export const S2_PRIMO_META = Object.freeze({
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
export const S2_SCORING_START_DEFAULTS=Object.freeze({
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

export const S2_SCORING_START_CHECKS=Object.freeze({finishEarlyAuto:false});

/* S2_ZERO_SCORE_DEFAULTS_V1
     The assumed scoring-start profile sits exactly on every S2 scoring floor. It is a
     neutral starting snapshot: carried/fixed Primostars may exist, but assumed progression
     itself must contribute exactly 0 Season Power before the optimizer recommends upgrades. */
export function validateS2ScoringStartDefaults(){
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

export function validateS2PrimoModel(){
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

// QY Maple Astral Pact thresholds. Primostars are cumulative across seasons; S2 continues after S1.
export const ASTRAL_PACT_NODES = [
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

export const ASTRAL_LABELS={atk:'ATK',def:'DEF',hp:'HP',spd:'SPD',ascension:'Ascension drop rate',gem:'Gem acquisition',dungeon:'Dungeon double reward',exp:'EXP gain'};

export const ASTRAL_ORDER=['atk','def','hp','spd','ascension','gem','dungeon','exp'];

export const LEGACY_GEAR_IDS = ['gearWeapon','gearOffhand','gearHelmet','gearArmor','gearBoots'];

export const GEAR_OUTPUT_IDS = ['targetGearWeapon','targetGearOffhand','targetGearHelmet','targetGearArmor','targetGearBoots'];

export const INPUT_IDS = [
    'targetStars','historicalStars','charLevel','charExp','bedExp','finishEarlyDays','skillLevel','relicLevel','fantomonLevel','gearLevel',
    'oreCurrent','oreRate','essenceCurrent','essenceRate','sandCurrent','sandBlueCurrent','sandEpicCurrent','sandRate','treatCurrent','treatPremiumCurrent','treatDeluxeCurrent','treatRate','shopRefreshesDaily',
    'hammerCurrent','knucklesCurrent','shovelCurrent','staminaMode','realmDailyOre','realmDailyEssence','realmDailySand','refinedOreCurrent','exactSkillLevels','exactRelicLevels','exactFantoLevels','exactGearLevels'
  ];

export const CHECK_IDS = ['finishEarlyAuto'];

export const defaults = Object.create(null);

/* COMPACT_NUMBER_INPUTS_V1
     High-volume calculator fields accept shorthand such as 22.7k, 1.3m, and 2b.
     Values are expanded to their full numeric form on commit so persisted state stays plain. */
export const COMPACT_NUMBER_INPUT_IDS = new Set([
    'charExp','bedExp',
    'oreCurrent','oreRate','essenceCurrent','essenceRate',
    'sandCurrent','sandBlueCurrent','sandEpicCurrent','sandRate',
    'treatCurrent','treatPremiumCurrent','treatDeluxeCurrent','treatRate',
    'hammerCurrent','knucklesCurrent','shovelCurrent','refinedOreCurrent'
  ]);

export function parseCompactNumber(raw,fallback=0){
    if(typeof raw==='number') return Number.isFinite(raw)?raw:fallback;
    const s=String(raw ?? '').trim().replace(/,/g,'');
    if(!s) return fallback;
    const match=s.match(/^([+-]?(?:\d+(?:\.\d*)?|\.\d+))\s*([kmb])?$/i);
    if(!match) return fallback;
    const multiplier=match[2]?({k:1e3,m:1e6,b:1e9})[match[2].toLowerCase()]:1;
    const value=Number(match[1])*multiplier;
    return Number.isFinite(value)?value:fallback;
  }

/* OPTIMIZER_CLEANUP_V5: one optimizer policy only — raw-first, acquisition-efficient. */
  /* EPIC_CHRONO_SAND_SAVED_V1: Rare/Blue = 5 Basic; Epic/Purple = 25 Basic. Shop average stays unchanged until an Epic shop roll is observed. */
export const SAND_BLUE_EQ=5, SAND_EPIC_EQ=25;

export const TREAT_BASIC_EXP=50, TREAT_PREMIUM_EQ=8, TREAT_DELUXE_EQ=40;

// CG_S2_SHOP_OBSERVED_N19_V1
  // Charming Glance S2 shop averages measured from nineteen observed shop pages.
  // Sep. 10 screenshots add four more observed pages (refreshes 7-10).
  // Keep regular Chrono Sand and Rare Chrono Sand separate in the raw sample data.
  // The optimizer converts Rare Chrono Sand at the same 5:1 ratio used by saved inventory.
export const S2_SHOP_OBSERVED_PAGES=Object.freeze([
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

export function s2ShopObservedAverage(){
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
export const DAILY_SHOP_CORE_BUNDLE_FACTOR=2/3;

export const DAILY_SHOP_TREAT_EQ_PER_REFRESH=35;

export function dailyShopMatsPerRefresh(cfg=activeCalcConfig()){
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

export const fmt = x => Math.round(x).toLocaleString('en-US');

export const fmtCompact = x => {
    const a = Math.abs(x);
    if (a >= 1_000_000) return `${(x/1_000_000).toFixed(a >= 10_000_000 ? 1 : 2).replace(/\.0+$/,'')}M`;
    if (a >= 1000) return `${(x/1000).toFixed(a >= 100_000 ? 1 : 1).replace(/\.0$/,'')}K`;
    return fmt(x);
  };

export const clamp = (x,a,b) => Math.min(b, Math.max(a,x));

export const activeCalcConfig = () => CALC_SEASONS[seasonKeyAt(Date.now())];

export const numberFromState = (state,id,fallback=0) => {
    const v = Number(state?.[id]);
    return Number.isFinite(v) ? v : fallback;
  };

export function remainingHoursAt(ms, cfg=activeCalcConfig()){ return Math.max(0, (cfg.end.getTime() - ms) / 3_600_000); }

/* PRESEASON_BED_RESERVE_V1
     Universal rollover strategy: stop CLAIMING Bed EXP 34 wall-clock hours before a season ends.
     The final daily reset inside that hold window still uses its free 2-hour speed-up, but that
     accelerated EXP stays in the Bed. Result at rollover: 34 natural hours + 2 boosted hours =
     36 hours of Bed EXP banked for the next season. Other Cart/material production is unaffected. */
export const PRESEASON_BED_HOLD_WALL_HOURS=34;

export const PRESEASON_BED_FINAL_RESET_BOOST_HOURS=2;

export function characterExpCollectionCutoffMs(cfg=activeCalcConfig()){
    return cfg.end.getTime()-(PRESEASON_BED_HOLD_WALL_HOURS*3_600_000);
  }

export function projectionBedClaimableHoursAt(ms,cfg=activeCalcConfig()){
    const cutoff=characterExpCollectionCutoffMs(cfg);
    const capped=Math.min(ms,cutoff);
    if(capped>=cutoff) return 0;
    const wallHours=Math.max(0,(cutoff-capped)/3_600_000);
    const boostHours=2*countFuturePacificResets(capped,cutoff);
    return Math.max(0,wallHours+boostHours);
  }

export function remainingHours(){ return remainingHoursAt(Date.now(),activeCalcConfig()); }

export function formatRemaining(hours){
    const mins = Math.max(0, Math.floor(hours*60));
    const d = Math.floor(mins/1440), h = Math.floor((mins%1440)/60), m = mins%60;
    return `${d}d ${h}h ${m}m remaining`;
  }

// Exact EXP-to-next-level data keyed by CURRENT level.
export const S1_EXP_REQUIREMENTS = {
    100:886086,101:888547,102:926501,103:964086,104:1012164,105:1054111,
    106:1096529,107:1135645,108:1174997,109:1214584,110:1258533,
    111:1303677,112:1348574,113:1393941,114:1439780,115:1486091,
    116:1532872,117:1580125,118:1627849,119:1676044,120:1730017,
    121:1783360,122:1833196,123:1833196,124:1833196
  };

export const S2_EXP_REQUIREMENTS = {
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
export const S2_EXACT_CHARACTER_EXP_FROM_130='3ry55.41kpv.4dinh.4p95g.50pfl.5bspk.5oes9.5zok8.6b072.6o2zg.6psa6.6qxxm.6s2sw.6t7o6.6ucjg.6vheq.6wma0.6xr5a.6ybkx.6zgg7.70lbh.715wd.71qc1.72aro.73fmz.74kia.769t8.78jju.79of5.7atag.7by5r.7dnbz.7es7a.7fx2k.7fx2k.7ghi7.7hmdh.7ir8r.7jboe.7kgjo.7lley.7mq5h.7nv0q.7pkbm.7r9mj.7sehs.7tjd1.7uo8b.7v8ny.7wdj7.7xieh.7ymix.7z6yi.7zre3.80btn.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98'.split('.').map(v=>parseInt(v,36));

export const S2_EXACT_FANTOMON_EXP_FROM_130='189m.195k.1a18.1ax6.1bt4.1cp2.1dkq.1ego.1fcm.1g8k.1h48.1i06.1iw4.1js2.1knq.1ljo.1mfm.1nbk.1o78.1p36.1pz4.1qv2.1rqq.1smo.1tim.1uek.1va8.1w66.1x24.1xxs.1ytq.1zpo.20lm.21ha.22d8.2396.2454.250s.25wq.26so.27om.28ka.29g8.2ac6.2b84.2c3s.2czq.2dvo.2erm.2fna.2gj8.2hf6.2iau.2j6s.2k2q.2kyo.2luc.2mqa.2nm8.2oi6.2pdu.2q9s.2r5q.2s1o.2sxc.2tta.2up8.2vl6.2wgu.2xcs.2y8q.2z4o.300c.30wa.31s8.32o6.33ju.34fs.35bq.367e.373c.37za.38v8.39qw.3amu.3bis.3ceq.3dae.3e6c.3f2a.3fy8.3gtw.3hpu.3ils.3jhq.3kde.3l9c.3m5a.3n18.3nww.3osu.3pos.3qkg.3rge.3scc.3t8a.3u3y.3uzw.3vvu.3wrs.3xng.3yje.3zfc.40ba.416y.422w.42yu.43us.44qg.45me.46ic.47ea.489y.495w.4a1u.4axs.4btg.4cpe.4dlc.4eh0.4fcy.4g8w.4h4u.4i0i.4iwg.4jse.4koc.4lk0.4mfy.4nbw.4o7u.4p3i.4pzg.4qve.4rrc.4sn0.4tiy.4uew.4vau.4w6i'.split('.').map(v=>parseInt(v,36));

export const S2_EXACT_UPGRADE_RULES=Object.freeze({
    floor:130,gearBase:16630,gearRate:166.3,gearBlessingLimit:300,gearScaleCap:150,
    skillBase:12025,skillRate:120.25,skillBlessingLimit:150,
    relicBase:13,relicPurpleBase:1350,relicPurpleRate:135,relicBlessingLimit:15,
    refinedOreEvery5:510,rollaPerOre:2
  });

// S1_MINED_EXP_PLATEAU_V1: the published client-derived S1 EXP table repeats 1,833,196
  // from Lv.122 onward across the supported late-season range. Use that exact plateau rather
  // than the old rounded ~1.83M community fallback.
export const S1_LATE_EXP_PLATEAU = 1_833_196;

export function isEstimatedS1ExpLevel(level){
    const l=Math.floor(Number(level)||0);
    return l>=123 && !S1_EXP_REQUIREMENTS[l];
  }

export function expRequiredForLevel(level,cfg=activeCalcConfig()){
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

export function s1ProjectionUsesEstimatedExp(fromLevel,toLevel){
    if(activeCalcConfig().key!=='s1') return false;
    const a=Math.max(1,Math.floor(Number(fromLevel)||1)),b=Math.max(a,Math.floor(Number(toLevel)||a));
    for(let l=a;l<=b;l++) if(isEstimatedS1ExpLevel(l)) return true;
    return false;
  }

export function maxFinishEarlyDays(cfg=activeCalcConfig()){
    const remainingDays=Math.max(0,(cfg.end.getTime()-Date.now())/86_400_000);
    // Never allow the planning cutoff to move before the present moment.
    return Math.floor((remainingDays+1e-9)*2)/2;
  }

export const gearScore = (levels,cfg=activeCalcConfig()) => levels.reduce((s,l) => s + Math.max(0,l-cfg.scoreFloor)*cfg.weights.gear, 0);

export const skillScore = (lvl,cfg=activeCalcConfig()) => Math.max(0,lvl-cfg.scoreFloor) * 8 * cfg.weights.skill;

export const relicScore = (lvl,cfg=activeCalcConfig()) => Math.max(0,lvl-cfg.relicFloor) * 20 * cfg.weights.relic;

export const fantoScore = (lvl,cfg=activeCalcConfig()) => Math.max(0,lvl-cfg.scoreFloor) * 4 * cfg.weights.fanto;

export const characterScore = (p,cfg=activeCalcConfig()) => Math.max(0, Math.floor((p.decimal-cfg.scoreFloor)*100 + 1e-9));

// Skills (8), Relics (20) and deployed Fantomons (4) score per INDIVIDUAL slot.
  // The compact UI accepts an average; internally it is converted to the closest balanced
  // integer-slot distribution (e.g. Relic 13.20 = four +14 slots + sixteen +13 slots).
export function levelsFromAverage(avg,count,minLevel,maxLevel=Infinity){
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

export function averageLevels(levels){ return levels.length?levels.reduce((a,b)=>a+b,0)/levels.length:0; }

export function categoryScoreFromLevels(levels,floor,weight){ return levels.reduce((sum,l)=>sum+Math.max(0,l-floor)*weight,0); }

export function formatAverage(x,precision=3){
    const v=Number(x)||0;
    return v.toFixed(precision).replace(/\.0+$/,'').replace(/(\.\d*?)0+$/,'$1');
  }

export function formatLevelMix(levels,{plus=false}={}){
    const counts=new Map();
    levels.forEach(l=>counts.set(l,(counts.get(l)||0)+1));
    const parts=[...counts.entries()].sort((a,b)=>b[0]-a[0]).map(([lvl,count])=>{
      const tag=plus?`+${lvl}`:`Lv.${lvl}`;
      return counts.size===1?tag:`${count}×${tag}`;
    });
    return parts.join(' · ');
  }

/* EXACT_LEVEL_AVERAGE_SYNC_V1
     Exact slot entries are the authoritative current progression state whenever they are
     present and valid. Mirror their arithmetic mean back into the four compact Average fields
     so the summary above always agrees with the exact distribution being used by the planner.
     Any nonblank exact entry also locks the Exact slot levels panel open until all four fields
     are cleared, preventing active overrides from being hidden accidentally. */
export const EXACT_LEVEL_AVERAGE_BINDINGS = Object.freeze([
    Object.freeze({exactId:'exactSkillLevels',avgId:'skillLevel',count:8,min:100,capKey:'skill'}),
    Object.freeze({exactId:'exactRelicLevels',avgId:'relicLevel',count:20,min:10,capKey:'relic'}),
    Object.freeze({exactId:'exactFantoLevels',avgId:'fantomonLevel',count:4,min:100,capKey:'fanto'}),
    Object.freeze({exactId:'exactGearLevels',avgId:'gearLevel',count:5,min:100,capKey:'gear'})
  ]);

export function categoryStateFromAverage(avg,count,minLevel,maxLevel,floor,weight){
    const levels=levelsFromAverage(avg,count,minLevel,maxLevel);
    return {levels,avg:averageLevels(levels),score:categoryScoreFromLevels(levels,floor,weight),exact:false};
  }

export function buildCategoryOptionsFromLevels(baseLevels,cap,floor,weight,stepCost,gateSpan=0){
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

export function buildCategoryOptions(baseAvg,count,cap,minLevel,floor,weight,stepCost){
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

export function relicCapForCharacter(characterLevel,cfg=activeCalcConfig()){
    const lvl=Math.max(1,Math.floor(Number(characterLevel)||1));
    // S2_ABOVE_CHARACTER_UPGRADES_V1: live Global evidence at Character Lv.131 includes
    // 18 Relics at +14 with enough material to push two slots to +15. Relic rank is not
    // Character-level capped; use the extracted S2 blessing table as the planning ceiling.
    if(cfg.key==='s2') return S2_EXACT_UPGRADE_RULES.relicBase + S2_EXACT_UPGRADE_RULES.relicBlessingLimit;
    return lvl<100 ? 10 : Math.max(10,Math.floor(lvl/10)+1);
  }

export function categoryCapsForCharacter(characterLevel,cfg=activeCalcConfig()){
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

export function categoryInputCapsForCharacter(characterLevel,cfg=activeCalcConfig()){
    const caps=categoryCapsForCharacter(characterLevel,cfg);
    if(cfg.key!=='s2') return caps;
    // Accept actual S2 values without Character-level clamping. The optimizer also allows new Gear/Skill/Relic
    // upgrades above Character level, bounded only by the supported seasonal cost tables; Fantomon remains conservative.
    return {...caps,skill:Infinity,relic:Infinity,fanto:Infinity,gear:Infinity};
  }

export function gearStepCost(level,cfg=activeCalcConfig()){
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

export function gearStepRefined(level,cfg=activeCalcConfig()){
    const l=Math.floor(level);
    if(cfg.key==='s2' && l>=S2_EXACT_UPGRADE_RULES.floor){
      const blessing=(l+1)-S2_EXACT_UPGRADE_RULES.floor;
      return blessing>=1 && blessing<=S2_EXACT_UPGRADE_RULES.gearBlessingLimit && blessing%5===0
        ? S2_EXACT_UPGRADE_RULES.refinedOreEvery5 : 0;
    }
    // Preserve the legacy pre-floor/S1 catch-up model where the S2 extracted blessing table does not apply.
    return ((l+1)%5===0) ? l+381 : 0;
  }

export function gearRefinedCost(fromLevels,toLevels){
    let total=0;
    for(let i=0;i<5;i++) for(let l=fromLevels[i];l<toLevels[i];l++) total+=gearStepRefined(l);
    return total;
  }

export function gearCost(fromLevels,toLevels,cfg=activeCalcConfig()){
    let total=0;
    for(let i=0;i<5;i++) for(let l=fromLevels[i];l<toLevels[i];l++) total+=gearStepCost(l,cfg);
    return total;
  }

export function skillStepCost(level,cfg=activeCalcConfig()){
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

export function skillCost(from,to,cfg=activeCalcConfig()){
    let each=0;
    for(let l=from;l<to;l++) each+=skillStepCost(l,cfg);
    return each*8;
  }

export function relicStepSand(level,cfg=activeCalcConfig()){
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

export function relicCost(from,to,cfg=activeCalcConfig()){
    if(to<=from) return 0;
    let total=0;
    for(let l=from;l<to;l++){ const c=relicStepSand(l,cfg); if(!Number.isFinite(c)) return Infinity; total+=c; }
    return total*20;
  }

export function fantoStepTreatCost(level,cfg=activeCalcConfig()){
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

export function fantoCost(from,to,cfg=activeCalcConfig()){
    if(to<=from) return 0;
    let each=0;
    for(let l=from;l<to;l++){ const c=fantoStepTreatCost(l,cfg); if(!Number.isFinite(c)) return Infinity; each+=c; }
    return each*4;
  }

export function balancedGearTarget(base, increments){
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
export function automaticResourceYields(characterLevel,cfg=activeCalcConfig()){
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

export function applyStaminaAllocation(base,allocation,cfg=activeCalcConfig()){
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

export function staminaPlanCost(plan,key){
    if(!plan) return 0;
    return key==='ore'?plan.oreCost:key==='essence'?plan.essenceCost:key==='sand'?plan.sandCost:0;
  }

export function staminaPlanBudget(resources,key){ return Number(resources?.[key])||0; }

export function staminaRealmYield(resources,key){
    if(key==='ore') return Number(resources?.yields?.orePerHammer)||0;
    if(key==='essence') return Number(resources?.yields?.essencePerKnuckles)||0;
    if(key==='sand') return Number(resources?.yields?.sandPerShovel)||0;
    return 0;
  }

export function staminaAllocationSignature(a){ return ['ore','essence','sand','rolla','unassigned'].map(k=>Math.floor(a?.[k]||0)).join('/'); }

/* TARGET_REACH_ETA_V1
     Estimate WHEN the already-selected goal route becomes executable. This deliberately does
     not rerun the expensive optimizer at every timestamp. Instead it binary-searches time using
     the recommended route's exact costs, current Character growth, Cart/shop production,
     Stamina, owned/planned Realm tools, and remaining Realm purchase capacity. */
export function targetMomentLabel(ms){
    return new Intl.DateTimeFormat(undefined,{month:'short',day:'numeric',hour:'numeric',minute:'2-digit'}).format(new Date(ms)).replace(' at ',' · ');
  }

export function compactDurationMs(ms){
    const mins=Math.max(0,Math.floor((Number(ms)||0)/60_000));
    const d=Math.floor(mins/1440),h=Math.floor((mins%1440)/60),m=mins%60;
    return d>0?`${d}d ${h}h`:h>0?`${h}h ${m}m`:`${m}m`;
  }

/* POST_TARGET_GAINS_V1
     Preview only: once the requested Primostar target is projected to be reached, show the
     resources expected to accumulate from that moment through season end. Post-target Realm
     purchase overrides affect this preview only and never feed back into Smart Balance scoring. */
export const POST_TARGET_TOOL_STORAGE_KEY='sxsPostTargetToolPlanV1';

// REALM_20_REFRESH_TOOL_COUNT_V1
  // One refresh grants 5 Realm tools/entries. The first 10 Dawnium prices are known;
  // refreshes 11–20 remain usable capacity but their Dawnium prices are intentionally unknown.
export const MATERIAL_REALM_BUY_COSTS = [60,60,100,100,150,150,200,200,250,300];

export const MAX_REALM_REFRESHES_PER_DAY=20;

export const REALM_RUNS_PER_REFRESH=5;

export const REALM_CHOICE_CACHE=new Map();

export function realmPurchaseChoices(days,baselinePerDay){
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

export function realmYieldFor(resources,key){
    if(key==='ore') return Number(resources?.yields?.orePerHammer)||0;
    if(key==='essence') return Number(resources?.yields?.essencePerKnuckles)||0;
    if(key==='sand') return Number(resources?.yields?.sandPerShovel)||0;
    return 0;
  }

// A paid Material Realm refresh is a PACK of five actual Realm runs/tools.
  // Banked tools are consumed first; Dawnium is charged only for newly purchased refresh packs.
export function realmTopup(resourceCost,projectedBudget,yieldPerRun,days,bankedRuns=0,baselinePerDay=0){
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

export function formatRealmSchedule(topup,label){
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

export function realmDailyRoute(topup){
    if(!topup || !Number.isFinite(topup.packs) || topup.packs<=0) return '';
    const counts=(topup.dailyCounts||[]).map(x=>Math.max(0,Math.floor(Number(x)||0)));
    let last=counts.length-1;
    while(last>=0&&counts[last]===0) last--;
    if(last<0) return '';
    return counts.slice(0,last+1).join('/');
  }

export function realmToolPurchaseText(topup,label){
    if(!topup) return '';
    const purchased=Number.isFinite(topup.purchasedRuns)?Math.max(0,Math.floor(topup.purchasedRuns)):0;
    const banked=Number.isFinite(topup.bankedUsed)?Math.max(0,Math.floor(topup.bankedUsed)):0;
    if(purchased>0) return `${fmt(purchased)} ${label}${banked?` + ${fmt(banked)} banked`:''}`;
    if(banked>0) return `${fmt(banked)} banked ${label}`;
    return '';
  }

export function firstGearOptionAtLeast(options,scoreNeeded){
    let lo=0,hi=options.length-1,ans=null;
    while(lo<=hi){
      const mid=(lo+hi)>>1;
      if(options[mid].score>=scoreNeeded){ans=options[mid];hi=mid-1;} else lo=mid+1;
    }
    return ans;
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
export const SURPLUS_ACQUISITION_FLOORS={ore:0.25,essence:0.25,sand:0.25,treat:0.25};

export const TOOL_SCARCITY_CREDIT=1.00;

// MARGINAL_INTEGRATED_SCARCITY_V5: these shape the price of the NEXT unit consumed.
  // The optimizer integrates this curve over the candidate spend instead of applying the
  // final depletion multiplier retroactively to the entire spend.
export const POST_PLAN_SCARCITY_MAX=3.50;

export const POST_PLAN_SCARCITY_EXPONENT=2.40;

/* OPTIMIZER_AUDIT_V3 · TOOLS_FIRST_S2_RESERVES_V1
     Enabled S2 Essence/Sand reserves hold carried/planned Realm tools first. Raw material
     is reserved only for the portion those tools cannot cover. If a reserve is disabled,
     raw remains the first current-season spend source and Realm tools stay untouched until
     the raw material is genuinely exhausted. */
export function rawOnlyAcquisitionSupply(key,resources,cfg=activeCalcConfig()){
    return Math.max(0,Number(resources?.[key])||0);
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
export function marginalWeightedSpend(amount,key,resources){
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

export function marginalWeightedCosts(costs,resources,cfg=activeCalcConfig()){
    return {
      ore:marginalWeightedSpend(costs?.ore,'ore',resources),
      essence:marginalWeightedSpend(costs?.essence,'essence',resources),
      sand:marginalWeightedSpend(costs?.sand,'sand',resources),
      treat:marginalWeightedSpend(costs?.treat,'treat',resources)
    };
  }

export function candidateResourceMetric(candidate){
    const base=Number(candidate?.acquisitionHours);
    return Number.isFinite(base)?base:1e18;
  }

/* S2_ACQUISITION_OPTIMIZER_V1
     Compare target plans by the time-equivalent burden of reacquiring the marginal
     resources they consume. This is season-agnostic: S2 uses its Lv.120 Realm/open-map
     yields and its own scoring/cost curves. GLOBAL_ACQUISITION_PRIORITY_V2 makes this
     metric primary across raw, existing-tool and paid-refresh sourcing instead of only
     comparing plans after Realm-stage gates are satisfied. */
export function compareAcquisitionEffort(candidate,best){
    const cm=candidateResourceMetric(candidate),bm=candidateResourceMetric(best);
    if(cm<bm-1e-9) return true;
    if(cm>bm+1e-9) return false;
    return null;
  }

/* REALM_TOOL_TIEBREAK_V2
     Source tier is a hard priority. Inside the same tier, material acquisition weighting
     ranks the route first; literal Realm-tool counts only break a weighted-material tie. */
export function candidateRealmToolBurden(candidate){
    const realms=['ore','essence','sand'].map(k=>candidate?.realm?.[k]).filter(Boolean);
    return {
      paidRuns:realms.reduce((sum,x)=>sum+Math.max(0,Number(x?.paidRunsUsed)||0),0),
      totalRuns:realms.reduce((sum,x)=>sum+Math.max(0,Number(x?.runsNeeded)||0),0),
      bankedUsed:realms.reduce((sum,x)=>sum+Math.max(0,Number(x?.bankedUsed)||0),0)
    };
  }

export function betterToolBurden(candidate,best){
    const c=candidateRealmToolBurden(candidate),b=candidateRealmToolBurden(best);
    if(c.paidRuns<b.paidRuns) return true;
    if(c.paidRuns>b.paidRuns) return false;
    if(c.totalRuns<b.totalRuns) return true;
    if(c.totalRuns>b.totalRuns) return false;
    if(c.bankedUsed<b.bankedUsed) return true;
    if(c.bankedUsed>b.bankedUsed) return false;
    return null;
  }

export function candidateRealmStage(candidate){
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

export function betterFeasibleCandidate(candidate,best){
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

export function betterDiagnosticCandidate(candidate,best){
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

/* COOPERATIVE_OPTIMIZER_V1
     Heavy Primostar searches run in short main-thread slices rather than monopolizing one
     JavaScript task. The mathematical search remains identical to searchPlans(); this layer
     only yields to the browser between expensive candidate batches and supports cancellation. */
export class OptimizerCancelledError extends Error{
    constructor(){ super('Optimizer calculation cancelled'); this.name='OptimizerCancelledError'; }
  }

export function optimizerReserveSummary(resources,cfg){
    if(cfg.key!=='s1') return '';
    const reserveKinds=[];
    if((resources?.s2SkillReserve?.target||0)>0) reserveKinds.push('Skill');
    if((resources?.s2RelicSandReserve?.target||0)>0) reserveKinds.push('Relic');
    if((resources?.s2FantomonTreatReserve?.target||0)>0) reserveKinds.push('Fantomon');
    return reserveKinds.length
      ? `Spend surplus first · minimize reacquisition effort · S2 ${reserveKinds.join(' + ')} reserve${reserveKinds.length>1?'s':''} protected`
      : 'Spend surplus first · minimize reacquisition effort · no S2 resource reserve';
  }

/* SMART_BALANCE_RAW_CEILING_V1
     The requested Primostar value is a minimum goal. If projected RAW income alone can
     reach a higher whole-Primostar breakpoint, recommend that higher breakpoint without
     touching Realm tools. Tools are only unlocked when raw cannot reach the requested goal. */
export function smartBalanceHighestAffordable(options,budget,costKey='cost',secondaryBudget=Infinity,secondaryKey=''){
    let best=Array.isArray(options)&&options.length?options[0]:null;
    for(const option of (options||[])){
      const primary=Math.max(0,Number(option?.[costKey])||0);
      const secondary=secondaryKey?Math.max(0,Number(option?.[secondaryKey])||0):0;
      if(primary<=budget+0.5 && secondary<=secondaryBudget+0.5) best=option;
      else if(primary>budget+0.5) break;
    }
    return best;
  }