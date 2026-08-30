from pathlib import Path
import re, subprocess, tempfile, sys

p=Path('index.html')
s=p.read_text(encoding='utf-8')
orig=s

cut='2026-08-30'
lines=[]
for line in s.splitlines(True):
    m=re.match(r"(\s*)\['(2026-\d\d-\d\d)'\s*,", line)
    if m and m.group(2) < cut: continue
    lines.append(line)
s=''.join(lines)

s=re.sub(r'\s*<span class="buildSeasonToggle" id="buildSeasonToggle"[\s\S]*?</span>\s*', '\n', s)
while 'function buildHtmlS1' in s:
    a=s.find('function buildHtmlS1'); line_a=s.rfind('\n',0,a)+1
    b=s.find('function buildHtmlS2',a)
    if b<0:
        s=s[:a]+'function legacyBuildHtmlS1'+s[a+len('function buildHtmlS1'):]
        break
    line_b=s.rfind('\n',0,b)+1
    s=s[:line_a]+s[line_b:]
s=s.replace("function buildSeasonKey(){ return currentResetIso()<'2026-08-30'?'s1':'s2'; }", "function buildSeasonKey(){ return 's2'; }")
s=s.replace("function buildClassesForSeason(key=buildSeasonKey()){ return key==='s1'?S1_BUILD_CLASSES:S2_BUILD_CLASSES; }", "function buildClassesForSeason(){ return S2_BUILD_CLASSES; }")
s=s.replace("let currentBuildSeason=buildSeasonKey();", "let currentBuildSeason='s2';", 1)
s=s.replace("let currentClass=currentBuildSeason==='s1'?'Berserker':'Conqueror';", "let currentClass='Conqueror';", 1)
s=re.sub(r"function liveBuildSeason\(\)\{[^\n]*\}", "function liveBuildSeason(){ return 's2'; }", s)
s=re.sub(r"function liveBuildClasses\(\)\{[^\n]*\}", "function liveBuildClasses(){ return S2_BUILD_CLASSES_LIVE; }", s)
s=s.replace("$('buildSeasonToggle')?.addEventListener('click',e=>{", "null?.addEventListener?.('click',e=>{")

s=s.replace("let currentSeason='s1';", "let currentSeason='s2';")
s=s.replace("let currentClass='Berserker';", "let currentClass='Conqueror';")
s=re.sub(r"function defaultSeason\(\)\{\s*return Date\.now\(\)>=new Date\('2026-08-30T06:00:00-07:00'\)\.getTime\(\)\?'s2':'s1';\s*\}", "function defaultSeason(){ return 's2'; }", s)
s=re.sub(r'\s*<[^>]+id="companionSeasonToggle"[\s\S]*?</[^>]+>\s*', '\n', s)
s=s.replace("const classes=currentSeason==='s1'?S1_CLASSES:S2_CLASSES;", "const classes=S2_CLASSES;")
s=s.replace("const list=season==='s1'?S1_BUILD_CLASSES_LIVE:S2_BUILD_CLASSES_LIVE;", "const list=S2_BUILD_CLASSES_LIVE;")

s=re.sub(r'\s*<label class="holdExpOption">[\s\S]*?</label>\s*', '\n', s)
for rid in ('reserveS2Ore','reserveS2Essence','reserveS2Sand','reserveS2Treats'):
    s=re.sub(rf'\s*<input id="{rid}"[^>]*>\s*', '\n', s)
s=re.sub(r'\s*<small class="seasonPlanningNote" id="oreReserveNote">[\s\S]*?</small>\s*', '\n', s)
s=re.sub(r'\s*<small class="bedReserveStartNote">[\s\S]*?</small>\s*', '', s)
s=s.replace("holdExp:true,preserveRealmTools:true", "holdExp:false,preserveRealmTools:true")
for fn in ('season2SkillEssenceReserve','season2SandReserve','season2TreatReserve','season2OreReserve'):
    s=re.sub(rf"(function {fn}\([^)]*\)\{{)(?! return \{{target:0)", r"\1 return {target:0,rawEssence:0,rawSand:0,rawTreat:0,rawOre:0,knucklesReserved:0,shovelsReserved:0,hammersReserved:0,knuckleEssence:0,shovelSand:0,hammerOre:0,projectedKnuckles:0,projectedShovels:0,projectedHammers:0,shortfall:0,hours:0,exp:0,targetLevel:130}; /* S2 live: rollover reserve retired */", s)
s=s.replace("<p><b>1 · Protect enabled rollover reserves during Season 1.</b> Raw Essence/Sand cover those reserves first; Knuckles/Shovels are reserved only for any uncovered remainder. Once S2 scoring is active, the old S1→S2 reserve toggles are hidden and the planner uses your live S2 inventory directly.</p>", "<p><b>1 · Use live Season 2 inventory.</b> The planner evaluates your current materials, Cart production, Stamina and Realm options directly.</p>")

s=s.replace("$('historicalStarsLabel').textContent=cfg.key==='s1'?'Historical stars':'Season 1 Primostars (carried)';", "$('historicalStarsLabel').textContent='Season 1 Primostars (carried)';")
s=re.sub(r'\s*<[^>]+id="calcSeasonToggle"[\s\S]*?</[^>]+>\s*', '\n', s)
s=s.replace('Season 2 launch checklist', 'Season 2 Day 1 checklist')
s=s.replace('<strong>Log in after Season 2 is live.</strong><em>Make sure the rollover/reset has fully happened before claiming anything.</em>', '<strong>Start with rollover rewards.</strong><em>Season 2 is live; collect the new-season rewards before spending progression resources.</em>')

assert 'REALM_SAVED_TOOL_EFFICIENCY_HURDLE=0.10' in s
assert 'REALM_PAID_REFRESH_EFFICIENCY_HURDLE=0.20' in s
assert 'id="preserveRealmTools"' in s
assert 'Season 1 Primostars (carried)' in s and 'historicalStars' in s and 'Astral' in s
assert 'reserveHours' in s and 'value="34"' in s and '2*countFuturePacificResets' in s
assert 'id="buildSeasonToggle"' not in s
assert "function buildHtmlS1" not in s
assert "['2026-08-29',46" not in s
for rid in ('reserveS2Ore','reserveS2Essence','reserveS2Sand','reserveS2Treats'):
    assert f'id="{rid}"' not in s

p.write_text(s,encoding='utf-8')
blocks=re.findall(r'<script(?:\s[^>]*)?>([\s\S]*?)</script>', s, flags=re.I)
for i,b in enumerate(blocks):
    if not b.strip(): continue
    q=Path(tempfile.gettempdir())/f's2-inline-{i}.js'; q.write_text(b,encoding='utf-8')
    r=subprocess.run(['node','--check',str(q)],capture_output=True,text=True)
    if r.returncode:
        print(r.stdout); print(r.stderr,file=sys.stderr); raise SystemExit(f'inline JS syntax failed block {i}')
if s==orig: raise SystemExit('No changes made')
print(f'S2 handoff complete; {len(blocks)} inline script blocks syntax-checked.')
