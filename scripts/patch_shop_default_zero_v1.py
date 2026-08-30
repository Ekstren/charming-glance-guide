from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

# Make Daily Shop opt-in instead of assuming 3 refreshes/day.
s = s.replace(
    'id="shopRefreshesDaily" type="number" min="0" max="20" step="1" value="3"><small>Default plan: 3/day</small>',
    'id="shopRefreshesDaily" type="number" min="0" max="20" step="1" value="0"><small>Default: 0/day</small>'
)
s = s.replace('shopRefreshesDaily:3,', 'shopRefreshesDaily:0,')
s = s.replace('The default plan is 3 refreshes/day.', 'The default is 0 refreshes/day; users opt in to the number they actually buy.')

# One-time migration for states created while 3/day was the built-in default.
# After this migration, a user may freely choose 3 again and it will persist.
marker = 'SHOP_REFRESH_DEFAULT_ZERO_V1'
if marker not in s:
    needle = "      hadState = Object.keys(state).length>0;\n      if(hadState && state.preserveRealmTools===undefined) state.preserveRealmTools=true;"
    repl = "      hadState = Object.keys(state).length>0;\n      // SHOP_REFRESH_DEFAULT_ZERO_V1: the shop estimator is opt-in. Migrate the old inherited 3/day once.\n      if(hadState && localStorage.getItem('sxs-shop-refresh-default-zero-v1')!=='1'){\n        if(Number(state.shopRefreshesDaily)===3) state.shopRefreshesDaily=0;\n        localStorage.setItem('sxs-shop-refresh-default-zero-v1','1');\n      }\n      if(hadState && state.preserveRealmTools===undefined) state.preserveRealmTools=true;"
    if needle not in s:
        raise SystemExit('loadState migration anchor not found')
    s = s.replace(needle, repl, 1)

p.write_text(s, encoding='utf-8')

# Keep current source patchers from reintroducing the old default if rerun later.
for source in [Path('scripts/patch_shop_panel_final_v4.py'), Path('scripts/patch_shop_grounded_estimate_v5.py')]:
    if not source.exists():
        continue
    t = source.read_text(encoding='utf-8')
    t = t.replace('value=\\"3\\"><small>Default plan: 3/day</small>', 'value=\\"0\\"><small>Default: 0/day</small>')
    t = t.replace('value="3"><small>Default plan: 3/day</small>', 'value="0"><small>Default: 0/day</small>')
    t = t.replace('shopRefreshesDaily:3,', 'shopRefreshesDaily:0,')
    t = t.replace('The default plan is 3 refreshes/day.', 'The default is 0 refreshes/day; users opt in to the number they actually buy.')
    source.write_text(t, encoding='utf-8')

print('Daily Shop default set to 0/day')
