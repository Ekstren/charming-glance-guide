from pathlib import Path

source_path=Path('.github/scripts/add_seasonal_builds.py')
src=source_path.read_text(encoding='utf-8')
start=src.index("old_render='''")
mid=src.index("new_render='''", start)
correct_old="""old_render='''  function renderBuilds(){
    $('classTabs').innerHTML=classes.map(c=>`<button class=\"${c===currentClass?'active':''}\" data-class=\"${c}\">${c}</button>`).join('');
    $('buildContent').innerHTML=buildHtml(currentClass);
  }
  let buildsInitialized=false;
  function setupBuilds(){
    $('classTabs').addEventListener('click',e=>{
      const b=e.target.closest('button[data-class]');
      if(!b)return;
      currentClass=b.dataset.class;
      try{localStorage.setItem(BUILD_CLASS_STORAGE_KEY,currentClass);}catch(_){}
      renderBuilds();
    });
  }'''
"""
src=src[:start]+correct_old+src[mid:]
exec(compile(src, str(source_path), 'exec'))
