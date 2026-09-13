from pathlib import Path

index = Path('index.html')
html = index.read_text(encoding='utf-8')

# Keep the compact post-target controls visible by default.
html = html.replace('<details class="postTargetOptions">', '<details class="postTargetOptions" open>', 1)

replacements = {
    '<label>Ore Realm/day<input id="postTargetOreDaily"': '<label><span>Ore purchases/day</span><input id="postTargetOreDaily"',
    '<label>Essence Realm/day<input id="postTargetEssenceDaily"': '<label><span>Essence purchases/day</span><input id="postTargetEssenceDaily"',
    '<label>Sand Realm/day<input id="postTargetSandDaily"': '<label><span>Sand purchases/day</span><input id="postTargetSandDaily"',
}
for old, new in replacements.items():
    if old not in html:
        raise SystemExit(f'Expected post-target label not found: {old}')
    html = html.replace(old, new, 1)

index.write_text(html, encoding='utf-8')

css = Path('assets/site.css')
text = css.read_text(encoding='utf-8')
marker = '/* POST_TARGET_CUSTOM_ALIGN_V1 */'
if marker not in text:
    text += r'''

/* POST_TARGET_CUSTOM_ALIGN_V1 */
.postTargetCustom label{
  display:grid!important;
  grid-template-rows:24px 34px!important;
  gap:5px!important;
  align-content:start!important;
  align-items:stretch!important;
}
.postTargetCustom label>span{
  display:flex!important;
  align-items:flex-end!important;
  min-width:0;
  line-height:1.15!important;
}
.postTargetCustom input{
  height:34px!important;
  margin-top:0!important;
}
@media(max-width:430px){
  .postTargetCustom label{grid-template-rows:auto 34px!important}
}
'''
css.write_text(text, encoding='utf-8')
print('Post-target options now open by default with aligned purchase inputs.')
