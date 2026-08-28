from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')
marker = 'POSITIVE_SHORTFALL_LABEL_V1'

if marker in s:
    print('already applied')
    raise SystemExit(0)

old = "${shortfall>0?` · <strong>${fmt(shortfall)} short</strong>`:' · <strong class=\"reserveProtected\">✓ protected</strong>'}"
new = "${shortfall>0?` · <strong>${fmt(Math.abs(shortfall))} short</strong>`:' · <strong class=\"reserveProtected\">✓ protected</strong>'}"

if old not in s:
    raise SystemExit('reserve shortfall renderer not found')

s = s.replace(old, new, 1)
s = s.replace(
    "  function setEssenceBalance(id,cost,resources){ setReservedRawRemaining(id,cost,resources,'essence'); }",
    "  // POSITIVE_SHORTFALL_LABEL_V1: 'short' already implies a deficit; never render a negative sign.\n  function setEssenceBalance(id,cost,resources){ setReservedRawRemaining(id,cost,resources,'essence'); }",
    1,
)

p.write_text(s, encoding='utf-8')
print('patched reserve shortfall label')
