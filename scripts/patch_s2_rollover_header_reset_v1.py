from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
mark='S2_ROLLOVER_HEADER_RESET_V1'
if mark in s:
    print('S2 rollover header reset already installed')
    raise SystemExit(0)

old_html='<div class="calcSeasonNotice" id="calcSeasonNotice" hidden><div><strong id="calcSeasonNoticeTitle">Season rollover</strong><p id="calcSeasonNoticeText">—</p></div><button id="confirmSeasonSnapshot" type="button">Use entries as new snapshot</button></div>'
new_html='<div class="calcSeasonNotice" id="calcSeasonNotice" hidden><div><strong id="calcSeasonNoticeTitle">Season rollover</strong><p id="calcSeasonNoticeText">—</p></div><div class="calcSeasonNoticeActions"><button id="confirmSeasonSnapshot" type="button">Use entries as new snapshot</button><button id="resetSeasonSnapshot" type="button" class="calcSeasonReset">Reset calculator</button></div></div>'
if old_html not in s:
    raise SystemExit('calcSeasonNotice HTML anchor not found')
s=s.replace(old_html,new_html,1)

old_css='.calcSeasonNotice button{border:1px solid var(--gold);background:var(--surface);color:var(--ink);border-radius:9px;padding:8px 11px;font-size:9px;font-weight:850;cursor:pointer;white-space:nowrap}.calcSeasonNotice button:hover{background:var(--gold);color:#151515}'
new_css='.calcSeasonNoticeActions{display:flex;align-items:center;gap:8px;flex:0 0 auto}.calcSeasonNotice button{border:1px solid var(--gold);background:var(--surface);color:var(--ink);border-radius:9px;padding:8px 11px;font-size:9px;font-weight:850;cursor:pointer;white-space:nowrap}.calcSeasonNotice button:hover{background:var(--gold);color:#151515}.calcSeasonNotice .calcSeasonReset{border-color:var(--line);color:var(--secondary-text)}.calcSeasonNotice .calcSeasonReset:hover{border-color:var(--gold);background:color-mix(in srgb,var(--gold) 12%,var(--surface));color:var(--ink)}@media(max-width:620px){.calcSeasonNotice{align-items:stretch;flex-direction:column}.calcSeasonNoticeActions{width:100%;display:grid;grid-template-columns:1fr 1fr}.calcSeasonNoticeActions button{width:100%;white-space:normal}}'
if old_css not in s:
    raise SystemExit('calcSeasonNotice CSS anchor not found')
s=s.replace(old_css,new_css,1)

old_handler="$('confirmSeasonSnapshot')?.addEventListener('click',()=>{resetMaxAchievableUi();confirmCurrentSeasonSnapshot();});"
new_handler="/* S2_ROLLOVER_HEADER_RESET_V1 */\n    $('confirmSeasonSnapshot')?.addEventListener('click',()=>{resetMaxAchievableUi();confirmCurrentSeasonSnapshot();});\n    $('resetSeasonSnapshot')?.addEventListener('click',()=>{resetMaxAchievableUi();resetCalculator();});"
if old_handler not in s:
    raise SystemExit('confirmSeasonSnapshot handler anchor not found')
s=s.replace(old_handler,new_handler,1)

p.write_text(s,encoding='utf-8')
print('Added Reset calculator beside the season snapshot import/confirm action')
