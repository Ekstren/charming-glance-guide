from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
MARK='RESOURCE_CARD_CONSISTENCY_V1'

if MARK in s:
    print('resource card consistency already applied')
    raise SystemExit(0)

old_raw="    el.textContent=`Remaining: ${fmt(left)}${unitLabel?` ${unitLabel}`:''}`;"
new_raw="    el.innerHTML=`<span class=\"resourceRemainingLine\">Remaining: <b>${fmt(left)}</b>${unitLabel?` ${unitLabel}`:''}</span>`;"
if old_raw not in s:
    raise SystemExit('setRawRemaining anchor missing')
s=s.replace(old_raw,new_raw,1)

old_reserved='''    el.innerHTML=`<span class="resourceRemainingLine">Remaining: <b>${fmt(left)}</b>${unit}</span>`+
      (reserveTarget>0?`<span class="reserveRequirementLine${shortfall>0?' reserveShort':''}">Reserve target: <b>${fmt(reserveTarget)}</b>${unit} · ${fmt(covered)} covered${detail}${shortfall>0?` · <strong>${fmt(shortfall)} short</strong>`:' · ✓ protected'}</span>`:'');'''
new_reserved='''    el.innerHTML=`<span class="resourceRemainingLine">Remaining: <b>${fmt(left)}</b>${unit}</span>`+
      (reserveTarget>0?`<span class="reserveRequirementLine${shortfall>0?' reserveShort':''}">Reserve: <b>${fmt(reserveTarget)}</b>${unit}${shortfall>0?` · <strong>${fmt(shortfall)} short</strong>`:' · <strong class="reserveProtected">✓ protected</strong>'}</span>`:'');'''
if old_reserved not in s:
    raise SystemExit('reserved remaining renderer anchor missing')
s=s.replace(old_reserved,new_reserved,1)

css=r'''
<style id="resource-card-consistency-v1">
/* RESOURCE_CARD_CONSISTENCY_V1 */
/* One hierarchy on every resource card: title -> required amount -> balance/status. */
.planCosts>span>b:before,
.planCosts>span>b:after,
#sandCost:after{content:none!important;display:none!important}
.planCosts>span{gap:6px!important;align-content:start!important}
.planCosts>span>b{margin:0!important;font-size:19px!important;line-height:1.15!important}
.planCosts small.rawRemaining{
  display:grid!important;
  gap:0!important;
  align-content:start!important;
  min-height:58px!important;
  margin-top:5px!important;
  padding:9px 10px!important;
  border:1px solid var(--line)!important;
  border-radius:10px!important;
  background:color-mix(in srgb,var(--surface) 84%,var(--bg) 16%)!important;
  text-transform:none!important;
}
.planCosts .resourceRemainingLine,
.planCosts .reserveRequirementLine{
  display:block!important;
  background:none!important;
  border-left:0!important;
  border-right:0!important;
  border-bottom:0!important;
  border-radius:0!important;
  margin:0!important;
}
.planCosts .resourceRemainingLine{
  border-top:0!important;
  padding:0!important;
  color:var(--status-positive,var(--green))!important;
  font-size:10px!important;
  line-height:1.4!important;
  font-weight:800!important;
}
.planCosts .resourceRemainingLine b{font-size:inherit!important;color:inherit!important}
.planCosts .reserveRequirementLine{
  border-top:1px solid var(--line)!important;
  margin-top:7px!important;
  padding:7px 0 0!important;
  color:var(--secondary-text)!important;
  font-size:8.5px!important;
  line-height:1.4!important;
  font-weight:750!important;
}
.planCosts .reserveRequirementLine b{font-size:inherit!important;color:var(--ink)!important}
.planCosts .reserveRequirementLine .reserveProtected{color:var(--status-positive,var(--green))!important;font-weight:850!important}
.planCosts .reserveRequirementLine.reserveShort,
.planCosts .reserveRequirementLine.reserveShort b,
.planCosts .reserveRequirementLine.reserveShort strong{color:var(--status-negative,var(--red))!important}
@media(max-width:700px){
  .planCosts small.rawRemaining{min-height:58px!important;padding:10px 11px!important}
  .planCosts .resourceRemainingLine{font-size:10.5px!important}
  .planCosts .reserveRequirementLine{font-size:9px!important}
}
</style>
'''

head=s.find('</head>')
if head<0:
    raise SystemExit('</head> missing')
s=s[:head]+css+s[head:]
p.write_text(s,encoding='utf-8')
print('normalized resource cost cards')
