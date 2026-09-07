from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')
marker = 'ORE_TOOL_SPACING_FIX_V1'

if marker in s:
    print('Ore tool spacing fix already present.')
    raise SystemExit(0)

css = r'''
<style id="ore-tool-spacing-fix-v1">
/* ORE_TOOL_SPACING_FIX_V1
   The joined raw-material + Realm-tool card uses a negative margin to fuse two
   visible halves. When the raw-material line is hidden (common for Ore when the
   plan is funded entirely through Hammers), that same negative margin incorrectly
   pulls the Hammer-only inset upward. Restore the normal standalone inset spacing. */
.planCosts small.rawRemaining[hidden] + small.toolBalance:not([hidden]){
  min-height:34px!important;
  margin-top:5px!important;
  margin-bottom:0!important;
  padding:8px 10px!important;
  border:1px solid var(--line)!important;
  border-radius:10px!important;
  background:var(--input-bg,var(--surface))!important;
}
@media(max-width:720px){
  .planCosts small.rawRemaining[hidden] + small.toolBalance:not([hidden]){
    margin-top:5px!important;
  }
}
</style>
'''

needle = '</head>'
if needle not in s:
    raise SystemExit('Could not find </head>')
s = s.replace(needle, css + '\n' + needle, 1)
p.write_text(s, encoding='utf-8')
print('Applied Ore tool-only spacing fix.')
