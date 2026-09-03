from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

marker = 'MOBILE_SUMMARY_ROW_V1'
css = r'''
<style id="mobile-summary-row-v1">
/* MOBILE_SUMMARY_ROW_V1 */
@media(max-width:700px){
  .summary{
    grid-template-columns:repeat(3,minmax(0,1fr))!important;
    gap:8px!important;
  }
  .summary div,
  .summary div:first-child,
  .summary div:last-child{
    min-width:0!important;
    border:1px solid var(--line)!important;
    border-radius:14px!important;
    padding:14px 12px!important;
  }
  .summary span{
    margin-bottom:6px!important;
    font-size:8px!important;
    line-height:1.2!important;
    white-space:nowrap!important;
  }
  .summary .summaryNumber{
    font-size:24px!important;
  }
  .summary strong{
    font-size:12px!important;
    line-height:1.25!important;
    white-space:nowrap!important;
    overflow:hidden!important;
    text-overflow:ellipsis!important;
  }
  .summary .summaryMeta{
    margin-top:5px!important;
    font-size:8px!important;
    line-height:1.25!important;
    white-space:nowrap!important;
    overflow:hidden!important;
    text-overflow:ellipsis!important;
  }
}
</style>
'''

if marker in s:
    print('mobile summary row already installed')
else:
    if '</head>' not in s:
        raise SystemExit('index.html has no </head>')
    s = s.replace('</head>', css + '\n</head>', 1)
    p.write_text(s, encoding='utf-8')
    print('installed mobile summary row')
