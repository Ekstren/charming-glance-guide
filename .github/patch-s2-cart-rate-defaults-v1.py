from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')
marker = 'S2_CART_RATE_DEFAULTS_V1'
if marker in text:
    print('already applied')
    raise SystemExit(0)

old = """    oreCurrent:0,oreRate:0,essenceCurrent:0,essenceRate:0,
    sandCurrent:0,sandBlueCurrent:0,sandRate:0,
    treatCurrent:0,treatPremiumCurrent:0,treatDeluxeCurrent:0,treatRate:0,
"""
new = """    // S2_CART_RATE_DEFAULTS_V1: conservative starter Cart rates; lower than the user's current late-S1 production.
    oreCurrent:0,oreRate:1000,essenceCurrent:0,essenceRate:1200,
    sandCurrent:0,sandBlueCurrent:0,sandRate:800,
    treatCurrent:0,treatPremiumCurrent:0,treatDeluxeCurrent:0,treatRate:80,
"""
if old not in text:
    raise SystemExit('S2 default resource block not found; refusing unsafe patch')
text = text.replace(old, new, 1)

old_note = "Account-specific rates/materials remain 0\n     until the player enters them so the optimizer never fabricates spendable resources."
new_note = "Saved materials remain 0 until the player enters them. Starter Cart rates use conservative S2 planning defaults\n     (Ore 1,000/hr, Essence 1,200/hr, Sand 800/hr, Treats 80/hr) and can be replaced with live values at any time."
if old_note in text:
    text = text.replace(old_note, new_note, 1)

path.write_text(text, encoding='utf-8')
print('updated S2 Cart rate defaults')
