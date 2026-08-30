from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
MARK='RICH_BUILDS_V2'
if MARK in s:
    print('rich Builds v2 already applied')
    raise SystemExit(0)

# Keep Arena/Tournament visible regardless of Dominator DPS/Heals selection. The role
# switch is for role-specific PvE cards and stat/investment guidance, not PvP references.
old_role=r'''  function applyDominatorRole(host,mode){
    if(activeClass()!=='Dominator') return;
    host.querySelectorAll(':scope > .priorityPair[data-dominator-role]').forEach(el=>{
      el.hidden=el.dataset.dominatorRole!==mode;
    });
    host.querySelectorAll('.buildGrid .buildCard').forEach(card=>{
      const title=card.querySelector('h3')?.childNodes?.[0]?.textContent?.trim()||card.querySelector('h3')?.textContent?.trim()||'';
      const healing=/^Healing/i.test(title);
      const role=healing?'heals':'dps';
      card.dataset.dominatorRole=role;
      card.hidden=role!==mode;
    });
  }'''
new_role=r'''  // RICH_BUILDS_V2: role tabs filter only role-specific PvE. Arena and Tournament
  // remain useful references in either Dominator mode and stay visible in both.
  function applyDominatorRole(host,mode){
    if(activeClass()!=='Dominator') return;
    host.querySelectorAll(':scope > .priorityPair[data-dominator-role]').forEach(el=>{
      el.hidden=el.dataset.dominatorRole!==mode;
    });
    host.querySelectorAll('.buildGrid .buildCard').forEach(card=>{
      const title=card.querySelector('h3')?.childNodes?.[0]?.textContent?.trim()||card.querySelector('h3')?.textContent?.trim()||'';
      const alwaysVisible=/^(Arena|Tournament)/i.test(title);
      const healing=/^Healing/i.test(title);
      const role=healing?'heals':'dps';
      card.dataset.dominatorRole=alwaysVisible?'pvp':role;
      card.hidden=!alwaysVisible && role!==mode;
    });
  }'''
if old_role not in s:
    raise SystemExit('Dominator rich-role anchor not found')
s=s.replace(old_role,new_role,1)

# The recovered Aug 29 loadout/Fantomon enhancer used a broad subtree+attribute
# observer. It can see its own card/Fantomon writes and queue redundant passes.
# Build class switches replace direct children of #buildContent, so observe only that
# replacement boundary; the role selector has its own click handler elsewhere.
old_observer=r'''    const root=document.querySelector('.builds');
    if(root) new MutationObserver(queueApply).observe(root,{subtree:true,childList:true,attributes:true,attributeFilter:['class','aria-pressed']});'''
new_observer=r'''    const root=document.getElementById('buildContent');
    if(root) new MutationObserver(queueApply).observe(root,{childList:true});'''
if old_observer not in s:
    raise SystemExit('historical Builds observer anchor not found')
s=s.replace(old_observer,new_observer,1)

# The presentation enhancer needs nested child-list notices because the loadout injector
# rewrites .buildGrid after the main class render, but it does not need to observe its own
# class/hidden/aria changes.
old_rich_observer=r'''    if(host) new MutationObserver(queue).observe(host,{subtree:true,childList:true,attributes:true,attributeFilter:['class','hidden','aria-pressed']});'''
new_rich_observer=r'''    if(host) new MutationObserver(queue).observe(host,{subtree:true,childList:true});'''
if old_rich_observer not in s:
    raise SystemExit('rich presentation observer anchor not found')
s=s.replace(old_rich_observer,new_rich_observer,1)

p.write_text(s,encoding='utf-8')
print('kept Dominator PvP references in both roles and reduced Builds observer churn')
