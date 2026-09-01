from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ACTIVATOR = ROOT / 'scripts' / 'activate_pandarial_build_prep_v1.py'
DATA = ROOT / 'data' / 'pandarial-build-prep-v1.json'
TARGETS = [ROOT / 'index.html', ROOT / '.github' / 'build-fantomons-inject.html']

spec = importlib.util.spec_from_file_location('pandarial_activator', ACTIVATOR)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(mod)

data = json.loads(DATA.read_text(encoding='utf-8'))
assert data['release_gate_utc'] == '2026-10-14T13:00:00Z'
assert data['planned_impacts']['Conqueror']['All-Content'] == ['Nyxarchon', 'Pandarial']
assert data['planned_impacts']['Guardian']['Water Offensive'][0] == 'Pandarial'
assert data['planned_impacts']['Destroyer']['change'].startswith('No automatic Pandarial')
assert data['planned_impacts']['Dominator']['Healing'] == ['Pandarial', 'Mandragora']

for path in TARGETS:
    original = path.read_text(encoding='utf-8')
    assert mod.MARK not in original, f'{path}: release marker should not be live before activation'
    patched, changed = mod.patch_text(original)
    assert changed >= 12, f'{path}: expected staged replacements, got {changed}'
    assert mod.MARK in patched
    assert "pick('Pandarial','Burst/front-load alt" in patched
    assert "pick('Pandarial','Main aggressive Guardian lead" in patched
    assert "pick('Pandarial','Main healer/hybrid lead" in patched
    assert "Destroyer:{\n      Solo:[pick('Nyxarchon','Main premium choice" in patched
    assert "With Pandarial, Luminous Shield → Light Sword Array" in patched

print('Pandarial build prep validates cleanly against current index + maintained Fantomon source')
