from pathlib import Path

runtime = Path('assets/runtime.js')
rt = runtime.read_text(encoding='utf-8')
old = 'Max reached for current purchase plan. To finish earlier, increase Material Realm purchases per day.'
new = 'Current purchase plan sets this Max. Increase Material Realm purchases/day to finish earlier.'
if old not in rt:
    raise SystemExit('Finish Early helper wording not found')
rt = rt.replace(old, new)
runtime.write_text(rt, encoding='utf-8')

css = Path('assets/site.css')
ct = css.read_text(encoding='utf-8')
marker = '/* FINISH_EARLY_MAX_HINT_POLISH_V1 */'
if marker not in ct:
    ct += r'''

/* FINISH_EARLY_MAX_HINT_POLISH_V1 */
.finishEarlyMaxHint{
  width:fit-content!important;
  max-width:min(430px,100%)!important;
  margin:6px 0 10px auto!important;
  padding:8px 11px!important;
  border:1px solid color-mix(in srgb,var(--gold) 42%,var(--line))!important;
  border-radius:9px!important;
  background:color-mix(in srgb,var(--gold) 8%,var(--bg))!important;
  color:var(--body-text)!important;
  font-size:9px!important;
  font-weight:700!important;
  line-height:1.35!important;
  text-align:left!important;
  display:flex!important;
  align-items:flex-start!important;
  gap:8px!important;
  box-shadow:inset 3px 0 0 color-mix(in srgb,var(--gold) 65%,transparent)!important;
}
.finishEarlyMaxHint::before{
  content:'!';
  flex:0 0 17px;
  width:17px;
  height:17px;
  border-radius:50%;
  display:grid;
  place-items:center;
  margin-top:0;
  background:color-mix(in srgb,var(--gold) 16%,transparent);
  color:var(--gold);
  font-size:10px;
  font-weight:900;
  line-height:1;
}
.finishEarlyMaxHint[hidden]{display:none!important}
@media(max-width:700px){
  .finishEarlyMaxHint{
    width:100%!important;
    max-width:none!important;
    margin:5px 0 9px!important;
    font-size:9px!important;
  }
}
'''
css.write_text(ct, encoding='utf-8')
print('Polished Finish Early Max helper.')
