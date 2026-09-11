from pathlib import Path

path = Path('assets/runtime.js')
s = path.read_text(encoding='utf-8')

old = '''  function clearS2ForRequiredPlannerInputs(cfg,requirements){
    const missing=[];
    if(!requirements.hasBed) missing.push('Bed EXP/hr');
    missing.push(...requirements.missingCart);
    if($('projectedCharacter')) $('projectedCharacter').value='Enter required inputs';
    if($('resultProjectedCharacter')) $('resultProjectedCharacter').textContent='—';
    ['currentStars','currentScoreNow','summaryOptimizedScore','desiredScore','optimizedScore'].forEach(id=>{if($(id))$(id).textContent='—';});
'''
new = '''  function clearS2ForRequiredPlannerInputs(cfg,requirements,p=null){
    const missing=[];
    if(!requirements.hasBed) missing.push('Bed EXP/hr');
    missing.push(...requirements.missingCart);
    // Character projection is lightweight and only needs Bed EXP; keep it available while
    // the material-production guard continues to block the expensive Primostar optimizer.
    if(requirements.hasBed && p){
      if($('seasonRemaining')) $('seasonRemaining').textContent=formatRemaining(p.hours);
      if($('projectedCharacter')) $('projectedCharacter').value=`Lv.${p.level} · ${(p.pct*100).toFixed(1)}%`;
      if($('resultProjectedCharacter')) $('resultProjectedCharacter').textContent=`Lv.${p.level} (${(p.pct*100).toFixed(1)}%)`;
    }else{
      if($('projectedCharacter')) $('projectedCharacter').value='Enter Bed EXP';
      if($('resultProjectedCharacter')) $('resultProjectedCharacter').textContent='—';
    }
    ['currentStars','currentScoreNow','summaryOptimizedScore','desiredScore','optimizedScore'].forEach(id=>{if($(id))$(id).textContent='—';});
'''
if s.count(old) != 1:
    raise SystemExit(f'Expected one clearS2ForRequiredPlannerInputs header, found {s.count(old)}')
s = s.replace(old, new, 1)

old2 = '''    if(cfg.key==='s2'){
      const required=s2RequiredPlannerInputs();
      if(!required.hasBed || !required.hasAllCart){ clearS2ForRequiredPlannerInputs(cfg,required); return; }
    }
    const p=projectCharacter(cfg);
'''
new2 = '''    let p=null;
    if(cfg.key==='s2'){
      const required=s2RequiredPlannerInputs();
      // Bed EXP is the only production input required for Character level projection.
      if(!required.hasBed){ clearS2ForRequiredPlannerInputs(cfg,required); return; }
      p=projectCharacter(cfg);
      // Do not run the full Primostar/material optimizer until every Cart rate exists.
      if(!required.hasAllCart){ clearS2ForRequiredPlannerInputs(cfg,required,p); return; }
    }
    if(!p) p=projectCharacter(cfg);
'''
if s.count(old2) != 1:
    raise SystemExit(f'Expected one calculator input guard, found {s.count(old2)}')
s = s.replace(old2, new2, 1)

path.write_text(s, encoding='utf-8')

check = path.read_text(encoding='utf-8')
assert "if(!required.hasBed){ clearS2ForRequiredPlannerInputs(cfg,required); return; }" in check
assert "if(!required.hasAllCart){ clearS2ForRequiredPlannerInputs(cfg,required,p); return; }" in check
assert "$('projectedCharacter').value=`Lv.${p.level} · ${(p.pct*100).toFixed(1)}%`" in check
print('Bed-only Character projection patch applied.')
