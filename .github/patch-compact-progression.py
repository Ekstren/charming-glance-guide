from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
marker='COMPACT_PROGRESSION_TOP_V1'
if marker in s:
    print('already applied')
    raise SystemExit(0)

# Remove the standalone current-levels card entirely. Materials/Cart stays its own card.
start=s.find('      <details id="currentLevelsDetails" class="calcPanel currentLevelsPanel">')
end=s.find('      <details id="materialsDetails"', start)
if start < 0 or end < 0:
    raise SystemExit('current levels/materials boundary not found')
s=s[:start]+s[end:]

# Merge progression inputs into the primary top calculator card, immediately after the main character inputs.
insert_before='        <div class="projectionCallout projectionInline">'
if insert_before not in s:
    raise SystemExit('projection insertion marker not found')
compact='''        <!-- COMPACT_PROGRESSION_TOP_V1 -->
        <div class="compactProgression" aria-label="Current progression used by the optimizer">
          <div class="calcGrid currentProgressGrid">
            <label>Average Skill level<input id="skillLevel" type="number" step="0.125" value="100"></label>
            <label>Average Relic level<input id="relicLevel" min="10" type="number" step="0.05" value="10"></label>
            <label>Average Fantomon level<input id="fantomonLevel" min="100" type="number" step="0.25" value="100"></label>
          </div>
          <div class="calcGrid gearFields">
            <label>Weapon<input id="gearWeapon" type="number" value="100"></label>
            <label>Off-hand<input id="gearOffhand" type="number" value="100"></label>
            <label>Helmet<input id="gearHelmet" type="number" value="100"></label>
            <label>Armor<input id="gearArmor" type="number" value="100"></label>
            <label>Boots<input id="gearBoots" type="number" value="100"></label>
          </div>
          <details class="exactInputs progressionExactInputs compactExactInputs">
            <summary><span>Exact slot levels</span><small>Optional · overrides averages</small></summary>
            <div class="exactInputsBody exactProgressGrid">
              <label>Skills · 8 slots<input id="exactSkillLevels" type="text" placeholder="Example: 7x130, 1x129"></label>
              <label>Relics · 20 slots<input id="exactRelicLevels" type="text" placeholder="Example: 13x14, 7x13"></label>
              <label>Fantomons · 4 slots<input id="exactFantoLevels" type="text" placeholder="Example: 2x136, 2x135"></label>
              <small id="exactProgressStatus">Leave blank to keep using the balanced average model.</small>
            </div>
          </details>
        </div>
'''
s=s.replace(insert_before, compact+insert_before, 1)

# Compact styling: one card for goal/current progression, no redundant title/note/card chrome.
css='''\n<style id="compact-progression-top-v1">\n/* COMPACT_PROGRESSION_TOP_V1 */\n.compactProgression{border-top:1px solid var(--line);margin-top:11px;padding-top:10px}\n.compactProgression .currentProgressGrid{margin:0 0 7px;gap:7px}\n.compactProgression .gearFields{gap:7px}\n.compactProgression .calcGrid label{gap:4px;font-size:8px}\n.compactProgression .calcGrid input{min-height:36px;padding:6px 9px;font-size:13px}\n.compactProgression .exactInputs{margin-top:7px}\n.compactProgression .exactInputs>summary{padding:8px 10px;font-size:9px}\n.compactProgression .exactInputsBody{padding:10px}\n.compactProgression .exactInputsBody input{min-height:36px;margin-top:4px;padding:6px 8px}\n@media(max-width:700px){.compactProgression .currentProgressGrid{grid-template-columns:repeat(3,minmax(0,1fr))}.compactProgression .gearFields{grid-template-columns:repeat(5,minmax(0,1fr))}.compactProgression .calcGrid input{font-size:12px;padding:6px}}\n@media(max-width:560px){.compactProgression .currentProgressGrid{grid-template-columns:1fr 1fr}.compactProgression .gearFields{grid-template-columns:repeat(2,minmax(0,1fr))}}\n</style>\n'''
if '</head>' not in s:
    raise SystemExit('head close not found')
s=s.replace('</head>', css+'</head>', 1)

# Gear is always available to the optimizer now. Ignore any old saved lock state and remove the dead UI hook.
s=s.replace("const PANEL_OPEN_IDS = ['currentLevelsDetails','materialsDetails'];", "const PANEL_OPEN_IDS = ['materialsDetails'];")
s=s.replace('      gearLocked = !!state.gearLocked;', '      gearLocked = false; // gear lock UI removed; optimizer always considers Gear')
s=s.replace("    $('gearLockButton').addEventListener('click',()=>{gearLocked=!gearLocked;resetMaxAchievableUi();markManualSnapshot('gearLocked');updateGearLockUI();scheduleCalculatorUpdate(0);});\n", '')
s=s.replace("      `Gear lock: ${gearLocked?'ON':'OFF'}`,\n", '')
s=s.replace(" It never asks you to track a fiddly multi-resource split. <b>Gear Lock</b> removes new Gear levels from consideration. The optimizer otherwise uses one consistent acquisition-efficient, raw-first policy so the same inputs always produce the same resource strategy.", " It never asks you to track a fiddly multi-resource split. The optimizer uses one consistent acquisition-efficient, raw-first policy and always considers Gear alongside Skills, Relics and Fantomons.")

# The old standalone-card summary no longer exists; keep this update safe for older cached markup.
s=s.replace("    $('levelSummary').textContent=`Skills ${formatAverage(skill)} · Relics +${formatAverage(relic)} · Fantomons ${formatAverage(fanto)} · Gear avg ${(gear.reduce((a,b)=>a+b,0)/5).toFixed(0)}`;", "    if($('levelSummary')) $('levelSummary').textContent=`Skills ${formatAverage(skill)} · Relics +${formatAverage(relic)} · Fantomons ${formatAverage(fanto)} · Gear avg ${(gear.reduce((a,b)=>a+b,0)/5).toFixed(0)}`;")

p.write_text(s,encoding='utf-8')
print('patched compact progression into top card')
