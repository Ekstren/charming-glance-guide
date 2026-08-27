from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
marker='COLLAPSIBLE_CHARACTER_MATERIALS_V1'
if marker in s:
    print('already applied')
    raise SystemExit(0)

old='''    <div class="calcInputs">\n      <div class="calcPanel">\n        <div class="calcGrid">'''
new='''    <div class="calcInputs">\n      <details id="characterDetails" class="calcPanel currentLevelsPanel characterPanel collapsibleCard" open>\n        <summary class="characterSummary"><span>Character</span></summary>\n        <div class="currentLevelsBody characterPanelBody">\n        <div class="calcGrid">'''
if old not in s:
    raise SystemExit('top calculator card opening not found')
s=s.replace(old,new,1)

old_end='''        <div class="seasonRulesHint" id="s2TreatReserveHint">S2 Fantomon Treat reserve: calculating…</div>\n        \n      </div>\n\n      <details id="materialsDetails" class="calcPanel currentLevelsPanel materialPlanner">'''
new_end='''        <div class="seasonRulesHint" id="s2TreatReserveHint">S2 Fantomon Treat reserve: calculating…</div>\n        </div>\n      </details>\n\n      <details id="materialsDetails" class="calcPanel currentLevelsPanel materialPlanner collapsibleCard">'''
if old_end not in s:
    raise SystemExit('top calculator card closing not found')
s=s.replace(old_end,new_end,1)

old_title='<span class="materialsSummaryTitle">Edit saved materials and Cart rates</span>'
new_title='<span class="materialsSummaryTitle">Materials</span>'
if old_title not in s:
    raise SystemExit('materials summary title not found')
s=s.replace(old_title,new_title,1)

old_panels="const PANEL_OPEN_IDS = ['materialsDetails'];"
if old_panels not in s:
    old_panels="const PANEL_OPEN_IDS = ['currentLevelsDetails','materialsDetails'];"
new_panels="const PANEL_OPEN_IDS = ['characterDetails','materialsDetails'];"
if old_panels not in s:
    raise SystemExit('PANEL_OPEN_IDS not found')
s=s.replace(old_panels,new_panels,1)

old_load="""        panel.open = state.panelOpen && typeof state.panelOpen==='object' && state.panelOpen[id]===true;"""
new_load="""        const hasSavedPanelState=state.panelOpen && typeof state.panelOpen==='object' && Object.prototype.hasOwnProperty.call(state.panelOpen,id);\n        panel.open = hasSavedPanelState ? state.panelOpen[id]===true : id==='characterDetails';"""
if old_load not in s:
    raise SystemExit('panel restore assignment not found')
s=s.replace(old_load,new_load,1)

css='''\n<style id="collapsible-character-materials-v1">\n/* COLLAPSIBLE_CHARACTER_MATERIALS_V1 */\n.characterPanel{padding:0!important;overflow:hidden}\n.characterPanelBody{padding:13px 16px 16px!important}\n.characterPanel>summary.characterSummary{padding:12px 16px;min-height:44px}\n.characterPanel>summary.characterSummary span,.materialPlanner>summary.materialsSummary .materialsSummaryTitle{font-size:13px;font-weight:850;color:var(--ink);letter-spacing:-.01em}\n.collapsibleCard>summary{position:relative}\n.collapsibleCard>summary::after{content:'+';flex:0 0 auto;color:var(--muted);font-size:15px;font-weight:900;line-height:1;margin-left:8px}\n.collapsibleCard[open]>summary::after{content:'−'}\n.materialPlanner>summary.materialsSummary{min-height:54px;padding:11px 16px}\n.materialPlanner>summary.materialsSummary .materialsSummaryRight{margin-left:auto}\n@media(max-width:760px){.characterPanelBody{padding:12px 14px 14px!important}.characterPanel>summary.characterSummary,.materialPlanner>summary.materialsSummary{padding:11px 14px}}\n</style>\n'''
idx=s.rfind('</head>')
if idx<0:
    raise SystemExit('</head> not found')
s=s[:idx]+css+s[idx:]

p.write_text(s,encoding='utf-8')
print('applied collapsible Character/Materials cards')
