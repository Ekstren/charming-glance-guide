from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')

css = r'''
.entryMore{margin-top:6px;color:var(--muted);font-size:10px}
.entryMore summary{cursor:pointer;color:var(--green);font-weight:800;list-style:none;display:inline-flex;align-items:center;gap:5px}
.entryMore summary::-webkit-details-marker{display:none}
.entryMore summary:after{content:'+';font-size:11px}
.entryMore[open] summary:after{content:'−'}
.entryMore div{margin-top:6px;color:var(--secondary-text);font-size:11px;line-height:1.5}
'''.strip()
if '.entryMore{' not in text:
    text = text.replace('</style>', css + '\n</style>', 1)

helper = r'''
  function timelineSummaryText(e){
    const text=String((e&&e[4])||'').trim();
    const title=String((e&&e[3])||'');
    if(title.startsWith('Oceanic Festival')) return 'Global Aug 18–31. Prioritize Beach Shovels; Bingo Draw 2 overlaps on Charming Glance, so Destiny Fruit spending can progress both events.';
    if(title.startsWith('Bingo Draw')) return 'Do dailies first; roughly 60–80 Destiny Fruits usually clears the normal board. This run overlaps Oceanic, so Fruit spending progresses both.';
    if(title.startsWith('Lucky Scratch')) return 'Spend saved Material Realm tools to generate scratch cards. Aug 26–31 overlaps Oceanic, so Realm activity can also progress Beach Shovel objectives.';
    if(title.startsWith('Weekly gift code')) return '2,000 Rolla + 120 Dawnium. Redeem by Aug 25.';
    if(title.startsWith('Grand Treasure Hunt')){
      const reward=(text.match(/Lv\.5:\s*([^·.]+)/)||[])[1];
      return reward ? `Lv.5 reward: ${reward.trim()}. Auroradrasil Energy carries over.` : 'Check the Lv.5 reward before spending saved Auroradrasil Energy; unused Energy carries over.';
    }
    if(title==='Season 2 final-day prep') return 'Save dungeon attempts for S2: buy 2 and use none, then buy 2 more after reset for up to 6 day-one runs. Treat 36h Bed EXP banking as unconfirmed until the transition notice verifies it.';
    if(title==='Loong Haven opens') return 'Season 2 begins. Key level gates: Lv.106 T4/Loong Haven Five, Lv.108 Fantomon Adult/Materialization, Lv.116 Demonbind Tower.';
    if(title==='Vegetable Fairy Part Two') return 'Expected Sep 7 from a secondary event guide; no official Global or Charming Glance confirmation yet.';
    if(text.length<=170) return text;
    const sentences=text.split(/\.\s+/).filter(Boolean);
    let summary=sentences[0]||text;
    if(summary.length<95 && sentences.length>1) summary += '. ' + sentences[1];
    if(summary.length>170) summary=summary.slice(0,167).replace(/\s+\S*$/,'')+'…';
    if(summary && !/[.!?…]$/.test(summary)) summary+='.';
    return summary;
  }
  function timelineDetailHtml(e){
    const full=String((e&&e[4])||'').trim();
    const summary=timelineSummaryText(e);
    if(!full || summary===full) return `<p>${full}</p>`;
    return `<p>${summary}</p><details class="entryMore"><summary>Details</summary><div>${full}</div></details>`;
  }
'''.rstrip()
anchor = '  function renderTimeline(){'
if 'function timelineSummaryText(e)' not in text:
    if anchor not in text:
        raise SystemExit('Could not find renderTimeline anchor')
    text = text.replace(anchor, helper + '\n' + anchor, 1)

old_entry = '''<div><p><b>${e[3]}</b>${active?'<span class="activePill">ACTIVE</span>':''}${e[7]==='unconfirmed'?'<span class="unconfirmedPill">UNCONFIRMED</span>':''}</p><p>${e[4]}</p></div>'''
new_entry = '''<div><p><b>${e[3]}</b>${active?'<span class="activePill">ACTIVE</span>':''}${e[7]==='unconfirmed'?'<span class="unconfirmedPill">UNCONFIRMED</span>':''}</p>${timelineDetailHtml(e)}</div>'''
if old_entry in text:
    text = text.replace(old_entry, new_entry, 1)
elif new_entry not in text:
    raise SystemExit('Could not find timeline entry renderer')

old_now = '''const cards=activeEvents.map(e=>`<div class="timelineNowCard"><strong>${e[3]}</strong><small>${e[4]}</small></div>`).join('');'''
new_now = '''const cards=activeEvents.map(e=>`<div class="timelineNowCard"><strong>${e[3]}</strong><small>${timelineSummaryText(e)}</small></div>`).join('');'''
if old_now in text:
    text = text.replace(old_now, new_now, 1)
elif new_now not in text:
    raise SystemExit('Could not find Active now renderer')

path.write_text(text, encoding='utf-8')
