from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

if 'REALM_OPTION_PROPERTY_CACHE_V7' in s:
    print('Primostar Realm option property cache already applied.')
    raise SystemExit(0)
if 'NO_PAID_PRIMARY_FAST_COMPARE_V5' not in s:
    raise SystemExit('v8 optimizer marker not found')
if 'BOUNDED_COMPACT_BEST_V6' in s:
    raise SystemExit('rejected v9 compact candidate experiment is present; refusing to stack v10')

old="""    const oreCache=new Map(),essCache=new Map(),sandCache=new Map();
    const oreFor=go=>{const k=go.oreCost;if(!oreCache.has(k))oreCache.set(k,realmTopupFor('ore',k,resources.ore,resources,cfg,p));return oreCache.get(k);};
    const essFor=so=>{const k=so.cost;if(!essCache.has(k))essCache.set(k,realmTopupFor('essence',k,resources.essence,resources,cfg,p));return essCache.get(k);};
    const sandFor=ro=>{const k=ro.cost;if(!sandCache.has(k))sandCache.set(k,realmTopupFor('sand',k,resources.sand,resources,cfg,p));return sandCache.get(k);};
"""
new="""    /* REALM_OPTION_PROPERTY_CACHE_V7
       Realm top-up results are immutable for one search snapshot and every option object is
       search-local. Cache the result directly on the option instead of doing Map.has()+Map.set()
       +Map.get() on every hot-loop access. This preserves lazy evaluation (unused options still
       cost nothing) while turning repeat Gear/Skill/Relic lookups into one property read. */
    const oreFor=go=>go.__realmOreV7||(go.__realmOreV7=realmTopupFor('ore',go.oreCost,resources.ore,resources,cfg,p));
    const essFor=so=>so.__realmEssenceV7||(so.__realmEssenceV7=realmTopupFor('essence',so.cost,resources.essence,resources,cfg,p));
    const sandFor=ro=>ro.__realmSandV7||(ro.__realmSandV7=realmTopupFor('sand',ro.cost,resources.sand,resources,cfg,p));
"""
if old not in s:
    raise SystemExit('Realm Map-cache anchor not found')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('Applied Primostar v10 direct option-property Realm cache.')
