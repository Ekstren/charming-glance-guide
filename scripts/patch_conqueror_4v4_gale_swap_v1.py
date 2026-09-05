from pathlib import Path

SITE = Path("index.html")
text = SITE.read_text(encoding="utf-8")
original = text

old_note = (
    "Flash Fire gives reach, Darkness Descends removes buffs, and Flickering Blade + Blade Storm provide coordinated pressure. "
    "With two Conquerors, the higher-rank Gale Dance user can bring it for team SPD."
)
new_note = (
    "Flash Fire gives reach, Darkness Descends removes buffs, and Flickering Blade + Blade Storm provide coordinated pressure. "
    "If your team wants Gale Dance, swap Flash Fire → Gale Dance; normally only one Conqueror should carry it, preferably the higher-rank Gale Dance user."
)

if new_note not in text:
    if old_note not in text:
        raise SystemExit("Conqueror 4v4 Gale note anchor not found")
    text = text.replace(old_note, new_note)

swap_key = "'Tournament · 4v4|Flash Fire|Darkness Descends|Flickering Blade|Blade Storm':["
if swap_key not in text:
    anchor = """    'Arena|Darkness Descends|Doom Blade|Flickering Blade|Blade Storm':[
"""
    addition = """    'Tournament · 4v4|Flash Fire|Darkness Descends|Flickering Blade|Blade Storm':[
      ['Team SPD / Gale Dance','Flash Fire','Gale Dance']
    ],
"""
    if anchor not in text:
        raise SystemExit("Technique swap scenario anchor not found")
    text = text.replace(anchor, addition + anchor, 1)

if text == original:
    print("Conqueror 4v4 Gale swap is already applied.")
else:
    SITE.write_text(text, encoding="utf-8")
    print("Applied Conqueror 4v4 Gale Dance swap guidance.")
