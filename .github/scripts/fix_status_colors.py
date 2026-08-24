from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
marker='/* STATUS_COLOR_SEMANTICS_V1 */'
if marker in s:
    raise SystemExit('status color semantics already applied')

css=r'''

/* STATUS_COLOR_SEMANTICS_V1
   Rosé Pine stays the UI accent, but calculator state colors are semantic:
   blue/foam = healthy/positive, iris = informational, gold = caution, love = shortage/error. */
:root{
  --status-positive:#286983;
  --status-info:#907aa9;
  --status-warning:#ea9d34;
  --status-negative:#b4637a;
}
:root[data-theme="dark"]{
  --status-positive:#9ccfd8;
  --status-info:#c4a7e7;
  --status-warning:#f6c177;
  --status-negative:#eb6f92;
}

/* Material Realm inventory: current value is neutral, projection is info, remainder is positive. */
.realmInventoryGrid .realmCurrentValue{color:var(--secondary-text)!important}
#hammerProjected,#knucklesProjected,#shovelProjected{color:var(--status-info)!important}
.realmInventoryGrid .realmAfterPlan{color:var(--status-positive)!important}
.realmInventoryGrid .realmAfterPlan.toolLow{color:var(--status-warning)!important}

/* Daily purchase guidance. */
.realmDailyInputs small{color:var(--status-positive)!important}
.realmDailyInputs small.realmRecommendUp{color:var(--status-warning)!important}
.realmDailyInputs small.realmRecommendMax{color:var(--status-negative)!important}
.realmPlanSummary b{color:var(--status-positive)!important}

/* Results/resource cards: leftover/surplus is positive; usage is neutral; shortages stay negative. */
.planCosts small{color:var(--status-positive)!important}
.planCosts small.shortfallCount,
.planCosts .planShort,
.planCosts .hardShort{color:var(--status-negative)!important}
.planCosts .realmBridge{color:var(--status-warning)!important}
.planCosts small.toolBalance{color:var(--secondary-text)!important}
.planCosts small.toolBalance.toolLeft{color:var(--status-positive)!important}
.planCosts small.toolBalance.toolNeed,
.planCosts .toolNeedLine{color:var(--status-negative)!important}

/* Other clearly positive calculator states. */
.resultScoreLine i,
.resultScoreLine em:not(.notMet),
.rewardTotals b,
.exactInputs .inputGood{color:var(--status-positive)!important}
.resultScoreLine em.notMet,
.exactInputs .inputWarning{color:var(--status-negative)!important}
.materialRealmRecommendation.realmFeasible{
  border-color:color-mix(in srgb,var(--status-positive) 55%,var(--line))!important;
  background:color-mix(in srgb,var(--status-positive) 8%,var(--surface))!important;
}
.materialRealmRecommendation.realmFeasible b{color:var(--status-positive)!important}
.materialRealmRecommendation.realmImpossible b{color:var(--status-negative)!important}
'''

if '</style>' not in s:
    raise SystemExit('style closing tag not found')
s=s.replace('</style>',css+'\n</style>',1)
p.write_text(s,encoding='utf-8')
print('Applied semantic positive/info/warning/negative calculator colors.')
# trigger
