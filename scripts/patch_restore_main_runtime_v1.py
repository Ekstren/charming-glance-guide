from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')
MARK = 'MAIN_RUNTIME_REPAIR_V1'

if MARK in s:
    print('main runtime already repaired')
    raise SystemExit(0)

start = s.find("    CHECK_IDS.forEach(id=>$(id)?.addEventListener('change',()=>{")
end_marker = '<!-- BUILD_ROLE_TOGGLE_END -->'
end = s.find(end_marker, start)
if start < 0 or end < 0:
    raise SystemExit(f'anchors not found: start={start} end={end}')
end += len(end_marker)

replacement = r'''    /* MAIN_RUNTIME_REPAIR_V1
       Restore the calculator setup tail and startup sequence. A build-role patch had
       accidentally replaced this block, preventing navigation/timeline initialization. */
    CHECK_IDS.forEach(id=>$(id)?.addEventListener('change',()=>{
      resetMaxAchievableUi();
      markManualSnapshot(id);
      saveState();
      if(calculatorInitialized) scheduleCalculatorUpdate(0);
      else initializeCalculatorIfNeeded();
    }));
    PANEL_OPEN_IDS.forEach(id=>$(id)?.addEventListener('toggle',saveState));
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
    $('targetMessage')?.addEventListener('click',e=>{
      const btn=e.target.closest?.('.applyRealmRecommendation');
      if(btn) applyRecommendedRealmRefreshes(btn);
    });
    $('copyPlan')?.addEventListener('click',copyPlan);
    $('resetCalc')?.addEventListener('click',()=>{resetMaxAchievableUi();resetCalculator();});
    setInterval(()=>{
      if(!calculatorInitialized) return;
      rollSnapshotForward(Date.now(),true);
      if(!document.getElementById('calculatorSection')?.hidden) scheduleCalculatorUpdate(0);
    },60_000);
  }

  loadState();
  setupNavigation();
  let initialSection='timeline';
  try{
    const savedSection=localStorage.getItem(SECTION_STORAGE_KEY);
    if(['timeline','builds','companions','calculator'].includes(savedSection)) initialSection=savedSection;
  }catch(_){}
  setSection(initialSection);
  setupTimeline();
  setupBuilds();
  setupCalculator();
})();

</script>'''

s = s[:start] + replacement + s[end:]

# Guard against the specific corruption signature that killed the site.
for bad in [
    "const role=(card.dataset.role||'').toLowerCase();\n      const alwaysVisible=role==='arena'||role==='tournament';",
    "<!-- BUILD_ROLE_TOGGLE_END -->",
]:
    if bad in s[s.find('function setupCalculator()'):s.find('<!-- COMPANION_GUIDE_SCRIPT_START -->')]:
        raise SystemExit(f'corrupt setupCalculator fragment still present: {bad[:40]}')

# Required startup calls must be back in the primary runtime before the companion script.
head = s[:s.find('<!-- COMPANION_GUIDE_SCRIPT_START -->')]
for required in ['loadState();','setupNavigation();','setupTimeline();','setupBuilds();','setupCalculator();']:
    if required not in head:
        raise SystemExit(f'missing runtime startup call: {required}')

p.write_text(s, encoding='utf-8')
print('restored main runtime initialization')
