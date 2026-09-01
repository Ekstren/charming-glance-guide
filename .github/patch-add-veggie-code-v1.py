from pathlib import Path

path = Path('index.html')
html = path.read_text(encoding='utf-8')

MARKER = 'TIMELINE_VEGGIE_CODE_V1'
if MARKER in html:
    print('VEGGIE timeline code already applied')
    raise SystemExit(0)

anchor = "  function pacificClockParts(date=new Date()){\n"
if anchor not in html:
    raise SystemExit('Could not find timeline insertion anchor')

patch = r'''  /* TIMELINE_VEGGIE_CODE_V1
     Sep 1, 2026 code reported by GamesRadar; exact expiry time was not published,
     so the timeline uses the reported Sep 8 expiry date conservatively. */
  if(!timelineData.some(e=>e && e[3]==='Gift code · VEGGIE')){
    timelineData.push([
      '2026-09-01',49,'GIFT CODE','Gift code · VEGGIE',
      'New code: VEGGIE gives 10 Rare Auroral Badges + 80 Dawnium. GamesRadar reported it on Sep 1 with a Sep 8 expiration; exact cutoff time was not published, so redeem promptly.',
      'event','2026-09-08'
    ]);
    timelineData.sort((a,b)=>a[0].localeCompare(b[0]) || Number(a[1])-Number(b[1]));
  }

'''
html = html.replace(anchor, patch + anchor, 1)

summary_anchor = "    if(title==='Gift code · Summer') return 'UNCONFIRMED cutoff: Summer gives 160 Dawnium and is reported valid through Sep 1; redeem promptly.';\n"
if summary_anchor in html:
    html = html.replace(summary_anchor, summary_anchor + "    if(title==='Gift code · VEGGIE') return 'VEGGIE: 10 Rare Auroral Badges + 80 Dawnium. Reported Sep 1 with a Sep 8 expiry; redeem promptly.';\n", 1)

path.write_text(html, encoding='utf-8')
print('Added VEGGIE gift-code timeline event')
