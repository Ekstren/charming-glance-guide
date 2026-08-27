from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')
marker = 'RAW_BEFORE_REALM_TOOLS_V1'
if marker in text:
    print('Raw-before-Realm-tools optimizer policy already applied.')
    raise SystemExit(0)

old = r'''  function betterFeasibleCandidate(candidate,best){
    if(!best) return true;
    // Never spend more Dawnium just to force the preference. The policy only chooses
    // between routes that are equally cheap in paid Realm currency.
    if(candidate.dawniumCost<best.dawniumCost-1e-9) return true;
    if(Math.abs(candidate.dawniumCost-best.dawniumCost)>=1e-9) return false;

    // After paid-Realm cost is tied, compare modeled replacement effort. Preserve Ore uses
    // the same acquisition model with a bounded +50% Ore premium rather than an absolute veto.
    if(candidate.seasonKey==='s1' || best.seasonKey==='s1'){
      const cm=candidateResourceMetric(candidate),bm=candidateResourceMetric(best);
      if(cm<bm-1e-9) return true;
      if(cm>bm+1e-9) return false;
      if(optimizerMode()==='preserve'){
        if((candidate.bankedHammersUsed||0)<(best.bankedHammersUsed||0)) return true;
        if((candidate.bankedHammersUsed||0)>(best.bankedHammersUsed||0)) return false;
      }
    }

    if(candidate.realmPacks<best.realmPacks) return true;
    if(candidate.realmPacks!==best.realmPacks) return false;
    if((candidate.bankedToolsUsed||0)<(best.bankedToolsUsed||0)) return true;
    if((candidate.bankedToolsUsed||0)>(best.bankedToolsUsed||0)) return false;

    return candidate.overshoot<best.overshoot-1e-9||
      (Math.abs(candidate.overshoot-best.overshoot)<1e-9&&candidate.maxShare<best.maxShare-1e-9)||
      (Math.abs(candidate.overshoot-best.overshoot)<1e-9&&Math.abs(candidate.maxShare-best.maxShare)<1e-9&&candidate.sumShare<best.sumShare-1e-9);
  }

  function betterDiagnosticCandidate(candidate,best){
    if(!best) return true;
    if(candidate.hardShortfall<best.hardShortfall-0.5) return true;
    if(Math.abs(candidate.hardShortfall-best.hardShortfall)>0.5) return false;
    if(candidate.realmOverflow<best.realmOverflow) return true;
    if(candidate.realmOverflow!==best.realmOverflow) return false;
    if(candidate.remainingAfterMax<best.remainingAfterMax-0.5) return true;
    if(Math.abs(candidate.remainingAfterMax-best.remainingAfterMax)>0.5) return false;

    if(candidate.seasonKey==='s1' || best.seasonKey==='s1'){
      const cm=candidateResourceMetric(candidate),bm=candidateResourceMetric(best);
      if(cm<bm-1e-9) return true;
      if(cm>bm+1e-9) return false;
      if(optimizerMode()==='preserve'){
        if((candidate.bankedHammersUsed||0)<(best.bankedHammersUsed||0)) return true;
        if((candidate.bankedHammersUsed||0)>(best.bankedHammersUsed||0)) return false;
      }
    }

    if(candidate.realmPacks<best.realmPacks) return true;
    if(candidate.realmPacks!==best.realmPacks) return false;
    if((candidate.bankedToolsUsed||0)<(best.bankedToolsUsed||0)) return true;
    if((candidate.bankedToolsUsed||0)>(best.bankedToolsUsed||0)) return false;
    return candidate.overshoot<best.overshoot;
  }
'''

new = r'''  /* RAW_BEFORE_REALM_TOOLS_V1
     Upgrade selection is efficient WITHIN the cheapest Realm-tool tier, but raw materials
     that are safely spendable should be brute-forced before the planner consumes more Realm
     entries. Paid Realm purchases remain the strongest penalty; after that, fewer actual
     tool entries needed/consumed beats modeled reacquisition efficiency. This lets surplus
     Treats/Essence/Sand/Ore replace a tool-funded upgrade whenever the score math allows it. */
  function candidateRealmToolBurden(candidate){
    const realms=['ore','essence','sand'].map(k=>candidate?.realm?.[k]).filter(Boolean);
    return {
      paidRuns:realms.reduce((sum,x)=>sum+Math.max(0,Number(x?.paidRunsUsed)||0),0),
      totalRuns:realms.reduce((sum,x)=>sum+Math.max(0,Number(x?.runsNeeded)||0),0),
      bankedUsed:realms.reduce((sum,x)=>sum+Math.max(0,Number(x?.bankedUsed)||0),0)
    };
  }
  function betterToolBurden(candidate,best){
    const c=candidateRealmToolBurden(candidate),b=candidateRealmToolBurden(best);
    if(c.paidRuns<b.paidRuns) return true;
    if(c.paidRuns>b.paidRuns) return false;
    if(c.totalRuns<b.totalRuns) return true;
    if(c.totalRuns>b.totalRuns) return false;
    if(c.bankedUsed<b.bankedUsed) return true;
    if(c.bankedUsed>b.bankedUsed) return false;
    return null;
  }

  function betterFeasibleCandidate(candidate,best){
    if(!best) return true;
    // Buying more Realm refreshes is the last resort. Dawnium/unknown-price penalty wins first.
    if(candidate.dawniumCost<best.dawniumCost-1e-9) return true;
    if(Math.abs(candidate.dawniumCost-best.dawniumCost)>=1e-9) return false;

    // Inside the same purchase-cost tier, brute-force safely spendable raw resources before
    // consuming additional Realm entries. Only once tool burden is tied do we optimize the
    // long-run replacement-effort model.
    const toolCmp=betterToolBurden(candidate,best);
    if(toolCmp!==null) return toolCmp;

    if(candidate.seasonKey==='s1' || best.seasonKey==='s1'){
      const cm=candidateResourceMetric(candidate),bm=candidateResourceMetric(best);
      if(cm<bm-1e-9) return true;
      if(cm>bm+1e-9) return false;
      if(optimizerMode()==='preserve'){
        if((candidate.bankedHammersUsed||0)<(best.bankedHammersUsed||0)) return true;
        if((candidate.bankedHammersUsed||0)>(best.bankedHammersUsed||0)) return false;
      }
    }

    if(candidate.realmPacks<best.realmPacks) return true;
    if(candidate.realmPacks!==best.realmPacks) return false;

    return candidate.overshoot<best.overshoot-1e-9||
      (Math.abs(candidate.overshoot-best.overshoot)<1e-9&&candidate.maxShare<best.maxShare-1e-9)||
      (Math.abs(candidate.overshoot-best.overshoot)<1e-9&&Math.abs(candidate.maxShare-best.maxShare)<1e-9&&candidate.sumShare<best.sumShare-1e-9);
  }

  function betterDiagnosticCandidate(candidate,best){
    if(!best) return true;
    if(candidate.hardShortfall<best.hardShortfall-0.5) return true;
    if(Math.abs(candidate.hardShortfall-best.hardShortfall)>0.5) return false;
    if(candidate.realmOverflow<best.realmOverflow) return true;
    if(candidate.realmOverflow!==best.realmOverflow) return false;
    if(candidate.remainingAfterMax<best.remainingAfterMax-0.5) return true;
    if(Math.abs(candidate.remainingAfterMax-best.remainingAfterMax)>0.5) return false;

    const toolCmp=betterToolBurden(candidate,best);
    if(toolCmp!==null) return toolCmp;

    if(candidate.seasonKey==='s1' || best.seasonKey==='s1'){
      const cm=candidateResourceMetric(candidate),bm=candidateResourceMetric(best);
      if(cm<bm-1e-9) return true;
      if(cm>bm+1e-9) return false;
      if(optimizerMode()==='preserve'){
        if((candidate.bankedHammersUsed||0)<(best.bankedHammersUsed||0)) return true;
        if((candidate.bankedHammersUsed||0)>(best.bankedHammersUsed||0)) return false;
      }
    }

    if(candidate.realmPacks<best.realmPacks) return true;
    if(candidate.realmPacks!==best.realmPacks) return false;
    return candidate.overshoot<best.overshoot;
  }
'''

if text.count(old) != 1:
    raise SystemExit(f'Expected one optimizer comparator block, found {text.count(old)}')

text = text.replace(old, new, 1)
path.write_text(text, encoding='utf-8')
print('Applied raw-before-Realm-tools optimizer priority.')
