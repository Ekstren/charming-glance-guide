from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')
marker = 'RESULT_BORDER_STATE_V1'
if marker in text:
    print('Result border state styling already applied.')
    raise SystemExit(0)

style = r'''
<style id="result-border-state-v1">
/* RESULT_BORDER_STATE_V1
   Outer season-end result card follows the same semantic state as the status message:
   success = green, caution = yellow, unachievable = red. */
.calcResults:has(#targetMessage.caution):not(:has(#targetMessage.danger)){
  border-color:var(--status-warning)!important;
}
.calcResults:has(#targetMessage.danger),
.calcResults:has(#targetStatus.notMet){
  border-color:var(--status-negative)!important;
}
</style>
'''

if '</head>' not in text:
    raise SystemExit('Could not find </head>')
text = text.replace('</head>', style + '\n</head>', 1)
path.write_text(text, encoding='utf-8')
print('Applied yellow caution and red unachievable borders to calcResults.')
