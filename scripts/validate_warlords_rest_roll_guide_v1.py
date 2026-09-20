from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from activate_warlords_rest_roll_guide_v1 import FILES, MARKER, patch_text

REQUIRED = [
    MARKER,
    "Current baseline",
    "atk:['ATK','5.36K',1",
    "atkpct:['ATK%','18.7%',1",
    "def:['DEF','5.36K',1",
    "defpct:['DEF%','18.7%',1",
    "hp:['HP','26.8K',1",
    "hppct:['HP%','18.7%',1",
    "spd:['SPD','4.28K',1",
    "spdpct:['SPD%','18.7%',1",
    "crit:['Crit Rate','7.5%',1",
    "critdmg:['Crit DMG','11.2%',1",
    "block:['Block Rate','7.5%',1",
    "acc:['Accuracy','7.5%',1",
    "em:['Elemental Mastery','5.36K',1",
    "ehr:['Effect Hit Rate','5.36K',1",
    "dmgres:['DMG RES','Paired affix only',1",
    "heal:['Healing Boost','15%',1",
    "critpair:['Crit Rate + Crit DMG','15.3% + 23%',1",
    "critacc:['Crit Rate + Accuracy','15.3% + 15.3%',1",
    "blockpair:['Block Rate + Block Efficiency','15.3% + 23%',1",
    "healpair:['DMG RES + Healing Boost','7.68% + 30.7%',1",
]

for path in FILES:
    source = path.read_text(encoding='utf-8')
    staged = patch_text(source)
    missing = [token for token in REQUIRED if token not in staged]
    if missing:
        raise SystemExit(f'{path}: staged Warlord patch missing tokens: {missing}')
    print(f'{path}: staged Warlord patch validates')
