from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
marker='RESOURCE_TOOL_CARD_SPACING_V2'
if marker in s:
    print('already applied')
    raise SystemExit(0)

css=r'''
<style id="resource-tool-card-spacing-v2">
/* RESOURCE_TOOL_CARD_SPACING_V2
   Joined raw/tool balances should read as one compact inset card. The older raw
   balance min-height was useful for standalone cards, but creates dead space when
   a Realm-tool section is attached beneath it. */
.planCosts small.rawRemaining:has(+ small.toolBalance:not([hidden])){
  min-height:0!important;
  margin-top:5px!important;
  padding:9px 10px 7px!important;
  border-bottom:0!important;
  border-radius:10px 10px 0 0!important;
}
.planCosts small.rawRemaining:has(+ small.toolBalance:not([hidden])) .resourceRemainingLine{
  line-height:1.35!important;
}
.planCosts small.rawRemaining:has(+ small.toolBalance:not([hidden])) .reserveRequirementLine{
  margin-top:1px!important;
  padding-top:0!important;
  border-top:0!important;
  line-height:1.35!important;
}
.planCosts small.rawRemaining + small.toolBalance:not([hidden]){
  min-height:0!important;
  margin:0!important;
  padding:7px 10px 8px!important;
  border:1px solid var(--line)!important;
  border-top:1px solid var(--line)!important;
  border-radius:0 0 10px 10px!important;
  background:color-mix(in srgb,var(--surface) 84%,var(--bg) 16%)!important;
  box-shadow:none!important;
  gap:2px!important;
}
.planCosts small.rawRemaining + small.toolBalance:not([hidden]) .toolSimpleLine{
  min-height:0!important;
  line-height:1.3!important;
}
.planCosts small.rawRemaining + small.toolBalance:not([hidden]) .toolSimpleLine i,
.planCosts small.rawRemaining + small.toolBalance:not([hidden]) .toolSimpleLine b{
  line-height:1.3!important;
}

/* Keep the parent card rhythm tight and consistent after joining the two inset halves. */
.planCosts>span:has(> small.rawRemaining + small.toolBalance:not([hidden])){
  gap:5px!important;
}

@media(max-width:700px){
  .planCosts small.rawRemaining:has(+ small.toolBalance:not([hidden])){
    min-height:0!important;
    padding:9px 10px 7px!important;
  }
  .planCosts small.rawRemaining + small.toolBalance:not([hidden]){
    padding:7px 10px 8px!important;
  }
}
</style>
'''

if '</head>' not in s:
    raise SystemExit('</head> not found')
s=s.replace('</head>',css+'\n</head>',1)
p.write_text(s,encoding='utf-8')
print('tightened joined raw/tool resource card spacing')
