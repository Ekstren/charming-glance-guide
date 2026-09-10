from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
MARK='BUILD_SWITCH_NO_FLICKER_V1'
if MARK in s:
    print('Build no-flicker switch patch already applied.')
    raise SystemExit(0)
if 'SKILL_GEAR_TWO_POINTER_V10' not in s:
    raise SystemExit('Expected current optimized site baseline not found')

old_render="""  renderBuilds=function(){
    if(buildSeasonKey()==='s2') currentBuildSeason='s2';
    normalizeLiveBuildClass();
    renderBuildSeasonToggle();
    const list=liveBuildClasses();
    const s1=liveBuildSeason()==='s1';
    const label=document.querySelector('#buildsSection .sectionHeading span');
    const note=document.querySelector('#buildsSection .sectionHeading>p');
    if(label) label.textContent=s1?'Season 1 · Tier III build guide':'Season 2 · Tier IV build guide';
    if(note) note.textContent=s1
      ? 'Showing the live Season 1 / Tier III meta. This switches to Tier IV automatically at the Aug 30, 6:00 AM Pacific reset.'
      : 'Season 2 / Tier IV is live. Your selected class tab is remembered separately for each season.';
    $('classTabs').innerHTML=list.map(c=>`<button class="${c===currentClass?'active':''}" data-class="${c}">${c}</button>`).join('');
    $('buildContent').innerHTML=buildHtml(currentClass);
    applyDominatorBuildMode();
  };"""
new_render="""  /* BUILD_SWITCH_NO_FLICKER_V1
     Class switching used to destroy/recreate BOTH the class tabs and the full build tree, then
     a later requestAnimationFrame performed the META transform. That produced a visible repaint:
     raw build -> activity/role build. Keep the tab nodes stable, cache parsed class templates,
     mount one detached clone atomically, and ask the META layer to finish synchronously before
     the browser gets a chance to paint the new class. */
  const BUILD_TEMPLATE_CACHE=new Map();
  let buildTemplateWarmKey='';
  function buildTemplateForClass(cls){
    const key=`${liveBuildSeason()}|${cls}`;
    let template=BUILD_TEMPLATE_CACHE.get(key);
    if(!template){
      template=document.createElement('template');
      template.innerHTML=buildHtml(cls);
      BUILD_TEMPLATE_CACHE.set(key,template);
    }
    return template;
  }
  function syncBuildClassTabs(list){
    const tabs=$('classTabs');
    const signature=`${liveBuildSeason()}|${list.join('|')}`;
    if(tabs.dataset.buildClassSignature!==signature){
      tabs.innerHTML=list.map(c=>`<button type="button" role="tab" aria-selected="${c===currentClass}" class="${c===currentClass?'active':''}" data-class="${c}">${c}</button>`).join('');
      tabs.dataset.buildClassSignature=signature;
    }else{
      tabs.querySelectorAll('button[data-class]').forEach(btn=>{
        const active=btn.dataset.class===currentClass;
        btn.classList.toggle('active',active);
        btn.setAttribute('aria-selected',String(active));
      });
    }
  }
  function warmBuildTemplates(list){
    const key=`${liveBuildSeason()}|${list.join('|')}`;
    if(buildTemplateWarmKey===key) return;
    buildTemplateWarmKey=key;
    const work=()=>list.forEach(cls=>buildTemplateForClass(cls));
    if('requestIdleCallback' in window) requestIdleCallback(work,{timeout:500});
    else setTimeout(work,0);
  }
  renderBuilds=function(){
    if(buildSeasonKey()==='s2') currentBuildSeason='s2';
    normalizeLiveBuildClass();
    renderBuildSeasonToggle();
    const list=liveBuildClasses();
    const s1=liveBuildSeason()==='s1';
    const label=document.querySelector('#buildsSection .sectionHeading span');
    const note=document.querySelector('#buildsSection .sectionHeading>p');
    if(label) label.textContent=s1?'Season 1 · Tier III build guide':'Season 2 · Tier IV build guide';
    if(note) note.textContent=s1
      ? 'Showing the live Season 1 / Tier III meta. This switches to Tier IV automatically at the Aug 30, 6:00 AM Pacific reset.'
      : 'Season 2 / Tier IV is live. Your selected class tab is remembered separately for each season.';
    syncBuildClassTabs(list);
    const host=$('buildContent');
    const template=buildTemplateForClass(currentClass);
    host.replaceChildren(template.content.cloneNode(true));
    applyDominatorBuildMode();
    // The META script is loaded after this main runtime. On initial parse it will enhance at
    // DOMContentLoaded; on every later class click this hook exists and completes before paint.
    if(typeof window.__applyBuildMetaNow==='function') window.__applyBuildMetaNow();
    warmBuildTemplates(list);
  };"""
if old_render not in s:
    raise SystemExit('live renderBuilds anchor not found')
s=s.replace(old_render,new_render,1)

old_meta="""  let queued=false;
  function queueApply(){
    if(queued) return;
    queued=true;
    requestAnimationFrame(()=>{queued=false;apply();});
  }
  document.addEventListener('DOMContentLoaded',()=>{
    queueApply();
    const root=document.querySelector('.builds');
    if(root) new MutationObserver(queueApply).observe(root,{subtree:true,childList:true,attributes:true,attributeFilter:['class','aria-pressed']});"""
new_meta="""  let queued=false,suppressQueuedApply=false;
  function queueApply(){
    if(queued) return;
    queued=true;
    requestAnimationFrame(()=>{queued=false;apply();});
  }
  // BUILD_SWITCH_NO_FLICKER_V1: main Builds renderer calls this inside the class-click task.
  // META controls/loadouts/Fantomons therefore exist before the next paint instead of appearing
  // one animation frame after the raw class markup. Suppress the observer echo for that task.
  window.__applyBuildMetaNow=()=>{
    suppressQueuedApply=true;
    apply();
    setTimeout(()=>{suppressQueuedApply=false;},0);
  };
  document.addEventListener('DOMContentLoaded',()=>{
    // Initial/restored Builds view gets the same one-paint treatment.
    apply();
    const root=document.querySelector('.builds');
    if(root) new MutationObserver(()=>{if(!suppressQueuedApply) queueApply();}).observe(root,{subtree:true,childList:true,attributes:true,attributeFilter:['class','aria-pressed']});"""
if old_meta not in s:
    raise SystemExit('META queue/apply anchor not found')
s=s.replace(old_meta,new_meta,1)

p.write_text(s,encoding='utf-8')
print('Applied stable Builds tabs, cached parsed templates, atomic mounts, and synchronous META enhancement.')
