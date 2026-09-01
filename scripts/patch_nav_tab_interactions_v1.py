from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

# 1) Re-clicking the already-visible top-level section should be a true no-op.
old = """  function setSection(name){
    const map={timeline:'timelineSection',builds:'buildsSection',companions:'companionsSection',calculator:'calculatorSection'};
    if(!map[name]) name='timeline';
    document.querySelectorAll('.siteSection').forEach(s=>s.hidden=true);"""
new = """  function setSection(name){
    const map={timeline:'timelineSection',builds:'buildsSection',companions:'companionsSection',calculator:'calculatorSection'};
    if(!map[name]) name='timeline';
    const activeSection=document.querySelector('.sectionSwitch button[data-section].active')?.dataset.section;
    if(activeSection===name && !$(map[name]).hidden) return;
    document.querySelectorAll('.siteSection').forEach(s=>s.hidden=true);"""
if old in s:
    s = s.replace(old, new, 1)
elif new not in s:
    raise SystemExit('setSection anchor not found')

# 2) Companion class tabs should behave like Builds: re-clicking selected class does nothing.
old_comp = "$c('companionClassTabs')?.addEventListener('click',e=>{const b=e.target.closest('[data-companion-class]');if(!b)return;currentClass=b.dataset.companionClass;render();});"
new_comp = "$c('companionClassTabs')?.addEventListener('click',e=>{const b=e.target.closest('[data-companion-class]');if(!b)return;if(b.dataset.companionClass===currentClass)return;currentClass=b.dataset.companionClass;render();});"
if old_comp in s:
    s = s.replace(old_comp, new_comp, 1)
elif new_comp not in s:
    raise SystemExit('companion class handler anchor not found')

# 3) Touch browsers can leave :hover stuck after taps. Keep active state authoritative,
#    and only apply hover styling on devices that actually have a fine hover pointer.
marker = '/* NAV_TAB_INTERACTIONS_V1 */'
css = r'''<style id="nav-tab-interactions-v1">
/* NAV_TAB_INTERACTIONS_V1
   Active tabs always own the rose highlight. Hover is desktop-pointer-only so
   touch taps cannot leave a second tab visually highlighted. */
.sectionSwitch button.active,
.classTabs button.active,
.companionClassTabs button.active{
  background:var(--accent-strong)!important;
  border-color:var(--accent-strong)!important;
  color:#fffaf3!important;
  box-shadow:none!important;
}

@media (hover:hover) and (pointer:fine){
  .sectionSwitch button:not(.active):hover,
  .classTabs button:not(.active):hover,
  .companionClassTabs button:not(.active):hover{
    background:var(--ui-hover)!important;
    color:var(--green)!important;
    border-color:var(--ui-accent-border)!important;
  }
  .sectionSwitch button.active:hover,
  .classTabs button.active:hover,
  .companionClassTabs button.active:hover{
    background:var(--accent-strong)!important;
    color:#fffaf3!important;
    border-color:var(--accent-strong)!important;
  }
}

@media (hover:none), (pointer:coarse){
  .sectionSwitch button:not(.active):hover,
  .classTabs button:not(.active):hover,
  .companionClassTabs button:not(.active):hover{
    background:transparent!important;
    color:var(--muted)!important;
    border-color:transparent!important;
  }
  .sectionSwitch button.active:hover,
  .classTabs button.active:hover,
  .companionClassTabs button.active:hover{
    background:var(--accent-strong)!important;
    color:#fffaf3!important;
    border-color:var(--accent-strong)!important;
  }
}
</style>
'''
if marker not in s:
    if '</head>' not in s:
        raise SystemExit('</head> anchor not found')
    s = s.replace('</head>', css + '</head>', 1)

p.write_text(s, encoding='utf-8')
print('Stabilized section/class tab interactions')
# workflow trigger/update marker
