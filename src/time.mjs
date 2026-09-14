// Pacific reset calculations and bounded memoization.
  const PACIFIC_DATE_TIME_DTF=new Intl.DateTimeFormat('en-US',{timeZone:'America/Los_Angeles',year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',second:'2-digit',hourCycle:'h23'});
  const PACIFIC_DATE_DTF=new Intl.DateTimeFormat('en-US',{timeZone:'America/Los_Angeles',year:'numeric',month:'2-digit',day:'2-digit'});
  const FUTURE_RESET_COUNT_CACHE=new Map();
export function pacificLocalMs(iso,hour=6,minute=0){
    const [y,m,d]=iso.split('-').map(Number);
    const desiredAsUtc=Date.UTC(y,m-1,d,hour,minute,0);
    let guess=desiredAsUtc;
    for(let i=0;i<4;i++){
      const parts=Object.fromEntries(PACIFIC_DATE_TIME_DTF.formatToParts(new Date(guess)).filter(x=>x.type!=='literal').map(x=>[x.type,x.value]));
      const shownAsUtc=Date.UTC(Number(parts.year),Number(parts.month)-1,Number(parts.day),Number(parts.hour),Number(parts.minute),Number(parts.second));
      const delta=desiredAsUtc-shownAsUtc;
      guess+=delta;
      if(Math.abs(delta)<1000) break;
    }
    return guess;
  }
export function pacificIsoAt(ms){
    const parts=Object.fromEntries(PACIFIC_DATE_DTF.formatToParts(new Date(ms)).filter(x=>x.type!=='literal').map(x=>[x.type,x.value]));
    return `${parts.year}-${parts.month}-${parts.day}`;
  }
export function nextPacificResetMs(afterMs){
    const iso=pacificIsoAt(afterMs);
    const sameDay=pacificLocalMs(iso,6,0);
    return sameDay>afterMs ? sameDay : pacificLocalMs(isoAddDays(iso,1),6,0);
  }
export function countFuturePacificResets(startMs,cutoffMs){
    if(!(cutoffMs>startMs)) return 0;
    const first=nextPacificResetMs(startMs);
    if(!(first<cutoffMs)) return 0;
    const key=`${first}|${cutoffMs}`;
    if(FUTURE_RESET_COUNT_CACHE.has(key)) return FUTURE_RESET_COUNT_CACHE.get(key);
    let t=first,count=0,safety=0;
    while(t<cutoffMs && safety++<500){
      count++;
      t=pacificLocalMs(isoAddDays(pacificIsoAt(t),1),6,0);
    }
    FUTURE_RESET_COUNT_CACHE.set(key,count);
    if(FUTURE_RESET_COUNT_CACHE.size>64) FUTURE_RESET_COUNT_CACHE.delete(FUTURE_RESET_COUNT_CACHE.keys().next().value);
    return count;
  }
export function isoAddDays(iso,days){
    const [y,m,d]=iso.split('-').map(Number);
    const dt=new Date(Date.UTC(y,m-1,d)); dt.setUTCDate(dt.getUTCDate()+days);
    return dt.toISOString().slice(0,10);
  }
