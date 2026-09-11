from pathlib import Path

path = Path('assets/site.css')
css = path.read_text(encoding='utf-8')
start = '/* MOBILE_CALCULATOR_PASS_V1_START */'
end = '/* MOBILE_CALCULATOR_PASS_V1_END */'
if start in css and end in css:
    a = css.index(start)
    b = css.index(end, a) + len(end)
    css = (css[:a].rstrip() + '\n\n' + css[b:].lstrip())

block = r'''/* MOBILE_CALCULATOR_PASS_V1_START */
/* Dedicated phone/tablet cleanup layered after the accumulated desktop calculator rules. */
@media (max-width:760px){
  html,body{max-width:100%;overflow-x:hidden}
  .topbar{min-height:64px;padding:9px 12px;gap:10px}
  .logoButton{min-width:0;gap:10px}
  .logo{width:40px;height:40px;border-radius:12px;font-size:14px}
  .logoButton strong{font-size:14px}
  .logoButton small{font-size:9px}
  .themeToggle{flex:0 0 34px}

  .calculator{margin:18px auto 64px;padding:0 10px}
  .calculatorLayout{gap:10px}
  .calcInputs{gap:8px}
  .calcPanel,.calcResults,.methodPanel{border-radius:14px}
  .currentLevelsPanel>summary{min-height:44px;padding:13px 14px}
  .currentLevelsBody,.characterPanelBody,#materialsDetails .currentLevelsBody{padding:12px!important}
  .calcResults{padding:16px}
  .starTotal{font-size:40px}

  .calcGrid{gap:9px!important}
  .calcGrid label{min-width:0}
  .calcGrid input,.calcGrid select{min-width:0;min-height:42px!important;padding:8px 10px!important}

  .s2TargetPresets{padding:9px;gap:8px}
  .s2TargetPresets>div{display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:6px!important}
  .s2TargetPresets button{width:100%;min-height:42px!important}

  .seasonPlanningRow{grid-template-columns:1fr!important;gap:7px!important;margin-top:10px!important}
  .seasonPlanningRow .seasonDeadline{min-height:48px!important;padding:9px 10px!important;display:grid!important;grid-template-columns:auto minmax(0,1fr);column-gap:8px;row-gap:3px;align-content:center}
  .seasonDeadline b{min-width:0;white-space:normal;line-height:1.3}
  .seasonDeadline small{grid-column:1/-1;margin-left:0!important;text-align:left;line-height:1.25}
  .finishEarlyCard{width:100%;min-height:46px!important;padding:8px 10px!important;justify-content:flex-end!important;gap:6px!important}
  .finishEarlyCard input{width:34px!important;min-width:34px!important;max-width:34px!important;flex-basis:34px!important;height:28px!important}

  .materialsStaminaRow select{min-height:42px}
  .resourceCards>.resourceCard{min-width:0}
  .resourceCardHead{gap:8px}
  .resourceCardHead small{min-width:0;white-space:normal!important;line-height:1.25}
  .resourceCardFields input{min-height:42px!important}

  .resultScoreLine>span{max-width:100%;flex-wrap:wrap}
  .optimizerTargets span,.planCosts span,.suggestedGear span{min-width:0}
  .optimizerSummary,.targetMessage{overflow-wrap:anywhere}
  .exactInputs>summary,.accuracyInputs>summary,.resultDetails>summary{min-height:44px;align-items:center}
}

@media (max-width:560px){
  .sectionSwitch{display:grid;grid-template-columns:1fr 1fr;margin:12px 10px 0;gap:5px}
  .sectionSwitch button{width:100%;min-height:42px;padding:8px 6px;font-size:10px}

  .calculator{padding:0 8px}
  .characterPanelBody>.calcGrid,.currentProgressGrid{grid-template-columns:1fr!important}
  .resourceInputsFour{grid-template-columns:1fr!important}
  .resourceCardFields{grid-template-columns:1fr 1fr!important}

  .materialsStaminaRow{grid-template-columns:1fr!important;gap:6px}
  .materialsStaminaRow select{width:100%}
  .materialsStaminaRow small{grid-column:auto!important;text-align:left!important}

  .accuracyGrid{grid-template-columns:1fr!important}
  .realmPresetRow{gap:7px}
  .calcActions{align-items:stretch;flex-direction:column}
  .calcActions button{width:100%;min-height:44px}
  .calcActions span{text-align:left}

  .resultScoreLine{padding:9px 10px}
  .resultScoreLine>span{width:100%;justify-content:flex-start}
  .optimizerTargets{grid-template-columns:repeat(3,minmax(0,1fr))}
  .planCostsFour{grid-template-columns:repeat(2,minmax(0,1fr))}
}

@media (max-width:400px){
  .topbar{padding-inline:10px}
  .logoButton strong{font-size:13px}
  .logoButton small{font-size:8px}
  .calculator{padding:0 6px}
  .currentLevelsBody,.characterPanelBody,#materialsDetails .currentLevelsBody{padding:10px!important}
  .calcResults{padding:14px}
  .starTotal{font-size:36px}
  .s2TargetPresets{padding:8px}
  .finishEarlyCard{padding-inline:9px!important}
  .resourceCardFields{gap:6px!important}
  .optimizerTargets{gap:5px}
  .optimizerTargets span{padding:8px 6px}
  .planCostsFour{gap:6px}
  .planCosts span{padding:9px}
}
/* MOBILE_CALCULATOR_PASS_V1_END */'''

css = css.rstrip() + '\n\n' + block + '\n'
path.write_text(css, encoding='utf-8')
print('Applied mobile calculator pass v1')
