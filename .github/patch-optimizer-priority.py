from pathlib import Path

PATH = Path('index.html')
text = PATH.read_text(encoding='utf-8')
MARKER = 'OPTIMIZER_PRIORITY_TOGGLE_V1'

if MARKER in text:
    print('Optimizer priority toggle already applied.')
    raise SystemExit(0)


def replace_once(old: str, new: str, label: str):
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly 1 match, found {count}')
    text = text.replace(old, new, 1)

# UI: place the strategy control beside the other season-planning choices, but keep
# it independent from the reserve toggles. The hidden value participates in the
# calculator's normal save/reset state machinery.
season_note = '        <small class="seasonPlanningNote" id="graceText">Cart income and projected Stamina generation stop 12 hours before season end.</small>\n'
strategy_ui = season_note + '''        <div class="optimizerModeRow" id="optimizerModeRow">
          <div class="optimizerModeCopy"><b>Optimization priority</b><small id="optimizerModeNote">Protect Ore/Hammers after the target and hard S2 reserves are safe.</small></div>
          <div class="optimizerModeToggle" role="group" aria-label="Optimization priority">
            <button type="button" data-optimizer-mode="preserve" aria-pressed="true">Preserve Ore</button>
            <button type="button" data-optimizer-mode="balanced" aria-pressed="false">Balanced resources</button>
          </div>
          <input id="optimizerMode" type="hidden" value="preserve">
        </div>
'''
replace_once(season_note, strategy_ui, 'strategy UI insertion')

# Persist/reset the mode with the rest of the calculator state.
replace_once(
    "'hammerCurrent','knucklesCurrent','shovelCurrent','staminaMode','realmDailyOre'",
    "'hammerCurrent','knucklesCurrent','shovelCurrent','staminaMode','optimizerMode','realmDailyOre'",
    'INPUT_IDS optimizerMode',
)
replace_once(
    "staminaMode:'ore',realmDailyOre:0",
    "staminaMode:'ore',optimizerMode:'preserve',realmDailyOre:0",
    'S2 reset optimizerMode',
)

# Runtime accessor + segmented control rendering. Balanced mode intentionally does
# not change score formulas, target, reserves, Realm pricing, or Stamina yields; it
# only disables the late-S1 Ore-first tie breaker.
mode_anchor = "  const staminaModeLabel = (mode = staminaMode()) => ({ore:'Ore',auto:'Auto',essence:'Skill Essence',sand:'Chrono Sand'})[mode] || 'Ore';\n"
mode_code = mode_anchor + '''  const optimizerMode = () => $('optimizerMode')?.value === 'balanced' ? 'balanced' : 'preserve';
  function updateOptimizerModeUI(){
    const mode=optimizerMode();
    const row=$('optimizerModeRow');
    if(row) row.hidden=activeCalcConfig().key!=='s1';
    document.querySelectorAll('[data-optimizer-mode]').forEach(btn=>{
      const active=btn.dataset.optimizerMode===mode;
      btn.classList.toggle('active',active);
      btn.setAttribute('aria-pressed',active?'true':'false');
    });
    const note=$('optimizerModeNote');
    if(note) note.textContent=mode==='preserve'
      ? 'Protect Ore/Hammers after the target and hard S2 reserves are safe.'
      : 'Treat Ore like the other spendable resources and use the generic balanced-resource tie breaker.';
  }
  document.querySelectorAll('[data-optimizer-mode]').forEach(btn=>btn.addEventListener('click',()=>{
    const input=$('optimizerMode');
    if(!input) return;
    input.value=btn.dataset.optimizerMode==='balanced'?'balanced':'preserve';
    updateOptimizerModeUI();
    saveState();
    scheduleCalculatorUpdate(0);
  }));
'''
replace_once(mode_anchor, mode_code, 'optimizerMode runtime')

# Apply the late-S1 Ore bias only in Preserve Ore mode. There are intentionally two
# copies: feasible-route selection and the score-capable diagnostic/fallback route.
old_condition = "    if(candidate.seasonKey==='s1' || best.seasonKey==='s1'){"
condition_count = text.count(old_condition)
if condition_count != 2:
    raise SystemExit(f'optimizer condition: expected 2 matches, found {condition_count}')
text = text.replace(
    old_condition,
    "    if(optimizerMode()==='preserve' && (candidate.seasonKey==='s1' || best.seasonKey==='s1')){",
)

# Keep the visible optimizer summary honest about which policy is active.
old_summary = '''    return reserveKinds.length
      ? `Spend surplus first · minimize Ore · S2 ${reserveKinds.join(' + ')} reserve${reserveKinds.length>1?'s':''} protected`
      : 'Spend surplus first · minimize Ore · no S2 resource reserve';
'''
new_summary = '''    const policy=optimizerMode()==='preserve'?'minimize Ore':'balance spendable resources';
    return reserveKinds.length
      ? `Spend surplus first · ${policy} · S2 ${reserveKinds.join(' + ')} reserve${reserveKinds.length>1?'s':''} protected`
      : `Spend surplus first · ${policy} · no S2 resource reserve`;
'''
replace_once(old_summary, new_summary, 'optimizer summary policy')

# Re-render the segmented control after saved state/season state has been applied.
replace_once(
    '  function updateCalculator(){\n',
    '  function updateCalculator(){\n    updateOptimizerModeUI();\n',
    'updateCalculator mode render',
)

# Small, self-contained styling block so the control survives later layout patches.
head_close = '</head>'
style = '''<style id="optimizer-priority-toggle-v1">
/* OPTIMIZER_PRIORITY_TOGGLE_V1 */
.optimizerModeRow{display:flex;align-items:center;justify-content:space-between;gap:16px;border:1px solid var(--line);background:var(--ui-subpanel,var(--bg));border-radius:11px;margin:10px 0;padding:10px 12px}
.optimizerModeCopy{display:grid;gap:3px;min-width:0}.optimizerModeCopy b{color:var(--ink);font-size:10px}.optimizerModeCopy small{color:var(--muted);font-size:9px;line-height:1.4}
.optimizerModeToggle{display:grid;grid-template-columns:1fr 1fr;gap:3px;flex:0 0 auto;padding:3px;border:1px solid var(--line);background:var(--input-bg,var(--surface));border-radius:10px}
.optimizerModeToggle button{min-height:34px;border:0;border-radius:7px;padding:7px 11px;color:var(--muted);background:transparent;cursor:pointer;font-size:9px;font-weight:850;white-space:nowrap}
.optimizerModeToggle button:hover{color:var(--ink)}.optimizerModeToggle button.active,.optimizerModeToggle button[aria-pressed="true"]{background:var(--calc-accent-strong,var(--accent-strong));color:#fff}
@media(max-width:700px){.optimizerModeRow{align-items:stretch;flex-direction:column}.optimizerModeToggle{width:100%}.optimizerModeToggle button{white-space:normal;min-height:42px}}
</style>
'''
if text.count(head_close) != 1:
    raise SystemExit('Expected one </head> marker')
text = text.replace(head_close, style + head_close, 1)

PATH.write_text(text, encoding='utf-8')
print('Applied optimizer priority toggle patch.')
