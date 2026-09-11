from pathlib import Path

path = Path('assets/site.css')
css = path.read_text(encoding='utf-8')
marker = '/* FINISH_EARLY_INPUT_WIDTH_V1 */'
block = r'''

/* FINISH_EARLY_INPUT_WIDTH_V1 */
/* Give decimal half-day values enough room even when native number spinners are visible. */
.finishEarlyCard{
  min-height:50px!important;
  padding:9px 12px!important;
}
.finishEarlyCard input{
  width:58px!important;
  min-width:58px!important;
  max-width:58px!important;
  flex-basis:58px!important;
  height:32px!important;
  min-height:32px!important;
  padding-left:7px!important;
  padding-right:7px!important;
  font-size:12px!important;
}
@media(max-width:760px){
  .finishEarlyCard{min-height:52px!important;padding:10px 13px!important}
  .finishEarlyCard input{
    width:60px!important;
    min-width:60px!important;
    max-width:60px!important;
    flex-basis:60px!important;
    height:34px!important;
    min-height:34px!important;
    font-size:12px!important;
  }
}
'''

if marker not in css:
    css = css.rstrip() + block + '\n'
    path.write_text(css, encoding='utf-8')
