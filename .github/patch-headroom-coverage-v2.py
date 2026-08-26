from pathlib import Path

PATH=Path('index.html')
text=PATH.read_text(encoding='utf-8')
MARKER='DYNAMIC_HEADROOM_WEIGHTS_V2'
if MARKER in text:
    print('Coverage-aware headroom weighting already applied.')
    raise SystemExit(0)

old="""      // usefulShare=1 means all current supply can still be productively spent before the
      // safe cap. If supply already exceeds that headroom, only the excess is discounted.
      const usefulShare=usefulNeed<=0?0:(available>0?Math.min(1,usefulNeed/available):1);
      result[key]=floor+(1-floor)*usefulShare;
"""
new="""      // Value the NEXT unit by how much of the reachable cap is still UNFUNDED, rather
      // than pinning the material at full value until the entire cap can be paid at once.
      // Example: if 90% of the reachable Relic cap is already funded, Sand sits only 10%
      // above its deferred-use floor instead of being treated as maximally scarce.
      const fundedCoverage=usefulNeed<=0?1:(available>0?Math.min(1,available/usefulNeed):0);
      const unfundedShare=1-fundedCoverage;
      result[key]=floor+(1-floor)*unfundedShare;
"""
if text.count(old)!=1:
    raise SystemExit(f'coverage formula match count={text.count(old)}')
text=text.replace(old,new,1)
text=text.replace('DYNAMIC_HEADROOM_WEIGHTS_V1','DYNAMIC_HEADROOM_WEIGHTS_V1 · DYNAMIC_HEADROOM_WEIGHTS_V2',1)
text=text.replace(
    "      ? 'Joint Cart + shared-Stamina efficiency with dynamic safe-cap headroom, plus a +50% Ore premium for Gear runway.'\n      : 'Joint Cart + shared-Stamina efficiency with dynamic safe-cap headroom for Essence, Sand and Treats.';",
    "      ? 'Joint Cart + shared-Stamina efficiency with funded-cap coverage, plus a +50% Ore premium for Gear runway.'\n      : 'Joint Cart + shared-Stamina efficiency; capped resources get cheaper as their reachable cap becomes funded.';",
    1
)
PATH.write_text(text,encoding='utf-8')
print('Applied coverage-aware dynamic headroom weighting.')
