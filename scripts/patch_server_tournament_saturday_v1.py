from pathlib import Path

OLD = "    ['2026-09-04',52,'Event','4v4 Tournament registration opens','CONFIRMED FOR CHARMING GLANCE from the in-game Tournament screen captured Sep. 2 at about 8:00 AM PDT: “Registration starts in 1d 22h,” which lands at the Sep. 4 6:00 AM PDT server reset. The screen showed Season 6 ended and the countdown for the next 4v4 Tournament. This confirms registration opening only; the battle/qualification window is not inferred here.','event'],"
NEW = "    ['2026-09-05',53,'Event','Server Tournament','CONFIRMED FOR CHARMING GLANCE from the in-game Tournament screen captured Sep. 2 at about 8:00 AM PDT: registration begins at the Sep. 4 6:00 AM PDT reset, and the user confirmed registration opens one day before the non-Nexus tournament. The timeline therefore shows the actual Server Tournament on Sat Sep. 5 rather than the registration day, keeping it clearly distinct from Nexus Tournament.','event'],"

changed=[]
for path in [Path('index.html'), Path('scripts/patch_confirm_charming_glance_tournament_times_v1.py')]:
    s=path.read_text(encoding='utf-8')
    if OLD not in s:
        if NEW in s:
            continue
        raise SystemExit(f'expected tournament registration row not found in {path}')
    path.write_text(s.replace(OLD,NEW,1),encoding='utf-8')
    changed.append(str(path))

print('Updated:', ', '.join(changed) if changed else 'already current')
