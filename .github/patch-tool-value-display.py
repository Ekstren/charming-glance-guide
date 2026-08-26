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

if changed:
    path.write_text(text, encoding='utf-8')
    print('Applied consistent Realm tool values and compact Fantomon Treat card.')
else:
    print('Tool value display and Fantomon Treat card already current.')
