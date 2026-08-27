from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')
marker = 'ALL_RESOURCE_REMAINING_V2'
if marker in text:
    print('Unified resource Remaining display already applied.')
    raise SystemExit(0)

# All four resource cards should use the same language:
# Remaining: <amount> [(<protected S2 amount> reserved)]
# Ore has no S2 reserve. Essence/Sand/Treats show the protected amount when enabled.
old_left = "    el.textContent=`${fmt(left)}${unitLabel?` ${unitLabel}`:''} left`;\n"
new_left = "    el.textContent=`Remaining: ${fmt(left)}${unitLabel?` ${unitLabel}`:''}`;\n"
if text.count(old_left) != 1:
    raise SystemExit(f'Expected one generic raw Remaining line, found {text.count(old_left)}')
text = text.replace(old_left, new_left, 1)

old_sand = "  function setSandBalance(id,cost,resources){ setRawRemaining(id,cost,resources?.sand); }\n"
new_sand = "  function setSandBalance(id,cost,resources){ setReservedRawRemaining(id,cost,resources,'sand'); }\n"
if text.count(old_sand) != 1:
    raise SystemExit(f'Expected one Sand balance wrapper, found {text.count(old_sand)}')
text = text.replace(old_sand, new_sand, 1)

# Upgrade the existing V1 marker/comment so the result is easy to audit and idempotent.
text = text.replace(
    "  // ESSENCE_TREAT_RESERVE_DISPLAY_V1: make S2-protected raw resources as obvious as\n",
    "  // ALL_RESOURCE_REMAINING_V2: use one Remaining format for Ore / Essence / Sand / Treats.\n  // S2-protected resources also show the protected amount in parentheses.\n  // make S2-protected raw resources as obvious as\n",
    1,
)

path.write_text(text, encoding='utf-8')
print('Unified Remaining labels across all four resource cards and added Sand reserve display.')
