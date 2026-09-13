from pathlib import Path

css = Path('assets/site.css')
text = css.read_text(encoding='utf-8')
marker = '/* MOBILE_FINAL_PASS_V2 */'
if marker in text:
    print('Mobile final pass already present.')
    raise SystemExit(0)

text += r'''

/* MOBILE_FINAL_PASS_V2
   Final responsive cleanup for phone/tablet: preserve desktop density while preventing cramped
   navigation, narrow calculator columns, overflow, and tiny touch targets. */
@media (max-width:820px){
  html,body{max-width:100%;overflow-x:hidden!important}

  .calculatorLayout{grid-template-columns:1fr!important}
  .calculator,.builds,.companions{padding-left:10px!important;padding-right:10px!important}
  .calcInputs,.calcResults,.calcPanel,.methodPanel{min-width:0!important}

  .buildGrid{grid-template-columns:repeat(2,minmax(0,1fr))!important}
  .guideSummary,.gearPanel,.priorityPanel{grid-template-columns:1fr!important}
  .guideSummary>p{border-left:0!important;border-top:1px solid var(--line);padding-left:0!important;padding-top:12px}
  .gearItem,.priorityList li{border-left:0!important}

  .postTargetHeader{display:block!important}
  .postTargetHeader>small{display:block!important;max-width:none!important;text-align:left!important;margin-top:5px}
  .postTargetOptionsBody{grid-template-columns:1fr!important}

  .optimizerProgressPanel{
    left:10px!important;
    right:10px!important;
    bottom:10px!important;
    width:auto!important;
    max-width:none!important;
  }
}

@media (max-width:620px){
  .topbar{padding:8px 10px!important}
  .headerMeta{display:none!important}
  .logoButton small{max-width:180px;white-space:nowrap!important;overflow:hidden;text-overflow:ellipsis}

  .sectionSwitch{
    width:auto!important;
    margin:12px 10px 0!important;
    display:grid!important;
    grid-template-columns:repeat(2,minmax(0,1fr))!important;
    gap:5px!important;
  }
  .sectionSwitch button{min-height:44px!important;padding:7px 8px!important;font-size:11px!important;line-height:1.2!important}

  .summary{grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:7px!important;padding:0 10px!important}
  .summary>div{border:1px solid var(--line)!important;border-radius:12px!important;padding:12px!important}
  .summary>div:last-child{grid-column:1/-1}

  .controls{gap:8px!important}
  .filters{min-width:0;flex-wrap:wrap!important}
  .filters button,.pastToggle{min-height:40px}

  .buildGrid{grid-template-columns:1fr!important}
  .classTabs{overflow-x:auto!important;scrollbar-width:none;padding:5px!important}
  .classTabs::-webkit-scrollbar{display:none}
  .classTabs button{flex:0 0 auto!important;min-width:96px;min-height:42px}
  .priorityList{grid-template-columns:1fr!important}
  .gearGrid{grid-template-columns:1fr 1fr!important}

  .calcGrid{gap:8px!important}
  .calcGrid input,.calcGrid select,
  .exactInputs input,.exactInputs select{min-height:44px!important}

  .s2TargetPresets{grid-template-columns:1fr!important;padding:9px!important}
  .s2TargetPresets>div{grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:6px!important}
  .s2TargetPresets button{min-height:42px!important;padding:7px 8px!important;white-space:nowrap!important}
  .s2TargetPresets button>span{display:inline!important;margin-left:3px;font-size:.78em;letter-spacing:.05em;color:var(--muted)}
  .s2TargetPresets small{text-align:left!important}

  .seasonPlanningRow{grid-template-columns:1fr!important;gap:7px!important}
  .finishEarlyCard{width:100%!important;justify-content:flex-start!important;gap:7px!important;flex-wrap:wrap!important}
  .finishEarlyCard input{min-width:72px!important;flex:1 1 90px!important}
  .finishEarlyMax{min-height:40px!important}
  .finishEarlyMaxHint{margin-left:0!important;text-align:left!important}

  .s2ProgressionGates{grid-template-columns:repeat(2,minmax(0,1fr))!important}

  .targetTiming{grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:7px!important}
  .postTargetGainGrid{grid-template-columns:repeat(2,minmax(0,1fr))!important}
  .postTargetOptions .postTargetToolPlan,
  .postTargetOptions .postTargetStaminaPlan{padding:9px!important}
  .postTargetPlanControls{gap:8px 12px!important}
  .postTargetPlanControls label{min-height:34px}
  .postTargetCustom{grid-template-columns:repeat(3,minmax(0,1fr))!important;gap:6px!important}
  .postTargetCustom label{min-width:0}
  .postTargetCustom label>span{font-size:7.5px!important;overflow-wrap:anywhere}
  .postTargetCustom input{min-width:0!important;width:100%!important}

  .planCostsFour,.optimizerTargets{grid-template-columns:repeat(2,minmax(0,1fr))!important}
  .todayButton{right:10px!important;bottom:10px!important}
}

@media (max-width:430px){
  .calculator,.builds,.companions{padding-left:7px!important;padding-right:7px!important}
  .calcPanel,.calcResults,.methodPanel{border-radius:14px!important}
  .currentLevelsBody,.characterPanelBody,#materialsDetails .currentLevelsBody{padding:10px!important}

  .calcGrid{grid-template-columns:1fr!important}
  .currentProgressGrid,.exactProgressGrid{grid-template-columns:1fr!important}

  .targetTiming{grid-template-columns:1fr!important}
  .postTargetCustom{grid-template-columns:1fr!important}
  .postTargetCustom label{grid-template-rows:auto 36px!important}
  .postTargetCustom label>span{font-size:8px!important}
  .postTargetCustom input{height:36px!important}

  .gearGrid{grid-template-columns:1fr!important}
  .s2TargetPresets>div{grid-template-columns:repeat(2,minmax(0,1fr))!important}
  .s2TargetPresets button{font-size:10.5px!important}

  .starTotal{font-size:34px!important}
  .planCostsFour,.optimizerTargets{grid-template-columns:1fr!important}
}
'''

css.write_text(text, encoding='utf-8')
print('Applied MOBILE_FINAL_PASS_V2 responsive cleanup.')
