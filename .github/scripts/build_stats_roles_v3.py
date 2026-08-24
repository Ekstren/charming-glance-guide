from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

css='''
/* BUILD_STATS_ROLES_V3 */
.buildRoleTabs{border:1px solid var(--line);background:var(--surface);border-radius:12px;display:grid;grid-template-columns:1fr 1fr;gap:5px;width:min(320px,100%);padding:4px;margin:0 0 10px auto}
.buildRoleTabs button{border:0;background:transparent;color:var(--muted);cursor:pointer;border-radius:8px;padding:8px 12px;font-size:10px;font-weight:850}
.buildRoleTabs button.active{background:#345e51;color:#fff}
.buildRoleTabs button:hover{color:var(--green)}
.buildRoleTabs button.active:hover{color:#fff}
@media(max-width:760px){.buildRoleTabs{width:100%;margin-left:0}}
'''
if '/* BUILD_STATS_ROLES_V3 */' not in s:
    marker='.priorityPair{display:grid'
    pos=s.find(marker)
    if pos<0: raise SystemExit('priorityPair CSS marker missing')
    s=s[:pos]+css+s[pos:]

helpers=r'''
// BUILD_STATS_ROLES_V3
const BUILD_STAT_PROFILES={
  Berserker:{rule:'Physical multi-hit DPS. Main lines stay Physical through Season 1.',rows:[['Sword','Physical Mastery > ATK > SPD'],['Gauntlets','Physical Mastery > ATK > SPD'],['Helmet','DEF >= Physical RES = Elemental RES > HP'],['Chest','DEF >= Physical RES = Elemental RES > HP'],['Boots','Physical Mastery > ATK > SPD']],substats:'Crit Rate% > Crit DMG% > Technique DMG vs debuffed targets > Physical Mastery / Accuracy > SPD'},
  Paladin:{rule:'Block/DEF first; add damage only after the tank loop is stable.',rows:[['Sword','SPD > ATK > Physical Mastery'],['Shield','DEF > HP > RES'],['Helmet','DEF > HP > RES'],['Chest','DEF > HP > RES'],['Boots','SPD > ATK > Elemental / Physical Mastery']],substats:'Block Rate% > DEF% > DEF / HP% / HP; offensive stats come after survivability is reliable'},
  Archmage:{rule:'Elemental burst DPS. Crit and speed are premium once main lines are solved.',rows:[['Staff','Elemental Mastery > ATK > Crit > SPD'],['Codex','Elemental Mastery > ATK > Crit > SPD'],['Helmet','DEF / RES > HP'],['Chest','DEF / RES > HP'],['Boots','Elemental Mastery > ATK > SPD']],substats:'Crit Rate > Crit DMG > SPD > Elemental Mastery / Accuracy'},
  Arcanist:{
    dps:{rule:'Dark DoT DPS. Effect Hit Rate comes first so Erosion lands reliably.',rows:[['Staff','Effect Hit Rate >= Elemental Mastery >= ATK > SPD'],['Orb','Effect Hit Rate >= Elemental Mastery >= ATK > SPD'],['Helmet','HP > DEF / RES'],['Chest','HP > DEF / RES'],['Boots','Elemental Mastery > ATK > SPD']],substats:'Effect Hit Rate > Crit Rate / Crit DMG > Elemental Mastery > Accuracy / SPD'},
    heals:{rule:'Healing/support. Speed and Healing Boost matter more than DPS lines.',rows:[['Staff','SPD > Effect Hit Rate > Elemental Mastery'],['Orb','SPD > Effect Hit Rate > Elemental Mastery'],['Helmet','HP > DEF / RES'],['Chest','HP > DEF / RES'],['Boots','SPD > Elemental Mastery > HP']],substats:'Healing Boost% > SPD > HP% > Effect Hit Rate / Elemental Mastery > DEF / RES'}
  },
  Conqueror:{rule:'Elemental melee DPS. S2 Crit RES makes Crit Rate especially valuable.',rows:[['Sword','ATK >= Elemental Mastery > SPD'],['Gauntlets','ATK >= Elemental Mastery > SPD'],['Helmet','DEF >= Physical RES = Elemental RES > HP'],['Chest','DEF >= Physical RES = Elemental RES > HP'],['Boots','ATK >= Elemental Mastery > SPD']],substats:'Crit Rate% > Crit DMG% > Elemental Mastery / Accuracy% > SPD or HP/SPD-to-ATK conversion'},
  Guardian:{rule:'Block is the premium defensive stat; offensive slots still value speed.',rows:[['Sword','SPD > ATK > Physical Mastery > Elemental Mastery'],['Gauntlets','DEF > HP > Physical / Elemental RES'],['Helmet','DEF > HP > RES'],['Chest','DEF > HP > RES'],['Boots','SPD > ATK > Elemental / Physical Mastery']],substats:'Block Rate% > Block Efficiency > PvE/PvP DMG + DMG RES > DEF / SPD / HP / useful Crit'},
  Destroyer:{rule:'Elemental ranged DPS. Crit quality and Accuracy are major S2 damage checks.',rows:[['Staff','Elemental Mastery > Crit > ATK > SPD > Effect Hit Rate'],['Codex','Elemental Mastery > Crit > ATK > SPD > Effect Hit Rate'],['Helmet','DEF / RES > HP'],['Chest','DEF / RES > HP'],['Boots','Elemental Mastery > SPD > ATK']],substats:'Crit + Accuracy / Crit + Crit DMG > Elemental Mastery > Crit Rate / Accuracy / Crit DMG'},
  Dominator:{
    dps:{rule:'Dark DPS. High Effect Hit Rate is required before Erosion becomes dependable.',rows:[['Staff','Effect Hit Rate >= Elemental Mastery >= ATK > SPD'],['Orb','Effect Hit Rate >= Elemental Mastery >= ATK > SPD'],['Helmet','DEF / RES > HP'],['Chest','DEF / RES > HP'],['Boots','Elemental Mastery > ATK > SPD']],substats:'Crit + Accuracy / Crit + Crit DMG / ailment damage > Effect Hit Rate > useful conversions'},
    heals:{rule:'Healing/support is Dominator’s most reliable S2 role.',rows:[['Staff','SPD > Effect Hit Rate > Elemental Mastery > ATK'],['Orb','SPD > Effect Hit Rate > Elemental Mastery > ATK'],['Helmet','HP > DEF / RES'],['Chest','HP > DEF / RES'],['Boots','SPD > Elemental Mastery > ATK']],substats:'DMG RES + Healing > Healing Boost > Block packages > SPD / HP'}
  }
};
const BUILD_ROLE_KEYS={Arcanist:'sxs-build-role-arcanist',Dominator:'sxs-build-role-dominator'};
const BUILD_ROLE_PRIORITY={
  Arcanist:{
    dps:[
      ['DPS technique investment','Erosion engine first','Rank the Dark techniques that stay equipped in the standard DPS setups.',[['Mana Blast','Core AoE Dark hit with Erosion application.'],['Dark Bullet','Reliable single-target Erosion application.'],['Abyssal Hand','Reusable Dark AoE plus Slow utility.'],['Shadow of Termination / Shadow Impact','Boss cash-out or AoE Erosion trigger depending on content.']]],
      ['DPS charm investment','Stack Erosion faster','Build the DoT engine first, then its damage/safety shell.',[['Shadow Erosion','Foundation of the T3 DoT engine.'],['Linked Misfortune','Accelerates Erosion stacking.'],["Night's Blessing",'Straight Dark damage scaling.'],['Shadow Vengeance','Cheat-death plus a burst window.']]]
    ],
    heals:[
      ['Healing technique investment','Radiant Restoration first','Prioritize the techniques that keep the party alive and stabilize difficult content.',[['Radiant Restoration','Primary direct healing investment.'],['Frenzy Totem','High-value team sustain/support slot.'],['Waterling Summon','Reliable recurring party healing.'],['Void Blessing','Flexible support/healing utility.']]],
      ['Healing charm investment','Healing Mastery first','Invest in the core healing shell before flex utility.',[['Healing Mastery','Most universal healing throughput charm.'],['Overhealing','Turns excess healing into additional safety/value.'],['Resurrection','Best recovery tool when deaths are the failure point.'],['Flex support slot','Use party damage, utility or extra safety based on the encounter.']]]
    ]
  },
  Dominator:{
    dps:[
      ['DPS technique investment','Dark Starburst first','Keep technique and charm investment separate for the S2 Dark DPS profile.',[['Dark Starburst','Reliable multi-hit single-target damage.'],['Shadow of Termination','Key single-target Dark finisher.'],['Dark Bullet','Consistent Erosion application.'],['Mana Blast / Abyssal Hand','Use Mana Blast for Erosion/AoE pressure or Abyssal Hand for utility.']]],
      ['DPS charm investment','Shadow Erosion first','Only lean hard into the Erosion package once your Effect Hit Rate supports it.',[['Shadow Erosion','Core Erosion engine.'],['Linked Misfortune','Accelerates stack generation.'],["Night's Blessing",'Universal Dark damage scaling.'],['Shadow Vengeance / Soul Pact Resonance','Safety or greed depending on content.']]]
    ],
    heals:[
      ['Healing technique investment','Rejuvenating Rain first','T4 healing gets meaningful upgrades; rank the active healing tools first.',[['Rejuvenating Rain','Repeatable single-target heal and a core T4 upgrade.'],['Radiant Restoration','Strong direct party sustain.'],['Waterling Summon','Reliable recurring healing.'],['Frenzy Totem','Support/throughput option; Healing Touch can replace it when raw healing is needed.']]],
      ['Healing charm investment','Phantom Light first','Dominator’s strongest healer identity comes from its T4 charm package.',[['Phantom Light','Mandatory healing boost plus overheal-to-shield conversion.'],['Healing Mastery','Universal throughput.'],['Overhealing','Excellent with the T4 shield/heal loop.'],['Resurrection / Mantra of Blessings','Safety for progression or carry buff when the group is stable.']]]
    ]
  }
};
function renderedBuildName(root){return root.querySelector(':scope > .guideSummary strong')?.textContent.trim()||'';}
function buildRoleMode(name){
  if(!BUILD_ROLE_KEYS[name]) return 'dps';
  try{const v=localStorage.getItem(BUILD_ROLE_KEYS[name]);return v==='heals'?'heals':'dps';}catch(_){return 'dps';}
}
function buildStatProfile(name,mode){const p=BUILD_STAT_PROFILES[name];return p&&p[mode]?p[mode]:p;}
function setPriorityPanel(panel,data){
  const [kind,title,desc,items]=data;
  panel.innerHTML=`<div class="priorityIntro"><span>${kind}</span><strong>${title}</strong><p>${desc}</p></div><ol class="priorityList">${items.map((x,i)=>`<li><b>${i+1}</b><div><strong>${x[0]}</strong><p>${x[1]}</p></div></li>`).join('')}</ol>`;
}
function renderBuildQuickStats(root,name,mode){
  const guide=root.querySelector(':scope > .guideSummary');
  if(!guide) return;
  const profile=buildStatProfile(name,mode);
  if(!profile) return;
  let quick=guide.querySelector('.buildQuickStats');
  if(!quick){quick=document.createElement('div');quick.className='buildQuickStats';guide.children[1]?.replaceWith(quick);guide.classList.add('buildSummaryCompact');}
  quick.innerHTML=`<div class="quickTitle">Quick stats</div><p class="quickRule">${profile.rule}</p><div class="quickGearGrid">${profile.rows.map(r=>`<div class="quickGearRow"><b>${r[0]}</b><span>${r[1]}</span></div>`).join('')}</div><div class="quickSubstats"><b>Substats</b><span>${profile.substats}</span></div>`;
}
function applyBuildRole(root,name,mode){
  if(!BUILD_ROLE_KEYS[name]) return;
  let tabs=root.querySelector(':scope > .buildRoleTabs');
  const guide=root.querySelector(':scope > .guideSummary');
  if(!tabs && guide){tabs=document.createElement('div');tabs.className='buildRoleTabs';tabs.innerHTML='<button type="button" data-role="dps">DPS</button><button type="button" data-role="heals">Heals</button>';guide.before(tabs);}
  tabs?.querySelectorAll('button').forEach(btn=>{btn.classList.toggle('active',btn.dataset.role===mode);btn.setAttribute('aria-pressed',btn.dataset.role===mode?'true':'false');btn.onclick=()=>{const next=btn.dataset.role;try{localStorage.setItem(BUILD_ROLE_KEYS[name],next);}catch(_){}applyBuildRole(root,name,next);renderBuildQuickStats(root,name,next);};});
  const panels=[...root.querySelectorAll(':scope > .priorityPanel, :scope > .priorityPair > .priorityPanel')];
  const pdata=BUILD_ROLE_PRIORITY[name]?.[mode];
  if(pdata && panels.length>=2){setPriorityPanel(panels[0],pdata[0]);setPriorityPanel(panels[1],pdata[1]);}
  const allowed=name==='Arcanist'?(mode==='dps'?['Single Target DoT','AoE DoT']:['Healing / Support']):(mode==='dps'?['Single Target','AoE / Erosion']:['Healing / Group','Carry Support']);
  root.querySelectorAll('.buildGrid .buildCard').forEach(card=>{const h=card.querySelector('h3')?.textContent.trim()||'';card.hidden=!allowed.includes(h);});
}
'''
if '// BUILD_STATS_ROLES_V3\nconst BUILD_STAT_PROFILES=' not in s:
    marker='function polishBuildLayout(){'
    pos=s.find(marker)
    if pos<0: raise SystemExit('polishBuildLayout marker missing')
    s=s[:pos]+helpers+'\n'+s[pos:]

start=s.find('function polishBuildLayout(){')
if start<0: raise SystemExit('polish function missing')
end=s.find('\n(function setupBuildLayoutPolish()',start)
if end<0: raise SystemExit('polish function end marker missing')
new_func=r'''function polishBuildLayout(){
  const root=document.getElementById('buildContent');
  if(!root || !root.children.length) return;
  splitBerserkerPriorities(root);
  const name=renderedBuildName(root);
  const mode=buildRoleMode(name);
  applyBuildRole(root,name,mode);
  renderBuildQuickStats(root,name,mode);
  const gear=root.querySelector(':scope > .gearPanel');
  if(gear) gear.hidden=true;
  if(!root.querySelector(':scope > .priorityPair')){
    const panels=[...root.children].filter(el=>el.classList&&el.classList.contains('priorityPanel'));
    if(panels.length>=2){
      const pair=document.createElement('div');
      pair.className='priorityPair';
      panels[0].before(pair);
      pair.append(panels[0],panels[1]);
    }
  }
}
'''
s=s[:start]+new_func+s[end:]

# Verify every displayed class has a complete five-slot profile and substats.
classes=['Berserker','Paladin','Archmage','Arcanist','Conqueror','Guardian','Destroyer','Dominator']
for cls in classes:
    if f'  {cls}:' not in s:
        raise SystemExit(f'missing stat profile for {cls}')
for required in ['buildRoleTabs','BUILD_ROLE_PRIORITY','Healing technique investment','Healing charm investment','renderBuildQuickStats(root,name,mode)']:
    if required not in s: raise SystemExit(f'missing expected role/stat feature: {required}')

p.write_text(s,encoding='utf-8')
print('Added complete slot/substat profiles and DPS/Heals toggles for Arcanist and Dominator.')
