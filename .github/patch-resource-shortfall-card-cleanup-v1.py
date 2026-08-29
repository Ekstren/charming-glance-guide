from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')
marker = 'RESOURCE_SHORTFALL_CARD_CLEANUP_V1'
if marker in s:
    print('already applied')
    raise SystemExit(0)

# Replace the verbose two-box daily/hard shortfall renderer with one concise status line.
pat = re.compile(r"  function setRealmShortfallBreakdown\(id,planShort,yieldVal,itemName,maxExtraRuns,hardShort,resourceName='resource',appendText=''\)\{.*?\n  \}\n\n  function renderAstralPact", re.S)
rep = r'''  /* RESOURCE_SHORTFALL_CARD_CLEANUP_V1
     Resource cards use one shortage status instead of repeating daily-plan, hard-cap,
     and tool-footer warnings. Detailed Realm capacity remains in the Material Realm panel. */
  function setRealmShortfallBreakdown(id,planShort,yieldVal,itemName,maxExtraRuns,hardShort,resourceName='resource',appendText=''){
    const el=$(id); if(!el) return;
    const short=Math.max(0,Math.ceil(Number(planShort)||0));
    const per=Math.max(0,Number(yieldVal)||0);
    const runsToCover=per>0?Math.ceil(short/per):0;
    const extraRuns=Math.max(0,Math.floor(Number(maxExtraRuns)||0));
    const hard=Math.max(0,Math.ceil(Number(hardShort)||0));
    el.classList.remove('shortfallBreakdown','rawRemaining','reserveHasGap');
    el.classList.add('shortfallCount');
    el.hidden=false;
    if(short<=0){ el.textContent=''; el.hidden=true; return; }
    let suffix='';
    if(hard>0) suffix=' · hard cap';
    else if(runsToCover>0 && extraRuns>=runsToCover) suffix=` · ${fmt(runsToCover)} ${itemName} can cover`;
    else if(extraRuns>0) suffix=` · ${fmt(extraRuns)} extra ${itemName} available`;
    el.textContent=`${fmt(short)} short${suffix}${appendText||''}`;
  }

  function renderAstralPact'''
s2, n = pat.subn(rep, s, count=1)
if n != 1:
    raise SystemExit('Could not replace setRealmShortfallBreakdown')
s = s2

# Tool rows should explain actual tool use only. The resource balance above owns shortage status.
s = s.replace(
    "    if(planRuns<=0 && missing<=0){ el.innerHTML=''; el.hidden=true; return; }",
    "    if(planRuns<=0){ el.innerHTML=''; el.hidden=true; return; }",
    1,
)

old = """    if(missing>0){
      const rawStillShort=Math.max(0,Math.ceil(Number(hardShort)||0));
      lines.push(`<div class=\"toolSimpleLine toolNeedLine\"><i>Still short:</i><b>${fmt(rawStillShort)} ${materialName}</b></div>`);
    }
"""
if old not in s:
    raise SystemExit('Could not find duplicate Still short tool footer')
s = s.replace(old, '', 1)

p.write_text(s, encoding='utf-8')
print('applied resource shortfall card cleanup')
