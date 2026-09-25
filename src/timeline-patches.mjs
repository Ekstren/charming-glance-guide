/* NEXUS_TOURNAMENT_TIMING_SEP12_V2
   Direct Charming Glance in-game evidence on Sep. 12 shows Nexus in Preparation with
   16:37:57 remaining at about 8:22 PM PDT, resolving to a 1:00 PM PDT Sep. 13 tournament
   start. Registration/preparation is Sep. 12; the actual tournament belongs on Sep. 13.
   The following 14-day projections move with the corrected Sunday cadence. */
(()=>{
  const CORRECTIONS={
    '2026-09-12':{to:'2026-09-13',serverDay:61,seasonDay:15,summary:'Qualified server teams compete in cross-server 4v4; brackets and predictions are in game.'},
    '2026-09-26':{to:'2026-09-27',serverDay:75,seasonDay:29,summary:'Qualified server teams compete in cross-server 4v4; brackets and predictions are in game.'},
    '2026-10-10':{to:'2026-10-11',serverDay:89,seasonDay:43,summary:'Qualified server teams compete in cross-server 4v4; brackets and predictions are in game.'},
    '2026-10-24':{to:'2026-10-25',serverDay:103,seasonDay:57,summary:'Qualified server teams compete in cross-server 4v4; brackets and predictions are in game.'}
  };

  function dateParts(iso){
    const d=new Date(`${iso}T12:00:00Z`);
    return {
      month:d.toLocaleString('en-US',{month:'short',timeZone:'UTC'}),
      day:d.getUTCDate(),
      weekday:d.toLocaleString('en-US',{weekday:'short',timeZone:'UTC'})
    };
  }

  function createGroup(iso,cfg){
    const p=dateParts(iso);
    const article=document.createElement('article');
    article.className='dayGroup';
    article.dataset.date=iso;
    article.innerHTML=`<div class="dayMarker"><span>Server Day ${cfg.serverDay}</span><small class="seasonDayLabel">Season 2 Day ${cfg.seasonDay}</small><b></b></div><div class="dateBlock"><span>${p.month}</span><strong>${p.day}</strong><small>${p.weekday}</small></div><div class="entryStack"></div>`;
    return article;
  }

  function ensureGroup(timeline,iso,cfg){
    let target=timeline.querySelector(`.dayGroup[data-date="${iso}"]`);
    if(target) return target;
    target=createGroup(iso,cfg);
    const next=[...timeline.querySelectorAll('.dayGroup')].find(g=>(g.dataset.date||'')>iso);
    if(next) timeline.insertBefore(target,next); else timeline.append(target);
    return target;
  }

  let patchQueued=false;
  function patchTimeline(){
    patchQueued=false;
    const timeline=document.getElementById('timeline');
    if(!timeline) return;
    const nexusEntries=[...timeline.querySelectorAll('.entry')].filter(entry=>entry.querySelector('b')?.textContent.trim()==='Nexus Tournament · 4v4');
    if(!nexusEntries.length) return;

    nexusEntries.forEach(entry=>{
      const sourceGroup=entry.closest('.dayGroup');
      const from=sourceGroup?.dataset.date||'';
      const cfg=CORRECTIONS[from];
      if(!cfg) return;
      const targetGroup=ensureGroup(timeline,cfg.to,cfg);
      const detail=entry.querySelector('div > p + p');
      if(detail) detail.textContent=cfg.summary;
      targetGroup.querySelector('.entryStack')?.append(entry);
      if(sourceGroup && !sourceGroup.querySelector('.entryStack .entry')) sourceGroup.remove();
    });
  }

  function queuePatch(){
    if(patchQueued) return;
    patchQueued=true;
    requestAnimationFrame(patchTimeline);
  }

  function initPatch(){
    const timeline=document.getElementById('timeline');
    if(!timeline) return;
    new MutationObserver(queuePatch).observe(timeline,{childList:true,subtree:true});
    queuePatch();
  }

  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',initPatch,{once:true});
  else initPatch();
})();

/* TIMELINE_SUMMARY_ONLY_V1
   Timeline research/source/confidence UI is intentionally kept out of the player-facing timeline.
   Provenance remains in maintained source comments/data rather than secondary disclosure panels. */
(()=>{
  function enforceSummaryOnly(){
    document.querySelector('.timelineIntelWrap')?.remove();
    document.querySelector('.timelineSources')?.remove();
    document.querySelectorAll('#timeline details.entryMore').forEach(el=>el.remove());
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',enforceSummaryOnly,{once:true});
  else enforceSummaryOnly();
})();
