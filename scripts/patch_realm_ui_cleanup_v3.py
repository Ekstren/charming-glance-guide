from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')
marker = 'REALM_UI_CLEANUP_V3'
if marker in s:
    print('Realm UI cleanup already applied')
    raise SystemExit(0)

# Cleaner inventory wording.
s = s.replace('Hammers on hand', 'Hammers owned')
s = s.replace('Knuckles on hand', 'Knuckles owned')
s = s.replace('Shovels on hand', 'Shovels owned')

# The section already establishes that these are Material Realm purchases.
s = s.replace('Ore Realm Purchases / Day', 'Ore Purchases / Day')
s = s.replace('Essence Realm Purchases / Day', 'Essence Purchases / Day')
s = s.replace('Sand Realm Purchases / Day', 'Sand Purchases / Day')

css = r'''
<style id="realm-ui-cleanup-v3">
/* REALM_UI_CLEANUP_V3
   Final consistency repair for Realm/result cards and Daily Shop sizing. */

/* Result resource rows should visually read as one joined inset card. The parent
   result tile uses a 6px grid gap, so cancel that gap only between the two halves. */
.planCosts small.rawRemaining:has(+ small.toolBalance:not([hidden])){
  min-height:34px!important;
  margin-top:5px!important;
  padding:8px 10px!important;
  border:1px solid var(--line)!important;
  border-bottom:0!important;
  border-radius:10px 10px 0 0!important;
  background:var(--input-bg,var(--surface))!important;
}
.planCosts small.rawRemaining + small.toolBalance:not([hidden]){
  min-height:34px!important;
  margin-top:-6px!important;
  margin-bottom:0!important;
  padding:8px 10px!important;
  border:1px solid var(--line)!important;
  border-radius:0 0 10px 10px!important;
  background:var(--input-bg,var(--surface))!important;
}
.planCosts small.rawRemaining:not(:has(+ small.toolBalance:not([hidden]))){
  min-height:34px!important;
  margin-top:5px!important;
  padding:8px 10px!important;
  border:1px solid var(--line)!important;
  border-radius:10px!important;
  background:var(--input-bg,var(--surface))!important;
  align-content:center!important;
}
.planCosts .resourceRemainingLine,
.planCosts small.toolBalance .toolSimpleLine{
  font-size:9px!important;
  line-height:1.35!important;
}
.planCosts .resourceRemainingLine{
  display:grid!important;
  grid-template-columns:auto minmax(0,1fr)!important;
  gap:6px!important;
  align-items:baseline!important;
  font-weight:700!important;
  white-space:nowrap!important;
}
.planCosts .resourceRemainingLine b,
.planCosts small.toolBalance .toolSimpleLine b{
  font-size:inherit!important;
  line-height:inherit!important;
  font-weight:850!important;
}
.planCosts small.toolBalance .toolSimpleLine i{
  font-weight:700!important;
}

/* Daily Shop: make the restock control exactly one of the same three equal
   columns used by the Realm purchase controls; gains span the other two. */
.shopEstimateCompact{
  display:grid!important;
  grid-template-columns:repeat(3,minmax(0,1fr))!important;
  gap:9px!important;
  align-items:stretch!important;
  padding:0!important;
}
.shopRefreshControl{
  grid-column:1!important;
  min-width:0!important;
}
.shopGainSummary{
  grid-column:2 / 4!important;
  min-width:0!important;
}
.shopRefreshControl input{
  width:100%!important;
  box-sizing:border-box!important;
}

@media(max-width:700px){
  .shopEstimateCompact{grid-template-columns:1fr!important}
  .shopRefreshControl,.shopGainSummary{grid-column:1!important}
  .planCosts .resourceRemainingLine{white-space:normal!important}
  .planCosts small.rawRemaining + small.toolBalance:not([hidden]){margin-top:-6px!important}
}
</style>
'''

needle = '</head>'
if needle not in s:
    raise SystemExit('head close not found')
s = s.replace(needle, css + '\n' + needle, 1)
p.write_text(s, encoding='utf-8')
print('Applied Realm UI cleanup v3')
