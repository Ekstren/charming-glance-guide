from pathlib import Path

path = Path('index.html')
html = path.read_text(encoding='utf-8')

css = r'''

/* TIMELINE_REPORT_BUTTON_V1 */
.timelineReportRow{display:flex;justify-content:flex-end;margin-top:8px}
.timelineReportLink{display:inline-flex;align-items:center;gap:5px;color:var(--muted);font-size:9px;font-weight:800;letter-spacing:.04em;text-decoration:none;border:1px solid var(--line);border-radius:999px;padding:4px 8px;transition:border-color .15s,color .15s,background .15s}
.timelineReportLink:hover{color:var(--ink);border-color:var(--muted);background:var(--filter-bg)}
.timelineReportLink:focus-visible{outline:2px solid var(--green);outline-offset:2px}
'''
html = html.replace(css, '', 1)

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
html = html.replace(helper, '', 1)

with_report = "<p><b>${e[3]}</b>${active?'<span class=\"activePill\">ACTIVE</span>':''}</p>${timelineDetailHtml(e)}${timelineReportHtml(e)}</div></div>`;}).join('')"
without_report = "<p><b>${e[3]}</b>${active?'<span class=\"activePill\">ACTIVE</span>':''}</p>${timelineDetailHtml(e)}</div></div>`;}).join('')"
if with_report in html:
    html = html.replace(with_report, without_report, 1)

if 'timelineReportHtml(' in html or 'TIMELINE_REPORT_BUTTON_V1' in html or 'timelineReportLink' in html:
    raise SystemExit('Report-button code still present after cleanup')

path.write_text(html, encoding='utf-8')
print('Removed timeline Report button and helper code')
