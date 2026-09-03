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


def add_js_row(text, after_key, new_key, row):
    if re.search(rf'(?m)^\s*{re.escape(new_key)}:', text):
        return text
    lines = text.splitlines(keepends=True)
    for i, line in enumerate(lines):
        if re.match(rf'^\s*{re.escape(after_key)}:', line):
            indent = line[:len(line)-len(line.lstrip())]
            if not line.rstrip().endswith(','):
                lines[i] = line.rstrip('\n') + ',' + ('\n' if line.endswith('\n') else '')
            lines.insert(i+1, f'{indent}{new_key}:{row},\n')
            return ''.join(lines)
    raise RuntimeError(f'JS row {after_key} not found while adding {new_key}')


def add_python_dict_row(text, after_key, new_key, row):
    if re.search(rf"(?m)^\s*'{re.escape(new_key)}':", text):
        return text
    lines = text.splitlines(keepends=True)
    for i, line in enumerate(lines):
        if re.match(rf"^\s*'{re.escape(after_key)}':", line):
            indent = line[:len(line)-len(line.lstrip())]
            lines.insert(i+1, f"{indent}'{new_key}': {json.dumps(row, ensure_ascii=False)},\n")
            return ''.join(lines)
    raise RuntimeError(f'Python dict row {after_key} not found while adding {new_key}')


# Live/pre-160 Roll guide and its maintained source.
for path in ROLL_FILES:
    text = path.read_text(encoding='utf-8')
    for after_key, new_key in [('atk','atkpct'),('def','defpct'),('hp','hppct'),('spd','spdpct')]:
        text = add_js_row(text, after_key, new_key, PRE_ROWS[new_key])
    repls = {
        "Conqueror:['crit','critdmg','critpair','acc','critacc','em','spd','atk']": "Conqueror:['crit','critdmg','critpair','acc','critacc','em','spd','spdpct','atk','atkpct']",
        "Guardian:['block','blockpair','def','spd','hp']": "Guardian:['block','blockpair','def','spd','hp','defpct','spdpct','hppct']",
        "Destroyer:['crit','critdmg','critpair','atk','em','acc','critacc','spd']": "Destroyer:['crit','critdmg','critpair','atk','atkpct','em','acc','critacc','spd','spdpct']",
        "dps:['ehr','crit','critdmg','critpair','em','atk','spd']": "dps:['ehr','crit','critdmg','critpair','em','atk','atkpct','spd','spdpct']",
        "heals:['heal','healpair','spd','hp','dmgres']": "heals:['heal','healpair','spd','spdpct','hp','hppct','dmgres']",
    }
    for old,new in repls.items():
        if new not in text:
            if old not in text:
                raise RuntimeError(f'{path}: missing profile {old}')
            text = text.replace(old,new,1)
    path.write_text(text,encoding='utf-8')

# Visible quick-priority line must name the percent variants if Roll guide shows them.
quick = {
    "substats:'Crit Rate / Crit DMG > Accuracy > Elemental Mastery > SPD > ATK'": "substats:'Crit Rate / Crit DMG > Accuracy > Elemental Mastery > SPD / SPD% > ATK / ATK%'",
    "substats:'Block Rate > DEF > SPD > HP'": "substats:'Block Rate > DEF > SPD > HP > DEF% > SPD% > HP%'",
    "substats:'Crit Rate / Crit DMG > ATK ≈ Elemental Mastery > Accuracy > SPD'": "substats:'Crit Rate / Crit DMG > ATK / ATK% ≈ Elemental Mastery > Accuracy > SPD / SPD%'",
    "substats:'Effect Hit Rate > Crit Rate / Crit DMG > Elemental Mastery > ATK > SPD'": "substats:'Effect Hit Rate > Crit Rate / Crit DMG > Elemental Mastery > ATK / ATK% > SPD / SPD%'",
    "substats:'Healing Boost > SPD > HP > DMG RES'": "substats:'Healing Boost > SPD / SPD% > HP / HP% > DMG RES'",
}
for path in RICH_FILES:
    text=path.read_text(encoding='utf-8')
    for old,new in quick.items():
        if new not in text:
            if old not in text:
                raise RuntimeError(f'{path}: missing quick priority {old}')
            text=text.replace(old,new,1)
    path.write_text(text,encoding='utf-8')

# Warlord release activator must replace the same percent rows at Lv162.
text=ACTIVATOR.read_text(encoding='utf-8')
for after_key,new_key in [('atk','atkpct'),('def','defpct'),('hp','hppct'),('spd','spdpct')]:
    text=add_python_dict_row(text,after_key,new_key,WARLORD_ROWS[new_key])
ACTIVATOR.write_text(text,encoding='utf-8')

# Warlord validator and trigger verification.
text=VALIDATOR.read_text(encoding='utf-8')
needed=[
    '    "atkpct:[\'ATK%\',\'Lv162 max unconfirmed\',1",',
    '    "defpct:[\'DEF%\',\'Lv162 max unconfirmed\',1",',
    '    "hppct:[\'HP%\',\'Lv162 max unconfirmed\',1",',
    '    "spdpct:[\'SPD%\',\'Lv162 max unconfirmed\',1",',
]
anchor='    "crit:[\'Crit Rate\',\'≈ 7.50%\',1",\n'
if needed[0] not in text:
    if anchor not in text: raise RuntimeError('validator anchor missing')
    text=text.replace(anchor,''.join(x+'\n' for x in needed)+anchor,1)
VALIDATOR.write_text(text,encoding='utf-8')

text=TRIGGER.read_text(encoding='utf-8')
checks=(
    '          grep -Fq "atkpct:[\'ATK%\',\'Lv162 max unconfirmed\',1" index.html\n'
    '          grep -Fq "defpct:[\'DEF%\',\'Lv162 max unconfirmed\',1" index.html\n'
    '          grep -Fq "hppct:[\'HP%\',\'Lv162 max unconfirmed\',1" index.html\n'
    '          grep -Fq "spdpct:[\'SPD%\',\'Lv162 max unconfirmed\',1" index.html\n'
)
anchor='          grep -Fq "crit:[\'Crit Rate\',\'≈ 7.50%\',1" index.html\n'
if "atkpct:['ATK%','Lv162 max unconfirmed',1" not in text:
    if anchor not in text: raise RuntimeError('trigger anchor missing')
    text=text.replace(anchor,checks+anchor,1)
TRIGGER.write_text(text,encoding='utf-8')

# Staged research data: record the distinct percentage affixes without inventing caps.
data=json.loads(DATA.read_text(encoding='utf-8'))
normal=data['warlord_maxima']['normal_percentage']
for stat in ['ATK%','DEF%','HP%','SPD%']:
    normal.setdefault(stat,{
        'value':'Unverified Lv162 max',
        'confirmed':False,
        'basis':f'{stat} is a separate percentage core-stat affix from its flat counterpart. Current Global class guides explicitly list the percent variant; no direct Global-English Warlord Affix Preview maximum has been retained, so no numeric cap is invented.'
    })
for src in [
    'https://www.prydwen.gg/sword-x-staff/guides/build-guide-conqueror',
    'https://www.prydwen.gg/sword-x-staff/guides/build-guide-guardian',
]:
    if src not in data['sources']: data['sources'].append(src)
DATA.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('Separated flat and percent ATK/DEF/HP/SPD substats; Warlord staging updated')
