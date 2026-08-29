from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')
marker = 'RICH_RESOURCE_SHORTFALL_NO_DUPLICATE_V1'
if marker in s:
    print('already applied')
    raise SystemExit(0)

pat = re.compile(
    r"  /\* RESOURCE_SHORTFALL_CARD_CLEANUP_V1.*?\*/\n  function setRealmShortfallBreakdown\(id,planShort,yieldVal,itemName,maxExtraRuns,hardShort,resourceName='resource',appendText=''\)\{.*?\n  \}\n\n  function renderAstralPact",
    re.S,
)
rep = r'''  /* RICH_RESOURCE_SHORTFALL_NO_DUPLICATE_V1
     Keep the richer daily-plan / hard-cap presentation in the resource card itself.
     The separate Material Realm tool footer no longer repeats a "Still short" line. */
  function setRealmShortfallBreakdown(id,planShort,yieldVal,itemName,maxExtraRuns,hardShort,resourceName='resource',appendText=''){
    const el=$(id); if(!el) return;
    const short=Math.max(0,Math.ceil(Number(planShort)||0));
    const per=Math.max(0,Number(yieldVal)||0);
    const runsToCover=per>0?Math.ceil(short/per):0;
    const extraRuns=Math.max(0,Math.floor(Number(maxExtraRuns)||0));
    const usableExtra=Math.min(runsToCover,extraRuns);
    const extraResource=usableExtra*per;
    const hard=Math.max(0,Math.ceil(Number(hardShort)||0));
    el.classList.remove('shortfallCount','rawRemaining','reserveHasGap');
    el.classList.add('shortfallBreakdown');
    el.hidden=false;
    if(short<=0){
      el.textContent=`0 short${appendText}`;
      return;
    }
    const line1=`${fmt(short)} short on daily plan${runsToCover?` · ${fmt(runsToCover)} ${itemName} to fully cover`:''}`;
    let line2='';
    if(extraRuns>0 && per>0){
      line2=`${fmt(usableExtra)} extra ${itemName} still available = ${fmt(extraResource)} ${resourceName}${hard>0?` · ${fmt(hard)} hard short`:''}`;
    }else if(hard>0){
      line2=`${fmt(hard)} hard short · no extra ${itemName} capacity remains`;
    }
    el.innerHTML=`<span class="planShort">${line1}</span>${line2?`<span class="realmBridge">${line2}</span>`:''}${appendText?`<span>${appendText}</span>`:''}`;
  }

  function renderAstralPact'''

s2, n = pat.subn(rep, s, count=1)
if n != 1:
    raise SystemExit('Could not restore rich shortfall renderer')
s = s2

# Preserve the cleanup the user actually wanted: no duplicate tool-footer shortage.
if 'Still short:</i>' in s:
    raise SystemExit('Duplicate Still short footer unexpectedly present')
if "if(planRuns<=0){ el.innerHTML=''; el.hidden=true; return; }" not in s:
    raise SystemExit('Expected tool-footer hide guard is missing')

p.write_text(s, encoding='utf-8')
print('restored rich resource shortfall cards without duplicate footer')
