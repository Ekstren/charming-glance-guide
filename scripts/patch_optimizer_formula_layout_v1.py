from pathlib import Path
import re

index = Path('index.html')
s = index.read_text()

pattern = r'''\n\s*<details class="optimizerExplain" id="optimizerExplain">\s*<summary><span>How the optimizer decides</span><small>Best overall acquisition efficiency</small></summary>\s*<div class="optimizerExplainBody">(.*?)</div>\s*</details>'''
m = re.search(pattern, s, re.S)
if not m:
    raise SystemExit('optimizer explanation block not found')
body = m.group(1).strip()
s = s[:m.start()] + '\n' + s[m.end():]

anchor = '<details class="methodPanel"><summary>Formula and source checks</summary><div>'
if anchor not in s:
    raise SystemExit('Formula and source checks anchor missing')
embedded = '''<details class="methodPanel"><summary>Formula and source checks</summary><div>\n<section class="optimizerExplainEmbedded" id="optimizerExplain">\n  <div class="optimizerExplainEmbeddedHead"><h3>How the optimizer decides</h3><small>Best overall acquisition efficiency</small></div>\n  <div class="optimizerExplainBody">\n''' + body + '''\n  </div>\n</section>'''
s = s.replace(anchor, embedded, 1)
index.write_text(s)

css_path = Path('assets/site.css')
css = css_path.read_text()
marker = '/* OPTIMIZER_IN_FORMULA_PANEL_V1 */'
if marker in css:
    raise SystemExit('optimizer/formula layout style already present')
css += '''\n\n/* OPTIMIZER_IN_FORMULA_PANEL_V1
   Keep the Character editor focused on inputs; explanatory optimizer copy belongs
   with the calculator formula/source reference below the result layout. */
.optimizerExplainEmbedded{
  border-bottom:1px solid var(--line);
  margin:0 0 13px;
  padding:0 0 13px;
}
.optimizerExplainEmbeddedHead{
  display:flex;
  align-items:baseline;
  justify-content:space-between;
  gap:14px;
  margin-bottom:8px;
}
.optimizerExplainEmbeddedHead h3{
  margin:0;
  color:var(--ink);
  font-size:11px;
  font-weight:850;
}
.optimizerExplainEmbeddedHead small{
  color:var(--muted);
  font-size:9px;
  text-align:right;
}
.optimizerExplainEmbedded .optimizerExplainBody{
  border-top:0;
  padding:0;
  gap:7px;
}
@media(max-width:700px){
  .optimizerExplainEmbeddedHead{align-items:flex-start;flex-direction:column;gap:2px}
  .optimizerExplainEmbeddedHead small{font-size:9px;text-align:left}
}

/* PROJECTION_FIELD_EQUAL_HEIGHT_V2
   Match the projected season-end readout to the neighboring calculator inputs. */
.projectionCallout.projectionInline.projectionGridCell>strong{
  min-height:42px!important;
  height:42px!important;
  border-radius:9px!important;
  padding:8px 10px!important;
  box-sizing:border-box!important;
}
@media(max-width:760px){
  .projectionCallout.projectionInline.projectionGridCell>strong{
    min-height:44px!important;
    height:44px!important;
  }
}
'''
css_path.write_text(css)

# Structural guards.
s = index.read_text()
top = s.index('<details id="characterDetails"')
method = s.index('<details class="methodPanel">')
character = s[top:method]
assert 'How the optimizer decides' not in character
method_block = s[method:]
assert '<section class="optimizerExplainEmbedded" id="optimizerExplain">' in method_block
assert method_block.index('How the optimizer decides') < method_block.index('<b>Season 1 carry-forward:')
print('optimizer explanation moved into Formula and source checks; projection height matched')
