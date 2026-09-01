from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from activate_warlords_rest_roll_guide_v1 import FILES, MARKER, patch_text

REQUIRED = [
    MARKER,
    "Warlord's Rest · Lv162",
    "crit:['Crit Rate','≈ 7.50%',1",
    "critdmg:['Crit DMG','≈ 11.25%',1",
    "block:['Block Rate','≈ 7.50%',1",
    "acc:['Accuracy','≈ 7.50%',1",
    "heal:['Healing Boost','≈ 15.00%',1",
    "critpair:['Crit Rate + Crit DMG','15.3% + 23%',0",
    "critacc:['Crit Rate + Accuracy','15.3% + 15.3%',1",
    "blockpair:['Block Rate + Block Efficiency','15.3% + 23%',1",
    "healpair:['DMG RES + Healing Boost','7.68% + 30.7%',1",
    "em:['Elemental Mastery','Lv162 scaling',1",
    "ehr:['Effect Hit Rate','Lv162 scaling',1",
]

for path in FILES:
    source = path.read_text(encoding='utf-8')
    staged = patch_text(source)
    missing = [token for token in REQUIRED if token not in staged]
    if missing:
        raise SystemExit(f'{path}: staged Warlord patch missing tokens: {missing}')
    print(f'{path}: staged Warlord patch validates')
