(()=>{
  const S1_CLASSES=['Berserker','Paladin','Archmage','Arcanist'];
  const S2_CLASSES=['Destroyer','Dominator','Conqueror','Guardian'];
  const CLASS_META={
    Berserker:{season:'s1',line:'Duelist → Berserker',path:'duelist',focus:'Crit Rate → Accuracy',summary:'Berserker wants offensive Companion breakpoints that amplify its already-strong Crit scaling. Get the high-value Crit companions online first, then fill Accuracy so burst stays reliable.'},
    Conqueror:{season:'s2',line:'Duelist → Berserker → Conqueror',path:'duelist',focus:'Crit Rate → Accuracy',summary:'Conqueror wants the same Crit-first offensive progression: establish the best Crit breakpoints first, then add Accuracy for consistency.',carry:'Keep your S1 Berserker Companion investment. Affinity levels are permanent and do not reset with the season.'},
    Paladin:{season:'s1',line:'Knight → Paladin',path:'knight',focus:'Block Rate >>> defensive utility',summary:'Paladin gets the most account value from Block. Block improves survival and also supports counter/Rebound play, so your defensive breakpoint companions come before generic DPS companions.'},
    Guardian:{season:'s2',line:'Knight → Paladin → Guardian',path:'knight',focus:'Block Rate >>> defensive utility',summary:'Guardian is a Block-first class. Build the strongest Block breakpoints first, then branch into offensive companions only if you deliberately play Water/offensive Guardian.',carry:'Your Paladin Block companions remain the correct long-term investment in S2. There is no seasonal Companion reset.'},
    Archmage:{season:'s1',line:'Sorcerer → Archmage',path:'sorcerer',focus:'Crit Rate → Accuracy',summary:'Archmage is a pure DPS line. Companion Crit is the first breakpoint target; Accuracy is the second consistency layer. Elemental Mastery is handled elsewhere because it is not a normal Companion breakpoint specialty.'},
    Destroyer:{season:'s2',line:'Sorcerer → Archmage → Destroyer',path:'sorcerer',focus:'Crit Rate → Accuracy',summary:'Destroyer is Crit-first. The Fire branch especially likes reliable Crits, while Accuracy remains the next best Companion-side consistency stat.',carry:'Continue the Archmage roster you already raised. S2 does not invalidate those permanent Crit/Accuracy gains.'},
    Arcanist:{season:'s1',line:'Sage → Arcanist',path:'sage',focus:'DPS: Accuracy → Crit · Heals: Healing Boost at Lv100',summary:'Arcanist has two legitimate Companion paths. DPS wants consistency first; healer investment is delayed because Healing Boost does not pay out until Affinity 100.'},
    Dominator:{season:'s2',line:'Sage → Arcanist → Dominator',path:'sage',focus:'DPS: Accuracy → Crit · Heals: Healing Boost at Lv100',summary:'Dominator has two real paths: Accuracy/Crit for damage, or a dedicated Lv100 Healing Boost push for support.',carry:'Do not rebuild from zero in S2. Continue the Arcanist DPS or healer path you already started.'}
  };

  const CRIT_COMMUNITY=['Eiichi','Karlos','Naira','Qin','Wuji','Mateo','Mio'];
  const ACCURACY_POOL=['Akane','Hermes','Jiangwang','Kazuma','Ophelia'];
  const ARCHMAGE_POOL=['Akane','Hermes','Jiangwang','Mateo','Mio','Ophelia','Sylvia','Chief (Santa)'];
  const BLOCK_CORE=['Braulio','Darkness','Mayoi'];
  const PALADIN_POOL=['Gerald','Hui','Juubee','Micaela','Molly','Vigard'];
  const SAGE_NATIVE=['Astrid','Chief','Isla','Killian'];
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
        {rank:'First',title:'Crit breakpoint targets',names:CRIT_COMMUNITY,why:'Community players have repeatedly identified these as strong DMG Boost/Crit candidates. Prioritize any gold-outline version and confirm the Lv50 tooltip before spending heavily.'},
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
        ['2','Block core → 50','Braulio, Darkness and Mayoi are the repeatedly documented Block targets for tank builds.'],
        ['3','Block core → 70','Repeat their defensive Lv20 bonus while keeping the roster efficient by gift type.'],
        ['4','Best Block → 100','Repeat the Lv50 Block breakpoint. Only then sink heavily into Crit RES or offensive side-build companions.']
      ],
      groups:[
        {rank:'First',title:'Verified Block core',names:BLOCK_CORE,why:'Loot & Waifus and OSLink both call these out for Block-focused Knight/Paladin play. This is the cleanest first investment for a tank main.'},
        {rank:'Second',title:'Paladin / Guardian defensive pool',names:PALADIN_POOL,why:'These are repeatedly listed as Paladin-relevant companions. Among them, raise the ones whose Lv50 tooltip shows Block before Crit RES if your goal is maximum tank value.'},
        {rank:'Offense',title:'Only for an offensive branch',names:['Akane','Hermes','Jiangwang','Ophelia'],why:'Use these after the Block core if you intentionally play Glass Cannon Paladin or offensive Water Guardian. Do not sacrifice your tank breakpoints just for sheet damage.'}
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
        {rank:'Crit check',title:'Cross-class Crit candidates',names:CRIT_COMMUNITY,why:'Companion bonuses are global, so a Crit companion is useful even when its portrait class is different. These are community-identified Crit candidates worth checking on your roster.'},
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
        ['2','Accuracy → 50','DPS Sage/Arcanist/Dominator wants consistency first; Effect Hit Rate itself is not a normal Companion breakpoint stat.'],
        ['3','Crit → 50, Accuracy → 70','Add Crit after Accuracy, then repeat the offensive Lv20 bonus on your best consistency targets.'],
        ['4','Accuracy → 100','Repeat the Lv50 Accuracy breakpoint on your best DPS targets, then finish Crit 70/100.']
      ],
      groups:[
        {rank:'First',title:'Accuracy / offensive DPS core',names:ACCURACY_POOL,why:'Loot & Waifus and Mobi repeatedly recommend this pool for DPS Sage. It is the cleanest named group to start with for Accuracy/offensive value.'},
        {rank:'Second',title:'Sage-native candidates',names:SAGE_NATIVE,why:'These are commonly listed as Arcanist-relevant. Check their Lv50 tooltip and prioritize Accuracy first, then Crit for your DPS build.'},
        {rank:'Then',title:'Crit candidates',names:CRIT_COMMUNITY,why:'Once Accuracy is healthy, global Crit companions are still valuable because Companion bonuses apply regardless of portrait class.'}
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
        {rank:'Before 100',title:'Survival / general account value',names:['DMG Reduction companions','Useful Block / Crit RES companions'],why:'Healing Boost is back-loaded. Do not leave the rest of your account at Lv1 while tunnel-visioning a single healer companion to 100.'},
        {rank:'Hybrid',title:'If you also DPS',names:ACCURACY_POOL,why:'After the healer core is secured, this is the most practical hybrid path for Arcanist/Dominator players who still need solo damage.'}
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
    ['100','Repeats Lv50; healer payoff','Repeats the specialty stat; healer companions such as Aqua/Suimo/Suzu can gain Healing Boost here.']
  ];

  const $c=id=>document.getElementById(id);
  const classStorage={s1:'sxs-companion-class-s1',s2:'sxs-companion-class-s2'};
  const roleStorage='sxs-companion-sage-role';
  let currentSeason='s2';
  let currentClass='Conqueror';
  let sageRole='dps';

  function defaultSeason(){ return 's2'; }
  function loadPrefs(){
    currentSeason=defaultSeason();
    try{
      const r=localStorage.getItem(roleStorage); if(r==='dps'||r==='heals') sageRole=r;
    }catch(_){}
    const list=currentSeason==='s2'?S2_CLASSES:S1_CLASSES;
    let saved=''; try{saved=localStorage.getItem(classStorage[currentSeason])||'';}catch(_){}
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
  function render(){
    const list=currentSeason==='s2'?S2_CLASSES:S1_CLASSES;
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
          <div class="companionPanel" style="margin-top:10px"><span class="companionPanelLabel">Universal reference</span><h3>Affinity breakpoints</h3>${breakpointsHtml()}</div>
        </div>
      </div>
      <div class="companionSources">Research basis · <a href="https://www.prydwen.gg/sword-x-staff/guides/beginner-guide" target="_blank" rel="noreferrer">Prydwen Companion basics ↗</a> · <a href="https://www.lootbar.com/blog/en/companion-upgrade-guide-sword-x-staff.html" target="_blank" rel="noreferrer">LootBar breakpoint guide ↗</a> · <a href="https://lootandwaifus.com/sword-x-staff-companion-database/" target="_blank" rel="noreferrer">Loot & Waifus Companion DB ↗</a> · <a href="https://mobi.gg/en/tips/sword-x-staff-companions/" target="_blank" rel="noreferrer">Mobi class companion guide ↗</a></div>`;
    savePrefs();
  }
  function setup(){
    if(!$c('companionsSection')) return;
    loadPrefs();
    $c('companionClassTabs')?.addEventListener('click',e=>{const b=e.target.closest('[data-companion-class]');if(!b)return;if(b.dataset.companionClass===currentClass)return;currentClass=b.dataset.companionClass;render();});
    $c('companionContent')?.addEventListener('click',e=>{const b=e.target.closest('[data-companion-role]');if(!b)return;sageRole=b.dataset.companionRole;render();});
    render();
  }
  setup();
})();
