/* BUILD_HERO_LAYOUT_ICONS_V1
   Legacy asset filename/hook; decorative icons are intentionally removed.
   BUILD_HERO_LAYOUT_V2 reflows the existing generated build summary only. */
(()=>{
  const ICON_SELECTOR='.buildGearIcon,.rollStatIcon,.buildSubstatIcon';
  const DESKTOP_ROLL=window.matchMedia('(min-width:861px)');

  function removeLegacyIcons(root){
    root?.querySelectorAll?.(ICON_SELECTOR).forEach(el=>el.remove());
  }

  function prepQuick(quick){
    if(!quick) return;
    removeLegacyIcons(quick);
    const title=quick.querySelector(':scope > .quickTitle');
    if(title&&title.textContent.trim()!=='Gear & stat priorities') title.textContent='Gear & stat priorities';
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
    host.addEventListener('click',e=>{if(e.target.closest?.('[data-dominator-mode]')) setTimeout(queue,0)});
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
