from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
MARK='DOMINATOR_TOGGLE_INLINE_V1'
if MARK in s:
    print('Dominator inline toggle already applied')
    raise SystemExit(0)

old='''      <div class="dominatorModeTabs" role="group" aria-label="Dominator build role"><button type="button" data-dominator-mode="dps">DPS</button><button type="button" data-dominator-mode="heals">Heals</button></div>
      <div class="guideSummary"><div><span>Dark DPS / healer / support</span><strong>Dominator</strong><p>T4 is a difficult DPS tier for Sage because Erosion needs high Effect Hit Rate and summons are easier to kill. Healing/support gets meaningful upgrades and remains the most reliable role.</p></div><p><b>Quick stat rule</b>DPS: Effect Hit Rate ≥ Elemental Mastery ≥ ATK &gt; SPD. Healer: SPD &gt; Effect Hit Rate &gt; Elemental Mastery &gt; ATK. Do not use one gear priority for both jobs.</p></div>'''
new='''      <div class="guideSummary dominatorGuideSummary"><div><span>Dark DPS / healer / support</span><div class="dominatorHeadingRow"><strong>Dominator</strong><div class="dominatorModeTabs" role="group" aria-label="Dominator build role"><button type="button" data-dominator-mode="dps">DPS</button><button type="button" data-dominator-mode="heals">Heals</button></div></div><p>T4 is a difficult DPS tier for Sage because Erosion needs high Effect Hit Rate and summons are easier to kill. Healing/support gets meaningful upgrades and remains the most reliable role.</p></div><p><b>Quick stat rule</b>DPS: Effect Hit Rate ≥ Elemental Mastery ≥ ATK &gt; SPD. Healer: SPD &gt; Effect Hit Rate &gt; Elemental Mastery &gt; ATK. Do not use one gear priority for both jobs.</p></div>'''
if old not in s:
    raise SystemExit('Dominator template anchor not found')
s=s.replace(old,new,1)

css='''\n<style id="dominator-toggle-inline-v1">\n/* DOMINATOR_TOGGLE_INLINE_V1 */\n.dominatorHeadingRow{display:flex;align-items:center;gap:10px;margin-top:3px;min-width:0}\n.dominatorHeadingRow>strong{margin-top:0;flex:0 0 auto}\n.dominatorHeadingRow .dominatorModeTabs{display:inline-flex;align-items:center;gap:4px;margin:0;padding:3px;border-radius:10px;flex:0 0 auto}\n.dominatorHeadingRow .dominatorModeTabs button{min-height:28px;min-width:54px;padding:4px 10px;font-size:9px;border-radius:7px;flex:0 0 auto}\n@media(max-width:520px){\n  .dominatorHeadingRow{gap:8px;flex-wrap:wrap}\n  .dominatorHeadingRow .dominatorModeTabs button{min-height:30px;min-width:52px;font-size:10px}\n}\n</style>\n'''
if '</head>' not in s:
    raise SystemExit('index.html has no head close')
s=s.replace('</head>',css+'</head>',1)

p.write_text(s,encoding='utf-8')
print('moved Dominator DPS/Heals toggle beside the Dominator title')
