from pathlib import Path

path = Path('assets/runtime.js')
text = path.read_text(encoding='utf-8')

old = "s2:{key:'s2',name:'Season 2',nextName:'Season 3',end:S2_END,deadline:'device-local',scoreFloor:130,relicFloor:13,starBase:45,scorePerStar:27,weights:{character:100,gear:18,skill:7,relic:33,fanto:8},skillCap:null,relicCap:null,fantoCap:null,gearCap:null,realmMaxLevel:120,realm:{ore:1200,essence:1500,sand:1000,rolla:11800},map:{ore:1400,essence:1770,sand:1180,rolla:14000,bigRate:0.0932},optimizeRelic:true,optimizeFanto:true}"
new = "s2:{key:'s2',name:'Season 2',nextName:'Season 3',end:S2_END,deadline:'device-local',scoreFloor:130,relicFloor:13,starBase:45,scorePerStar:27,weights:{character:100,gear:18,skill:7,relic:33,fanto:8},skillCap:null,relicCap:null,fantoCap:null,gearCap:null,realmMaxLevel:120,realm:{ore:1888.455092195316,essence:2645.717313492359,sand:1797.432822048046,rolla:19169.242644394664},map:{ore:1400,essence:1770,sand:1180,rolla:14000,bigRate:0.0932},optimizeRelic:true,optimizeFanto:true}"

marker = "/* S2_MINED_REALM_YIELDS_V1\n     S2 max-bracket (Champion III / client Saint III) Material Realm averages are precomputed\n     from factual live-client tables: rank multiplier 19.5 plus object weights, durability,\n     hit-damage probabilities, break rewards and free-box rules. Values are long-run expected\n     resources per actual Realm run/tool. Sand is Basic/White equivalent (Blue x5, Purple x25). */\n"
anchor = "  const CALC_SEASONS = {\n"

if old in text:
    text = text.replace(old, new, 1)
elif new not in text:
    raise SystemExit('Expected S2 config not found; refusing unsafe patch')

if 'S2_MINED_REALM_YIELDS_V1' not in text:
    if anchor not in text:
        raise SystemExit('CALC_SEASONS anchor not found')
    text = text.replace(anchor, marker + anchor, 1)

path.write_text(text, encoding='utf-8')
print('patched S2 mined Realm yields')
