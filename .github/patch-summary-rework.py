from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

old_css = '.summary{grid-template-columns:170px 1fr 1.4fr;'
new_css = '.summary{grid-template-columns:170px 170px 1fr;'
if old_css in s:
    s = s.replace(old_css, new_css, 1)
elif new_css not in s:
    raise SystemExit('Could not find summary grid CSS')

old_style = '.summary div:first-child strong{color:var(--green);font-size:30px;line-height:1}.summary .summarySeasonDay{color:var(--green);margin-top:5px;font-size:11px;font-weight:800;display:block}'
new_style = '.summary .summaryNumber{color:var(--green);font-size:30px;line-height:1}.summary .summaryMeta{color:var(--muted);margin-top:6px;font-size:10px;font-weight:750;display:block}'
if old_style in s:
    s = s.replace(old_style, new_style, 1)
elif new_style not in s:
    raise SystemExit('Could not find summary number/meta CSS')

old_js = '''    const nextMilestone=fixedUpcoming
      ? `${fixedUpcoming[3]} · ${displayDate(fixedUpcoming[0]).toLocaleString('en-US',{month:'short',day:'numeric',timeZone:'UTC'})}`
      : 'No fixed milestone loaded';
    const seasonDay=Math.max(1,serverDay-scope.current.start+1);
    $('timelineSummary').innerHTML=`<div><span>Server day</span><strong>${serverDay}</strong></div><div><span>Current season</span><strong>${scope.current.label}</strong><small class="summarySeasonDay">Season Day ${seasonDay}</small></div><div><span>Next fixed milestone</span><strong>${nextMilestone}</strong></div>`;
'''
new_js = '''    const seasonDay=Math.max(1,serverDay-scope.current.start+1);
    const seasonNumber=Math.max(1,TIMELINE_SEASON_WINDOWS.indexOf(scope.current)+1);
    const milestoneName=fixedUpcoming?String(fixedUpcoming[3]):'No fixed milestone loaded';
    const milestoneDate=fixedUpcoming?displayDate(fixedUpcoming[0]).toLocaleString('en-US',{month:'short',day:'numeric',timeZone:'UTC'}):'';
    const milestoneDays=fixedUpcoming?Math.max(0,isoDayDiff(boundaryIso,fixedUpcoming[0])):null;
    const milestoneWhen=milestoneDays===null?'':milestoneDays===0?'today':milestoneDays===1?'in 1 day':`in ${milestoneDays} days`;
    $('timelineSummary').innerHTML=`<div><span>Server day</span><strong class="summaryNumber">${serverDay}</strong></div><div><span>Season day</span><strong class="summaryNumber">${seasonDay}</strong><small class="summaryMeta">Season ${seasonNumber} · ${scope.current.label.replace(/^Season \\d+ · /,'')}</small></div><div><span>Next milestone</span><strong>${milestoneName}${milestoneWhen?` · ${milestoneWhen}`:''}</strong>${milestoneDate?`<small class="summaryMeta">${milestoneDate}</small>`:''}</div>`;
'''
if old_js in s:
    s = s.replace(old_js, new_js, 1)
elif new_js not in s:
    raise SystemExit('Could not find timeline summary JS')

p.write_text(s, encoding='utf-8')
