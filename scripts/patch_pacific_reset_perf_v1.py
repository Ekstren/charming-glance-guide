from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')
marker = 'PACIFIC_RESET_PERF_V1'

if marker in s:
    print('Pacific reset performance patch already applied')
    raise SystemExit(0)

start = s.find('  function pacificLocalMs(iso,hour=6,minute=0){')
end = s.find('  function localClockLabel(ms){', start)
if start < 0 or end < 0:
    raise SystemExit('Pacific reset helper block not found')

replacement = r'''  /* PACIFIC_RESET_PERF_V1
     S2 spans many weeks, so reset counting must be O(1), not a per-day timezone loop.
     Reuse Intl formatters and count Pacific-local reset dates arithmetically; this stays
     correct across the November PDT -> PST transition because reset eligibility is based
     on local calendar dates and an exact 6:00 AM boundary check. */
  const PACIFIC_DATE_FORMATTER = new Intl.DateTimeFormat('en-US',{
    timeZone:'America/Los_Angeles',year:'numeric',month:'2-digit',day:'2-digit'
  });
  const PACIFIC_DATE_TIME_FORMATTER = new Intl.DateTimeFormat('en-US',{
    timeZone:'America/Los_Angeles',year:'numeric',month:'2-digit',day:'2-digit',
    hour:'2-digit',minute:'2-digit',second:'2-digit',hourCycle:'h23'
  });
  function pacificLocalMs(iso,hour=6,minute=0){
    const [y,m,d]=iso.split('-').map(Number);
    const desiredAsUtc=Date.UTC(y,m-1,d,hour,minute,0);
    let guess=desiredAsUtc;
    for(let i=0;i<4;i++){
      const parts=Object.fromEntries(PACIFIC_DATE_TIME_FORMATTER.formatToParts(new Date(guess)).filter(x=>x.type!=='literal').map(x=>[x.type,x.value]));
      const shownAsUtc=Date.UTC(Number(parts.year),Number(parts.month)-1,Number(parts.day),Number(parts.hour),Number(parts.minute),Number(parts.second));
      const delta=desiredAsUtc-shownAsUtc;
      guess+=delta;
      if(Math.abs(delta)<1000) break;
    }
    return guess;
  }
  function pacificIsoAt(ms){
    const parts=Object.fromEntries(PACIFIC_DATE_FORMATTER.formatToParts(new Date(ms)).filter(x=>x.type!=='literal').map(x=>[x.type,x.value]));
    return `${parts.year}-${parts.month}-${parts.day}`;
  }
  function nextPacificResetMs(afterMs){
    const iso=pacificIsoAt(afterMs);
    const sameDay=pacificLocalMs(iso,6,0);
    return sameDay>afterMs ? sameDay : pacificLocalMs(isoAddDays(iso,1),6,0);
  }
  function isoDayOrdinal(iso){
    const [y,m,d]=iso.split('-').map(Number);
    return Math.floor(Date.UTC(y,m-1,d)/86_400_000);
  }
  function countFuturePacificResets(startMs,cutoffMs){
    if(!(cutoffMs>startMs)) return 0;
    const startIso=pacificIsoAt(startMs);
    const startReset=pacificLocalMs(startIso,6,0);
    const firstIso=startReset>startMs ? startIso : isoAddDays(startIso,1);

    const cutoffIso=pacificIsoAt(cutoffMs);
    const cutoffReset=pacificLocalMs(cutoffIso,6,0);
    const lastIso=cutoffReset<cutoffMs ? cutoffIso : isoAddDays(cutoffIso,-1);

    return Math.max(0,isoDayOrdinal(lastIso)-isoDayOrdinal(firstIso)+1);
  }
'''

s = s[:start] + replacement + s[end:]
p.write_text(s, encoding='utf-8')
print('Applied Pacific reset performance patch')
