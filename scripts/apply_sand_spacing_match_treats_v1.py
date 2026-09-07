from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')
marker = 'sand-spacing-match-treats-v1'

if marker in s:
    print('Sand spacing already matches Treats.')
    raise SystemExit(0)

if 'sandResourceFields' not in s or 'treatResourceFields' not in s:
    raise SystemExit('Expected sand/treat resource field classes not found')

style = r'''
<style id="sand-spacing-match-treats-v1">
/* SAND_SPACING_MATCH_TREATS_V1
   Keep the 4 Sand inputs on the same equal 2x2 grid rhythm as Fantomon Treats. */
.sandResourceFields{
  grid-template-columns:repeat(2,minmax(0,1fr))!important;
}
@media(max-width:520px){
  .sandResourceFields{grid-template-columns:1fr 1fr!important}
}
@media(max-width:380px){
  .sandResourceFields{grid-template-columns:1fr!important}
}
</style>
'''

anchor = '</head>'
if anchor not in s:
    raise SystemExit('Missing </head> anchor')
s = s.replace(anchor, style + '\n' + anchor, 1)
p.write_text(s, encoding='utf-8')
print('Matched Chrono Sand field spacing to Fantomon Treats.')
