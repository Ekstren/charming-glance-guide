from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
marker='/* EYE_COMFORT_PALETTE_V1 */'
if marker in s:
    raise SystemExit('Eye comfort palette already present')

css=r'''

/* EYE_COMFORT_PALETTE_V1
   Light: Gruvbox Material Light Soft inspired.
   Dark: Everforest Medium inspired.
   Intent: warm, moderate contrast, no pure-white/pure-black glare, one coherent UI accent family. */
:root{
  --bg:#f2e5bc;
  --surface:#fbf1c7;
  --surface-glass:#fbf1c7ec;
  --topbar:#f2e5bcf2;
  --ink:#3c3836;
  --body-text:#504945;
  --secondary-text:#665c54;
  --muted:#7c6f64;
  --line:#c9b99a;
  --green:#6c782e;
  --green-soft:#e4e2bf;
  --blue:#45707a;
  --gold:#b47109;
  --red:#c14a4a;
  --purple:#945e80;
  --filter-bg:#ebdbb2;
  --filter-text:#504945;
  --today-bg:#e5e2bf;
  --today-border:#a9ad74;
  --footer:#ebdbb2;
  --accent-strong:#596624;
  --accent-deep:#48541e;
  --input-bg:#ebdbb2;
  --soft-shadow:#3c38361a;
  --calc-accent-strong:var(--accent-strong);
  --calc-accent-soft:color-mix(in srgb,var(--green) 8%,var(--surface));
  --calc-accent-border:color-mix(in srgb,var(--green) 34%,var(--line));
}
:root[data-theme=dark]{
  --bg:#232a2e;
  --surface:#2d353b;
  --surface-glass:#2d353bec;
  --topbar:#232a2ef2;
  --ink:#d3c6aa;
  --body-text:#c8bca2;
  --secondary-text:#9da9a0;
  --muted:#859289;
  --line:#475258;
  --green:#a7c080;
  --green-soft:#35443b;
  --blue:#7fbbb3;
  --gold:#dbbc7f;
  --red:#e67e80;
  --purple:#d699b6;
  --filter-bg:#343f44;
  --filter-text:#c1cbbd;
  --today-bg:#35443b;
  --today-border:#61725e;
  --footer:#1f262a;
  --accent-strong:#4f654f;
  --accent-deep:#3e5444;
  --input-bg:#263035;
  --soft-shadow:#0000002b;
  --calc-accent-strong:var(--accent-strong);
  --calc-accent-soft:color-mix(in srgb,var(--green) 8%,var(--surface));
  --calc-accent-border:color-mix(in srgb,var(--green) 30%,var(--line));
}

/* Fix the parts that were still carrying legacy teal/blue styling. */
.logo{background:var(--accent-deep)!important}
.headerMeta span{color:var(--muted)!important}
.sectionSwitch button.active,.classTabs button.active,.filters button.active,
.buildRoleTabs button.active,.calcActions button,.gearLockButton.locked{
  background:var(--accent-strong)!important;
  border-color:var(--accent-strong)!important;
  color:#fffdf5!important;
  box-shadow:none!important;
}
.sectionSwitch button:hover,.classTabs button:hover,.filters button:hover,.buildRoleTabs button:hover{
  background:color-mix(in srgb,var(--green) 10%,var(--surface))!important;
  color:var(--green)!important;
  border-color:var(--calc-accent-border)!important;
}
.priorityList>li>b{background:var(--accent-strong)!important;color:#fffdf5!important}
.scoreBar i{background:linear-gradient(90deg,var(--accent-strong),var(--green))!important}
.dayGroup.today .dateBlock{background:var(--accent-strong)!important;border-color:var(--calc-accent-border)!important;color:#fffdf5!important}
.dayGroup.today .dateBlock span,.dayGroup.today .dateBlock small{color:#f5edcf!important}
.todayButton{background:var(--accent-deep)!important;color:#fffdf5!important;box-shadow:0 10px 26px var(--soft-shadow)!important}
.todayButton:hover{background:var(--accent-strong)!important}
.dateBlock small{color:var(--muted)!important}

/* Form hierarchy: panel -> subpanel -> input, with a visible but gentle step each time. */
.calcGrid input,.calcGrid select,.resourceInputs input,.rolloverHold input[type=number],
.resourceCardFields input,.realmInventoryGrid input,.realmDailyInputs input,
.exactInputsBody input,.accuracyGrid input,.staminaInput input,.staminaSimple select,
input[type=number]:not([disabled]),input[type=text]:not([disabled]),select,textarea{
  background:var(--input-bg)!important;
  color:var(--ink)!important;
  border-color:var(--line)!important;
}
.calcGrid input:focus,.calcGrid select:focus,.resourceInputs input:focus,
.resourceCardFields input:focus,.realmInventoryGrid input:focus,.realmDailyInputs input:focus,
.exactInputsBody input:focus,.accuracyGrid input:focus,.staminaInput input:focus,.staminaSimple select:focus{
  border-color:var(--green)!important;
  box-shadow:0 0 0 3px color-mix(in srgb,var(--green) 16%,transparent)!important;
}
.calcGrid input:disabled,.resourceInputs input:disabled{background:var(--green-soft)!important;color:var(--green)!important}

/* Calculator/result surfaces: remove the leftover aqua wash from the prior palette. */
.calcPanel,.calcResults,.methodPanel,.resourceCard,.realmInventory,.staminaSimple,
.accuracyInputs,.exactInputs,.realmPlanSummary,.seasonDeadline,.resultScoreLine,
.optimizerTargets span,.planCosts span,.resourceInputs>div{
  border-color:var(--line)!important;
}
.calcResults{background:var(--surface)!important;border-color:var(--calc-accent-border)!important;box-shadow:0 14px 34px var(--soft-shadow)!important}
.calcResults.success{background:var(--surface)!important}
.projectionCallout,.rolloverHold,.resourceGrace,.optimizedResult,.suggestedGear span{
  background:var(--calc-accent-soft)!important;
  border-color:var(--calc-accent-border)!important;
}
.timelineNowInner{background:var(--calc-accent-soft)!important;border-color:var(--calc-accent-border)!important}

/* Semantic colors stay distinct, but all badges now share the same soft surface treatment. */
.category{color:var(--secondary-text)!important;background:var(--filter-bg)!important}
.category-event{color:var(--purple)!important;background:color-mix(in srgb,var(--purple) 13%,var(--surface))!important}
.category-dungeon{color:var(--red)!important;background:color-mix(in srgb,var(--red) 12%,var(--surface))!important}
.category-region{color:var(--green)!important;background:color-mix(in srgb,var(--green) 12%,var(--surface))!important}
.category-class-advancement{color:var(--purple)!important;background:color-mix(in srgb,var(--purple) 11%,var(--surface))!important}
.category-seasonal-map{color:var(--blue)!important;background:color-mix(in srgb,var(--blue) 12%,var(--surface))!important}
.category-ancient-relic{color:var(--gold)!important;background:color-mix(in srgb,var(--gold) 12%,var(--surface))!important}
.category-fantomon{color:var(--gold)!important;background:color-mix(in srgb,var(--gold) 10%,var(--surface))!important}
.category-companion{color:var(--green)!important;background:color-mix(in srgb,var(--green) 10%,var(--surface))!important}
.category-feature{color:var(--blue)!important;background:color-mix(in srgb,var(--blue) 10%,var(--surface))!important}

.dayGroup.activeEvent{border-color:var(--calc-accent-border)!important;box-shadow:inset 3px 0 0 var(--green)!important}
.entry.entry-active{background:color-mix(in srgb,var(--green) 5%,var(--surface))!important}
.entry .activePill{background:color-mix(in srgb,var(--green) 11%,transparent)!important;border-color:var(--calc-accent-border)!important;color:var(--green)!important}
.entry,.dateBlock,.timelineNowCard,.eventCycleCard,.futureSeasonGrid div,
.guideSummary,.buildCard,.priorityPanel,.gearPanel,.timelineIntel,.summary div,.sectionSwitch,.classTabs{
  box-shadow:none;
}
'''

if '</style>' not in s:
    raise SystemExit('style closing tag not found')
s=s.replace('</style>',css+'\n</style>',1)
p.write_text(s,encoding='utf-8')
print('Applied researched eye-comfort light/dark palette and normalized legacy colors.')
# trigger
