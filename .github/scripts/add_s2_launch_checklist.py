from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')

entry = """    ['2026-08-30',47,'Feature','Season 2 launch checklist','<span class=\"launchChecklist\"><span><b>1.</b><strong>Log in after Season 2 is live.</strong><em>Make sure the rollover/reset has fully happened before claiming anything.</em></span><span><b>2.</b><strong>Claim Astral / season rewards.</strong><em>Grab rollover, Astral Pact, and other immediately available season rewards.</em></span><span><b>3.</b><strong>Rank up as far as possible.</strong><em>Do this before spending Stamina or Material Realm resources so later rewards use your higher rank where applicable.</em></span><span><b>4.</b><strong>Claim your saved Bed EXP.</strong><em>Collect the banked 36 hours now. Current community testing says waiting for statues does not increase EXP already stored.</em></span><span><b>5.</b><strong>Push the new map and activate reachable statues.</strong><em>Explore as far as your level allows and activate every Goddess / Lost Goddess Statue you can reach.</em></span><span><b>6.</b><strong>Use Bed boosts after statue progress.</strong><em>Use the free 2-hour Bed boost and other Bed speed-ups after pushing statues so the new rate applies to the boosted time.</em></span><span><b>7.</b><strong>Spend Stamina and Material Realm resources.</strong><em>Once rank and early map progress are set, start using saved Realm tools, refreshes, and Stamina.</em></span><span><b>8.</b><strong>Finish progression cleanup.</strong><em>Do class advancement, relics, gear, Fantomons, and other upgrades as the new level gates open.</em></span></span>','feature'],
"""

if 'Season 2 launch checklist' not in text:
    anchor = "    ['2026-08-30',47,'Region','Loong Haven opens','Season 2 Day 1. Level-gated milestones happen when you actually reach them, not automatically on Day 1: Lv.106 = T4 class advancement + Loong Haven Five / area stockpile (Gateway Key ×5 · Withering Potion ×1 · Magic Drill ×1 · Water Mine ×2 · cloud key ×7); Lv.108 = Fantomon Adult / Materialization; Lv.116 = Demonbind Tower. QY merge reference: 01–04 · 05–08 · 09–12 · 13–16.','region'],\n"
    if anchor not in text:
        raise SystemExit('Loong Haven S2 Day 1 anchor not found')
    text = text.replace(anchor, anchor + entry, 1)

css = """
<style id="s2-launch-checklist-v1">
.launchChecklist{display:grid;gap:8px;margin-top:8px}
.launchChecklist>span{display:grid;grid-template-columns:28px minmax(0,1fr);column-gap:9px;row-gap:2px;border:1px solid var(--line);background:var(--filter-bg);border-radius:10px;padding:9px 11px}
.launchChecklist>span>b{grid-column:1;grid-row:1/3;align-self:start;color:var(--gold);font-size:13px;line-height:1.35}
.launchChecklist>span>strong{grid-column:2;color:var(--ink);font-size:11px;line-height:1.35}
.launchChecklist>span>em{grid-column:2;color:var(--secondary-text);font-size:10px;line-height:1.45;font-style:normal}
@media(max-width:700px){.launchChecklist>span{grid-template-columns:24px minmax(0,1fr);padding:8px 9px}}
</style>
"""
if 'id="s2-launch-checklist-v1"' not in text:
    text = text.replace('</head>', css + '</head>', 1)

path.write_text(text, encoding='utf-8')
