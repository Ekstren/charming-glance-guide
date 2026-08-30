from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
marker='PURCHASE_RESTOCK_LABELS_V1'
if marker in s:
    print('Purchase/restock labels already applied')
    raise SystemExit(0)

repls={
    'Daily Realm refresh plan':'Daily Realm purchase plan',
    'Each refresh = 5 tools · max 20/day per Realm':'Each purchase = 5 tools · max 20/day per Realm',
    'Ore Realm refreshes / day':'Ore Realm purchases / day',
    'Essence Realm refreshes / day':'Essence Realm purchases / day',
    'Sand Realm refreshes / day':'Sand Realm purchases / day',
    'paid Realm refreshes need >20%':'paid Realm purchases need >20%',
    'additional paid Realm refreshes must improve it by more than 20%':'additional Realm purchases must improve it by more than 20%',
    'A route that requires additional paid Realm refreshes':'A route that requires additional Realm purchases',
    'Paid refreshes face the higher hurdle.':'Realm purchases face the higher hurdle.',
    'Each paid refresh grants <b>5 actual Realm entries/tools</b>':'Each Realm purchase grants <b>5 actual Realm entries/tools</b>',
    '20 refreshes per Realm per server day':'20 purchases per Realm per server day',
    'refreshes 1–10:':'purchases 1–10:',
    'Refreshes 11–20':'Purchases 11–20',
    'additional paid refreshes require more than a 20% improvement':'additional Realm purchases require more than a 20% improvement',
    'paid refreshes merely to save Ore':'Realm purchases merely to save Ore',
    'additional paid refreshes are the final fallback':'additional Realm purchases are the final fallback',
    'Recommended: ${fmt(recommended)} ${realmLabel} Realm refresh${recommended===1?\'\':\'es\'}/day':'Recommended: ${fmt(recommended)} ${realmLabel} Realm purchase${recommended===1?\'\':\'s\'}/day',
    '>Apply refreshes</button>':'>Apply purchases</button>',
    'recommended Material Realm refresh plan':'recommended Material Realm purchase plan',
    'Shop refreshes / day':'Shop restocks / day',
    'Set refreshes/day to include the extremely conservative Daily Shop material estimate.':'Set restocks/day to include the extremely conservative Daily Shop material estimate.',
    'each paid refresh counts only <b>2/3 of one current-season map bundle</b>':'each restock counts only <b>2/3 of one current-season map bundle</b>',
    'per refresh;':'per restock;',
    'per refresh</b>':'per restock</b>',
    '3 refreshes/day':'3 restocks/day',
}

changed=[]
for old,new in repls.items():
    if old in s:
        s=s.replace(old,new)
        changed.append(old)

# Add a harmless marker in the final style block so the patch is idempotent.
idx=s.rfind('</style>')
if idx<0:
    raise SystemExit('style close not found')
s=s[:idx]+f'\n/* {marker} */\n'+s[idx:]
p.write_text(s,encoding='utf-8')
print(f'Applied purchase/restock terminology ({len(changed)} replacements)')
