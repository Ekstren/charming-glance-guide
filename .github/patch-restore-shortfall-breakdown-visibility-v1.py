from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')
marker = 'SHORTFALL_BREAKDOWN_VISIBLE_V1'
if marker in s:
    print('already applied')
    raise SystemExit(0)

old = ".planCosts small.shortfallBreakdown{display:none!important}"
new = "/* SHORTFALL_BREAKDOWN_VISIBLE_V1: keep the detailed daily-plan / Realm-capacity shortfall card visible; the duplicate Still short footer remains removed. */\n.planCosts small.shortfallBreakdown{display:grid!important;gap:2px!important}"
if old not in s:
    raise SystemExit('Could not find hidden shortfallBreakdown CSS override')
s = s.replace(old, new, 1)

# Keep the surrounding cleanup comment accurate.
s = s.replace(
    "One goal-status warning; resource cards keep only the useful balance/shortfall line.",
    "One goal-status warning; resource cards keep the detailed shortfall block without a duplicate tool-footer shortage.",
    1,
)

p.write_text(s, encoding='utf-8')
print('restored detailed resource shortfall visibility')
