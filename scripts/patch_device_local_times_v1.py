from pathlib import Path

runtime_path = Path('assets/runtime.js')
index_path = Path('index.html')
runtime = runtime_path.read_text(encoding='utf-8')
index = index_path.read_text(encoding='utf-8')

old = """  function finishScoreCutoffMs(cfg=activeCalcConfig()){
    const days=finishEarlyDaysValue();
    if(days<=0) return cfg.end.getTime();
    const endIso=pacificIsoAt(cfg.end.getTime());
    const wholeDays=Math.floor(days);
    const hasHalf=days-wholeDays>=0.5;
    // Preserve reset-day semantics across DST. A half day lands at 6 PM Pacific on
    // the preceding local date instead of subtracting a blind 12h from a UTC timestamp.
    const cutoffIso=isoAddDays(endIso,-(wholeDays+(hasHalf?1:0)));
    const cutoff=pacificLocalMs(cutoffIso,hasHalf?18:6,0);
    return Math.min(cfg.end.getTime(),cutoff);
  }
"""
new = """  function finishScoreCutoffMs(cfg=activeCalcConfig()){
    const days=finishEarlyDaysValue();
    if(days<=0) return cfg.end.getTime();
    // FINISH_EARLY_DEVICE_LOCAL_V1: \"days early\" is an elapsed duration from the
    // actual season-end instant. Server/reset math remains Pacific internally, while
    // any displayed cutoff/deadline is formatted in the viewer device's local zone.
    const cutoff=cfg.end.getTime()-(days*24*60*60*1000);
    return Math.min(cfg.end.getTime(),cutoff);
  }
"""
if old not in runtime:
    raise SystemExit('finishScoreCutoffMs block not found')
runtime = runtime.replace(old, new, 1)

anchor = """  function localDeadlineLabel(date,projected=false){
    const text=new Intl.DateTimeFormat(undefined,{month:'long',day:'numeric',year:'numeric',hour:'numeric',minute:'2-digit',timeZoneName:'short'}).format(date).replace(' at ',' · ');
    return `${projected?'Projected · ':''}${text}`;
  }
"""
replacement = anchor + """  function localShortDateTimeLabel(value){
    const date=value instanceof Date?value:new Date(value);
    if(!Number.isFinite(date.getTime())) return '—';
    return new Intl.DateTimeFormat(undefined,{month:'short',day:'numeric',hour:'numeric',minute:'2-digit',timeZoneName:'short'}).format(date).replace(' at ',' · ');
  }
"""
if anchor not in runtime:
    raise SystemExit('localDeadlineLabel anchor not found')
runtime = runtime.replace(anchor, replacement, 1)

# Device-local timeline summaries for rows that previously exposed hard-coded Pacific conversions.
runtime = runtime.replace(
    "    if(title==='Gift code · CRYSTAL') return '300 Raw Ore + 1 Stellatie · reported cutoff Sep. 14 at 10:00 PM PDT.';",
    "    if(title==='Gift code · CRYSTAL'){const t=Date.parse(String((e&&e[8])||''));return `300 Raw Ore + 1 Stellatie · reported cutoff ${Number.isFinite(t)?localShortDateTimeLabel(t):'Sep. 15 source cutoff'}.`;}",
)
runtime = runtime.replace(
    "    if(title.startsWith('Weekly gift code')) return '2,000 Rolla + 120 Dawnium. Expired at the reported Aug 25 00:00 UTC-5 cutoff (Aug 24, 10:00 PM PDT).';",
    "    if(title.startsWith('Weekly gift code')) return `2,000 Rolla + 120 Dawnium. Expired ${localShortDateTimeLabel('2026-08-25T05:00:00Z')}.`;",
)
runtime = runtime.replace(
    "    if(title==='Gift code · VEGGIE') return 'Official Global Discord: 10 Rare Auroral Badges + 80 Dawnium. Expires Sep 8 at 00:00 UTC-5 = Sep 7 at 10:00 PM PDT; redeem before then.';",
    "    if(title==='Gift code · VEGGIE'){const t=Date.parse(String((e&&e[8])||''));return `Official Global Discord: 10 Rare Auroral Badges + 80 Dawnium. Expires ${Number.isFinite(t)?localShortDateTimeLabel(t):'at the stored source cutoff'}; redeem before then.`;}",
)
runtime = runtime.replace(
    "    if(title==='Loong Haven opens') return 'Confirmed Aug 30 at 6:00 AM PDT. Gates: Lv.106 T4; Lv.108 + Numbuville + Mythic duplicate for Fantomon Adult; Lv.116 Demonbind Tower.';",
    "    if(title==='Loong Haven opens') return `Confirmed ${localShortDateTimeLabel(S1_END)}. Gates: Lv.106 T4; Lv.108 + Numbuville + Mythic duplicate for Fantomon Adult; Lv.116 Demonbind Tower.`;",
)

# Hidden maintenance/source rows should not carry Pacific conversions into future UI reuse either.
runtime = runtime.replace('Season 2 Day 1 begins Aug 30 at the 6:00 AM PDT reset. On Aug 26 at about 8:15 AM PDT,', 'Season 2 Day 1 begins at the Aug 30 server reset. On Aug 26,')
runtime = runtime.replace('confirmed for the Aug 30 6:00 AM PDT reset', 'confirmed for the Aug 30 server reset')
runtime = runtime.replace('which is Sep. 7 at 10:00 PM PDT for Charming Glance. Redeem before 10:00 PM PDT Sep. 7.', 'with its stored expiry timestamp converted to the viewer\'s local timezone.')
runtime = runtime.replace('which is Sep. 14 at 10:00 PM PDT for Charming Glance.', 'with its stored expiry timestamp converted to the viewer\'s local timezone.')
runtime = runtime.replace('which is Sep. 6 at 10:00 PM PDT for Charming Glance:', 'with the stored start timestamp converted to the viewer\'s local timezone:')
runtime = runtime.replace('without claiming a 6:00 AM PDT start.', 'without claiming a server-reset start time.')

old_intro = """        <p><b>Charming Glance calendar:</b> Day 1 = Jul 15. The server reset is converted automatically to <b id=\"timelineResetLocal\">this device's local time</b>. Season 2 / <b>Crossed Paths</b> is <b>confirmed for Server Day 47 / Aug 30 at the 6:00 AM PDT reset</b> on Charming Glance. On Aug 26 at about 8:15 AM PDT, the in-game season countdown showed 3d 21h remaining, aligning with the Aug 30 reset; Prydwen's Day-47 model independently matches that timing. <b>QY Maple is now the primary season-day table</b> for later unlock timing; legacy Qenu/Limitless rows are retained only when they add a useful conflict note rather than creating duplicate milestones.</p>"""
new_intro = """        <p><b>Charming Glance calendar:</b> Day 1 = Jul 15. The server reset is converted automatically to <b id=\"timelineResetLocal\">this device's local time</b>. Season 2 / <b>Crossed Paths</b> is <b>confirmed for Server Day 47 / Aug 30 at the server reset</b> on Charming Glance. On Aug 26, the in-game season countdown showed 3d 21h remaining, aligning with the Aug 30 reset; Prydwen's Day-47 model independently matches that timing. <b>QY Maple is now the primary season-day table</b> for later unlock timing; legacy Qenu/Limitless rows are retained only when they add a useful conflict note rather than creating duplicate milestones.</p>"""
if old_intro not in index:
    raise SystemExit('timeline intro block not found')
index = index.replace(old_intro, new_intro, 1)
index = index.replace('title="Stop counting Character score and projected resources this many reset-days before season end"', 'title="Stop counting Character score and projected resources this many days before season end"', 1)

runtime_path.write_text(runtime, encoding='utf-8')
index_path.write_text(index, encoding='utf-8')
print('patched device-local visible time handling')
