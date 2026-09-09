from pathlib import Path

path = Path('index.html')
s = path.read_text(encoding='utf-8')

MARKER = 'RESULT_RESOURCE_CARDS_CLEANUP_V1'
if MARKER in s:
    print('Result resource card cleanup already present.')
    raise SystemExit(0)

replacements = {
    "brief.push('cards = after selected daily Realm plan');": "brief.push('Resource totals include the selected daily Realm plan');",
    "$('targetStatus').textContent=resourceBlocked?'resources':'✓';": "$('targetStatus').textContent=resourceBlocked?'shortfall':'✓';",
    "$('targetMessage').innerHTML=`⚠ Goal not achievable with remaining Realm capacity.<span class=\"targetMessageDetail\">Short at max 20 refreshes/day: ${shortageBits.join(' · ')||'resources'}.</span>`;": "$('targetMessage').innerHTML=`⚠ Goal exceeds remaining Realm capacity.<span class=\"targetMessageDetail\">Still short after maxing Realm purchases: ${shortageBits.join(' · ')||'resources'}.</span>`;",
    "const hardLine=`${fmt(hard)} ${resourceName} hard short · Extra ${itemName} will not cover requirements`;": "const hardLine=`${fmt(hard)} ${resourceName} still missing · max Realm capacity exhausted`;",
    "const line1=`${fmt(short)} ${resourceName} short${runsToCover?` · ${fmt(runsToCover)} ${itemName} needed`:''}`;": "const line1=`${fmt(short)} ${resourceName} short${runsToCover?` · +${fmt(runsToCover)} ${itemName}`:''}`;",
}
for old, new in replacements.items():
    if old not in s:
        raise SystemExit(f'Expected patch target not found: {old[:100]}')
    s = s.replace(old, new)

css = r'''
<style id="result-resource-cards-cleanup-v1">
/* RESULT_RESOURCE_CARDS_CLEANUP_V1
   The outer material tile is the card. Raw balance, Realm-tool actions and Stamina
   are compact rows inside it instead of a stack of nested rounded cards/bars. */
.planCosts,.planCostsFour{
  gap:10px!important;
  margin:0 0 18px!important;
  align-items:stretch!important;
}
.planCosts>span{
  display:flex!important;
  flex-direction:column!important;
  align-content:initial!important;
  min-height:0!important;
  padding:13px 14px 12px!important;
  border-radius:13px!important;
  gap:0!important;
  overflow:hidden!important;
}
.planCosts>span>b{
  margin:4px 0 9px!important;
  font-size:20px!important;
  line-height:1.1!important;
  letter-spacing:-.02em!important;
}
.planCosts>span>small,
.planCosts>span>small *{
  text-transform:none!important;
}

/* Kill all older joined-inset-card treatments. */
.planCosts small.rawRemaining,
.planCosts small.rawRemaining:has(+ small.toolBalance:not([hidden])),
.planCosts small.rawRemaining:not(:has(+ small.toolBalance:not([hidden]))),
.planCosts small.toolBalance:not([hidden]),
.planCosts small.rawRemaining + small.toolBalance:not([hidden]){
  box-sizing:border-box!important;
  width:100%!important;
  min-height:0!important;
  margin:0!important;
  padding:0!important;
  border:0!important;
  border-radius:0!important;
  background:transparent!important;
  box-shadow:none!important;
  position:static!important;
}
.planCosts small.rawRemaining{
  display:grid!important;
  gap:4px!important;
  padding-top:9px!important;
  border-top:1px solid var(--line)!important;
  color:var(--secondary-text)!important;
}
.planCosts small.toolBalance:not([hidden]){
  display:grid!important;
  gap:5px!important;
  padding-top:9px!important;
  border-top:1px solid var(--line)!important;
}
.planCosts small.rawRemaining + small.toolBalance:not([hidden]){
  margin-top:8px!important;
  padding-top:8px!important;
}

.planCosts .resourceRemainingLine,
.planCosts .reserveRequirementLine,
.planCosts small.shortfallBreakdown,
.planCosts small.shortfallBreakdown .planShort,
.planCosts small.shortfallBreakdown .realmBridge,
.planCosts small.shortfallBreakdown .hardShort{
  margin:0!important;
  padding:0!important;
  border:0!important;
  background:transparent!important;
  border-radius:0!important;
  min-height:0!important;
  font-size:9px!important;
  line-height:1.4!important;
  letter-spacing:0!important;
}
.planCosts .resourceRemainingLine{
  display:flex!important;
  align-items:baseline!important;
  justify-content:space-between!important;
  gap:8px!important;
  color:var(--status-positive,var(--green))!important;
  font-weight:800!important;
}
.planCosts .reserveRequirementLine{
  color:var(--secondary-text)!important;
  font-weight:700!important;
}
.planCosts small.shortfallBreakdown{
  display:grid!important;
  gap:3px!important;
}
.planCosts small.shortfallBreakdown .planShort,
.planCosts small.shortfallBreakdown .hardShort{
  color:var(--status-negative,var(--red))!important;
  font-weight:850!important;
}
.planCosts small.shortfallBreakdown .realmBridge{
  color:var(--status-warning,var(--gold))!important;
  font-weight:750!important;
}

/* Realm action rows: label column + value column, no colored full-width bars. */
.planCosts small.toolBalance .toolSimpleLine{
  display:grid!important;
  grid-template-columns:48px minmax(0,1fr)!important;
  align-items:baseline!important;
  gap:7px!important;
  min-height:0!important;
  margin:0!important;
  padding:0!important;
  border:0!important;
  background:transparent!important;
  border-radius:0!important;
  font-size:9px!important;
  line-height:1.4!important;
}
.planCosts small.toolBalance .toolSimpleLine i,
.planCosts small.toolBalance .toolSimpleLine b,
.planCosts small.toolBalance .toolSimpleLine b em{
  font-size:inherit!important;
  line-height:inherit!important;
}
.planCosts small.toolBalance .toolSimpleLine i{
  color:var(--secondary-text)!important;
  font-style:normal!important;
  font-weight:700!important;
}
.planCosts small.toolBalance .toolSimpleLine b{
  margin:0!important;
  padding:0!important;
  border:0!important;
  background:transparent!important;
  font-weight:850!important;
}
.planCosts small.toolBalance .toolSimpleLine b em{
  color:inherit!important;
  opacity:.82!important;
  font-style:normal!important;
  font-weight:700!important;
}
.planCosts small.toolBalance .toolUseLine,
.planCosts small.toolBalance .toolUseLine i,
.planCosts small.toolBalance .toolUseLine b,
.planCosts small.toolBalance .toolUseLine b em{
  color:var(--status-info,var(--blue))!important;
}
.planCosts small.toolBalance .toolNeedLine,
.planCosts small.toolBalance .toolNeedLine i,
.planCosts small.toolBalance .toolNeedLine b,
.planCosts small.toolBalance .toolNeedLine b em{
  color:var(--status-negative,var(--red))!important;
}
.planCosts small.toolBalance .toolRemainingLine,
.planCosts small.toolBalance .toolRemainingLine i,
.planCosts small.toolBalance .toolRemainingLine b,
.planCosts small.toolBalance .toolRemainingLine b em{
  color:var(--status-positive,var(--green))!important;
}
.planCosts small.toolBalance .staminaProjectionLine,
.planCosts small.toolBalance .staminaProjectionLine i,
.planCosts small.toolBalance .staminaProjectionLine b,
.planCosts small.toolBalance .staminaProjectionLine b em{
  color:var(--status-info,var(--blue))!important;
}
.planCosts small.toolBalance .staminaProjectionLine{
  margin:0!important;
  padding:0!important;
  border-top:0!important;
}

/* The small line between upgrades and resource cards should read like a caption, not debug text. */
.optimizerSummary:not([hidden]){
  margin:2px 0 12px!important;
  padding:0!important;
  color:var(--secondary-text)!important;
  font-size:9px!important;
  line-height:1.45!important;
  font-weight:650!important;
}

/* Resource-blocked score state is a badge instead of a stray red word. */
.resultScoreLine em.notMet{
  display:inline-flex!important;
  align-items:center!important;
  min-height:20px!important;
  padding:2px 7px!important;
  border:1px solid color-mix(in srgb,var(--status-negative,var(--red)) 46%,var(--line))!important;
  border-radius:999px!important;
  background:color-mix(in srgb,var(--status-negative,var(--red)) 9%,transparent)!important;
  color:var(--status-negative,var(--red))!important;
  text-transform:uppercase!important;
  letter-spacing:.05em!important;
  font-size:8px!important;
  line-height:1!important;
  font-style:normal!important;
  font-weight:900!important;
}
#targetMessage .targetMessageDetail{
  margin-top:4px!important;
  font-weight:700!important;
  opacity:.9!important;
}

@media(max-width:700px){
  .planCosts>span{padding:12px!important}
  .planCosts>span>b{font-size:19px!important}
  .planCosts .resourceRemainingLine,
  .planCosts .reserveRequirementLine,
  .planCosts small.shortfallBreakdown,
  .planCosts small.toolBalance .toolSimpleLine{font-size:10px!important}
  .planCosts small.toolBalance .toolSimpleLine{grid-template-columns:52px minmax(0,1fr)!important}
  .optimizerSummary:not([hidden]){font-size:9.5px!important}
}
</style>
'''

if '</head>' not in s:
    raise SystemExit('Missing </head> marker')
s = s.replace('</head>', css + '\n</head>', 1)
path.write_text(s, encoding='utf-8')
print('Polished result resource cards and shortfall messaging.')
