from pathlib import Path
import runpy

V1=Path('scripts/patch_t4_class_order_dominator_roles_v1.py')
META=Path('scripts/patch_meta_build_modes_v1.py')

# v1 patches actual runtime JS and the maintained Python source with the same helper.
# The click handler is literal JS in the runtime file, but escaped inside the maintained
# Python generator. Allow the generic helper to skip that one source-only anchor; below
# we patch the generator's escaped click string explicitly.
s=V1.read_text(encoding='utf-8')
old="        if anchor not in text:raise RuntimeError('Guardian click anchor missing')\n        text=text.replace(anchor,add,1)"
new="        if anchor in text:text=text.replace(anchor,add,1)"
if old in s:
    s=s.replace(old,new,1)
elif new not in s:
    raise RuntimeError('Could not fix v1 click-anchor handling')
V1.write_text(s,encoding='utf-8')

# Run the main audited patch now that its source/runtime distinction is safe.
runpy.run_path(str(V1),run_name='__main__')

# Keep the maintained META patch able to reproduce Dominator role clicks from scratch.
meta=META.read_text(encoding='utf-8')
if "const dominatorBtn=e.target.closest?.('[data-dominator-mode]');" not in meta:
    oldfrag="if(guardianBtn&&activeClass()==='Guardian'){metaWrite('sxs-build-guardian-mode',guardianBtn.dataset.guardianMode==='dps'?'dps':'tank');applyMetaVisibility('Guardian');queueApply();return;}\\n      const modeBtn=e.target.closest?.('[data-meta-mode]');"
    newfrag="if(guardianBtn&&activeClass()==='Guardian'){metaWrite('sxs-build-guardian-mode',guardianBtn.dataset.guardianMode==='dps'?'dps':'tank');applyMetaVisibility('Guardian');queueApply();return;}\\n      const dominatorBtn=e.target.closest?.('[data-dominator-mode]');\\n      if(dominatorBtn&&activeClass()==='Dominator'){metaWrite('sxs-build-dominator-mode',dominatorBtn.dataset.dominatorMode==='heals'?'heals':'dps');applyMetaVisibility('Dominator');queueApply();return;}\\n      const modeBtn=e.target.closest?.('[data-meta-mode]');"
    if oldfrag not in meta:
        raise RuntimeError('Maintained meta click-string anchor missing')
    meta=meta.replace(oldfrag,newfrag,1)
    META.write_text(meta,encoding='utf-8')

print('T4 class order/Dominator role v2 completed')
