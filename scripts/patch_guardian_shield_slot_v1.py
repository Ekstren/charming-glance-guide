from pathlib import Path

MARK='GUARDIAN_SHIELD_SLOT_V1'
files=[Path('index.html'),Path('scripts/patch_restore_rich_builds_v1.py')]
old="rows:[['Sword','SPD > ATK > Physical Mastery > Elemental Mastery'],['Gauntlets','DEF > HP > Physical / Elemental RES'],['Helmet','DEF > HP > RES'],['Chest','DEF > HP > RES'],['Boots','SPD > ATK > Elemental / Physical Mastery']]"
new="rows:[['Sword','SPD > ATK > Physical Mastery > Elemental Mastery'],['Shield','DEF > HP > Physical / Elemental RES'],['Helmet','DEF > HP > RES'],['Chest','DEF > HP > RES'],['Boots','SPD > ATK > Elemental / Physical Mastery']]"

for p in files:
    s=p.read_text(encoding='utf-8')
    if old not in s:
        if new in s:
            print(f'{p}: already corrected')
            continue
        raise SystemExit(f'{p}: Guardian stat profile anchor not found')
    s=s.replace(old,new,1)
    if p.name=='index.html':
        s=s.replace('<style id="site-polish-v1">',f'<!-- {MARK} -->\n<style id="site-polish-v1">',1)
    p.write_text(s,encoding='utf-8')
    print(f'{p}: Guardian off-hand label corrected to Shield')
