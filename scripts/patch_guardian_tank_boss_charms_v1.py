from pathlib import Path

PATHS = [
    Path('index.html'),
    Path('.github/build-fantomons-inject.html'),
    Path('scripts/patch_meta_build_modes_v1.py'),
    Path('scripts/patch_guardian_tank_dps_toggle_v1.py'),
]

OLD = "role('Crucible / Conquest · Tank','Carry-support / boss-score meta',['Valor Surge','Leap Attack','Holy Purification','Lunarwater Threads'],['Frigid Aura','Frigid Glint','Iron Fortress','Oath of Vigil'],'This bar exists to make the strongest carry better. If there is no buff worth dispelling, Holy Purification → damage. Lunarwater Threads → Seismic Tide for steadier Cold stacking.','Kels is the default boss-support Fantomon when Dispel/DEF Down matters; Nyxarchon is the greedier damage-amplification option.','Prydwen support core')"

NEW = "role('Crucible / Conquest · Tank','Carry-support / boss tank meta',['Valor Surge','Leap Attack','Holy Purification','Lunarwater Threads'],['Holy Aegis','Soul Protection','Iron Fortress','Oath of Vigil'],'This is the true Tank/support version: buff the carry, contribute Dispel/DEF-down utility, and spend the Charm bar on staying alive plus team protection. If there is no buff worth dispelling, Holy Purification → damage.','Frigid Aura + Frigid Glint belong to Guardian DPS/Water mode, not this Tank card. If your Block is still inconsistent, Soul Protection → Block Awareness. Kels remains the default boss-support Fantomon when Dispel/DEF Down matters.','Tank/support synthesis')"

changed = 0
for path in PATHS:
    text = path.read_text(encoding='utf-8')
    count = text.count(OLD)
    if count:
        text = text.replace(OLD, NEW)
        path.write_text(text, encoding='utf-8')
        changed += count
    elif NEW not in text:
        raise RuntimeError(f'Could not find Guardian Crucible/Conquest Tank role in {path}')

if changed == 0:
    print('Guardian tank boss Charm fix already applied')
else:
    print(f'Updated Guardian Crucible/Conquest Tank Charm setup in {changed} maintained/live locations')
