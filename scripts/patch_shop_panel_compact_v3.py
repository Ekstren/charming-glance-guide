from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

marker = 'DAILY_SHOP_LAYOUT_MATCH_REALM_V8'
if marker in s:
    print('Daily Shop realm-match polish already applied')
    raise SystemExit(0)

css = r'''
/* DAILY_SHOP_LAYOUT_MATCH_REALM_V8
   Match the Material Realm visual language: rounded inset inputs, soft nested cards,
   and no sharp table-like separators inside the gain summary. */
.shopEstimateCompact{
  grid-template-columns:minmax(210px,.72fr) minmax(320px,1.28fr)!important;
  gap:10px!important;
  align-items:stretch!important;
}
.shopRefreshControl,.shopGainSummary{
  border:1px solid var(--line)!important;
  border-radius:11px!important;
  background:var(--surface)!important;
  padding:12px 13px!important;
}
.shopRefreshControl label{
  display:flex!important;
  flex-direction:column!important;
  gap:6px!important;
}
.shopRefreshControl input{
  display:block!important;
  width:100%!important;
  height:46px!important;
  min-height:46px!important;
  margin:0!important;
  padding:9px 11px!important;
  border:1px solid var(--line)!important;
  border-radius:10px!important;
  background:var(--input-bg)!important;
  color:var(--ink)!important;
  font-size:14px!important;
  font-weight:850!important;
  box-sizing:border-box!important;
}
.shopRefreshControl input:focus{
  outline:none!important;
  border-color:var(--green)!important;
  box-shadow:0 0 0 3px color-mix(in srgb,var(--green) 15%,transparent)!important;
}
.shopRefreshControl small{
  margin-top:0!important;
  color:var(--secondary-text)!important;
  font-size:9px!important;
}
.shopGainSummary{
  display:grid!important;
  grid-template-columns:1fr!important;
  gap:5px!important;
}
.shopGainSummary>div{
  display:flex!important;
  align-items:center!important;
  justify-content:space-between!important;
  gap:16px!important;
  min-height:32px!important;
  padding:3px 0!important;
  border:0!important;
  border-radius:0!important;
  background:transparent!important;
}
.shopGainSummary span{font-size:10px!important;color:var(--body-text)!important;font-weight:700!important}
.shopGainSummary b{font-size:11px!important;color:var(--status-positive)!important;font-weight:850!important;font-variant-numeric:tabular-nums!important}
.shopEstimateNote{padding-top:7px!important}
@media(max-width:700px){
  .shopEstimateCompact{grid-template-columns:1fr!important}
  .shopRefreshControl,.shopGainSummary{padding:12px!important}
}
'''

idx = s.rfind('</style>')
if idx < 0:
    raise SystemExit('final style close not found')
s = s[:idx] + css + '\n' + s[idx:]
p.write_text(s, encoding='utf-8')
print('Applied Daily Shop realm-match polish V8')
