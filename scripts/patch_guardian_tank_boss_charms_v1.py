from pathlib import Path

PATHS = [
    Path('index.html'),
    Path('.github/build-fantomons-inject.html'),
    Path('scripts/patch_meta_build_modes_v1.py'),
    Path('scripts/patch_guardian_tank_dps_toggle_v1.py'),
]

OLD = "role('Crucible / Conquest · Tank','Carry-support / boss-score meta',['Valor Surge','Leap Attack','Holy Purification','Lunarwater Threads'],['Frigid Aura','Frigid Glint','Iron Fortress','Oath of Vigil'],'This bar exists to make the strongest carry better. If there is no buff worth dispelling, Holy Purification → damage. Lunarwater Threads → Seismic Tide for steadier Cold stacking.','Kels is the default boss-support Fantomon when Dispel/DEF Down matters; Nyxarchon is the greedier damage-amplification option.','Prydwen support core')"

NEW = "role('Crucible / Conquest · Tank','Carry-support / boss tank meta',['Valor Surge','Leap Attack','Holy Purification','Lunarwater Threads'],['Frigid Aura','Frigid Glint','Iron Fortress','Oath of Vigil'],'Buff the carry, use Holy Purification for Dispel/utility, and let Lunarwater Threads + the Frigid charms add useful Water/Cold pressure. If the boss has no important buff to remove, Holy Purification → a higher-damage option.','Iron Fortress and Oath of Vigil keep the party protected without overcommitting to personal mitigation. If you are actually dying, Frigid Glint → Soul Protection; if needed, Frigid Aura → Holy Aegis. Kels remains the boss-support Fantomon when Dispel/DEF Down matters.','Guide-backed')"

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
