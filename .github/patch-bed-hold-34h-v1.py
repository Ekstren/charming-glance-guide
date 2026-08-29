from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')
marker = 'BED_HOLD_34H_V1'
if marker in s:
    print('already patched')
    raise SystemExit(0)

replacements = [
    ('<small class="bedReserveStartNote">Start <b>Aug 28, 6:00 PM PDT</b></small>', '<small class="bedReserveStartNote">Start <b>Aug 28, 8:00 PM PDT</b></small>'),
    ('<input id="reserveHours" min="0" max="36" type="number" value="36" hidden>', '<input id="reserveHours" min="0" max="36" type="number" value="34" hidden>'),
    ("clamp(n('reserveHours',36),0,36)", "clamp(n('reserveHours',34),0,36)"),
    ('reserveHours:36,skillLevel:100', 'reserveHours:34,skillLevel:100'),
    ('A 36-hour EXP reserve removes natural Bed hours only; reset boost hours inside that reserve still count.', 'A 34-hour EXP reserve removes natural Bed hours only; reset boost hours inside that reserve still count.'),
    ('Collect the banked 36 hours now.', 'Collect the banked 34 hours now.'),
    ('Bed EXP historically banks up to 36h, but Aug 21 community reports say recent maintenance behavior may auto-claim stored EXP; verify the transition notice before relying on the full bank.', 'The planner starts the Bed EXP hold 34h before reset. Bed EXP historically banks up to 36h, but Aug 21 community reports say recent maintenance behavior may auto-claim stored EXP; verify the transition notice before relying on the full bank.'),
    ("return 'Aug 29: sell unused S1 dungeon shards unless they buy another Primostar tier, and save dungeon attempts for S2. Treat 36h Bed EXP banking as unconfirmed.';", "return 'Aug 29: sell unused S1 dungeon shards unless they buy another Primostar tier, and save dungeon attempts for S2. Bed EXP hold begins 34h before reset; full 36h banking remains unconfirmed.';"),
]

for old, new in replacements:
    count = s.count(old)
    if count == 0:
        raise SystemExit(f'missing expected text: {old[:90]}')
    s = s.replace(old, new)

# Existing localStorage snapshots may still contain the old hidden default of 36 hours.
# Migrate only that old default; preserve any other explicitly stored value.
needle = "      INPUT_IDS.forEach(id => { if (state[id] !== undefined && $(id)) $(id).value = state[id]; });"
insert = "      if(Number(state.reserveHours)===36) state.reserveHours='34'; // BED_HOLD_34H_V1 migrate old hidden default\n" + needle
if needle not in s:
    raise SystemExit('load-state anchor missing')
s = s.replace(needle, insert, 1)

# Keep an explicit marker near the migration so future passes can detect this policy.
p.write_text(s, encoding='utf-8')
print('patched Bed EXP hold to 34 hours before reset')
