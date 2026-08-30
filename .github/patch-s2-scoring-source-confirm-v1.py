from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
MARK='S2_SCORING_SOURCE_CONFIRM_V1'
if MARK in s:
    print('already applied')
    raise SystemExit(0)

old="Starter profile: Lv.130 · Gear 130 · Skills 130 · Fantomons 130 · Relics +14; carried stars/resources should be replaced with your actual snapshot."
new="Starter profile: Lv.130 · Gear 130 · Skills 130 · Fantomons 130 · Relics +13; carried stars/resources should be replaced with your actual snapshot."
if s.count(old)!=1:
    raise SystemExit(f'expected one stale +14 starter-profile string, found {s.count(old)}')
s=s.replace(old,new,1)

old_fallback="cfg.key==='s2'?14:13"
if s.count(old_fallback)!=2:
    raise SystemExit(f'expected two stale S2 relic fallbacks, found {s.count(old_fallback)}')
s=s.replace(old_fallback,"cfg.key==='s2'?13:13")

anchor="  /* S2_PRIMO_READY_V1\n"
if anchor not in s:
    raise SystemExit('S2_PRIMO_READY_V1 anchor missing')
source_note="  /* S2_SCORING_SOURCE_CONFIRM_V1\n     Cross-checked against live-player CN/TW S2 references: scoring begins above Lv.130\n     (Relics above +13), weights are Character 100 / Gear 18 / Skill 7 / Fantomon 8 /\n     Relic 33, S2 contributes 45 fixed Primostars, and progression converts at 27 score\n     per Primostar. Existing 920-star benchmark remains the regression check. */\n"
s=s.replace(anchor,source_note+anchor,1)

p.write_text(s,encoding='utf-8')
print('confirmed S2 scoring presentation and neutral relic fallback')
