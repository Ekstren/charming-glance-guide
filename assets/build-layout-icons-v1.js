/* BUILD_HERO_LAYOUT_ICONS_V1
   Reflows the existing generated build summary and decorates actionable stats with inline SVG icons. */
(()=>{
  const SVG=(body)=>`<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">${body}</svg>`;
  const I={
    sword:SVG('<path d="M14.5 4.5 19.5 3l-1.5 5-9.1 9.1-2-2L16 6"/><path d="m7.8 14.2 2 2-2.3 2.3-2-2z"/><path d="m5.3 18.7-1.8 1.8"/>'),
    gauntlet:SVG('<path d="M7 11V6.8a1.3 1.3 0 0 1 2.6 0V10"/><path d="M9.6 9V5.8a1.3 1.3 0 1 1 2.6 0V9"/><path d="M12.2 9V6.4a1.3 1.3 0 1 1 2.6 0v4"/><path d="M14.8 10V8a1.3 1.3 0 1 1 2.6 0v5.2c0 4.5-2.1 7.3-6.2 7.3-3.4 0-5.3-1.7-6.7-4.5l-1.2-2.4a1.4 1.4 0 0 1 2.4-1.4L7 14"/>'),
    helmet:SVG('<path d="M4 13c0-5 3.1-8 8-8s8 3 8 8v3h-5l-1.5-2h-3L9 16H4z"/><path d="M8 16v3M16 16v3M12 5v9"/>'),
    chest:SVG('<path d="m8 5 2 2h4l2-2 4 2-2 4v9H6v-9L4 7z"/><path d="M10 7v3h4V7"/>'),
    boots:SVG('<path d="M8 4h7v8l4 3v3c-4 .8-8.7.8-14 0v-3l3-2z"/><path d="M8 9h7M5 18h14"/>'),
    staff:SVG('<path d="M8 21 15.5 5.5"/><path d="M14.5 6.5 17 4l3 1-1 3-3.5 1z"/><path d="M7 18l3 1.5"/>'),
    book:SVG('<path d="M4 5.5c2.7-.8 5.2-.3 8 1.4v13c-2.8-1.7-5.3-2.2-8-1.4z"/><path d="M20 5.5c-2.7-.8-5.2-.3-8 1.4v13c2.8-1.7 5.3-2.2 8-1.4z"/><path d="M12 7v13"/>'),
    orb:SVG('<circle cx="12" cy="12" r="6"/><path d="M12 3v3M12 18v3M3 12h3M18 12h3"/><path d="m5.6 5.6 2.1 2.1m8.6 8.6 2.1 2.1m0-12.8-2.1 2.1m-8.6 8.6-2.1 2.1"/>'),
    target:SVG('<circle cx="12" cy="12" r="7"/><circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3"/>'),
    burst:SVG('<path d="m12 2 1.7 5 4.6-2.4-.9 5.1 5 .3-4 3.4 3.5 3.7-5.1-.1.5 5.2-4.4-2.7L11 22l-1.7-5-4.6 2.4.9-5.1-5-.3 4-3.4L1.1 6.9l5.1.1-.5-5.2 4.4 2.7z"/>'),
    combo:SVG('<circle cx="8.5" cy="12" r="5"/><circle cx="15.5" cy="12" r="5"/><path d="M12 8.5v7M8.5 12h7"/>'),
    element:SVG('<path d="M12 2c1.5 4-2.5 5.1-1 8 1.2 2.3 4 .9 4-1.6 2.7 2 4 4.2 4 6.6a7 7 0 0 1-14 0c0-3.5 2.1-6.5 5.4-9.4-.4 3 1.2 3.4 1.6 4.8"/>'),
    speed:SVG('<path d="M4 8h10M2 12h12M5 16h9"/><path d="m14 6 6 6-6 6"/>'),
    shield:SVG('<path d="M12 3 19 6v5c0 4.7-2.7 8.1-7 10-4.3-1.9-7-5.3-7-10V6z"/>'),
    shieldCheck:SVG('<path d="M12 3 19 6v5c0 4.7-2.7 8.1-7 10-4.3-1.9-7-5.3-7-10V6z"/><path d="m8.5 12 2.2 2.2 4.8-5"/>'),
    heart:SVG('<path d="M20.8 8.6c0 5-8.8 10.4-8.8 10.4S3.2 13.6 3.2 8.6A4.4 4.4 0 0 1 11 5.8l1 1.1 1-1.1a4.4 4.4 0 0 1 7.8 2.8z"/>'),
    heal:SVG('<path d="M9 4h6v5h5v6h-5v5H9v-5H4V9h5z"/>'),
    resist:SVG('<path d="M12 3 19 6v5c0 4.7-2.7 8.1-7 10-4.3-1.9-7-5.3-7-10V6z"/><path d="m8 16 8-8"/>'),
    tune:SVG('<path d="M4 7h10M18 7h2M4 17h2M10 17h10M14 4v6M8 14v6"/>'),
    effect:SVG('<circle cx="12" cy="12" r="7"/><path d="M12 7v5l3 2"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2"/>')
  };
  const gearMap={Sword:'sword',Gauntlets:'gauntlet',Helmet:'helmet',Chest:'chest',Boots:'boots',Shield:'shield',Staff:'staff',Codex:'book',Orb:'orb'};
  const statIcon=(name)=>{
    const n=(name||'').replace(/\?/g,'').trim().toLowerCase();
    if(n.includes('crit rate + accuracy')||n.includes('crit rate + crit dmg')) return I.combo;
    if(n.includes('block rate + block efficiency')) return I.shieldCheck;
    if(n.includes('dmg res + healing boost')) return I.heal;
    if(n.includes('crit dmg')) return I.burst;
    if(n.includes('crit rate')||n.includes('accuracy')) return I.target;
    if(n.includes('elemental mastery')) return I.element;
    if(n==='spd'||n.includes('speed')) return I.speed;
    if(n==='atk'||n.includes('attack')) return I.sword;
    if(n.includes('block')) return I.shield;
    if(n==='def'||n.includes('defense')) return I.shield;
    if(n==='hp'||n.includes('health')) return I.heart;
    if(n.includes('effect hit')) return I.effect;
    if(n.includes('healing')) return I.heal;
    if(n.includes('dmg res')) return I.resist;
    return I.tune;
  };
  const gearIcon=(name)=>I[gearMap[(name||'').trim()]||'tune'];
  const addIcon=(parent,className,markup)=>{
    let el=parent.querySelector(`:scope > .${className}`);
    if(!el){
      el=document.createElement('span');
      el.className=className;
      parent.prepend(el);
    }
    if(el.innerHTML!==markup) el.innerHTML=markup;
  };
  function decorateQuick(quick){
    const title=quick.querySelector(':scope > .quickTitle');
    if(title&&title.textContent.trim()!=='Gear & stat priorities') title.textContent='Gear & stat priorities';
    quick.querySelectorAll(':scope > .quickGearGrid > .quickGearRow').forEach(row=>{
      const label=row.querySelector(':scope > b')?.textContent.trim()||'';
      addIcon(row,'buildGearIcon',gearIcon(label));
    });
    const sub=quick.querySelector(':scope > .quickSubstats');
    if(sub) addIcon(sub,'buildSubstatIcon',I.tune);
  }
  function decorateRoll(roll){
    roll.querySelectorAll('.rollGuideRow').forEach(row=>{
      const node=row.querySelector('.rollGuideName');
      const name=node?.childNodes?.[0]?.textContent?.trim()||node?.textContent?.trim()||'';
      addIcon(row,'rollStatIcon',statIcon(name));
    });
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
      clone.open=sameSig?preserveOpen:window.matchMedia('(min-width:761px)').matches;
      right.replaceChildren(clone);
      roll=clone;
    }
    decorateRoll(roll);
  }
  function enhanceGuide(guide){
    const quick=guide.querySelector('.buildQuickStats');
    if(!quick) return;
    guide.classList.add('buildHeroLayoutV1');
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
    decorateQuick(quick);
    syncRoll(quick,right);
  }
  let queued=false;
  function apply(){
    queued=false;
    document.querySelectorAll('#buildContent .guideSummary.buildSummaryCompact').forEach(enhanceGuide);
  }
  function queue(){
    if(queued) return;
    queued=true;
    requestAnimationFrame(()=>setTimeout(apply,0));
  }
  function init(){
    const host=document.getElementById('buildContent');
    if(!host) return;
    new MutationObserver(queue).observe(host,{subtree:true,childList:true});
    document.getElementById('classTabs')?.addEventListener('click',queue);
    host.addEventListener('click',e=>{if(e.target.closest?.('[data-dominator-mode]')) setTimeout(queue,0)});
    queue();
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',init,{once:true}); else init();
  window.addEventListener('load',queue);
})();
