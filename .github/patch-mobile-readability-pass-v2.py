from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')
marker = 'MOBILE_READABILITY_PASS_V2'
if marker in s:
    print('mobile/readability pass already applied')
    raise SystemExit(0)

css = r'''
<style id="mobile-readability-pass-v2">
/* MOBILE_READABILITY_PASS_V2 */
/* Readability floor: keep the compact dashboard feel without forcing users to read 8–10px UI copy. */
html{-webkit-text-size-adjust:100%;text-size-adjust:100%}
body{line-height:1.5}
:root{--muted:#70675f;--secondary-text:#665d55}
:root[data-theme=dark]{--muted:#ada195;--secondary-text:#b9ada1}

.logoButton small,.headerMeta span{font-size:11px}
.sectionHeading span,.summary span{font-size:11px}
.sectionHeading>p{font-size:12px;line-height:1.6}
.classTabs button{font-size:12px}
.guideSummary span,.guideSummary>p b,.gearIntro>span,.gearItem span,.priorityIntro>span,.skillGroup>span,.calcEyebrow{font-size:10px}
.guideSummary p,.gearIntro p,.gearItem p,.priorityList p,.buildCard header p,.buildCard ul{font-size:11px;line-height:1.58}
.skillGroup b,.buildSource{font-size:10px}
.priorityList strong{font-size:13px}

.currentLevelsPanel>summary small,.calcPanel h3,.calcResults h3{font-size:11px}
.autoToggle,.optimizerNote,.calcGrid label,.projectionCallout span,.calcAdvanced summary,.calcActions span,.scoreSummary span,.optimizerSummary,.yieldInputs>p,.planCosts span,.resultDetails>summary,.shortfallPlan p,.shortfallPlan ol,.rewardCount,.breakdownExplain,.methodPanel p,.timelineNowHead span,.timelineNowEmpty,.eventSourceNote{font-size:10px}
.seasonDeadline span,.resourceGrace small,.projectionCallout small,.optimizerTargets span,.resourceInputs label,.resourceInputs small,.resourceUse span,.resourceCaption,.affordableResult,.optimizedResult span,.planCosts small.toolBalance,.materialFallback .materialNote,.suggestedGear span,.timelineNowCard small,.entry .activePill{font-size:9px}
.seasonDeadline b,.rolloverHold label,.targetMessage,.finalLevelLine,.resourceInputs strong,.resourceUse b,.affordableResult b,.optimizedResult b,.shortfallPlan p,.shortfallPlan ol,.rewardTotals span,.scoreBreakdown dt,.scoreBreakdown dd,.milestoneNote,.methodPanel summary,.timelineNowCard strong,.huntPhases span,.eventCycleCard p{font-size:11px}
.rolloverHold input[type=number],.resourceInputs input{font-size:13px}
.planCosts small,.rewardTotals b,.timelineNowHead b{font-size:12px}
.targetMessage,.optimizerSummary,.rewardCount,.breakdownExplain,.methodPanel p,.timelineIntelBody,.eventCycleCard p{line-height:1.6}

/* Give keyboard/touch users a visible focus treatment without changing mouse styling. */
button:focus-visible,a:focus-visible,input:focus-visible,select:focus-visible,summary:focus-visible{outline:2px solid var(--green);outline-offset:2px}

@media(max-width:760px){
  body{font-size:14px}
  .topbar{min-height:64px;gap:10px;padding:9px 12px}
  .logo{width:40px;height:40px;border-radius:12px}
  .logoButton{gap:10px;min-width:0}
  .logoButton strong{font-size:15px}
  .logoButton small{font-size:11px;white-space:normal;line-height:1.25}
  .headerTools{gap:6px;flex:0 0 auto}
  .headerMeta{gap:5px;min-width:0}
  .headerMeta span{padding:6px 8px;font-size:10px}
  .themeToggle{width:40px;height:40px;flex:0 0 40px}

  .sectionSwitch{margin:12px 12px 0;max-width:none;overflow-x:auto;overscroll-behavior-inline:contain;scrollbar-width:none;-webkit-overflow-scrolling:touch}
  .sectionSwitch::-webkit-scrollbar,.classTabs::-webkit-scrollbar{display:none}
  .sectionSwitch button{flex:0 0 auto;min-width:92px;min-height:44px;padding:0 13px;font-size:12px}

  .summary{grid-template-columns:1fr 1fr;gap:8px;margin-top:14px;padding:0 12px}
  .summary div{border:1px solid var(--line)!important;border-radius:12px!important;padding:14px 15px}
  .summary div:first-child{grid-column:1/-1}
  .summary span{margin-bottom:5px;font-size:10px;letter-spacing:.065em}
  .summary strong{font-size:15px;white-space:normal;text-overflow:clip;overflow:visible}
  .summary div:first-child strong{font-size:28px}

  .builds,.calculator{margin-top:18px;padding-left:12px;padding-right:12px}
  .sectionHeading{align-items:flex-start;flex-direction:column;gap:5px;margin-bottom:12px}
  .sectionHeading h2{font-size:23px;line-height:1.15}
  .sectionHeading>p{max-width:none;text-align:left;font-size:12px;line-height:1.55}

  .classTabs{overflow-x:auto;overscroll-behavior-inline:contain;scrollbar-width:none;-webkit-overflow-scrolling:touch}
  .classTabs button{flex:0 0 auto;min-width:112px;min-height:44px;padding:10px 13px;font-size:12px}

  .guideSummary{grid-template-columns:1fr;gap:11px;padding:15px 16px}
  .guideSummary>p{border-left:0;border-top:1px solid var(--line);padding:11px 0 0}
  .gearPanel,.priorityPanel{grid-template-columns:1fr}
  .gearIntro,.priorityIntro{padding:18px}
  .gearGrid,.priorityList{grid-template-columns:1fr 1fr}
  .gearItem,.priorityList li{min-width:0;padding:15px}
  .gearItem{border-left:0;border-right:1px solid var(--line)}
  .gearItem:nth-child(2n){border-right:0}
  .gearItem:nth-child(n+3){border-bottom:0}
  .priorityList li{border-left:0;border-right:1px solid var(--line)}
  .priorityList li:nth-child(2n){border-right:0}
  .buildGrid{grid-template-columns:1fr;gap:9px}
  .buildCard{padding:16px}
  .skillGroup b{padding:6px 8px;font-size:10px}

  .calculatorLayout{grid-template-columns:1fr;gap:10px}
  .calcResults{position:static;top:auto;padding:18px}
  .calcPanel{padding:16px}
  .currentLevelsPanel>summary{padding:15px 16px}
  .currentLevelsBody{padding:15px 16px 17px}
  .currentProgressGrid{grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}
  .gearFields{grid-template-columns:repeat(2,minmax(0,1fr))}
  .calcGrid{gap:9px}
  .calcGrid label{font-size:10px;letter-spacing:.045em}
  .calcGrid input,.calcGrid select{min-height:44px;font-size:14px}
  .calcActions button{min-height:44px;padding:10px 14px;font-size:11px}
  .seasonDeadline,.rolloverHold,.resourceGrace{align-items:flex-start;flex-wrap:wrap}
  .seasonDeadline small{margin-left:0;width:100%}
  .resourceGrace small{max-width:none;text-align:left;width:100%}
  .projectionCallout{gap:5px 10px;padding:12px}
  .starTotal{font-size:43px}
  .scoreSummary{margin-bottom:16px}
  .optimizerTargets,.resourceInputs,.resourceUse{grid-template-columns:repeat(2,minmax(0,1fr))}
  .resourceInputsTwo,.resourceInputsFour,.planCosts,.planCostsFour,.rewardTotals{grid-template-columns:repeat(2,minmax(0,1fr))}
  .resourceInputs>div,.planCosts span{min-width:0}
  .planCosts span{font-size:10px;padding:10px}
  .planCosts b{font-size:15px}
  .shortfallPlan{padding:12px}
  .scoreBreakdown div{gap:12px}
  .suggestedGear{display:flex;gap:6px;overflow-x:auto;overscroll-behavior-inline:contain;scrollbar-width:none;padding-bottom:2px}
  .suggestedGear::-webkit-scrollbar{display:none}
  .suggestedGear span{flex:0 0 74px;min-width:74px;font-size:9px}
  .methodPanel{margin-top:10px}

  .timelineNow,.timelineIntelWrap{padding-left:12px;padding-right:12px}
  .timelineNow{margin-top:10px}
  .timelineNowInner{padding:11px 12px}
  .timelineNowHead{align-items:flex-start;gap:8px}
  .timelineNowHead b{font-size:12px}
  .timelineNowHead span{text-align:right;font-size:10px;line-height:1.35}
  .timelineNowGrid{grid-template-columns:1fr}
  .timelineNowCard{padding:10px 11px}
  .timelineNowCard strong{font-size:11px}
  .timelineNowCard small{font-size:10px;line-height:1.5}
  .timelineIntel>summary{align-items:flex-start;gap:10px;padding:13px 14px}
  .timelineIntel>summary span{font-size:12px}
  .timelineIntel>summary small{font-size:10px;line-height:1.4}
  .timelineIntelBody{padding:13px 14px;font-size:11px}
  .recurringGrid,.huntPhases,.timelineIntelBody.eventCycleGrid{grid-template-columns:1fr}
  .huntPhases{padding:0 14px 14px}
  .sourcePills a{min-height:40px;display:inline-flex;align-items:center;padding:7px 10px;font-size:10px}

  .buildCard,.gearItem,.priorityList li,.calcPanel,.calcResults,.timelineNowCard,.eventCycleCard{overflow-wrap:anywhere}
  .buildCard>*,.gearItem>*,.priorityList li>*,.calcPanel>*,.calcResults>*,.timelineNowCard>*,.eventCycleCard>*{min-width:0}
}

@media(max-width:520px){
  .topbar{padding:8px 10px}
  .headerMeta span{display:none}
  .sectionSwitch{margin-left:10px;margin-right:10px}
  .summary{padding:0 10px;gap:7px}
  .builds,.calculator,.timelineNow,.timelineIntelWrap{padding-left:10px;padding-right:10px}
  .summary div{padding:13px}
  .sectionHeading h2{font-size:22px}
  .gearGrid,.priorityList{grid-template-columns:1fr}
  .gearItem,.priorityList li{border-right:0!important;border-bottom:1px solid var(--line)!important}
  .gearItem:last-child,.priorityList li:last-child{border-bottom:0!important}
  .currentProgressGrid,.calcGrid,.gearFields,.optimizerTargets,.resourceInputs,.resourceInputsTwo,.resourceInputsFour,.resourceUse,.planCosts,.planCostsFour,.rewardTotals{grid-template-columns:1fr}
  .scoreSummary{grid-template-columns:repeat(3,minmax(0,1fr));gap:5px}
  .scoreSummary span{font-size:9px}
  .scoreSummary b{font-size:12px}
  .projectionCallout{grid-template-columns:1fr}
  .projectionCallout strong{grid-area:auto;font-size:18px}
  .rolloverHold{align-items:stretch}
  .rolloverHold input[type=number]{width:72px}
  .timelineNowHead,.timelineIntel>summary{flex-direction:column}
  .timelineNowHead span,.timelineIntel>summary small{text-align:left}
}
</style>
'''

if '</head>' not in s:
    raise SystemExit('head close not found')
s = s.replace('</head>', css + '</head>', 1)
p.write_text(s, encoding='utf-8')
print('applied mobile/readability pass v2')
