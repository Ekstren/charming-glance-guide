from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
marker='SHORTFALL_MESSAGING_V2'
if marker in s:
    print('already applied')
    raise SystemExit(0)

old="""    const line1=`${fmt(short)} short on daily plan${runsToCover?` · ${fmt(runsToCover)} ${itemName} to fully cover`:''}`;
    /* HARD_SHORT_STATUS_V1: a hard short is an unachievable/error state, not a warning.
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
new="""    /* SHORTFALL_MESSAGING_V2
       Hard shorts collapse to one red failure line; don't show a theoretical daily-plan
       bridge that cannot actually succeed. Recoverable shortages keep a concise red+yellow
       two-line pattern with the exact raw-material deficit. */
    if(hard>0){
      const hardLine=`${fmt(hard)} ${resourceName} hard short · Extra ${itemName} will not cover requirements`;
      el.innerHTML=`<span class=\"hardShort\">${hardLine}</span>${appendText?`<span>${appendText}</span>`:''}`;
      return;
    }
    const line1=`${fmt(short)} ${resourceName} short`;
    let line2='';
    if(extraRuns>0 && per>0){
      line2=`Extra ${itemName} can cover requirements`;
    }
    el.innerHTML=`<span class=\"planShort\">${line1}</span>${line2?`<span class=\"realmBridge\">${line2}</span>`:''}${appendText?`<span>${appendText}</span>`:''}`;
"""
if old not in s:
    raise SystemExit('Could not find current shortfall renderer block')
s=s.replace(old,new,1)

# Match the top caution banner to the concise recoverable wording while preserving
# the recommended refresh route and Apply button.
old_banner="""        $('targetMessage').innerHTML=`<span class=\"targetMessageCopy\">⚠ Goal is achievable, but your current Material Realm refresh plan is too low.${route}</span>${action}`;
"""
new_banner="""        const recoverableBits=[];
        if(orePlanShort>0.5 && oreHardShort<=0.5) recoverableBits.push(`${fmt(Math.ceil(orePlanShort))} Ore short · extra Hammers can cover`);
        if(essPlanShort>0.5 && essHardShort<=0.5) recoverableBits.push(`${fmt(Math.ceil(essPlanShort))} Essence short · extra Knuckles can cover`);
        if(sandPlanShort>0.5 && sandHardShort<=0.5) recoverableBits.push(`${fmt(Math.ceil(sandPlanShort))} Sand short · extra Shovels can cover`);
        const recoverableText=recoverableBits.length?` ${recoverableBits.join(' · ')}.`:' Goal is achievable with additional Material Realm refreshes.';
        $('targetMessage').innerHTML=`<span class=\"targetMessageCopy\">⚠${recoverableText}${route}</span>${action}`;
"""
if old_banner not in s:
    raise SystemExit('Could not find current achievable caution banner')
s=s.replace(old_banner,new_banner,1)

p.write_text(s,encoding='utf-8')
print('applied concise shortfall messaging v2')
