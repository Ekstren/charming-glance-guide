from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')
changed = False

# Keep the generic Hammers / Knuckles / Shovels value display consistent.
if 'TOOL_VALUE_DISPLAY_V6' not in text:
    old = r'''    const gained=Math.max(0,planRuns*planPer+reserveRuns*reservePer);
    const left=Math.max(0,Math.floor(Number(top?.bankedRemaining)||0)+Math.floor(Number(top?.sparePurchasedRuns)||0));
    // TOOL_VALUE_DISPLAY_V5: if tools are being carried/used for an S2 reserve, value the
    // leftover tools at that same S2 rate so the Used and Left rows do not mix seasons.
    const leftPer=reserveRuns>0&&reservePer>0
      ? reservePer
      : Math.max(0,Number(planPer||yieldVal)||0);
    const leftValue=left*leftPer;
    const required=Math.max(0,Math.floor(Number(top?.runsNeeded)||totalRuns));'''
    new = r'''    const left=Math.max(0,Math.floor(Number(top?.bankedRemaining)||0)+Math.floor(Number(top?.sparePurchasedRuns)||0));
    // TOOL_VALUE_DISPLAY_V6: Use one display value per tool for BOTH Used and Left.
    // This applies to Hammers, Knuckles and Shovels, so a card can never mix S1 and S2
    // rates between the two rows. If any of the tools are fulfilling the season-transition
    // requirement, the whole card uses that carried-forward value; otherwise it uses the
    // current plan yield.
    const displayPer=reserveRuns>0&&reservePer>0
      ? reservePer
      : Math.max(0,Number(planPer||yieldVal)||0);
    const gained=totalRuns*displayPer;
    const leftValue=left*displayPer;
    const required=Math.max(0,Math.floor(Number(top?.runsNeeded)||totalRuns));'''
    if old not in text:
        raise SystemExit('V5 tool value block not found')
    text = text.replace(old, new, 1)
    changed = True

# Match the Fantomon Treat card to the other three cost cards. The old standalone
# unitHint creates an extra visual row and pushes the main cost down.
if 'FANTOMON_TREAT_CARD_COMPACT_V1' not in text:
    old_card = '<span>Fantomon Treats <i class="unitHint">basic-eq.</i><b id="treatCost">0</b><small id="treatBalance">—</small></span>'
    new_card = '<span><!-- FANTOMON_TREAT_CARD_COMPACT_V1 -->Fantomon Treats · basic-eq.<b id="treatCost">0</b><small id="treatBalance">—</small></span>'
    if old_card not in text:
        raise SystemExit('Fantomon Treat result card not found')
    text = text.replace(old_card, new_card, 1)
    changed = True

# Show the projected RAW inventory left after the recommended S1 upgrade spend.
# S2 reserve accounting remains hidden and is handled separately by the optimizer/tool gap logic.
if 'RAW_REMAINING_DISPLAY_V1' not in text:
    old_balance = r'''  function setEssenceBalance(id,cost,resources){ hidePlanBalance(id); }
  function setSandBalance(id,cost,resources){ hidePlanBalance(id); }
  function setTreatBalance(id,cost,resources){
    const totalNeed=Math.max(0,Number(cost)||0)+Math.max(0,Number(resources?.s2FantomonTreatReserve?.target)||0);
    const available=Math.max(0,Number(resources?.treat)||0);
    const el=$(id); if(!el) return;
    if(totalNeed<=available+0.5){ hidePlanBalance(id); return; }
    const short=Math.ceil(totalNeed-available);
    el.hidden=false; el.textContent=`${fmt(short)} Treats short`; el.classList.add('shortfallCount');
  }
'''
    new_balance = r'''  /* RAW_REMAINING_DISPLAY_V1: visible balance is only raw/material-equivalent left
     after the S1 upgrade spend. Reserve bookkeeping stays internal. */
  function setRawRemaining(id,cost,available,unitLabel='raw'){
    const el=$(id); if(!el) return;
    el.classList.remove('shortfallCount','shortfallBreakdown','reserveHasGap');
    el.classList.add('rawRemaining');
    const left=Math.max(0,Math.floor((Number(available)||0)-(Number(cost)||0)+1e-9));
    el.hidden=false;
    el.textContent=`${fmt(left)} ${unitLabel} left`;
  }
  function setEssenceBalance(id,cost,resources){ setRawRemaining(id,cost,resources?.essence,'raw'); }
  function setSandBalance(id,cost,resources){ setRawRemaining(id,cost,resources?.sand,'raw'); }
  function setTreatBalance(id,cost,resources){ setRawRemaining(id,cost,resources?.treat,'basic-eq.'); }
'''
    if old_balance not in text:
        raise SystemExit('hidden balance function block not found')
    text = text.replace(old_balance, new_balance, 1)

    old_ore = r'''      const oreBudgetWithRealm=resources.ore+(plan.realm?.ore?.provided||0);
      setBalance('oreBalance',plan.oreCost,oreBudgetWithRealm,resources.yields.orePerHammer,'Hammers');'''
    new_ore = r'''      setRawRemaining('oreBalance',plan.oreCost,resources.ore,'raw');'''
    if old_ore not in text:
        raise SystemExit('feasible Ore balance render block not found')
    text = text.replace(old_ore, new_ore, 1)
    changed = True

if changed:
    path.write_text(text, encoding='utf-8')
    print('Applied tool display, compact Fantomon card, and raw remaining balances.')
else:
    print('Tool display, Fantomon card, and raw remaining balances already current.')
