from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
marker='/* ROSE_PINE_PALETTE_V1 */'
if marker in s:
    raise SystemExit('Rosé Pine palette already present')

css=r'''

/* ROSE_PINE_PALETTE_V1
   Light: Rosé Pine Dawn inspired.
   Dark: Rosé Pine Moon inspired.
   Primary UI accent is rose; secondary accents are iris, foam, and gold. */
:root{
  --bg:#faf4ed;
  --surface:#fffaf3;
  --surface-glass:#fffaf3ef;
  --topbar:#faf4edf2;
  --ink:#575279;
  --body-text:#575279;
  --secondary-text:#797593;
  --muted:#9893a5;
  --line:#dfdad9;
  --green:#b4637a;
  --green-soft:#f6e8e8;
  --blue:#56949f;
  --gold:#ea9d34;
  --red:#b4637a;
  --purple:#907aa9;
  --filter-bg:#f2e9e1;
  --filter-text:#575279;
  --today-bg:#f7e9ea;
  --today-border:#d8b9c1;
  --footer:#f2e9e1;
  --accent-strong:#b4637a;
  --accent-deep:#9c5269;
  --input-bg:#f2e9e1;
  --soft-shadow:#57527918;
  --calc-accent-strong:#b4637a;
  --calc-accent-soft:#f7e9ea;
  --calc-accent-border:#d8b9c1;
  --ui-accent:#b4637a;
  --ui-accent-soft:#f7e9ea;
  --ui-accent-border:#d8b9c1;
  --ui-hover:#f6e8ee;
}
:root[data-theme=dark]{
  --bg:#232136;
  --surface:#2a273f;
  --surface-glass:#2a273fee;
  --topbar:#232136f2;
  --ink:#e0def4;
  --body-text:#e0def4;
  --secondary-text:#908caa;
  --muted:#6e6a86;
  --line:#44415a;
  --green:#eb6f92;
  --green-soft:#3a2f45;
  --blue:#9ccfd8;
  --gold:#f6c177;
  --red:#eb6f92;
  --purple:#c4a7e7;
  --filter-bg:#393552;
  --filter-text:#e0def4;
  --today-bg:#342d46;
  --today-border:#6b526f;
  --footer:#1f1d2e;
  --accent-strong:#b4638d;
  --accent-deep:#8f4f75;
  --input-bg:#393552;
  --soft-shadow:#00000035;
  --calc-accent-strong:#b4638d;
  --calc-accent-soft:#342d46;
  --calc-accent-border:#6b526f;
  --ui-accent:#b4638d;
  --ui-accent-soft:#342d46;
  --ui-accent-border:#6b526f;
  --ui-hover:#3b3150;
}

/* Primary interactions: rose, not green/teal. */
.logo{background:var(--accent-deep)!important}
.sectionSwitch button.active,.classTabs button.active,.filters button.active,
.buildRoleTabs button.active,.calcActions button,.gearLockButton.locked{
  background:var(--accent-strong)!important;
  border-color:var(--accent-strong)!important;
  color:#fffaf3!important;
  box-shadow:none!important;
}
.sectionSwitch button:hover,.classTabs button:hover,.filters button:hover,.buildRoleTabs button:hover{
  background:var(--ui-hover)!important;
  color:var(--green)!important;
  border-color:var(--ui-accent-border)!important;
}
.priorityList>li>b{background:var(--accent-strong)!important;color:#fffaf3!important}
.scoreBar i{background:linear-gradient(90deg,var(--accent-strong),var(--purple))!important}
.dayGroup.today .dateBlock{background:var(--accent-strong)!important;border-color:var(--ui-accent-border)!important;color:#fffaf3!important}
.dayGroup.today .dateBlock span,.dayGroup.today .dateBlock small{color:#fff1f5!important}
.todayButton{background:var(--accent-deep)!important;color:#fffaf3!important;box-shadow:0 10px 26px var(--soft-shadow)!important}
.todayButton:hover{background:var(--accent-strong)!important}

/* Inputs and nested calculator cards use Dawn/Moon overlays instead of beige/green washes. */
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
  box-shadow:0 0 0 3px color-mix(in srgb,var(--green) 15%,transparent)!important;
}
.calcGrid input:disabled,.resourceInputs input:disabled{background:var(--green-soft)!important;color:var(--green)!important}

.calcResults{background:var(--surface)!important;border-color:var(--ui-accent-border)!important;box-shadow:0 14px 34px var(--soft-shadow)!important}
.calcResults.success{background:var(--surface)!important}
.projectionCallout,.rolloverHold,.resourceGrace,.optimizedResult,.suggestedGear span,.timelineNowInner{
  background:var(--ui-accent-soft)!important;
  border-color:var(--ui-accent-border)!important;
}

/* Semantic badges stay varied so the page isn't monochrome. */
.category{color:var(--secondary-text)!important;background:var(--filter-bg)!important}
.category-event{color:var(--purple)!important;background:color-mix(in srgb,var(--purple) 13%,var(--surface))!important}
.category-dungeon{color:#d05b72!important;background:color-mix(in srgb,#d05b72 11%,var(--surface))!important}
.category-region{color:var(--blue)!important;background:color-mix(in srgb,var(--blue) 12%,var(--surface))!important}
.category-class-advancement{color:var(--purple)!important;background:color-mix(in srgb,var(--purple) 12%,var(--surface))!important}
.category-seasonal-map{color:var(--blue)!important;background:color-mix(in srgb,var(--blue) 12%,var(--surface))!important}
.category-ancient-relic{color:var(--gold)!important;background:color-mix(in srgb,var(--gold) 12%,var(--surface))!important}
.category-fantomon{color:#d7827e!important;background:color-mix(in srgb,#d7827e 11%,var(--surface))!important}
.category-companion{color:#56949f!important;background:color-mix(in srgb,#56949f 11%,var(--surface))!important}
.category-feature{color:var(--purple)!important;background:color-mix(in srgb,var(--purple) 10%,var(--surface))!important}
:root[data-theme=dark] .category-dungeon{color:#eb6f92!important}
:root[data-theme=dark] .category-fantomon{color:#ea9a97!important}
:root[data-theme=dark] .category-companion{color:#9ccfd8!important}

.entry .activePill{background:color-mix(in srgb,var(--green) 12%,transparent)!important;border-color:var(--ui-accent-border)!important;color:var(--green)!important}
.dayGroup.activeEvent{border-color:var(--ui-accent-border)!important;box-shadow:inset 3px 0 0 var(--green)!important}
.entry.entry-active{background:color-mix(in srgb,var(--green) 5%,var(--surface))!important}

/* Keep the hierarchy clean and reduce muddy shadows. */
.entry,.dateBlock,.timelineNowCard,.eventCycleCard,.futureSeasonGrid div,
.guideSummary,.buildCard,.priorityPanel,.gearPanel,.timelineIntel,.summary div,.sectionSwitch,.classTabs{
  box-shadow:none!important;
}
'''

if '</style>' not in s:
    raise SystemExit('style closing tag not found')
s=s.replace('</style>',css+'\n</style>',1)
p.write_text(s,encoding='utf-8')
print('Applied Rosé Pine Dawn/Moon palette override.')
# trigger
