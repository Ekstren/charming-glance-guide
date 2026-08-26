from pathlib import Path

p = Path('index.html')
s = p.read_text()

# Add a visible saved Blue Sand input beside normal Chrono Sand. Relic costs in the
# planner are normalized to basic/white-sand equivalent, and existing cost comments
# already establish 1 Blue = 5 basic (e.g. 3,200 Blue = 16,000 basic).
if 'id="sandBlueCurrent"' not in s:
    old = '<div class="resourceCard"><div class="resourceCardHead"><strong>Chrono Sand</strong><small id="sandProjected">Projected: —</small></div><div class="resourceCardFields"><label><span>Saved</span><input id="sandCurrent" type="number" value="0"></label><label><span>Cart / hr</span><input id="sandRate" type="number" value="0"></label></div></div>'
    new = '<div class="resourceCard sandResourceCard"><div class="resourceCardHead"><strong>Chrono Sand</strong><small id="sandProjected">Projected: —</small></div><div class="resourceCardFields sandResourceFields"><label><span>Saved · Basic</span><input id="sandCurrent" type="number" min="0" value="0"></label><label><span>Saved · Blue ×5</span><input id="sandBlueCurrent" type="number" min="0" step="1" value="0" title="Each Blue Sand counts as 5 Basic Chrono Sand in the planner."></label><label style="grid-column:1/-1"><span>Cart / hr · Basic</span><input id="sandRate" type="number" min="0" value="0"></label></div><small class="treatEquivalent" id="sandEquivalentNow">Saved total: — basic-equivalent</small></div>'
    if old not in s:
        raise SystemExit('Could not locate Chrono Sand resource card')
    s = s.replace(old, new, 1)

# Persist/reset the new input with the rest of the calculator state. Target the input
# list specifically so the Cart snapshot-aging tuple remains Basic Sand + sandRate.
old_inputs = "...GEAR_IDS,'oreCurrent','oreRate','essenceCurrent','essenceRate','sandCurrent','sandRate','treatCurrent'"
new_inputs = "...GEAR_IDS,'oreCurrent','oreRate','essenceCurrent','essenceRate','sandCurrent','sandBlueCurrent','sandRate','treatCurrent'"
if old_inputs in s:
    s = s.replace(old_inputs, new_inputs, 1)

# Repair the malformed tuple from the initial Blue Sand patch if it is present.
s = s.replace("['sandCurrent','sandBlueCurrent','sandRate','sand'],", "['sandCurrent','sandRate','sand'],")

s = s.replace("sandCurrent:0,sandRate:0", "sandCurrent:0,sandBlueCurrent:0,sandRate:0")
s = s.replace("if(id==='sandCurrent') snapshotCarry.sand=0;", "if(id==='sandCurrent' || id==='sandBlueCurrent') snapshotCarry.sand=0;")

# Convert Blue Sand to the planner's existing basic/white-sand equivalent before all
# reserve, shortfall, Material Realm, and relic-cost calculations.
if 'const SAND_BLUE_EQ=5;' not in s:
    needle = "  const TREAT_BASIC_EXP=50, TREAT_PREMIUM_EQ=8, TREAT_DELUXE_EQ=40;"
    replacement = "  const SAND_BLUE_EQ=5;\n  function savedSandEquivalent(){\n    return Math.max(0,n('sandCurrent')) + Math.max(0,n('sandBlueCurrent'))*SAND_BLUE_EQ;\n  }\n  const TREAT_BASIC_EXP=50, TREAT_PREMIUM_EQ=8, TREAT_DELUXE_EQ=40;"
    if needle not in s:
        raise SystemExit('Could not locate treat-equivalent constants')
    s = s.replace(needle, replacement, 1)

s = s.replace("sand:Math.max(0,n('sandCurrent'))+Math.max(0,n('sandRate'))*resourceHours,", "sand:savedSandEquivalent()+Math.max(0,n('sandRate'))*resourceHours,")

# Make the conversion visible so the user can verify that Blue Sand was counted.
projection = "    $('sandProjected').textContent=`Projected: ${fmtCompact(displayedSand)}${sandStam}${sandReserveSuffix}`;"
if "id=\"sandEquivalentNow\"" in s and "savedSandEq=savedSandEquivalent" not in s:
    replacement = projection + "\n    const savedSandEq=savedSandEquivalent();\n    if($('sandEquivalentNow')) $('sandEquivalentNow').textContent=`Saved total: ${fmtCompact(savedSandEq)} basic-equivalent · Blue counts ×${SAND_BLUE_EQ}`;"
    if projection not in s:
        raise SystemExit('Could not locate sand projection renderer')
    s = s.replace(projection, replacement, 1)

p.write_text(s)
