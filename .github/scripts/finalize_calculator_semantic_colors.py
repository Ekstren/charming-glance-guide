from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
marker='/* CALCULATOR_SEMANTIC_COLORS_FINAL_V1 */'
if marker in s:
    raise SystemExit('calculator semantic final colors already applied')

css=r'''
<style id="calculator-semantic-colors-final">
/* CALCULATOR_SEMANTIC_COLORS_FINAL_V1
   Final cascade-level semantic pass. This intentionally lives after legacy v57/v59
   styles so rose stays an interaction accent instead of reading like an error state. */

/* Saved-material cards: projections are information, not warnings. */
.resourceCardHead small,
#oreProjected,#essenceProjected,#sandProjected,#treatProjected{
  color:var(--status-info)!important;
}
.treatEquivalent{color:var(--secondary-text)!important}
.staminaCurrentPlan{color:var(--status-info)!important}
.staminaCurrentPlan .staminaGain{color:var(--status-positive)!important}

/* Material Realm: neutral current value, informational future estimate, positive remainder. */
.realmInventoryGrid .realmCurrentValue{color:var(--secondary-text)!important}
#hammerProjected,#knucklesProjected,#shovelProjected{color:var(--status-info)!important}
.realmInventoryGrid .realmAfterPlan{color:var(--status-positive)!important}
.realmInventoryGrid .realmAfterPlan.toolLow{color:var(--status-warning)!important}
.realmDailyInputs small{color:var(--status-positive)!important}
.realmDailyInputs small.realmRecommendUp{color:var(--status-warning)!important}
.realmDailyInputs small.realmRecommendMax{color:var(--status-negative)!important}
.realmPlanSummary b{color:var(--status-positive)!important}

/* Result cards: surplus/left is good; usage is neutral; actual need/shortfall is negative. */
.planCosts small{color:var(--status-positive)!important}
.planCosts small.shortfallCount,
.planCosts .planShort,
.planCosts .hardShort{color:var(--status-negative)!important}
.planCosts .realmBridge{color:var(--status-warning)!important}
.planCosts small.toolBalance{color:var(--secondary-text)!important}
.planCosts small.toolBalance.toolLeft{color:var(--status-positive)!important}
.planCosts small.toolBalance.toolNeed{color:var(--status-negative)!important}
.planCosts small.toolBalance .toolUsedLine{color:var(--secondary-text)!important}
.planCosts small.toolBalance .toolRemainingLine{color:var(--status-positive)!important}
.planCosts small.toolBalance .toolNeedLine{color:var(--status-negative)!important}

/* Recommended gear is informational, not a rose/error state. */
.suggestedGear span{
  color:var(--status-info)!important;
  border-color:color-mix(in srgb,var(--status-info) 34%,var(--line))!important;
  background:color-mix(in srgb,var(--status-info) 7%,var(--surface))!important;
}
.suggestedGear b{color:var(--ink)!important}

/* Score/result semantics. */
.resultScoreLine i,
.resultScoreLine em:not(.notMet),
.rewardTotals b,
.exactInputs .inputGood{color:var(--status-positive)!important}
.resultScoreLine em.notMet,
.exactInputs .inputWarning{color:var(--status-negative)!important}
</style>
'''

if '</head>' not in s:
    raise SystemExit('head closing tag not found')
s=s.replace('</head>',css+'\n</head>',1)
p.write_text(s,encoding='utf-8')
print('Appended final calculator semantic color overrides after all legacy styles.')
# trigger
