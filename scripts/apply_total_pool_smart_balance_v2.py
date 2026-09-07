from pathlib import Path

src_path=Path('scripts/apply_total_pool_smart_balance_v1.py')
src=src_path.read_text(encoding='utf-8')
bad='  function marginalWeightedCosts(costs,resources,cfg=activeCalcConfig()){"\ns=s[:m.start()]+new_scarcity+s[m.end():]'
good='  function marginalWeightedCosts(costs,resources,cfg=activeCalcConfig()){"""\ns=s[:m.start()]+new_scarcity+s[m.end():]'
if bad in src:
    src=src.replace(bad,good,1)
    src_path.write_text(src,encoding='utf-8')
    print('Repaired total-pool v1 patch source.')
exec(compile(src,str(src_path)+'::v2-fixed','exec'))
