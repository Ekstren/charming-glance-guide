from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
marker='RESOURCE_TOOL_CARD_SEAM_V3'
if marker in s:
    print('already applied')
    raise SystemExit(0)

css=r'''
<style id="resource-tool-card-seam-v3">
/* RESOURCE_TOOL_CARD_SEAM_V3
   The raw and Realm-tool halves are separate grid items. The parent keeps a 5px row
   gap for the title/amount rhythm, so cancel that gap only at the raw -> tool seam. */
.planCosts small.rawRemaining + small.toolBalance:not([hidden]){
  margin-top:-5px!important;
  width:100%!important;
  box-sizing:border-box!important;
}
/* Keep the seam as one deliberate divider, with no exposed background between side borders. */
.planCosts small.rawRemaining:has(+ small.toolBalance:not([hidden])){
  position:relative;
  z-index:1;
}
.planCosts small.rawRemaining + small.toolBalance:not([hidden]){
  position:relative;
  z-index:2;
}
@media(max-width:700px){
  .planCosts small.rawRemaining + small.toolBalance:not([hidden]){margin-top:-5px!important}
}
</style>
'''

if '</head>' not in s:
    raise SystemExit('</head> not found')
s=s.replace('</head>',css+'\n</head>',1)
p.write_text(s,encoding='utf-8')
print('removed joined resource-card seam gap')
