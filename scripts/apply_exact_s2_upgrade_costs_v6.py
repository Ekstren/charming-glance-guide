from pathlib import Path

# v5 contains the full audited replacement payload, but its one interpolation block was
# accidentally written as a Python f-string even though it also contains JavaScript braces.
# Read it as text, turn only that block into an ordinary triple-quoted string, fill the two
# intended data placeholders explicitly, then execute the corrected patch source.
src_path=Path('scripts/apply_exact_s2_upgrade_costs_v5.py')
src=src_path.read_text(encoding='utf-8')
if "insert=f'''" not in src:
    raise SystemExit('v5 interpolation anchor not found')
src=src.replace("insert=f'''","insert='''",1)
anchor="'''\nif anchor not in s: raise SystemExit('EXP insert anchor not found')"
replacement="'''\ninsert=insert.replace('{char_data}',char_data).replace('{fanto_data}',fanto_data)\nif anchor not in s: raise SystemExit('EXP insert anchor not found')"
if anchor not in src:
    raise SystemExit('v5 interpolation close anchor not found')
src=src.replace(anchor,replacement,1)
exec(compile(src,str(src_path)+'::v6-fixed','exec'))
