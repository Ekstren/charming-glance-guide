from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

if 'EXACT_S2_UPGRADE_COSTS_V5' in s:
    print('Exact S2 upgrade costs v5 already applied.')
    raise SystemExit(0)

char_data='3ry55.41kpv.4dinh.4p95g.50pfl.5bspk.5oes9.5zok8.6b072.6o2zg.6psa6.6qxxm.6s2sw.6t7o6.6ucjg.6vheq.6wma0.6xr5a.6ybkx.6zgg7.70lbh.715wd.71qc1.72aro.73fmz.74kia.769t8.78jju.79of5.7atag.7by5r.7dnbz.7es7a.7fx2k.7fx2k.7ghi7.7hmdh.7ir8r.7jboe.7kgjo.7lley.7mq5h.7nv0q.7pkbm.7r9mj.7sehs.7tjd1.7uo8b.7v8ny.7wdj7.7xieh.7ymix.7z6yi.7zre3.80btn.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98.80w98'
fanto_data='189m.195k.1a18.1ax6.1bt4.1cp2.1dkq.1ego.1fcm.1g8k.1h48.1i06.1iw4.1js2.1knq.1ljo.1mfm.1nbk.1o78.1p36.1pz4.1qv2.1rqq.1smo.1tim.1uek.1va8.1w66.1x24.1xxs.1ytq.1zpo.20lm.21ha.22d8.2396.2454.250s.25wq.26so.27om.28ka.29g8.2ac6.2b84.2c3s.2czq.2dvo.2erm.2fna.2gj8.2hf6.2iau.2j6s.2k2q.2kyo.2luc.2mqa.2nm8.2oi6.2pdu.2q9s.2r5q.2s1o.2sxc.2tta.2up8.2vl6.2wgu.2xcs.2y8q.2z4o.300c.30wa.31s8.32o6.33ju.34fs.35bq.367e.373c.37za.38v8.39qw.3amu.3bis.3ceq.3dae.3e6c.3f2a.3fy8.3gtw.3hpu.3ils.3jhq.3kde.3l9c.3m5a.3n18.3nww.3osu.3pos.3qkg.3rge.3scc.3t8a.3u3y.3uzw.3vvu.3wrs.3xng.3yje.3zfc.40ba.416y.422w.42yu.43us.44qg.45me.46ic.47ea.489y.495w.4a1u.4axs.4btg.4cpe.4dlc.4eh0.4fcy.4g8w.4h4u.4i0i.4iwg.4jse.4koc.4lk0.4mfy.4nbw.4o7u.4p3i.4pzg.4qve.4rrc.4sn0.4tiy.4uew.4vau.4w6i'

anchor='''  // Late-S1 community method: use confirmed checkpoints first, then the nearest accepted late-S1 plateau.\n'''
insert=f'''  /* EXACT_S2_UPGRADE_COSTS_V5\n     Season-2 scoring-floor-and-above upgrade economics are sourced from the extracted live-client\n     season tables used by the public multi-season calculator, rather than hand-fit extrapolations.\n     Character EXP is exact from Lv.130 through the extracted table range; Fantomon feed EXP is\n     exact from Lv.130 upward through its extracted range. Gear/Skill use the client season base/rate\n     with game rounding to the nearest 5. S2 Relics use the Purple-Sand blessing table, and every\n     fifth S2 Gear blessing costs a fixed 510 Refined Ore. Existing pre-Lv.130 catch-up curves are\n     intentionally retained because the extracted seasonal table begins at the S2 scoring floor. */\n  const S2_EXACT_CHARACTER_EXP_FROM_130='{char_data}'.split('.').map(v=>parseInt(v,36));\n  const S2_EXACT_FANTOMON_EXP_FROM_130='{fanto_data}'.split('.').map(v=>parseInt(v,36));\n  const S2_EXACT_UPGRADE_RULES=Object.freeze({\n    floor:130,gearBase:16630,gearRate:166.3,gearBlessingLimit:300,gearScaleCap:150,\n    skillBase:12025,skillRate:120.25,skillBlessingLimit:150,\n    relicBase:13,relicPurpleBase:1350,relicPurpleRate:135,relicBlessingLimit:15,\n    refinedOreEvery5:510,rollaPerOre:2\n  });\n\n'''
if anchor not in s: raise SystemExit('EXP insert anchor not found')
s=s.replace(anchor,insert+anchor,1)

old='''  function expRequiredForLevel(level,cfg=activeCalcConfig()){
    const l=Math.max(1,Math.floor(Number(level)||1));
    if(cfg.key==='s2'){
      if(S2_EXP_REQUIREMENTS[l]) return S2_EXP_REQUIREMENTS[l];
      if(l>210) return 13_478_732;
      return S1_EXP_REQUIREMENTS[l] || 886_000;
    }
    if(S1_EXP_REQUIREMENTS[l]) return S1_EXP_REQUIREMENTS[l];
    if(l>=123) return S1_LATE_EXP_PLATEAU;
    return 886_086;
  }'''
new='''  function expRequiredForLevel(level,cfg=activeCalcConfig()){
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
  }'''
if old not in s: raise SystemExit('expRequiredForLevel anchor not found')
s=s.replace(old,new,1)

old='''  function gearStepCost(level,cfg=activeCalcConfig()){
    const l=Math.floor(level);
    if(cfg.key==='s1') return 90*l + 310;
    if(l<=109) return 9520 + 240*(l-100);
    if(l<=119) return 11925 + 245*(l-110);
    if(l<=129) return 14380 + 250*(l-120);
    if(l===130) return 16630;
    const d=l-130;
    return 16630 + 165*d + 5*Math.ceil(d/4);
  }
  function gearStepRefined(level){
    const l=Math.floor(level);
    return ((l+1)%5===0) ? l+381 : 0;
  }'''
new='''  function gearStepCost(level,cfg=activeCalcConfig()){
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
  }'''
if old not in s: raise SystemExit('Gear cost anchor not found')
s=s.replace(old,new,1)

old='''  function skillStepCost(level,cfg=activeCalcConfig()){
    const l=Math.floor(level);
    if(cfg.key==='s1') return l<=109 ? 60*l+25 : 60*l+30;
    if(l===100) return 6025;
    if(l===101) return 6205;
    if(l<=109) return 6565 + 180*(l-102);
    if(l<=119) return 8025 + 200*(l-110);
    if(l<=129) return 10045 + 220*(l-120);
    if(l===130) return 12025;
    return 12025 + 120*(l-130) + (l>=140?5:0);
  }'''
new='''  function skillStepCost(level,cfg=activeCalcConfig()){
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
  }'''
if old not in s: raise SystemExit('Skill cost anchor not found')
s=s.replace(old,new,1)

old='''  function relicStepSand(level,cfg=activeCalcConfig()){
    const l=Math.floor(level);
    if(cfg.key==='s1'){
      // White/Chrono-Sand equivalent per Relic slot. Current Global community planner: +10→11 3,200 Blue (=16,000 White), +11→12 3,520 Blue, +12→13 3,840 Blue; +13→14 is 1,350 Purple (=33,750 White).
      const table={10:16000,11:17600,12:19200,13:33750};
      return table[l] ?? Infinity;
    }
    const table={10:16000,11:17600,12:19200,13:20800,14:37125,15:40500,16:43875,17:47250,18:50625,19:54000,20:57375,21:60750};
    return table[l] ?? Infinity;
  }'''
new='''  function relicStepSand(level,cfg=activeCalcConfig()){
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
  }'''
if old not in s: raise SystemExit('Relic cost anchor not found')
s=s.replace(old,new,1)

old='''  function fantoStepTreatCost(level,cfg=activeCalcConfig()){
    const l=Math.floor(level);
    if(cfg.key==='s1'){
      if(l>=100 && l<=114) return 526 + 10*(l-100);
      if(l>=115 && l<=119) return 678 + 10*(l-115);
      if(l===120) return 730;
      if(l===121) return 740;
      if(l>=122 && l<=199) return 962 + 23*(l-122);
      return Infinity;
    }
    if(l>=100 && l<=114) return 526 + 10*(l-100);
    if(l>=115 && l<=119) return 678 + 10*(l-115);
    if(l>=120 && l<=199) return 916 + 23*(l-120);
    return Infinity;
  }'''
new='''  function fantoStepTreatCost(level,cfg=activeCalcConfig()){
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
  }'''
if old not in s: raise SystemExit('Fantomon cost anchor not found')
s=s.replace(old,new,1)

# The result already calculates secondary Gear costs; make those exact costs visible instead of suppressing them.
s=s.replace('<div class="secondaryCostNote" id="secondaryCostNote" hidden style="display:none!important"></div>','<div class="secondaryCostNote" id="secondaryCostNote" hidden></div>',1)
old="""    if((plan.gearAdds||0)>0||(plan.relicAdds||0)>0) secondaryBits.push('<b>Rolla:</b> not tracked');"""
new="""    if((plan.gearAdds||0)>0) secondaryBits.push(`<b>Rolla:</b> ${fmt((Number(plan.oreCost)||0)*S2_EXACT_UPGRADE_RULES.rollaPerOre)} required · inventory not tracked`);"""
if old not in s: raise SystemExit('Rolla secondary-cost anchor not found')
s=s.replace(old,new,1)

old='''S2 cost curves are applied from the actual scoring-start levels you enter: Gear/Ore and Skill Essence use the current S2 tables, Relic Sand uses the known S2 step table, and Fantomon Treats use the S2 level curve.'''
new='''S2 cost curves are applied from the actual scoring-start levels you enter: from the Lv.130 / +13 scoring floor upward, Gear Ore/Rolla/Refined Ore, Skill Essence, Relic Purple-Sand and Fantomon feed EXP use the extracted live-client Season 2 tables/rules rather than hand-fit extrapolations; pre-floor catch-up costs retain the existing Global curve because the extracted seasonal blessing tables start at the scoring floor.'''
if old not in s: raise SystemExit('S2 method cost text anchor not found')
s=s.replace(old,new,1)

old='''<p><b>Planning model:</b> Skills, Relics and Fantomons are optimized as individual slots, not forced to move as a whole category.'''
new='''<p><b>Exact S2 upgrade-cost source:</b> scoring-floor-and-above costs are cross-checked against the extracted live-client Season 2 blessing/level tables published by the 0xNobody multi-season calculator. Gear uses the client base/rate with nearest-5 rounding, Rolla is 2× Gear Ore, and every fifth S2 blessing requires 510 Refined Ore; Skills use their extracted base/rate with nearest-5 rounding; Relics use 1,350 Purple Sand at the first +13→+14 blessing and +135 Purple per subsequent S2 blessing; Fantomon feed EXP and Character EXP use the extracted per-level tables. Unknown levels outside the extracted ranges are not extrapolated as exact.</p>\n<p><b>Planning model:</b> Skills, Relics and Fantomons are optimized as individual slots, not forced to move as a whole category.'''
if old not in s: raise SystemExit('Planning-model method anchor not found')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('Applied exact extracted S2 upgrade costs v5.')
