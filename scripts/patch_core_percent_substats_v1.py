from pathlib import Path
import json
import re

ROLL_FILES = [Path('index.html'), Path('scripts/patch_build_roll_guide_v2.py')]
RICH_FILES = [Path('index.html'), Path('scripts/patch_restore_rich_builds_v1.py')]
ACTIVATOR = Path('scripts/activate_warlords_rest_roll_guide_v1.py')
VALIDATOR = Path('scripts/validate_warlords_rest_roll_guide_v1.py')
TRIGGER = Path('.github/workflows/warlords-rest-roll-guide-trigger.yml')
DATA = Path('data/warlords-rest-roll-guide-v1.json')

PRE_ROWS = {
    'atkpct': "['ATK%','Max unconfirmed',1,'ATK% is a separate percentage substat from flat ATK. Current Global class guides explicitly list both ATK and ATK%, but I do not have a direct pre-160 English-client Affix Preview capture proving the maximum roll.',0]",
    'defpct': "['DEF%','Max unconfirmed',1,'DEF% is a separate percentage substat from flat DEF. Current Global class guides explicitly list both DEF and DEF%, but I do not have a direct pre-160 English-client Affix Preview capture proving the maximum roll.',0]",
    'hppct': "['HP%','Max unconfirmed',1,'HP% is a separate percentage substat from flat HP. Current Global class guides explicitly list both HP and HP%, but I do not have a direct pre-160 English-client Affix Preview capture proving the maximum roll.',0]",
    'spdpct': "['SPD%','Max unconfirmed',1,'SPD% is a separate percentage substat from flat SPD. Current Global class guides explicitly list both SPD and SPD%, but I do not have a direct pre-160 English-client Affix Preview capture proving the maximum roll.',0]",
}

WARLORD_ROWS = {
    'atkpct': "['ATK%','Lv162 max unconfirmed',1,'ATK% is a separate percentage substat from flat ATK. Current Global guides confirm the affix exists, but I do not have a direct Global-English Warlord Affix Preview proving its Lv162 maximum.',0]",
    'defpct': "['DEF%','Lv162 max unconfirmed',1,'DEF% is a separate percentage substat from flat DEF. Current Global evidence includes percentage DEF refinement lines, but I do not have a direct Warlord Affix Preview proving the Lv162 maximum.',0]",
    'hppct': "['HP%','Lv162 max unconfirmed',1,'HP% is a separate percentage substat from flat HP. Current Global guides confirm the affix exists, but I do not have a direct Global-English Warlord Affix Preview proving its Lv162 maximum.',0]",
    'spdpct': "['SPD%','Lv162 max unconfirmed',1,'SPD% is a separate percentage substat from flat SPD. Current Global guides confirm the affix exists, but I do not have a direct Global-English Warlord Affix Preview proving its Lv162 maximum.',0]",
}


def insert_row_after(text: str, after_key: str, new_key: str, row: str) -> str:
    if re.search(rf'(?m)^\s*{re.escape(new_key)}:', text):
        return text
    pat = re.compile(rf'(?m)^(\s*){re.escape(after_key)}:(\[.*\],?)$')
    m = pat.search(text)
    if not m:
        raise RuntimeError(f'Could not find row {after_key} while adding {new_key}')
    comma = ',' if not m.group(2).endswith(',') else ''
    old_line = m.group(0)
    if comma:
        old_line += ','
    new_line = f"{m.group(1)}{new_key}:{row},"
    return text[:m.start()] + old_line + '\n' + new_line + text[m.end():]


for path in ROLL_FILES:
    text = path.read_text(encoding='utf-8')
    text = insert_row_after(text, 'atk', 'atkpct', PRE_ROWS['atkpct'])
    text = insert_row_after(text, 'def', 'defpct', PRE_ROWS['defpct'])
    text = insert_row_after(text, 'hp', 'hppct', PRE_ROWS['hppct'])
    text = insert_row_after(text, 'spd', 'spdpct', PRE_ROWS['spdpct'])
    profile_repls = {
        "Conqueror:['crit','critdmg','critpair','acc','critacc','em','spd','atk']": "Conqueror:['crit','critdmg','critpair','acc','critacc','em','spd','spdpct','atk','atkpct']",
        "Guardian:['block','blockpair','def','spd','hp']": "Guardian:['block','blockpair','def','spd','hp','defpct','spdpct','hppct']",
        "Destroyer:['crit','critdmg','critpair','atk','em','acc','critacc','spd']": "Destroyer:['crit','critdmg','critpair','atk','atkpct','em','acc','critacc','spd','spdpct']",
        "dps:['ehr','crit','critdmg','critpair','em','atk','spd']": "dps:['ehr','crit','critdmg','critpair','em','atk','atkpct','spd','spdpct']",
        "heals:['heal','healpair','spd','hp','dmgres']": "heals:['heal','healpair','spd','spdpct','hp','hppct','dmgres']",
    }
    for old, new in profile_repls.items():
        if new not in text:
            if old not in text:
                raise RuntimeError(f'{path}: missing Roll profile token: {old}')
            text = text.replace(old, new, 1)
    path.write_text(text, encoding='utf-8')

# Make the visible priority line explicitly distinguish flat and percentage core substats.
substat_repls = {
    "substats:'Crit Rate / Crit DMG > Accuracy > Elemental Mastery > SPD > ATK'": "substats:'Crit Rate / Crit DMG > Accuracy > Elemental Mastery > SPD / SPD% > ATK / ATK%'",
    "substats:'Block Rate > DEF > SPD > HP'": "substats:'Block Rate > DEF > SPD > HP > DEF% > SPD% > HP%'",
    "substats:'Crit Rate / Crit DMG > ATK ≈ Elemental Mastery > Accuracy > SPD'": "substats:'Crit Rate / Crit DMG > ATK / ATK% ≈ Elemental Mastery > Accuracy > SPD / SPD%'",
    "substats:'Effect Hit Rate > Crit Rate / Crit DMG > Elemental Mastery > ATK > SPD'": "substats:'Effect Hit Rate > Crit Rate / Crit DMG > Elemental Mastery > ATK / ATK% > SPD / SPD%'",
    "substats:'Healing Boost > SPD > HP > DMG RES'": "substats:'Healing Boost > SPD / SPD% > HP / HP% > DMG RES'",
}
for path in RICH_FILES:
    text = path.read_text(encoding='utf-8')
    for old, new in substat_repls.items():
        if new not in text:
            if old not in text:
                raise RuntimeError(f'{path}: missing quick-substat token: {old}')
            text = text.replace(old, new, 1)
    path.write_text(text, encoding='utf-8')

# Keep the pre-staged Warlord activator aware of the new percentage rows.
text = ACTIVATOR.read_text(encoding='utf-8')
for after_key, new_key in [('atk','atkpct'),('def','defpct'),('hp','hppct'),('spd','spdpct')]:
    text = insert_row_after(text, after_key, new_key, WARLORD_ROWS[new_key])
ACTIVATOR.write_text(text, encoding='utf-8')

# Require the Warlord staged validator to preserve/update the new rows too.
text = VALIDATOR.read_text(encoding='utf-8')
required = [
    '    "atkpct:[\'ATK%\',\'Lv162 max unconfirmed\',1",',
    '    "defpct:[\'DEF%\',\'Lv162 max unconfirmed\',1",',
    '    "hppct:[\'HP%\',\'Lv162 max unconfirmed\',1",',
    '    "spdpct:[\'SPD%\',\'Lv162 max unconfirmed\',1",',
]
anchor = '    "crit:[\'Crit Rate\',\'≈ 7.50%\',1",\n'
if required[0] not in text:
    if anchor not in text:
        raise RuntimeError('Warlord validator anchor missing')
    text = text.replace(anchor, ''.join(x+'\n' for x in required) + anchor, 1)
VALIDATOR.write_text(text, encoding='utf-8')

# Add the new Warlord rows to the workflow's activated-data verification.
text = TRIGGER.read_text(encoding='utf-8')
checks = (
    '          grep -Fq "atkpct:[\'ATK%\',\'Lv162 max unconfirmed\',1" index.html\n'
    '          grep -Fq "defpct:[\'DEF%\',\'Lv162 max unconfirmed\',1" index.html\n'
    '          grep -Fq "hppct:[\'HP%\',\'Lv162 max unconfirmed\',1" index.html\n'
    '          grep -Fq "spdpct:[\'SPD%\',\'Lv162 max unconfirmed\',1" index.html\n'
)
anchor = '          grep -Fq "crit:[\'Crit Rate\',\'≈ 7.50%\',1" index.html\n'
if "atkpct:['ATK%','Lv162 max unconfirmed',1" not in text:
    if anchor not in text:
        raise RuntimeError('Warlord trigger verification anchor missing')
    text = text.replace(anchor, checks + anchor, 1)
TRIGGER.write_text(text, encoding='utf-8')

# Record the distinction in the staged Warlord data without inventing maxima.
data = json.loads(DATA.read_text(encoding='utf-8'))
normal = data['warlord_maxima']['normal_percentage']
for stat in ['ATK%', 'DEF%', 'HP%', 'SPD%']:
    normal.setdefault(stat, {
        'value': 'Unverified Lv162 max',
        'confirmed': False,
        'basis': f'{stat} is a separate percentage core-stat affix from its flat counterpart. Current Global class guides explicitly list the percent variant; no direct Global-English Warlord Affix Preview maximum has been retained, so no numeric cap is invented.'
    })
for src in [
    'https://www.prydwen.gg/sword-x-staff/guides/build-guide-conqueror',
    'https://www.prydwen.gg/sword-x-staff/guides/build-guide-guardian',
]:
    if src not in data['sources']:
        data['sources'].append(src)
DATA.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

print('Separated flat and percentage ATK/DEF/HP/SPD substats and updated Warlord staging')
