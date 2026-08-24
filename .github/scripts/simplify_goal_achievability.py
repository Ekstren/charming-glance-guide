from pathlib import Path
import re

p=Path('index.html')
s=p.read_text(encoding='utf-8')
marker='/* GOAL_ACHIEVABILITY_CLEANUP_V1 */'
if marker in s:
    raise SystemExit('goal achievability cleanup already applied')

# Make it explicit that the daily numeric inputs are refresh counts, not raw tool counts.
s=s.replace(
    '<span class="realmDailyTitle">Daily purchase plan <small>0–20 refreshes per Realm</small></span>',
    '<span class="realmDailyTitle">Daily Realm refresh plan <small>Each refresh = 5 tools · max 20/day per Realm</small></span>'
)
s=s.replace('<label>Hammers / day<input id="realmDailyOre"', '<label>Ore Realm refreshes / day<input id="realmDailyOre"')
s=s.replace('<label>Knuckles / day<input id="realmDailyEssence"', '<label>Essence Realm refreshes / day<input id="realmDailyEssence"')
s=s.replace('<label>Shovels / day<input id="realmDailySand"', '<label>Sand Realm refreshes / day<input id="realmDailySand"')

# Simplify per-resource shortage output to one useful status line.
pat=re.compile(r"  function setRealmShortfallBreakdown\(id,planShort,yieldVal,itemName,maxExtraRuns,hardShort,resourceName='resource',appendText=''\)\{.*?\n  \}\n  function setToolBalance", re.S)
replacement="""  function setRealmShortfallBreakdown(id,planShort,yieldVal,itemName,maxExtraRuns,hardShort,resourceName='resource',appendText=''){
    const el=$(id); if(!el) return;
    const short=Math.max(0,Math.ceil(Number(planShort)||0));
    const hard=Math.max(0,Math.ceil(Number(hardShort)||0));
    el.classList.remove('shortfallCount');
    if(hard>0){
      el.innerHTML=`<span class=\"hardShort\">${fmt(hard)} short at max Realm capacity${appendText||''}</span>`;
      el.classList.add('shortfallCount');
      return;
    }
    if(short>0){
      el.innerHTML=`<span class=\"realmBridge\">${fmt(short)} short on current refresh plan · covered by extra refreshes${appendText||''}</span>`;
      return;
    }
    el.textContent=`Covered by current refresh plan${appendText||''}`;
  }
  function setToolBalance"""
s,n=pat.subn(replacement,s,count=1)
if n!=1:
    raise SystemExit(f'setRealmShortfallBreakdown replacement count={n}')

# The hard-short warning is the only achievability warning when the target cannot be reached.
old="$('targetMessage').textContent=`⚠ Daily plan is short ${dailyShortBits.join(' · ')||'resources'}. After using every remaining extra Realm slot, hard short = ${shortageBits.join(' · ')||'resources'}. No fallback target.`;"
new="$('targetMessage').textContent=`⚠ Goal not achievable with remaining Realm capacity. Short at max 20 refreshes/day: ${shortageBits.join(' · ')||'resources'}.`;"
if old not in s:
    raise SystemExit('old hard-short target warning not found')
s=s.replace(old,new,1)

# Replace the verbose/contradictory Material Realm callout with a single target warning.
pat2=re.compile(r"    if\(hasRealmNeed\|\|resourceBlocked\)\{.*?\n    \}else\{realmRec\.hidden=true;realmRec\.textContent='';realmRec\.classList\.remove\('realmFeasible','realmImpossible'\);realmRec\.removeAttribute\('title'\);\}", re.S)
replacement2="""    const dailySuggested=suggestedRealmDailyPlan(plan,cfg);
    if(!resourceBlocked && hasRealmNeed){
      $('targetMessage').hidden=false;
      $('targetMessage').classList.add('warning');
      const route=dailySuggested.changed
        ? ` Recommended refreshes/day: Ore ${dailySuggested.ore} · Essence ${dailySuggested.essence} · Sand ${dailySuggested.sand}.`
        : '';
      $('targetMessage').textContent=`⚠ Goal is achievable, but your current Material Realm refresh plan is too low.${route}`;
    }
    realmRec.hidden=true;realmRec.textContent='';realmRec.classList.remove('realmFeasible','realmImpossible');realmRec.removeAttribute('title');"""
s,n=pat2.subn(replacement2,s,count=1)
if n!=1:
    raise SystemExit(f'Material Realm callout replacement count={n}')

css=r'''
<style id="goal-achievability-cleanup">
/* GOAL_ACHIEVABILITY_CLEANUP_V1
   Keep one clear goal-status warning and remove low-value tool accounting from result cards. */
.planCosts small.toolBalance{display:none!important}
.planCosts span{gap:6px!important}
.targetMessage:not([hidden]){margin:10px 0 14px!important;min-height:0!important}
.materialRealmRecommendation{display:none!important}
</style>
'''
if '</head>' not in s:
    raise SystemExit('head closing tag not found')
s=s.replace('</head>',css+'\n</head>',1)
p.write_text(s,encoding='utf-8')
print('Simplified goal achievability, fixed Realm refresh wording, and removed contradictory callout.')
# trigger
