from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')
marker = '/* MOBILE_TIMELINE_LAYOUT_V1 */'

if marker in s:
    print('mobile timeline layout v1 already applied')
    raise SystemExit(0)

css = r'''

/* MOBILE_TIMELINE_LAYOUT_V1 */
@media (max-width:720px){
  html,body{max-width:100%;overflow-x:hidden}

  .topbar{
    align-items:center;
    gap:14px;
    min-height:72px;
    padding:10px 16px;
  }
  .logoButton{min-width:0;flex:1}
  .logoButton>span:last-child{min-width:0}
  .logoButton strong{font-size:15px;line-height:1.2}
  .logoButton small{font-size:10px;line-height:1.35}
  .themeToggle{flex:0 0 auto}

  .sectionSwitch{
    display:grid;
    grid-template-columns:repeat(2,minmax(0,1fr));
    width:auto;
    max-width:none;
    height:auto;
    margin:12px 16px 0;
    padding:6px;
    gap:6px;
    position:relative;
  }
  .sectionSwitch button{
    width:100%;
    min-width:0;
    min-height:42px;
    padding:8px 6px;
    line-height:1.2;
    white-space:normal;
  }

  .summary{
    display:grid;
    grid-template-columns:1fr;
    gap:10px;
    width:auto;
    max-width:none;
    margin:16px 16px 0;
    padding:0;
  }
  .summary div,
  .summary div:first-child,
  .summary div:nth-child(2),
  .summary div:last-child{
    grid-column:auto;
    margin:0;
    border:1px solid var(--line);
    border-radius:14px;
    padding:17px 18px;
  }
  .summary span{margin-bottom:6px}

  .timelineNow,
  .timelineIntelWrap,
  .timeline,
  .controls{
    width:100%;
    max-width:none;
    padding-left:16px;
    padding-right:16px;
  }
  .timelineNow{margin-top:14px}
  .timelineIntelWrap{margin-top:12px}
  .timelineNowHead{
    align-items:flex-start;
    flex-direction:column;
    gap:4px;
  }
  .timelineNowHead span{text-align:left;line-height:1.4}
  .timelineNowGrid{grid-template-columns:1fr}
  .timelineNowCard{min-width:0;overflow-wrap:anywhere}
  .timelineIntel>summary{padding:13px 14px}
  .timelineIntelBody{padding:13px 14px}

  .controls{
    flex-direction:column;
    align-items:stretch;
    gap:10px;
    margin:18px 0 26px;
  }
  .filters{
    display:grid;
    grid-template-columns:repeat(2,minmax(0,1fr));
    width:100%;
    min-width:0;
    gap:7px;
  }
  .filters button{
    width:100%;
    min-width:0;
    padding:9px 8px;
    line-height:1.2;
    white-space:normal;
    text-align:center;
  }
  .pastToggle{width:100%;padding:2px 2px 0}

  .timeline{padding-bottom:calc(88px + env(safe-area-inset-bottom))}
  .dayGroup{min-width:0}
  .entryStack,.entry{min-width:0}
  .entry p{overflow-wrap:anywhere}

  .todayButton{
    right:14px;
    bottom:calc(12px + env(safe-area-inset-bottom));
    max-width:calc(100vw - 28px);
    min-height:42px;
    padding:10px 14px;
    font-size:0;
    line-height:1;
  }
  .todayButton::after{content:'Current';font-size:11px;font-weight:850}
}

@media (max-width:430px){
  .topbar{padding-left:14px;padding-right:14px}
  .sectionSwitch{margin-left:14px;margin-right:14px}
  .summary{margin-left:14px;margin-right:14px}
  .timelineNow,.timelineIntelWrap,.timeline,.controls{padding-left:14px;padding-right:14px}
  .huntPhases,.futureSeasonGrid{grid-template-columns:1fr}
}
'''

anchor = '</style>'
if anchor not in s:
    raise SystemExit('style closing tag not found')

s = s.replace(anchor, css + '\n' + anchor, 1)
p.write_text(s, encoding='utf-8')
print('applied mobile timeline layout v1')
