from pathlib import Path

p=Path('index.html')
s=p.read_text()
old='''          <div class="projectionCallout projectionInline projectionGridCell"><span>Projected season-end level</span><strong id="projectedCharacter">—</strong><small id="projectionNote" hidden></small></div>'''
new='''          <label class="projectionField">Projected season-end level<input id="projectedCharacter" type="text" value="—" readonly aria-readonly="true"><small id="projectionNote" hidden></small></label>'''
if old not in s:
    raise SystemExit('projected field markup anchor missing')
s=s.replace(old,new,1)
p.write_text(s)

p=Path('assets/runtime.js')
s=p.read_text()
replacements={
    "$('projectedCharacter').textContent=`Lv.${p.level} · ${(p.pct*100).toFixed(1)}%`;":"$('projectedCharacter').value=`Lv.${p.level} · ${(p.pct*100).toFixed(1)}%`;",
    "$('projectedCharacter').textContent='Update snapshot';":"$('projectedCharacter').value='Update snapshot';",
    "$('projectedCharacter').textContent=pc;":"$('projectedCharacter').value=pc;",
}
for old,new in replacements.items():
    if old not in s:
        raise SystemExit(f'runtime anchor missing: {old}')
    s=s.replace(old,new,1)
p.write_text(s)

p=Path('scripts/site_smoke_test.mjs')
s=p.read_text()
anchor="assert(projectionGeometry, 'projection/Bed EXP geometry unavailable');"
extra="""assert(projectionGeometry, 'projection/Bed EXP geometry unavailable');
const projectedFieldKind = await page.evaluate(()=>{
  const el=document.getElementById('projectedCharacter');
  return el?{tag:el.tagName,readOnly:!!el.readOnly}:null;
});
assert(projectedFieldKind?.tag==='INPUT' && projectedFieldKind.readOnly,
  `projected season-end field must reuse the native readonly input geometry: ${JSON.stringify(projectedFieldKind)}`);"""
if anchor not in s:
    raise SystemExit('geometry regression anchor missing')
s=s.replace(anchor,extra,1)
p.write_text(s)
