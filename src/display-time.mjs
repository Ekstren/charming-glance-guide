import { nextPacificResetMs } from './time.mjs';
export function viewerTimeZone(){
    try{return Intl.DateTimeFormat().resolvedOptions().timeZone||undefined;}catch(_){return undefined;}
  }

export function viewerDateTimeFormatter(options){
    const timeZone=viewerTimeZone();
    return new Intl.DateTimeFormat(undefined,timeZone?{...options,timeZone}:options);
  }

export function localClockLabel(ms){
    return viewerDateTimeFormatter({hour:'numeric',minute:'2-digit',timeZoneName:'short'}).format(new Date(ms));
  }

export function localDeadlineLabel(date,projected=false){
    const text=viewerDateTimeFormatter({month:'long',day:'numeric',year:'numeric',hour:'numeric',minute:'2-digit',timeZoneName:'short'}).format(date).replace(' at ',' · ');
    return `${projected?'Projected · ':''}${text}`;
  }

export function localShortDateTimeLabel(value){
    const date=value instanceof Date?value:new Date(value);
    if(!Number.isFinite(date.getTime())) return '—';
    return viewerDateTimeFormatter({month:'short',day:'numeric',hour:'numeric',minute:'2-digit',timeZoneName:'short'}).format(date).replace(' at ',' · ');
  }

export function nextResetLocalLabel(){ return localClockLabel(nextPacificResetMs(Date.now())); }