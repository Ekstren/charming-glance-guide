from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')
marker = 'HARD_SHORT_STATUS_V1'
if marker in s:
    print('already applied')
    raise SystemExit(0)

old = """    let line2='';
    if(extraRuns>0 && per>0){
      line2=`${fmt(usableExtra)} extra ${itemName} still available = ${fmt(extraResource)} ${resourceName}${hard>0?` · ${fmt(hard)} hard short`:''}`;
    }else if(hard>0){
      line2=`${fmt(hard)} hard short · no extra ${itemName} capacity remains`;
    }
    el.innerHTML=`<span class=\"planShort\">${line1}</span>${line2?`<span class=\"realmBridge\">${line2}</span>`:''}${appendText?`<span>${appendText}</span>`:''}`;
"""
new = """    /* HARD_SHORT_STATUS_V1: a hard short is an unachievable/error state, not a warning.
       Keep the exact raw-material deficit visible and explain that remaining Realm-tool
       capacity cannot close it. Recoverable Realm bridges stay yellow. */
    let line2='';
    let line2Class='realmBridge';
    if(hard>0){
      line2=`${fmt(hard)} ${resourceName} hard short · Extra ${itemName} will not cover requirements`;
      line2Class='hardShort';
    }else if(extraRuns>0 && per>0){
      line2=`${fmt(usableExtra)} extra ${itemName} still available = ${fmt(extraResource)} ${resourceName}`;
    }
    el.innerHTML=`<span class=\"planShort\">${line1}</span>${line2?`<span class=\"${line2Class}\">${line2}</span>`:''}${appendText?`<span>${appendText}</span>`:''}`;
"""
if old not in s:
    raise SystemExit('Could not find rich resource shortfall line2 renderer')
s = s.replace(old, new, 1)

p.write_text(s, encoding='utf-8')
print('applied hard short status presentation')
