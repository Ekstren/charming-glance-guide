from pathlib import Path
import re

p = Path('index.html')
text = p.read_text(encoding='utf-8')

start = '<!-- SITE_LAYOUT_MOBILE_START -->'
end = '<!-- SITE_LAYOUT_MOBILE_END -->'
block = r'''<!-- SITE_LAYOUT_MOBILE_START -->
<style id="site-layout-mobile-v1">
/* Keep Builds, Companions and Calculator on the same content rails. */
.calculator{max-width:980px;margin:32px auto 80px;padding:0 20px}

/* Keep the S1/S2 selector visually inside the Builds navigation button. */
.buildsNavCell{position:relative;flex:1;min-width:0}
.buildsNavCell>button[data-section="builds"]{width:100%;padding-right:94px}
.buildSeasonToggle{
  position:absolute;
  z-index:3;
  top:50%;
  right:7px;
  transform:translateY(-50%);
  display:grid;
  grid-template-columns:1fr 1fr;
  gap:2px;
  padding:3px;
  border:1px solid color-mix(in srgb,var(--line) 78%,transparent);
  border-radius:9px;
  background:color-mix(in srgb,var(--bg) 72%,transparent);
  box-shadow:0 1px 4px #00000012;
}
.buildSeasonToggle button{
  flex:0 0 auto!important;
  min-width:31px!important;
  min-height:30px!important;
  padding:5px 7px!important;
  border:0!important;
  border-radius:7px!important;
  background:transparent!important;
  color:var(--muted)!important;
  font-size:8px!important;
  line-height:1!important;
  font-weight:900!important;
  box-shadow:none!important;
}
.buildSeasonToggle button[aria-pressed="true"],
.buildSeasonToggle button.active{
  background:var(--accent-strong)!important;
  color:#fff!important;
}
.buildsNavCell>button[data-section="builds"].active + .buildSeasonToggle{
  border-color:color-mix(in srgb,#fff 22%,transparent);
  background:color-mix(in srgb,var(--accent-deep) 54%,transparent);
}
.buildsNavCell>button[data-section="builds"].active + .buildSeasonToggle button{
  color:color-mix(in srgb,#fff 70%,transparent)!important;
}
.buildsNavCell>button[data-section="builds"].active + .buildSeasonToggle button[aria-pressed="true"],
.buildsNavCell>button[data-section="builds"].active + .buildSeasonToggle button.active{
  background:color-mix(in srgb,#fff 24%,transparent)!important;
  color:#fff!important;
}

@media (min-width:1400px){
  .calculator{max-width:1560px;margin-top:38px;padding:0 28px}
  .calculator .methodPanel,
  .calculator .calcSeasonNotice{max-width:none}
  .buildsNavCell>button[data-section="builds"]{padding-right:104px}
  .buildSeasonToggle{right:9px}
  .buildSeasonToggle button{min-width:34px!important;min-height:32px!important;font-size:9px!important}
}

/* Tablet: stop desktop grids from becoming narrow mini-columns. */
@media (max-width:900px){
  .calculatorLayout{grid-template-columns:1fr}
  .calcResults{position:static;top:auto}
  .buildGrid{grid-template-columns:repeat(2,minmax(0,1fr))}
  .priorityPair{grid-template-columns:1fr}
  .companionHero,.companionGrid{grid-template-columns:1fr}
  .companionFocus{border-left:0;border-top:1px solid var(--line)}
}

/* Phone layout shared across the main sections. */
@media (max-width:720px){
  html{scroll-padding-top:68px}
  body{overflow-x:hidden}

  .topbar{min-height:64px;padding:9px 12px;align-items:center;gap:10px}
  .logoButton{gap:9px;min-width:0}
  .logo{width:38px;height:38px;border-radius:11px;font-size:13px;flex:0 0 38px}
  .logoButton strong{font-size:14px;line-height:1.2}
  .logoButton small{display:block;max-width:190px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-size:9px}
  .headerTools{margin-left:auto;flex:0 0 auto}
  .headerMeta{display:none}
  .themeToggle{width:36px;height:36px;flex:0 0 36px}

  .sectionSwitch{display:grid;grid-template-columns:1fr 1fr;gap:4px;margin:12px 10px 0;padding:4px;border-radius:13px}
  .sectionSwitch>button,.sectionSwitch>.buildsNavCell{min-width:0}
  .sectionSwitch>button{min-height:42px;padding:7px 6px;font-size:10px}
  .buildsNavCell{display:block;position:relative}
  .buildsNavCell>button[data-section]{width:100%;min-height:42px;padding:7px 70px 7px 8px;font-size:10px}
  .buildSeasonToggle{right:4px;padding:2px;gap:1px;border-radius:8px}
  .buildSeasonToggle button{min-width:27px!important;min-height:32px!important;padding:4px!important;font-size:8px!important}

  .builds,.companions,.calculator{width:100%;max-width:none;margin:16px auto 60px;padding:0 10px}
  .classTabs,.companionClassTabs{display:grid;grid-template-columns:1fr 1fr;gap:4px;padding:4px;margin-bottom:8px}
  .classTabs button{min-height:42px;padding:9px 6px;font-size:10px}

  .guideSummary{padding:14px;gap:12px}
  .guideSummary.buildSummaryCompact{grid-template-columns:1fr}
  .buildQuickStats{border-left:0;border-top:1px solid var(--line);padding:12px 0 0}
  .quickGearGrid{grid-template-columns:1fr}
  .buildGrid{grid-template-columns:1fr;gap:8px}
  .buildCard{padding:14px}
  .priorityPair{gap:8px}

  .companionHeroMain,.companionFocus{padding:15px}
  .companionHeroMain h2{font-size:20px}
  .companionHeroMain p{font-size:10px}
  .companionFocus strong{font-size:16px}
  .companionGrid{gap:8px}
  .companionPanel{padding:14px}
  .companionLadder{grid-template-columns:1fr 1fr;gap:6px}
  .companionTitleRow{align-items:flex-start;flex-wrap:wrap;gap:8px}
  .companionTitleRow .companionRoleToggle{width:100%;display:grid;grid-template-columns:1fr 1fr;margin-top:2px}
  .companionRoleToggle button{min-height:38px}
  .companionSources{text-align:left}

  .calculatorLayout{display:grid;grid-template-columns:1fr;gap:10px}
  .calcInputs,.calcResults{min-width:0;width:100%}
  .calcPanel{padding:15px}
  .calcResults{position:static;top:auto;padding:16px}
  .currentLevelsBody{padding:14px 15px 16px}
  .currentLevelsPanel>summary{padding:14px 15px}
  .calcGrid,.gearFields,.currentProgressGrid{grid-template-columns:1fr 1fr;gap:8px}
  .calcGrid input,.calcGrid select,.resourceInputs input,.realmInventoryGrid input,.realmDailyInputs input,.accuracyGrid input,.exactInputsBody input{font-size:16px}
  .resourceInputs,.resourceInputsTwo,.resourceInputsFour,.resourceUse,.planCosts,.planCostsFour{grid-template-columns:1fr 1fr;gap:7px}
  .accuracyGrid,.exactProgressGrid{grid-template-columns:1fr 1fr}
  .realmInventoryGrid,.realmDailyInputs{grid-template-columns:1fr 1fr}
  .realmDailyPlanRow{grid-template-columns:1fr}
  .staminaSimple{flex-direction:column;align-items:stretch}
  .staminaControl{width:100%;min-width:0;align-items:stretch}
  .staminaSimple select{width:100%;min-width:0;font-size:16px}
  .staminaCurrentPlan{max-width:none;text-align:left}
  .seasonDeadline,.rolloverHold{flex-wrap:wrap;align-items:flex-start}
  .seasonDeadline small{width:100%;margin-left:0}
  .calcActions{flex-direction:column;align-items:stretch}
  .calcActions button{width:100%;min-height:44px}
  .methodPanel{max-width:none}
  .resultScoreLine>span{flex-wrap:wrap}
  .starTotal{font-size:42px}
  .suggestedGear{grid-template-columns:repeat(3,minmax(0,1fr))}
}

@media (max-width:480px){
  .logoButton small{max-width:145px}
  .calcGrid,.gearFields,.currentProgressGrid,.accuracyGrid,.exactProgressGrid{grid-template-columns:1fr}
  .resourceInputs,.resourceInputsTwo,.resourceInputsFour,.resourceUse,.planCosts,.planCostsFour{grid-template-columns:1fr}
  .realmInventoryGrid,.realmDailyInputs{grid-template-columns:1fr}
  .scoreSummary,.optimizerTargets{grid-template-columns:1fr 1fr}
  .companionLadder{grid-template-columns:1fr}
  .suggestedGear{grid-template-columns:1fr 1fr}
  .resultHeadline{gap:2px}
  .starTotal{font-size:38px}
}
</style>
<!-- SITE_LAYOUT_MOBILE_END -->'''

# Idempotent replacement when this patch runs again.
pat = re.compile(re.escape(start) + r'.*?' + re.escape(end), re.S)
if pat.search(text):
    text = pat.sub(block, text, count=1)
else:
    if '</head>' not in text:
        raise SystemExit('Missing </head> insertion point')
    text = text.replace('</head>', block + '\n</head>', 1)

p.write_text(text, encoding='utf-8')
print('Applied shared section width, integrated build season control, and mobile layout polish')
