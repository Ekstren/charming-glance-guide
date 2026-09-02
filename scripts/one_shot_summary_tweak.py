from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

old = """    const seasonDay=Math.max(1,serverDay-scope.current.start+1);
    const seasonNumber=Math.max(1,TIMELINE_SEASON_WINDOWS.indexOf(scope.current)+1);
    const milestoneName=fixedUpcoming?String(fixedUpcoming[3]):'No fixed milestone loaded';
    const milestoneDate=fixedUpcoming?displayDate(fixedUpcoming[0]).toLocaleString('en-US',{month:'short',day:'numeric',timeZone:'UTC'}):'';
    const milestoneDays=fixedUpcoming?Math.max(0,isoDayDiff(boundaryIso,fixedUpcoming[0])):null;
    const milestoneWhen=milestoneDays===null?'':milestoneDays===0?'today':milestoneDays===1?'in 1 day':`in ${milestoneDays} days`;
    $('timelineSummary').innerHTML=`<div><span>Server day</span><strong class=\"summaryNumber\">${serverDay}</strong></div><div><span>Season day</span><strong class=\"summaryNumber\">${seasonDay}</strong><small class=\"summaryMeta\">Season ${seasonNumber} · ${scope.current.label.replace(/^Season \\d+ · /,'')}</small></div><div><span>Next milestone</span><strong>${milestoneName}${milestoneWhen?` · ${milestoneWhen}`:''}</strong>${milestoneDate?`<small class=\"summaryMeta\">${milestoneDate}</small>`:''}</div>`;
"""

new = """    const seasonDay=Math.max(1,serverDay-scope.current.start+1);
    const milestoneName=fixedUpcoming?String(fixedUpcoming[3]):'No fixed milestone loaded';
    const milestoneDays=fixedUpcoming?Math.max(0,isoDayDiff(boundaryIso,fixedUpcoming[0])):null;
    const milestoneWhen=milestoneDays===null?'':milestoneDays===0?'today':milestoneDays===1?'1 day to go':`${milestoneDays} days to go`;
    $('timelineSummary').innerHTML=`<div><span>Server day</span><strong class=\"summaryNumber\">${serverDay}</strong></div><div><span>Season day</span><strong class=\"summaryNumber\">${seasonDay}</strong></div><div><span>Next milestone</span><strong>${milestoneName}</strong>${milestoneWhen?`<small class=\"summaryMeta\">${milestoneWhen}</small>`:''}</div>`;
"""

if old not in s:
    raise SystemExit('Timeline summary block not found')

p.write_text(s.replace(old, new, 1), encoding='utf-8')
