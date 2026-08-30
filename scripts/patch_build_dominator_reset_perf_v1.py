from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')
MARK = 'BUILD_DOMINATOR_RESET_PERF_V1'
if MARK in s:
    print('already patched')
    raise SystemExit(0)

# 1) The Builds tab was wrapped in an extra div, so it was not an equal flex item like
# the other three top-level tabs. Restore four direct sibling buttons.
old_nav = '''  <div class="buildsNavCell">\n    <button role="tab" aria-selected="false" data-section="builds">Builds</button>\n</div>'''
new_nav = '''  <button role="tab" aria-selected="false" data-section="builds">Builds</button>'''
if old_nav not in s:
    raise SystemExit('Builds nav wrapper anchor not found')
s = s.replace(old_nav, new_nav, 1)

# 2) Cache Pacific formatters and reset counts. The S2 calculator asks the same
# "how many 6 AM resets remain?" question from many resource/Realm paths; rebuilding
# Intl formatters and walking ~67 days for every candidate was a major long-season cost.
old_time = '''  // Convert a Pacific-local calendar date/time to an exact instant without hard-coding PDT/PST.\n  // The small iterative correction handles the November DST boundary safely.\n  function pacificLocalMs(iso,hour=6,minute=0){\n    const [y,m,d]=iso.split('-').map(Number);\n    const desiredAsUtc=Date.UTC(y,m-1,d,hour,minute,0);\n    let guess=desiredAsUtc;\n    const dtf=new Intl.DateTimeFormat('en-US',{timeZone:'America/Los_Angeles',year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',second:'2-digit',hourCycle:'h23'});\n    for(let i=0;i<4;i++){\n      const parts=Object.fromEntries(dtf.formatToParts(new Date(guess)).filter(x=>x.type!=='literal').map(x=>[x.type,x.value]));\n      const shownAsUtc=Date.UTC(Number(parts.year),Number(parts.month)-1,Number(parts.day),Number(parts.hour),Number(parts.minute),Number(parts.second));\n      const delta=desiredAsUtc-shownAsUtc;\n      guess+=delta;\n      if(Math.abs(delta)<1000) break;\n    }\n    return guess;\n  }\n  function pacificIsoAt(ms){\n    const parts=Object.fromEntries(new Intl.DateTimeFormat('en-US',{timeZone:'America/Los_Angeles',year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(new Date(ms)).filter(x=>x.type!=='literal').map(x=>[x.type,x.value]));\n    return `${parts.year}-${parts.month}-${parts.day}`;\n  }\n  function nextPacificResetMs(afterMs){\n    const iso=pacificIsoAt(afterMs);\n    const sameDay=pacificLocalMs(iso,6,0);\n    return sameDay>afterMs ? sameDay : pacificLocalMs(isoAddDays(iso,1),6,0);\n  }\n  function countFuturePacificResets(startMs,cutoffMs){\n    if(!(cutoffMs>startMs)) return 0;\n    let t=nextPacificResetMs(startMs), count=0, safety=0;\n    while(t<cutoffMs && safety++<500){ count++; t=pacificLocalMs(isoAddDays(pacificIsoAt(t),1),6,0); }\n    return count;\n  }'''
new_time = '''  // BUILD_DOMINATOR_RESET_PERF_V1\n  // Pacific reset math is hot in S2: Realm/tool/resource projection asks the same\n  // question many times during a solve. Reuse Intl formatters and memoize each\n  // first-reset/cutoff pair while preserving exact PDT/PST behavior.\n  const PACIFIC_DATE_TIME_DTF=new Intl.DateTimeFormat('en-US',{timeZone:'America/Los_Angeles',year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',second:'2-digit',hourCycle:'h23'});\n  const PACIFIC_DATE_DTF=new Intl.DateTimeFormat('en-US',{timeZone:'America/Los_Angeles',year:'numeric',month:'2-digit',day:'2-digit'});\n  const FUTURE_RESET_COUNT_CACHE=new Map();\n  let FUTURE_REALM_DAY_CACHE={key:'',value:0,validUntil:0};\n  function pacificLocalMs(iso,hour=6,minute=0){\n    const [y,m,d]=iso.split('-').map(Number);\n    const desiredAsUtc=Date.UTC(y,m-1,d,hour,minute,0);\n    let guess=desiredAsUtc;\n    for(let i=0;i<4;i++){\n      const parts=Object.fromEntries(PACIFIC_DATE_TIME_DTF.formatToParts(new Date(guess)).filter(x=>x.type!=='literal').map(x=>[x.type,x.value]));\n      const shownAsUtc=Date.UTC(Number(parts.year),Number(parts.month)-1,Number(parts.day),Number(parts.hour),Number(parts.minute),Number(parts.second));\n      const delta=desiredAsUtc-shownAsUtc;\n      guess+=delta;\n      if(Math.abs(delta)<1000) break;\n    }\n    return guess;\n  }\n  function pacificIsoAt(ms){\n    const parts=Object.fromEntries(PACIFIC_DATE_DTF.formatToParts(new Date(ms)).filter(x=>x.type!=='literal').map(x=>[x.type,x.value]));\n    return `${parts.year}-${parts.month}-${parts.day}`;\n  }\n  function nextPacificResetMs(afterMs){\n    const iso=pacificIsoAt(afterMs);\n    const sameDay=pacificLocalMs(iso,6,0);\n    return sameDay>afterMs ? sameDay : pacificLocalMs(isoAddDays(iso,1),6,0);\n  }\n  function countFuturePacificResets(startMs,cutoffMs){\n    if(!(cutoffMs>startMs)) return 0;\n    const first=nextPacificResetMs(startMs);\n    if(!(first<cutoffMs)) return 0;\n    const key=`${first}|${cutoffMs}`;\n    if(FUTURE_RESET_COUNT_CACHE.has(key)) return FUTURE_RESET_COUNT_CACHE.get(key);\n    let t=first,count=0,safety=0;\n    while(t<cutoffMs && safety++<500){\n      count++;\n      t=pacificLocalMs(isoAddDays(pacificIsoAt(t),1),6,0);\n    }\n    FUTURE_RESET_COUNT_CACHE.set(key,count);\n    if(FUTURE_RESET_COUNT_CACHE.size>64) FUTURE_RESET_COUNT_CACHE.delete(FUTURE_RESET_COUNT_CACHE.keys().next().value);\n    return count;\n  }'''
if old_time not in s:
    raise SystemExit('Pacific reset block anchor not found')
s = s.replace(old_time, new_time, 1)

# 3) Daily Shop and Material Realm use the identical future-reset window. Give the
# Realm-day helper a short-lived cache so optimizer candidates do not even redo the
# first-reset timezone conversion.
s = s.replace(
    "    const days=active?Math.max(0,countFuturePacificResets(Date.now(),cfg.end.getTime())):0;",
    "    const days=active?Math.max(0,futureRealmPurchaseDays(cfg)):0;",
    1,
)
old_future = '''  function futureRealmPurchaseDays(cfg=activeCalcConfig()){\n    const now=Date.now();\n    const cutoff=cfg.end.getTime();\n    return cutoff>now ? countFuturePacificResets(now,cutoff) : 0;\n  }'''
new_future = '''  function futureRealmPurchaseDays(cfg=activeCalcConfig()){\n    const now=Date.now();\n    const cutoff=cfg.end.getTime();\n    if(cutoff<=now) return 0;\n    const key=`${cfg.key}|${cutoff}`;\n    if(FUTURE_REALM_DAY_CACHE.key===key && now<FUTURE_REALM_DAY_CACHE.validUntil) return FUTURE_REALM_DAY_CACHE.value;\n    const nextReset=nextPacificResetMs(now);\n    const value=countFuturePacificResets(now,cutoff);\n    FUTURE_REALM_DAY_CACHE={key,value,validUntil:Math.min(nextReset,now+60_000)};\n    return value;\n  }'''
if old_future not in s:
    raise SystemExit('futureRealmPurchaseDays anchor not found')
s = s.replace(old_future, new_future, 1)

old_realm_days = '''  function materialRealmDaysAvailable(cfg=activeCalcConfig()){\n    const now=Date.now();\n    const cutoff=cfg.end.getTime();\n    if(cutoff<=now) return 0;\n    // Current server-day window + each future 6 AM reset strictly before the cutoff.\n    return 1+countFuturePacificResets(now,cutoff);\n  }'''
new_realm_days = '''  function materialRealmDaysAvailable(cfg=activeCalcConfig()){\n    if(cfg.end.getTime()<=Date.now()) return 0;\n    // Current server-day window + each future 6 AM reset strictly before the cutoff.\n    return 1+futureRealmPurchaseDays(cfg);\n  }'''
if old_realm_days not in s:
    raise SystemExit('materialRealmDaysAvailable anchor not found')
s = s.replace(old_realm_days, new_realm_days, 1)

# 4) Reintroduce the Dominator DPS / Heals selector as part of the canonical build
# renderer itself. This avoids the detached post-render patch that previously damaged
# the main calculator/navigation script.
dom_start = "    if(cls==='Dominator') return `\n      <div class=\"guideSummary\">"
if dom_start not in s:
    raise SystemExit('Dominator template start not found')
s = s.replace(dom_start, "    if(cls==='Dominator') return `\n      <div class=\"dominatorModeTabs\" role=\"group\" aria-label=\"Dominator build role\"><button type=\"button\" data-dominator-mode=\"dps\">DPS</button><button type=\"button\" data-dominator-mode=\"heals\">Heals</button></div>\n      <div class=\"guideSummary\">", 1)

role_replacements = [
    ('<div class="priorityPanel"><div class="priorityIntro"><span>Core support investment</span>', '<div class="priorityPanel" data-dominator-role="heals"><div class="priorityIntro"><span>Core support investment</span>'),
    ('<div class="priorityPanel"><div class="priorityIntro"><span>Core DPS investment</span>', '<div class="priorityPanel" data-dominator-role="dps"><div class="priorityIntro"><span>Core DPS investment</span>'),
    ('<article class="buildCard"><header><div><h3>Single Target</h3>', '<article class="buildCard" data-dominator-role="dps"><header><div><h3>Single Target</h3>'),
    ('<article class="buildCard"><header><div><h3>AoE / Erosion</h3>', '<article class="buildCard" data-dominator-role="dps"><header><div><h3>AoE / Erosion</h3>'),
    ('<article class="buildCard"><header><div><h3>Healing / Group</h3>', '<article class="buildCard" data-dominator-role="heals"><header><div><h3>Healing / Group</h3>'),
    ('<article class="buildCard"><header><div><h3>Carry Support</h3>', '<article class="buildCard" data-dominator-role="heals"><header><div><h3>Carry Support</h3>'),
]
for old,new in role_replacements:
    if old not in s:
        raise SystemExit(f'Dominator role anchor not found: {old[:70]}')
    s = s.replace(old,new,1)

build_html_anchor = "  function buildHtml(cls){ return buildSeasonKey()==='s1'?buildHtmlS1(cls):buildHtmlS2(cls); }\n"
mode_js = '''  const DOMINATOR_BUILD_MODE_KEY='sxs-build-dominator-mode';\n  let dominatorBuildMode='dps';\n  try{\n    const saved=localStorage.getItem(DOMINATOR_BUILD_MODE_KEY);\n    if(saved==='dps'||saved==='heals') dominatorBuildMode=saved;\n  }catch(_){}\n  function applyDominatorBuildMode(){\n    const root=$('buildContent');\n    if(!root || currentClass!=='Dominator') return;\n    root.querySelectorAll('[data-dominator-mode]').forEach(btn=>{\n      const active=btn.dataset.dominatorMode===dominatorBuildMode;\n      btn.classList.toggle('active',active);\n      btn.setAttribute('aria-pressed',String(active));\n    });\n    root.querySelectorAll('[data-dominator-role]').forEach(el=>{\n      el.hidden=el.dataset.dominatorRole!==dominatorBuildMode;\n    });\n  }\n\n'''
if build_html_anchor not in s:
    raise SystemExit('buildHtml anchor not found')
s = s.replace(build_html_anchor, mode_js + build_html_anchor, 1)

# Both the base and live S2 renderers use this assignment. Sync mode immediately after render.
render_line = "    $('buildContent').innerHTML=buildHtml(currentClass);"
if s.count(render_line) < 2:
    raise SystemExit('expected both build renderer assignments')
s = s.replace(render_line, render_line + "\n    applyDominatorBuildMode();")

active_setup = '''    $('classTabs').addEventListener('click',e=>{\n      const b=e.target.closest('button[data-class]');\n      if(!b)return;\n      currentClass=b.dataset.class;\n      try{localStorage.setItem(liveBuildStorageKey(),currentClass);}catch(_){}\n      renderBuilds();\n    });\n    renderBuilds();'''
active_setup_new = '''    $('classTabs').addEventListener('click',e=>{\n      const b=e.target.closest('button[data-class]');\n      if(!b)return;\n      currentClass=b.dataset.class;\n      try{localStorage.setItem(liveBuildStorageKey(),currentClass);}catch(_){}\n      renderBuilds();\n    });\n    $('buildContent').addEventListener('click',e=>{\n      const b=e.target.closest('button[data-dominator-mode]');\n      if(!b || currentClass!=='Dominator') return;\n      dominatorBuildMode=b.dataset.dominatorMode==='heals'?'heals':'dps';\n      try{localStorage.setItem(DOMINATOR_BUILD_MODE_KEY,dominatorBuildMode);}catch(_){}\n      applyDominatorBuildMode();\n    });\n    renderBuilds();'''
if active_setup not in s:
    raise SystemExit('active setupBuilds anchor not found')
s = s.replace(active_setup, active_setup_new, 1)

# 5) Style the repaired nav and role selector without introducing another script block.
style = '''\n<style id="build-dominator-reset-perf-v1">\n/* BUILD_DOMINATOR_RESET_PERF_V1 */\n.sectionSwitch>button{display:grid;place-items:center;text-align:center}\n.dominatorModeTabs{display:flex;gap:6px;margin:0 0 10px;padding:5px;border:1px solid var(--line);border-radius:13px;background:var(--surface)}\n.dominatorModeTabs button{min-height:38px;flex:1;border:0;border-radius:9px;background:transparent;color:var(--muted);cursor:pointer;font-size:10px;font-weight:850;letter-spacing:.03em}\n.dominatorModeTabs button:hover{color:var(--green)}\n.dominatorModeTabs button.active{background:var(--accent-strong);color:#fff}\n@media(max-width:520px){.dominatorModeTabs button{min-height:42px;font-size:11px}}\n</style>\n'''
if '</head>' not in s:
    raise SystemExit('head close not found')
s = s.replace('</head>', style + '\n</head>', 1)

p.write_text(s,encoding='utf-8')
print('patched Builds centering, Dominator roles, and S2 reset performance')
