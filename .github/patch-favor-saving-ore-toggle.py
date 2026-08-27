from pathlib import Path
import re

path = Path('index.html')
text = path.read_text(encoding='utf-8')
original = text


def replace_once(old, new, label):
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly 1 match, found {count}')
    text = text.replace(old, new, 1)

# Replace the two-button optimizer selector styling with one compact checkbox toggle.
pattern = r'<style id="optimizer-priority-toggle-v1">.*?</style>'
new_css = '''<style id="favor-saving-ore-toggle-v1">
/* FAVOR_SAVING_ORE_TOGGLE_V1 · efficient optimizer is always the base policy */
.optimizerModeRow{display:flex;align-items:center;justify-content:space-between;gap:16px;border:1px solid var(--line);background:var(--ui-subpanel,var(--bg));border-radius:11px;margin:10px 0;padding:10px 12px}
.optimizerModeCopy{display:grid;gap:3px;min-width:0}.optimizerModeCopy b{color:var(--ink);font-size:10px}.optimizerModeCopy small{color:var(--muted);font-size:9px;line-height:1.4}
.favorOreToggle{display:flex;align-items:center;gap:8px;flex:0 0 auto;min-height:34px;border:1px solid var(--line);background:var(--input-bg,var(--surface));border-radius:10px;padding:7px 11px;color:var(--ink);cursor:pointer;font-size:9px;font-weight:850;white-space:nowrap}
.favorOreToggle input{margin:0;accent-color:var(--calc-accent-strong,var(--accent-strong));cursor:pointer}
@media(max-width:700px){.optimizerModeRow{align-items:stretch;flex-direction:column}.favorOreToggle{width:100%;justify-content:flex-start;white-space:normal;min-height:42px}}
</style>'''
text, n = re.subn(pattern, new_css, text, count=1, flags=re.S)
if n != 1:
    raise SystemExit(f'optimizer CSS: expected 1 match, found {n}')

old_html = '''        <div class="optimizerModeRow" id="optimizerModeRow">
          <div class="optimizerModeCopy"><b>Optimization priority</b><small id="optimizerModeNote">Use acquisition effort, with an extra future-value premium on Ore/Hammers.</small></div>
          <div class="optimizerModeToggle" role="group" aria-label="Optimization priority">
            <button type="button" data-optimizer-mode="preserve" aria-pressed="true">Preserve Ore</button>
            <button type="button" data-optimizer-mode="acquisition" aria-pressed="false">Acquisition Efficient</button>
          </div>
          <input id="optimizerMode" type="hidden" value="preserve">
        </div>'''
new_html = '''        <div class="optimizerModeRow" id="optimizerModeRow">
          <div class="optimizerModeCopy"><b>Resource strategy</b><small id="optimizerModeNote">Efficient raw-first planning using normal replacement effort across resources.</small></div>
          <label class="favorOreToggle"><input id="favorOre" type="checkbox"> Favor saving Ore</label>
        </div>'''
replace_once(old_html, new_html, 'optimizer controls')

replace_once(
    "'hammerCurrent','knucklesCurrent','shovelCurrent','staminaMode','optimizerMode','realmDailyOre','realmDailyEssence','realmDailySand'",
    "'hammerCurrent','knucklesCurrent','shovelCurrent','staminaMode','realmDailyOre','realmDailyEssence','realmDailySand'",
    'INPUT_IDS optimizerMode removal'
)
replace_once(
    "const CHECK_IDS = ['freeSpeed','holdExp','grace12','reserveS2Essence','reserveS2Sand','reserveS2Treats'];",
    "const CHECK_IDS = ['freeSpeed','holdExp','grace12','reserveS2Essence','reserveS2Sand','reserveS2Treats','favorOre'];",
    'CHECK_IDS favorOre addition'
)

old_js = '''  const optimizerMode = () => {
    const raw=$('optimizerMode')?.value;
    // Migrate the short-lived Balanced mode to the new acquisition-efficiency model.
    return raw==='acquisition'||raw==='balanced' ? 'acquisition' : 'preserve';
  };
  function updateOptimizerModeUI(){
    const mode=optimizerMode();
    const input=$('optimizerMode');
    if(input && input.value==='balanced') input.value='acquisition';
    const row=$('optimizerModeRow');
    if(row) row.hidden=activeCalcConfig().key!=='s1';
    document.querySelectorAll('[data-optimizer-mode]').forEach(btn=>{
      const active=btn.dataset.optimizerMode===mode;
      btn.classList.toggle('active',active);
      btn.setAttribute('aria-pressed',active?'true':'false');
    });
    const note=$('optimizerModeNote');
    if(note) note.textContent=mode==='preserve'
      ? 'Raw-first gates: reserve S2 tools first, spend safe capped raw before Realm tools, then apply a +50% Ore premium for Gear runway.'
      : 'Raw-first gates: reserve S2 tools first, spend fully funded capped raw before Realm tools, then minimize replacement effort.';
  }
  document.querySelectorAll('[data-optimizer-mode]').forEach(btn=>btn.addEventListener('click',()=>{
    const input=$('optimizerMode');
    if(!input) return;
    input.value=btn.dataset.optimizerMode==='acquisition'?'acquisition':'preserve';
    updateOptimizerModeUI();
    saveState();
    scheduleCalculatorUpdate(0);
  }));'''
new_js = '''  // FAVOR_SAVING_ORE_TOGGLE_V1: acquisition-efficient planning is always the base model.
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
  }'''
replace_once(old_js, new_js, 'optimizer mode JS')

# Preserve each existing user's old two-button choice on the first load after migration.
load_anchor = '''      INPUT_IDS.forEach(id => { if (state[id] !== undefined && $(id)) $(id).value = state[id]; });
      CHECK_IDS.forEach(id => { if (state[id] !== undefined && $(id)) $(id).checked = !!state[id]; });'''
load_replacement = '''      // FAVOR_SAVING_ORE_TOGGLE_V1 migration: preserve the user's previous selector choice.
      if(state.favorOre===undefined && state.optimizerMode!==undefined){
        state.favorOre = state.optimizerMode==='preserve';
      }
      INPUT_IDS.forEach(id => { if (state[id] !== undefined && $(id)) $(id).value = state[id]; });
      CHECK_IDS.forEach(id => { if (state[id] !== undefined && $(id)) $(id).checked = !!state[id]; });'''
replace_once(load_anchor, load_replacement, 'state migration')

# Remove the obsolete hidden optimizer default from the S2 reset object.
replace_once(
    "shovelCurrent:0,staminaMode:'ore',optimizerMode:'preserve',realmDailyOre:0",
    "shovelCurrent:0,staminaMode:'ore',realmDailyOre:0",
    'S2 optimizer default removal'
)

old_doc = '''After those are protected, the Optimization priority decides the tie-break: Acquisition Efficient minimizes estimated replacement effort from the entered Cart rates plus the current map yield (one 5-Stamina node per natural hour); Preserve Ore uses the same acquisition model but applies a 50% strategic premium to Ore/Hammers because Gear has the broadest progression runway.'''
new_doc = '''After those are protected, the planner always minimizes estimated replacement effort from the entered Cart rates plus the current map yield (one 5-Stamina node per natural hour). If Favor saving Ore is enabled, that same efficient model applies a 50% strategic premium to Ore/Hammers because Gear has the broadest progression runway.'''
replace_once(old_doc, new_doc, 'details optimizer wording')

if text == original:
    raise SystemExit('patch made no changes')
path.write_text(text, encoding='utf-8')
print('Applied FAVOR_SAVING_ORE_TOGGLE_V1')
