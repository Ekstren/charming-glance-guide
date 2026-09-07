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

# EPIC_SAND_COMPACT_COMMIT_V1:
# Keep Epic/Purple Sand on exactly the same compact-number/commit path as the
# existing Basic/Rare Sand fields. Scope the check to the compact set itself;
# the same field sequence also appears in INPUT_IDS, so a whole-file `new in s`
# check can produce a false positive.
compact_start = s.find('const COMPACT_NUMBER_INPUT_IDS = new Set([')
if compact_start < 0:
    raise SystemExit('Compact-number input set not found')
compact_end = s.find(']);', compact_start)
if compact_end < 0:
    raise SystemExit('Compact-number input set terminator not found')
compact_block = s[compact_start:compact_end]
if "'sandEpicCurrent'" not in compact_block:
    old = "'sandCurrent','sandBlueCurrent','sandRate',"
    new = "'sandCurrent','sandBlueCurrent','sandEpicCurrent','sandRate',"
    if old not in compact_block:
        raise SystemExit('Sand compact-number anchor not found')
    compact_block = compact_block.replace(old, new, 1)
    s = s[:compact_start] + compact_block + s[compact_end:]
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
    print('Added/updated Epic/Purple Chrono Sand saved-material support.')
else:
    print('Epic/Purple Chrono Sand saved-material support already current.')
