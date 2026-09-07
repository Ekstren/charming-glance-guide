from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

repls = [
    (
        '<div class="resourceCard sandResourceCard"><div class="resourceCardHead"><strong>Chrono Sand</strong><small id="sandProjected">Projected: —</small></div><div class="resourceCardFields sandResourceFields"><label><span>Saved · Basic</span><input id="sandCurrent" type="number" min="0" value="0"></label><label><span>Saved · Blue</span><input id="sandBlueCurrent" type="number" min="0" step="1" value="0" title="Each Blue Sand counts as 5 Basic Chrono Sand in the planner."></label><label style="grid-column:1/-1"><span>Cart / hr · Basic</span><input id="sandRate" type="number" min="0" value="0"></label></div><small class="treatEquivalent" id="sandEquivalentNow">Saved total: — basic-equivalent</small></div>',
        '<div class="resourceCard sandResourceCard"><div class="resourceCardHead"><strong>Chrono Sand</strong><small id="sandProjected">Projected: —</small></div><div class="resourceCardFields sandResourceFields"><label><span>Saved · Basic</span><input id="sandCurrent" type="number" min="0" value="0"></label><label><span>Saved · Rare (Blue)</span><input id="sandBlueCurrent" type="number" min="0" step="1" value="0" title="Each Rare (Blue) Chrono Sand counts as 5 Basic Chrono Sand in the planner."></label><label><span>Saved · Epic (Purple)</span><input id="sandEpicCurrent" type="number" min="0" step="1" value="0" title="Each Epic (Purple) Chrono Sand counts as 25 Basic Chrono Sand in the planner."></label><label><span>Cart / hr · Basic</span><input id="sandRate" type="number" min="0" value="0"></label></div><small class="treatEquivalent" id="sandEquivalentNow">Saved total: — basic-equivalent</small></div>'
    ),
    (
        'sandCurrent:0,sandBlueCurrent:0,sandRate:800,',
        'sandCurrent:0,sandBlueCurrent:0,sandEpicCurrent:0,sandRate:800,'
    ),
    (
        "...GEAR_IDS,'oreCurrent','oreRate','essenceCurrent','essenceRate','sandCurrent','sandBlueCurrent','sandRate','treatCurrent'",
        "...GEAR_IDS,'oreCurrent','oreRate','essenceCurrent','essenceRate','sandCurrent','sandBlueCurrent','sandEpicCurrent','sandRate','treatCurrent'"
    ),
    (
        "'sandCurrent','sandBlueCurrent','sandRate',",
        "'sandCurrent','sandBlueCurrent','sandEpicCurrent','sandRate',"
    ),
    (
        "const SAND_BLUE_EQ=5;\n  function savedSandEquivalent(){\n    return Math.max(0,n('sandCurrent')) + Math.max(0,n('sandBlueCurrent'))*SAND_BLUE_EQ;\n  }",
        "const SAND_BLUE_EQ=5, SAND_EPIC_EQ=25;\n  function savedSandEquivalent(){\n    return Math.max(0,n('sandCurrent')) + Math.max(0,n('sandBlueCurrent'))*SAND_BLUE_EQ + Math.max(0,n('sandEpicCurrent'))*SAND_EPIC_EQ;\n  }"
    ),
    (
        "if(id==='sandCurrent' || id==='sandBlueCurrent') snapshotCarry.sand=0;",
        "if(id==='sandCurrent' || id==='sandBlueCurrent' || id==='sandEpicCurrent') snapshotCarry.sand=0;"
    ),
]

changed = False
for old, new in repls:
    if new in s:
        continue
    if old not in s:
        raise SystemExit(f'Expected patch anchor not found: {old[:120]!r}')
    s = s.replace(old, new, 1)
    changed = True

marker = 'EPIC_CHRONO_SAND_SAVED_V1'
if marker not in s:
    anchor = '  const SAND_BLUE_EQ=5, SAND_EPIC_EQ=25;'
    if anchor not in s:
        raise SystemExit('Epic sand conversion anchor missing after patch')
    s = s.replace(anchor, f'  /* {marker}: Rare/Blue = 5 Basic; Epic/Purple = 25 Basic. Shop average stays unchanged until an Epic shop roll is observed. */\n{anchor}', 1)
    changed = True

if changed:
    p.write_text(s, encoding='utf-8')
    print('Added Epic/Purple Chrono Sand saved-material support.')
else:
    print('Epic/Purple Chrono Sand saved-material support already current.')
