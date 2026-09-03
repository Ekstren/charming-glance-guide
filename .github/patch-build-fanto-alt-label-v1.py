from pathlib import Path

paths=[Path('index.html'),Path('.github/build-fantomons-inject.html')]
old="const labels=['Main','Alt','F2P / No Shop'];"
new="const labels=['Main','Alt','Alt'];"
for path in paths:
    text=path.read_text(encoding='utf-8')
    if text.count(old)!=1:
        raise SystemExit(f'{path}: label match count {text.count(old)}')
    text=text.replace(old,new,1)
    path.write_text(text,encoding='utf-8')

smoke=Path('scripts/site_smoke_test.mjs')
text=smoke.read_text(encoding='utf-8')
text=text.replace('loadouts, and Main+Alt+F2P Fantomon cards. Lock all of that in so it cannot silently','loadouts, and Main+two-Alt Fantomon cards. Lock all of that in so it cannot silently',1)
old_block="""  const f2pLabels=await visibleCards.locator('.fantomonPick small').allTextContents();\n  assert(f2pLabels.some(x=>/F2P \/ No Shop/i.test(x)), `${cls} visible build is missing the F2P / No Shop Fantomon label`);\n  const f2pName=await visibleCards.locator('.fantomonPick').nth(2).locator('b').innerText();\n  assert(!['Nyxarchon','Aegiswing'].includes(f2pName.trim()), `${cls} F2P / No Shop pick incorrectly uses shop Fantomon ${f2pName}`);\n"""
new_block="""  const fantoLabels=await visibleCards.locator('.fantomonPick small').allTextContents();\n  assert(fantoLabels.length===3 && /^main$/i.test(fantoLabels[0]) && /^alt$/i.test(fantoLabels[1]) && /^alt$/i.test(fantoLabels[2]), `${cls} Fantomon labels should be Main / Alt / Alt: ${fantoLabels.join(' | ')}`);\n  const thirdAltName=await visibleCards.locator('.fantomonPick').nth(2).locator('b').innerText();\n  assert(!['Nyxarchon','Aegiswing'].includes(thirdAltName.trim()), `${cls} third Alt incorrectly uses shop Fantomon ${thirdAltName}`);\n"""
if text.count(old_block)!=1:
    raise SystemExit(f'smoke label block match count {text.count(old_block)}')
text=text.replace(old_block,new_block,1)
text=text.replace('Main/Alt/F2P Fantomons + Dominator roles/PvP refs + mobile stack','Main/two-Alt Fantomons + Dominator roles/PvP refs + mobile stack',1)
smoke.write_text(text,encoding='utf-8')
print('renamed third Fantomon recommendation to Alt')
