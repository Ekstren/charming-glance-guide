import baseline from '../data/affix-preview-baseline.json';

// The screenshot transcription is the single source of truth for displayed ranges.
const R=Object.fromEntries(baseline.affixes.filter(row=>row.kind==='normal'||row.kind==='paired').map(row=>[row.id,row]));
  const PROFILES={
    Conqueror:['crit','critdmg','critpair','acc','critacc','em','spd','spdpct','atk','atkpct'],
    Guardian:{
      tank:['block','blockpair','def','spd','hp','defpct','spdpct','hppct'],
      dps:['block','blockpair','crit','critdmg','spd','spdpct','atk','atkpct','em']
    },
    Destroyer:['crit','critdmg','critpair','atk','atkpct','em','acc','critacc','spd','spdpct'],
    Dominator:{
      dps:['ehr','crit','critdmg','critpair','em','atk','atkpct','spd','spdpct'],
      heals:['heal','healpair','spd','spdpct','hp','hppct']
    }
  };
  const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const activeClass=()=>document.querySelector('#classTabs button.active')?.dataset.class||'Conqueror';
  const role=cls=>{try{if(cls==='Guardian')return localStorage.getItem('sxs-build-guardian-mode')==='dps'?'dps':'tank';return localStorage.getItem('sxs-build-dominator-mode')==='heals'?'heals':'dps'}catch(_){return cls==='Guardian'?'tank':'dps'}};

const rowsFor=(cls,mode)=>{
  const profile=PROFILES[cls];
  const keys=Array.isArray(profile)?profile:profile?.[mode];
  return (keys||PROFILES.Conqueror).map(key=>R[key]);
};
const displayName=row=>row.name+(row.id.endsWith('pct')?'%':'');
const help=row=>{
  const detail=`${row.kind==='paired'?'Paired':'Normal'} affix · ${row.drop_rate_percent.toFixed(3)}% drop rate. ${row.components.map(part=>`${part.stat}: ${part.range}`).join('; ')}.`;
  return `<button type="button" class="rollHelp" aria-label="${esc(displayName(row))}: affix details" data-tip="${esc(detail)}">i</button>`;
};
const guideHtml=(cls,mode)=>{
  const rows=rowsFor(cls,mode);
  const label=cls==='Dominator'?`${cls} · ${mode==='heals'?'Heals':'DPS'}`:cls==='Guardian'?`${cls} · ${mode==='dps'?'DPS':'Tank'}`:cls;
  return `<details class="rollGuide" data-roll-sig="${esc(cls+'|'+mode)}"><summary><span>Affix ranges</span><small>${esc(label)} · Current baseline</small></summary><div class="rollGuideBody"><div class="rollGuideNote">In-game minimum–maximum ranges for the recommended affixes. Paired values follow the listed stat order.</div>${['normal','paired'].map(kind=>`<div class="rollGuideNote">${kind==='normal'?'Normal affixes':'Paired affixes · both stats roll together'}</div><div class="rollGuideGrid">${rows.filter(row=>row.kind===kind).map(row=>`<div class="rollGuideRow" data-affix-id="${esc(row.id)}"><span class="rollGuideName">${esc(displayName(row))}${help(row)}</span><span class="rollGuideValue">${row.components.map(part=>esc(part.range)).join('<br>')}</span></div>`).join('')}</div>`).join('')}<div class="rollGuideSources">Confirmed in the in-game Affix Preview. Normal and paired affixes have different ranges; use the matching row. Flat values can change with gear progression.</div></div></details>`;
};
  function apply(){
    const cls=activeClass(),mode=(cls==='Dominator'||cls==='Guardian')?role(cls):'dps',sig=cls+'|'+mode;
    document.querySelectorAll('#buildContent .buildQuickStats').forEach(quick=>{
      const existing=quick.querySelector(':scope > .rollGuide');
      if(existing?.dataset.rollSig===sig) return;
      const html=guideHtml(cls,mode);
      if(existing) existing.outerHTML=html;
      else quick.querySelector(':scope > .quickSubstats')?.insertAdjacentHTML('afterend',html);
    });
  }
  // BUILD_VISUAL_STABILITY_V2: Roll Guide is part of the finished class layout,
  // so make it available to the synchronous Builds render pipeline.
  window.__applyBuildRollNow=apply;

