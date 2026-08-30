from pathlib import Path
import re

INDEX = Path('index.html')
MAINT = Path('.github/build-maintenance.md')
s = INDEX.read_text(encoding='utf-8')
MARK = 'SPAGHETTI_CLEANUP_V1'
if MARK in s:
    print('already cleaned')
    raise SystemExit(0)


def remove_style(style_id: str):
    global s
    pattern = re.compile(r'\n?<style id="' + re.escape(style_id) + r'">.*?</style>\n?', re.S)
    s, count = pattern.subn('\n', s, count=1)
    if count != 1:
        raise SystemExit(f'style block not found exactly once: {style_id} ({count})')


# ---------------------------------------------------------------------------
# Builds: one owner for role filtering, no hidden legacy role-tab renderer.
# ---------------------------------------------------------------------------
apply_role = re.compile(
    r'\nfunction applyBuildRole\(root,name,mode\)\{.*?\n\}\n\nfunction polishBuildLayout\(\)\{',
    re.S,
)
s, count = apply_role.subn(
    '\n// SPAGHETTI_CLEANUP_V1: role filtering/priority swapping is owned by BUILD_ROLE_TOGGLE_V2.\n'
    'function polishBuildLayout(){',
    s,
    count=1,
)
if count != 1:
    raise SystemExit(f'legacy applyBuildRole block not found exactly once ({count})')

old_call = "  applyBuildRole(root,name,mode);\n  renderBuildQuickStats(root,name,mode);"
new_call = "  renderBuildQuickStats(root,name,mode);"
if old_call not in s:
    raise SystemExit('polishBuildLayout legacy role call not found')
s = s.replace(old_call, new_call, 1)

legacy_role_css = "/* BUILD_ARENA_ROLE_UI_REPAIR_V4: only .buildModeTabs is interactive. */\n.buildRoleTabs{display:none!important}\n\n"
if legacy_role_css not in s:
    raise SystemExit('legacy buildRoleTabs CSS guard not found')
s = s.replace(
    legacy_role_css,
    '/* SPAGHETTI_CLEANUP_V1: .buildModeTabs is the only role control. */\n',
    1,
)

role_keys_line = "  const ROLE_KEYS={Arcanist:'sxs-build-role-arcanist',Dominator:'sxs-build-role-dominator'};\n"
if role_keys_line not in s:
    raise SystemExit('duplicate local ROLE_KEYS map not found')
s = s.replace(role_keys_line, '', 1)
s = s.replace("localStorage.getItem(ROLE_KEYS[cls])", "localStorage.getItem(BUILD_ROLE_KEYS[cls])", 1)
s = s.replace("localStorage.setItem(ROLE_KEYS[cls],mode)", "localStorage.setItem(BUILD_ROLE_KEYS[cls],mode)", 1)

# The loadout/Fantomon enhancer used to watch its own DOM writes (including aria/class
# changes), which could wake the role observer and itself repeatedly. Main build renders
# replace buildContent's direct children, so that is the only mutation we need to watch.
old_fanto_observer = """  document.addEventListener('DOMContentLoaded',()=>{\n    queueApply();\n    const root=document.querySelector('.builds');\n    if(root) new MutationObserver(queueApply).observe(root,{subtree:true,childList:true,attributes:true,attributeFilter:['class','aria-pressed']});\n  });\n  window.addEventListener('load',queueApply);"""
new_fanto_observer = """  function startBuildLoadoutSync(){\n    queueApply();\n    const content=document.getElementById('buildContent');\n    if(content) new MutationObserver(queueApply).observe(content,{childList:true});\n    document.querySelector('.builds .classTabs')?.addEventListener('click',queueApply);\n  }\n  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',startBuildLoadoutSync,{once:true});\n  else startBuildLoadoutSync();"""
if old_fanto_observer not in s:
    raise SystemExit('broad build loadout observer not found')
s = s.replace(old_fanto_observer, new_fanto_observer, 1)

old_role_observer = """  function start(){\n    queue();\n    const root=document.querySelector('.builds');\n    if(root)new MutationObserver(queue).observe(root,{subtree:true,childList:true,attributes:true,attributeFilter:['class','data-role']});\n  }\n  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start,{once:true});else start();\n  window.addEventListener('load',queue);"""
new_role_observer = """  function start(){\n    queue();\n    const content=document.getElementById('buildContent');\n    if(content)new MutationObserver(queue).observe(content,{childList:true});\n    document.querySelector('.builds .classTabs')?.addEventListener('click',queue);\n  }\n  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start,{once:true});else start();"""
if old_role_observer not in s:
    raise SystemExit('broad build role observer not found')
s = s.replace(old_role_observer, new_role_observer, 1)

# Timeline compactor had the same query twice in succession.
dupe = "    document.querySelectorAll('#timelineNow .timelineNowCard').forEach(compactNow);\n    document.querySelectorAll('#timelineNow .timelineNowCard').forEach(compactNow);"
if dupe not in s:
    raise SystemExit('duplicate timeline compactNow call not found')
s = s.replace(dupe, "    document.querySelectorAll('#timelineNow .timelineNowCard').forEach(compactNow);", 1)

# ---------------------------------------------------------------------------
# Calculator CSS: remove dead generations and merge fixes into their owner block.
# ---------------------------------------------------------------------------
# Current renderer emits toolSimpleLine. These two blocks only style the retired
# toolUsedLine/toolCompactLine generations and were being overridden later anyway.
remove_style('v57-tool-usage-polish')
remove_style('compact-tool-summary-v9')

# Fold RESOURCE_TOOL_CARD_SEAM_V3 into RESOURCE_TOOL_CARD_SPACING_V2.
old_raw_join = """.planCosts small.rawRemaining:has(+ small.toolBalance:not([hidden])){\n  min-height:0!important;\n  margin-top:5px!important;\n  padding:9px 10px 7px!important;\n  border-bottom:0!important;\n  border-radius:10px 10px 0 0!important;\n}"""
new_raw_join = """.planCosts small.rawRemaining:has(+ small.toolBalance:not([hidden])){\n  min-height:0!important;\n  margin-top:5px!important;\n  padding:9px 10px 7px!important;\n  border-bottom:0!important;\n  border-radius:10px 10px 0 0!important;\n  position:relative;\n  z-index:1;\n}"""
if old_raw_join not in s:
    raise SystemExit('raw joined-card spacing rule not found')
s = s.replace(old_raw_join, new_raw_join, 1)

old_tool_join = """.planCosts small.rawRemaining + small.toolBalance:not([hidden]){\n  min-height:0!important;\n  margin:0!important;\n  padding:7px 10px 8px!important;\n  border:1px solid var(--line)!important;\n  border-top:1px solid var(--line)!important;\n  border-radius:0 0 10px 10px!important;\n  background:color-mix(in srgb,var(--surface) 84%,var(--bg) 16%)!important;\n  box-shadow:none!important;\n  gap:2px!important;\n}"""
new_tool_join = """.planCosts small.rawRemaining + small.toolBalance:not([hidden]){\n  min-height:0!important;\n  margin:-5px 0 0!important;\n  width:100%!important;\n  box-sizing:border-box!important;\n  padding:7px 10px 8px!important;\n  border:1px solid var(--line)!important;\n  border-top:1px solid var(--line)!important;\n  border-radius:0 0 10px 10px!important;\n  background:color-mix(in srgb,var(--surface) 84%,var(--bg) 16%)!important;\n  box-shadow:none!important;\n  gap:2px!important;\n  position:relative;\n  z-index:2;\n}"""
if old_tool_join not in s:
    raise SystemExit('tool joined-card spacing rule not found')
s = s.replace(old_tool_join, new_tool_join, 1)
remove_style('resource-tool-card-seam-v3')

# Four Bed EXP style patches had become one override chain. Keep the exact final
# absolute-note behavior in one owner block.
for style_id in (
    'bed-exp-start-note',
    'bed-exp-note-under-toggle-v3',
    'season-toggle-top-align-v1',
    'bed-exp-absolute-note-align-v1',
):
    remove_style(style_id)

bed_css = r'''
<style id="bed-exp-hold-layout-v4">
/* SPAGHETTI_CLEANUP_V1: consolidated Bed EXP hold toggle + note layout. */
.seasonPlanningControls{align-items:center!important}
.holdExpOption{
  position:relative!important;
  display:flex!important;
  align-items:center!important;
  align-self:auto!important;
  justify-content:flex-start!important;
  gap:7px!important;
}
.holdExpOption>input,.holdExpOption>#holdExpLabel{margin:0!important}
.holdExpOption>.bedReserveStartNote{
  position:absolute!important;
  left:25px!important;
  top:calc(100% + 3px)!important;
  margin:0!important;
  padding:0!important;
  white-space:nowrap!important;
  color:var(--status-info,var(--secondary-text));
  font-size:10px;
  line-height:1.25!important;
  font-weight:750;
  letter-spacing:0;
  text-transform:none;
}
.holdExpOption>.bedReserveStartNote b{color:var(--status-info,var(--blue));font-weight:850}
.seasonPlanningControls:has(#holdExp:checked){padding-bottom:24px!important}
.holdExpOption>input:not(:checked)~.bedReserveStartNote{display:none!important}
</style>
'''
anchor = '<style id="s2-launch-checklist-v1">'
if anchor not in s:
    raise SystemExit('Bed EXP consolidated CSS insertion anchor not found')
s = s.replace(anchor, bed_css + '\n' + anchor, 1)

# Marker lives beside the build layout code so future cleanup scripts have one stable signal.
layout_marker = '// BUILD_LAYOUT_V2\n'
if layout_marker not in s:
    raise SystemExit('BUILD_LAYOUT_V2 marker not found')
s = s.replace(layout_marker, layout_marker + '// SPAGHETTI_CLEANUP_V1: dead build observers/CSS generations consolidated.\n', 1)

INDEX.write_text(s, encoding='utf-8')

# Keep maintenance policy aligned with the runtime architecture so old guidance cannot
# reintroduce the duplicate role/filter behavior on a future build pass.
md = MAINT.read_text(encoding='utf-8')
old_role_doc = '- Arcanist and Dominator keep their **DPS / Heals** selector. DPS shows their DPS loadouts; Heals shows only the dedicated Healing loadout. Switching roles must not destroy/recreate build data or remove Fantomon recommendations.'
new_role_doc = '- Arcanist and Dominator keep one **DPS / Heals** selector. DPS/Heals filters only the role-specific PvE cards; **Arena and Tournament stay visible in both modes**. Switching roles must not destroy/recreate build data or remove Fantomon recommendations.'
if old_role_doc not in md:
    raise SystemExit('maintenance role guidance anchor not found')
md = md.replace(old_role_doc, new_role_doc, 1)

old_pvp_doc = 'Change this structure only when credible current evidence supports a real meta change. Do not add Arena/Tournament cards just to create mode coverage.'
new_pvp_doc = 'Change the PvE structure only when credible current evidence supports a real meta change. **Arena and Tournament are deliberate always-visible reference cards for every class** and are maintained separately from the PvE card-count rule.'
if old_pvp_doc not in md:
    raise SystemExit('maintenance Arena/Tournament guidance anchor not found')
md = md.replace(old_pvp_doc, new_pvp_doc, 1)

architecture = '''\n## Runtime ownership\n\n- `ROLE_PRESETS` owns evidence-based PvE loadout data; `PVP_ROLE_PRESETS` owns Arena/Tournament loadouts. The renderer combines them once.\n- `.buildModeTabs` / `BUILD_ROLE_TOGGLE_V2` is the **only** Arcanist/Dominator role control. Layout-polish code may update presentation, but must not create another role toggle or independently filter cards.\n- Build observers watch the main `#buildContent` replacement boundary instead of the full Builds subtree. Enhancers must not observe their own Fantomon/card DOM writes.\n- Current Realm-tool result markup uses `toolSimpleLine`. Do not revive retired `toolUsedLine`, `toolUsageRow`, or `toolCompactLine` CSS generations.\n'''
if '## Runtime ownership' not in md:
    md = md.replace('\n## Combat Fantomon format\n', architecture + '\n## Combat Fantomon format\n', 1)
MAINT.write_text(md, encoding='utf-8')

print('cleaned dead build observers, duplicate role ownership, and obsolete CSS layers')
