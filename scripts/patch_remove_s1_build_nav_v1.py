from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
MARK='S2_ONLY_BUILD_NAV_V1'
if MARK in s:
    print('S2-only Builds navigation already applied')
    raise SystemExit(0)

payload=r'''
<style id="s2-only-build-nav-v1">
/* S2_ONLY_BUILD_NAV_V1
   Charming Glance is in Season 2. Remove the obsolete S1/S2 selector from the
   main Builds tab and keep Builds as the same centered, equal-width nav item. */
.buildSeasonToggle{display:none!important}
.buildsNavCell>button[data-section="builds"]{padding-right:6px!important}
</style>
<script id="s2-only-build-nav-v1-script">
(()=>{
  function stripLegacyBuildSeasonNav(){
    const toggle=document.getElementById('buildSeasonToggle');
    if(toggle) toggle.remove();
    const cell=document.querySelector('.sectionSwitch > .buildsNavCell');
    if(!cell) return;
    const button=cell.querySelector(':scope > button[data-section="builds"]');
    if(button) cell.replaceWith(button);
    else cell.remove();
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',stripLegacyBuildSeasonNav,{once:true});
  else stripLegacyBuildSeasonNav();
  window.addEventListener('load',stripLegacyBuildSeasonNav,{once:true});
})();
</script>
'''

if '</body>' not in s:
    raise SystemExit('index.html missing </body>')
s=s.replace('</body>',payload+'\n</body>',1)
p.write_text(s,encoding='utf-8')
print('removed obsolete S1/S2 Builds selector and restored a plain centered Builds tab')
