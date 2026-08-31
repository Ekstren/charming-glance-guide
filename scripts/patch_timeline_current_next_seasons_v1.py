from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
MARK='TIMELINE_CURRENT_NEXT_SEASONS_V1'
if MARK in s:
    print('timeline current+next scope already applied')
    raise SystemExit(0)

anchor="""  function renderTimeline(){
    renderLocalTimeLabels();
    const boundaryIso=currentResetIso();
    const showPast=$('showPast').checked;
    const filtered=timelineData.filter(e=>{
      const active=eventIsActive(e,boundaryIso);
      if(!showPast && e[0]<boundaryIso && !active) return false;
      return timelineFilterMatches(e);
    });
"""
replacement="""  /* TIMELINE_CURRENT_NEXT_SEASONS_V1
     Keep the visible roadmap focused: only the current season and the immediately
     following season are eligible for timeline cards. Historical seasons never come
     back through Show past; when a season rolls over, the window advances automatically. */
  const TIMELINE_SEASON_WINDOWS=[
    {key:'s1',label:'Season 1',start:1,end:46},
    {key:'s2',label:'Season 2 · Crossed Paths',start:47,end:113},
    {key:'s3',label:'Season 3 · Aethyris',start:114,end:225},
    {key:'s4',label:'Season 4 · Hapadi',start:226,end:334},
    {key:'s5',label:'Season 5 · Ignis',start:335,end:Infinity}
  ];
  function timelineSeasonScope(boundaryIso=currentResetIso()){
    const serverDay=Math.max(1,isoDayDiff(SERVER_START_ISO,boundaryIso)+1);
    let index=TIMELINE_SEASON_WINDOWS.findIndex(x=>serverDay>=x.start&&serverDay<=x.end);
    if(index<0) index=TIMELINE_SEASON_WINDOWS.length-1;
    const current=TIMELINE_SEASON_WINDOWS[index];
    const next=TIMELINE_SEASON_WINDOWS[index+1]||null;
    return {serverDay,current,next,minDay:current.start,maxDay:next?next.end:current.end};
  }
  function timelineDataForScope(boundaryIso=currentResetIso()){
    const scope=timelineSeasonScope(boundaryIso);
    return {scope,data:timelineData.filter(e=>{
      const day=Number(e?.[1]);
      return Number.isFinite(day)&&day>=scope.minDay&&day<=scope.maxDay;
    })};
  }

  function renderTimeline(){
    renderLocalTimeLabels();
    const boundaryIso=currentResetIso();
    const {scope,data:scopedTimelineData}=timelineDataForScope(boundaryIso);
    const showPast=$('showPast').checked;
    const filtered=scopedTimelineData.filter(e=>{
      const active=eventIsActive(e,boundaryIso);
      if(!showPast && e[0]<boundaryIso && !active) return false;
      return timelineFilterMatches(e);
    });
"""
if anchor not in s:
    raise SystemExit('renderTimeline anchor not found')
s=s.replace(anchor,replacement,1)

old="""    const serverDay=Math.max(1,isoDayDiff(SERVER_START_ISO,boundaryIso)+1);
    const fixedUpcoming=timelineData.find(e=>e[0]>=boundaryIso && e[5]!=='event') || timelineData[timelineData.length-1];
    const season=serverDay<47?'Season 1':serverDay<114?'Season 2 · Crossed Paths':serverDay<226?'Season 3 · Aethyris':serverDay<335?'Season 4 · Hapadi':'Season 5 · Ignis';
    const nextDate=displayDate(fixedUpcoming[0]).toLocaleString('en-US',{month:'short',day:'numeric',timeZone:'UTC'});
    $('timelineSummary').innerHTML=`<div><span>Server day</span><strong>${serverDay}</strong></div><div><span>Current season</span><strong>${season}</strong></div><div><span>Next fixed milestone</span><strong>${fixedUpcoming[3]} · ${nextDate}</strong></div>`;
"""
new="""    const serverDay=scope.serverDay;
    const fixedUpcoming=scopedTimelineData.find(e=>e[0]>=boundaryIso && e[5]!=='event') || scopedTimelineData.filter(e=>e[5]!=='event').at(-1) || null;
    const nextMilestone=fixedUpcoming
      ? `${fixedUpcoming[3]} · ${displayDate(fixedUpcoming[0]).toLocaleString('en-US',{month:'short',day:'numeric',timeZone:'UTC'})}`
      : 'No fixed milestone loaded';
    $('timelineSummary').innerHTML=`<div><span>Server day</span><strong>${serverDay}</strong></div><div><span>Current season</span><strong>${scope.current.label}</strong></div><div><span>Next fixed milestone</span><strong>${nextMilestone}</strong></div>`;
"""
if old not in s:
    raise SystemExit('timeline summary anchor not found')
s=s.replace(old,new,1)

old_small='<summary><span>Timeline coverage & source confidence</span><small>Full refresh Aug 23 · QY Maple + current Global/community data</small></summary>'
new_small='<summary><span>Timeline coverage & source confidence</span><small>Current + next season only · QY Maple + current Global/community data</small></summary>'
if old_small not in s:
    raise SystemExit('timeline coverage summary anchor not found')
s=s.replace(old_small,new_small,1)

old_footer='<footer class="timelineSources"><p>Timeline refreshed Aug 26, 2026 / v69 timeline audit: S1/S2 scoring and seasonal floors cross-checked, Fantomon seasonal +10 ceiling restored, three Fantomon Treat tiers added, device-local reset/deadline display added, S2 Gear ceiling repaired, level-gated S2 milestones separated from calendar dates, Lv.108 Fantomon Adult and Lv.116 Demonbind Tower restored as visible entries, QY S3/S4 season lengths rechecked, Hapadi/T6 projection corrected to Server Day 226, Realm max brackets rechecked, and Astral Pact rewards made dynamic from the verified cumulative S1/S2 threshold table.</p><div class="footerLinks">'
new_footer='<footer class="timelineSources"><p>Timeline is intentionally limited to the <b>current season and the next season</b>. Older seasons stay hidden even with Show past, and farther roadmap seasons enter automatically when the season window advances. Dates use QY Maple plus current Global/community cross-checks.</p><div class="footerLinks">'
if old_footer not in s:
    raise SystemExit('timeline footer anchor not found')
s=s.replace(old_footer,new_footer,1)

p.write_text(s,encoding='utf-8')
print('limited visible timeline to current + next season')
