const $=id=>document.getElementById(id);

const LIVE_BUILD_CLASSES=['Destroyer','Dominator','Conqueror','Guardian'];
const BUILD_CLASS_STORAGE_KEY='sxs-build-class-s2';

const T4_SOURCE_BUILDS={
  Destroyer:{
    url:'https://www.prydwen.gg/sword-x-staff/guides/build-guide-destroyer',
    builds:[
      {name:'AOE Build',techniques:['Formation Breaker','Howling Hurricane','Meteoric Flames','Wind Blade Spiral'],charms:['Rapid Cast','Void Bubble','Cyclone Lament','Radiant Sear']},
      {name:'ST Build',techniques:['Formation Breaker','Divine Wrath','Wind Blade Spiral','Thunder of Judgment'],charms:['Rapid Cast','Void Bubble','Mana Surge','Radiant Sear']},
      {name:'Fire AoE Build',techniques:['Formation Breaker','Fiery Star Trail','Fireball','Meteoric Flames'],charms:['Rapid Cast','Void Bubble','Explosive Spirit','Fiery Burst']},
      {name:'Elsa Build',techniques:['Flowing Doom','Water Assault','Frosty Nova','Ice Spike'],charms:['Rapid Cast','Void Bubble','Shattering Ice','Water to Ice']}
    ]
  },
  Dominator:{
    url:'https://www.prydwen.gg/sword-x-staff/guides/build-guide-dominator',
    builds:[
      {name:'Single Target',techniques:['Dark Bullet','Dark Starburst','Chaos Rune','Shadow of Termination'],charms:['Shadow Vengeance',"Night's Blessing",'Shadow Erosion','Linked Misfortune']},
      {name:'AoE',techniques:['Mana Blast','Dark Bullet','Abyssal Hand','Shadow Impact'],charms:['Shadow Vengeance',"Night's Blessing",'Shadow Erosion','Linked Misfortune']},
      {name:'Healing Build',techniques:['Waterling Summon','Rejuvenating Rain','Radiant Restoration','Frenzy Totem'],charms:['Phantom Light','Healing Mastery','Overhealing','FLEX']}
    ]
  },
  Conqueror:{
    url:'https://www.prydwen.gg/sword-x-staff/guides/build-guide-conqueror',
    builds:[
      {name:'Generic Build for all Content',techniques:['Flash Fire','Flame Aura','Flickering Blade','Blade Storm'],charms:['Insightful Eye','Piercing Assault','Tactical Adaptation','Indomitable Will']},
      {name:'Dragon Build',techniques:['Flame Aura','Blade Storm','Flash Fire','Flickering Blade'],charms:['Insightful Eye','Piercing Assault','Tactical Adaptation','Blazing Clash']}
    ]
  },
  Guardian:{
    url:'https://www.prydwen.gg/sword-x-staff/guides/build-guide-guardian',
    builds:[
      {name:'Generic Dungeon Grid',techniques:['Valor Surge','Heart of Challenge','Luminous Shield','Desperate Protection'],charms:['Iron Will','Holy Aegis','Block Awareness','Soul Protection']},
      {name:'Water Paladin',techniques:['Swirling Blade','Lunarwater Threads','Seismic Tide','Raging Maelstrom'],charms:['Frigid Aura','Defensive Assault','Frigid Glint','Potential Rebirth']},
      {name:'Support Knight',techniques:['Valor Surge','Leap Attack','Holy Purification','Lunarwater Threads'],charms:['Frigid Aura','Frigid Glint','Iron Fortress','Oath of Vigil']},
      {name:'Secondary PvE build',techniques:['Desperate Protection','Luminous Shield','Forceful Charge','Star Shattering Slash'],charms:['Rebound','Holy Aegis','Block Mastery','Block Awareness']}
    ]
  }
};

let currentClass='Conqueror';
try{
  const saved=localStorage.getItem(BUILD_CLASS_STORAGE_KEY)||localStorage.getItem('sxs-build-class');
  if(LIVE_BUILD_CLASSES.includes(saved)) currentClass=saved;
}catch(_){}

const escapeHtml=value=>String(value).replace(/[&<>"']/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));

function renderBuildGroup(label,items){
  return `<div class="skillGroup"><span>${label}</span><div>${items.map(item=>`<b>${escapeHtml(item)}</b>`).join('')}</div></div>`;
}

function buildHtml(cls){
  const source=T4_SOURCE_BUILDS[cls];
  if(!source)return '';
  const cards=source.builds.map(build=>`
    <article class="buildCard sourceBuildCard">
      <header><div><h3>${escapeHtml(build.name)}</h3></div></header>
      ${renderBuildGroup('Techniques',build.techniques)}
      ${renderBuildGroup('Charms',build.charms)}
    </article>`).join('');
  return `
    <div class="sourceBuildCollection">
      <p class="sourceBuildNote">Published T4 presets from Prydwen, shown under their original names.</p>
      <div class="buildGrid sourceBuildGrid">${cards}</div>
      <p class="buildSource">Source: <a class="buildSourceLink" href="${source.url}" rel="noreferrer" target="_blank">Prydwen · ${escapeHtml(cls)} T4 build guide ↗</a> · guide updated Sep 1, 2026; checked Sep 25, 2026.</p>
    </div>`;
}

function renderClassTabs(){
  const tabs=$('classTabs');
  tabs.innerHTML=LIVE_BUILD_CLASSES.map(cls=>`<button type="button" role="tab" aria-selected="${cls===currentClass}" class="${cls===currentClass?'active':''}" data-class="${cls}">${cls}</button>`).join('');
}

function renderBuilds(){
  renderClassTabs();
  $('buildContent').innerHTML=buildHtml(currentClass);
}

function setupBuilds(){
  $('classTabs').addEventListener('click',event=>{
    const button=event.target.closest('button[data-class]');
    if(!button||button.dataset.class===currentClass)return;
    currentClass=button.dataset.class;
    try{localStorage.setItem(BUILD_CLASS_STORAGE_KEY,currentClass);}catch(_){}
    renderBuilds();
  });
  renderBuilds();
}

let initialized=false;
export function initialize(){
  if(initialized)return;
  initialized=true;
  setupBuilds();
}
