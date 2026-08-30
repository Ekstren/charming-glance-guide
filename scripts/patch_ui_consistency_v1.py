from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')

# Remove the long-range S5 card from the visible timeline intel area.
s, removed = re.subn(
    r'\s*<details\s+class="timelineIntel"\s+id="ignisReferenceDetails">.*?</details>',
    '',
    s,
    count=1,
    flags=re.S,
)

marker = 'UI_CONSISTENCY_V1'
if marker not in s:
    css = r'''
<style id="ui-consistency-v1">
/* UI_CONSISTENCY_V1
   One visual language for Material Realm + Daily Shop controls:
   outer section -> rounded mini-card -> rounded input -> rounded summary. */

/* Belt-and-suspenders: keep the removed long-range S5 reference hidden if older markup is ever reintroduced. */
#ignisReferenceDetails{display:none!important}

/* Section headers use the same spacing/alignment in Material Realm and Daily Shop. */
.realmInventoryTop{
  display:flex!important;
  align-items:center!important;
  justify-content:space-between!important;
  gap:12px!important;
  margin-bottom:9px!important;
}
.realmInventoryTop strong{font-size:12px!important;line-height:1.3!important}
.realmInventoryTop small{
  color:var(--secondary-text)!important;
  font-size:9px!important;
  line-height:1.35!important;
  text-align:right!important;
}

/* The saved-tool cards establish the canonical mini-card treatment. */
.realmInventoryGrid>label,
.realmDailyInputs>label,
.shopRefreshControl,
.shopGainSummary{
  min-width:0!important;
  border:1px solid var(--line)!important;
  border-radius:11px!important;
  background:var(--ui-subpanel,var(--bg))!important;
  padding:10px 11px!important;
  box-shadow:none!important;
}

/* Material Realm purchase controls should look like the Hammers / Knuckles / Shovels cards. */
.realmDailyPlanRow{
  display:grid!important;
  grid-template-columns:1fr!important;
  gap:10px!important;
  align-items:stretch!important;
  border-top:1px solid var(--line)!important;
  margin-top:12px!important;
  padding-top:12px!important;
}
.realmDailyCustom{min-width:0!important}
.realmDailyTitle{
  display:flex!important;
  align-items:center!important;
  justify-content:space-between!important;
  gap:12px!important;
  margin:0 0 8px!important;
  color:var(--ink)!important;
  font-size:9px!important;
  font-weight:850!important;
  line-height:1.3!important;
  text-transform:uppercase!important;
  letter-spacing:.05em!important;
}
.realmDailyTitle small{
  color:var(--secondary-text)!important;
  font-size:8px!important;
  font-weight:650!important;
  line-height:1.35!important;
  text-transform:none!important;
  letter-spacing:0!important;
  text-align:right!important;
}
.realmDailyInputs{
  display:grid!important;
  grid-template-columns:repeat(3,minmax(0,1fr))!important;
  gap:9px!important;
  align-items:stretch!important;
}
.realmDailyInputs>label{
  display:grid!important;
  grid-template-rows:minmax(24px,auto) 46px auto!important;
  gap:6px!important;
  align-content:start!important;
  color:var(--body-text)!important;
  font-size:9px!important;
  font-weight:800!important;
  line-height:1.25!important;
  text-transform:uppercase!important;
  letter-spacing:.04em!important;
}
.realmDailyInputs input{
  display:block!important;
  width:100%!important;
  height:46px!important;
  min-height:46px!important;
  margin:0!important;
  padding:9px 11px!important;
  border:1px solid var(--line)!important;
  border-radius:10px!important;
  background:var(--input-bg,var(--surface))!important;
  color:var(--ink)!important;
  font-size:14px!important;
  font-weight:850!important;
  box-sizing:border-box!important;
}
.realmDailyInputs input:focus{
  outline:none!important;
  border-color:var(--green)!important;
  box-shadow:0 0 0 3px color-mix(in srgb,var(--green) 15%,transparent)!important;
}
.realmDailyInputs small{
  display:block!important;
  margin:0!important;
  color:var(--status-info,var(--green))!important;
  font-size:9px!important;
  font-weight:750!important;
  line-height:1.35!important;
  text-transform:none!important;
  letter-spacing:0!important;
}
.realmDailyInputs small.realmRecommendUp{color:var(--status-warning,var(--gold))!important}
.realmDailyInputs small.realmRecommendMax{color:var(--status-negative,var(--red))!important}

/* Make the daily-gain footer a deliberate summary bubble instead of a flat strip. */
.realmPlanSummary{
  display:grid!important;
  grid-template-columns:auto minmax(0,1fr) auto!important;
  align-items:center!important;
  gap:9px!important;
  min-height:48px!important;
  padding:10px 12px!important;
  border:1px solid var(--line)!important;
  border-radius:11px!important;
  background:var(--ui-subpanel,var(--bg))!important;
  box-shadow:none!important;
}
.realmPlanSummary span{
  margin:0!important;
  color:var(--muted)!important;
  font-size:8px!important;
  font-weight:800!important;
  text-transform:uppercase!important;
  letter-spacing:.05em!important;
}
.realmPlanSummary b{
  margin:0!important;
  color:var(--status-positive,var(--green))!important;
  font-size:12px!important;
  font-weight:850!important;
  min-width:0!important;
}
.realmPlanSummary small{
  margin:0!important;
  color:var(--secondary-text)!important;
  font-size:8px!important;
  line-height:1.35!important;
  text-align:right!important;
}

/* Daily Shop mirrors Material Realm rather than using its own visual dialect. */
.shopEstimatePanel{margin-top:12px!important;overflow:hidden!important}
.shopEstimatePanel .realmInventoryTop{
  padding-bottom:0!important;
  border-bottom:0!important;
  margin-bottom:9px!important;
}
.shopEstimateCompact{
  display:grid!important;
  grid-template-columns:minmax(210px,.72fr) minmax(320px,1.28fr)!important;
  gap:9px!important;
  align-items:stretch!important;
  padding:0!important;
}
.shopRefreshControl{
  display:flex!important;
  align-items:stretch!important;
}
.shopRefreshControl label{
  display:grid!important;
  grid-template-rows:minmax(24px,auto) 46px auto!important;
  gap:6px!important;
  width:100%!important;
  color:var(--body-text)!important;
  font-size:9px!important;
  font-weight:800!important;
  line-height:1.25!important;
  text-transform:uppercase!important;
  letter-spacing:.04em!important;
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
  background:var(--input-bg,var(--surface))!important;
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
  margin:0!important;
  color:var(--secondary-text)!important;
  font-size:9px!important;
  font-weight:650!important;
  line-height:1.35!important;
  text-transform:none!important;
  letter-spacing:0!important;
}
.shopGainSummary{
  display:grid!important;
  grid-template-columns:1fr!important;
  gap:0!important;
}
.shopGainSummary>div{
  display:flex!important;
  align-items:center!important;
  justify-content:space-between!important;
  gap:16px!important;
  min-height:28px!important;
  padding:3px 0!important;
  border:0!important;
  background:transparent!important;
}
.shopGainSummary span{color:var(--body-text)!important;font-size:10px!important;font-weight:700!important}
.shopGainSummary b{
  color:var(--status-positive,var(--green))!important;
  font-size:11px!important;
  font-weight:850!important;
  white-space:nowrap!important;
  font-variant-numeric:tabular-nums!important;
}
.shopEstimateNote{
  display:block!important;
  margin:0!important;
  padding:7px 2px 0!important;
  color:var(--muted)!important;
  font-size:8px!important;
  line-height:1.35!important;
}

@media(max-width:700px){
  .realmInventoryTop{align-items:flex-start!important;flex-direction:column!important;gap:3px!important}
  .realmInventoryTop small{text-align:left!important;max-width:none!important}
  .realmDailyTitle{align-items:flex-start!important;flex-direction:column!important;gap:3px!important}
  .realmDailyTitle small{text-align:left!important}
  .realmDailyInputs,.shopEstimateCompact{grid-template-columns:1fr!important}
  .realmPlanSummary{grid-template-columns:1fr!important;gap:3px!important}
  .realmPlanSummary small{text-align:left!important}
}
</style>
'''
    close = s.lower().rfind('</body>')
    if close < 0:
        raise SystemExit('closing </body> not found')
    s = s[:close] + css + '\n' + s[close:]

p.write_text(s, encoding='utf-8')
print(f'UI consistency patch applied; removed Ignis card: {bool(removed)}')
