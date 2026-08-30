from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

marker = 'DAILY_SHOP_LAYOUT_POLISH_V7'
if marker in s:
    print('Daily Shop layout polish already applied')
    raise SystemExit(0)

css = r'''
/* DAILY_SHOP_LAYOUT_POLISH_V7 */
.shopEstimatePanel{margin-top:14px;overflow:hidden}
.shopEstimatePanel .realmInventoryTop{align-items:center;padding-bottom:10px;border-bottom:1px solid var(--line)}
.shopEstimatePanel .realmInventoryTop small{font-size:9px;line-height:1.25;text-align:right}
.shopEstimateCompact{display:grid;grid-template-columns:minmax(190px,.66fr) minmax(300px,1.34fr);gap:12px;align-items:stretch;padding:12px 0 0}
.shopRefreshControl,.shopGainSummary{border:1px solid var(--line);border-radius:11px;background:var(--surface);padding:12px 13px}
.shopRefreshControl{display:flex;align-items:stretch}
.shopRefreshControl label{display:flex;flex-direction:column;justify-content:flex-start;gap:7px;width:100%;font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.04em}
.shopRefreshControl input{width:100%;min-height:42px;margin:0}
.shopRefreshControl small{font-size:9px;font-weight:650;text-transform:none;letter-spacing:0;color:var(--status-info)}
.shopGainSummary{display:grid;grid-template-columns:1fr;gap:0;border-left:1px solid var(--line)}
.shopGainSummary>div{display:flex;align-items:center;justify-content:space-between;gap:16px;min-height:31px;padding:5px 1px;border-bottom:1px solid color-mix(in srgb,var(--line) 65%,transparent)}
.shopGainSummary>div:last-child{border-bottom:0}
.shopGainSummary span{font-size:10px;color:var(--body-text);font-weight:700}
.shopGainSummary b{font-size:11px;color:var(--status-positive);white-space:nowrap;font-variant-numeric:tabular-nums}
.shopEstimateNote{display:block;padding:8px 1px 0;margin:0;color:var(--muted);font-size:8px;line-height:1.35}
@media(max-width:700px){
  .shopEstimatePanel .realmInventoryTop{align-items:flex-start}
  .shopEstimatePanel .realmInventoryTop small{text-align:left}
  .shopEstimateCompact{grid-template-columns:1fr}
  .shopRefreshControl,.shopGainSummary{padding:12px}
}
'''

idx = s.rfind('</style>')
if idx < 0:
    raise SystemExit('final style close not found')
s = s[:idx] + css + '\n' + s[idx:]
p.write_text(s, encoding='utf-8')
print('Applied Daily Shop layout polish V7')
