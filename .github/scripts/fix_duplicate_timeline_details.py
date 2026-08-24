from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

marker='''  function timelineDetailHtml(e){\n    const full=String((e&&e[4])||'').trim();\n    const summary=timelineSummaryText(e);\n    if(!full || summary===full) return `<p>${full}</p>`;\n    return `<p>${summary}</p><details class="entryMore"><summary>Details</summary><div>${full}</div></details>`;\n  }\n'''

insert='''  function timelineDetailHtml(e){\n    const full=String((e&&e[4])||'').trim();\n    const summary=timelineSummaryText(e);\n    if(!full || summary===full) return `<p>${full}</p>`;\n    return `<p>${summary}</p><details class="entryMore"><summary>Details</summary><div>${full}</div></details>`;\n  }\n  function dedupeTimelineDetails(){\n    const timeline=$('timeline');\n    if(!timeline) return;\n    timeline.querySelectorAll('.entry').forEach(entry=>{\n      const details=[...entry.querySelectorAll('details.entryMore')];\n      details.slice(1).forEach(el=>el.remove());\n    });\n  }\n'''

if 'function dedupeTimelineDetails()' not in s:
    if marker not in s:
        raise SystemExit('timelineDetailHtml marker not found')
    s=s.replace(marker,insert,1)

needle="""    }).join('') || '<div class=\"emptyBuild\">No timeline entries match this filter.</div>';\n\n    const serverDay="""
replacement="""    }).join('') || '<div class=\"emptyBuild\">No timeline entries match this filter.</div>';\n    dedupeTimelineDetails();\n\n    const serverDay="""
if 'dedupeTimelineDetails();\n\n    const serverDay=' not in s:
    if needle not in s:
        raise SystemExit('timeline render insertion point not found')
    s=s.replace(needle,replacement,1)

# CSS fallback in case a stale/legacy renderer ever produces duplicate detail siblings.
css='.entry .entryMore + .entryMore{display:none!important}\n'
if css.strip() not in s:
    pos=s.find('.entryMore{margin-top:6px')
    if pos<0: raise SystemExit('entryMore css marker not found')
    s=s[:pos]+css+s[pos:]

# Recheck the requested build-layout patch is still present and structurally able
# to apply to both seasons.
checks={
    'build layout marker':'/* BUILD_LAYOUT_V2 */',
    'quick stats renderer':'function polishBuildLayout()',
    'berserker split':'function splitBerserkerPriorities(root)',
    'priority pair css':'.priorityPair{display:grid',
    'S2 conqueror':'function buildHtmlS2(cls)',
    'S2 technique priority':'Core technique investment',
    'S2 charm priority':'Core charm investment',
}
for label,text in checks.items():
    if text not in s:
        raise SystemExit(f'missing {label}: {text}')

p.write_text(s,encoding='utf-8')
print('Fixed duplicate timeline Details controls and verified build layout v2 markers.')
