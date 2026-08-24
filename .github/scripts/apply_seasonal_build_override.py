from pathlib import Path

index=Path('index.html')
s=index.read_text(encoding='utf-8')
if 'SEASONAL_BUILD_OVERRIDE_V1' in s:
    raise SystemExit(0)

# Reuse the researched S1 build library text from the earlier patch source.
source=Path('.github/scripts/add_seasonal_builds.py').read_text(encoding='utf-8')
start=source.index("s1_func=r'''", 0)+len("s1_func=r'''")
end=source.index("'''.rstrip()", start)
s1_js=source[start:end].rstrip()

marker='  // ---------- Navigation/theme ----------'
if marker not in s:
    raise SystemExit('Navigation marker not found')

override=r'''
  // SEASONAL_BUILD_OVERRIDE_V1
  // Keep the live Builds section on T3/S1 until the Aug 30 6:00 AM Pacific reset,
  // then switch automatically to the existing T4/S2 library.
  const S1_BUILD_CLASSES_LIVE=['Berserker','Paladin','Archmage','Arcanist'];
  const S2_BUILD_CLASSES_LIVE=['Conqueror','Guardian','Destroyer','Dominator'];
  const BUILD_SEASON_STORAGE_KEYS={s1:'sxs-build-class-s1',s2:'sxs-build-class-s2'};
  const buildHtmlT4Live=buildHtml;
  function liveBuildSeason(){ return currentResetIso()<'2026-08-30'?'s1':'s2'; }
  function liveBuildClasses(){ return liveBuildSeason()==='s1'?S1_BUILD_CLASSES_LIVE:S2_BUILD_CLASSES_LIVE; }
  function liveBuildStorageKey(){ return BUILD_SEASON_STORAGE_KEYS[liveBuildSeason()]; }
  function normalizeLiveBuildClass(){
    const list=liveBuildClasses();
    if(list.includes(currentClass)) return;
    let saved=null;
    try{
      saved=localStorage.getItem(liveBuildStorageKey());
      if(!saved && liveBuildSeason()==='s2') saved=localStorage.getItem('sxs-build-class');
    }catch(_){}
    currentClass=list.includes(saved)?saved:list[0];
  }
  buildHtml=function(cls){ return liveBuildSeason()==='s1'?buildHtmlS1(cls):buildHtmlT4Live(cls); };
  renderBuilds=function(){
    normalizeLiveBuildClass();
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
  };
  setupBuilds=function(){
    $('classTabs').addEventListener('click',e=>{
      const b=e.target.closest('button[data-class]');
      if(!b)return;
      currentClass=b.dataset.class;
      try{localStorage.setItem(liveBuildStorageKey(),currentClass);}catch(_){}
      renderBuilds();
    });
    renderBuilds();
    setInterval(()=>{
      if(buildsInitialized){
        const before=currentClass;
        normalizeLiveBuildClass();
        if(before!==currentClass || liveBuildSeason()==='s2') renderBuilds();
      }
    },60_000);
  };
'''.rstrip()

s=s.replace(marker,s1_js+'\n\n'+override+'\n\n'+marker,1)
index.write_text(s,encoding='utf-8')
