from pathlib import Path

INDEX = Path('index.html')
INJECT = Path('.github/build-fantomons-inject.html')
MARK = 'RESTORE_RICH_BUILDS_V1'
START = '<!-- BUILD_FANTOMON_PAIRS_START -->'
END = '<!-- BUILD_FANTOMON_PAIRS_END -->'

s = INDEX.read_text(encoding='utf-8')
if MARK in s:
    print('rich Builds already restored')
    raise SystemExit(0)

inject = INJECT.read_text(encoding='utf-8')
required = [
    START, END,
    'BUILD_ARENA_TOURNAMENT_SPLIT_V1',
    "role('Arena'",
    "role('Tournament'",
    'fantomonPair',
]
for token in required:
    if token not in inject:
        raise SystemExit(f'historical Builds inject missing expected token: {token}')

# Remove any older/incomplete Fantomon/loadout injection before installing the known-good one.
if START in s:
    a = s.index(START)
    b = s.find(END, a)
    if b < 0:
        raise SystemExit('found Builds injection start without end marker')
    b += len(END)
    s = s[:a] + s[b:]

rich = r'''
<style id="restore-rich-builds-v1">
/* RESTORE_RICH_BUILDS_V1
   Restores the compact per-slot stat panel and the side-by-side investment layout
   from the maintained Aug 29 Builds UI. */
#buildContent>.gearPanel{display:none!important}
.guideSummary.buildSummaryCompact{grid-template-columns:minmax(0,.82fr) minmax(0,1.18fr);align-items:stretch}
.buildQuickStats{border-left:1px solid var(--line);padding-left:20px;display:flex;flex-direction:column;justify-content:center;gap:8px;min-width:0}
.buildQuickStats .quickTitle{color:var(--ink);letter-spacing:.08em;text-transform:uppercase;font-size:9px;font-weight:900}
.buildQuickStats .quickRule{color:var(--muted);font-size:10px;line-height:1.45;margin:0}
.quickGearGrid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:6px 16px}
.quickGearRow{display:grid;grid-template-columns:max-content 1fr;gap:8px;align-items:baseline;border-top:1px solid color-mix(in srgb,var(--line) 72%,transparent);padding-top:6px;min-width:0}
.quickGearRow b{color:var(--green);font-size:9px;white-space:nowrap}
.quickGearRow span{color:var(--body-text);font-size:9px;line-height:1.35;text-transform:none;letter-spacing:0;font-weight:650;min-width:0}
.quickSubstats{border-top:1px solid color-mix(in srgb,var(--line) 72%,transparent);padding-top:7px;display:grid;grid-template-columns:max-content 1fr;gap:8px;align-items:baseline}
.quickSubstats b{color:var(--gold);font-size:9px;white-space:nowrap}
.quickSubstats span{color:var(--body-text);font-size:9px;line-height:1.4}

.priorityPair{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin-top:10px;align-items:stretch}
.priorityPair>.priorityPanel{margin-top:0;grid-template-columns:1fr;height:100%}
.priorityPair .priorityIntro{padding:17px 18px;border-bottom:1px solid var(--line)}
.priorityPair .priorityIntro>strong{font-size:16px}
.priorityPair .priorityIntro p{font-size:10px}
.priorityPair .priorityList{grid-template-columns:1fr}
.priorityPair .priorityList li{border-left:0;border-bottom:1px solid var(--line);padding:13px 15px}
.priorityPair .priorityList li:nth-child(n+3){border-bottom:1px solid var(--line)}
.priorityPair .priorityList li:last-child{border-bottom:0}

@media(max-width:900px){.priorityPair{grid-template-columns:1fr}}
@media(max-width:760px){
  .guideSummary.buildSummaryCompact{grid-template-columns:1fr}
  .buildQuickStats{border-left:0;border-top:1px solid var(--line);padding:14px 0 0}
  .quickGearGrid{grid-template-columns:1fr}
  .priorityPair{grid-template-columns:1fr}
}
@media(max-width:520px){
  .buildQuickStats{padding:12px 0 0}
  .priorityPair{gap:8px}
}
</style>
<script id="restore-rich-builds-v1-script">
(()=>{
  const BUILD_STAT_PROFILES={
    Conqueror:{
      rule:'Current T4 evidence supports ATK ≥ Elemental Mastery on main secondaries. Crit Rate/Crit DMG are the premium reroll stats; Accuracy matters more in PvP and high-Block fights.',
      rows:[['Sword','ATK ≥ Elemental Mastery > SPD'],['Gauntlets','ATK ≥ Elemental Mastery > SPD'],['Helmet','DEF ≥ Physical RES = Elemental RES > HP'],['Chest','DEF ≥ Physical RES = Elemental RES > HP'],['Boots','ATK ≥ Elemental Mastery > SPD']],
      substats:'Crit Rate / Crit DMG > Accuracy > Elemental Mastery > SPD > ATK.'
    },
    Guardian:{
      rule:'Block is Guardian’s defining stat. Stack Block Rate first; after that, DEF/DMG RES drive survival while SPD remains the best offensive/support tempo stat.',
      rows:[['Sword','SPD > ATK > Physical Mastery > Elemental Mastery'],['Shield','DEF > HP > Physical RES = Elemental RES'],['Helmet','DEF ≥ Physical RES = Elemental RES > HP > Effect RES'],['Chest','DEF ≥ Physical RES = Elemental RES > HP'],['Boots','SPD > ATK > Elemental Mastery = Physical Mastery']],
      substats:'Block Rate > DEF > SPD > HP.'
    },
    Destroyer:{
      rule:'S2 Destroyer is balance-sensitive, not permanently EM-first. Keep a healthy Elemental Mastery floor, then flat ATK can match or beat more EM on developed accounts. Crit remains premium; dummy-test close swaps.',
      rows:[['Staff','ATK ≈ Elemental Mastery > Crit > SPD'],['Codex','ATK ≈ Elemental Mastery > Crit > SPD'],['Helmet','DEF ≥ Physical RES = Elemental RES > HP > Effect RES'],['Chest','DEF ≥ Physical RES = Elemental RES > HP'],['Boots','ATK ≈ Elemental Mastery > SPD']],
      substats:'Crit Rate / Crit DMG > ATK ≈ Elemental Mastery > Accuracy > SPD.'
    },
    Dominator:{
      dps:{
        rule:'Effect Hit Rate is a threshold stat: get enough to land Erosion reliably, then favor damage-quality affixes instead of blindly stacking more EHR. If Erosion is unreliable, hybrid/direct damage is safer.',
        rows:[['Staff','Effect Hit Rate ≥ Elemental Mastery ≥ ATK > SPD'],['Orb','Effect Hit Rate ≥ Elemental Mastery ≥ ATK > SPD'],['Helmet','DEF ≥ Physical RES = Elemental RES > HP > Effect RES'],['Chest','DEF ≥ Physical RES = Elemental RES > HP'],['Boots','Elemental Mastery > ATK > SPD']],
        substats:'Effect Hit Rate > Crit Rate / Crit DMG > Elemental Mastery > ATK > SPD.'
      },
      heals:{
        rule:'Healer Dominator is SPD-first on Staff/Orb/Boots and HP-first on Helmet/Chest. Effect Hit Rate is the second main-secondary target on Staff/Orb, but only an average healer affix when rerolling substats.',
        rows:[['Staff','SPD > Effect Hit Rate > Elemental Mastery > ATK'],['Orb','SPD > Effect Hit Rate > Elemental Mastery > ATK'],['Helmet','HP > DEF ≥ Physical RES = Elemental RES > Effect RES'],['Chest','HP > DEF ≥ Physical RES = Elemental RES'],['Boots','SPD > Elemental Mastery > ATK']],
        substats:'Healing Boost > SPD > HP > DMG RES.'
      }
    }
  };

  const DOMINATOR_PRIORITY={
    dps:[
      ['DPS technique investment','Dark Starburst first','Only Techniques that are actually equipped in the DPS loadouts are ranked here.',[
        ['Dark Starburst','Reliable multi-hit single-target damage.'],
        ['Shadow of Termination','Key single-target Dark finisher.'],
        ['Dark Bullet','Consistent Erosion application across the DPS bars.'],
        ['Mana Blast / Abyssal Hand','Both are equipped in the AoE/Erosion loadout.']
      ]],
      ['DPS charm investment','Shadow Erosion first','Only Charms that actually occupy the DPS loadouts are ranked here.',[
        ['Shadow Erosion','Core Erosion engine.'],
        ['Linked Misfortune','Accelerates stack generation.'],
        ["Night's Blessing",'Universal Dark damage scaling.'],
        ['Shadow Vengeance','The equipped survival/damage-window slot in both DPS bars.']
      ]]
    ],
    heals:[
      ['Healing technique investment','Rejuvenating Rain first','Rank the active healing Techniques that are actually equipped in the healer loadout.',[
        ['Rejuvenating Rain','Repeatable single-target heal and a core T4 upgrade.'],
        ['Radiant Restoration','Strong direct party sustain.'],
        ['Waterling Summon','Reliable recurring healing.'],
        ['Frenzy Totem','The equipped support/throughput slot in the main healing bar.']
      ]],
      ['Healing charm investment','Phantom Light first','Rank the healer Charms that actually occupy the support shell.',[
        ['Phantom Light','Mandatory healing boost plus overheal-to-shield conversion.'],
        ['Healing Mastery','Universal throughput.'],
        ['Overhealing','Core healer-shell safety and value.'],
        ['Resurrection / Overhealing','The carry-support recovery/flex slot as actually shown below.']
      ]]
    ]
  };

  const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const root=()=>document.getElementById('buildContent');
  const activeClass=()=>document.querySelector('#classTabs button.active')?.dataset.class||'';
  const roleMode=()=>{
    try{return localStorage.getItem('sxs-build-dominator-mode')==='heals'?'heals':'dps';}catch(_){return 'dps';}
  };
  const profileFor=(cls,mode)=>{
    const p=BUILD_STAT_PROFILES[cls];
    return p?.[mode]||p||null;
  };
  function renderQuickStats(host,cls,mode){
    const profile=profileFor(cls,mode);
    const guide=host.querySelector(':scope > .guideSummary');
    if(!profile||!guide) return;
    let quick=guide.querySelector('.buildQuickStats');
    if(!quick){
      quick=document.createElement('div');
      quick.className='buildQuickStats';
      if(guide.children[1]) guide.children[1].replaceWith(quick); else guide.append(quick);
      guide.classList.add('buildSummaryCompact');
    }
    quick.innerHTML=`<div class="quickTitle">Stat priorities</div><p class="quickRule">${esc(profile.rule)}</p><div class="quickGearGrid">${profile.rows.map(([slot,stats])=>`<div class="quickGearRow"><b>${esc(slot)}</b><span>${esc(stats)}</span></div>`).join('')}</div><div class="quickSubstats"><b>Substats</b><span>${esc(profile.substats)}</span></div>`;
    const gear=host.querySelector(':scope > .gearPanel');
    if(gear) gear.hidden=true;
  }
  function makePanel(data){
    const [kind,title,desc,items]=data;
    const panel=document.createElement('section');
    panel.className='priorityPanel';
    panel.innerHTML=`<div class="priorityIntro"><span>${esc(kind)}</span><strong>${esc(title)}</strong><p>${esc(desc)}</p></div><ol class="priorityList">${items.map((it,i)=>`<li><b>${i+1}</b><div><strong>${esc(it[0])}</strong><p>${esc(it[1])}</p></div></li>`).join('')}</ol>`;
    return panel;
  }
  function ensurePriorityPair(host,cls,mode){
    if(cls==='Dominator'){
      // The temporary regressed template mixed Techniques and Charms into one panel.
      // Replace those direct panels with one true Technique-left / Charm-right pair per role.
      [...host.children].filter(el=>el.classList?.contains('priorityPanel')).forEach(el=>el.remove());
      for(const key of ['dps','heals']){
        let pair=host.querySelector(`:scope > .priorityPair[data-dominator-role="${key}"]`);
        if(!pair){
          pair=document.createElement('div');
          pair.className='priorityPair';
          pair.dataset.dominatorRole=key;
          const data=DOMINATOR_PRIORITY[key];
          pair.append(makePanel(data[0]),makePanel(data[1]));
          const grid=host.querySelector(':scope > .buildGrid');
          if(grid) grid.before(pair); else host.append(pair);
        }
        pair.hidden=key!==mode;
      }
      return;
    }
    if(host.querySelector(':scope > .priorityPair')) return;
    const panels=[...host.children].filter(el=>el.classList?.contains('priorityPanel'));
    if(panels.length>=2){
      const pair=document.createElement('div');
      pair.className='priorityPair';
      panels[0].before(pair);
      // Existing class templates are ordered Technique first, Charm second.
      pair.append(panels[0],panels[1]);
    }
  }
  function applyDominatorRole(host,mode){
    if(activeClass()!=='Dominator') return;
    host.querySelectorAll(':scope > .priorityPair[data-dominator-role]').forEach(el=>{
      el.hidden=el.dataset.dominatorRole!==mode;
    });
    host.querySelectorAll('.buildGrid .buildCard').forEach(card=>{
      const title=card.querySelector('h3')?.childNodes?.[0]?.textContent?.trim()||card.querySelector('h3')?.textContent?.trim()||'';
      const healing=/^Healing/i.test(title);
      const role=healing?'heals':'dps';
      card.dataset.dominatorRole=role;
      card.hidden=role!==mode;
    });
  }
  function signature(host,cls,mode){
    const cards=[...host.querySelectorAll('.buildGrid .buildCard h3')].map(x=>x.textContent.trim()).join('|');
    return `${cls}|${mode}|${cards}`;
  }
  let queued=false;
  function apply(){
    queued=false;
    const host=root(),cls=activeClass();
    if(!host||!cls||!BUILD_STAT_PROFILES[cls]) return;
    const mode=cls==='Dominator'?roleMode():'dps';
    const sig=signature(host,cls,mode);
    const complete=host.querySelector('.buildQuickStats')&&host.querySelector(':scope > .priorityPair');
    if(host.dataset.richBuildSig===sig&&complete) return;
    host.dataset.richBuildSig=sig;
    renderQuickStats(host,cls,mode);
    ensurePriorityPair(host,cls,mode);
    applyDominatorRole(host,mode);
  }
  function queue(){
    if(queued) return;
    queued=true;
    requestAnimationFrame(()=>setTimeout(apply,0));
  }
  document.addEventListener('DOMContentLoaded',()=>{
    const host=root();
    if(host) new MutationObserver(queue).observe(host,{subtree:true,childList:true,attributes:true,attributeFilter:['class','hidden','aria-pressed']});
    document.getElementById('classTabs')?.addEventListener('click',queue);
    host?.addEventListener('click',e=>{if(e.target.closest?.('[data-dominator-mode]')) setTimeout(()=>{if(host) host.dataset.richBuildSig='';queue();},0);});
    queue();
  });
  window.addEventListener('load',queue);
})();
</script>
'''

# Historical loadout/Fantomon enhancer first, then the richer presentation layer.
payload = '\n' + inject.strip() + '\n' + rich.strip() + '\n'
if '</body>' not in s:
    raise SystemExit('index.html has no body close')
s = s.replace('</body>', payload + '</body>', 1)
INDEX.write_text(s, encoding='utf-8')
print('restored maintained Builds loadouts, Fantomon pairs, slot stats, and side-by-side priorities')
