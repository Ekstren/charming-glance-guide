from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

old = """      const entrySeason=TIMELINE_SEASON_WINDOWS.find(x=>Number(first[1])>=x.start&&Number(first[1])<=x.end);\n      const seasonDay=entrySeason?Math.max(1,Number(first[1])-entrySeason.start+1):1;\n      return `<article class=\"dayGroup${today?' today':''}${groupActive?' activeEvent':''}\" data-date=\"${date}\"><div class=\"dayMarker\"><span>Server Day ${first[1]}</span><small class=\"seasonDayLabel\">Season Day ${seasonDay}</small><b>${today?'CURRENT RESET':groupActive?'ACTIVE EVENT':''}</b></div>"""

new = """      const entrySeason=TIMELINE_SEASON_WINDOWS.find(x=>Number(first[1])>=x.start&&Number(first[1])<=x.end);\n      const seasonDay=entrySeason?Math.max(1,Number(first[1])-entrySeason.start+1):1;\n      const seasonNumber=entrySeason?TIMELINE_SEASON_WINDOWS.indexOf(entrySeason)+1:1;\n      return `<article class=\"dayGroup${today?' today':''}${groupActive?' activeEvent':''}\" data-date=\"${date}\"><div class=\"dayMarker\"><span>Server Day ${first[1]}</span><small class=\"seasonDayLabel\">Season ${seasonNumber} Day ${seasonDay}</small><b>${today?'CURRENT RESET':groupActive?'ACTIVE EVENT':''}</b></div>"""

if old in s:
    s = s.replace(old, new, 1)
elif new in s:
    print('timeline season-number label already applied')
    raise SystemExit(0)
else:
    raise SystemExit('timeline day-marker anchor not found')

p.write_text(s, encoding='utf-8')
print('timeline now shows Server Day # with Season # Day # underneath')
