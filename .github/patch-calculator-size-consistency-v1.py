from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
marker='CALCULATOR_SIZE_CONSISTENCY_V1'
if marker in s:
    print('already applied')
    raise SystemExit(0)

css=r'''
<style id="calculator-size-consistency-v1">
/* CALCULATOR_SIZE_CONSISTENCY_V1
   Presentation-only normalization for the Primostar calculator. Keep one clear
   hierarchy for panels, nested cards, fields, helper text and result/reference UI. */

/* Overall rhythm */
.calculatorLayout{gap:16px!important}
.calcInputs{gap:12px!important}
.calcPanel,.calcResults,.methodPanel{border-radius:18px!important}
.calcPanel{padding:20px!important}
.currentLevelsBody{padding:18px 20px 20px!important}
.currentLevelsPanel>summary{padding:17px 20px!important}
.currentLevelsPanel>summary span{font-size:13px!important}
.currentLevelsPanel>summary small{font-size:10px!important;line-height:1.35!important}
.calcPanel h3,.calcResults h3{font-size:13px!important;margin-bottom:13px!important}

/* One field scale across normal, resource, Realm and advanced inputs */
.calcGrid{gap:11px!important}
.calcGrid label,
.resourceCardFields label>span,
.realmInventoryGrid label,
.realmDailyInputs label,
.accuracyGrid label,
.exactInputsBody label,
.realmPresetPicker{
  font-size:9px!important;
  line-height:1.25!important;
  letter-spacing:.05em!important;
  font-weight:820!important;
}
.calcGrid input,.calcGrid select,
.resourceCardFields input,
.realmInventoryGrid input,
.realmDailyInputs input,
.accuracyGrid input,
.exactInputsBody input,
.realmPresetPicker select,
.staminaSimple select{
  min-height:42px!important;
  border-radius:9px!important;
  padding:8px 10px!important;
  font-size:13px!important;
  line-height:1.2!important;
}

/* Resource-entry cards */
.resourceCards{gap:10px!important}
.resourceCard{border-radius:12px!important;padding:12px 13px!important;gap:8px!important}
.resourceCardHead{gap:10px!important}
.resourceCardHead strong{font-size:11px!important;line-height:1.3!important}
.resourceCardHead small{font-size:9px!important;line-height:1.3!important}
.resourceCardFields{gap:8px!important}
.resourceInputs>div>small,.treatEquivalent{font-size:9px!important;line-height:1.4!important}

/* Material Realm: same card/input hierarchy as the resource-entry cards */
.realmInventory{border-radius:12px!important;margin-top:12px!important;padding:13px 14px!important}
.realmInventoryTop{margin-bottom:9px!important;gap:12px!important}
.realmInventoryTop strong{font-size:12px!important;line-height:1.3!important}
.realmInventoryTop small{font-size:9px!important;line-height:1.35!important}
.realmInventoryGrid{gap:9px!important}
.realmInventoryGrid input{margin-top:5px!important}
.realmInventoryGrid label>small{font-size:9px!important;line-height:1.35!important;margin-top:4px!important}
.realmInventoryGrid .realmAfterPlan{margin-top:2px!important}
.realmDailyPlanRow{gap:12px!important;margin-top:12px!important;padding-top:12px!important}
.realmDailyTitle{font-size:9px!important;margin-bottom:7px!important}
.realmDailyTitle small{font-size:9px!important}
.realmDailyInputs{gap:8px!important}
.realmDailyInputs small{font-size:9px!important;line-height:1.35!important;margin-top:4px!important}
.realmPlanSummary{border-radius:10px!important;min-height:62px!important;padding:9px 11px!important}
.realmPlanSummary span{font-size:8px!important}
.realmPlanSummary b{font-size:12px!important}
.realmPlanSummary small{font-size:9px!important;line-height:1.35!important}

/* Nested controls should feel related instead of each having a separate scale */
.staminaSimple,.accuracyInputs,.exactInputs{border-radius:11px!important}
.accuracyInputs>summary{padding:12px 14px!important;font-size:10px!important}
.accuracyInputsBody{padding:13px 14px!important}
.exactInputs>summary{padding:11px 13px!important;font-size:10px!important}
.exactInputsBody{padding:12px 13px!important}
.optimizerNote,.optimizedResult{border-radius:10px!important;padding:10px 12px!important;font-size:9px!important;line-height:1.5!important}

/* Main result hierarchy */
.calcResults{padding:20px!important}
.calcEyebrow{font-size:9px!important;line-height:1.3!important}
.resultHeadline{margin:3px 0 13px!important}
.starTotal{font-size:46px!important}
.starTotal small{font-size:14px!important}
.resultScoreLine{border-radius:11px!important;padding:10px 12px!important;margin-bottom:18px!important}
.resultScoreLine small{font-size:9px!important}
.resultScoreLine b,.resultScoreLine i{font-size:13px!important}
.resultScoreLine em{font-size:11px!important}
.targetMessage{font-size:10px!important;line-height:1.5!important;margin-bottom:16px!important}
.optimizerTargets{gap:8px!important;margin-bottom:8px!important}
.optimizerTargets span{border-radius:10px!important;padding:10px 11px!important;font-size:8px!important}
.optimizerTargets b{font-size:15px!important}
.optimizerSummary{font-size:10px!important;line-height:1.5!important;margin:9px 0 17px!important}
.suggestedGear{gap:7px!important;margin-bottom:16px!important}
.suggestedGear span{border-radius:10px!important;padding:9px 6px!important;font-size:8px!important}
.suggestedGear b{font-size:16px!important}

/* Result resource cards + joined raw/tool inset */
.planCosts,.planCostsFour{gap:9px!important;margin:0 0 18px!important}
.planCosts>span{border-radius:12px!important;padding:12px 13px!important;gap:6px!important;font-size:9px!important;line-height:1.3!important}
.planCosts b{font-size:18px!important;line-height:1.15!important}
.planCosts small{font-size:9px!important;line-height:1.4!important}
.planCosts small.rawRemaining{padding:9px 10px 8px!important;border-radius:10px!important}
.planCosts small.rawRemaining:has(+ small.toolBalance:not([hidden])){border-radius:10px 10px 0 0!important}
.planCosts small.rawRemaining + small.toolBalance:not([hidden]){padding:8px 10px 9px!important;border-radius:0 0 10px 10px!important;font-size:9px!important}
.planCosts .resourceRemainingLine,.planCosts .reserveRequirementLine,.planCosts .toolSimpleLine{line-height:1.35!important}

/* Expandable reference/detail sections */
.resultDetails{margin:5px 0 14px!important}
.resultDetails>summary{min-height:42px!important;padding:11px 0!important;font-size:10px!important;line-height:1.3!important}
.resultDetails>div{padding-top:8px!important}
.primostarRewardsBody{padding:8px 0 3px!important}
.primostarRewardsIntro{font-size:10px!important;line-height:1.45!important;margin-bottom:11px!important}
.primostarRewardSeason{border-radius:11px!important}
.primostarRewardSeason h4{padding:9px 11px!important;font-size:9px!important}
.primostarRewardRow{grid-template-columns:60px minmax(0,1fr) auto!important;gap:9px!important;padding:8px 10px!important;font-size:9px!important;line-height:1.35!important}
.scoreBreakdown{border-radius:11px!important;margin-bottom:18px!important}
.scoreBreakdown div{padding:9px 11px!important}
.scoreBreakdown dt,.scoreBreakdown dd{font-size:10px!important}
.breakdownExplain,.rewardCount{font-size:9px!important;line-height:1.5!important}
.rewardTotals{gap:8px!important}
.rewardTotals span{border-radius:10px!important;padding:9px 10px!important;font-size:9px!important}
.rewardTotals b{font-size:12px!important}

/* Buttons and action row */
.calcActions{gap:10px!important;padding:3px 2px!important}
.calcActions button{min-height:42px!important;border-radius:10px!important;padding:9px 14px!important;font-size:10px!important}
.calcActions span{font-size:9px!important;line-height:1.4!important}

/* Medium/mobile: retain readability while tightening vertical sprawl. */
@media(max-width:760px){
  .calculator{padding-left:12px!important;padding-right:12px!important}
  .calculatorLayout{gap:12px!important}
  .calcInputs{gap:10px!important}
  .calcPanel,.calcResults{padding:15px!important;border-radius:15px!important}
  .currentLevelsPanel{padding:0!important}
  .currentLevelsPanel>summary{padding:14px 15px!important;min-height:46px!important}
  .currentLevelsBody{padding:14px 15px 15px!important}
  .calcGrid label,.resourceCardFields label>span,.realmInventoryGrid label,.realmDailyInputs label,.accuracyGrid label,.exactInputsBody label{font-size:10px!important}
  .calcGrid input,.calcGrid select,.resourceCardFields input,.realmInventoryGrid input,.realmDailyInputs input,.accuracyGrid input,.exactInputsBody input,.realmPresetPicker select,.staminaSimple select{min-height:44px!important;font-size:14px!important}
  .resourceCard{padding:11px 12px!important}
  .resourceCardHead strong{font-size:12px!important}
  .resourceCardHead small{font-size:10px!important}
  .resourceInputs>div>small,.treatEquivalent{font-size:10px!important}
  .realmInventory{padding:12px!important}
  .realmInventoryTop strong{font-size:13px!important}
  .realmInventoryTop small{font-size:10px!important}
  .realmInventoryGrid label>small,.realmDailyInputs small{font-size:10px!important}
  .starTotal{font-size:42px!important}
  .starTotal small{font-size:14px!important}
  .targetMessage,.optimizerSummary{font-size:11px!important}
  .resultScoreLine{padding:11px 12px!important}
  .resultScoreLine small{font-size:10px!important}
  .resultScoreLine b,.resultScoreLine i{font-size:14px!important}
  .optimizerTargets span{font-size:9px!important;padding:10px!important}
  .optimizerTargets b{font-size:16px!important}
  .suggestedGear span{font-size:9px!important;min-height:58px!important}
  .suggestedGear b{font-size:17px!important}
  .planCosts{gap:8px!important}
  .planCosts>span{padding:12px!important;font-size:10px!important}
  .planCosts b{font-size:19px!important}
  .planCosts small,.planCosts small.rawRemaining + small.toolBalance:not([hidden]){font-size:10px!important}
  .resultDetails>summary{min-height:44px!important;font-size:10px!important}
  .primostarRewardsIntro{font-size:10px!important}
  .primostarRewardRow{grid-template-columns:62px minmax(0,1fr) auto!important;padding:9px 10px!important;font-size:10px!important}
}

@media(max-width:520px){
  .calculator{padding-left:10px!important;padding-right:10px!important}
  .calcPanel,.calcResults{padding:13px!important}
  .currentLevelsPanel{padding:0!important}
  .currentLevelsPanel>summary{padding:13px!important}
  .currentLevelsBody{padding:13px!important}
  .realmInventory{padding:11px!important}
  .realmInventoryTop{align-items:flex-start!important;flex-direction:column!important;gap:3px!important}
  .resourceCards,.planCosts{gap:8px!important}
  .starTotal{font-size:40px!important}
  .resultScoreLine{gap:7px!important}
  .primostarRewardColumns{grid-template-columns:1fr!important}
  .primostarRewardColumns>.primostarRewardList + .primostarRewardList{border-left:0!important;border-top:1px solid var(--line)!important}
}
</style>
'''

if '</head>' not in s:
    raise SystemExit('</head> not found')
s=s.replace('</head>',css+'\n</head>',1)
p.write_text(s,encoding='utf-8')
print('applied calculator size and consistency pass')
