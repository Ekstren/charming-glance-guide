from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')
marker = 'PRESERVE_ORE_LEXICOGRAPHIC_V1'
if marker in text:
    print('Preserve Ore strict priority already applied.')
    raise SystemExit(0)

old = """    if(candidate.seasonKey==='s1' || best.seasonKey==='s1'){
      const cm=candidateResourceMetric(candidate),bm=candidateResourceMetric(best);
      if(cm<bm-1e-9) return true;
      if(cm>bm+1e-9) return false;
      if(optimizerMode()==='preserve'){
        if((candidate.bankedHammersUsed||0)<(best.bankedHammersUsed||0)) return true;
        if((candidate.bankedHammersUsed||0)>(best.bankedHammersUsed||0)) return false;
      }
    }
"""
new = """    if(candidate.seasonKey==='s1' || best.seasonKey==='s1'){
      /* PRESERVE_ORE_LEXICOGRAPHIC_V1
         Once paid/total Realm-tool burden is tied, Preserve Ore means what the label says:
         minimize raw Ore spent first, even if that shifts score into safely spendable
         Essence/Sand/Treats. Acquisition Efficient keeps using reacquisition time instead.
         This never buys/uses extra Realm tools just to save Ore because betterToolBurden()
         has already been resolved above. */
      if(optimizerMode()==='preserve'){
        const cOre=Math.max(0,Number(candidate.oreCost)||0),bOre=Math.max(0,Number(best.oreCost)||0);
        if(cOre<bOre-0.5) return true;
        if(cOre>bOre+0.5) return false;
        if((candidate.bankedHammersUsed||0)<(best.bankedHammersUsed||0)) return true;
        if((candidate.bankedHammersUsed||0)>(best.bankedHammersUsed||0)) return false;
      }
      const cm=candidateResourceMetric(candidate),bm=candidateResourceMetric(best);
      if(cm<bm-1e-9) return true;
      if(cm>bm+1e-9) return false;
    }
"""
count = text.count(old)
if count != 2:
    raise SystemExit(f'Expected two candidate comparison blocks, found {count}')
text = text.replace(old, new)

text = text.replace(
    "const policy=optimizerMode()==='preserve'?'acquisition effort + 50% Ore premium':'minimize reacquisition effort';",
    "const policy=optimizerMode()==='preserve'?'minimize Ore first, then reacquisition effort':'minimize reacquisition effort';",
)
text = text.replace(
    'Joint Cart + shared-Stamina efficiency with funded-cap coverage, plus a +50% Ore premium for Gear runway.',
    'Preserve Ore minimizes Ore first within the same Realm-tool tier, then uses reacquisition efficiency for ties.',
)

path.write_text(text, encoding='utf-8')
print('Preserve Ore now strictly minimizes raw Ore within an equal tool tier.')
