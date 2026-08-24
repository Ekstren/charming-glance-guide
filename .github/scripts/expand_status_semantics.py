from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
marker='/* GLOBAL_STATUS_SEMANTICS_V1 */'
if marker in s:
    raise SystemExit('global status semantics already applied')

old="if (state.theme === 'light' || state.theme === 'dark') document.documentElement.dataset.theme = state.theme;"
new="document.documentElement.dataset.theme = (state.theme === 'light' || state.theme === 'dark') ? state.theme : 'dark';"
if old not in s:
    raise SystemExit('theme restore anchor not found')
s=s.replace(old,new,1)

css=r'''

/* GLOBAL_STATUS_SEMANTICS_V1
   Keep rose for navigation/selection. Use semantic colors only where UI text means
   healthy/current, informational, caution, or failure/shortage. */

/* Timeline: active/current is positive, unconfirmed remains caution. */
.timelineNowInner{
  border-color:color-mix(in srgb,var(--status-positive) 42%,var(--line))!important;
  background:color-mix(in srgb,var(--status-positive) 6%,var(--surface))!important;
}
.dayGroup.activeEvent{
  border-color:color-mix(in srgb,var(--status-positive) 52%,var(--line))!important;
  box-shadow:inset 3px 0 0 var(--status-positive)!important;
}
.entry.entry-active{
  background:color-mix(in srgb,var(--status-positive) 7%,var(--surface-glass))!important;
}
.entry .activePill{
  background:color-mix(in srgb,var(--status-positive) 12%,transparent)!important;
  border-color:color-mix(in srgb,var(--status-positive) 38%,transparent)!important;
  color:var(--status-positive)!important;
}
.dayMarker b{color:var(--status-positive)!important}
.dayGroup.today{
  border-color:color-mix(in srgb,var(--status-positive) 44%,var(--line))!important;
  background:color-mix(in srgb,var(--status-positive) 6%,var(--surface))!important;
  box-shadow:0 14px 38px color-mix(in srgb,var(--status-positive) 10%,transparent)!important;
}
.dayGroup.today .dateBlock{
  background:var(--status-positive)!important;
  border-color:color-mix(in srgb,var(--status-positive) 62%,var(--line))!important;
  color:var(--surface)!important;
}
.dayGroup.today .dateBlock span,
.dayGroup.today .dateBlock small{color:var(--surface)!important}
.timelineWarning{border-left-color:var(--status-warning)!important}
.entry .unconfirmedPill{color:var(--status-warning)!important}

/* Calculator: recommended/success states are positive; projections are informational. */
.calcResults.success{
  border-color:color-mix(in srgb,var(--status-positive) 42%,var(--line))!important;
  background:linear-gradient(180deg,color-mix(in srgb,var(--status-positive) 7%,var(--surface)),var(--surface) 42%)!important;
}
.calcResults.success .calcEyebrow{color:var(--status-positive)!important}
.scoreBar i{background:linear-gradient(90deg,var(--status-info),var(--status-positive))!important}
.projectionCallout,
.projectionCallout.projectionInline{
  background:color-mix(in srgb,var(--status-info) 8%,var(--surface))!important;
  border-color:color-mix(in srgb,var(--status-info) 38%,var(--line))!important;
}
.projectionCallout span{color:var(--status-info)!important}
.seasonDeadline small{color:var(--status-info)!important}
.optimizedResult{
  background:color-mix(in srgb,var(--status-positive) 8%,var(--surface))!important;
  border:1px solid color-mix(in srgb,var(--status-positive) 30%,var(--line));
}
.optimizedResult span{color:var(--status-positive)!important}
.targetMessage.warning{color:var(--status-warning)!important}
.shortfallPlan{
  border-color:color-mix(in srgb,var(--status-warning) 45%,var(--line))!important;
  background:color-mix(in srgb,var(--status-warning) 8%,var(--surface))!important;
}
.materialRealmRecommendation.realmImpossible{
  border-color:color-mix(in srgb,var(--status-negative) 58%,var(--line))!important;
  background:color-mix(in srgb,var(--status-negative) 8%,var(--surface))!important;
}
.materialRealmRecommendation.realmImpossible b{color:var(--status-negative)!important}

/* Generic validation/status helpers used outside the resource cards. */
.inputGood,.statusGood,.isReady{color:var(--status-positive)!important}
.inputWarning,.statusWarning{color:var(--status-warning)!important}
.statusError,.notMet{color:var(--status-negative)!important}
'''

if '</style>' not in s:
    raise SystemExit('style closing tag not found')
s=s.replace('</style>',css+'\n</style>',1)

p.write_text(s,encoding='utf-8')
print('Expanded semantic status colors and enforced dark fallback theme.')
# trigger
