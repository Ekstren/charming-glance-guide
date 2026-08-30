from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

marker = 'TOOL_TOGGLE_TOP_V1'
if marker in s:
    print('already applied')
    raise SystemExit(0)

old_daily = '''                <label class="realmToolPreserveOption"><input id="preserveRealmTools" checked type="checkbox"><span>Minimize tools</span><small>Saved Realm tools need >10% acquisition improvement to justify spending; paid refreshes need >20%. Turn off for pure efficiency.</small></label>\n'''
if old_daily not in s:
    raise SystemExit('daily Minimize tools control not found')
s = s.replace(old_daily, '', 1)

old_top = '''          <label class="holdExpOption"><input id="holdExp" checked type="checkbox"> <span id="holdExpLabel">Hold Bed EXP for Season 2</span><small class="bedReserveStartNote">Start <b>Aug 28, 8:00 PM PDT</b></small></label>\n          <input id="reserveS2Ore" checked type="checkbox" hidden>'''
new_top = '''          <label class="holdExpOption"><input id="holdExp" checked type="checkbox"> <span id="holdExpLabel">Hold Bed EXP for Season 2</span><small class="bedReserveStartNote">Start <b>Aug 28, 8:00 PM PDT</b></small></label>\n          <label class="realmToolPreserveOption realmToolPreserveTop"><input id="preserveRealmTools" checked type="checkbox"><span>Minimize tools</span><small>Saved tools need >10% improvement; paid Realm refreshes need >20%. Turn off for pure efficiency.</small></label>\n          <input id="reserveS2Ore" checked type="checkbox" hidden>'''
if old_top not in s:
    raise SystemExit('season planning control anchor not found')
s = s.replace(old_top, new_top, 1)

old_css = '''<style id="realm-tool-preserve-policy-v3">\n.realmToolPreserveOption{display:flex;align-items:flex-start;gap:8px;margin:9px 0 12px;color:var(--body-text);font-size:11px;font-weight:750;line-height:1.35}.realmToolPreserveOption input{margin-top:2px;flex:0 0 auto}.realmToolPreserveOption span{white-space:nowrap}.realmToolPreserveOption small{color:var(--muted);font-size:9px;font-weight:600;line-height:1.4}\n@media(max-width:680px){.realmToolPreserveOption{flex-wrap:wrap}.realmToolPreserveOption small{flex-basis:100%;padding-left:22px}}\n</style>'''
new_css = '''<style id="realm-tool-preserve-policy-v4">\n/* TOOL_TOGGLE_TOP_V1: keep the optimizer policy beside the season-level Bed EXP control, not buried in Material Realm details. */\n.realmToolPreserveOption{display:flex;align-items:flex-start;gap:8px;color:var(--body-text);font-size:11px;font-weight:750;line-height:1.35}.realmToolPreserveOption input{margin-top:2px;flex:0 0 auto}.realmToolPreserveOption span{white-space:nowrap}.realmToolPreserveOption small{color:var(--muted);font-size:9px;font-weight:600;line-height:1.4}\n.realmToolPreserveTop{align-items:center;margin:0;min-width:0}.realmToolPreserveTop input{margin-top:0}.realmToolPreserveTop small{max-width:420px}\n@media(max-width:760px){.seasonPlanningControls .realmToolPreserveTop{flex-basis:100%;margin-top:5px}.realmToolPreserveTop{flex-wrap:wrap}.realmToolPreserveTop small{flex-basis:100%;max-width:none;padding-left:22px}}\n</style>'''
if old_css not in s:
    raise SystemExit('realm tool preserve CSS v3 block not found')
s = s.replace(old_css, new_css, 1)

# Guard against accidentally duplicating the stateful control.
if s.count('id="preserveRealmTools"') != 1:
    raise SystemExit(f'expected exactly one preserveRealmTools control, found {s.count(chr(105)+chr(100)+chr(61)+chr(34)+"preserveRealmTools"+chr(34))}')
if 'realmDailyTitle">Daily Realm refresh plan' not in s:
    raise SystemExit('Material Realm plan structure missing after patch')

p.write_text(s, encoding='utf-8')
print('moved Minimize tools beside Hold Bed EXP')
