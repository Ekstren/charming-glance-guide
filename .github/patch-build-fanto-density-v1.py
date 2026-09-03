from pathlib import Path

paths=[Path('index.html'),Path('.github/build-fantomons-inject.html')]
anchor="""@media(max-width:620px){.buildCard .fantomonRankList{grid-template-columns:1fr}}\n"""
insert="""@media(min-width:1180px){\n  .builds .buildGrid.metaModeGrid>.buildCard:not([hidden])>.fantomonPair .fantomonRankList{grid-template-columns:repeat(2,minmax(0,1fr))}\n  .builds .buildGrid.metaModeGrid>.buildCard:not([hidden])>.fantomonPair .fantomonPick.main{grid-column:1/-1}\n}\n"""

for path in paths:
    text=path.read_text(encoding='utf-8')
    if text.count(insert):
        raise SystemExit(f'{path}: density CSS already present')
    if text.count(anchor)!=1:
        raise SystemExit(f'{path}: anchor match count {text.count(anchor)}')
    text=text.replace(anchor,anchor+insert,1)
    path.write_text(text,encoding='utf-8')

smoke=Path('scripts/site_smoke_test.mjs')
text=smoke.read_text(encoding='utf-8')
needle="""  const cardCols=await visibleCards.evaluate(el=>{const left=el.querySelector('.buildLoadoutColumn')?.getBoundingClientRect();const right=el.querySelector('.fantomonPair')?.getBoundingClientRect();return left&&right?{lx:left.x,ly:left.y,rx:right.x,ry:right.y}:null;});\n  assert(cardCols && cardCols.rx>cardCols.lx+20 && Math.abs(cardCols.ry-cardCols.ly)<30, `${cls} desktop loadout/Fantomon columns are not side-by-side`);\n"""
extra="""  const fantoLayout=await visibleCards.locator('.fantomonRankList').evaluate(el=>({cols:getComputedStyle(el).gridTemplateColumns,items:[...el.querySelectorAll('.fantomonPick')].map(x=>{const r=x.getBoundingClientRect();return {x:r.x,y:r.y,w:r.width};})}));\n  assert(fantoLayout.items.length===3, `${cls} wide desktop Fantomon list lost a choice`);\n  assert(fantoLayout.cols.split(' ').length===2, `${cls} wide desktop Fantomon list is not two columns: ${fantoLayout.cols}`);\n  assert(Math.abs(fantoLayout.items[1].y-fantoLayout.items[2].y)<3 && fantoLayout.items[2].x>fantoLayout.items[1].x, `${cls} Alt/F2P Fantomons are not side-by-side`);\n  assert(fantoLayout.items[0].w>fantoLayout.items[1].w*1.8, `${cls} Main Fantomon does not span both columns`);\n"""
if text.count(needle)!=1:
    raise SystemExit(f'smoke desktop anchor match count {text.count(needle)}')
text=text.replace(needle,needle+extra,1)
smoke.write_text(text,encoding='utf-8')
print('compacted wide-desktop Fantomon cards')
