from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')
marker = 'MATERIAL_REALM_VISUAL_CLEANUP_V1'
if marker in s:
    print('already applied')
    raise SystemExit(0)

# Trim redundant wording without touching any planner math.
repls = {
    'ORE REALM REFRESHES / DAY': 'ORE REFRESHES / DAY',
    'ESSENCE REALM REFRESHES / DAY': 'ESSENCE REFRESHES / DAY',
    'SAND REALM REFRESHES / DAY': 'SAND REFRESHES / DAY',
    'Existing tools + your normal daily purchases': 'Saved tools + daily purchases',
    'Current amount covers target': 'Covers target',
}
for old, new in repls.items():
    s = s.replace(old, new)

css = r'''
<style id="material-realm-visual-cleanup-v1">
/* MATERIAL_REALM_VISUAL_CLEANUP_V1
   Presentation only: make the Material Realm block read like the rest of the
   calculator instead of a dense spreadsheet. No optimizer/resource logic changes. */
.realmInventory{
  padding:14px!important;
  border-radius:14px!important;
}
.realmInventoryTop{
  margin-bottom:10px!important;
  align-items:baseline!important;
}
.realmInventoryTop strong{
  font-size:13px!important;
  letter-spacing:-.01em;
}
.realmInventoryTop small{
  color:var(--secondary-text)!important;
  font-size:9px!important;
}

/* Group each saved Realm tool with its value/projection in one quiet mini-card. */
.realmInventoryGrid{
  gap:9px!important;
}
.realmInventoryGrid>label{
  min-width:0;
  padding:9px 10px 8px!important;
  border:1px solid var(--line)!important;
  border-radius:11px!important;
  background:var(--ui-subpanel,var(--bg))!important;
  color:var(--body-text)!important;
  font-size:9px!important;
  line-height:1.2!important;
}
.realmInventoryGrid input{
  min-height:40px!important;
  margin-top:5px!important;
  padding:7px 9px!important;
  border-radius:9px!important;
  font-size:14px!important;
}
.realmInventoryGrid label>small{
  margin-top:4px!important;
  font-size:9px!important;
  line-height:1.25!important;
}
.realmInventoryGrid .realmCurrentValue{
  color:var(--secondary-text)!important;
  font-weight:700!important;
}
#hammerProjected,#knucklesProjected,#shovelProjected{
  color:var(--secondary-text)!important;
  font-weight:750!important;
}
.realmInventoryGrid .realmAfterPlan{
  color:var(--status-positive,var(--green))!important;
  font-weight:800!important;
}

/* Give the daily plan its own clean row, then a slim full-width gain summary. */
.realmDailyPlanRow{
  grid-template-columns:1fr!important;
  gap:9px!important;
  align-items:stretch!important;
  margin-top:12px!important;
  padding-top:12px!important;
}
.realmDailyTitle{
  align-items:baseline!important;
  margin-bottom:7px!important;
  font-size:10px!important;
}
.realmDailyTitle small{
  color:var(--secondary-text)!important;
  font-size:8px!important;
}
.realmDailyInputs{
  gap:9px!important;
}
.realmDailyInputs label{
  font-size:9px!important;
  line-height:1.2!important;
}
.realmDailyInputs input{
  min-height:40px!important;
  margin-top:5px!important;
  padding:7px 9px!important;
  font-size:14px!important;
  border-radius:9px!important;
}
.realmDailyInputs small{
  margin-top:4px!important;
  font-size:9px!important;
  line-height:1.25!important;
  font-weight:750!important;
}
.realmDailyInputs small:not(.realmRecommendUp):not(.realmRecommendMax){
  color:var(--secondary-text)!important;
}
.realmPlanSummary{
  min-height:0!important;
  display:flex!important;
  align-items:baseline!important;
  gap:10px!important;
  padding:8px 10px!important;
  border-radius:10px!important;
  background:var(--ui-subpanel,var(--bg))!important;
}
.realmPlanSummary span{
  flex:0 0 auto;
  color:var(--muted)!important;
  font-size:8px!important;
}
.realmPlanSummary b{
  margin:0!important;
  color:var(--ink)!important;
  font-size:11px!important;
  line-height:1.3!important;
}
.realmPlanSummary small{
  margin:0 0 0 auto!important;
  color:var(--secondary-text)!important;
  font-size:8px!important;
  line-height:1.3!important;
  text-align:right;
}

@media(max-width:700px){
  .realmInventory{padding:12px!important}
  .realmInventoryTop{align-items:flex-start!important}
  .realmInventoryGrid,.realmDailyInputs{grid-template-columns:1fr!important}
  .realmInventoryGrid>label{padding:10px!important}
  .realmPlanSummary{
    align-items:flex-start!important;
    flex-direction:column!important;
    gap:3px!important;
  }
  .realmPlanSummary small{margin-left:0!important;text-align:left!important}
}
</style>
'''

if '</head>' not in s:
    raise SystemExit('</head> not found')
s = s.replace('</head>', css + '\n</head>', 1)
p.write_text(s, encoding='utf-8')
print('cleaned Material Realm presentation')
