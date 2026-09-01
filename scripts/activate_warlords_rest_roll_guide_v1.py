from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import re

GATE_UTC = datetime(2026, 9, 12, 13, 0, 0, tzinfo=timezone.utc)  # 6:00 AM PDT
MARKER = 'BUILD_ROLL_GUIDE_WARLORD_V1'
FILES = [Path('index.html'), Path('scripts/patch_build_roll_guide_v2.py')]

WARLORD_ROWS = {
    'atk': "['ATK','Lv162 scaling',1,'Flat ATK scales with receiving gear level. Global-English Warlord-era transfer evidence at Lv162 shows inherited ATK lines reaching 3577 and 4501, but those are observed values rather than a proven Affix Preview maximum.',1]",
    'def': "['DEF','Lv162 scaling',1,'Flat DEF scales with receiving gear level. Global-English Warlord-era transfer evidence at Lv162 shows an inherited DEF line reaching 3603, but that is an observed value rather than a proven Affix Preview maximum.',1]",
    'hp': "['HP','Lv162 scaling',1,'Flat HP scales with receiving gear level. I do not have a direct Global-English Warlord Affix Preview capture proving the maximum Lv162 roll.',1]",
    'spd': "['SPD','Lv162 scaling',1,'Flat SPD scales with receiving gear level. I do not have a direct Global-English Warlord Affix Preview capture proving the maximum Lv162 roll.',1]",
    'crit': "['Crit Rate','≈ 7.50%',1,'Approximate Warlord/Lv162 standalone Crit Rate maximum. Older-server first-post-160 scaling reports about +50% for normal percentage affixes, and Global community evidence independently places high-end Crit rolls around 7.5%; a direct current English-client Affix Preview maximum is still needed.',0]",
    'critdmg': "['Crit DMG','≈ 11.25%',1,'Approximate Warlord/Lv162 standalone Crit DMG maximum from the first-post-160 normal-affix scaling step. A direct current English-client Affix Preview maximum is still needed.',0]",
    'block': "['Block Rate','≈ 7.50%',1,'Approximate Warlord/Lv162 standalone Block Rate maximum from the first-post-160 normal-affix scaling step. A direct current English-client Affix Preview maximum is still needed.',0]",
    'acc': "['Accuracy','≈ 7.50%',1,'Approximate Warlord/Lv162 standalone Accuracy maximum from the first-post-160 normal-affix scaling step. A direct current English-client Affix Preview maximum is still needed.',0]",
    'em': "['Elemental Mastery','Lv162 scaling',1,'Elemental Mastery is a flat-number refinable affix whose inherited value scales with receiving gear level. I do not have a direct Global-English Warlord Affix Preview capture proving the maximum Lv162 roll.',1]",
    'ehr': "['Effect Hit Rate','Lv162 scaling',1,'Effect Hit Rate is a flat-number refinable affix. I do not have a direct Global-English Warlord Affix Preview capture proving the maximum Lv162 roll.',1]",
    'dmgres': "['DMG RES','No verified standalone max',1,'The current refinement pool clearly exposes the paired DMG RES + Healing Boost affix, but I could not establish a trustworthy standalone Warlord DMG RES refinement maximum.',0]",
    'heal': "['Healing Boost','≈ 15.00%',1,'Approximate Warlord/Lv162 standalone Healing Boost maximum from the first-post-160 normal-affix scaling step. A direct current English-client Affix Preview maximum is still needed.',0]",
    'critpair': "['Crit Rate + Crit DMG','15.3% + 23%',0,'',0]",
    'critacc': "['Crit Rate + Accuracy','15.3% + 15.3%',1,'High-confidence post-160 special-affix maximum from the documented 3× special-affix breakpoint and older-server S2 affix table, but not retained as a direct current Global-English Affix Preview capture.',0]",
    'blockpair': "['Block Rate + Block Efficiency','15.3% + 23%',1,'High-confidence post-160 special-affix maximum from the documented 3× special-affix breakpoint and older-server S2 affix table, but not retained as a direct current Global-English Affix Preview capture.',0]",
    'healpair': "['DMG RES + Healing Boost','7.68% + 30.7%',1,'High-confidence post-160 special-affix maximum from the documented 3× special-affix breakpoint and older-server S2 affix table, but not retained as a direct current Global-English Affix Preview capture.',0]",
}


def replace_roll_rows(text: str) -> str:
    block_re = re.compile(r'(const R=\{\n)(.*?)(\n  \};\n  const PROFILES=\{)', re.S)
    m = block_re.search(text)
    if not m:
        raise RuntimeError('Could not locate Roll guide R block')

    body = m.group(2)
    for key, value in WARLORD_ROWS.items():
        line_re = re.compile(rf'(?m)^(\s*){re.escape(key)}:\[.*?\](,?)$')
        hit = line_re.search(body)
        if not hit:
            raise RuntimeError(f'Could not locate Roll guide row: {key}')
        comma = hit.group(2) or ','
        body = line_re.sub(lambda x, k=key, v=value, c=comma: f"{x.group(1)}{k}:{v}{c}", body, count=1)

    return text[:m.start()] + m.group(1) + body + m.group(3) + text[m.end():]


def patch_text(text: str) -> str:
    if MARKER in text:
        return text

    text = replace_roll_rows(text)

    # Label the active tier rather than the retired pre-160 reference.
    text, n = re.subn(
        r'\$\{esc\(label\)\} · Early S2 &lt;160',
        '${esc(label)} · Warlord\'s Rest · Lv162',
        text,
        count=1,
    )
    if n != 1:
        raise RuntimeError('Could not replace Early S2 Roll guide header')

    old_footer = 'Pre-160 S2 reference. Double-Crit is directly documented; other paired values marked <b>?</b> are derived from older-server S2 scaling. Flat/white-number stats such as Mastery scale with gear level.'
    new_footer = "Warlord's Rest / Lv162 reference. Double-Crit is directly documented; other paired values marked <b>?</b> use the documented post-160 special-affix breakpoint. Normal single-stat caps marked <b>?</b> are first-post-160 estimates; flat-number stats scale with gear level."
    if old_footer not in text:
        raise RuntimeError('Could not locate pre-160 Roll guide footer')
    text = text.replace(old_footer, new_footer, 1)

    old_note = 'Only substats recommended above are shown. <b>?</b> = approximate/unconfirmed.'
    new_note = "Only substats recommended above are shown. <b>?</b> = approximate, derived, or not directly confirmed on the current Global client."
    if old_note not in text:
        raise RuntimeError('Could not locate Roll guide confidence note')
    text = text.replace(old_note, new_note, 1)

    # Preserve the existing CSS/script ids for compatibility; marker records the live data tier.
    if 'BUILD_ROLL_GUIDE_V2' not in text:
        raise RuntimeError('Could not locate BUILD_ROLL_GUIDE_V2 marker')
    text = text.replace('BUILD_ROLL_GUIDE_V2', f'BUILD_ROLL_GUIDE_V2 {MARKER}', 1)
    return text


def main() -> int:
    now = datetime.now(timezone.utc)
    if now < GATE_UTC:
        print(f"Warlord's Rest gate not reached: now={now.isoformat()} gate={GATE_UTC.isoformat()}")
        return 0

    changed = []
    for path in FILES:
        text = path.read_text(encoding='utf-8')
        patched = patch_text(text)
        if patched != text:
            path.write_text(patched, encoding='utf-8')
            changed.append(str(path))

    if changed:
        print("Activated Warlord's Rest Roll guide in: " + ', '.join(changed))
    else:
        print("Warlord's Rest Roll guide already activated; no changes")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
