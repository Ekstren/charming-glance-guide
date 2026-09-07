from pathlib import Path

src_path=Path('scripts/apply_total_pool_smart_balance_v1.py')
src=src_path.read_text(encoding='utf-8')
bad='  function marginalWeightedCosts(costs,resources,cfg=activeCalcConfig()){"\ns=s[:m.start()]+new_scarcity+s[m.end():]'
good='  function marginalWeightedCosts(costs,resources,cfg=activeCalcConfig()){"""\ns=s[:m.start()]+new_scarcity+s[m.end():]'
if bad not in src:
    raise SystemExit('v1 string-close anchor not found')
src=src.replace(bad,good,1)
exec(compile(src,str(src_path)+'::v2-fixed','exec'))
