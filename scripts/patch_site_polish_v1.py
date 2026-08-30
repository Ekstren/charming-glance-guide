from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
MARK='SITE_POLISH_V1'
if MARK in s:
    print('site polish already applied')
    raise SystemExit(0)

# Readability: remove a few leftover/verbose labels from the regressed Builds template.
repls={
    '<b>Quick stat rule</b>':'<b>Stat priority</b>',
    '<span>Core technique investment</span>':'<span>Technique investment</span>',
    '<span>Core charm investment</span>':'<span>Charm investment</span>',
    '<strong>Only skills equipped below</strong>':'<strong>Only equipped Techniques</strong>',
}
for old,new in repls.items():
    s=s.replace(old,new)

# Efficiency: once the compact per-slot stat panel has been generated, the legacy
# gear panel is dead DOM. Remove it instead of merely hiding it.
s=s.replace("    if(gear) gear.hidden=true;", "    if(gear) gear.remove();", 1)

# Efficiency: minute ticks do not need to do work while the browser tab itself is hidden.
s=s.replace("    setInterval(()=>{\n      renderLocalTimeLabels();", "    setInterval(()=>{\n      if(document.hidden) return;\n      renderLocalTimeLabels();", 1)
s=s.replace("setInterval(()=>{ if(buildsInitialized && buildSeasonKey()!==currentBuildSeason)", "setInterval(()=>{ if(!document.hidden && buildsInitialized && buildSeasonKey()!==currentBuildSeason)", 1)
s=s.replace("    setInterval(()=>{\n      if(!buildsInitialized) return;", "    setInterval(()=>{\n      if(document.hidden||!buildsInitialized) return;", 1)
s=s.replace("    setInterval(()=>{\n      if(!calculatorInitialized) return;", "    setInterval(()=>{\n      if(document.hidden||!calculatorInitialized) return;", 1)

css=r'''
<style id="site-polish-v1">
/* SITE_POLISH_V1
   Conservative consistency/readability pass. No optimizer math changes. */
html{scrollbar-gutter:stable}

/* One predictable focus treatment across navigation, calculator controls and toggles. */
button:focus-visible,input:focus-visible,select:focus-visible,summary:focus-visible,a:focus-visible{
  outline:2px solid var(--green);
  outline-offset:2px;
}

/* Keep the main navigation families visually related. */
.sectionSwitch,.classTabs{border-radius:14px!important;padding:5px!important;gap:6px!important}
.sectionSwitch button,.classTabs button{border-radius:9px!important;line-height:1.2}

/* Builds: readable at normal desktop viewing distance without making the page bulky. */
.guideSummary{padding:17px 18px!important;gap:18px!important}
.guideSummary span,.guideSummary>p b,.buildQuickStats .quickTitle,
.priorityIntro>span,.skillGroup>span,.buildCard .fantomonPair>span{
  font-size:10px!important;
  line-height:1.25;
}
.guideSummary p,.buildQuickStats .quickRule{font-size:11px!important;line-height:1.5!important}
.quickGearGrid{gap:7px 18px!important}
.quickGearRow,.quickSubstats{gap:9px!important;padding-top:7px!important}
.quickGearRow b,.quickSubstats b{font-size:10px!important}
.quickGearRow span,.quickSubstats span{font-size:10px!important;line-height:1.45!important}
.priorityPair{gap:12px!important}
.priorityPair>.priorityPanel{border-radius:15px!important}
.priorityPair .priorityIntro{padding:16px 17px!important}
.priorityPair .priorityIntro>strong{font-size:16px!important;line-height:1.3}
.priorityPair .priorityIntro p{font-size:10.5px!important;line-height:1.5!important}
.priorityPair .priorityList li{padding:13px 15px!important;gap:11px!important}
.priorityPair .priorityList strong{font-size:12px!important}
.priorityPair .priorityList p{font-size:10.5px!important;line-height:1.45!important}
.buildGrid{gap:12px!important}
.buildCard{border-radius:15px!important;padding:17px!important;min-width:0}
.buildCard h3{font-size:15px!important;line-height:1.25}
.buildCard header p,.buildCard ul{font-size:11px!important;line-height:1.55!important}
.skillGroup{margin-top:14px!important}
.skillGroup b{font-size:10px!important;line-height:1.25!important;padding:5px 7px!important}
.buildSource{font-size:10px!important;line-height:1.45}
.buildCard .fantomonPair{margin-top:13px!important;padding-top:12px!important}
.buildCard .fantomonPairNote{font-size:9.5px!important;line-height:1.4!important}
.buildCard .fantomonRankList{gap:8px!important}
.buildCard .fantomonPick{border-radius:10px!important;padding:9px 10px!important}
.buildCard .fantomonPick small{font-size:9px!important}
.buildCard .fantomonPick b{font-size:11px!important}
.buildCard .fantomonPick p{font-size:10px!important;line-height:1.4!important}

/* Dominator role control belongs to the title, not as a visually separate section. */
.dominatorHeadingRow{gap:9px!important;align-items:center!important;flex-wrap:wrap}
.dominatorHeadingRow .dominatorModeTabs{padding:3px!important;gap:3px!important}
.dominatorHeadingRow .dominatorModeTabs button{min-height:30px!important;min-width:52px!important;padding:4px 9px!important;font-size:10px!important}

/* Calculator: several historical 8–9px labels were unnecessarily hard to read. */
#calculatorSection .calcGrid label,
#calculatorSection .autoToggle,
#calculatorSection .calcEyebrow,
#calculatorSection .optimizerNote,
#calculatorSection .scoreSummary span,
#calculatorSection .optimizerSummary,
#calculatorSection .resourceCaption,
#calculatorSection .resourceInputs label,
#calculatorSection .resourceInputs small,
#calculatorSection .resourceUse span,
#calculatorSection .optimizedResult span,
#calculatorSection .seasonDeadline span,
#calculatorSection .seasonDeadline small,
#calculatorSection .projectionCallout span,
#calculatorSection .projectionCallout small,
#calculatorSection .resultDetails>summary,
#calculatorSection .calcActions span,
#calculatorSection .planCosts span,
#calculatorSection .planCosts small{
  font-size:10px!important;
  line-height:1.4;
}
#calculatorSection .resourceInputs strong,
#calculatorSection .resourceUse b,
#calculatorSection .optimizedResult b{font-size:11px!important}
#calculatorSection .calcPanel h3,#calculatorSection .calcResults h3{font-size:14px!important}

/* Medium widths: do not squeeze three dense build cards into unreadable columns. */
@media(max-width:920px){
  .buildGrid{grid-template-columns:repeat(2,minmax(0,1fr))!important}
}

/* Phone/tablet: deterministic grids beat conflicting old flex/overflow rules. */
@media(max-width:620px){
  .sectionSwitch{display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr));margin-left:12px!important;margin-right:12px!important}
  .sectionSwitch button{min-width:0!important;min-height:44px!important;font-size:11px!important;padding:8px!important}
  .classTabs{display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr));overflow:visible!important}
  .classTabs button{min-width:0!important;width:auto!important;min-height:44px!important;font-size:11px!important;padding:9px 7px!important}
  .buildGrid{grid-template-columns:1fr!important}
  .guideSummary{padding:15px!important;gap:12px!important}
  .buildQuickStats{padding-top:12px!important}
  .priorityPair{grid-template-columns:1fr!important;gap:9px!important}
  .buildCard{padding:15px!important}
  .buildCard .fantomonRankList{grid-template-columns:1fr 1fr}
  .dominatorHeadingRow{gap:7px!important}
}
@media(max-width:420px){
  .buildCard .fantomonRankList{grid-template-columns:1fr!important}
  .dominatorHeadingRow .dominatorModeTabs button{min-width:50px!important}
}

@media(prefers-reduced-motion:reduce){
  *,*::before,*::after{scroll-behavior:auto!important;transition-duration:.01ms!important;animation-duration:.01ms!important;animation-iteration-count:1!important}
}
</style>
'''
if '</head>' not in s:
    raise SystemExit('missing </head>')
s=s.replace('</head>',css+'\n</head>',1)
p.write_text(s,encoding='utf-8')
print('applied site consistency, efficiency and readability pass')
