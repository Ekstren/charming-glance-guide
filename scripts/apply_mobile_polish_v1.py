from pathlib import Path

css=Path('assets/site.css')
s=css.read_text()
marker='MOBILE_POLISH_V1'
block=r'''

/* MOBILE_POLISH_V1
   Phone/tablet touch-target and density pass. Desktop geometry remains unchanged. */
@media (max-width:900px){
  .sectionSwitch{
    display:grid!important;
    grid-template-columns:repeat(4,minmax(0,1fr))!important;
    gap:4px!important;
    margin:10px 8px 0!important;
    padding:4px!important;
  }
  .sectionSwitch>button[data-section]{
    min-width:0!important;
    min-height:44px!important;
    padding:6px 3px!important;
    font-size:10px!important;
    line-height:1.15!important;
    white-space:normal!important;
  }
  #timelineFilters button{min-height:40px!important;padding-block:8px!important}
  .classTabs button{min-height:44px!important;padding:9px 8px!important}
  #buildContent .metaBuildTabs button{min-height:42px!important;padding-block:8px!important}
  #staminaMode{min-height:44px!important}
}
@media (max-width:600px){
  .classTabs{
    display:grid!important;
    grid-template-columns:repeat(2,minmax(0,1fr))!important;
    gap:6px!important;
  }
  .classTabs button{width:100%!important;min-width:0!important}
}
@media (max-width:430px){
  .topbar{padding-inline:12px!important}
  .sectionSwitch{margin-top:8px!important}
  .calculator,.builds,.companions{padding-inline:12px!important}
  .calcPanel{border-radius:14px!important}
  .currentLevelsBody{padding-inline:12px!important}
  .calcGrid input,.calcGrid select{height:44px!important;min-height:44px!important}
  #staminaMode{height:44px!important}
}
'''
if marker not in s:
    css.write_text(s+block)

audit=Path('scripts/mobile_audit_v1.mjs')
a=audit.read_text()
a=a.replace("nav.forEach(b=>assert(b.h>=40,`w${width}: top nav ${b.text} tap target only ${b.h}px`));",
            "nav.forEach(b=>assert(b.h>=44,`w${width}: top nav ${b.text} tap target only ${b.h}px`));\n  if(width<=430) assert(base.nav<=62,`w${width}: top navigation still consumes ${base.nav}px vertically`);")
a=a.replace("assert(timeline.groups>0,`w${width}: Timeline did not render`);",
            "assert(timeline.groups>0,`w${width}: Timeline did not render`);\n  timeline.filters.forEach((b,i)=>assert(b.h>=40,`w${width}: timeline filter ${i+1} only ${b.h}px tall`));")
a=a.replace("return {text:x.textContent.trim(),w:r.width,h:r.height}","return {text:x.textContent.trim(),w:r.width,h:r.height,x:r.x,y:r.y}")
a=a.replace("buildMetrics.classTabs.forEach(b=>assert(b.h>=38,`w${width}: Builds class tab ${b.text} only ${b.h}px tall`));",
            "buildMetrics.classTabs.forEach(b=>assert(b.h>=44,`w${width}: Builds class tab ${b.text} only ${b.h}px tall`));\n  buildMetrics.scenarioTabs.forEach(b=>assert(b.h>=40,`w${width}: Builds scenario tab ${b.text} only ${b.h}px tall`));\n  if(width<=600 && buildMetrics.classTabs.length===4){\n    const rows=[...new Set(buildMetrics.classTabs.map(b=>Math.round(b.y)))];\n    assert(rows.length===2,`w${width}: Builds class tabs should be a compact 2x2 grid, found ${rows.length} rows`);\n  }")
a=a.replace("assert(companions.overflow<=1,`w${width}: Companions overflows by ${companions.overflow}px`);",
            "assert(companions.overflow<=1,`w${width}: Companions overflows by ${companions.overflow}px`);\n  companions.buttons.forEach(b=>assert(b.h>=44,`w${width}: Companion class tab ${b.text} only ${b.h}px tall`));")
audit.write_text(a)

ci=Path('.github/workflows/site-ci.yml')
c=ci.read_text()
if 'Mobile layout regression' not in c:
    anchor='      - name: Full browser smoke\n        run: node scripts/site_smoke_test.mjs\n'
    extra=anchor+'      - name: Mobile layout regression\n        run: node scripts/mobile_audit_v1.mjs\n'
    if anchor not in c:
        raise SystemExit('Site CI smoke anchor missing')
    ci.write_text(c.replace(anchor,extra,1))
