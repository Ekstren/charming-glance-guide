from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')
marker = 'ALL_RESOURCE_REMAINING_V4'
if marker in text:
    print('Unified raw-resource reserved labels already applied.')
    raise SystemExit(0)

old = r'''  // ALL_RESOURCE_REMAINING_V3: use one Remaining format for Ore / Essence / Sand / Treats.
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

new = r'''  // ALL_RESOURCE_REMAINING_V4: use the same compact reserve wording as Realm tools.
  // Keep showing the FULL S2 reserve requirement; only simplify the label to "(<amount> reserved)".
  function setReservedRawRemaining(id,cost,resources,key,unitLabel=''){
    const el=$(id); if(!el) return;
    el.classList.remove('shortfallCount','shortfallBreakdown','reserveHasGap');
    el.classList.add('rawRemaining');
    const available=Math.max(0,Number(resources?.[key])||0);
    const left=Math.max(0,Math.floor(available-(Number(cost)||0)+1e-9));
    const reserveTarget=Math.max(0,Math.floor(reserveTargetFor(key,resources)+1e-9));
    const unit=unitLabel?` ${unitLabel}`:'';
    el.hidden=false;
    el.textContent=`Remaining: ${fmt(left)}${unit}${reserveTarget>0?` (${fmt(reserveTarget)}${unit} reserved)`:''}`;
  }
'''

if text.count(old) != 1:
    raise SystemExit(f'Expected one V3 reserved-resource display block, found {text.count(old)}')

text = text.replace(old, new, 1)
path.write_text(text, encoding='utf-8')
print('Simplified raw-resource reserve labels while preserving full S2 reserve targets.')
