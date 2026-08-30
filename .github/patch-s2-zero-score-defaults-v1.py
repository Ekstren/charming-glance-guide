from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
marker='S2_ZERO_SCORE_DEFAULTS_V1'
if marker in s:
    print('already applied')
    raise SystemExit(0)

old="skillLevel:130,relicLevel:14,fantomonLevel:130,"
new="skillLevel:130,relicLevel:13,fantomonLevel:130,"
if old not in s:
    raise SystemExit('Could not find S2 scoring-start relic default')
s=s.replace(old,new,1)

s=s.replace(
    'The default S2 profile is Lv.130 / Gear 130 / Skills 130 / Fantomons 130 / Relics +14.',
    'The default S2 profile is Lv.130 / Gear 130 / Skills 130 / Fantomons 130 / Relics +13, so assumed progression contributes 0 Season Power.',
    1,
)

# Add an explicit regression check right after the scoring-start defaults object.
needle="""  const S2_SCORING_START_CHECKS=Object.freeze({
    holdExp:true,reserveS2Ore:false,reserveS2Essence:false,reserveS2Sand:false,reserveS2Treats:false
  });

  function validateS2PrimoModel(){
"""
insert="""  const S2_SCORING_START_CHECKS=Object.freeze({
    holdExp:true,reserveS2Ore:false,reserveS2Essence:false,reserveS2Sand:false,reserveS2Treats:false
  });
  /* S2_ZERO_SCORE_DEFAULTS_V1
     The assumed scoring-start profile sits exactly on every S2 scoring floor. It is a
     neutral starting snapshot: carried/fixed Primostars may exist, but assumed progression
     itself must contribute exactly 0 Season Power before the optimizer recommends upgrades. */
  function validateS2ScoringStartDefaults(){
    const d=S2_SCORING_START_DEFAULTS,c=CALC_SEASONS.s2,w=c.weights;
    const gear=[d.gearWeapon,d.gearOffhand,d.gearHelmet,d.gearArmor,d.gearBoots];
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

  function validateS2PrimoModel(){
"""
if needle not in s:
    raise SystemExit('Could not find S2 scoring-start checks block')
s=s.replace(needle,insert,1)

p.write_text(s,encoding='utf-8')
print('set S2 starter progression to zero score')
