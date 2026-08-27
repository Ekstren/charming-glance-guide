from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')
marker = 'AUTO_AGE_REALM_TOOLS_V1'
if marker in text:
    print('Realm tool auto-aging already applied.')
    raise SystemExit(0)

old = """    const elapsedResourceHours = Math.max(0, oldResourceHours-newResourceHours);\n    const resourceDefs = [\n"""
new = """    const elapsedResourceHours = Math.max(0, oldResourceHours-newResourceHours);\n\n    /* AUTO_AGE_REALM_TOOLS_V1\n       Treat the saved Daily Realm refresh plan like Cart production: once a planned 6 AM\n       reset has actually passed, move those purchased entries into the on-hand tool counts.\n       Future projection then loses that reset at the same time, so season-end tool totals stay\n       stable instead of requiring the user to manually add Hammers/Knuckles/Shovels each day.\n       Match futureRealmPurchaseDays(): purchases stop at the optional finishing-window cutoff. */\n    const realmCutoffMs=cfg.end.getTime()-($('grace12')?.checked?12*3_600_000:0);\n    const realmAgeEnd=Math.min(cappedNow,realmCutoffMs);\n    const elapsedRealmResets=realmAgeEnd>snapshotAtMs\n      ? countFuturePacificResets(snapshotAtMs,realmAgeEnd)\n      : 0;\n    if(elapsedRealmResets>0){\n      const toolDefs=[\n        ['hammerCurrent','ore'],\n        ['knucklesCurrent','essence'],\n        ['shovelCurrent','sand']\n      ];\n      toolDefs.forEach(([currentId,key])=>{\n        const gained=elapsedRealmResets*realmDailyValue(key)*REALM_RUNS_PER_REFRESH;\n        if(gained>0 && $(currentId)) $(currentId).value=String(Math.max(0,Math.floor(n(currentId,0)))+gained);\n      });\n    }\n\n    const resourceDefs = [\n"""
if text.count(old) != 1:
    raise SystemExit(f'Expected one resource-aging anchor, found {text.count(old)}')
text = text.replace(old, new, 1)

old_return = """    return elapsedResourceHours>0 || elapsedExpHours>0;\n"""
new_return = """    return elapsedResourceHours>0 || elapsedExpHours>0 || elapsedRealmResets>0;\n"""
if text.count(old_return) != 1:
    raise SystemExit(f'Expected one snapshot-aging return, found {text.count(old_return)}')
text = text.replace(old_return, new_return, 1)

path.write_text(text, encoding='utf-8')
print('Added automatic daily Realm-tool aging at passed resets.')
