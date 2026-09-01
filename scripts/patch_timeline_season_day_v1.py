from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
marker='TIMELINE_SEASON_DAY_V1'
if marker in s:
    print('already applied')
    raise SystemExit(0)

css='''\n<style id="timeline-season-day-v1">\n/* TIMELINE_SEASON_DAY_V1 */\n.dayMarker .seasonDayLabel{display:block;margin-top:3px;font-size:10px;font-weight:750;line-height:1.15;color:var(--muted);letter-spacing:.02em}\n@media(max-width:620px){.dayMarker .seasonDayLabel{font-size:9px}}\n</style>\n'''
if '</head>' not in s:
    raise SystemExit('missing </head>')
s=s.replace('</head>',css+'\n</head>',1)

old="""      return `<article class=\"dayGroup${today?' today':''}${groupActive?' activeEvent':''}\" data-date=\"${date}\"><div class=\"dayMarker\"><span>Server Day ${first[1]}</span><b>${today?'CURRENT RESET':groupActive?'ACTIVE EVENT':''}</b></div><div class=\"dateBlock\"><span>${month}</span><strong>${day}</strong><small>${weekday}</small></div><div class=\"entryStack\">${entries.map(e=>{const active=eventIsActive(e,boundaryIso);return `<div class=\"entry${active?' entry-active':''}\"><span class=\"category category-${e[5]}\">${e[2]}</span><div><p><b>${e[3]}</b>${active?'<span class=\"activePill\">ACTIVE</span>':''}${e[7]==='unconfirmed'?'<span class=\"unconfirmedPill\">UNCONFIRMED</span>':''}</p>${timelineDetailHtml(e)}</div></div>`;}).join('')}</div></article>`;\n"""
new="""      const entrySeason=TIMELINE_SEASON_WINDOWS.find(x=>Number(first[1])>=x.start&&Number(first[1])<=x.end);\n      const seasonDay=entrySeason?Math.max(1,Number(first[1])-entrySeason.start+1):1;\n      return `<article class=\"dayGroup${today?' today':''}${groupActive?' activeEvent':''}\" data-date=\"${date}\"><div class=\"dayMarker\"><span>Server Day ${first[1]}</span><small class=\"seasonDayLabel\">Season Day ${seasonDay}</small><b>${today?'CURRENT RESET':groupActive?'ACTIVE EVENT':''}</b></div><div class=\"dateBlock\"><span>${month}</span><strong>${day}</strong><small>${weekday}</small></div><div class=\"entryStack\">${entries.map(e=>{const active=eventIsActive(e,boundaryIso);return `<div class=\"entry${active?' entry-active':''}\"><span class=\"category category-${e[5]}\">${e[2]}</span><div><p><b>${e[3]}</b>${active?'<span class=\"activePill\">ACTIVE</span>':''}${e[7]==='unconfirmed'?'<span class=\"unconfirmedPill\">UNCONFIRMED</span>':''}</p>${timelineDetailHtml(e)}</div></div>`;}).join('')}</div></article>`;\n"""
if old not in s:
    raise SystemExit('timeline day-group render anchor not found')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')
print('applied timeline season day label')
