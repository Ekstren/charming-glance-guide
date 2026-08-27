from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')

old = '''  // ALL_RESOURCE_REMAINING_V4: use the same compact reserve wording as Realm tools.
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

new = '''  // RAW_FIRST_RESERVE_DISPLAY_V5: Remaining is strictly RAW material left after the
  // current-season upgrade spend. S2 reserve text may annotate only the portion of that
  // raw remainder that is actually reserved. Any reserve gap is handled separately by
  // Material Realm tools; tool-equivalent value must never inflate the raw Remaining number.
  function setReservedRawRemaining(id,cost,resources,key,unitLabel=''){
    const el=$(id); if(!el) return;
    el.classList.remove('shortfallCount','shortfallBreakdown','reserveHasGap');
    el.classList.add('rawRemaining');
    const available=Math.max(0,Number(resources?.[key])||0);
    const left=Math.max(0,Math.floor(available-(Number(cost)||0)+1e-9));
    const reserveTarget=Math.max(0,Math.floor(reserveTargetFor(key,resources)+1e-9));
    const rawReserved=Math.min(left,reserveTarget);
    const unit=unitLabel?` ${unitLabel}`:'';
    el.hidden=false;
    el.textContent=`Remaining: ${fmt(left)}${unit}${reserveTarget>0?` (${fmt(rawReserved)}${unit} reserved)`:''}`;
  }
'''

if old in text:
    text = text.replace(old, new, 1)
elif 'RAW_FIRST_RESERVE_DISPLAY_V5' not in text:
    raise SystemExit('Expected setReservedRawRemaining V4 block was not found; refusing to patch.')

# Keep the shortage-view documentation aligned with the actual UI contract: the visible
# balance itself is raw-only; Realm tools participate only after raw has been exhausted.
old_comment = '''    // Two shortage views are intentional:
    // 1) Resource cards = after the USER'S committed plan (Cart/Stamina + tools on hand + recurring daily tools).
    //    This must move when 0/0/0 vs 4/4/4 vs 10/10/10 changes.
    // 2) Top warning = hard residual after EVERY remaining extra Realm refresh slot is also exhausted.
    //    This is the true physical season-end impossibility amount.
'''
new_comment = '''    // Two shortage views are intentional:
    // 1) Normal Resource-card Remaining = RAW material only after the recommended spend.
    //    Realm tools enter the card only once raw material is exhausted and a shortage must be bridged.
    // 2) Top warning = hard residual after EVERY remaining extra Realm refresh slot is also exhausted.
    //    This is the true physical season-end impossibility amount.
'''
if old_comment in text:
    text = text.replace(old_comment, new_comment, 1)

path.write_text(text, encoding='utf-8')
