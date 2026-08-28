#!/usr/bin/env python3
from pathlib import Path

PATH = Path("index.html")
text = PATH.read_text(encoding="utf-8")
MARKER = "S2_PRIMO_READY_V1"

if MARKER in text:
    print(f"{MARKER} already present; nothing to do.")
    raise SystemExit(0)

def replace_once(old: str, new: str, label: str):
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly 1 match, found {count}")
    text = text.replace(old, new, 1)

anchor = """  };
  // QY Maple Astral Pact thresholds. Primostars are cumulative across seasons; S2 continues after S1.
"""
insert = """  };

  /* S2_PRIMO_READY_V1
     Season 2 is prepared in parallel; Season 1 remains the active calculator until the
     existing season boundary switches activeCalcConfig() to S2.
     Cross-region S2 scoring references agree on:
       - Character/Gear/Skill/Fantomon floor: Lv.130
       - Relic scoring starts above +13
       - +45 fixed Primostars
       - 27 progression score per Primostar
       - Character 100 / Gear 18 / Skill 7 / Relic 33 / Fantomon 8 per level
     Global live UI should still be spot-checked at rollover before changing any constants. */
  const S2_PRIMO_META = Object.freeze({
    modelStatus:'cross-region-confirmed-global-spotcheck',
    scoreFloor:130,
    relicFloor:13,
    fixedStars:45,
    scorePerStar:27,
    weights:Object.freeze({character:100,gear:18,skill:7,relic:33,fanto:8}),
    commonTargets:Object.freeze([530,680,920]),
    milestones:Object.freeze([
      Object.freeze({level:106,label:'T4 class'}),
      Object.freeze({level:108,label:'Adult Fantomon'}),
      Object.freeze({level:116,label:'Tower'}),
      Object.freeze({level:120,label:'Max S2 Realm bracket'}),
      Object.freeze({level:130,label:'Season Power scoring / second dungeon'})
    ])
  });
  function validateS2PrimoModel(){
    const c=CALC_SEASONS.s2,m=S2_PRIMO_META,w=c.weights||{},mw=m.weights;
    const ok=c.scoreFloor===m.scoreFloor &&
      c.relicFloor===m.relicFloor &&
      c.starBase===m.fixedStars &&
      c.scorePerStar===m.scorePerStar &&
      w.character===mw.character && w.gear===mw.gear && w.skill===mw.skill &&
      w.relic===mw.relic && w.fanto===mw.fanto;
    if(!ok) console.warn('S2_PRIMO_READY_V1: Season 2 scoring constants drifted from the validated model.',{config:c,expected:m});
    return ok;
  }
  validateS2PrimoModel();

  // QY Maple Astral Pact thresholds. Primostars are cumulative across seasons; S2 continues after S1.
"""
replace_once(anchor, insert, "S2 metadata anchor")

old_target = """          <label>Target Primostars<input id="targetStars" type="number" value="200"></label>
          <label><span id="historicalStarsLabel">Historical stars</span><input id="historicalStars" type="number" value="0"></label>
"""
new_target = """          <label>Target Primostars<input id="targetStars" type="number" value="200"></label>
          <label><span id="historicalStarsLabel">Historical stars</span><input id="historicalStars" type="number" value="0"></label>
          <div class="s2TargetPresets" id="s2TargetPresets" hidden aria-label="Season 2 common planning targets"><span>S2 planning targets</span><div><button type="button" data-s2-target="530">530</button><button type="button" data-s2-target="680">680</button><button type="button" data-s2-target="920">920</button></div><small>Quick-fill only — your target can still be any value.</small></div>
"""
replace_once(old_target, new_target, "S2 target presets")

old_deadline = """        <div class="seasonDeadline"><span id="seasonDeadlineLabel">Season 1 ends</span><b id="seasonDeadlineDate">—</b><small id="seasonRemaining">—</small></div><div class="seasonRulesHint" id="seasonRulesHint" hidden></div>
"""
new_deadline = """        <div class="seasonDeadline"><span id="seasonDeadlineLabel">Season 1 ends</span><b id="seasonDeadlineDate">—</b><small id="seasonRemaining">—</small></div><div class="seasonRulesHint" id="seasonRulesHint" hidden></div>
        <div class="s2ProgressionGates" id="s2ProgressionGates" hidden aria-label="Season 2 progression gates"><span><b>106</b>T4</span><span><b>108</b>Adult Fanto</span><span><b>116</b>Tower</span><span><b>120</b>Realm max</span><span><b>130</b>Scoring + Dungeon</span></div>
"""
replace_once(old_deadline, new_deadline, "S2 progression gates")

css_anchor = """<style id="tool-only-resource-gaps-v4">"""
css_insert = """<style id="s2-primo-ready-v1-style">
/* S2 Primostar readiness controls. Hidden until the active calculator season is S2. */
.s2TargetPresets{grid-column:1/-1;border:1px solid var(--line);background:var(--filter-bg);border-radius:10px;padding:9px 10px;display:grid;grid-template-columns:auto 1fr auto;align-items:center;gap:8px 10px}
.s2TargetPresets[hidden],.s2ProgressionGates[hidden]{display:none!important}
.s2TargetPresets>span{color:var(--green);font-size:9px;font-weight:850;letter-spacing:.06em;text-transform:uppercase}
.s2TargetPresets>div{display:flex;gap:5px;flex-wrap:wrap}
.s2TargetPresets button{border:1px solid var(--line);background:var(--surface);color:var(--body-text);border-radius:8px;min-height:32px;padding:6px 9px;font-size:10px;font-weight:850;cursor:pointer}
.s2TargetPresets button:hover,.s2TargetPresets button.active{border-color:var(--green);color:var(--green);background:var(--green-soft)}
.s2TargetPresets small{color:var(--muted);font-size:8px;line-height:1.35;text-align:right}
.s2ProgressionGates{margin-top:8px;display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:6px}
.s2ProgressionGates span{border:1px solid var(--line);background:var(--filter-bg);color:var(--secondary-text);border-radius:9px;padding:7px 6px;text-align:center;font-size:8px;line-height:1.25;font-weight:750}
.s2ProgressionGates b{display:block;color:var(--green);font-size:12px;line-height:1.1;margin-bottom:2px}
@media(max-width:760px){.s2TargetPresets{grid-template-columns:1fr}.s2TargetPresets small{text-align:left}.s2ProgressionGates{grid-template-columns:repeat(3,minmax(0,1fr))}}
@media(max-width:520px){.s2ProgressionGates{grid-template-columns:repeat(2,minmax(0,1fr))}}
</style>
<style id="tool-only-resource-gaps-v4">"""
replace_once(css_anchor, css_insert, "S2 readiness CSS")

old_chrome = """    if($('astralBonusReference')) $('astralBonusReference').hidden=false;
    const setInputMax=(id,max)=>{const el=$(id);if(!el)return;if(Number.isFinite(max))el.max=String(max);else el.removeAttribute('max');};
    if(cfg.key==='s2'){
      $('seasonRulesHint').innerHTML='<b>Lv.120</b> = max S2 Material Realm/open-map resource bracket · <b>Lv.130</b> = Season Power scoring unlock/floor · late-S2 Skill/Relic planning stays conservative when an exact unlock gate is not verified.';
"""
new_chrome = """    if($('astralBonusReference')) $('astralBonusReference').hidden=false;
    const s2Presets=$('s2TargetPresets'),s2Gates=$('s2ProgressionGates'),seasonHint=$('seasonRulesHint');
    if(s2Presets) s2Presets.hidden=cfg.key!=='s2';
    if(s2Gates) s2Gates.hidden=cfg.key!=='s2';
    if(seasonHint) seasonHint.hidden=cfg.key!=='s2';
    if(s2Presets){
      const currentTarget=Math.floor(n('targetStars',cfg.key==='s2'?680:200));
      s2Presets.querySelectorAll('[data-s2-target]').forEach(btn=>btn.classList.toggle('active',Number(btn.dataset.s2Target)===currentTarget));
    }
    const setInputMax=(id,max)=>{const el=$(id);if(!el)return;if(Number.isFinite(max))el.max=String(max);else el.removeAttribute('max');};
    if(cfg.key==='s2'){
      $('seasonRulesHint').innerHTML='<b>S2 score:</b> +45 fixed · 27 score / Primostar · floor Lv.130 / Relics above +13 · weights Character 100, Gear 18, Skill 7, Relic 33, Fantomon 8. <b>Lv.120</b> is the max S2 Material Realm/open-map resource bracket. Late-S2 upgrade gates stay conservative where an exact unlock rule is not verified.';
"""
replace_once(old_chrome, new_chrome, "S2 season chrome")

old_confirm = """  function confirmCurrentSeasonSnapshot(){
    const cfg=activeCalcConfig();
    snapshotSeason=cfg.key; snapshotAtMs=Date.now(); snapshotCarry={ore:0,essence:0,sand:0,treat:0,exp:0}; snapshotStateLoaded=true;
"""
new_confirm = """  function confirmCurrentSeasonSnapshot(){
    const cfg=activeCalcConfig();
    // A persisted 200-ish S1 target is not useful in S2. Change it only at explicit rollover confirmation;
    // preserve any target the user already raised for S2.
    if(cfg.key==='s2' && $('targetStars')){
      const target=Number($('targetStars').value);
      if(!Number.isFinite(target) || target<=230) $('targetStars').value='680';
    }
    snapshotSeason=cfg.key; snapshotAtMs=Date.now(); snapshotCarry={ore:0,essence:0,sand:0,treat:0,exp:0}; snapshotStateLoaded=true;
"""
replace_once(old_confirm, new_confirm, "S2 rollover target default")

old_events = """    PANEL_OPEN_IDS.forEach(id=>$(id)?.addEventListener('toggle',saveState));
    $('confirmSeasonSnapshot')?.addEventListener('click',()=>{resetMaxAchievableUi();confirmCurrentSeasonSnapshot();});
    $('findMaxStars')?.addEventListener('click',findMaxAchievableStars);
"""
new_events = """    PANEL_OPEN_IDS.forEach(id=>$(id)?.addEventListener('toggle',saveState));
    $('s2TargetPresets')?.addEventListener('click',e=>{
      const btn=e.target.closest?.('[data-s2-target]');
      if(!btn || activeCalcConfig().key!=='s2') return;
      $('targetStars').value=btn.dataset.s2Target;
      resetMaxAchievableUi();
      markManualSnapshot('targetStars');
      saveState();
      scheduleCalculatorUpdate(0);
    });
    $('confirmSeasonSnapshot')?.addEventListener('click',()=>{resetMaxAchievableUi();confirmCurrentSeasonSnapshot();});
    $('findMaxStars')?.addEventListener('click',findMaxAchievableStars);
"""
replace_once(old_events, new_events, "S2 target event binding")

old_cap = """    const capText=cfg.key==='s1'?` S1 safe-upgrade cap uses projected Lv.${p.upgradeCapLevel??p.level}${$('grace12').checked?` at the 12h finishing cutoff (final Character projects Lv.${p.level})`:''}: Skills ${projectedCaps.skill}, Fantomons ${projectedCaps.fanto} (next 10-level band), Relics +${projectedCaps.relic}; Gear is not Character-level capped.`:` S2 scoring constants are the preloaded QY/community model pending live Global verification; max Realm bracket is Lv.120.`;
"""
new_cap = """    const capText=cfg.key==='s1'?` S1 safe-upgrade cap uses projected Lv.${p.upgradeCapLevel??p.level}${$('grace12').checked?` at the 12h finishing cutoff (final Character projects Lv.${p.level})`:''}: Skills ${projectedCaps.skill}, Fantomons ${projectedCaps.fanto} (next 10-level band), Relics +${projectedCaps.relic}; Gear is not Character-level capped.`:` S2 score model: floor Lv.130 / Relics above +13, +45 fixed Primostars, 27 score per Primostar, weights Character 100 / Gear 18 / Skill 7 / Relic 33 / Fantomon 8. Max Realm bracket is Lv.120; Global live values are still spot-checked at rollover before changing the model.`;
"""
replace_once(old_cap, new_cap, "S2 result formula text")

method_anchor = """<p><b>S2 resource breakpoints:</b> community/QY data separates two milestones that are easy to confuse."""
method_insert = """<p><b>S2 Primostar calculator readiness:</b> Season 2 is preloaded as a separate profile and does not replace Season 1. The scoring model uses the cross-region S2 consensus: normal progression scores only above Lv.130, Relics score above +13, the season contributes 45 fixed Primostars, and every 27 progression score adds one more Primostar after flooring. Per-level weights are Character 100, Gear 18, Skill 7, Fantomon 8 and Relic 33. The rollover guard still requires a fresh S2 account snapshot before calculations resume, so stale S1 levels/resources cannot silently contaminate the S2 plan. Exact Global cost/unlock data that is not independently confirmed remains conservative rather than fabricated.</p>
<p><b>S2 progression gates:</b> the prepared calculator surfaces Lv.106 T4 class, Lv.108 Adult Fantomon, Lv.116 Tower, Lv.120 maximum S2 Realm/open-map material bracket and Lv.130 Season Power scoring/second-dungeon milestone. These gates are informational; they do not override the calculator's conservative upgrade-cap logic.</p>
<p><b>S2 resource breakpoints:</b> community/QY data separates two milestones that are easy to confuse."""
replace_once(method_anchor, method_insert, "S2 method documentation")

required = [
    "s1:{key:'s1',name:'Season 1'",
    "s2:{key:'s2',name:'Season 2'",
    "const seasonKeyAt = (ms=Date.now()) => ms < S1_END.getTime() ? 's1' : 's2';",
    "scoreFloor:130,relicFloor:13,starBase:45,scorePerStar:27",
    "weights:{character:100,gear:18,skill:7,relic:33,fanto:8}",
    "S2_PRIMO_READY_V1",
]
for needle in required:
    if needle not in text:
        raise SystemExit(f"integrity check failed: missing {needle!r}")

if text.count(MARKER) != 2:
    raise SystemExit(f"expected 2 {MARKER} occurrences after patch, found {text.count(MARKER)}")

PATH.write_text(text, encoding="utf-8")
print("Prepared parallel Season 2 Primostar calculator without replacing Season 1.")
