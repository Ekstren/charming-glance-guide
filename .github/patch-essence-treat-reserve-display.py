from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')
marker = 'ALL_RESOURCE_REMAINING_V3'
if marker in text:
    print('Unified resource Remaining/reserve-target display already applied.')
    raise SystemExit(0)

# ALL_RESOURCE_REMAINING_V3
# Keep all four cards on the same "Remaining:" language. For S2-protected resources,
# the parenthetical must show the FULL S2 reserve requirement, not min(remaining, target).
# The old min() behavior made Sand look like its reserve mysteriously changed with the S1 plan.
old_block = r'''  // ALL_RESOURCE_REMAINING_V2: use one Remaining format for Ore / Essence / Sand / Treats.
  // S2-protected resources also show the protected amount in parentheses.
  // make S2-protected raw resources as obvious as
  // reserved Realm tools. Remaining includes the protected amount; the parenthetical shows
  // how much of that total must stay untouched for S2.
  function setReservedRawRemaining(id,cost,resources,key,unitLabel=''){
    const el=$(id); if(!el) return;
    el.classList.remove('shortfallCount','shortfallBreakdown','reserveHasGap');
    el.classList.add('rawRemaining');
    const available=Math.max(0,Number(resources?.[key])||0);
    const left=Math.max(0,Math.floor(available-(Number(cost)||0)+1e-9));
    const reserve=Math.min(left,Math.max(0,Math.floor(reserveTargetFor(key,resources)+1e-9)));
    const unit=unitLabel?` ${unitLabel}`:'';
    el.hidden=false;
    el.textContent=`Remaining: ${fmt(left)}${unit}${reserve>0?` (${fmt(reserve)}${unit} reserved)`:''}`;
  }
'''
new_block = r'''  // ALL_RESOURCE_REMAINING_V3: use one Remaining format for Ore / Essence / Sand / Treats.
  // S2-protected resources show the FULL reserve requirement. Do not cap the displayed reserve
  // at the raw amount left after the S1 plan; Realm tools can cover the rest of that requirement.
  function setReservedRawRemaining(id,cost,resources,key,unitLabel=''){
    const el=$(id); if(!el) return;
    el.classList.remove('shortfallCount','shortfallBreakdown','reserveHasGap');
    el.classList.add('rawRemaining');
    const available=Math.max(0,Number(resources?.[key])||0);
    const left=Math.max(0,Math.floor(available-(Number(cost)||0)+1e-9));
    const reserveTarget=Math.max(0,Math.floor(reserveTargetFor(key,resources)+1e-9));
    const unit=unitLabel?` ${unitLabel}`:'';
    el.hidden=false;
    el.textContent=`Remaining: ${fmt(left)}${unit}${reserveTarget>0?` (S2 reserve: ${fmt(reserveTarget)}${unit})`:''}`;
  }
'''
if text.count(old_block) != 1:
    raise SystemExit(f'Expected one V2 reserved-resource display block, found {text.count(old_block)}')
text = text.replace(old_block, new_block, 1)

path.write_text(text, encoding='utf-8')
print('Fixed resource cards to show full S2 reserve targets instead of capping at Remaining.')
