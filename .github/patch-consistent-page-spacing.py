from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')
marker = 'CONSISTENT_PAGE_SPACING_V1'
if marker in s:
    print('already applied')
    raise SystemExit(0)

css = r'''
<style id="consistent-page-spacing-v1">
/* CONSISTENT_PAGE_SPACING_V1
   Shared vertical rhythm for main navigation, sub-tabs, and top-level page content. */
:root{
  --page-stack-gap:12px;
  --page-stack-gap-mobile:10px;
}

/* Every page starts the same distance below the main selector. */
.siteSection{
  margin-top:var(--page-stack-gap)!important;
  padding-top:0!important;
}
.siteSection > :first-child{
  margin-top:0!important;
}

/* Builds + Companions: identical sub-tab -> content spacing. */
#buildsSection > .classTabs,
#companionsSection > .companionClassTabs{
  margin-top:0!important;
  margin-bottom:var(--page-stack-gap)!important;
}

/* Use one rhythm between the major generated blocks instead of a mix of 10/12/14px margins. */
#buildContent,
#companionContent{
  display:grid!important;
  gap:var(--page-stack-gap)!important;
}
#buildContent > *,
#companionContent > *{
  margin-top:0!important;
  margin-bottom:0!important;
}

/* Calculator follows the same 12px stack rhythm. */
#calculatorSection .calculatorLayout{
  gap:var(--page-stack-gap)!important;
}
#calculatorSection .calcInputs{
  gap:var(--page-stack-gap)!important;
}

/* Timeline's first summary and the next overview block follow the same cadence. */
#timelineSection > .summary{
  margin-top:0!important;
}
#timelineSection > .timelineNow{
  margin-top:var(--page-stack-gap)!important;
}
#timelineSection > .timelineIntelWrap{
  margin-top:var(--page-stack-gap)!important;
}

@media(max-width:720px){
  .siteSection{margin-top:var(--page-stack-gap-mobile)!important}
  #buildsSection > .classTabs,
  #companionsSection > .companionClassTabs{margin-bottom:var(--page-stack-gap-mobile)!important}
  #buildContent,#companionContent{gap:var(--page-stack-gap-mobile)!important}
  #calculatorSection .calculatorLayout,
  #calculatorSection .calcInputs{gap:var(--page-stack-gap-mobile)!important}
  #timelineSection > .timelineNow,
  #timelineSection > .timelineIntelWrap{margin-top:var(--page-stack-gap-mobile)!important}
}
</style>
'''

if '</head>' not in s:
    raise SystemExit('head close not found')
s = s.replace('</head>', css + '</head>', 1)
p.write_text(s, encoding='utf-8')
print('normalized main page spacing')
