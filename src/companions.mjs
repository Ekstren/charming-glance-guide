import companionReference from '../data/season3-companions.json';

  const S1_CLASSES=['Berserker','Paladin','Archmage','Arcanist'];
  const S2_CLASSES=['Destroyer','Dominator','Conqueror','Guardian'];
  const S3_CLASSES=['Magister','Prophet','Ravager','Templar'];
  const T5_FROM_T4={Destroyer:'Magister',Dominator:'Prophet',Conqueror:'Ravager',Guardian:'Templar'};
  const CLASS_META={
    Magister:{season:'s3',line:'Sorcerer → Archmage → Destroyer → Magister',path:'sorcerer',focus:'Crit Rate → Accuracy',summary:'Keep your permanent offensive affinity bonuses as you advance to Magister. Aethyris adds Sylvia and Freya for Crit, plus Ophelia for Accuracy.'},
    Prophet:{season:'s3',line:'Sage → Arcanist → Dominator → Prophet',path:'sage',focus:'DPS: Accuracy → Crit · Heals: Healing Boost at Lv100',summary:'Continue your chosen damage or healing affinity route. Astrid and Isla are defensive Crit RES companions; their Sage class does not make them Healing Boost targets.'},
    Ravager:{season:'s3',line:'Duelist → Berserker → Conqueror → Ravager',path:'duelist',focus:'Crit Rate → Accuracy',summary:'Your Conqueror affinity investment carries forward. Add the Aethyris Crit companions by favorite gift, then fill Accuracy for consistency.'},
    Templar:{season:'s3',line:'Knight → Paladin → Guardian → Templar',path:'knight',focus:'Block Rate → defensive utility',summary:'Continue the Block-first affinity route. Aethyris adds Vigard and Gerald for Block; Astrid and Isla provide Crit RES when you want another defensive gift outlet.'},
    Berserker:{season:'s1',line:'Duelist → Berserker',path:'duelist',focus:'Crit Rate → Accuracy',summary:'Berserker wants offensive Companion breakpoints that amplify its already-strong Crit scaling. Get the high-value Crit companions online first, then fill Accuracy so burst stays reliable.'},
    Conqueror:{season:'s2',line:'Duelist → Berserker → Conqueror',path:'duelist',focus:'Crit Rate → Accuracy',summary:'Conqueror wants the same Crit-first offensive progression: establish the best Crit breakpoints first, then add Accuracy for consistency.',carry:'Keep your S1 Berserker Companion investment. Affinity levels are permanent and do not reset with the season.'},
    Paladin:{season:'s1',line:'Knight → Paladin',path:'knight',focus:'Block Rate >>> defensive utility',summary:'Paladin gets the most account value from Block. Block improves survival and also supports counter/Rebound play, so your defensive breakpoint companions come before generic DPS companions.'},
    Guardian:{season:'s2',line:'Knight → Paladin → Guardian',path:'knight',focus:'Block Rate >>> defensive utility',summary:'Guardian is a Block-first class. Build the strongest Block breakpoints first, then branch into offensive companions only if you deliberately play Water/offensive Guardian.',carry:'Your Paladin Block companions remain the correct long-term investment in S2. There is no seasonal Companion reset.'},
    Archmage:{season:'s1',line:'Sorcerer → Archmage',path:'sorcerer',focus:'Crit Rate → Accuracy',summary:'Archmage is a pure DPS line. Companion Crit is the first breakpoint target; Accuracy is the second consistency layer. Elemental Mastery is handled elsewhere because it is not a normal Companion breakpoint specialty.'},
    Destroyer:{season:'s2',line:'Sorcerer → Archmage → Destroyer',path:'sorcerer',focus:'Crit Rate → Accuracy',summary:'Destroyer is Crit-first. The Fire branch especially likes reliable Crits, while Accuracy remains the next best Companion-side consistency stat.',carry:'Continue the Archmage roster you already raised. S2 does not invalidate those permanent Crit/Accuracy gains.'},
    Arcanist:{season:'s1',line:'Sage → Arcanist',path:'sage',focus:'DPS: Accuracy → Crit · Heals: Healing Boost at Lv100',summary:'Arcanist has two legitimate Companion paths. DPS wants consistency first; healer investment is delayed because Healing Boost does not pay out until Affinity 100.'},
    Dominator:{season:'s2',line:'Sage → Arcanist → Dominator',path:'sage',focus:'DPS: Accuracy → Crit · Heals: Healing Boost at Lv100',summary:'Dominator has two real paths: Accuracy/Crit for damage, or a dedicated Lv100 Healing Boost push for support.',carry:'Do not rebuild from zero in S2. Continue the Arcanist DPS or healer path you already started.'}
  };

  const CRIT_COMMUNITY=['Freya','Sylvia','Eiichi','Karlos','Naira','Qin','Wuji','Mateo','Mio','Ming'];
  const ACCURACY_POOL=['Akane','Hermes','Jiangwang','Kazuma','Ophelia'];
  const ARCHMAGE_POOL=['Akane','Hermes','Jiangwang','Mateo','Mio','Ophelia','Sylvia','Chief (Santa)'];
  const BLOCK_CORE=['Braulio','Darkness','Mayoi','Vigard','Gerald'];
  const PALADIN_POOL=['Gerald','Hui','Juubee','Micaela','Molly','Vigard'];
  const SAGE_NATIVE=['Chief','Killian'];
  const HEAL_CORE=['Aqua','Suimo','Suzu'];

  const PATHS={
    duelist:{
      ladder:[
        ['1','All → 20','Unlock the first DMG Boost/Reduction passive across the roster before tunneling one companion.'],
        ['2','Crit targets → 50','Prioritize companions whose Lv50 tooltip gives Crit Rate; gold-outline first when the target stat is the same.'],
        ['3','Accuracy → 50, Crit → 70','Add consistency, then repeat the offensive Lv20 bonus on your best Crit companions at 70.'],
        ['4','Crit → 100','Repeat the Lv50 Crit breakpoint on the best targets, then finish Accuracy 70/100.']
      ],
      groups:[
        {rank:'First',title:'Crit breakpoint targets',names:CRIT_COMMUNITY,why:'Community Crit candidates. Prioritize gold outlines and verify Lv50. Ming, Freya and Sylvia give +1% Crit at 50 and +2% cumulative Crit at 100.'},
        {rank:'Second',title:'Accuracy / ATK pool',names:ACCURACY_POOL,why:'Loot & Waifus and multiple class guides repeatedly recommend this pool for offensive consistency. Raise these after the important Crit breakpoints are online.'},
        {rank:'Later',title:'Defensive account stats',names:['Block / DMG Reduction companions'],why:'Useful eventually, especially for high power-gap pushing, but they should not delay your core Crit and Accuracy breakpoints on a Duelist-line main.'}
      ],
      rules:[
        ['GOLD','Same stat? Gold first','Prydwen notes gold-outline companions have higher passive stats. Rarity does not replace the breakpoint check; it breaks ties between equally useful stats.'],
        ['50','Tooltip decides','Names are a shortlist, not a substitute for the in-game exclamation-mark panel. Event/variant companions can differ, so the actual Lv50 stat always wins.'],
        ['GIFTS','Use all gift types','Within the same priority tier, favor one strong target per favorite-gift type so one scarce gift category does not bottleneck your entire plan.']
      ]
    },
    knight:{
      ladder:[
        ['1','All → 20','Take the cheap roster-wide first passive before specializing. Defensive companions will show DMG Reduction at this stage.'],
        ['2','Block core → 50','Build your existing Block core, then add Aethyris targets Vigard (Books) and Gerald (Practical gifts).'],
        ['3','Block core → 70','Repeat their defensive Lv20 bonus while keeping the roster efficient by gift type.'],
        ['4','Best Block → 100','Repeat the Lv50 Block breakpoint. Only then sink heavily into Crit RES or offensive side-build companions.']
      ],
      groups:[
        {rank:'First',title:'Verified Block core',names:BLOCK_CORE,why:'Braulio, Darkness and Mayoi remain useful. Vigard and Gerald add confirmed +1% Block at 50 and +2% cumulative Block at 100.'},
        {rank:'Second',title:'Permanent defensive pool',names:PALADIN_POOL,why:'These are repeatedly listed as Paladin-relevant companions. Among them, raise the ones whose Lv50 tooltip shows Block before Crit RES if your goal is maximum tank value.'},
        {rank:'Offense',title:'Only for an offensive branch',names:['Akane','Hermes','Jiangwang','Ophelia'],why:'Use these after the Block core if you intentionally play an offensive Water Templar branch. Do not sacrifice your tank breakpoints just for sheet damage.'}
      ],
      rules:[
        ['BLOCK','Block beats generic defense','For the Knight line, the class guides consistently treat Block as the special Companion stat to chase first.'],
        ['GOLD','Same Block stat? Gold first','When two companions give the same desired breakpoint, the gold-outline companion gets priority because its passive stat contribution is higher.'],
        ['50','Check before gifting','Use the in-game tooltip to separate Block from Crit RES companions. Both are defensive; Block is the priority for the standard tank path.']
      ]
    },
    sorcerer:{
      ladder:[
        ['1','All → 20','Collect the cheap first passive from the roster. For DPS, DMG Boost companions are the long-term targets.'],
        ['2','Crit → 50','Crit is the main Companion-side damage bottleneck for Sorcerer-line classes.'],
        ['3','Accuracy → 50, Crit → 70','Fill Accuracy after Crit, then repeat DMG Boost on your best offensive companions.'],
        ['4','Crit → 100','Repeat the Lv50 Crit stat on the strongest targets; finish Accuracy afterward.']
      ],
      groups:[
        {rank:'First',title:'Sorcerer / Archmage priority pool',names:ARCHMAGE_POOL,why:'Mobi lists this group as Archmage-relevant. Within the pool, raise companions showing Crit at Lv50 first, then the Accuracy options.'},
        {rank:'Crit check',title:'Cross-class Crit candidates',names:CRIT_COMMUNITY,why:'These Crit bonuses are global. Freya and Sylvia join Ming as verified Crit targets in Aethyris.'},
        {rank:'Event',title:'Current/event variants',names:['Megumin','Other gold-outline Crit/Accuracy variants'],why:'Event companions can be excellent, but variant stats can differ. Slot them into the same Crit → Accuracy priority based on their actual Lv50/Lv100 tooltip.'}
      ],
      rules:[
        ['CRIT','Crit before Accuracy','Prydwen and LootBar both put Crit first for Sorcerer DPS; Accuracy follows once your primary Crit breakpoints are established.'],
        ['70','Do not stop at 60','Lv60 is cosmetic. If you are spending toward power, the next meaningful stop is 70.'],
        ['GOLD','Gold breaks ties','Gold-outline first only when the companion provides the stat you actually want. A gold defensive stat is not automatically better than a normal Crit target for DPS.']
      ]
    },
    sageDps:{
      ladder:[
        ['1','All → 20','Get the roster-wide first passives before specialization.'],
        ['2','Accuracy → 50','DPS Sage-line classes, including Prophet, want consistency first; Effect Hit Rate itself is not a normal Companion breakpoint stat.'],
        ['3','Crit → 50, Accuracy → 70','Add Crit after Accuracy, then repeat the offensive Lv20 bonus on your best consistency targets.'],
        ['4','Accuracy → 100','Repeat the Lv50 Accuracy breakpoint on your best DPS targets, then finish Crit 70/100.']
      ],
      groups:[
        {rank:'First',title:'Accuracy / offensive DPS core',names:ACCURACY_POOL,why:'Loot & Waifus and Mobi repeatedly recommend this pool for DPS Sage. It is the cleanest named group to start with for Accuracy/offensive value.'},
        {rank:'Second',title:'Crit candidates',names:CRIT_COMMUNITY,why:'Global Crit stays useful after Accuracy. Freya and Sylvia join Ming as verified Crit targets in Aethyris.'},
        {rank:'Optional',title:'Defensive / hybrid pool',names:['Astrid','Isla',...SAGE_NATIVE],why:'Astrid and Isla give Crit RES, not Accuracy. Use defensive companions when survival is the goal; sharing the Sage class does not make a companion an offensive priority.'}
      ],
      rules:[
        ['ACC','Accuracy first','LootBar rates DPS/DoT Sage as Accuracy → Crit. This is a Companion priority, not a replacement for Effect Hit Rate on gear/builds.'],
        ['ROLE','Commit to your role','If healing is your actual end goal, switch to the Heals guide instead of spending every rare gift pushing DPS targets to 100.'],
        ['50','Tooltip wins','Use the exclamation-mark stat panel before committing. Named pools are guide shortlists; your exact variant/stat breakpoint is authoritative.']
      ]
    },
    sageHeal:{
      ladder:[
        ['1','All → 20','Take the cheap permanent first passive across your roster. Healer-specific payoff comes much later.'],
        ['2','Aqua / Suimo / Suzu → 50','Build the three known healer targets steadily; their intermediate stats still contribute while you work toward 100.'],
        ['3','Healer trio → 70','Repeat their Lv20 passive, but remember the actual Healing Boost has not arrived yet.'],
        ['4','Healer trio → 100','This is the payoff: Aqua, Suimo and Suzu are documented to grant Healing Boost at Lv100.']
      ],
      groups:[
        {rank:'Core',title:'Healing Boost targets',names:HEAL_CORE,why:'Loot & Waifus explicitly identifies Aqua, Suimo and Suzu as the healer companions that gain Healing Boost at Affinity 100.'},
        {rank:'Survival',title:'Aethyris defensive options',names:['Astrid','Isla','Vigard','Gerald'],why:'Astrid and Isla add Crit RES; Vigard and Gerald add Block. These are defensive investments, not replacements for the Healing Boost trio.'},
        {rank:'Hybrid',title:'If you also DPS',names:ACCURACY_POOL,why:'After the healer core is secured, this is the most practical hybrid path for Dominator/Prophet players who still need solo damage.'}
      ],
      rules:[
        ['100','Healing Boost is late','Current guides agree the healer-specific Healing Boost does not appear before Lv100. Plan for that long runway.'],
        ['20','Do not starve the roster','The all-20 floor is extremely efficient permanent account power and should happen before an all-in Lv100 rush.'],
        ['GIFTS','Spread intelligently','Use favorite gift types efficiently. If Aqua, Suimo and Suzu compete for the same scarce gift, keep another useful target moving with other gift categories.']
      ]
    }
  };

  const BREAKPOINTS=[
    ['20','DMG Boost or DMG Reduction','First meaningful specialization signal. Cheap enough that bringing the roster to 20 is generally efficient.'],
    ['50','Crit / Accuracy / Block / Crit RES','The major class-targeting breakpoint. This is where your leveling order should become selective.'],
    ['60','Cosmetic skin','No power breakpoint. Do not intentionally stop here if the goal is stats.'],
    ['70','Repeats the Lv20-type bonus','Another DMG Boost/Reduction increase on the companions you already chose.'],
    ['100','Second specialty / healer payoff','Most repeat the Lv50 stat; healer companions such as Aqua/Suimo/Suzu gain Healing Boost here.']
  ];

  const $c=id=>document.getElementById(id);
  const classStorage={s1:'sxs-companion-class-s1',s2:'sxs-companion-class-s2',s3:'sxs-companion-class-s3'};
  const roleStorage='sxs-companion-sage-role';
  let currentSeason='s3';
  let currentClass='Magister';
  let sageRole='dps';

  function defaultSeason(){ return 's3'; }
  function loadPrefs(){
    currentSeason=defaultSeason();
    try{
      const r=localStorage.getItem(roleStorage); if(r==='dps'||r==='heals') sageRole=r;
    }catch(_){}
    const list=currentSeason==='s3'?S3_CLASSES:currentSeason==='s2'?S2_CLASSES:S1_CLASSES;
    let saved=''; try{saved=localStorage.getItem(classStorage[currentSeason])||T5_FROM_T4[localStorage.getItem(classStorage.s2)]||'';}catch(_){}
    currentClass=list.includes(saved)?saved:list[0];
  }
  function savePrefs(){
    try{localStorage.setItem(classStorage[currentSeason],currentClass);localStorage.setItem(roleStorage,sageRole);}catch(_){}
  }
  function groupsHtml(groups){
    return groups.map(g=>`<div class="companionGroup"><div class="companionGroupHead"><b>${g.title}</b><small>${g.rank}</small></div><p>${g.why}</p><div class="companionNames">${g.names.map(n=>`<span>${n}</span>`).join('')}</div></div>`).join('');
  }
  function ladderHtml(ladder){
    return ladder.map(x=>`<div><b>Step ${x[0]}</b><strong>${x[1]}</strong><span>${x[2]}</span></div>`).join('');
  }
  function rulesHtml(rules){
    return rules.map(x=>`<div class="companionRule"><b>${x[0]}</b><div><strong>${x[1]}</strong><p>${x[2]}</p></div></div>`).join('');
  }
  function breakpointsHtml(){
    return `<table class="companionBreakpointTable"><thead><tr><th>Affinity</th><th>What unlocks</th><th>How to use it</th></tr></thead><tbody>${BREAKPOINTS.map(x=>`<tr><td>Lv${x[0]}</td><td>${x[1]}</td><td>${x[2]}</td></tr>`).join('')}</tbody></table>`;
  }
  function regionalReferenceHtml(rows){
    const bonus=(row,stat,level)=>row.breakpoints[level][stat]||0;
    return `<table class="companionBreakpointTable"><thead><tr><th>Companion</th><th>Gifts / unlock</th><th>Affinity bonuses</th></tr></thead><tbody>${rows.map(row=>{const damage=bonus(row,'DMG Boost',20)?'DMG Boost':'DMG RES';const specialty=['Crit Rate','Accuracy','Block Rate','Crit RES'].find(stat=>bonus(row,stat,50));const heal=bonus(row,'Healing Boost',100);return `<tr><td style="white-space:normal"><b>${row.name}</b><br>${row.nativeClass}${row.premium?'<br>Gold':''}</td><td>${row.gift}<br>${row.journals} journal${row.journals===1?'':'s'}</td><td>${damage}: +${bonus(row,damage,20)}% / +${bonus(row,damage,70)}%<br>${specialty}: +${bonus(row,specialty,50)}% / +${bonus(row,specialty,100)}%${heal?`<br>Healing Boost: +${heal}% at 100`:''}</td></tr>`;}).join('')}</tbody></table>`;
  }
  function seasonReferenceHtml(){
    return `<div class="companionPanel" style="margin-top:10px"><span class="companionPanelLabel">Season 3 · Aethyris</span><h3>New-region companion reference</h3><p>Astrid and Isla give Crit RES, not Healing Boost. Freya / Sylvia add Crit, Ophelia adds Accuracy, and Vigard / Gerald add Block.</p><details><summary>Aethyris gifts &amp; affinity · 7 companions</summary><p>Bonus pairs are cumulative at Lv20 / 70 for DMG and Lv50 / 100 for the specialty stat.</p>${regionalReferenceHtml(companionReference.aethyris)}<p class="companionCaution">Favorite gifts give ×1.25 affinity; each companion’s own journal gives ×2.</p></details><details><summary>Loong Haven carryover</summary>${regionalReferenceHtml(companionReference.loongHaven)}</details></div><div class="companionPanel" style="margin-top:10px"><span class="companionPanelLabel">Aethyris progression</span><h3>Bond Odyssey &amp; Stone Symphony</h3><p>Check Vista Dispatch challenge requirements, then match the displayed companion roles before sending timed expeditions. Companions can return with resources and souvenirs; the mission panel gives the current timer and Major Success bonus.</p></div>`;
  }
  function render(){
    const list=currentSeason==='s3'?S3_CLASSES:currentSeason==='s2'?S2_CLASSES:S1_CLASSES;
    if(!list.includes(currentClass)) currentClass=list[0];
    $c('companionClassTabs').innerHTML=list.map(name=>`<button type="button" class="${name===currentClass?'active':''}" data-companion-class="${name}">${name}</button>`).join('');
    const meta=CLASS_META[currentClass];
    const isSage=meta.path==='sage';
    let pathKey=meta.path;
    if(isSage) pathKey=sageRole==='heals'?'sageHeal':'sageDps';
    const guide=PATHS[pathKey];
    const roleToggle=isSage?`<div class="companionRoleToggle" role="group" aria-label="${currentClass} companion role"><button type="button" data-companion-role="dps" class="${sageRole==='dps'?'active':''}">DPS</button><button type="button" data-companion-role="heals" class="${sageRole==='heals'?'active':''}">Heals</button></div>`:'';
    $c('companionContent').innerHTML=`
      <div class="companionHero">
        <div class="companionHeroMain"><span>${meta.line}</span><div class="companionTitleRow"><h2>${currentClass}</h2>${roleToggle}</div><p>${meta.summary}</p></div>
        <div class="companionFocus"><small>Stat focus</small><strong>${meta.focus}</strong><p>Affinity is permanent account progression. Match your gifts to the right breakpoint stats instead of leveling companions only because their portrait class matches yours.</p></div>
      </div>
      <div class="companionGrid">
        <div>
          <div class="companionPanel"><span class="companionPanelLabel">Recommended leveling route</span><h3>${isSage?(sageRole==='heals'?'Healer Affinity path':'DPS Affinity path'):'Priority order'}</h3><p>Use these as breakpoints, not hard caps. If two targets give the same desired stat, favor the gold-outline companion and the gift type you can actually feed efficiently.</p><div class="companionLadder">${ladderHtml(guide.ladder)}</div></div>
          <div class="companionPanel" style="margin-top:10px"><span class="companionPanelLabel">Who to raise first</span><h3>Priority companion pools</h3><div class="companionGroups">${groupsHtml(guide.groups)}</div><p class="companionCaution"><b>Important:</b> companion/event variants can differ. The in-game exclamation-mark stat panel is the final authority; the names above are a research-backed shortlist for what to inspect first.</p></div>
        </div>
        <div>
          <div class="companionPanel"><span class="companionPanelLabel">Decision rules</span><h3>How to spend gifts efficiently</h3><div class="companionRules">${rulesHtml(guide.rules)}</div></div>
          <div class="companionPanel" style="margin-top:10px"><span class="companionPanelLabel">Universal reference</span><h3>Affinity breakpoints</h3>${breakpointsHtml()}</div>${seasonReferenceHtml()}
        </div>
      </div>
      <div class="companionSources">Season 3 checked Nov 8, 2026 · <a href="https://www.purrwikimania.com/npcs" target="_blank" rel="noreferrer">NPC gift / stat reference ↗</a> · <a href="https://www.prydwen.gg/sword-x-staff/guides/beginner-guide" target="_blank" rel="noreferrer">Prydwen Companion basics ↗</a> · <a href="https://www.lootbar.com/blog/en/companion-upgrade-guide-sword-x-staff.html" target="_blank" rel="noreferrer">LootBar breakpoint guide ↗</a> · <a href="https://lootandwaifus.com/sword-x-staff-companion-database/" target="_blank" rel="noreferrer">Loot & Waifus Companion DB ↗</a> · <a href="https://mobi.gg/en/tips/sword-x-staff-companions/" target="_blank" rel="noreferrer">Mobi class companion guide ↗</a> · <a href="https://0xnobodyyt.github.io/sxs-companions/" target="_blank" rel="noreferrer">Current client Companion catalog ↗</a></div>`;
    savePrefs();
  }
  function setup(){
    if(!$c('companionsSection')) return;
    loadPrefs();
    $c('companionClassTabs')?.addEventListener('click',e=>{const b=e.target.closest('[data-companion-class]');if(!b)return;if(b.dataset.companionClass===currentClass)return;currentClass=b.dataset.companionClass;render();});
    $c('companionContent')?.addEventListener('click',e=>{const b=e.target.closest('[data-companion-role]');if(!b)return;sageRole=b.dataset.companionRole;render();});
    render();
  }
  let initialized=false;
  export function initialize(){if(initialized)return;initialized=true;setup();}
