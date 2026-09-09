from pathlib import Path
import re

path = Path('index.html')
s = path.read_text(encoding='utf-8')

old_warlord = "['2026-09-12',60,'Dungeon','Warlord’s Rest','CONFIRMED CHARMING GLANCE DATE + NORMAL REQUIREMENTS: an in-game Warlord’s Rest — Normal countdown captured on Sep. 8 at about 8:54 PM PDT showed 3d 09h 05m 54s remaining, resolving exactly to the Sep. 12, 2026 6:00 AM PDT server reset. The same Charming Glance unlock screen directly shows Player Lv.130 and 3.55M Power for Normal. Existing higher-difficulty requirements remain Hard 5M · Nightmare 6M; those two thresholds are not established by this Normal-mode screenshot.','dungeon'],"
new_warlord = "['2026-09-12',60,'Dungeon','Warlord’s Rest','Player Lv.130 · Normal 3.55M · Hard 5M · Nightmare 6M','dungeon'],"
if old_warlord not in s:
    raise SystemExit('Current Warlord’s Rest row not found')
s = s.replace(old_warlord, new_warlord, 1)

anchor = """  function timelineSummaryText(e){
    const text=String((e&&e[4])||'').trim();
    const title=String((e&&e[3])||'');
"""
if anchor not in s:
    raise SystemExit('timelineSummaryText anchor not found')
replacement = anchor + """    const type=String((e&&e[2])||'');
    // TIMELINE_PLAIN_EVENT_COPY_V1: user-facing cards summarize the event itself.
    // Research confidence/source prose stays in the maintained raw row when useful,
    // but CONFIRMED / UNCONFIRMED / PROJECTED-style audit language is not shown on cards.
    if(title==='Warlord’s Rest') return 'Player Lv.130 · Normal 3.55M · Hard 5M · Nightmare 6M';
    if(title==='Server Tournament') return 'Registration opens Sep. 4 · tournament Sep. 5.';
    if(title==='Nexus Tournament · 4v4') return '4v4 Nexus Tournament · Top-4 qualification format; brackets and prediction phases are handled in game.';
    if(title==='Acme Nexus') return 'Loong Haven seasonal map · gateway to Aethyris.';
    if(title==='Aethyris opens') return 'Season 3 · Aethyris · Tier 5 · Nexus grouping expands from 4 servers to an 8-server pool.';
    if(title==='Crystal Spiral Tree') return 'Aethyris’s first dungeon · current older-server guidance lists Hard at 9M.';
    if(title==='Gift code · CRYSTAL') return '300 Raw Ore + 1 Stellatie · redeem before the reported Sep. 15 expiry.';
    if(title==='Official Top-Up Platform events open') return 'Cumulative Top-up Lottery + Daily Top-up Sign-in open on the official top-up platform.';
    if(title==='Vegetables Fairy Collab Pt. 2') return 'Daily sign-in, Veggie Shop, Veggie Shuffle, Lemon Whale purification, Cabbage Dog Fantomon and Part 2 Visages.';
"""
s = s.replace(anchor, replacement, 1)

old_default = """    if(title==='Vegetable Fairy Part Two') return 'Expected Sep 7 from a secondary event guide; no official Global or Charming Glance confirmation yet.';
    if(text.length<=170) return text;
    const sentences=text.split(/\\.\\s+/).filter(Boolean);
    let summary=sentences[0]||text;
"""
new_default = """    if(title==='Vegetable Fairy Part Two') return 'Vegetable Fairy Part Two event.';
    let displayText=text;
    if(/^(?:CONFIRMED|UNCONFIRMED|PROJECTED|EXPECTED|STRONGLY SUPPORTED|OFFICIAL GLOBAL NAME)/i.test(displayText)){
      const colon=displayText.indexOf(':');
      if(colon>=0 && colon<180) displayText=displayText.slice(colon+1).trim();
      displayText=displayText
        .replace(/^(?:CONFIRMED|UNCONFIRMED|PROJECTED|EXPECTED|STRONGLY SUPPORTED)\\b[^.]{0,180}\\.\\s*/i,'')
        .replace(/\\b(?:CONFIRMED|UNCONFIRMED|PROJECTED|STRONGLY SUPPORTED)\\b/gi,'')
        .replace(/\\s{2,}/g,' ')
        .trim();
    }
    if(displayText.length<=170) return displayText;
    const sentences=displayText.split(/\\.\\s+/).filter(Boolean);
    let summary=sentences[0]||displayText;
"""
if old_default not in s:
    raise SystemExit('timelineSummaryText default block not found')
s = s.replace(old_default, new_default, 1)

old_detail = """    const summary=timelineSummaryText(e);
    if(!full || summary===full) return `<p>${full}</p>`;
    return `<p>${summary}</p><details class=\"entryMore\"><summary>Details</summary><div>${full}</div></details>`;
"""
new_detail = """    const summary=timelineSummaryText(e);
    const evidenceHeavy=/^(?:CONFIRMED|UNCONFIRMED|PROJECTED|EXPECTED|STRONGLY SUPPORTED|OFFICIAL GLOBAL NAME)/i.test(full);
    if(!full || summary===full || evidenceHeavy) return `<p>${summary||full}</p>`;
    return `<p>${summary}</p><details class=\"entryMore\"><summary>Details</summary><div>${full}</div></details>`;
"""
if old_detail not in s:
    raise SystemExit('timelineDetailHtml block not found')
s = s.replace(old_detail, new_detail, 1)

for needle in [
    "'Warlord’s Rest','Player Lv.130 · Normal 3.55M · Hard 5M · Nightmare 6M'",
    'TIMELINE_PLAIN_EVENT_COPY_V1',
    "if(title==='Nexus Tournament · 4v4')",
    'const evidenceHeavy='
]:
    if needle not in s:
        raise SystemExit(f'Missing expected marker: {needle}')

path.write_text(s, encoding='utf-8')
print('Cleaned timeline event-facing copy and normalized Warlord’s Rest.')
