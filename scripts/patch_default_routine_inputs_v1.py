from pathlib import Path

runtime_path = Path('assets/runtime.js')
runtime = runtime_path.read_text(encoding='utf-8')

replacements = [
    (
        "    shopRefreshesDaily:0,\n    hammerCurrent:0,knucklesCurrent:0,shovelCurrent:0,\n    staminaMode:'auto',realmDailyOre:4,realmDailyEssence:4,realmDailySand:4,",
        "    // ROUTINE_SPEND_DEFAULTS_V1: safe baseline routine plan for a fresh/reset S2 calculator.\n    shopRefreshesDaily:1,\n    hammerCurrent:0,knucklesCurrent:0,shovelCurrent:0,\n    staminaMode:'auto',realmDailyOre:2,realmDailyEssence:2,realmDailySand:2,"
    ),
]

for old, new in replacements:
    count = runtime.count(old)
    if count != 1:
        raise SystemExit(f'Expected exactly one runtime replacement, found {count}: {old[:100]!r}')
    runtime = runtime.replace(old, new, 1)

runtime_path.write_text(runtime, encoding='utf-8')

index_path = Path('index.html')
index = index_path.read_text(encoding='utf-8')

index_replacements = [
    ('id="realmDailyOre" type="number" min="0" max="20" step="1" value="0"', 'id="realmDailyOre" type="number" min="0" max="20" step="1" value="2"'),
    ('id="realmDailyEssence" type="number" min="0" max="20" step="1" value="0"', 'id="realmDailyEssence" type="number" min="0" max="20" step="1" value="2"'),
    ('id="realmDailySand" type="number" min="0" max="20" step="1" value="0"', 'id="realmDailySand" type="number" min="0" max="20" step="1" value="2"'),
    ('id="shopRefreshesDaily" type="number" min="0" max="20" step="1" value="0"', 'id="shopRefreshesDaily" type="number" min="0" max="20" step="1" value="1"'),
]

for old, new in index_replacements:
    count = index.count(old)
    if count != 1:
        raise SystemExit(f'Expected exactly one index replacement, found {count}: {old!r}')
    index = index.replace(old, new, 1)

index_path.write_text(index, encoding='utf-8')

runtime_check = runtime_path.read_text(encoding='utf-8')
index_check = index_path.read_text(encoding='utf-8')
assert 'shopRefreshesDaily:1,' in runtime_check
assert "realmDailyOre:2,realmDailyEssence:2,realmDailySand:2" in runtime_check
for id_ in ('realmDailyOre','realmDailyEssence','realmDailySand'):
    assert f'id="{id_}" type="number" min="0" max="20" step="1" value="2"' in index_check
assert 'id="shopRefreshesDaily" type="number" min="0" max="20" step="1" value="1"' in index_check

print('Routine Realm/shop defaults patched successfully.')
