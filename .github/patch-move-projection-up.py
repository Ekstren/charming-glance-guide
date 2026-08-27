from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')
marker = '<!-- MOVE_PROJECTION_BEFORE_PROGRESSION_V1 -->'
if marker in s:
    print('already patched')
    raise SystemExit(0)

block = '''        <div class="projectionCallout projectionInline"><span>Projected season-end level</span><strong id="projectedCharacter">—</strong><small id="projectionNote" hidden></small></div>
        <div class="seasonDeadline"><span id="seasonDeadlineLabel">Season 1 ends</span><b id="seasonDeadlineDate">—</b><small id="seasonRemaining">—</small></div><div class="seasonRulesHint" id="seasonRulesHint" hidden></div>
'''

if s.count(block) != 1:
    raise SystemExit(f'expected exactly one projection/deadline block, found {s.count(block)}')

anchor = '''        <!-- COMPACT_PROGRESSION_TOP_V1 -->
        <div class="compactProgression" aria-label="Current progression used by the optimizer">'''
if s.count(anchor) != 1:
    raise SystemExit(f'expected exactly one compact progression anchor, found {s.count(anchor)}')

# Remove the forecast rows from below the progression editor, then insert them
# immediately after the XP / Find Max grid and before Skills/Relics/Fantomons/Gear.
s = s.replace(block, '', 1)
insert = f'''        {marker}\n{block}{anchor}'''
s = s.replace(anchor, insert, 1)

p.write_text(s, encoding='utf-8')
print('moved projected season-end level and season deadline above progression inputs')
