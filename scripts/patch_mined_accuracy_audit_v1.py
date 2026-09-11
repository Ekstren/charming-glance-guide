from pathlib import Path
import json

runtime_path=Path('assets/runtime.js')
text=runtime_path.read_text(encoding='utf-8')

# The responsive regular-goal + target-specific Finish Early fixes must already be present.
required_markers=[
    'GOAL_CHANGE_FINISH_EARLY_RESET_V1',
    'RESPONSIVE_GOAL_PREP_V1',
    'COOPERATIVE_OPTIMIZER_BOOTSTRAP_V2',
]
for marker in required_markers:
    if marker not in text:
        raise SystemExit(f'missing required optimizer marker: {marker}')

# Exact long-run Material Realm averages from the published client-derived probability model.
old_s1="realm:{ore:610,essence:1000,sand:568,rolla:9000}"
new_s1="realm:{ore:1041.7527105032607,essence:1466.093120963844,sand:987.7707800556983,rolla:10616.811310741661}"
if old_s1 in text:
    text=text.replace(old_s1,new_s1,1)
elif new_s1 not in text:
    raise SystemExit('S1 Realm constants anchor not found')

# Explain which values are mined and which are not. The public snapshot currently exposes
# Material Realm rules but not open-map 5-Stamina gathering-node rewards.
realm_comment="""/* MINED_REALM_AND_OPEN_MAP_PROVENANCE_V1
     Material Realm values below are long-run expectations computed from published client-derived
     object weights, durability, damage probabilities, break rewards, free-box rules and each
     season's max rank multiplier. Open-map `map` values are a SEPARATE 5-Stamina-node model.
     The current public mined snapshot does not expose the gathering-node reward table, so S2
     1400 Ore / 1770 Essence / 1180 Sand / 14000 Rolla per 5 Stamina remain live-observed model
     values and are deliberately NOT relabeled or altered as mined data. */
"""
if 'MINED_REALM_AND_OPEN_MAP_PROVENANCE_V1' not in text:
    anchor='/* S2_MINED_REALM_YIELDS_V1\n'
    if anchor not in text:
        raise SystemExit('realm provenance anchor not found')
    text=text.replace(anchor,realm_comment+anchor,1)

# S1 client EXP table: 122->123 and every published later S1 entry use 1,833,196.
old_exp='121:1783360,122:1833196,124:1830000'
new_exp='121:1783360,122:1833196,123:1833196,124:1833196'
if old_exp in text:
    text=text.replace(old_exp,new_exp,1)
elif new_exp not in text:
    raise SystemExit('S1 EXP table anchor not found')

old_plateau="""  // Late-S1 community method: use confirmed checkpoints first, then the nearest accepted late-S1 plateau.
  // 122→123 is confirmed at 1,833,196 and the user's live 124→125 value is 1.83M, so unknown 123+ steps
  // use 1.83M rather than extrapolating an artificial rising curve.
  const S1_LATE_EXP_PLATEAU = 1_830_000;
"""
new_plateau="""  // S1_MINED_EXP_PLATEAU_V1: the published client-derived S1 EXP table repeats 1,833,196
  // from Lv.122 onward across the supported late-season range. Use that exact plateau rather
  // than the old rounded ~1.83M community fallback.
  const S1_LATE_EXP_PLATEAU = 1_833_196;
"""
if old_plateau in text:
    text=text.replace(old_plateau,new_plateau,1)
elif 'S1_MINED_EXP_PLATEAU_V1' not in text:
    raise SystemExit('S1 late EXP plateau anchor not found')

text=text.replace(
    "late-S1 unknown EXP steps use the community-style ~1.83M/level plateau.",
    "late-S1 EXP uses the exact mined 1,833,196/level plateau.",
)

# Make elapsed time update at every cooperative browser-yield checkpoint too. The interval
# remains for smooth display, but this guarantees visible progress as the optimizer yields.
old_checkpoint="""      if(force || now-lastYield>=12){
        await new Promise(resolve=>setTimeout(resolve,0));
        lastYield=performance.now();
        if(job.cancelled) throw new OptimizerCancelledError();
      }
"""
new_checkpoint="""      if(force || now-lastYield>=8){
        // OPTIMIZER_CANCEL_TIMER_V3: refresh elapsed time at the same cooperative checkpoints
        // that service click/input events. This keeps the timer honest and gives Cancel a
        // browser turn even when the setInterval callback was delayed by optimizer work.
        const elapsed=$('optimizerProgressElapsed');
        const seconds=(performance.now()-job.started)/1000;
        if(elapsed) elapsed.textContent=`${seconds.toFixed(seconds<10?1:0)}s elapsed`;
        await new Promise(resolve=>setTimeout(resolve,0));
        lastYield=performance.now();
        if(job.cancelled) throw new OptimizerCancelledError();
      }
"""
if old_checkpoint in text:
    text=text.replace(old_checkpoint,new_checkpoint,1)
elif 'OPTIMIZER_CANCEL_TIMER_V3' not in text:
    raise SystemExit('optimizer checkpoint anchor not found')

runtime_path.write_text(text,encoding='utf-8')

# Persist a compact accuracy/provenance report beside the mined snapshot.
audit={
  'audit_version':'MINED_SITE_ACCURACY_AUDIT_V1',
  'scope':'Calculator/game-data constants checked against the refreshed public mined snapshot',
  'verified_or_matched':{
    's1_scoring':'Season 1 scoring floors/fixed stars/divisor/weights match archived season rules',
    's2_scoring':'Season 2 floor 130, relic floor 13, fixed 45, divisor 27, weights 100/18/7/33/8 match',
    's2_character_exp':'Exact Lv.130+ curve matches archived CHARACTER_XP_DATA season 2',
    's2_fantomon_exp':'Exact Lv.130+ curve matches archived FANTOMON_XP_DATA season 2',
    's2_gear_costs':'16630 base, 166.3 rate and every-5 blessing 510 Refined Ore match archived rules',
    's2_skill_costs':'12025 base and 120.25 rate match archived rules',
    's2_relic_costs':'Purple Sand 1350 base +135/step; Purple=25 Basic-equivalent matches archived rules',
    's2_realm_max':'Champion III/client Saint III multiplier 19.5; expected yields already exact',
    'server_data':'Refreshed from latest upstream snapshot',
  },
  'corrected_in_this_pass':{
    's1_character_exp_plateau':1833196,
    's1_realm_max_expected':{
      'multiplier':10.8,
      'ore':1041.7527105032607,
      'essence':1466.093120963844,
      'sand_basic_equivalent':987.7707800556983,
      'rolla':10616.811310741661,
    },
  },
  'not_mined_verified':{
    's2_open_map_5_stamina':{
      'status':'retained; public mined snapshot has no open-map gathering reward table',
      'current_model':{'ore':1400,'essence':1770,'sand':1180,'rolla':14000,'stamina':5},
    },
    's1_open_map_5_stamina':{
      'status':'mixed live/community model; not replaced by Material Realm data',
      'current_model':{'ore':900,'essence':1475,'sand':838,'rolla':9000,'stamina':5},
    },
  },
  'archived_but_not_auto_applied':{
    'future_seasons':'S3-S6 factual tables remain stored locally but dormant until their season is relevant',
    'class_skill_data':'Exact class/skill/inheritance data is archived for build validation; recommendation prose is not copied from upstream tools',
    'timeline_localization':'Official Global names/dates remain authoritative over mined/pre-release/localized labels',
  },
}
out=Path('data/mined/site-accuracy-audit.json')
out.write_text(json.dumps(audit,indent=2,sort_keys=True)+'\n',encoding='utf-8')
print('patched optimizer responsiveness + mined accuracy audit')
