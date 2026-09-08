from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
MARK='STALE_OCEANIC_EVENT_REFS_V2'
if MARK in s:
    print('Stale Oceanic recurring cleanup v2 already applied.')
    raise SystemExit(0)

old="""{base:15,name:'Bingo Draw',prep:'Destiny Fruits',note:'Rewards: board and milestone prizes (the exact item grid can vary). Complete every daily mission first. Global players report roughly 60–80 Destiny Fruits is usually enough to finish the normal board; the separate 200-Fruit mission belongs to the current Oceanic Festival.'},"""
new="""{base:15,name:'Bingo Draw',prep:'Destiny Fruits',note:'Rewards: board and milestone prizes (the exact item grid can vary). Complete every daily mission first. Global players report roughly 60–80 Destiny Fruits is usually enough to finish the normal board.'},"""
if old not in s:
    raise SystemExit('generic Bingo recurring-note anchor not found')
s=s.replace(old,new,1)

anchor='''    // Normal rotating mini-events: Bingo -> Lucky Scratch -> Feneck, each one week.'''
if anchor not in s:
    raise SystemExit('recurring mini-event anchor not found')
s=s.replace(anchor,"""    // STALE_OCEANIC_EVENT_REFS_V2: recurring future rows contain only event-specific guidance;
    // expired limited-event overlaps are kept only on their historical runs.
"""+anchor,1)

p.write_text(s,encoding='utf-8')
print('Removed final stale Oceanic reference from generic future Bingo rows.')
