from pathlib import Path
import subprocess

subprocess.run(['python','.github/patch-fantasia-ascent-builds-v2.py'],check=True)

dominator_rows=[
"      role('Fantasia Ascent · DPS','Solo push: Erosion AoE with Shadow Vengeance safety',['Mana Blast','Dark Bullet','Abyssal Hand','Shadow Impact'],['Shadow Vengeance',\"Night's Blessing\",'Shadow Erosion','Linked Misfortune'],'The AoE Erosion package handles mixed floors and Shadow Vengeance buys time to finish dangerous waves.','Effect Hit Rate still matters whenever the floor depends on Erosion sticking.','Community Ascent')",
"      role('Fantasia Ascent · Heals','Solo push: sustain hybrid for Healing Boost builds',['Rejuvenating Rain','Radiant Restoration','Dark Bullet','Shadow of Termination'],['Phantom Light','Healing Mastery','Shadow Vengeance','Mantra of Blessings'],'Rejuvenating Rain + Radiant Restoration sustain the run while Dark Bullet and Shadow of Termination preserve kill pressure.','Best for accounts already invested into Healing Boost and SPD.','Ascent sustain')"
]
insert=',\n'+',\n'.join(dominator_rows)

for path in [Path('index.html'),Path('.github/build-fantomons-inject.html')]:
    text=path.read_text(encoding='utf-8')
    cursor=0
    preset_blocks=0
    patched=0
    while True:
        preset_start=text.find('const ROLE_PRESETS={',cursor)
        if preset_start<0:
            break
        next_preset=text.find('const ROLE_PRESETS={',preset_start+1)
        scope_end=next_preset if next_preset>=0 else len(text)
        dom_start=text.find('\n    Dominator:[',preset_start,scope_end)
        if dom_start>=0:
            preset_blocks+=1
            close=text.find('\n    ]',dom_start,scope_end)
            if close<0:
                raise SystemExit(f'{path}: could not close Dominator preset block #{preset_blocks}')
            if "role('Fantasia Ascent · DPS'" not in text[dom_start:close]:
                text=text[:close]+insert+text[close:]
                patched+=1
                added=len(insert)
                scope_end+=added
                if next_preset>=0:
                    next_preset+=added
        cursor=(next_preset if next_preset>=0 else len(text))
        if next_preset<0:
            break
    if preset_blocks<1:
        raise SystemExit(f'{path}: no ROLE_PRESETS Dominator blocks found')
    path.write_text(text,encoding='utf-8')
    print(f'{path}: Dominator ROLE_PRESETS blocks={preset_blocks}, additionally patched={patched}')

print('ensured Fantasia Ascent DPS/Heals rows exist in every Dominator ROLE_PRESETS copy')
