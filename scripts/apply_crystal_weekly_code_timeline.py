from pathlib import Path

path = Path('index.html')
s = path.read_text(encoding='utf-8')

new_row = "    ['2026-09-08',56,'Event','Gift code · CRYSTAL','STRONGLY SUPPORTED CURRENT REPORT: GamesRadar updated Sep. 8 lists CRYSTAL as the new Community Weekly Gift Code, rewarding 300 Raw Ore + 1 Stellatie and expiring Sep. 15, 2026. A current community code tracker independently lists CRYSTAL as new on Sep. 8. The mirrored official Global Discord feed has not yet carried this code (latest mirrored official post is Sep. 7), so the exact expiry clock is not confirmed here; redeem promptly rather than assuming it lasts through the full Sep. 15 Charming Glance day.','event','2026-09-15'],\n"

if "'Gift code · CRYSTAL'" in s:
    print('CRYSTAL timeline row already present; no change needed.')
else:
    anchor = "    ['2026-09-01',49,'Event','Gift code · VEGGIE'"
    idx = s.find(anchor)
    if idx < 0:
        raise SystemExit('Could not find VEGGIE timeline anchor')
    line_end = s.find('\n', idx)
    if line_end < 0:
        raise SystemExit('Could not find end of VEGGIE timeline row')
    s = s[:line_end + 1] + new_row + s[line_end + 1:]
    path.write_text(s, encoding='utf-8')
    print('Added CRYSTAL weekly gift-code timeline row.')

for needle in [
    "'Gift code · CRYSTAL'",
    '300 Raw Ore + 1 Stellatie',
    "'2026-09-15'",
    'mirrored official Global Discord feed has not yet carried this code'
]:
    if needle not in s:
        raise SystemExit(f'Missing expected CRYSTAL timeline marker: {needle}')
