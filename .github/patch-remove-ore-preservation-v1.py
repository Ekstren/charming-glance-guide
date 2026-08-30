from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
orig=s

# REMOVE_ORE_PRESERVATION_V1
# The S1-specific +50% Ore bias predates the global acquisition-efficiency optimizer and
# Minimize-tools policy. Remove both the user-facing note and the hidden optimizer bias.

s=s.replace('          <input id="reserveS2Ore" checked type="checkbox" hidden>\n','')
s=s.replace('        <small class="seasonPlanningNote" id="oreReserveNote"><b>Ore preservation:</b> Ore gets a 50% premium in optimizer comparisons, so comparable non-Ore routes are preferred. It is a soft preference, not a hard reserve—the planner will still spend Ore when preserving it would sacrifice overall efficiency.</small>\n','')
s=s.replace("      // S2_ORE_PREMIUM_V1: existing saved states opt into the new soft Ore-preservation preference.\n      if(hadState && state.reserveS2Ore===undefined) state.reserveS2Ore=true;\n",'')
s=s.replace("    ['reserveS2Ore','reserveS2Essence','reserveS2Sand','reserveS2Treats'].forEach(id=>{", "    ['reserveS2Essence','reserveS2Sand','reserveS2Treats'].forEach(id=>{")
s=s.replace("    if($('oreReserveNote')) $('oreReserveNote').hidden=!(cfg.key==='s1' && $('reserveS2Ore')?.checked);\n",'')

old="""  /* S2_ORE_PREMIUM_V1
     Soft S2 Ore preservation: within the optimizer's existing efficiency stage, spending Ore
     is valued at 1.5x. Hard efficiency gates still win first, so this cannot force extra Realm
     tool use or paid refreshes merely to save Ore. */
  function marginalWeightedCosts(costs,resources,cfg=activeCalcConfig()){
    const orePremium=(cfg.key==='s1' && $('reserveS2Ore')?.checked)?1.5:1;
    return {
      ore:Math.max(0,Number(costs?.ore)||0)*orePremium,
"""
new="""  /* REMOVE_ORE_PRESERVATION_V1
     Ore now participates in the same acquisition-efficiency model as every other score
     resource. Tool preservation is handled only by the Minimize-tools 10%/20% hurdles. */
  function marginalWeightedCosts(costs,resources,cfg=activeCalcConfig()){
    return {
      ore:Math.max(0,Number(costs?.ore)||0),
"""
if old not in s:
    raise SystemExit('expected S2 Ore premium block not found')
s=s.replace(old,new,1)

if s==orig:
    raise SystemExit('no changes made')
for forbidden in ['id="oreReserveNote"','reserveS2Ore','S2_ORE_PREMIUM_V1','orePremium']:
    if forbidden in s:
        raise SystemExit(f'stale ore-preservation remnant: {forbidden}')
if 'REMOVE_ORE_PRESERVATION_V1' not in s:
    raise SystemExit('cleanup marker missing')
if 'REALM_SAVED_TOOL_EFFICIENCY_HURDLE=0.10' not in s or 'REALM_PAID_REFRESH_EFFICIENCY_HURDLE=0.20' not in s:
    raise SystemExit('Minimize-tools hurdles changed unexpectedly')
if "reserveHours:34" not in s:
    raise SystemExit('34h Bed hold changed unexpectedly')

p.write_text(s,encoding='utf-8')
print('Removed obsolete Ore-preservation note and +50% optimizer bias.')
