from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')
marker = 'CONSISTENCY_MOBILE_V4'
if marker in s:
    print('Consistency/mobile v4 already applied')
    raise SystemExit(0)

# Wording cleanup: keep Realm context at the section level instead of repeating it on every control.
replacements = {
    'Saved tools + daily purchases': 'Owned tools + daily purchases',
    'Daily Realm purchase plan': 'Daily purchase plan',
    'Ore Realm purchases / day': 'Ore purchases / day',
    'Essence Realm purchases / day': 'Essence purchases / day',
    'Sand Realm purchases / day': 'Sand purchases / day',
    'Each purchase = 5 tools · max 20/day per Realm': 'Each purchase = 5 tools · max 20/day per material',
    'Projected daily gain': 'Daily tools added',
    '+20 H · +20 K · +20 S / reset': '+20 Hammers · +20 Knuckles · +20 Shovels per reset',
    'Extremely conservative estimate · material rolls only': 'Extremely conservative estimate · materials only',
    'Default: 0/day': 'Planner default: 0/day',
    'Current day excluded to avoid double-counting materials already entered under Saved.': 'Today excluded to avoid double-counting Saved materials.',
    '<!-- FANTOMON_TREAT_CARD_COMPACT_V1 -->Fantomon Treats · basic-eq.': '<!-- FANTOMON_TREAT_CARD_COMPACT_V1 -->Fantomon Treats',
}
for old, new in replacements.items():
    s = s.replace(old, new)

# Cleaner Stamina phrasing.
s = s.replace("const prefix=mode==='auto'?'Auto currently →':'Current plan →';", "const prefix=mode==='auto'?'Auto allocation:':'Current allocation:';")
s = s.replace("const oreStam=added.ore?` · +${fmtCompact(added.ore)} Stamina`:'';", "const oreStam=added.ore?` · Stamina +${fmtCompact(added.ore)}`:'';")
s = s.replace("const essStam=added.essence?` · +${fmtCompact(added.essence)} Stamina`:'';", "const essStam=added.essence?` · Stamina +${fmtCompact(added.essence)}`:'';")
s = s.replace("const sandStam=added.sand?` · +${fmtCompact(added.sand)} Stamina`:'';", "const sandStam=added.sand?` · Stamina +${fmtCompact(added.sand)}`:'';")

# Material Realm projection copy: spell out tool names and use a cleaner season-end label.
s = s.replace("$('hammerProjected').textContent=`Season end: ${fmt(totals.hammer)} estimated`;", "$('hammerProjected').textContent=`Season-end estimate: ${fmt(totals.hammer)}`;")
s = s.replace("$('knucklesProjected').textContent=`Season end: ${fmt(totals.knuckles)} estimated`;", "$('knucklesProjected').textContent=`Season-end estimate: ${fmt(totals.knuckles)}`;")
s = s.replace("$('shovelProjected').textContent=`Season end: ${fmt(totals.shovel)} estimated`;", "$('shovelProjected').textContent=`Season-end estimate: ${fmt(totals.shovel)}`;")
s = s.replace('Season end: —', 'Season-end estimate: —')
s = s.replace("$('realmDailyGain').textContent=`+${fmt(daily.ore*REALM_RUNS_PER_REFRESH)} H · +${fmt(daily.essence*REALM_RUNS_PER_REFRESH)} K · +${fmt(daily.sand*REALM_RUNS_PER_REFRESH)} S per future reset`;", "$('realmDailyGain').textContent=`+${fmt(daily.ore*REALM_RUNS_PER_REFRESH)} Hammers · +${fmt(daily.essence*REALM_RUNS_PER_REFRESH)} Knuckles · +${fmt(daily.sand*REALM_RUNS_PER_REFRESH)} Shovels per reset`;")
s = s.replace("$('realmDaysRemaining').textContent=`${fmt(days)} future purchase day${days===1?'':'s'} · current routine adds ${fmt(added.ore)} H / ${fmt(added.essence)} K / ${fmt(added.sand)} S`;", "$('realmDaysRemaining').textContent=`${fmt(days)} future purchase day${days===1?'':'s'} · plan adds ${fmt(added.ore)} Hammers · ${fmt(added.essence)} Knuckles · ${fmt(added.sand)} Shovels`;")

# Shop gain formatting: remove the visually awkward spaces around /day.
s = s.replace("`+${fmtCompact(value)} / day`", "`+${fmtCompact(value)}/day`")

# Result balance rows: keep the value and its unit together so Basic-eq. does not fall onto a lonely line.
s = s.replace(
    "el.innerHTML=`<span class=\"resourceRemainingLine\">Remaining: <b>${fmt(left)}</b>${unitLabel?` ${unitLabel}`:''}</span>`;",
    "el.innerHTML=`<span class=\"resourceRemainingLine\">Remaining: <b>${fmt(left)}${unitLabel?` ${unitLabel}`:''}</b></span>`;"
)

css = r'''
<style id="consistency-mobile-v4">
/* CONSISTENCY_MOBILE_V4
   Final wording/spacing pass for Materials + result cards, with explicit narrow-screen rules. */

/* Keep the section helpers compact and semantically aligned with the labels below. */
.realmInventoryTop small,.realmDailyTitle small,.shopEstimatePanel .realmInventoryTop small{
  line-height:1.35!important;
}

/* Full tool names are clearer than H/K/S; let the summary wrap naturally instead of clipping. */
.realmPlanSummary b{
  line-height:1.35!important;
  white-space:normal!important;
  overflow-wrap:anywhere!important;
}
.realmPlanSummary small{
  line-height:1.4!important;
  white-space:normal!important;
}

/* Result balance rows: one readable label/value pair, with the value + unit kept together. */
.planCosts .resourceRemainingLine{
  grid-template-columns:auto minmax(0,1fr)!important;
  column-gap:6px!important;
  align-items:baseline!important;
}
.planCosts .resourceRemainingLine b{
  min-width:0!important;
  white-space:nowrap!important;
}

/* Long projected values may wrap, but headers should stay aligned rather than collide. */
.resourceCardHead{
  gap:6px 10px!important;
}
.resourceCardHead small{
  line-height:1.3!important;
  text-align:right!important;
}

/* The shop uses the same 1/3 + 2/3 rhythm as the purchase row above. */
.shopEstimateCompact{
  grid-template-columns:repeat(3,minmax(0,1fr))!important;
  gap:9px!important;
}
.shopRefreshControl{grid-column:1!important;min-width:0!important}
.shopGainSummary{grid-column:2 / 4!important;min-width:0!important}
.shopGainSummary>div{min-width:0!important}
.shopGainSummary span{min-width:0!important}

@media(max-width:700px){
  /* Tablet/phone: stack explanatory text and keep controls touch-friendly. */
  .realmInventoryTop,.realmDailyTitle{
    align-items:flex-start!important;
    flex-direction:column!important;
    gap:3px!important;
  }
  .realmInventoryTop small,.realmDailyTitle small,.shopEstimatePanel .realmInventoryTop small{
    max-width:none!important;
    text-align:left!important;
  }
  .shopEstimateCompact{
    grid-template-columns:1fr!important;
  }
  .shopRefreshControl,.shopGainSummary{
    grid-column:1!important;
  }
  .shopGainSummary>div{
    gap:12px!important;
  }
  .realmPlanSummary{
    grid-template-columns:1fr!important;
    gap:4px!important;
  }
  .realmPlanSummary small{
    text-align:left!important;
  }
  .resourceCardHead{
    align-items:flex-start!important;
    flex-wrap:wrap!important;
  }
  .resourceCardHead small{
    max-width:100%!important;
    text-align:left!important;
  }
  .planCosts .resourceRemainingLine{
    white-space:normal!important;
  }
}

@media(max-width:520px){
  /* Phone: no compressed three-across Realm controls. */
  .realmInventoryGrid,.realmDailyInputs,.shopEstimateCompact{
    grid-template-columns:1fr!important;
  }
  .realmDailyInputs>label,.realmInventoryGrid>label,.shopRefreshControl,.shopGainSummary{
    min-width:0!important;
    width:100%!important;
  }
  .realmDailyInputs input,.realmInventoryGrid input,.shopRefreshControl input{
    width:100%!important;
  }
  .shopGainSummary>div{
    min-height:30px!important;
  }
  .planCosts .resourceRemainingLine b{
    white-space:normal!important;
  }
}
</style>
'''

needle = '</head>'
if needle not in s:
    raise SystemExit('head close not found')
s = s.replace(needle, css + '\n' + needle, 1)
p.write_text(s, encoding='utf-8')
print('Applied consistency/mobile v4')
