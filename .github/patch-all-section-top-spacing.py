from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')
marker = 'ALL_SECTION_TOP_SPACING_V1'
if marker in s:
    print('already applied')
    raise SystemExit(0)

css = '''
<style id="all-section-top-spacing-v1">
/* ALL_SECTION_TOP_SPACING_V1 */
/* Remove the extra section-level gap on Builds, Companions, and Calculator too. */
.siteSection{
  padding-top:0!important;
  margin-top:0!important;
}
.siteSection > :first-child{
  margin-top:10px!important;
}
@media(max-width:700px){
  .siteSection > :first-child{margin-top:8px!important}
}
</style>
'''

if '</head>' not in s:
    raise SystemExit('head close not found')
s = s.replace('</head>', css + '</head>', 1)
p.write_text(s, encoding='utf-8')
print('normalized top spacing for all site sections')
