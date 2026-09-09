from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
old="""    ['2026-09-08',56,'Event','Gift code · CRYSTAL','STRONGLY SUPPORTED CURRENT REPORT: GamesRadar updated Sep. 8 lists CRYSTAL as the new Community Weekly Gift Code, rewarding 300 Raw Ore + 1 Stellatie and expiring Sep. 15, 2026. A current community code tracker independently lists CRYSTAL as new on Sep. 8. The mirrored official Global Discord feed has not yet carried this code (latest mirrored official post is Sep. 7), so the exact expiry clock is not confirmed here; redeem promptly rather than assuming it lasts through the full Sep. 15 Charming Glance day.','event','2026-09-15'],"""
new="""    // CRYSTAL_EXPIRY_SEP9_V1: current code trackers agree on Sep. 15 00:00 UTC-5; official mirror has not carried CRYSTAL yet.
    // This resolves to Sep. 14 10:00 PM PDT for Charming Glance, eight hours before the Sep. 15 server reset.
    ['2026-09-08',56,'Event','Gift code · CRYSTAL','Current reports list CRYSTAL as the Community Weekly Gift Code: 300 Raw Ore + 1 Stellatie. Reported expiry is Sep. 15 at 00:00 UTC-5, which is Sep. 14 at 10:00 PM PDT for Charming Glance. The mirrored official Global feed has not carried this code yet.','event','2026-09-15','unconfirmed','2026-09-15T05:00:00Z'],"""
if old not in s:
    raise SystemExit('CRYSTAL timeline row not found; refusing to patch')
s=s.replace(old,new,1)
old_summary="""    if(title==='Gift code · CRYSTAL') return '300 Raw Ore + 1 Stellatie · redeem before the reported Sep. 15 expiry.';"""
new_summary="""    if(title==='Gift code · CRYSTAL') return '300 Raw Ore + 1 Stellatie · reported cutoff Sep. 14 at 10:00 PM PDT.';"""
if old_summary not in s:
    raise SystemExit('CRYSTAL summary override not found; refusing to patch')
s=s.replace(old_summary,new_summary,1)
p.write_text(s,encoding='utf-8')
print('Applied CRYSTAL exact reported expiry and PDT cutoff.')
