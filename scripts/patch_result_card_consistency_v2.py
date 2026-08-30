from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')
marker = 'RESULT_CARD_CONSISTENCY_V2'
if marker in s:
    print('Result-card consistency patch already applied')
    raise SystemExit(0)

css = r'''
<style id="result-card-consistency-v2">
/* RESULT_CARD_CONSISTENCY_V2
   Recommended gear is informational, not a success state. Keep it neutral.
   Result resource rows use the same label/value weight and spacing rhythm. */

/* Recommended gear: neutral tiles, same family as the other recommendation cards. */
.suggestedGear span{
  background:var(--ui-subpanel,var(--bg))!important;
  border:1px solid var(--line)!important;
  color:var(--muted)!important;
  box-shadow:none!important;
}
.suggestedGear b{
  color:var(--ink)!important;
  font-weight:850!important;
}

/* Result resource inset rows: one consistent row system. */
.planCosts small.rawRemaining,
.planCosts small.toolBalance:not([hidden]){
  box-sizing:border-box!important;
  background:var(--input-bg,var(--surface))!important;
  border-color:var(--line)!important;
  font-size:9px!important;
  line-height:1.35!important;
}

.planCosts small.rawRemaining:has(+ small.toolBalance:not([hidden])){
  min-height:34px!important;
  margin-top:5px!important;
  padding:8px 10px!important;
  border:1px solid var(--line)!important;
  border-bottom:0!important;
  border-radius:10px 10px 0 0!important;
}
.planCosts small.rawRemaining + small.toolBalance:not([hidden]){
  min-height:34px!important;
  margin:0!important;
  padding:8px 10px!important;
  border:1px solid var(--line)!important;
  border-radius:0 0 10px 10px!important;
}
.planCosts small.rawRemaining:not(:has(+ small.toolBalance:not([hidden]))){
  min-height:34px!important;
  margin-top:5px!important;
  padding:8px 10px!important;
  border:1px solid var(--line)!important;
  border-radius:10px!important;
  align-content:center!important;
}

/* Matching typography: labels normal/medium, values bold. */
.planCosts .resourceRemainingLine{
  display:grid!important;
  grid-template-columns:auto minmax(0,1fr)!important;
  align-items:baseline!important;
  gap:6px!important;
  margin:0!important;
  color:var(--status-positive,var(--green))!important;
  font-size:9px!important;
  font-weight:700!important;
  line-height:1.35!important;
}
.planCosts .resourceRemainingLine b{
  margin:0!important;
  color:inherit!important;
  font-size:inherit!important;
  font-weight:850!important;
  line-height:inherit!important;
}
.planCosts small.toolBalance .toolSimpleLine{
  grid-template-columns:auto minmax(0,1fr)!important;
  gap:6px!important;
  align-items:baseline!important;
  margin:0!important;
  min-height:0!important;
  font-size:9px!important;
  line-height:1.35!important;
}
.planCosts small.toolBalance .toolSimpleLine i{
  font-weight:700!important;
}
.planCosts small.toolBalance .toolSimpleLine b{
  font-size:inherit!important;
  font-weight:850!important;
  line-height:inherit!important;
}

@media(max-width:720px){
  .planCosts small.rawRemaining,
  .planCosts small.toolBalance:not([hidden]),
  .planCosts .resourceRemainingLine,
  .planCosts small.toolBalance .toolSimpleLine{font-size:10px!important}
}
</style>
'''

needle = '</head>'
if needle not in s:
    raise SystemExit('head close not found')
s = s.replace(needle, css + '\n' + needle, 1)
p.write_text(s, encoding='utf-8')
print('Applied result-card consistency patch')
