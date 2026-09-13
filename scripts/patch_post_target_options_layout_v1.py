from pathlib import Path

index = Path('index.html')
html = index.read_text(encoding='utf-8')
stop = '            <label><input type="radio" name="postTargetToolMode" value="stop"> Stop tool purchases</label>\n'
if stop not in html:
    raise SystemExit('Stop tool purchases option not found')
html = html.replace(stop, '', 1)
index.write_text(html, encoding='utf-8')

css = Path('assets/site.css')
text = css.read_text(encoding='utf-8')
marker = '/* POST_TARGET_OPTIONS_SIDE_BY_SIDE_V1 */'
if marker not in text:
    text += r'''

/* POST_TARGET_OPTIONS_SIDE_BY_SIDE_V1 */
.postTargetOptionsBody{
  display:grid!important;
  grid-template-columns:repeat(2,minmax(0,1fr))!important;
  gap:10px!important;
  padding:0 0 10px!important;
}
.postTargetOptions .postTargetToolPlan,
.postTargetOptions .postTargetStaminaPlan{
  min-width:0;
  margin:0!important;
  padding:10px!important;
  border:1px solid var(--line)!important;
  border-radius:10px;
  background:color-mix(in srgb,var(--surface) 92%,var(--purple));
}
.postTargetOptions .postTargetPlanHead{
  display:block!important;
  margin-bottom:8px!important;
}
.postTargetOptions .postTargetPlanHead small{
  display:block;
  margin-top:3px;
  text-align:left!important;
  line-height:1.35;
}
.postTargetOptions .postTargetPlanControls{
  gap:7px 12px;
}
@media(max-width:760px){
  .postTargetOptionsBody{grid-template-columns:1fr!important}
}
'''
css.write_text(text, encoding='utf-8')
print('Placed post-target tool and Stamina plans side by side and removed stop-purchases option.')
