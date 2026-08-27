from pathlib import Path
import re

PATH=Path('index.html')
text=PATH.read_text(encoding='utf-8')
original=text
MARKER='REMOVE_RESOURCE_STRATEGY_V1'
if MARKER in text:
    print('Resource strategy section already removed.')
    raise SystemExit(0)

# Remove the dedicated Favor saving Ore / Resource strategy styling block.
text,n=re.subn(r'\n?<style id="favor-saving-ore-toggle-v1">.*?</style>\n?', '\n', text, count=1, flags=re.S)
if n!=1:
    raise SystemExit(f'favor-saving-ore CSS: expected 1 match, found {n}')

# Remove the visible Resource strategy row while leaving the optimizer explanation directly below it.
text,n=re.subn(
    r'\s*<div class="optimizerModeRow" id="optimizerModeRow">.*?</div>\s*(?=<details class="optimizerExplain")',
    '\n        ',
    text,
    count=1,
    flags=re.S,
)
if n!=1:
    raise SystemExit(f'resource strategy row: expected 1 match, found {n}')

# The planner is now always the acquisition-efficient/raw-first model.
old_js="""  // FAVOR_SAVING_ORE_TOGGLE_V1: acquisition-efficient planning is always the base model.
  // The checkbox only adds the existing +50% strategic Ore/Hammer premium.
  const optimizerMode = () => $('favorOre')?.checked ? 'preserve' : 'acquisition';
  function updateOptimizerModeUI(){
    const favorOre=optimizerMode()==='preserve';
    const row=$('optimizerModeRow');
    if(row) row.hidden=activeCalcConfig().key!=='s1';
    const note=$('optimizerModeNote');
    if(note) note.textContent=favorOre
      ? 'Efficient raw-first planning with a +50% strategic premium on Ore/Hammers.'
      : 'Efficient raw-first planning using normal replacement effort across resources.';
  }"""
new_js="""  /* REMOVE_RESOURCE_STRATEGY_V1: one optimizer policy only — raw-first, acquisition-efficient. */
  const optimizerMode = () => 'acquisition';
  function updateOptimizerModeUI(){}"""
if text.count(old_js)!=1:
    raise SystemExit(f'optimizer mode JS: expected 1 match, found {text.count(old_js)}')
text=text.replace(old_js,new_js,1)

# Stop persisting the removed checkbox.
old_checks="const CHECK_IDS = ['freeSpeed','holdExp','grace12','reserveS2Essence','reserveS2Sand','reserveS2Treats','favorOre'];"
new_checks="const CHECK_IDS = ['freeSpeed','holdExp','grace12','reserveS2Essence','reserveS2Sand','reserveS2Treats'];"
if text.count(old_checks)!=1:
    raise SystemExit(f'CHECK_IDS: expected 1 match, found {text.count(old_checks)}')
text=text.replace(old_checks,new_checks,1)

# Remove migration of the obsolete selector/toggle state.
text,n=re.subn(
    r'\s*// FAVOR_SAVING_ORE_TOGGLE_V1 migration: preserve the user\'s previous selector choice\.\s*if\(state\.favorOre===undefined && state\.optimizerMode!==undefined\)\{\s*state\.favorOre = state\.optimizerMode===\'preserve\';\s*\}\s*',
    '\n      ',
    text,
    count=1,
    flags=re.S,
)
if n!=1:
    raise SystemExit(f'favorOre state migration: expected 1 match, found {n}')

# Update the public explanation so it no longer references a removed control.
old_explain="<b>Auto Stamina</b> tests Ore, Essence and Sand gathering against the selected upgrade route and uses the split that reduces required paid Realm farming. <b>Gear Lock</b> removes new Gear levels from consideration. <b>Favor saving Ore</b> keeps the same optimizer and gate order, but applies a +50% strategic cost premium to Ore/Hammers so close alternatives lean away from Gear."
new_explain="<b>Auto Stamina</b> tests Ore, Essence and Sand gathering against the selected upgrade route and uses the split that reduces required paid Realm farming. <b>Gear Lock</b> removes new Gear levels from consideration. The optimizer otherwise uses one consistent acquisition-efficient, raw-first policy so the same inputs always produce the same resource strategy."
if text.count(old_explain)!=1:
    raise SystemExit(f'optimizer explanation favorOre line: expected 1 match, found {text.count(old_explain)}')
text=text.replace(old_explain,new_explain,1)

# Update the formula/method documentation if the old Favor Ore sentence is still present.
old_doc="After those are protected, the planner always minimizes estimated replacement effort from the entered Cart rates plus the current map yield (one 5-Stamina node per natural hour). If Favor saving Ore is enabled, that same efficient model applies a 50% strategic premium to Ore/Hammers because Gear has the broadest progression runway."
new_doc="After those are protected, the planner minimizes estimated replacement effort from the entered Cart rates plus the current map yield (one 5-Stamina node per natural hour), using one consistent acquisition-efficient raw-first strategy across all resources."
if old_doc in text:
    text=text.replace(old_doc,new_doc,1)

if text==original:
    raise SystemExit('patch made no changes')
PATH.write_text(text,encoding='utf-8')
print('Removed Resource strategy / Favor saving Ore UI and standardized the optimizer on acquisition-efficient raw-first planning.')
