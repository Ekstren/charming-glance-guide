from pathlib import Path

path = Path('index.html')
s = path.read_text(encoding='utf-8')
marker = 'LEFT_ALIGN_REMAINING_COUNTS_V1'
if marker in s:
    print('Remaining counts already left aligned.')
    raise SystemExit(0)

css = r'''
<style id="left-align-remaining-counts-v1">
/* LEFT_ALIGN_REMAINING_COUNTS_V1
   Keep the Remaining value visually attached to its label instead of pinning it
   to the far edge of each resource card. */
.planCosts .resourceRemainingLine{
  justify-content:flex-start!important;
  gap:6px!important;
}
.planCosts .resourceRemainingLine b{
  margin-left:0!important;
}
</style>
'''

if '</head>' not in s:
    raise SystemExit('Missing </head>')
s = s.replace('</head>', css + '\n</head>', 1)
path.write_text(s, encoding='utf-8')
print('Left-aligned Remaining counts in result resource cards.')
