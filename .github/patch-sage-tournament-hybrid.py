from pathlib import Path
import re

FILES=[Path('index.html'),Path('.github/build-fantomons-inject.html')]
MARK='SAGE_TOURNAMENT_HYBRID_V1'

ARCANIST="      role('Tournament','Hybrid team pressure / revive utility',['Mana Blast','Abyssal Hand','Radiant Restoration','Frenzy Totem'],['Resurrection','Shadow Vengeance','Shadow Erosion','Linked Misfortune'],'Tournament should not default to full healing: Mana Blast + Abyssal Hand provide Dark pressure, Erosion and Slow while Frenzy Totem buffs the team and Radiant Restoration gives one efficient group-heal slot.','PvP healing is heavily reduced. Only move toward the dedicated Healing card when your Healing Boost/SPD are genuinely built for it; otherwise keep Resurrection + damage/debuff utility.','Community hybrid PvP')"

DOMINATOR="      role('Tournament','Hybrid support / anti-tank pressure',['Decoy Clone','Frenzy Totem','Dark Starburst','Abyssal Hand'],['Mantra of Blessings','Resurrection','Shadow Vengeance',\"Night's Blessing\"],'Use Dominator as a support/sub-DPS, not a pure healer: Decoy Clone pressures shield-heavy tanks, Frenzy Totem + Mantra amplify the carry, and Dark Starburst/Abyssal Hand keep meaningful direct pressure and Slow utility.','If your team truly needs healing, Abyssal Hand → Radiant Restoration. Full healing should be reserved for unusually high Healing Boost/SPD setups because PvP cuts healing effectiveness.','Community hybrid PvP')"

TOURNAMENT_PICKS={
    'Arcanist': "      Tournament:[pick('Nyxarchon','Main hybrid Tournament pick: damage plus DEF shred contributes even while you spend slots on team utility.'),pick('Sylvaerie','Alt for ATK + SPD; speed is especially valuable for getting support/debuff actions out early.')],\n",
    'Dominator': "      Tournament:[pick('Nyxarchon','Main hybrid Tournament pick: adds real damage and DEF shred while the Dominator handles buffs and utility.'),pick('Terragon','Alt team-utility pick when reducing enemy ATK/pressure matters more than personal damage.')],\n",
}

for p in FILES:
    s=p.read_text(encoding='utf-8')
    if MARK in s:
        print(p,'already patched')
        continue

    s,n1=re.subn(r"^      role\('Tournament','Team sustain / revive support'.*$",ARCANIST,s,count=1,flags=re.M)
    if n1!=1:
        raise SystemExit(f'Arcanist Tournament preset not found exactly once in {p}: {n1}')
    s,n2=re.subn(r"^      role\('Tournament','Team support / carry protection'.*$",DOMINATOR,s,count=1,flags=re.M)
    if n2!=1:
        raise SystemExit(f'Dominator Tournament preset not found exactly once in {p}: {n2}')

    fanto=s.find('  const FANTO={')
    if fanto<0:
        raise SystemExit(f'FANTO block missing in {p}')
    for cls,block in TOURNAMENT_PICKS.items():
        anchor=f"    {cls}:{{\n"
        pos=s.find(anchor,fanto)
        if pos<0:
            raise SystemExit(f'{cls} FANTO anchor missing in {p}')
        pos+=len(anchor)
        if s.startswith('      Tournament:[',pos):
            continue
        s=s[:pos]+block+s[pos:]

    old="""    if(role==='Tournament'){
      if(cls==='Arcanist'||cls==='Dominator') return pools.Tournament||pools.Dungeon||pools.PvP||[];
      return pools.Tournament||pools.PvP||[];
    }"""
    new="""    if(role==='Tournament'){
      return pools.Tournament||pools.PvP||pools.Dungeon||[];
    }"""
    if old in s:
        s=s.replace(old,new,1)

    marker='/* BUILD_ARENA_TOURNAMENT_SPLIT_V1 */'
    if marker in s:
        s=s.replace(marker,marker+'\n/* '+MARK+' */',1)
    else:
        raise SystemExit(f'build split marker missing in {p}')

    p.write_text(s,encoding='utf-8')
    print('updated hybrid Tournament Sage builds in',p)
