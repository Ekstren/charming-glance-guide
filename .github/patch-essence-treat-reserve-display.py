from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')
marker = 'ESSENCE_TREAT_RESERVE_DISPLAY_V1'
if marker in text:
    print('Essence/Treat reserve display already applied.')
    raise SystemExit(0)

old = r'''  function setEssenceBalance(id,cost,resources){ setRawRemaining(id,cost,resources?.essence); }
  function setSandBalance(id,cost,resources){ setRawRemaining(id,cost,resources?.sand); }
  function setTreatBalance(id,cost,resources){ setRawRemaining(id,cost,resources?.treat,'basic-eq.'); }
'''

new = r'''  // ESSENCE_TREAT_RESERVE_DISPLAY_V1: make S2-protected raw resources as obvious as
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
  function setEssenceBalance(id,cost,resources){ setReservedRawRemaining(id,cost,resources,'essence'); }
  function setSandBalance(id,cost,resources){ setRawRemaining(id,cost,resources?.sand); }
  function setTreatBalance(id,cost,resources){ setReservedRawRemaining(id,cost,resources,'treat','basic-eq.'); }
'''

if text.count(old) != 1:
    raise SystemExit(f'Expected one Essence/Sand/Treat balance block, found {text.count(old)}')
text = text.replace(old, new, 1)

path.write_text(text, encoding='utf-8')
print('Added S2 reserve amounts to Essence and Treat remaining lines.')
