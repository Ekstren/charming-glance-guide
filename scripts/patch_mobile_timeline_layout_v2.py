from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')
marker_v1 = '/* MOBILE_TIMELINE_LAYOUT_V1 */'
marker_v2 = 'MOBILE_TIMELINE_LAYOUT_FINAL_V2'

# Remove the first pass, which landed before later mobile CSS and could be overridden.
if marker_v1 in s:
    start = s.index(marker_v1)
    end = s.find('</style>', start)
    if end == -1:
        raise SystemExit('could not find closing style tag after v1 marker')
    s = s[:start] + s[end:]

if marker_v2 in s:
    print('mobile timeline layout v2 already applied')
    p.write_text(s, encoding='utf-8')
    raise SystemExit(0)

css = r'''
<style id="mobile-timeline-layout-final-v2">
/* MOBILE_TIMELINE_LAYOUT_FINAL_V2
   Final mobile cascade pass: keep navigation in flow, remove horizontal overflow,
   make filters fit the viewport, and keep the floating current button out of the way. */
@media (max-width:720px){
  html,body{max-width:100%;overflow-x:hidden!important}

  /* A two-row sticky section nav consumed too much of the phone viewport and could
     visually sit on top of the summary. Keep only the top bar sticky on phones. */
  .sectionSwitch{
    position:relative!important;
    top:auto!important;
    z-index:auto!important;
    display:grid!important;
    grid-template-columns:repeat(2,minmax(0,1fr))!important;
    width:auto!important;
    max-width:none!important;
    height:auto!important;
    margin:10px 12px 0!important;
    padding:5px!important;
    gap:5px!important;
  }
  .sectionSwitch button{
    width:100%!important;
    min-width:0!important;
    min-height:44px!important;
    padding:8px 6px!important;
    line-height:1.15!important;
    white-space:normal!important;
  }

  /* Summary cards should be clean standalone cards on a phone, not desktop cells. */
  .summary{
    display:grid!important;
    grid-template-columns:1fr!important;
    gap:9px!important;
    width:auto!important;
    max-width:none!important;
    margin:14px 12px 0!important;
    padding:0!important;
  }
  .summary div,
  .summary div:first-child,
  .summary div:nth-child(2),
  .summary div:last-child{
    grid-column:auto!important;
    margin:0!important;
    border:1px solid var(--line)!important;
    border-radius:14px!important;
    padding:15px 16px!important;
  }

  .timelineNow,.timelineIntelWrap,.timeline,.controls{
    width:100%!important;
    max-width:none!important;
    padding-left:12px!important;
    padding-right:12px!important;
  }
  .timelineNow{margin-top:12px!important}
  .timelineIntelWrap{margin-top:12px!important}
  .timelineNowHead{align-items:flex-start!important;flex-direction:column!important;gap:4px!important}
  .timelineNowHead span{text-align:left!important;line-height:1.4!important}
  .timelineNowGrid{grid-template-columns:1fr!important}
  .timelineNowCard{min-width:0!important;overflow-wrap:anywhere}
  .timelineNowCard .activePill{display:inline-flex!important;margin-left:6px!important}

  /* The old flex row used intrinsic button widths and could extend off-screen. */
  .controls{
    flex-direction:column!important;
    align-items:stretch!important;
    gap:10px!important;
    margin:18px 0 26px!important;
  }
  .filters{
    display:grid!important;
    grid-template-columns:repeat(3,minmax(0,1fr))!important;
    width:100%!important;
    max-width:100%!important;
    min-width:0!important;
    gap:7px!important;
  }
  .filters button{
    width:100%!important;
    min-width:0!important;
    padding:9px 6px!important;
    line-height:1.2!important;
    white-space:normal!important;
    text-align:center!important;
  }
  .pastToggle{width:100%!important;padding:2px 2px 0!important}

  .timeline{padding-bottom:calc(82px + env(safe-area-inset-bottom))!important}
  .dayGroup,.entryStack,.entry{min-width:0!important}
  .entry p{overflow-wrap:anywhere}

  /* Keep the shortcut, but make it a compact phone control instead of a large
     pill that covers the filter row/content. The original text remains in the DOM. */
  .todayButton{
    right:12px!important;
    bottom:calc(10px + env(safe-area-inset-bottom))!important;
    min-height:40px!important;
    max-width:calc(100vw - 24px)!important;
    padding:9px 13px!important;
    font-size:0!important;
    line-height:1!important;
  }
  .todayButton::after{content:'Current';font-size:11px;font-weight:850}
}

@media (max-width:520px){
  .filters{grid-template-columns:repeat(2,minmax(0,1fr))!important}
}

@media (max-width:380px){
  .sectionSwitch{margin-left:8px!important;margin-right:8px!important}
  .summary{margin-left:8px!important;margin-right:8px!important}
  .timelineNow,.timelineIntelWrap,.timeline,.controls{padding-left:8px!important;padding-right:8px!important}
}
</style>
'''

anchor = '</head>'
if anchor not in s:
    raise SystemExit('head closing tag not found')
s = s.replace(anchor, css + '\n' + anchor, 1)
p.write_text(s, encoding='utf-8')
print('applied final mobile timeline layout v2')
