/* BUILD_HERO_LAYOUT_ICONS_V1
   Legacy asset filename/hook; decorative icons are intentionally removed.
   BUILD_HERO_LAYOUT_V2 reflows the existing generated build summary only. */
(()=>{
  const ICON_SELECTOR='.buildGearIcon,.rollStatIcon,.buildSubstatIcon';
  const DESKTOP_ROLL=window.matchMedia('(min-width:861px)');
  const GEM_PROFILES={
    Conqueror:{
      Sword:'Obsidian > Amethyst ≥ Ruby',
      Gauntlets:'Obsidian > Amethyst ≥ Citrine',
      Helmet:'Citrine > Beryl = Sapphire',
      Chest:'Moonstone > Beryl = Sapphire',
      Boots:'Amethyst > Citrine'
    },
    Guardian:{
      tank:{
        Sword:'Obsidian > Amethyst ≥ Ruby',
        Shield:'Moonstone > Sapphire > Citrine',
        Helmet:'Sapphire > Citrine > Beryl',
        Chest:'Moonstone > Beryl = Sapphire',
        Boots:'Amethyst > Citrine'
      },
      dps:{
        Sword:'Obsidian > Amethyst ≥ Ruby',
        Shield:'Moonstone > Sapphire > Citrine',
        Helmet:'Sapphire > Citrine > Beryl',
        Chest:'Moonstone > Beryl = Sapphire',
        Boots:'Amethyst > Citrine'
      }
    },
    Destroyer:{
      Staff:'Obsidian > Amethyst',
      Codex:'Obsidian > Amethyst > Moonstone',
      Helmet:'Citrine > Beryl = Sapphire',
      Chest:'Moonstone',
      Boots:'Amethyst'
    },
    Dominator:{
      dps:{
        Staff:'Obsidian > Amethyst > Ruby',
        Orb:'Obsidian > Amethyst > Ruby',
        Helmet:'Citrine',
        Chest:'Moonstone',
        Boots:'Amethyst > Ruby'
      },
      heals:{
        Staff:'Amethyst',
        Orb:'Amber > Citrine',
        Helmet:'Amber > Citrine',
        Chest:'Moonstone',
        Boots:'Amber > Citrine'
      }
    }
  };

  function removeLegacyIcons(root){
    root?.querySelectorAll?.(ICON_SELECTOR).forEach(el=>el.remove());
  }

  function activeClass(){
    return document.querySelector('#classTabs button.active')?.dataset.class||'';
  }

  function roleFor(cls){
    try{
      if(cls==='Guardian') return localStorage.getItem('sxs-build-guardian-mode')==='dps'?'dps':'tank';
      if(cls==='Dominator') return localStorage.getItem('sxs-build-dominator-mode')==='heals'?'heals':'dps';
    }catch(_){/* fall through */}
    return cls==='Guardian'?'tank':'dps';
  }

  function gemProfileFor(cls){
    const profile=GEM_PROFILES[cls];
    if(!profile) return null;
    if(cls==='Guardian'||cls==='Dominator') return profile[roleFor(cls)]||null;
    return profile;
  }

  function applyGemPriorities(quick){
    const cls=activeClass();
    const mode=(cls==='Guardian'||cls==='Dominator')?roleFor(cls):'dps';
    const profile=gemProfileFor(cls);
    const rows=[...quick.querySelectorAll(':scope > .quickGearGrid > .quickGearRow')];
    const sig=`${cls}|${mode}`;
    const complete=rows.length===5&&rows.every(row=>row.querySelector(':scope > .quickGemLine'))&&quick.querySelector(':scope > .quickGemNote');
    if(profile&&quick.dataset.gemPrioritySig===sig&&complete) return;

    quick.querySelectorAll(':scope > .quickGearGrid > .quickGearRow > .quickGemLine').forEach(el=>el.remove());
    quick.querySelector(':scope > .quickGemNote')?.remove();
    delete quick.dataset.gemPrioritySig;
    if(!profile||rows.length!==5) return;

    rows.forEach(row=>{
      const slot=row.querySelector(':scope > b')?.textContent.trim();
      const gems=slot?profile[slot]:null;
      if(!gems) return;
      const line=document.createElement('div');
      line.className='quickGemLine';
      const label=document.createElement('span');
      label.className='quickGemLabel';
      label.textContent='Gems';
      const text=document.createElement('span');
      text.className='quickGemText';
      text.textContent=gems;
      line.append(label,text);
      row.append(line);
    });

    const grid=quick.querySelector(':scope > .quickGearGrid');
    if(grid&&rows.every(row=>row.querySelector(':scope > .quickGemLine'))){
      const note=document.createElement('div');
      note.className='quickGemNote';
      note.textContent='S2 Lv130+: 2 gems per gear slot · duplicates allowed';
      grid.insertAdjacentElement('afterend',note);
      quick.dataset.gemPrioritySig=sig;
    }
  }

  function prepQuick(quick){
    if(!quick) return;
    removeLegacyIcons(quick);
    const title=quick.querySelector(':scope > .quickTitle');
    if(title&&title.textContent.trim()!=='Gear & stat priorities') title.textContent='Gear & stat priorities';
    applyGemPriorities(quick);
  }

  function setRollMode(roll,{resetMobile=false}={}){
    if(!roll) return;
    const summary=roll.querySelector(':scope > summary');
    if(DESKTOP_ROLL.matches){
      roll.open=true;
      summary?.setAttribute('aria-disabled','true');
      if(summary) summary.tabIndex=-1;
    }else{
      summary?.removeAttribute('aria-disabled');
      summary?.removeAttribute('tabindex');
      if(resetMobile) roll.open=false;
    }
  }

  function syncRoll(quick,right){
    const source=quick.querySelector(':scope > .rollGuide');
    if(!source) return;
    const sourceHtml=source.innerHTML;
    const sig=source.dataset.rollSig||'';
    let roll=right.querySelector(':scope > .rollGuide');
    if(!roll||roll.dataset.rollSig!==sig||roll.__buildSourceHtml!==sourceHtml){
      const preserveOpen=!!roll?.open;
      const sameSig=!!roll&&roll.dataset.rollSig===sig;
      const clone=source.cloneNode(true);
      clone.classList.add('rollGuideHero');
      clone.__buildSourceHtml=sourceHtml;
      clone.open=DESKTOP_ROLL.matches?true:(sameSig?preserveOpen:false);
      right.replaceChildren(clone);
      roll=clone;
    }
    setRollMode(roll);
    removeLegacyIcons(roll);
  }

  function enhanceGuide(guide){
    const quick=guide.querySelector('.buildQuickStats');
    if(!quick) return;

    guide.classList.add('buildHeroLayoutV1','buildHeroLayoutV2');
    removeLegacyIcons(guide);

    let left=guide.querySelector(':scope > .buildHeroLeft');
    let right=guide.querySelector(':scope > .buildHeroRoll');

    if(!left){
      const identity=guide.firstElementChild;
      left=document.createElement('div');
      left.className='buildHeroLeft';
      guide.insertBefore(left,identity||guide.firstChild);
      if(identity&&identity!==quick) left.append(identity);
      left.append(quick);
    }else if(quick.parentElement!==left){
      left.append(quick);
    }

    if(!right){
      right=document.createElement('div');
      right.className='buildHeroRoll';
      guide.append(right);
    }

    prepQuick(quick);
    syncRoll(quick,right);
  }

  let queued=false;
  function apply(){
    queued=false;
    document.querySelectorAll('#buildContent .guideSummary.buildSummaryCompact').forEach(enhanceGuide);
  }
  // BUILD_VISUAL_STABILITY_V2: finish the hero reflow in the originating class-click task.
  window.__applyBuildHeroNow=apply;
  function queue(){
    if(queued) return;
    queued=true;
    requestAnimationFrame(()=>setTimeout(apply,0));
  }
  function syncResponsiveRolls(){
    document.querySelectorAll('#buildContent .buildHeroRoll > .rollGuide').forEach(roll=>setRollMode(roll,{resetMobile:!DESKTOP_ROLL.matches}));
  }
  function init(){
    const host=document.getElementById('buildContent');
    if(!host) return;
    removeLegacyIcons(host);
    new MutationObserver(queue).observe(host,{subtree:true,childList:true});
    document.getElementById('classTabs')?.addEventListener('click',queue);
    host.addEventListener('click',e=>{
      if(e.target.closest?.('[data-dominator-mode],[data-guardian-mode]')) setTimeout(queue,0);
    });
    DESKTOP_ROLL.addEventListener?.('change',()=>{
      syncResponsiveRolls();
      queue();
    });
    queue();
  }

  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',init,{once:true});
  else init();
  window.addEventListener('load',queue);
})();

/* NEXUS_TOURNAMENT_TIMING_SEP12_V2
   Direct Charming Glance in-game evidence on Sep. 12 shows Nexus in Preparation with
   16:37:57 remaining at about 8:22 PM PDT, resolving to a 1:00 PM PDT Sep. 13 tournament
   start. Registration/preparation is Sep. 12; the actual tournament belongs on Sep. 13.
   The following 14-day projections move with the corrected Sunday cadence. */
(()=>{
  const CORRECTIONS={
    '2026-09-12':{to:'2026-09-13',serverDay:61,seasonDay:15,summary:'Starts Sunday Sep. 13 at 1:00 PM PDT · 4v4 Nexus Tournament · Top-4 qualification format.'},
    '2026-09-26':{to:'2026-09-27',serverDay:75,seasonDay:29,summary:'Projected 14-day Nexus cadence from the confirmed Sep. 13 slot · Sunday Sep. 27. Recheck the in-game timer as it approaches.'},
    '2026-10-10':{to:'2026-10-11',serverDay:89,seasonDay:43,summary:'Projected 14-day Nexus cadence from the confirmed Sep. 13 slot · Sunday Oct. 11. Recheck the in-game timer as it approaches.'},
    '2026-10-24':{to:'2026-10-25',serverDay:103,seasonDay:57,summary:'Projected 14-day Nexus cadence from the confirmed Sep. 13 slot · Sunday Oct. 25. Recheck the in-game timer as it approaches.'}
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
