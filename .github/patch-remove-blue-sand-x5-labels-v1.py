from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
marker='BLUE_SAND_LABEL_CLEANUP_V1'
if marker in s:
    print('already applied')
    raise SystemExit(0)

old_label='<span>Saved · Blue ×5</span>'
new_label='<span>Saved · Blue</span>'
if old_label not in s:
    raise SystemExit('Blue Sand field label not found')
s=s.replace(old_label,new_label,1)

old_helper="if($('sandEquivalentNow')) $('sandEquivalentNow').textContent=`Saved total: ${fmtCompact(savedSandEq)} basic-equivalent · Blue counts ×${SAND_BLUE_EQ}`;"
new_helper="/* BLUE_SAND_LABEL_CLEANUP_V1: the planner still applies the canonical Blue Sand conversion internally; the UI no longer repeats the x5 note. */\n    if($('sandEquivalentNow')) $('sandEquivalentNow').textContent=`Saved total: ${fmtCompact(savedSandEq)} basic-equivalent`;"
if old_helper not in s:
    raise SystemExit('Blue Sand saved-total helper not found')
s=s.replace(old_helper,new_helper,1)

p.write_text(s,encoding='utf-8')
print('removed redundant Blue Sand x5 labels')
