from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

# 1) The earlier BUILD_LAYOUT_V2 helper was appended outside the app IIFE,
# so references to currentBuildSeason/currentClass threw before any layout work ran.
old="""function splitBerserkerPriorities(root){
  if(currentBuildSeason!=='s1' || currentClass!=='Berserker') return;
  const panel=[...root.children].find(el=>el.classList&&el.classList.contains('priorityPanel'));
"""
new="""function splitBerserkerPriorities(root){
  const buildName=root.querySelector(':scope > .guideSummary strong')?.textContent.trim()||'';
  if(buildName!=='Berserker') return;
  const panel=[...root.children].find(el=>el.classList&&el.classList.contains('priorityPanel'));
"""
if old in s:
    s=s.replace(old,new,1)
elif new not in s:
    raise SystemExit('Could not patch Berserker scope bug')

# 2) The compact-timeline renderer was creating its own Details control after
# timelineDetailHtml had already created entryMore. Skip the legacy extra control.
old_compact="""  function compactEntry(card){
    if(card.dataset[COMPACT_MARK]) return;
    const ps=[...card.querySelectorAll('p')];
"""
new_compact="""  function compactEntry(card){
    if(card.dataset[COMPACT_MARK]) return;
    if(card.querySelector('details.entryMore')){ card.dataset[COMPACT_MARK]='1'; return; }
    const ps=[...card.querySelectorAll('p')];
"""
if old_compact in s:
    s=s.replace(old_compact,new_compact,1)
elif new_compact not in s:
    raise SystemExit('Could not patch compactEntry duplicate-details guard')

# Strong CSS fallback for any already-rendered legacy extra details element.
css='.entry .timelineCardDetails{display:none!important}\n'
if css.strip() not in s:
    marker='.timelineCardDetails{margin-top:6px;border-top:1px solid var(--line)}'
    if marker not in s:
        raise SystemExit('Could not find timelineCardDetails CSS marker')
    s=s.replace(marker,css+marker,1)

# Keep the prior generic entryMore dedupe as an additional safety net.
if 'function dedupeTimelineDetails()' not in s:
    raise SystemExit('Expected dedupeTimelineDetails helper is missing')

# Sanity-check the layout pieces that should now be able to run for S1 and S2.
required=[
    '/* BUILD_LAYOUT_V2 */',
    'function polishBuildLayout()',
    '.priorityPair{display:grid',
    '.buildQuickStats{',
    'function buildHtmlS2(cls)',
    'Core technique investment',
    'Core charm investment',
]
for item in required:
    if item not in s:
        raise SystemExit(f'Missing expected build-layout marker: {item}')

p.write_text(s,encoding='utf-8')
print('Fixed BUILD_LAYOUT_V2 scope bug and duplicate timeline Details source conflict.')
