from pathlib import Path
import re

# Result UI
p=Path('index.html')
s=p.read_text()
anchor='''      <div class="resultScoreLine">\n        <span><small>Score</small><b id="currentScoreNow">—</b><i>→</i><b id="summaryOptimizedScore">—</b></span>\n        <span><small>Target</small><b id="desiredScore">—</b><em id="targetStatus">—</em></span>\n      </div>\n      <p class="targetMessage" id="targetMessage" hidden></p>'''
repl='''      <div class="resultScoreLine">\n        <span><small>Score</small><b id="currentScoreNow">—</b><i>→</i><b id="summaryOptimizedScore">—</b></span>\n        <span><small>Target</small><b id="desiredScore">—</b><em id="targetStatus">—</em></span>\n      </div>\n      <div class="targetTiming" id="targetTiming" title="Estimate based on current production inputs and the recommended target route.">\n        <span><small>Projected target</small><b id="targetReachedDate">—</b></span>\n        <span><small>Season left after target</small><b id="targetSeasonLeft">—</b></span>\n      </div>\n      <p class="targetMessage" id="targetMessage" hidden></p>'''
if 'id="targetTiming"' not in s:
    if anchor not in s: raise SystemExit('index target-score anchor missing')
    s=s.replace(anchor,repl,1)
    p.write_text(s)

# Styling
p=Path('assets/site.css')
s=p.read_text()
if 'TARGET_TIMING_V1' not in s:
    s += r'''

/* TARGET_TIMING_V1 · compact target ETA directly under Score / Target. */
.targetTiming{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;margin:10px 0 14px}
.targetTiming>span{min-width:0;border:1px solid var(--line);background:color-mix(in srgb,var(--surface) 78%,var(--green-soft));border-radius:12px;padding:10px 12px}
.targetTiming small{display:block;color:var(--muted);font-size:9px;font-weight:800;letter-spacing:.055em;text-transform:uppercase;margin-bottom:4px}
.targetTiming b{display:block;color:var(--ink);font-size:14px;line-height:1.25;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.targetTiming.isUnreachable>span{background:var(--surface)}
.targetTiming.isUnreachable b{color:var(--muted)}
@media (max-width:430px){.targetTiming{gap:6px}.targetTiming>span{padding:9px 10px}.targetTiming small{font-size:8px;letter-spacing:.035em}.targetTiming b{font-size:12px}}
'''
    p.write_text(s)

# Runtime: allow time-scoped resource projection and render a target ETA
# using the already-selected target route. No repeated optimizer calls are added.
p=Path('assets/runtime.js')
s=p.read_text()

old='''  function dailyShopMaterialEstimate(cfg=activeCalcConfig()){\n    const active=cfg.key==='s1'||cfg.key==='s2';\n    // SHOP_BUYOUTS_V1: input counts full shop pages purchased, not refresh presses.\n    // 0 = off; 1 = base page only; 2 = base page + one restock + second full-page buyout.\n    const buyouts=active?clamp(Math.floor(n('shopRefreshesDaily',0)),0,20):0;\n    const days=active?Math.max(0,futureRealmPurchaseDays(cfg)):0;'''
new='''  function dailyShopMaterialEstimate(cfg=activeCalcConfig(),daysOverride=null){\n    const active=cfg.key==='s1'||cfg.key==='s2';\n    // SHOP_BUYOUTS_V1: input counts full shop pages purchased, not refresh presses.\n    // 0 = off; 1 = base page only; 2 = base page + one restock + second full-page buyout.\n    const buyouts=active?clamp(Math.floor(n('shopRefreshesDaily',0)),0,20):0;\n    const days=active?Math.max(0,Number.isFinite(Number(daysOverride))?Math.floor(Number(daysOverride)):futureRealmPurchaseDays(cfg)):0;'''
if 'daysOverride=null' not in s:
    if old not in s: raise SystemExit('shop estimate anchor missing')
    s=s.replace(old,new,1)

pattern=re.compile(r'''  // Build the season-end resource snapshot BEFORE deciding what Stamina should gather\.\n  // The optimizer assigns the available 5-Stamina nodes to current-season score bottlenecks first, then banks all surplus nodes as Raw Ore\.\n  function projectedResources\(hours,cfg=activeCalcConfig\(\)\)\{.*?\n  \}\n\n  function applyStaminaAllocation''',re.S)
m=pattern.search(s)
if not m: raise SystemExit('projectedResources block missing')
replacement=r'''  // Build a resource snapshot up to an arbitrary point in the active season.
  // Season-end projection calls this with cfg.end; target ETA reuses it without rerunning the optimizer.
  function futureRealmPurchaseDaysUntil(targetMs,cfg=activeCalcConfig()){
    const now=Date.now();
    const cutoff=Math.max(now,Math.min(Number(targetMs)||cfg.end.getTime(),cfg.end.getTime()));
    return cutoff>now?countFuturePacificResets(now,cutoff):0;
  }
  function projectedResourcesTo(targetMs,cfg=activeCalcConfig()){
    const now=Date.now();
    const cutoff=Math.max(now,Math.min(Number(targetMs)||cfg.end.getTime(),cfg.end.getTime()));
    const fullRemaining=projectionResourceHoursAt(now,cfg);
    const afterCutoffRemaining=projectionResourceHoursAt(cutoff,cfg);
    const resourceHours=Math.max(0,fullRemaining-afterCutoffRemaining);
    const wallResourceHours=Math.max(0,(cutoff-now)/3_600_000);
    const boostResets=countFuturePacificResets(now,cutoff);
    const futureDays=futureRealmPurchaseDaysUntil(cutoff,cfg);
    const staminaStart=0;
    const yields=automaticResourceYields(n('charLevel',cfg.key==='s2'?100:122),cfg);
    const staminaGenerated=Math.max(0,Math.floor(resourceHours*5));
    const staminaSpendable=staminaStart+staminaGenerated;
    const staminaNodes=Math.floor(staminaSpendable/yields.staminaPerNode);
    const staminaUnused=staminaSpendable-staminaNodes*yields.staminaPerNode;
    const cartOre=Math.max(0,n('oreRate'))*resourceHours;
    const shopEstimate=dailyShopMaterialEstimate(cfg,futureDays);
    const refinedRaw=$('refinedOreCurrent')?.value?.trim?.() ?? '';
    const refinedTracked=refinedRaw!=='';
    const refined=refinedTracked?Math.max(0,Number(refinedRaw)||0):0;
    return {
      cartHours:resourceHours,wallResourceHours,boostResets,resourceCutoffMs:cutoff,realmDays:1+futureDays,
      staminaHours:resourceHours,staminaStart,staminaGenerated,staminaSpendable,staminaNodes,staminaUnused,
      yields,cartOre,shopEstimate,
      ore:Math.max(0,n('oreCurrent'))+cartOre+shopEstimate.total.ore,
      essence:Math.max(0,n('essenceCurrent'))+Math.max(0,n('essenceRate'))*resourceHours+shopEstimate.total.essence,
      sand:savedSandEquivalent()+Math.max(0,n('sandRate'))*resourceHours+shopEstimate.total.sand,
      treat:savedTreatEquivalent()+Math.max(0,n('treatRate'))*resourceHours+shopEstimate.total.treat,
      refinedTracked,refined,
      staminaAllocation:{ore:0,essence:0,sand:0,rolla:0,unassigned:staminaNodes},
      staminaAdded:{ore:0,essence:0,sand:0,rolla:0}
    };
  }
  function projectedResources(hours,cfg=activeCalcConfig()){
    return projectedResourcesTo(cfg.end.getTime(),cfg);
  }

  function applyStaminaAllocation'''
s=s[:m.start()]+replacement+s[m.end():]

timing_anchor="  function staminaAllocationSignature(a){ return ['ore','essence','sand','rolla','unassigned'].map(k=>Math.floor(a?.[k]||0)).join('/'); }\n"
timing_block=r'''

  /* TARGET_REACH_ETA_V1
     Estimate WHEN the already-selected goal route becomes executable. This deliberately does
     not rerun the expensive optimizer at every timestamp. Instead it binary-searches time using
     the recommended route's exact costs, current Character growth, Cart/shop production,
     Stamina, owned/planned Realm tools, and remaining Realm purchase capacity. */
  function targetMomentLabel(ms){
    return new Intl.DateTimeFormat(undefined,{month:'short',day:'numeric',hour:'numeric',minute:'2-digit'}).format(new Date(ms)).replace(' at ',' · ');
  }
  function compactDurationMs(ms){
    const mins=Math.max(0,Math.floor((Number(ms)||0)/60_000));
    const d=Math.floor(mins/1440),h=Math.floor((mins%1440)/60),m=mins%60;
    return d>0?`${d}d ${h}h`:h>0?`${h}h ${m}m`:`${m}m`;
  }
  function realmTopupForMoment(key,cost,resources,targetMs,pAt,cfg=activeCalcConfig()){
    const ids={ore:'hammerCurrent',essence:'knucklesCurrent',sand:'shovelCurrent'};
    const futureDays=futureRealmPurchaseDaysUntil(targetMs,cfg);
    const baseline=realmDailyValue(key);
    const manual=Math.max(0,Math.floor(n(ids[key],0)));
    const planned=futureDays*baseline*REALM_RUNS_PER_REFRESH;
    let perRun=realmYieldFor(resources,key);
    if(cfg.key==='s2' && Math.floor((pAt?.decimal??pAt?.level??n('charLevel',100)))<cfg.realmMaxLevel) perRun=0;
    return realmTopup(Math.max(0,Number(cost)||0),Math.max(0,Number(resources?.[key])||0),perRun,1+futureDays,manual+planned,baseline);
  }
  function fixedTargetRouteFundableAt(plan,requestedDesired,targetMs,pEnd,cfg=activeCalcConfig()){
    if(!plan) return false;
    const pAt=projectCharacterTo(targetMs,cfg);
    const nonCharacterScore=Math.max(0,(Number(plan.score)||0)-characterScore(pEnd,cfg));
    if(nonCharacterScore+characterScore(pAt,cfg)<requestedDesired-1e-9) return false;

    if(cfg.key==='s1'){
      const caps=categoryCapsForCharacter(pAt.level,cfg);
      if((plan.skillLevels||[]).some(x=>x>caps.skill)) return false;
      if((plan.relicLevels||[]).some(x=>x>caps.relic)) return false;
      if((plan.fantoLevels||[]).some(x=>x>caps.fanto)) return false;
    }

    const base=projectedResourcesTo(targetMs,cfg);
    const total=Math.max(0,Math.floor(base.staminaNodes||0));
    const empty={ore:0,essence:0,sand:0,rolla:0,unassigned:0};
    const map=base.yields?.map||{};
    const allocationCandidates=[];
    if(!base.yields?.mapReady || total<=0){
      allocationCandidates.push({...empty,unassigned:total});
    }else if(staminaMode()==='auto'){
      for(const key of ['ore','essence','sand']) if((Number(map[key])||0)>0) allocationCandidates.push({...empty,[key]:total});
    }else{
      const key=staminaMode();
      allocationCandidates.push((Number(map[key])||0)>0?{...empty,[key]:total}:{...empty,unassigned:total});
    }
    if(!allocationCandidates.length) allocationCandidates.push({...empty,unassigned:total});

    for(const allocation of allocationCandidates){
      const resources=applyStaminaAllocation(base,allocation,cfg);
      if((Number(plan.treatCost)||0)>(Number(resources.treat)||0)+0.5) continue;
      if(resources.refinedTracked && (Number(plan.refinedCost)||0)>(Number(resources.refined)||0)+0.5) continue;
      const ore=realmTopupForMoment('ore',plan.oreCost,resources,targetMs,pAt,cfg);
      const essence=realmTopupForMoment('essence',plan.essenceCost,resources,targetMs,pAt,cfg);
      const sand=realmTopupForMoment('sand',plan.sandCost,resources,targetMs,pAt,cfg);
      if(ore.feasible&&essence.feasible&&sand.feasible) return true;
    }
    return false;
  }
  function estimateTargetReachMoment(plan,resourceBlocked,requestedDesired,pEnd,cfg=activeCalcConfig()){
    if(!plan||resourceBlocked) return null;
    const now=Date.now(),end=cfg.end.getTime();
    if(end<=now) return null;
    if(fixedTargetRouteFundableAt(plan,requestedDesired,now,pEnd,cfg)) return now;
    if(!fixedTargetRouteFundableAt(plan,requestedDesired,end,pEnd,cfg)) return null;
    let lo=now,hi=end;
    for(let i=0;i<18 && hi-lo>60_000;i++){
      const mid=Math.floor((lo+hi)/2);
      if(fixedTargetRouteFundableAt(plan,requestedDesired,mid,pEnd,cfg)) hi=mid;
      else lo=mid+1;
    }
    return hi;
  }
  function renderTargetTiming(plan,resourceBlocked,requestedDesired,pEnd,cfg=activeCalcConfig()){
    const host=$('targetTiming'),dateEl=$('targetReachedDate'),leftEl=$('targetSeasonLeft');
    if(!host||!dateEl||!leftEl) return;
    const reached=estimateTargetReachMoment(plan,resourceBlocked,requestedDesired,pEnd,cfg);
    host.classList.toggle('isUnreachable',!Number.isFinite(reached));
    if(!Number.isFinite(reached)){
      dateEl.textContent='Not projected';
      leftEl.textContent='—';
      return;
    }
    const now=Date.now();
    dateEl.textContent=reached<=now+60_000?'Now':targetMomentLabel(reached);
    leftEl.textContent=compactDurationMs(Math.max(0,cfg.end.getTime()-reached));
  }
'''
if 'TARGET_REACH_ETA_V1' not in s:
    if timing_anchor not in s: raise SystemExit('timing insertion anchor missing')
    s=s.replace(timing_anchor,timing_anchor+timing_block,1)

render_anchor="    $('optimizedScore').textContent=resourceBlocked?`${fmt(plan.score)} / ${fmt(requestedDesired)} score · ${fmt(targetStars)} Primostars target plan`:`${fmt(plan.score)} / ${fmt(requestedDesired)} score · ${fmt(planStars)} Primostars · goal ${fmt(targetStars)} ✓`;\n"
if 'renderTargetTiming(plan,resourceBlocked,requestedDesired,p,cfg);' not in s:
    if render_anchor not in s: raise SystemExit('target render anchor missing')
    s=s.replace(render_anchor,render_anchor+"    renderTargetTiming(plan,resourceBlocked,requestedDesired,p,cfg);\n",1)
p.write_text(s)

# Browser smoke: keep the result strip present and populated into a valid state.
p=Path('scripts/site_smoke_test.mjs')
s=p.read_text()
smoke_anchor="assert(calcYieldMs < 5000, `calculator blocked the browser for ${calcYieldMs}ms`);\n"
smoke=r'''assert(calcYieldMs < 5000, `calculator blocked the browser for ${calcYieldMs}ms`);
const targetTiming=page.locator('#targetTiming');
assert(await targetTiming.count()===1, 'target timing strip missing');
const targetTimingState=await targetTiming.evaluate(el=>({text:el.innerText,overflow:Math.max(0,el.scrollWidth-el.clientWidth)}));
assert(/Projected target/i.test(targetTimingState.text) && /Season left after target/i.test(targetTimingState.text), `target timing labels missing: ${targetTimingState.text}`);
assert(targetTimingState.overflow<=1, `target timing strip overflows by ${targetTimingState.overflow}px`);
assert((await page.locator('#targetReachedDate').innerText()).trim().length>0, 'target timing date did not render');
'''
if 'target timing strip missing' not in s:
    if smoke_anchor not in s: raise SystemExit('site smoke calculator anchor missing')
    s=s.replace(smoke_anchor,smoke,1)
    p.write_text(s)
