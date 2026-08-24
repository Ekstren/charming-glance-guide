from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
marker='/* RESULTS_SPACING_CLEANUP_V1 */'
if marker in s:
    raise SystemExit('results spacing cleanup already applied')

# Keep the element for existing JS/clipboard references, but never render the Refined Ore / Rolla advisory strip.
s=s.replace('<div class="secondaryCostNote" id="secondaryCostNote" hidden></div>', '<div class="secondaryCostNote" id="secondaryCostNote" hidden style="display:none!important"></div>', 1)

css='''\n\n/* RESULTS_SPACING_CLEANUP_V1 */\n/* Prevent the resource cards from crowding/overlapping the recommended gear row. */\n.suggestedGear{margin-bottom:18px!important}\n.planCosts,.planCostsFour{margin:0 0 20px!important}\n.secondaryCostNote{display:none!important}\n@media(max-width:700px){\n  .suggestedGear{margin-bottom:14px!important}\n}\n'''
if '</style>' not in s:
    raise SystemExit('style closing tag not found')
s=s.replace('</style>',css+'\n</style>',1)

p.write_text(s,encoding='utf-8')
print('Fixed result spacing and hid secondary cost strip.')
# trigger
