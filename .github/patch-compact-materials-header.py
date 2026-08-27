from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
marker='MATERIALS_HEADER_COMPACT_V1'
if marker in s:
    print('already applied')
    raise SystemExit(0)

old='''        <summary class="materialsSummary"><span class="materialsSummaryTitle">Materials</span><span class="materialsSummaryRight"><small>Optional · makes the final plan account-specific</small><span class="staminaHeaderControl" onclick="event.stopPropagation()" onkeydown="event.stopPropagation()"><b>Stamina</b><span class="staminaControl"><select id="staminaMode" title="Late-S1 Ore is verified; Essence/Sand use community-style estimates derived from the same S1 Ore-to-Realm scaling."><option value="auto" selected>Auto</option><option value="ore">Raw Ore</option><option value="essence">Skill Essence</option><option value="sand">Chrono Sand</option></select><small id="staminaCurrentPlan" class="staminaCurrentPlan">Current plan: —</small></span></span></span></summary>
        <div class="currentLevelsBody">'''
new='''        <summary class="materialsSummary compactCardSummary"><span>Materials</span></summary>
        <div class="currentLevelsBody">
          <div class="materialsStaminaRow">
            <b>Stamina</b>
            <select id="staminaMode" title="Late-S1 Ore is verified; Essence/Sand use community-style estimates derived from the same S1 Ore-to-Realm scaling."><option value="auto" selected>Auto</option><option value="ore">Raw Ore</option><option value="essence">Skill Essence</option><option value="sand">Chrono Sand</option></select>
            <small id="staminaCurrentPlan" class="staminaCurrentPlan">Current plan: —</small>
          </div>'''
if old not in s:
    raise SystemExit('materials header block not found')
s=s.replace(old,new,1)

style='''\n<style id="materials-header-compact-v1">\n/* MATERIALS_HEADER_COMPACT_V1 */\n#materialsDetails>summary.materialsSummary{min-height:0!important;padding:14px 16px!important;display:flex!important;align-items:center!important;gap:10px!important}\n#materialsDetails>summary.materialsSummary>span{font-size:12px!important;font-weight:850!important;color:var(--ink)!important}\n.materialsStaminaRow{display:grid;grid-template-columns:auto minmax(150px,190px) minmax(0,1fr);align-items:center;gap:10px;margin:0 0 10px;padding:0 0 10px;border-bottom:1px solid var(--line)}\n.materialsStaminaRow>b{color:var(--muted);font-size:9px;letter-spacing:.08em;text-transform:uppercase}\n.materialsStaminaRow select{min-height:36px;padding:7px 30px 7px 10px;border:1px solid var(--line);border-radius:9px;background:var(--input-bg);color:var(--ink);font-size:12px;font-weight:800}\n.materialsStaminaRow small{margin:0;color:var(--green);font-size:9px;font-weight:800;line-height:1.3;text-align:right}\n@media(max-width:620px){.materialsStaminaRow{grid-template-columns:auto minmax(130px,1fr)}.materialsStaminaRow small{grid-column:1/-1;text-align:left}}\n</style>\n'''
if '</head>' not in s:
    raise SystemExit('</head> not found')
s=s.replace('</head>',style+'</head>',1)
p.write_text(s,encoding='utf-8')
print('compacted Materials header and moved Stamina into body')
