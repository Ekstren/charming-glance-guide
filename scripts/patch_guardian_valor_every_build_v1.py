from pathlib import Path
import re

TARGETS = [
    Path('index.html'),
    Path('scripts/patch_meta_build_modes_v1.py'),
    Path('scripts/patch_guardian_tank_dps_toggle_v1.py'),
]

TECH_REPLACEMENTS = {
    "['Luminous Shield','Forceful Charge','Star Shattering Slash','Desperate Protection']":
        "['Valor Surge','Luminous Shield','Star Shattering Slash','Desperate Protection']",
    "['Swirling Blade','Lunarwater Threads','Seismic Tide','Raging Maelstrom']":
        "['Valor Surge','Swirling Blade','Lunarwater Threads','Raging Maelstrom']",
    "['Swirling Blade','Lunarwater Threads','Seismic Tide','Star Shattering Slash']":
        "['Valor Surge','Swirling Blade','Lunarwater Threads','Star Shattering Slash']",
    "['Swirling Blade','Luminous Shield','Forceful Charge','Star Shattering Slash']":
        "['Valor Surge','Swirling Blade','Luminous Shield','Star Shattering Slash']",
}

TEXT_REPLACEMENTS = {
    # Live Guardian descriptions: keep the copy aligned with the new four-slot bars.
    "Need more Taunt: Valor Surge → Hamper Strike.":
        "Need more Taunt: Desperate Protection → Hamper Strike when survival is already stable.",
    "Forceful Charge maintains contact and Star Shattering Slash supplies kill pressure while Luminous Shield and Desperate Protection cover burst windows.":
        "Valor Surge keeps the damage buff and cleanse online while Star Shattering Slash supplies kill pressure; Luminous Shield and Desperate Protection cover burst windows.",
    "Swirling Blade, Lunarwater Threads, Seismic Tide, and Raging Maelstrom stack Cold and spread Water AoE quickly.":
        "Valor Surge keeps the damage buff and cleanse online while Swirling Blade, Lunarwater Threads, and Raging Maelstrom handle Water/Cold AoE pressure.",
    "Swirling Blade, Lunarwater Threads, and Seismic Tide maintain Cold while Star Shattering Slash delivers the heavy single-target hit.":
        "Valor Surge keeps the damage buff active while Swirling Blade + Lunarwater Threads maintain Water/Cold pressure and Star Shattering Slash delivers the heavy single-target hit.",
    "Swirling Blade and Forceful Charge keep pressure on the target while Star Shattering Slash supplies the finisher and Luminous Shield preserves bruiser durability.":
        "Valor Surge keeps its buff and cleanse active while Swirling Blade + Star Shattering Slash supply kill pressure and Luminous Shield preserves bruiser durability.",
    "Swirling Blade, Forceful Charge, and Star Shattering Slash create kill pressure while Luminous Shield helps survive focus.":
        "Valor Surge buffs and cleanses the duo while Swirling Blade + Star Shattering Slash create kill pressure and Luminous Shield helps survive focus.",
    "Swirling Blade, Lunarwater Threads, Seismic Tide, and Raging Maelstrom spread Cold and Water AoE across the enemy team.":
        "Valor Surge buffs and cleanses the team while Swirling Blade, Lunarwater Threads, and Raging Maelstrom spread Water/Cold pressure across the enemy team.",
    "The Water/Cold package clears dense floors while Swirling Blade adds its own shield.":
        "Valor Surge stays locked in for the buff/cleanse while Swirling Blade, Lunarwater Threads, and Raging Maelstrom clear dense Water/Cold floors.",
    "Forceful Charge keeps contact and Star Shattering Slash gives the tank setup a real finisher.":
        "Valor Surge keeps the buff/cleanse online and Star Shattering Slash gives the tank setup a real finisher.",
    # Conditional swaps must not recommend removing Valor.
    "['Need more Taunt','Valor Surge','Hamper Strike']":
        "['Need more Taunt','Desperate Protection','Hamper Strike']",
    "'Arena · Tank|Luminous Shield|Forceful Charge|Star Shattering Slash|Desperate Protection'":
        "'Arena · Tank|Valor Surge|Luminous Shield|Star Shattering Slash|Desperate Protection'",
    "['Need cleanse + damage buff','Forceful Charge','Valor Surge']":
        "['Need more mobility','Star Shattering Slash','Forceful Charge']",
    "'Dungeon · DPS|Swirling Blade|Lunarwater Threads|Seismic Tide|Raging Maelstrom'":
        "'Dungeon · DPS|Valor Surge|Swirling Blade|Lunarwater Threads|Raging Maelstrom'",
    "'Crucible / Conquest · DPS|Swirling Blade|Lunarwater Threads|Seismic Tide|Star Shattering Slash'":
        "'Crucible / Conquest · DPS|Valor Surge|Swirling Blade|Lunarwater Threads|Star Shattering Slash'",
    "'Arena · DPS|Swirling Blade|Luminous Shield|Forceful Charge|Star Shattering Slash'":
        "'Arena · DPS|Valor Surge|Swirling Blade|Luminous Shield|Star Shattering Slash'",
    "['Need cleanse + damage buff','Forceful Charge','Valor Surge']":
        "['Need more mobility','Star Shattering Slash','Forceful Charge']",
    "'Tournament · 2v2 · DPS|Swirling Blade|Luminous Shield|Forceful Charge|Star Shattering Slash'":
        "'Tournament · 2v2 · DPS|Valor Surge|Swirling Blade|Luminous Shield|Star Shattering Slash'",
    "['Need cleanse + duo buff','Forceful Charge','Valor Surge']":
        "['Need more mobility','Star Shattering Slash','Forceful Charge']",
    "'Fantasia Ascent · Tank|Luminous Shield|Forceful Charge|Star Shattering Slash|Desperate Protection'":
        "'Fantasia Ascent · Tank|Valor Surge|Luminous Shield|Star Shattering Slash|Desperate Protection'",
    "'Fantasia Ascent · DPS|Swirling Blade|Lunarwater Threads|Seismic Tide|Raging Maelstrom'":
        "'Fantasia Ascent · DPS|Valor Surge|Swirling Blade|Lunarwater Threads|Raging Maelstrom'",
    # Tooltip policy: Valor is no longer the flex-out slot.
    "'Pre-cast support for Dungeon and boss teams; flex it out when you need more Taunt.'":
        "'Universal Guardian slot: keep it equipped for the team damage buff and cleanse; flex another Technique when you need more Taunt.'",
}

HTML_REPLACEMENTS = {
    # Old fallback Guardian cards should obey the same rule if the richer runtime ever fails.
    '<div><b>Swirling Blade</b><b>Lunarwater Threads</b><b>Seismic Tide</b><b>Raging Maelstrom</b></div>':
        '<div><b>Valor Surge</b><b>Swirling Blade</b><b>Lunarwater Threads</b><b>Raging Maelstrom</b></div>',
    '<div><b>Desperate Protection</b><b>Luminous Shield</b><b>Forceful Charge</b><b>Star Shattering Slash</b></div>':
        '<div><b>Valor Surge</b><b>Luminous Shield</b><b>Star Shattering Slash</b><b>Desperate Protection</b></div>',
    '<li><b>Defensive:</b> Valor Surge → Hamper Strike for more taunt uptime</li>':
        '<li><b>Defensive:</b> Desperate Protection → Hamper Strike for more taunt uptime</li>',
}


def patch_text(text: str) -> str:
    out = text
    for old, new in TECH_REPLACEMENTS.items():
        out = out.replace(old, new)
    for old, new in TEXT_REPLACEMENTS.items():
        out = out.replace(old, new)
    for old, new in HTML_REPLACEMENTS.items():
        out = out.replace(old, new)
    return out


def validate_index(text: str) -> None:
    matches = re.findall(r"\n    Guardian:\[\n(.*?)\n    \],\n    Destroyer:\[", text, re.S)
    if not matches:
        raise RuntimeError('Could not locate the live Guardian role block')
    block = max(matches, key=lambda x: x.count("role('"))
    role_rows = re.findall(r"role\('([^']+)'[^\n]*?,\[(.*?)\],\[(.*?)\]", block)
    if len(role_rows) != 12:
        raise RuntimeError(f'Expected 12 Guardian Tank/DPS builds, found {len(role_rows)}')
    missing = [name for name, techniques, _ in role_rows if "'Valor Surge'" not in techniques]
    if missing:
        raise RuntimeError('Guardian builds missing Valor Surge: ' + ', '.join(missing))
    if "['Need more Taunt','Valor Surge','Hamper Strike']" in text:
        raise RuntimeError('A Guardian conditional swap still removes Valor Surge')
    if "['Need cleanse + damage buff','Forceful Charge','Valor Surge']" in text or "['Need cleanse + duo buff','Forceful Charge','Valor Surge']" in text:
        raise RuntimeError('A Guardian conditional swap still treats Valor Surge as an optional add-in')


changed = []
for path in TARGETS:
    if not path.exists():
        raise RuntimeError(f'Missing target: {path}')
    before = path.read_text(encoding='utf-8')
    after = patch_text(before)
    if path.name == 'index.html':
        validate_index(after)
    if after != before:
        path.write_text(after, encoding='utf-8')
        changed.append(str(path))

print('Guardian Valor policy applied. Changed:', ', '.join(changed) if changed else 'none')
