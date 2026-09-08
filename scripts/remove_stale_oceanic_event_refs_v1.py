from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
MARK='STALE_OCEANIC_EVENT_REFS_V1'
if MARK in s:
    print('Stale Oceanic event cleanup already applied.')
    raise SystemExit(0)

repls=[
("""<div class=\"eventCycleCard\"><b>Bingo Draw</b><span>Every 3 weeks · first appears Server Day 15</span><p>Uses <strong>Destiny Fruits</strong> for extra tickets. Rewards come from the board/milestones and can vary by run. Global community reports usually clearing normal Bingo with roughly <strong>60–80 Fruits plus all daily missions</strong>. The separate 200-Fruit summer mission is now live inside <strong>Oceanic Festival</strong>.</p></div>""",
"""<div class=\"eventCycleCard\"><b>Bingo Draw</b><span>Every 3 weeks · first appears Server Day 15</span><p>Uses <strong>Destiny Fruits</strong> for extra tickets. Rewards come from the board/milestones and can vary by run. Global community reports usually clearing normal Bingo with roughly <strong>60–80 Fruits plus all daily missions</strong>.</p></div>"""),
("""<div><b>Charming Glance right now</b><p><b>Aug 19–26:</b> Bingo Draw 2 overlaps Oceanic Festival, so Destiny Fruit spending can advance both. <b>Aug 26:</b> Lucky Scratch 2 starts while Oceanic is still active; Material Realm activity can also feed Oceanic Beach Shovel objectives.</p></div>""",
"""<div><b>Rotation handling</b><p>Bingo Draw → Lucky Scratch → Feneck's Puzzle repeats on the projected 21-day server-age cycle. Use the dated timeline rows below for the current and upcoming Charming Glance run instead of carrying old limited-event overlap notes forward.</p></div>"""),
("""<div class=\"eventSourceNote\" style=\"padding:0 16px 14px\">Schedule cross-check: Limitless Gaming server-age timeline. Treasure Hunt Phase 1–15 rewards: QY Maple. Event strategy: current Oceanic Festival guides, Loot & Waifus, Prydwen and Global community reports.</div>""",
"""<div class=\"eventSourceNote\" style=\"padding:0 16px 14px\">Schedule cross-check: Limitless Gaming server-age timeline. Treasure Hunt Phase 1–15 rewards: QY Maple. Event strategy: Loot & Waifus, Prydwen and Global community reports.</div>"""),
("""if(title.startsWith('Bingo Draw')) return 'Do dailies first; roughly 60–80 Destiny Fruits usually clears the normal board. This run overlaps Oceanic, so Fruit spending progresses both.';""",
"""if(title.startsWith('Bingo Draw')) return 'Do dailies first; roughly 60–80 Destiny Fruits usually clears the normal board. Save extra Fruits for the next Bingo run if you finish early.';"""),
("""if(title.startsWith('Lucky Scratch')) return 'Aug 26–Sep 2. Spend saved Material Realm tools to generate scratch cards; through Aug 31, Realm activity also overlaps Oceanic Beach Shovel objectives.';""",
"""if(title.startsWith('Lucky Scratch')) return 'Spend saved Material Realm tools while Lucky Scratch is active to generate more scratch cards; bank tools during Feneck week for the next run.';""")
]

for old,new in repls:
    if old not in s:
        raise SystemExit('anchor not found:\n'+old[:180])
    s=s.replace(old,new,1)

# Preserve historical Oceanic Festival rows/notes, but mark the cleanup near the recurring-event block.
anchor='''    <details class="timelineIntel" id="recurringEventsDetails">'''
if anchor not in s:
    raise SystemExit('recurring events block anchor not found')
s=s.replace(anchor,'''    <!-- STALE_OCEANIC_EVENT_REFS_V1: current/future recurring event copy no longer inherits expired Oceanic Festival overlap text. -->\n'''+anchor,1)

p.write_text(s,encoding='utf-8')
print('Removed stale Oceanic references from current/future recurring-event copy.')
