from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')
marker = 'PAGE_SPACING_MAX_TARGET_ALIGN_V1'
if marker in s:
    print('already applied')
    raise SystemExit(0)

css = '''
<style id="page-spacing-max-target-align-v1">
/* PAGE_SPACING_MAX_TARGET_ALIGN_V1 */
/* Keep section content visually attached to the page selector. */
.siteSection > :first-child{margin-top:10px!important}

/* Keep the max-target action and its plan summary vertically aligned. */
.calcGrid .findMaxCell .maxTargetControl{
  min-height:40px!important;
  padding:0 10px!important;
  display:flex!important;
  align-items:center!important;
  gap:10px!important;
}
.calcGrid .findMaxCell .maxTargetControl button,
.calcGrid .findMaxCell .maxTargetControl small{
  align-self:center!important;
  margin:0!important;
  line-height:1.15!important;
}
.calcGrid .findMaxCell .maxTargetControl small{
  display:flex!important;
  align-items:center!important;
  min-height:20px!important;
}
@media(max-width:700px){
  .siteSection > :first-child{margin-top:8px!important}
  .calcGrid .findMaxCell .maxTargetControl{gap:7px!important;padding:0 9px!important}
}
</style>
'''

if '</head>' not in s:
    raise SystemExit('head close not found')
s = s.replace('</head>', css + '</head>', 1)
p.write_text(s, encoding='utf-8')
print('tightened section spacing and aligned max-target row')
