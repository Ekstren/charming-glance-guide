from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
marker='/* CALC_ACTION_ROW_POLISH_V1 */'
if marker in s:
    raise SystemExit('calculator action row polish already applied')

css=r'''
<style id="calc-action-row-polish">
/* CALC_ACTION_ROW_POLISH_V1 */
.calcActions{
  display:grid!important;
  grid-template-columns:auto auto minmax(0,1fr)!important;
  align-items:center!important;
  justify-content:start!important;
  column-gap:10px!important;
  row-gap:6px!important;
  padding:2px 2px 0!important;
  margin-top:0!important;
}
.calcActions button{
  width:auto!important;
  min-width:88px;
  min-height:38px!important;
  padding:8px 14px!important;
  font-size:11px!important;
  line-height:1.2;
}
.calcActions span{
  grid-column:auto!important;
  margin-left:8px!important;
  color:var(--secondary-text)!important;
  text-align:left!important;
  font-size:10px!important;
  line-height:1.4!important;
}
@media(max-width:700px){
  .calcActions{
    grid-template-columns:1fr 1fr!important;
    gap:8px!important;
  }
  .calcActions button{width:100%!important;min-height:44px!important;font-size:12px!important}
  .calcActions span{
    grid-column:1/-1!important;
    margin-left:0!important;
    text-align:center!important;
    font-size:10px!important;
  }
}
</style>
'''
if '</head>' not in s:
    raise SystemExit('head closing tag not found')
s=s.replace('</head>',css+'\n</head>',1)
p.write_text(s,encoding='utf-8')
print('Tightened calculator action row and increased helper text size.')
# trigger
