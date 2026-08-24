from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
marker='/* GOAL_ACHIEVABILITY_CLEANUP_V1 */'
if marker in s:
    raise SystemExit('goal achievability cleanup already applied')

# Make it explicit that these numbers are paid refresh counts; each refresh creates five tools.
old_title='<span class="realmDailyTitle">Daily purchase plan <small>0–20 refreshes per Realm</small></span>'
new_title='<span class="realmDailyTitle">Daily Realm refresh plan <small>Each refresh = 5 tools · max 20/day per Realm</small></span>'
if old_title not in s:
    raise SystemExit('daily Realm title not found')
s=s.replace(old_title,new_title,1)
s=s.replace('<label>Hammers / day<input id="realmDailyOre"', '<label>Ore Realm refreshes / day<input id="realmDailyOre"',1)
s=s.replace('<label>Knuckles / day<input id="realmDailyEssence"', '<label>Essence Realm refreshes / day<input id="realmDailyEssence"',1)
s=s.replace('<label>Shovels / day<input id="realmDailySand"', '<label>Sand Realm refreshes / day<input id="realmDailySand"',1)

# If even max Realm capacity cannot reach the goal, say only that.
old="$('targetMessage').textContent=`⚠ Daily plan is short ${dailyShortBits.join(' · ')||'resources'}. After using every remaining extra Realm slot, hard short = ${shortageBits.join(' · ')||'resources'}. No fallback target.`;"
new="$('targetMessage').textContent=`⚠ Goal not achievable with remaining Realm capacity. Short at max 20 refreshes/day: ${shortageBits.join(' · ')||'resources'}.`;"
if old not in s:
    raise SystemExit('old hard-short target warning not found')
s=s.replace(old,new,1)

# For reachable goals that need more than the selected daily Realm routine, use the same single warning area.
needle="      realmRec.innerHTML=`<b>Material Realm:</b> ${extraText} · daily ${dailyPreset.ore}/${dailyPreset.essence}/${dailyPreset.sand} already included${priceNote}${hardNotes.length?` · ${hardNotes.join(' · ')}`:''}${suggestionLine}`;\n      realmRec.title=realmDetailParts.join(' · ');"
insert="""      realmRec.innerHTML=`<b>Material Realm:</b> ${extraText} · daily ${dailyPreset.ore}/${dailyPreset.essence}/${dailyPreset.sand} already included${priceNote}${hardNotes.length?` · ${hardNotes.join(' · ')}`:''}${suggestionLine}`;
      if(!resourceBlocked && hasRealmNeed){
        $('targetMessage').hidden=false;
        $('targetMessage').classList.add('warning');
        const route=dailySuggested.changed
          ? ` Recommended refreshes/day: Ore ${dailySuggested.ore} · Essence ${dailySuggested.essence} · Sand ${dailySuggested.sand}.`
          : '';
        $('targetMessage').textContent=`⚠ Goal is achievable, but your current Material Realm refresh plan is too low.${route}`;
      }
      realmRec.title=realmDetailParts.join(' · ');"""
if needle not in s:
    raise SystemExit('Material Realm render insertion point not found')
s=s.replace(needle,insert,1)

css=r'''
<style id="goal-achievability-cleanup">
/* GOAL_ACHIEVABILITY_CLEANUP_V1
   One goal-status warning; resource cards keep only the useful balance/shortfall line. */
.materialRealmRecommendation{display:none!important}
.planCosts small.toolBalance{display:none!important}
.planCosts small.shortfallBreakdown .planShort{display:none!important}
.planCosts span{gap:6px!important}
.targetMessage:not([hidden]){margin:10px 0 14px!important;min-height:0!important}
</style>
'''
if '</head>' not in s:
    raise SystemExit('head closing tag not found')
s=s.replace('</head>',css+'\n</head>',1)
p.write_text(s,encoding='utf-8')
print('Simplified goal achievability and clarified Material Realm refresh counts.')
# trigger 2
