from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
marker='S2_SCORING_INPUT_FLOOR_V2'
if marker in s:
    print('already applied')
    raise SystemExit(0)

# Character Lv.130 gates the S2 Primostar calculator, but category inputs must remain able
# to represent lagging real slots. Their below-floor score is zero; if upgraded after the
# scoring unlock, their actual catch-up resource cost must still be charged.
old="""      $('skillLevel').min=String(cfg.scoreFloor); setInputMax('skillLevel',currentCaps.skill); $('skillLevel').step='0.125';
      $('relicLevel').min=String(cfg.relicFloor); setInputMax('relicLevel',currentCaps.relic); $('relicLevel').step='0.05';
      $('fantomonLevel').min=String(cfg.scoreFloor); setInputMax('fantomonLevel',currentCaps.fanto); $('fantomonLevel').step='0.25';
      GEAR_IDS.forEach(id=>{if($(id)) $(id).min=String(cfg.scoreFloor);});
"""
new="""      /* S2_SCORING_INPUT_FLOOR_V2: Character Lv.130 unlocks the planner; actual category
         inputs may still be below their score floors and must retain their real catch-up costs. */
      $('skillLevel').min='100'; setInputMax('skillLevel',currentCaps.skill); $('skillLevel').step='0.125';
      $('relicLevel').min='10'; setInputMax('relicLevel',currentCaps.relic); $('relicLevel').step='0.05';
      $('fantomonLevel').min='100'; setInputMax('fantomonLevel',currentCaps.fanto); $('fantomonLevel').step='0.25';
      GEAR_IDS.forEach(id=>{if($(id)) $(id).min='100';});
"""
if old not in s:
    raise SystemExit('strict S2 input min block not found')
s=s.replace(old,new,1)

old="""    const normalInputFloor=cfg.key==='s2'?cfg.scoreFloor:100;
    const relicInputFloor=cfg.key==='s2'?cfg.relicFloor:10;
    const gear=GEAR_IDS.map(id=>Math.max(normalInputFloor,Math.floor(n(id,cfg.key==='s2'?130:143))));
    const skillState=categoryStateFromUser('skillLevel','exactSkillLevels',8,normalInputFloor,currentCaps.skill,cfg.scoreFloor,cfg.weights.skill,cfg.key==='s2'?130:122);
    const relicState=categoryStateFromUser('relicLevel','exactRelicLevels',20,relicInputFloor,currentCaps.relic,cfg.relicFloor,cfg.weights.relic,cfg.key==='s2'?14:13);
    const fantoState=categoryStateFromUser('fantomonLevel','exactFantoLevels',4,normalInputFloor,currentCaps.fanto,cfg.scoreFloor,cfg.weights.fanto,cfg.key==='s2'?130:130);
"""
new="""    const normalInputFloor=100;
    const relicInputFloor=10;
    const gear=GEAR_IDS.map(id=>Math.max(normalInputFloor,Math.floor(n(id,cfg.key==='s2'?130:143))));
    const skillState=categoryStateFromUser('skillLevel','exactSkillLevels',8,normalInputFloor,currentCaps.skill,cfg.scoreFloor,cfg.weights.skill,cfg.key==='s2'?130:122);
    const relicState=categoryStateFromUser('relicLevel','exactRelicLevels',20,relicInputFloor,currentCaps.relic,cfg.relicFloor,cfg.weights.relic,cfg.key==='s2'?14:13);
    const fantoState=categoryStateFromUser('fantomonLevel','exactFantoLevels',4,normalInputFloor,currentCaps.fanto,cfg.scoreFloor,cfg.weights.fanto,cfg.key==='s2'?130:130);
"""
count=s.count(old)
if count!=2:
    raise SystemExit(f'expected 2 scoring progression blocks, found {count}')
s=s.replace(old,new,2)

s=s.replace(
"The calculator therefore starts score planning at Lv.130 and intentionally excludes the Lv.100→130 catch-up costs. Normal progression scores only above Lv.130, Relics score above +13,",
"The calculator therefore starts planning only once Character Lv.130 unlocks Season Power. Progression already spent before that snapshot is outside the plan; however, any Gear/Skill/Fantomon/Relic slot that is still below its score floor at Lv.130 can be entered normally, scores zero until it crosses the floor, and keeps its real catch-up resource cost. Normal progression scores only above Lv.130, Relics score above +13,",
1)

s=s.replace(
"S2 cost curves are used only for score-relevant upgrades from that floor forward: Gear/Ore and Skill Essence use the current late-S2 tables, Relic Sand uses the known +13-and-up steps, and Fantomon Treats use the S2 level curve.",
"S2 cost curves are applied from the actual scoring-start levels you enter: Gear/Ore and Skill Essence use the current S2 tables, Relic Sand uses the known S2 step table, and Fantomon Treats use the S2 level curve. This preserves the cost of catching up a lagging slot after Season Power unlocks instead of granting a free jump to the score floor.",
1)

# Clarify the pre-scoring lock text: it excludes PRE-Lv130 planning, not all sub-floor category costs forever.
s=s.replace(
"Current Lv.${current.level} is still in the S2 catch-up phase, so 100→${cfg.scoreFloor} upgrade costs are intentionally excluded from this Primostar planner.",
"Current Lv.${current.level} is still in the pre-Season-Power catch-up phase, so the planner stays paused until Character Lv.${cfg.scoreFloor}. Once unlocked, enter your actual Gear/Skill/Relic/Fantomon levels; lagging slots are allowed and their future catch-up costs are counted.",
1)

p.write_text(s,encoding='utf-8')
print('corrected S2 scoring-start input floors')
