from pathlib import Path

path = Path('assets/runtime.js')
text = path.read_text(encoding='utf-8')

marker = 'EXACT_LEVEL_AVERAGE_SYNC_V1'
if marker in text:
    print('Patch already applied.')
    raise SystemExit(0)

anchor = """  function categoryStateFromAverage(avg,count,minLevel,maxLevel,floor,weight){
"""
insert = r"""  /* EXACT_LEVEL_AVERAGE_SYNC_V1
     Exact slot entries are the authoritative current progression state whenever they are
     present and valid. Mirror their arithmetic mean back into the four compact Average fields
     so the summary above always agrees with the exact distribution being used by the planner.
     Any nonblank exact entry also locks the Exact slot levels panel open until all four fields
     are cleared, preventing active overrides from being hidden accidentally. */
  const EXACT_LEVEL_AVERAGE_BINDINGS = Object.freeze([
    Object.freeze({exactId:'exactSkillLevels',avgId:'skillLevel',count:8,min:100,capKey:'skill'}),
    Object.freeze({exactId:'exactRelicLevels',avgId:'relicLevel',count:20,min:10,capKey:'relic'}),
    Object.freeze({exactId:'exactFantoLevels',avgId:'fantomonLevel',count:4,min:100,capKey:'fanto'}),
    Object.freeze({exactId:'exactGearLevels',avgId:'gearLevel',count:5,min:100,capKey:'gear'})
  ]);
  function exactProgressionHasEntries(){
    return EXACT_LEVEL_AVERAGE_BINDINGS.some(({exactId})=>String($(exactId)?.value||'').trim().length>0);
  }
  function exactProgressionDetails(){ return document.querySelector('details.progressionExactInputs'); }
  function syncExactProgressionPanelLock(){
    const details=exactProgressionDetails();
    if(!details) return false;
    const locked=exactProgressionHasEntries();
    if(locked) details.open=true;
    details.dataset.exactLocked=locked?'true':'false';
    const hint=details.querySelector('summary small');
    if(hint) hint.textContent=locked?'Exact entries active · clear to collapse':'Optional · overrides averages';
    if(!details.dataset.exactLockBound){
      details.dataset.exactLockBound='1';
      const summary=details.querySelector(':scope > summary');
      summary?.addEventListener('click',event=>{
        if(exactProgressionHasEntries()){
          event.preventDefault();
          details.open=true;
        }
      });
      details.addEventListener('toggle',()=>{
        if(exactProgressionHasEntries()&&!details.open) details.open=true;
      });
    }
    return locked;
  }
  function syncAverageInputsFromExact(cfg=activeCalcConfig(),providedCaps=null){
    const characterLevel=Math.max(1,Math.floor(n('charLevel',cfg.key==='s2'?130:100)));
    const caps=providedCaps||categoryInputCapsForCharacter(characterLevel,cfg);
    for(const binding of EXACT_LEVEL_AVERAGE_BINDINGS){
      const max=Number(caps?.[binding.capKey]);
      const parsed=parseExactLevelInput(binding.exactId,binding.count,binding.min,Number.isFinite(max)?max:Infinity);
      if(!parsed.active||!parsed.valid) continue;
      const average=averageLevels(parsed.levels);
      const input=$(binding.avgId);
      if(input) input.value=formatAverage(average,3);
    }
  }
  function syncExactProgressionUi(cfg=activeCalcConfig(),providedCaps=null){
    syncExactProgressionPanelLock();
    syncAverageInputsFromExact(cfg,providedCaps);
  }
  document.addEventListener('input',event=>{
    if(!EXACT_LEVEL_AVERAGE_BINDINGS.some(({exactId})=>exactId===event.target?.id)) return;
    syncExactProgressionUi(activeCalcConfig());
  },true);

"""
if anchor not in text:
    raise SystemExit('Could not find categoryStateFromAverage anchor')
text = text.replace(anchor, insert + anchor, 1)

anchor2 = """    const currentCaps=categoryInputCapsForCharacter(currentCharacter.level,cfg);
    const projectedCaps=optimizerCategoryCaps(p,cfg);
"""
replace2 = """    const currentCaps=categoryInputCapsForCharacter(currentCharacter.level,cfg);
    // EXACT_LEVEL_AVERAGE_SYNC_V1: loaded/saved exact distributions also refresh the compact
    // averages and keep the exact editor visible before planner state is read.
    syncExactProgressionUi(cfg,currentCaps);
    const projectedCaps=optimizerCategoryCaps(p,cfg);
"""
if anchor2 not in text:
    raise SystemExit('Could not find currentCaps updateCalculator anchor')
text = text.replace(anchor2, replace2, 1)

path.write_text(text, encoding='utf-8')
print('Applied exact average sync + locked-open exact panel patch.')
