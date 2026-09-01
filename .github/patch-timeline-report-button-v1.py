from pathlib import Path

path = Path('index.html')
html = path.read_text(encoding='utf-8')

MARKER = 'TIMELINE_REPORT_BUTTON_V1'
if MARKER in html:
    print('Timeline report button already applied')
    raise SystemExit(0)

css = r'''

/* TIMELINE_REPORT_BUTTON_V1 */
.timelineReportRow{display:flex;justify-content:flex-end;margin-top:8px}
.timelineReportLink{display:inline-flex;align-items:center;gap:5px;color:var(--muted);font-size:9px;font-weight:800;letter-spacing:.04em;text-decoration:none;border:1px solid var(--line);border-radius:999px;padding:4px 8px;transition:border-color .15s,color .15s,background .15s}
.timelineReportLink:hover{color:var(--ink);border-color:var(--muted);background:var(--filter-bg)}
.timelineReportLink:focus-visible{outline:2px solid var(--green);outline-offset:2px}
'''
if '</style>' not in html:
    raise SystemExit('Could not find closing style tag')
html = html.replace('</style>', css + '\n</style>', 1)

helper_anchor = "  function renderTimeline(){\n"
helper = r'''  function timelineReportPlainText(value){
    return String(value||'')
      .replace(/<br\s*\/?>/gi,'\n')
      .replace(/<\/p>|<\/div>|<\/span>/gi,'\n')
      .replace(/<[^>]*>/g,' ')
      .replace(/&nbsp;/g,' ')
      .replace(/&amp;/g,'&')
      .replace(/&lt;/g,'<')
      .replace(/&gt;/g,'>')
      .replace(/\s+\n/g,'\n')
      .replace(/\n\s+/g,'\n')
      .replace(/[ \t]{2,}/g,' ')
      .trim();
  }
  function timelineReportUrl(e){
    const eventName=String((e&&e[3])||'Timeline event');
    const date=String((e&&e[0])||'');
    const serverDay=String((e&&e[1])||'');
    const category=String((e&&e[2])||'');
    const details=timelineReportPlainText((e&&e[4])||'');
    const title=`[Timeline Report] ${eventName} · ${date}`;
    const body=[
      '### Timeline event',
      `- **Event:** ${eventName}`,
      `- **Date:** ${date}`,
      `- **Server day:** ${serverDay}`,
      `- **Category:** ${category}`,
      '',
      '### Current timeline details',
      details || '_No details are currently loaded for this entry._',
      '',
      '### What seems wrong?',
      '<!-- Tell us what looks incorrect. A screenshot, source link, server day, season day, or older-server timing is especially helpful. -->',
      '',
      '> Generated from the Charming Glance timeline. The automated timeline watcher will re-check this event against current sources after the issue is submitted.'
    ].join('\n');
    return `https://github.com/Ekstren/charming-glance-guide/issues/new?title=${encodeURIComponent(title)}&body=${encodeURIComponent(body)}`;
  }
  function timelineReportHtml(e){
    const href=timelineReportUrl(e).replace(/&/g,'&amp;').replace(/"/g,'&quot;');
    const label=`Report possible problem with ${String((e&&e[3])||'timeline event')}`.replace(/"/g,'&quot;');
    return `<div class="timelineReportRow"><a class="timelineReportLink" href="${href}" target="_blank" rel="noopener noreferrer" aria-label="${label}" title="Report this timeline event">Report</a></div>`;
  }

'''
if helper_anchor not in html:
    raise SystemExit('Could not find renderTimeline anchor')
html = html.replace(helper_anchor, helper + helper_anchor, 1)

old = "<p><b>${e[3]}</b>${active?'<span class=\"activePill\">ACTIVE</span>':''}</p>${timelineDetailHtml(e)}</div></div>`;}).join('')"
new = "<p><b>${e[3]}</b>${active?'<span class=\"activePill\">ACTIVE</span>':''}</p>${timelineDetailHtml(e)}${timelineReportHtml(e)}</div></div>`;}).join('')"
if old not in html:
    raise SystemExit('Could not find timeline entry render fragment')
html = html.replace(old, new, 1)

path.write_text(html, encoding='utf-8')
print('Added Report links to timeline cards')
