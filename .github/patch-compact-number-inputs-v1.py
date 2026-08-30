from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')
marker = 'COMPACT_NUMBER_INPUTS_V1'
if marker in text:
    print('already applied')
    raise SystemExit(0)

old = """  const $ = id => document.getElementById(id);\n  const n = (id, fallback=0) => {\n    const v = Number($(id)?.value);\n    return Number.isFinite(v) ? v : fallback;\n  };\n"""
new = """  const $ = id => document.getElementById(id);\n\n  /* COMPACT_NUMBER_INPUTS_V1\n     High-volume calculator fields accept shorthand such as 22.7k, 1.3m, and 2b.\n     Values are expanded to their full numeric form on commit so persisted state stays plain. */\n  const COMPACT_NUMBER_INPUT_IDS = new Set([\n    'charExp','bedExp','bedStoredExp',\n    'oreCurrent','oreRate','essenceCurrent','essenceRate',\n    'sandCurrent','sandBlueCurrent','sandRate',\n    'treatCurrent','treatPremiumCurrent','treatDeluxeCurrent','treatRate',\n    'hammerCurrent','knucklesCurrent','shovelCurrent','refinedOreCurrent'\n  ]);\n  function parseCompactNumber(raw,fallback=0){\n    if(typeof raw==='number') return Number.isFinite(raw)?raw:fallback;\n    const s=String(raw ?? '').trim().replace(/,/g,'');\n    if(!s) return fallback;\n    const match=s.match(/^([+-]?(?:\\d+(?:\\.\\d*)?|\\.\\d+))\\s*([kmb])?$/i);\n    if(!match) return fallback;\n    const multiplier=match[2]?({k:1e3,m:1e6,b:1e9})[match[2].toLowerCase()]:1;\n    const value=Number(match[1])*multiplier;\n    return Number.isFinite(value)?value:fallback;\n  }\n  function normalizeCompactNumberInput(id){\n    if(!COMPACT_NUMBER_INPUT_IDS.has(id)) return;\n    const el=$(id);\n    if(!el) return;\n    const raw=String(el.value ?? '').trim();\n    if(!raw) return;\n    const value=parseCompactNumber(raw,NaN);\n    if(Number.isFinite(value)) el.value=String(value);\n  }\n  function enableCompactNumberInputs(){\n    COMPACT_NUMBER_INPUT_IDS.forEach(id=>{\n      const el=$(id);\n      if(!el) return;\n      if(el.type==='number') el.type='text';\n      el.inputMode='decimal';\n      el.autocomplete='off';\n      el.dataset.compactNumber='1';\n      const hint='Supports k/m/b shorthand (example: 22.7k = 22700, 1.3m = 1300000).';\n      el.title=el.title?`${el.title} ${hint}`:hint;\n    });\n  }\n  enableCompactNumberInputs();\n  const n = (id, fallback=0) => parseCompactNumber($(id)?.value,fallback);\n"""
if old not in text:
    raise SystemExit('numeric parser block not found; refusing unsafe patch')
text = text.replace(old, new, 1)

old_change = """      el.addEventListener('change',()=>{if(id!=='targetStars')resetMaxAchievableUi();markManualSnapshot(id);scheduleCalculatorUpdate(0);});\n"""
new_change = """      el.addEventListener('change',()=>{\n        normalizeCompactNumberInput(id);\n        if(id!=='targetStars') resetMaxAchievableUi();\n        markManualSnapshot(id);\n        scheduleCalculatorUpdate(0);\n      });\n"""
if old_change not in text:
    raise SystemExit('calculator input change handler not found; refusing unsafe patch')
text = text.replace(old_change, new_change, 1)

path.write_text(text, encoding='utf-8')
print('patched compact k/m/b calculator number entry')
