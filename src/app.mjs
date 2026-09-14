import { timelineData } from './timeline-data.mjs';
import { setupNavigation } from './navigation.mjs';
import { isoAddDays } from './time.mjs';
import { S1_END } from './season-clock.mjs';
import { localShortDateTimeLabel,nextResetLocalLabel } from './display-time.mjs';
import {openCalculator} from './calculator-loader.mjs';
import {loadTheme,saveTheme} from './preferences.mjs';
const $=id=>document.getElementById(id);
const SECTION_STORAGE_KEY='sxs-active-section';
function renderLocalTimeLabels(){const reset=nextResetLocalLabel();if($('headerResetLocal'))$('headerResetLocal').textContent=`Reset: ${reset}`;if($('timelineResetLocal'))$('timelineResetLocal').textContent=reset;}
function isoForServerDay(serverDay){ return isoAddDays('2026-07-15',serverDay-1); }

function treasureHuntReward(phase){
    const fixed={
      1:'Selectable Cinder Ridge Mythic Relic',2:'Lucky Statue',3:'Selectable Tier 3 class skill shards ×180',4:'Primal Gem',
      5:'Selectable Aqualis Mythic Relic',6:'Lucky Statue',7:'Selectable Tier 4 class skill shards ×180',8:'Primal Gem',
      9:'Selectable Loong Haven I Mythic Relic',10:'Lucky Statue',11:'Selectable Tier 4 class skill shards ×180',12:'Primal Gem',
      13:'Selectable Loong Haven II Mythic Relic',14:'Lucky Statue',15:'Selectable Tier 4 class skill shards ×180'
    };
    if(fixed[phase]) return fixed[phase];
    const cycle=(phase-16)%4;
    if(cycle===0){
      if(phase>=32) return 'Primal Gem / Philosopher’s Stone / Treasure Detector';
      if(phase>=20) return 'Primal Gem / Philosopher’s Stone';
      return 'Primal Gem';
    }
    if(cycle===1) return 'Selectable Miracle Relic Box';
    if(cycle===2){
      if(phase>=34) return 'Lucky Statue / Golden Divine Tree / Endless Hourglass';
      return 'Lucky Statue / Golden Divine Tree';
    }
    const tier=phase>=47?7:phase>=31?6:5;
    return `Selectable Tier ${tier} class skill shards`;
  }

function addRecurringEvents(){
    // Grand Treasure Hunt: Phase 1 on server day 8, then weekly.
    for(let phase=1;phase<=57;phase++){
      const serverDay=8+(phase-1)*7;
      const start=isoForServerDay(serverDay), end=isoAddDays(start,7);
      const reward=treasureHuntReward(phase);
      let strategy='Auroradrasil Energy carries over; check the Lv.5 reward before spending.';
      if(/Lucky Statue/.test(reward)) strategy='High-priority farming relic: chance to double dungeon chest rewards. Energy carries over.';
      else if(/Primal Gem/.test(reward)) strategy='High-priority farming relic: improves Gem acquisition. Energy carries over.';
      else if(/skill shards/.test(reward)) strategy='Class-skill phase; useful when you still need the current Tier skill investment.';
      else if(/Mythic Relic/.test(reward)||/Miracle Relic/.test(reward)) strategy='Relic-focused phase; compare against your current collection before spending saved Energy.';
      timelineData.push([start,serverDay,'Treasure Hunt',`Grand Treasure Hunt · Phase ${phase}`,`UNCONFIRMED recurring server-age projection · Lv.5: ${reward} · ${strategy}`,'event',end,'unconfirmed']);
    }
    // STALE_OCEANIC_EVENT_REFS_V2: recurring future rows contain only event-specific guidance;
    // expired limited-event overlaps are kept only on their historical runs.
    // Normal rotating mini-events: Bingo -> Lucky Scratch -> Feneck, each one week.
    const defs=[
      {base:15,name:'Bingo Draw',prep:'Destiny Fruits',note:'Rewards: board and milestone prizes (the exact item grid can vary). Complete every daily mission first. Global players report roughly 60–80 Destiny Fruits is usually enough to finish the normal board.'},
      {base:22,name:'Lucky Scratch',prep:'Material Realm tools',note:'Rewards: scratch-card RNG and milestone prizes. Use saved Material Realm consumables while this event is active to generate more scratch cards. This is the week to cash in the tools you banked during Feneck.'},
      {base:29,name:"Feneck's Puzzle",prep:'No major stockpile',note:'Rewards: puzzle and daily-track prizes. Do the event rewards and start banking Material Realm tools for the next Lucky Scratch.'}
    ];
    defs.forEach(def=>{
      let count=1;
      for(let serverDay=def.base;serverDay<=400;serverDay+=21,count++){
        const start=isoForServerDay(serverDay), end=isoAddDays(start,7);
        let note=def.note;
        if(def.name==='Bingo Draw' && count===2) note += ' Charming Glance: this run overlaps Oceanic Festival Aug 19–26, so Fruit spending can advance both events.';
        if(def.name==='Lucky Scratch' && count===2) note += ' Charming Glance: starts Aug 26 while Oceanic is still active; Material Realm activity can also advance Oceanic Beach Shovel objectives.';
        timelineData.push([start,serverDay,def.name,`${def.name} · ${count}`,`UNCONFIRMED recurring server-age projection · ${def.prep} · ${note}`,'event',end,'unconfirmed']);
      }
    });
    timelineData.sort((a,b)=>a[0].localeCompare(b[0]) || a[1]-b[1] || a[2].localeCompare(b[2]));
  }

addRecurringEvents();

let timelineFilter='all';

const SERVER_START_ISO='2026-07-15';

const PACIFIC_TZ='America/Los_Angeles';

function isoDayNumber(iso){
    const [y,m,d]=iso.split('-').map(Number);
    return Math.floor(Date.UTC(y,m-1,d)/86400000);
  }

function isoDayDiff(a,b){ return isoDayNumber(b)-isoDayNumber(a); }

function displayDate(iso){
    const [y,m,d]=iso.split('-').map(Number);
    return new Date(Date.UTC(y,m-1,d,12));
  }

function pacificClockParts(date=new Date()){
    const parts=Object.fromEntries(new Intl.DateTimeFormat('en-US',{timeZone:PACIFIC_TZ,year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',hourCycle:'h23'}).formatToParts(date).filter(p=>p.type!=='literal').map(p=>[p.type,p.value]));
    return {year:Number(parts.year),month:Number(parts.month),day:Number(parts.day),hour:Number(parts.hour)};
  }

function currentResetIso(date=new Date()){
    const p=pacificClockParts(date);
    const iso=`${p.year}-${String(p.month).padStart(2,'0')}-${String(p.day).padStart(2,'0')}`;
    return p.hour>=6 ? iso : isoAddDays(iso,-1);
  }

function eventIsActive(e,boundaryIso){
  if(e[5]!=='event' || !e[6] || e[0]>boundaryIso) return false;
  const exactExpiry=e[8];
  if(exactExpiry){
    const ms=Date.parse(exactExpiry);
    if(Number.isFinite(ms)) return Date.now()<ms;
  }
  return boundaryIso<e[6];
}

function timelineFilterMatches(e){
    if(timelineFilter==='all') return true;
    if(timelineFilter==='maps') return e[5]==='region' || e[5]==='seasonal-map';
    return e[5]===timelineFilter;
  }

function timelineSummaryText(e){
    const text=String((e&&e[4])||'').trim();
    const title=String((e&&e[3])||'');
    const type=String((e&&e[2])||'');
    // TIMELINE_PLAIN_EVENT_COPY_V1: user-facing cards summarize the event itself.
    // Research confidence/source prose stays in the maintained raw row when useful,
    // but CONFIRMED / UNCONFIRMED / PROJECTED-style audit language is not shown on cards.
    if(title==='Warlord’s Rest') return 'Player Lv.130 · Normal 3.55M · Hard 5M · Nightmare 6M';
    if(title==='Server Tournament') return e[0]==='2026-09-12' ? 'Registration opens Friday Sep. 11 · tournament Saturday Sep. 12.' : 'Registration opens the day before · tournament Saturday.';
    if(title==='Nexus Tournament · 4v4') return '4v4 Nexus Tournament · Top-4 qualification format; brackets and prediction phases are handled in game.';
    if(title==='Acme Nexus') return 'Loong Haven seasonal map · gateway to Aethyris.';
    if(title==='Aethyris opens') return 'Season 3 · Aethyris · Tier 5 · Skyrend Cliff, Unbroken Camp and Harmonic Crystal · Nexus grouping expands from 4 servers to an 8-server pool.';
    // TIMELINE_SUMMARY_PROVENANCE_CLEAN_V2: keep source/confidence wording in raw rows/comments only.
    if(title==='Aethyris area-unlock stockpile') return 'Gateway Key ×5 · Magic Drill ×2 · Water Mine ×2 · cloud key ×2 · hammer ×5';
    if(title==='Astral Odyssey') return 'Aethyris season map';
    if(title==='Abyssal Bastion') return 'Normal 20M · Hard 26M · Nightmare 30M · Purgatory 46M';
    if(title==='Aethyris Relic II') return 'Second Aethyris relic gacha';
    if(title==='Courtyard of Purification') return 'Normal 32.5M · Hard 43M · Nightmare 50.5M · Purgatory 75M';
    if(title==='Temple of Order') return 'Normal 55M · Hard 65M · Nightmare 82M · Purgatory 115M';
    if(title==='Aethyris Relic III') return 'Third Aethyris relic gacha';
    if(title==='Solar Spire') return 'Normal 84.5M · Hard 100M · Nightmare 120M · Purgatory 180M';
    if(title==='Sovereign’s Nest') return 'Normal 125M · Hard 145M · Nightmare 180M · Purgatory 250M · Abyss 350M';
    if(title==='Hapadi opens') return 'Season 4 · Hapadi';
    if(title==='Ingenious Clocktower') return 'Hapadi Day 1 · Normal · Hard 27M';
    if(title==='Tier 6 class advancement') return 'Player Lv.172 · Class Lv.280 · Tier 5 class Lv.50 · Hapadi Nine';
    if(title==='Hapadi area-unlock stockpile') return 'Gateway Key ×5 · Magic Drill ×2 · Water Mine ×2 · season item ×5';
    if(title==='Fantomon Resonance unlock') return 'Player Lv.180';
    if(title==='Pirate Galleon') return 'Hapadi Day 14 · Normal 35M · Hard 48M · Nightmare 57M · Purgatory 84M';
    if(title==='Grotesque Fairground') return 'Hapadi Day 15 season map';
    if(title==='Leviathan Submersible') return 'Hapadi Day 28 · Normal 62M · Hard 72M · Nightmare 87M · Purgatory 130M';
    if(title==='Crystal Spiral Tree') return 'Aethyris’s first dungeon · Sylvan Set · current older-server guidance lists Hard at 9M.';
    if(title==='Gift code · CRYSTAL'){const t=Date.parse(String((e&&e[8])||''));return `300 Raw Ore + 1 Stellatie · reported cutoff ${Number.isFinite(t)?localShortDateTimeLabel(t):'Sep. 15 source cutoff'}.`;}
    if(title==='Official Top-Up Platform events open') return 'Cumulative Top-up Lottery + Daily Top-up Sign-in open on the official top-up platform.';
    if(title==='Vegetables Fairy Collab Pt. 2') return 'Daily sign-in, Veggie Shop, Veggie Shuffle, Lemon Whale purification, Cabbage Dog Fantomon and Part 2 Visages.';
    if(title.startsWith('Oceanic Festival')) return 'Global Aug 18–31. Prioritize Beach Shovels; Bingo Draw 2 overlaps on Charming Glance, so Destiny Fruit spending can progress both events.';
    if(title.startsWith('Bingo Draw')) return 'Do dailies first; roughly 60–80 Destiny Fruits usually clears the normal board. Save extra Fruits for the next Bingo run if you finish early.';
    if(title.startsWith('Lucky Scratch')) return 'Spend saved Material Realm tools while Lucky Scratch is active to generate more scratch cards; bank tools during Feneck week for the next run.';
    if(title.startsWith('Weekly gift code')) return `2,000 Rolla + 120 Dawnium. Expired ${localShortDateTimeLabel('2026-08-25T05:00:00Z')}.`;
    if(title==='Gift code · Summer') return 'UNCONFIRMED cutoff: Summer gives 160 Dawnium and is reported valid through Sep 1; redeem promptly.';
    if(title==='Gift code · VEGGIE'){const t=Date.parse(String((e&&e[8])||''));return `Official Global Discord: 10 Rare Auroral Badges + 80 Dawnium. Expires ${Number.isFinite(t)?localShortDateTimeLabel(t):'at the stored source cutoff'}; redeem before then.`;}
    if(title.startsWith('Grand Treasure Hunt')){
      const reward=(text.match(/Lv\.5:\s*([^·.]+)/)||[])[1];
      return reward ? `Lv.5 reward: ${reward.trim()}. Auroradrasil Energy carries over.` : 'Check the Lv.5 reward before spending saved Auroradrasil Energy; unused Energy carries over.';
    }
    if(title==='Season 2 final-day prep') return 'Historical rollover note: the Bed EXP hold used 34 hours of natural accumulation plus the single 2-hour reset boost, filling the 36-hour Bed capacity.';
    if(title==='Loong Haven opens') return `Confirmed ${localShortDateTimeLabel(S1_END)}. Gates: Lv.106 T4; Lv.108 + Numbuville + Mythic duplicate for Fantomon Adult; Lv.116 Demonbind Tower.`;
    if(title==='Gear Refinement & Affix Transfer') return 'S2 feature: Mythic+ S2 gear can reroll or transfer affixes; S1 gear cannot transfer forward. Same-season transfer is free.';
    if(title==='Season 2 Day 1 checklist') return 'At S2 reset: claim rollover rewards, rank up first, push reachable statues, then spend saved Bed boosts, Stamina and Material Realm resources.';
    if(title==='Vegetable Fairy Part Two') return 'Vegetable Fairy Part Two event.';
    let displayText=text;
    if(/^(?:CONFIRMED|UNCONFIRMED|PROJECTED|EXPECTED|STRONGLY SUPPORTED|OFFICIAL GLOBAL NAME)/i.test(displayText)){
      const colon=displayText.indexOf(':');
      if(colon>=0 && colon<180) displayText=displayText.slice(colon+1).trim();
      displayText=displayText
        .replace(/^(?:CONFIRMED|UNCONFIRMED|PROJECTED|EXPECTED|STRONGLY SUPPORTED)\b[^.]{0,180}\.\s*/i,'')
        .replace(/\b(?:CONFIRMED|UNCONFIRMED|PROJECTED|STRONGLY SUPPORTED)\b/gi,'')
        .replace(/\s{2,}/g,' ')
        .trim();
    }
    if(displayText.length<=170) return displayText;
    const sentences=displayText.split(/\.\s+/).filter(Boolean);
    let summary=sentences[0]||displayText;
    if(summary.length<95 && sentences.length>1) summary += '. ' + sentences[1];
    if(summary.length>170) summary=summary.slice(0,167).replace(/\s+\S*$/,'')+'…';
    if(summary && !/[.!?…]$/.test(summary)) summary+='.';
    return summary;
  }

function timelineDetailHtml(e){
    const summary=timelineSummaryText(e);
    return `<p>${summary}</p>`;
  }

function dedupeTimelineDetails(){
    const timeline=$('timeline');
    if(!timeline) return;
    timeline.querySelectorAll('.entry').forEach(entry=>{
      const details=[...entry.querySelectorAll('details.entryMore')];
      details.slice(1).forEach(el=>el.remove());
    });
  }

const TIMELINE_SEASON_WINDOWS=[
    {key:'s1',label:'Season 1',start:1,end:46},
    {key:'s2',label:'Season 2 · Crossed Paths',start:47,end:113},
    {key:'s3',label:'Season 3 · Aethyris',start:114,end:225},
    {key:'s4',label:'Season 4 · Hapadi',start:226,end:334},
    {key:'s5',label:'Season 5 · Ignis',start:335,end:Infinity}
  ];

function timelineSeasonScope(boundaryIso=currentResetIso()){
    const serverDay=Math.max(1,isoDayDiff(SERVER_START_ISO,boundaryIso)+1);
    let index=TIMELINE_SEASON_WINDOWS.findIndex(x=>serverDay>=x.start&&serverDay<=x.end);
    if(index<0) index=TIMELINE_SEASON_WINDOWS.length-1;
    const current=TIMELINE_SEASON_WINDOWS[index];
    const next=TIMELINE_SEASON_WINDOWS[index+1]||null;
    return {serverDay,current,next,minDay:current.start,maxDay:next?next.end:current.end};
  }

function timelineDataForScope(boundaryIso=currentResetIso()){
    const scope=timelineSeasonScope(boundaryIso);
    return {scope,data:timelineData.filter(e=>{
      const day=Number(e?.[1]);
      return Number.isFinite(day)&&day>=scope.minDay&&day<=scope.maxDay;
    })};
  }

function renderTimeline(){
    renderLocalTimeLabels();
    const boundaryIso=currentResetIso();
    const {scope,data:scopedTimelineData}=timelineDataForScope(boundaryIso);
    const showPast=$('showPast').checked;
    const filtered=scopedTimelineData.filter(e=>{
      const active=eventIsActive(e,boundaryIso);
      if(!showPast && e[0]<boundaryIso && !active) return false;
      return timelineFilterMatches(e);
    });
    const grouped=new Map(); filtered.forEach(e=>{if(!grouped.has(e[0])) grouped.set(e[0],[]); grouped.get(e[0]).push(e);});
    $('timeline').innerHTML=[...grouped.entries()].map(([date,entries])=>{
      const dt=displayDate(date); const first=entries[0];
      const month=dt.toLocaleString('en-US',{month:'short',timeZone:'UTC'}); const day=dt.getUTCDate(); const weekday=dt.toLocaleString('en-US',{weekday:'short',timeZone:'UTC'});
      const today=date===boundaryIso;
      const groupActive=entries.some(e=>eventIsActive(e,boundaryIso));
      const entrySeason=TIMELINE_SEASON_WINDOWS.find(x=>Number(first[1])>=x.start&&Number(first[1])<=x.end);
      const seasonDay=entrySeason?Math.max(1,Number(first[1])-entrySeason.start+1):1;
      const seasonNumber=entrySeason?TIMELINE_SEASON_WINDOWS.indexOf(entrySeason)+1:1;
      return `<article class="dayGroup${today?' today':''}${groupActive?' activeEvent':''}" data-date="${date}"><div class="dayMarker"><span>Server Day ${first[1]}</span><small class="seasonDayLabel">Season ${seasonNumber} Day ${seasonDay}</small><b>${today?'CURRENT RESET':groupActive?'ACTIVE EVENT':''}</b></div><div class="dateBlock"><span>${month}</span><strong>${day}</strong><small>${weekday}</small></div><div class="entryStack">${entries.map(e=>{const active=eventIsActive(e,boundaryIso);return `<div class="entry${active?' entry-active':''}"><span class="category category-${e[5]}">${e[2]}</span><div><p><b>${e[3]}</b>${active?'<span class="activePill">ACTIVE</span>':''}</p>${timelineDetailHtml(e)}</div></div>`;}).join('')}</div></article>`;
    }).join('') || '<div class="emptyBuild">No timeline entries match this filter.</div>';
    dedupeTimelineDetails();

    const serverDay=scope.serverDay;
    const fixedUpcoming=scopedTimelineData.find(e=>e[0]>=boundaryIso && e[5]!=='event') || scopedTimelineData.filter(e=>e[5]!=='event').at(-1) || null;
    const seasonDay=Math.max(1,serverDay-scope.current.start+1);
    const seasonNumber=Math.max(1,TIMELINE_SEASON_WINDOWS.indexOf(scope.current)+1);
    const milestoneName=fixedUpcoming?String(fixedUpcoming[3]):'No fixed milestone loaded';
    const milestoneDays=fixedUpcoming?Math.max(0,isoDayDiff(boundaryIso,fixedUpcoming[0])):null;
    const milestoneWhen=milestoneDays===null?'':milestoneDays===0?'today':milestoneDays===1?'1 day to go':`${milestoneDays} days to go`;
    $('timelineSummary').innerHTML=`<div><span>Server day</span><strong class="summaryNumber">${serverDay}</strong></div><div><span>Season ${seasonNumber} day</span><strong class="summaryNumber">${seasonDay}</strong></div><div><span>Next milestone</span><strong>${milestoneName}</strong>${milestoneWhen?`<small class="summaryMeta">${milestoneWhen}</small>`:''}</div>`;

    const activeEvents=timelineData.filter(e=>eventIsActive(e,boundaryIso));
    const live=$('timelineNow');
    if(live){
      const cards=activeEvents.map(e=>`<div class="timelineNowCard"><strong>${String(e[3]).replace(/\s*ACTIVE\s*$/i,'')}</strong><small>${timelineSummaryText(e)}</small></div>`).join('');
      live.innerHTML=`<div class="timelineNowInner"><div class="timelineNowHead"><b>Active now</b><span>Auto-updates at the ${nextResetLocalLabel()} local reset</span></div>${cards?`<div class="timelineNowGrid">${cards}</div>`:'<div class="timelineNowEmpty">No tracked multi-day events are active right now.</div>'}</div>`;
    }
  }

function setupTimeline(){
    renderLocalTimeLabels();
    const timelinePanelState=[
      ['timelineCoverageDetails','sxs-timeline-panel-coverage'],
      ['recurringEventsDetails','sxs-timeline-panel-events'],
      ['ignisReferenceDetails','sxs-timeline-panel-ignis']
    ];
    timelinePanelState.forEach(([id,key])=>{
      const panel=$(id);
      if(!panel) return;
      let saved=null;
      try{ saved=localStorage.getItem(key); }catch(_){}
      panel.open=saved==='1';
      panel.addEventListener('toggle',()=>{try{localStorage.setItem(key,panel.open?'1':'0');}catch(_){}});
    });
    const filters=[['all','All'],['dungeon','Dungeons'],['class-advancement','Class'],['maps','Maps / Regions'],['fantomon','Fantomons'],['ancient-relic','Relics'],['feature','Features'],['event','Events']];
    $('timelineFilters').innerHTML=filters.map(([k,l])=>`<button data-filter="${k}" class="${k==='all'?'active':''}">${l}</button>`).join('');
    $('timelineFilters').addEventListener('click',e=>{const b=e.target.closest('button[data-filter]');if(!b)return;timelineFilter=b.dataset.filter;[...$('timelineFilters').children].forEach(x=>x.classList.toggle('active',x===b));renderTimeline();});
    $('showPast').addEventListener('change',renderTimeline);
    $('todayButton').addEventListener('click',()=>{const groups=[...$('timeline').querySelectorAll('.dayGroup')];const reset=currentResetIso();const target=groups.find(g=>g.classList.contains('today'))||groups.find(g=>g.dataset.date>=reset)||groups[0];if(target)target.scrollIntoView({behavior:'smooth',block:'center'});});
    renderTimeline();
    let timelineMinuteSignature='';
    const currentTimelineSignature=()=>{
      const boundary=currentResetIso();
      const active=timelineData.filter(e=>eventIsActive(e,boundary)).map(e=>`${e[0]}:${e[3]}`).join('|');
      return `${boundary}::${active}`;
    };
    timelineMinuteSignature=currentTimelineSignature();
    setInterval(()=>{
      if(document.hidden) return;
      renderLocalTimeLabels();
      const nextSignature=currentTimelineSignature();
      if(nextSignature!==timelineMinuteSignature){
        timelineMinuteSignature=nextSignature;
        renderTimeline();
      }
    },60_000);
  }

const S1_BUILD_CLASSES=['Berserker','Paladin','Archmage','Arcanist'];

const S2_BUILD_CLASSES=['Destroyer','Dominator','Conqueror','Guardian'];

const BUILD_CLASS_STORAGE_KEYS={s1:'sxs-build-class-s1',s2:'sxs-build-class-s2'};

const BUILD_SEASON_VIEW_STORAGE_KEY='sxs-build-season-view';

function buildSeasonKey(){ return 's2'; }

function buildClassesForSeason(){ return S2_BUILD_CLASSES; }

let currentBuildSeason='s2';

try{
    if(currentBuildSeason==='s1'){
      const savedSeason=localStorage.getItem(BUILD_SEASON_VIEW_STORAGE_KEY);
      if(savedSeason==='s1'||savedSeason==='s2') currentBuildSeason=savedSeason;
    }
  }catch(_){}

let currentClass='Conqueror';

try{
    const classes=buildClassesForSeason(currentBuildSeason);
    const savedClass=localStorage.getItem(BUILD_CLASS_STORAGE_KEYS[currentBuildSeason]) || (currentBuildSeason==='s2'?localStorage.getItem('sxs-build-class'):null);
    if(classes.includes(savedClass)) currentClass=savedClass;
  }catch(_){}

function buildHtmlS2(cls){
    if(cls==='Conqueror') return `
      <div class="guideSummary"><div><span>Elemental melee DPS</span><strong>Conqueror</strong><p>T4 pivots from the old Physical-first Berserker plan into Elemental damage, DEF ignore and repeatable attacks. Excellent in both bosses and dungeons.</p></div><p><b>Stat priority</b>ATK ≥ Elemental Mastery &gt; SPD on offensive main lines. Crit Rate → Crit DMG are the premium substats. Aim past 100% Crit because S2 PvE enemies carry Crit RES.</p></div>
      <div class="gearPanel"><div class="gearIntro"><span>Season 2 gearing</span><strong>Gear & stat priorities</strong><p>Keep large power upgrades, but protect excellent rolls for S2 affix inheritance. Physical Mastery becomes a niche old-build stat rather than the default.</p></div><div class="gearGrid"><div class="gearItem"><span>Main lines</span><p>Sword / Gauntlets / Boots: ATK ≥ Elemental Mastery &gt; SPD. Helmet / Chest: DEF ≥ Physical RES = Elemental RES &gt; HP.</p></div><div class="gearItem"><span>Best substats</span><p>Crit Rate% → Crit DMG% → Elemental Mastery / Accuracy% → SPD or HP/SPD-to-ATK conversion. ATK is useful but less scarce.</p></div><div class="gearItem"><span>Gem plan</span><p>Weapon: Obsidian &gt; Amethyst ≥ Ruby. Off-hand: Obsidian &gt; Amethyst ≥ Citrine. Boots: Amethyst &gt; Citrine. Armor: Moonstone. Helm: Citrine.</p></div><div class="gearItem"><span>Important breakpoint</span><p>S2 PvE enemies have about 18% Crit RES, so roughly 118% displayed Crit Rate is the practical 100%-crit target before dropping Crit support.</p></div></div></div>
      <div class="priorityPanel"><div class="priorityIntro"><span>Technique investment</span><strong>Only equipped Techniques</strong><p>Rank the techniques that actually occupy your standard Conqueror loadouts; swap-only utility stays in the build notes.</p></div><ol class="priorityList"><li><b>1</b><div><strong>Flickering Blade</strong><p>No cooldown, very high single-target ceiling, and it is equipped in every listed Conqueror build.</p></div></li><li><b>2</b><div><strong>Blade Storm</strong><p>Core T4 AoE and also equipped across every listed build.</p></div></li><li><b>3</b><div><strong>Flash Fire</strong><p>Reliable Elemental damage and a main-slot technique in dungeon, boss and PvP setups.</p></div></li><li><b>4</b><div><strong>Flame Aura</strong><p>Main-slot damage for the generic and boss builds. Darkness Descends remains the PvP/utility replacement shown below.</p></div></li></ol></div>
      <div class="priorityPanel"><div class="priorityIntro"><span>Charm investment</span><strong>Piercing Assault first</strong><p>These are all actually equipped in the listed builds. Soul Breaker and Soul Splash remain optional swaps, not core upgrade recommendations.</p></div><ol class="priorityList"><li><b>1</b><div><strong>Piercing Assault</strong><p>Primary T4 investment and equipped in every Conqueror build below.</p></div></li><li><b>2</b><div><strong>Tactical Adaptation</strong><p>Universal offensive/defensive value and equipped in every listed build.</p></div></li><li><b>3</b><div><strong>Insightful Eye</strong><p>Actually occupies a slot in every listed build until your S2 gear solves the Crit requirement.</p></div></li><li><b>4</b><div><strong>Indomitable Will / Blazing Clash</strong><p>Indomitable is the equipped dungeon/PvP safety slot; Blazing Clash is the equipped boss damage slot.</p></div></li></ol></div>
      <div class="buildGrid">
        <article class="buildCard"><header><div><h3>Generic / Dungeons</h3><p>Default all-content Elemental setup</p></div></header><div class="skillGroup"><span>Techniques</span><div><b>Flash Fire</b><b>Flame Aura</b><b>Flickering Blade</b><b>Blade Storm</b></div></div><div class="skillGroup"><span>Charms</span><div><b>Insightful Eye</b><b>Piercing Assault</b><b>Tactical Adaptation</b><b>Indomitable Will</b></div></div><ul><li><b>Offensive:</b> Indomitable Will → Soul Splash</li><li><b>Defensive/utility:</b> Flame Aura → Darkness Descends when mobility/dispel keeps you safer</li><li>Once Crit is solved, Insightful Eye → Soul Breaker</li></ul></article>
        <article class="buildCard"><header><div><h3>Boss / Dragon</h3><p>Single-target and long-fight damage</p></div></header><div class="skillGroup"><span>Techniques</span><div><b>Flame Aura</b><b>Blade Storm</b><b>Flash Fire</b><b>Flickering Blade</b></div></div><div class="skillGroup"><span>Charms</span><div><b>Insightful Eye</b><b>Piercing Assault</b><b>Tactical Adaptation</b><b>Blazing Clash</b></div></div><ul><li><b>Offensive:</b> high Crit → Insightful Eye → Crit Mastery</li><li><b>Defensive:</b> Blazing Clash → Indomitable Will</li><li>Nyxarchon is the safest raw-DPS lead Fantomon; Pandarial can front-load cooldowns later in S2</li></ul></article>
        <article class="buildCard"><header><div><h3>PvP / Mobility</h3><p>Dispel, reach and cheat-death</p></div></header><div class="skillGroup"><span>Techniques</span><div><b>Flash Fire</b><b>Darkness Descends</b><b>Flickering Blade</b><b>Blade Storm</b></div></div><div class="skillGroup"><span>Charms</span><div><b>Insightful Eye</b><b>Piercing Assault</b><b>Tactical Adaptation</b><b>Indomitable Will</b></div></div><ul><li><b>Offensive:</b> Crit-capped Insightful Eye → Soul Breaker</li><li><b>Defensive:</b> keep Indomitable Will; do not greed it away in serious PvP</li><li>Darkness Descends is preferred here over Flame Aura for movement + dispel</li></ul></article>
      </div><p class="buildSource">Research snapshot Aug 21, 2026 · <a href="https://www.prydwen.gg/sword-x-staff/guides/build-guide-conqueror" rel="noreferrer" target="_blank">Prydwen Conqueror ↗</a> · <a href="https://lootandwaifus.com/guides/sword-x-staff-how-to-play-duelist/" rel="noreferrer" target="_blank">Loot &amp; Waifus Duelist/Conqueror ↗</a></p>`;

    if(cls==='Guardian') return `
      <div class="guideSummary"><div><span>Tank / support / bruiser</span><strong>Guardian</strong><p>T4 finally gives Knight real taunt tools plus stronger Water/Light offense. The long-term identity is still protection: Block, DEF, shields, taunt control and party support.</p></div><p><b>Stat priority</b>Block is the premium substat. Sword/Boots value SPD heavily; defensive slots prioritize DEF, then HP/RES. Build damage only after the tank loop is stable.</p></div>
      <div class="gearPanel"><div class="gearIntro"><span>Season 2 gearing</span><strong>Gear & stat priorities</strong><p>Guardian has very different offensive and defensive slots. Do not flatten everything into one generic tank stat.</p></div><div class="gearGrid"><div class="gearItem"><span>Main lines</span><p>Sword: SPD &gt; ATK &gt; Physical Mastery &gt; Elemental Mastery. Gauntlets: DEF &gt; HP &gt; Physical/Elemental RES. Boots: SPD &gt; ATK &gt; Elemental/Physical Mastery.</p></div><div class="gearItem"><span>Best substats</span><p>Block Rate% → Block Rate + Block Efficiency → PvE/PvP DMG + DMG RES. Then flat DEF / SPD / HP and useful Crit.</p></div><div class="gearItem"><span>Gem plan</span><p>Weapon: Obsidian &gt; Amethyst ≥ Ruby. Off-hand: Moonstone &gt; Sapphire &gt; Citrine. Boots: Amethyst &gt; Citrine. Armor: Moonstone &gt; Sapphire/Beryl. Helm: Sapphire &gt; Citrine &gt; Beryl.</p></div><div class="gearItem"><span>Fantomon focus</span><p>Adult Aegiswing is the Guardian priority for tanking. Kels is excellent support (DEF down + dispel). Nyx adds damage/debuffs; Pandarial later adds opening-CD reduction and healing.</p></div></div></div>
      <div class="priorityPanel"><div class="priorityIntro"><span>Technique investment</span><strong>Swirling Blade first</strong><p>Current S2 Guardian testing consistently elevates Swirling Blade as the best T4 Technique investment because it works in the Water shell, shield builds and general PvE while still giving a shield.</p></div><ol class="priorityList"><li><b>1</b><div><strong>Swirling Blade</strong><p>The most reusable T4 damage Technique: strong single-target damage, Water synergy and a self-shield. It is also the first offensive flex into the dungeon tank bar.</p></div></li><li><b>2</b><div><strong>Valor Surge</strong><p>Long-lived party damage and cleanse utility; equipped in dungeon and Dragon/Chaos support.</p></div></li><li><b>3</b><div><strong>Heart of Challenge</strong><p>The core group-taunt slot in the default dungeon tank build.</p></div></li><li><b>4</b><div><strong>Luminous Shield</strong><p>Still central to the dungeon and reflect shells, though high-Block accounts can flex it more aggressively later.</p></div></li></ol></div>
      <div class="priorityPanel"><div class="priorityIntro"><span>Charm investment</span><strong>Soul Protection first</strong><p>Fresh S2 Guardian feedback is unusually consistent here: Soul Protection is the standout T4 Charm and remains useful across dungeons, Arena and Nexus-style team PvP.</p></div><ol class="priorityList"><li><b>1</b><div><strong>Soul Protection</strong><p>The best T4 Guardian investment: a massive opening shield that scales the whole shield/DEF loop and works in essentially every mode.</p></div></li><li><b>2</b><div><strong>Holy Aegis</strong><p>Universal DEF plus stronger DEF-based shields; excellent wherever Guardian is actually tanking.</p></div></li><li><b>3</b><div><strong>Iron Will</strong><p>Excellent damage reduction once Taunt is active, especially in dungeon and team-PvP tank bars.</p></div></li><li><b>4</b><div><strong>Oath of Vigil</strong><p>High-value group/PvP protection. One copy is already useful, so it ranks below the more universal personal-core investments.</p></div></li></ol></div>
      <div class="buildGrid">
        <article class="buildCard"><header><div><h3>Dungeon Tank</h3><p>Safest default party grid</p></div></header><div class="skillGroup"><span>Techniques</span><div><b>Valor Surge</b><b>Heart of Challenge</b><b>Luminous Shield</b><b>Desperate Protection</b></div></div><div class="skillGroup"><span>Charms</span><div><b>Iron Will</b><b>Holy Aegis</b><b>Block Awareness</b><b>Soul Protection</b></div></div><ul><li><b>Offensive:</b> Desperate Protection → Swirling Blade or Star Shattering Slash</li><li><b>Defensive:</b> Desperate Protection → Hamper Strike for more taunt uptime</li><li>If the party still folds, add Iron Fortress</li></ul></article>
        <article class="buildCard"><header><div><h3>Water / AoE</h3><p>Cold stacking with real damage</p></div></header><div class="skillGroup"><span>Techniques</span><div><b>Valor Surge</b><b>Swirling Blade</b><b>Lunarwater Threads</b><b>Raging Maelstrom</b></div></div><div class="skillGroup"><span>Charms</span><div><b>Frigid Aura</b><b>Defensive Assault</b><b>Frigid Glint</b><b>Potential Rebirth</b></div></div><ul><li><b>Offensive:</b> Potential Rebirth → Pursuit of Victory / high-investment Blade of Lament</li><li><b>Defensive:</b> keep Potential Rebirth or add a stronger tank charm when pushing deficits</li><li>Mostly AoE, but still respectable single-target damage</li></ul></article>
        <article class="buildCard"><header><div><h3>Dragon / Chaos Support</h3><p>Buff, cleanse and debuff support</p></div></header><div class="skillGroup"><span>Techniques</span><div><b>Valor Surge</b><b>Leap Attack</b><b>Holy Purification</b><b>Lunarwater Threads</b></div></div><div class="skillGroup"><span>Charms</span><div><b>Frigid Aura</b><b>Frigid Glint</b><b>Iron Fortress</b><b>Oath of Vigil</b></div></div><ul><li><b>Offensive:</b> no dispel needed → Holy Purification → Seismic Tide</li><li><b>Defensive:</b> retain Iron Fortress + Oath; Terragon lead if the team needs DMG reduction</li><li>Kels (adult) is excellent here for DEF down + dispel</li></ul></article>
        <article class="buildCard"><header><div><h3>Reflect / Solo PvE</h3><p>Old Tank &amp; Spank, still useful</p></div></header><div class="skillGroup"><span>Techniques</span><div><b>Valor Surge</b><b>Luminous Shield</b><b>Star Shattering Slash</b><b>Desperate Protection</b></div></div><div class="skillGroup"><span>Charms</span><div><b>Rebound</b><b>Holy Aegis</b><b>Block Mastery</b><b>Block Awareness</b></div></div><ul><li><b>Offensive:</b> enough Block → Block Awareness → Eye for an Eye</li><li><b>Defensive:</b> Luminous Shield → Guardian Ring / add Potential Rebirth</li><li>Pandarial can enable a more aggressive Light Sword Array variant later</li></ul></article>
      </div><p class="buildSource">Research snapshot Sep 2, 2026 · <a href="https://www.prydwen.gg/sword-x-staff/guides/build-guide-guardian" rel="noreferrer" target="_blank">Prydwen Guardian ↗</a></p>`;

    if(cls==='Destroyer') return `
      <div class="guideSummary"><div><span>Ranged elemental DPS</span><strong>Destroyer</strong><p>T4 is more specialized than Archmage: mixed Light/Wind/Fire handles general and boss content, pure Fire is the horde specialist, and Wind remains strong in PvP. Freeze is playable but less reliable.</p></div><p><b>Stat priority</b>ATK ≈ Elemental Mastery &gt; Crit &gt; SPD on Staff/Codex. Keep enough EM to avoid an underbuilt multiplier, but once EM is healthy, developed S2 accounts often gain more from flat ATK. Dummy-test close swaps.</p></div>
      <div class="gearPanel"><div class="gearIntro"><span>Season 2 gearing</span><strong>Gear & stat priorities</strong><p>Destroyer wants a balanced damage profile. EM supplies the elemental multiplier, but flat ATK keeps scaling every damaging Technique and becomes increasingly competitive once your EM pool is already strong.</p></div><div class="gearGrid"><div class="gearItem"><span>Main lines</span><p>Staff/Codex: ATK ≈ Elemental Mastery &gt; Crit &gt; SPD. Helmet/Chest: DEF/RES &gt; HP. Boots: ATK ≈ Elemental Mastery &gt; SPD. If two pieces are close, use the 50-round dummy test.</p></div><div class="gearItem"><span>Best substats</span><p>Crit Rate / Crit DMG &gt; ATK ≈ Elemental Mastery &gt; Accuracy &gt; SPD.</p></div><div class="gearItem"><span>Gem plan</span><p>Weapon &amp; Off-hand: Obsidian / Amethyst. Boots: Amethyst. Armor: Moonstone. Helm: Citrine; use Beryl/Sapphire mainly for conversion or power padding.</p></div><div class="gearItem"><span>Relic elements</span><p>Light is the safest general priority, Fire is excellent for horde content, and Wind is especially strong for PvP/control. Favor Affinity over Aegis on offensive relic slots.</p></div></div></div>
      <div class="priorityPanel"><div class="priorityIntro"><span>Technique investment</span><strong>Formation Breaker is #1</strong><p>Every ranked technique here is equipped in at least one listed Destroyer build; swap-only options stay in the card notes.</p></div><ol class="priorityList"><li><b>1</b><div><strong>Formation Breaker</strong><p>Universal party ATK support plus a chance to accelerate allies; appears in essentially every serious T4 setup.</p></div></li><li><b>2</b><div><strong>Thunder of Judgment</strong><p>Destroyer’s best T4 single-target nuke and it prioritizes large targets.</p></div></li><li><b>3</b><div><strong>Wind Blade Spiral</strong><p>Fast-cycling Wind damage; more efficient than older Hurricane-style options in sustained fights.</p></div></li><li><b>4</b><div><strong>Meteoric Flames</strong><p>Still a workhorse for both mixed AoE and pure Fire compositions.</p></div></li></ol></div>
      <div class="priorityPanel"><div class="priorityIntro"><span>Charm investment</span><strong>Universal first, Fire second</strong><p>Every ranked charm here is equipped in the builds below; Fire-specific pieces are ranked because they occupy the Fire Horde loadout.</p></div><ol class="priorityList"><li><b>1</b><div><strong>Rapid Cast</strong><p>Elemental Mastery plus opening cooldown acceleration—excellent across multiple Destroyer builds.</p></div></li><li><b>2</b><div><strong>Radiant Sear</strong><p>Core generic Destroyer damage proc and a staple of the Light/mixed setups.</p></div></li><li><b>3</b><div><strong>Fiery Burst</strong><p>The damage engine of the pure Fire horde build; scales hard with Crit frequency.</p></div></li><li><b>4</b><div><strong>Explosive Spirit</strong><p>Stacks Crit from Fire techniques and helps Fiery Burst trigger consistently. Mana Surge is the fallback.</p></div></li></ol></div>
      <div class="buildGrid">
        <article class="buildCard"><header><div><h3>General AoE</h3><p>Mixed Wind/Fire wave clear</p></div></header><div class="skillGroup"><span>Techniques</span><div><b>Formation Breaker</b><b>Howling Hurricane</b><b>Meteoric Flames</b><b>Wind Blade Spiral</b></div></div><div class="skillGroup"><span>Charms</span><div><b>Rapid Cast</b><b>Void Bubble</b><b>Cyclone Lament</b><b>Radiant Sear</b></div></div><ul><li><b>Offensive:</b> safe content → Void Bubble → Mana Surge / another damage charm</li><li><b>Defensive:</b> keep Void Bubble when pushing deficits</li><li>Cyclone Lament benefits from running two Wind techniques here</li></ul></article>
        <article class="buildCard"><header><div><h3>Boss / Single Target</h3><p>Default S2 boss setup</p></div></header><div class="skillGroup"><span>Techniques</span><div><b>Formation Breaker</b><b>Divine Wrath</b><b>Wind Blade Spiral</b><b>Thunder of Judgment</b></div></div><div class="skillGroup"><span>Charms</span><div><b>Rapid Cast</b><b>Void Bubble</b><b>Mana Surge</b><b>Radiant Sear</b></div></div><ul><li><b>Offensive:</b> Void Bubble → another damage charm when survival is irrelevant</li><li><b>Defensive:</b> Mana Surge → Overload Protection</li><li><b>Test slot:</b> Wind Blade Spiral, Meteoric Flames, or Wind's Delight can win depending on ranks and Radiant Sear proc rate; use a long dummy test</li></ul></article>
        <article class="buildCard"><header><div><h3>Fire Horde</h3><p>Best when enemy count is the problem</p></div></header><div class="skillGroup"><span>Techniques</span><div><b>Formation Breaker</b><b>Fiery Star Trail</b><b>Fireball</b><b>Meteoric Flames</b></div></div><div class="skillGroup"><span>Charms</span><div><b>Rapid Cast</b><b>Void Bubble</b><b>Explosive Spirit</b><b>Fiery Burst</b></div></div><ul><li><b>Offensive:</b> strong gear → Void Bubble → Radiant Sear / extra Fire offense</li><li><b>Defensive:</b> retain Void Bubble; Fiery Rejuvenation is a sustain alternative in long Fire fights</li><li>Crit Rate is especially important because Fiery Burst procs from Fire crits</li></ul></article>
        <article class="buildCard"><header><div><h3>Freeze / Water</h3><p>Playable control variant, not the boss meta</p></div></header><div class="skillGroup"><span>Techniques</span><div><b>Flowing Doom</b><b>Water Assault</b><b>Frosty Nova</b><b>Ice Spike</b></div></div><div class="skillGroup"><span>Charms</span><div><b>Rapid Cast</b><b>Void Bubble</b><b>Shattering Ice</b><b>Water to Ice</b></div></div><ul><li><b>Offensive/control:</b> Ice Spike → Aqua Vortex first slot for more Freeze setup</li><li><b>Defensive:</b> keep Void Bubble</li><li>Boss Freeze is limited until the white gauge is broken, so do not over-invest just for bosses</li></ul></article>
      </div><p class="buildSource">Research snapshot Aug 31, 2026 · <a href="https://www.prydwen.gg/sword-x-staff/guides/build-guide-destroyer" rel="noreferrer" target="_blank">Prydwen Destroyer ↗</a> · <a href="https://www.reddit.com/r/SwordxStaff_Official/comments/1vdjbo4/better_destroyer_builds/" rel="noreferrer" target="_blank">S2 community testing ↗</a> · <a href="https://lootandwaifus.com/guides/sword-x-staff-how-to-play-sorcerer/" rel="noreferrer" target="_blank">Loot &amp; Waifus ↗</a></p>`;

    if(cls==='Dominator') return `
      <div class="guideSummary dominatorGuideSummary"><div><span>Dark DPS / healer / support</span><div class="dominatorHeadingRow"><strong>Dominator</strong><div class="dominatorModeTabs" role="group" aria-label="Dominator build role"><button type="button" data-dominator-mode="dps">DPS</button><button type="button" data-dominator-mode="heals">Heals</button></div></div><p>T4 is a difficult DPS tier for Sage because Erosion needs high Effect Hit Rate and summons are easier to kill. Healing/support gets meaningful upgrades and remains the most reliable role.</p></div><p><b>Stat priority</b>DPS: Effect Hit Rate ≥ Elemental Mastery ≥ ATK &gt; SPD. Healer: SPD &gt; Effect Hit Rate &gt; Elemental Mastery &gt; ATK. Do not use one gear priority for both jobs.</p></div>
      <div class="gearPanel"><div class="gearIntro"><span>Season 2 gearing</span><strong>Two gear profiles</strong><p>Dominator is the class where a DPS preset and a healer preset are genuinely worth maintaining.</p></div><div class="gearGrid"><div class="gearItem"><span>DPS main lines</span><p>Staff/Orb: Effect Hit Rate ≥ Elemental Mastery ≥ ATK &gt; SPD. Boots: Elemental Mastery &gt; ATK &gt; SPD. Defensive slots: DEF/RES &gt; HP.</p></div><div class="gearItem"><span>Healer main lines</span><p>Staff/Orb: SPD &gt; Effect Hit Rate &gt; Elemental Mastery &gt; ATK. Helmet/Chest favor HP first, then DEF/RES. Boots: SPD &gt; Elemental Mastery &gt; ATK.</p></div><div class="gearItem"><span>Substats</span><p>DPS: Crit+Accuracy / Crit+Crit DMG / ailment damage, then EHR and conversions. Healer: DMG RES + Healing, Block packages, Healing Boost, then SPD/HP.</p></div><div class="gearItem"><span>Gem plan</span><p>Healer: Amethyst weapon, Amber off-hand/helm/boots, Moonstone armor. DPS: Obsidian weapon/off-hand, Citrine helm, Moonstone armor, Amethyst boots.</p></div></div></div>
      <div class="priorityPanel" data-dominator-role="heals"><div class="priorityIntro"><span>Core support investment</span><strong>Phantom Light is mandatory</strong><p>These are all equipped in the Healing/Group or Carry Support builds below, not standalone wishlist recommendations.</p></div><ol class="priorityList"><li><b>1</b><div><strong>Phantom Light</strong><p>Healing boost plus overheal-to-shield conversion. The must-have Dominator healer Charm.</p></div></li><li><b>2</b><div><strong>Rejuvenating Rain</strong><p>Repeatable single-target heal and a clean answer to low-HP allies.</p></div></li><li><b>3</b><div><strong>Mantra of Blessings</strong><p>High-value carry buff for co-op and scoring content when raw survival is already handled.</p></div></li><li><b>4</b><div><strong>Decoy Clone</strong><p>Excellent hypercarry/scoring utility when your team can exploit the clone connection and positioning.</p></div></li></ol></div>
      <div class="priorityPanel" data-dominator-role="dps"><div class="priorityIntro"><span>Core DPS investment</span><strong>EHR decides the build</strong><p>These are all equipped in the listed Single Target or AoE/Erosion builds; situational alternates remain in the build notes.</p></div><ol class="priorityList"><li><b>1</b><div><strong>Dark Starburst</strong><p>Reliable multi-hit single-target damage that does not require Erosion stacks to function.</p></div></li><li><b>2</b><div><strong>Shadow of Termination</strong><p>Key single-target Dark finisher/core technique.</p></div></li><li><b>3</b><div><strong>Shadow Erosion</strong><p>Core DPS Charm when your Effect Hit Rate is high enough to land the status reliably.</p></div></li><li><b>4</b><div><strong>Linked Misfortune</strong><p>Standard Erosion/Dark damage package piece across both ST and AoE builds.</p></div></li></ol></div>
      <div class="buildGrid">
        <article class="buildCard" data-dominator-role="dps"><header><div><h3>Single Target</h3><p>Reliable hybrid before perfect EHR</p></div></header><div class="skillGroup"><span>Techniques</span><div><b>Dark Bullet</b><b>Dark Starburst</b><b>Chaos Rune</b><b>Shadow of Termination</b></div></div><div class="skillGroup"><span>Charms</span><div><b>Shadow Vengeance</b><b>Night's Blessing</b><b>Shadow Erosion</b><b>Linked Misfortune</b></div></div><ul><li><b>Offensive:</b> high EHR → Chaos Rune → Mana Blast</li><li><b>Defensive:</b> retain Shadow Vengeance</li><li>Frenzy Totem + Soul Pact Resonance is another offensive variant depending on rarity/stats</li></ul></article>
        <article class="buildCard" data-dominator-role="dps"><header><div><h3>AoE / Erosion</h3><p>Still the old Arcanist AoE core</p></div></header><div class="skillGroup"><span>Techniques</span><div><b>Mana Blast</b><b>Dark Bullet</b><b>Abyssal Hand</b><b>Shadow Impact</b></div></div><div class="skillGroup"><span>Charms</span><div><b>Shadow Vengeance</b><b>Night's Blessing</b><b>Shadow Erosion</b><b>Linked Misfortune</b></div></div><ul><li><b>Offensive:</b> once survival is safe, Shadow Vengeance → Soul Pact Resonance / offense</li><li><b>Defensive:</b> keep Shadow Vengeance</li><li>T4 adds no new dedicated AoE technique/charm package for Dominator</li></ul></article>
        <article class="buildCard" data-dominator-role="heals"><header><div><h3>Healing / Group</h3><p>Best all-around Dominator role</p></div></header><div class="skillGroup"><span>Techniques</span><div><b>Waterling Summon</b><b>Rejuvenating Rain</b><b>Radiant Restoration</b><b>Frenzy Totem</b></div></div><div class="skillGroup"><span>Charms</span><div><b>Phantom Light</b><b>Healing Mastery</b><b>Overhealing</b><b>FLEX</b></div></div><ul><li><b>Offensive/support:</b> FLEX → Mantra of Blessings when the party is stable</li><li><b>Defensive:</b> FLEX → Resurrection if allies die, or Shadow Vengeance if you die</li><li>Need more healing: Frenzy Totem → Healing Touch</li></ul></article>
        <article class="buildCard" data-dominator-role="heals"><header><div><h3>Carry Support</h3><p>Scoring / hypercarry utility</p></div></header><div class="skillGroup"><span>Core pieces</span><div><b>Mantra of Blessings</b><b>Decoy Clone</b><b>Rejuvenating Rain</b><b>Radiant Restoration</b></div></div><div class="skillGroup"><span>Support shell</span><div><b>Phantom Light</b><b>Healing Mastery</b><b>Resurrection / Overhealing</b><b>Flex</b></div></div><ul><li><b>Offensive/support:</b> favor Mantra + Decoy when a stronger DPS is carrying score</li><li><b>Defensive:</b> remove the greed slot for Resurrection / Shadow Vengeance</li><li>Pandarial later in S2 is a strong hybrid lead because opening CD reduction can enable earlier healing</li></ul></article>
      </div><p class="buildSource">Research snapshot Aug 21, 2026 · <a href="https://www.prydwen.gg/sword-x-staff/guides/build-guide-dominator" rel="noreferrer" target="_blank">Prydwen Dominator ↗</a> · <a href="https://lootandwaifus.com/guides/sword-x-staff-how-to-play-sage/" rel="noreferrer" target="_blank">Loot &amp; Waifus Sage/Dominator ↗</a></p>`;

    return '';
  }

const DOMINATOR_BUILD_MODE_KEY='sxs-build-dominator-mode';

let dominatorBuildMode='dps';

try{
    const saved=localStorage.getItem(DOMINATOR_BUILD_MODE_KEY);
    if(saved==='dps'||saved==='heals') dominatorBuildMode=saved;
  }catch(_){}

function applyDominatorBuildMode(){
    const root=$('buildContent');
    if(!root || currentClass!=='Dominator') return;
    root.querySelectorAll('[data-dominator-mode]').forEach(btn=>{
      const active=btn.dataset.dominatorMode===dominatorBuildMode;
      btn.classList.toggle('active',active);
      btn.setAttribute('aria-pressed',String(active));
    });
    root.querySelectorAll('[data-dominator-role]').forEach(el=>{
      el.hidden=el.dataset.dominatorRole!==dominatorBuildMode;
    });
  }

function buildHtml(cls){ return buildSeasonKey()==='s1'?buildHtmlS1(cls):buildHtmlS2(cls); }

function syncBuildSeason(){
    const nextSeason=buildSeasonKey();
    const classes=buildClassesForSeason(nextSeason);
    if(nextSeason!==currentBuildSeason || !classes.includes(currentClass)){
      currentBuildSeason=nextSeason;
      let saved=null;
      try{ saved=localStorage.getItem(BUILD_CLASS_STORAGE_KEYS[nextSeason]) || (nextSeason==='s2'?localStorage.getItem('sxs-build-class'):null); }catch(_){}
      currentClass=classes.includes(saved)?saved:classes[0];
    }
    return classes;
  }

function renderBuilds(){
    const classes=syncBuildSeason();
    const s1=currentBuildSeason==='s1';
    if($('buildSeasonLabel')) $('buildSeasonLabel').textContent=s1?'Season 1 · Tier III build guide':'Season 2 · Tier IV build guide';
    if($('buildSeasonNote')) $('buildSeasonNote').textContent=s1
      ? 'Showing the live Season 1 / Tier III meta. This section switches to Tier IV automatically at the Aug 30, 6:00 AM Pacific reset.'
      : 'Season 2 / Tier IV is live. Your selected class tab is remembered separately for each season.';
    $('classTabs').innerHTML=classes.map(c=>`<button class="${c===currentClass?'active':''}" data-class="${c}">${c}</button>`).join('');
    $('buildContent').innerHTML=buildHtml(currentClass);
    applyDominatorBuildMode();
  }

let buildsInitialized=false;

function setupBuilds(){
    $('classTabs').addEventListener('click',e=>{
      const b=e.target.closest('button[data-class]');
      if(!b)return;
      if(b.dataset.class===currentClass)return;
      currentClass=b.dataset.class;
      try{localStorage.setItem(BUILD_CLASS_STORAGE_KEYS[currentBuildSeason],currentClass);}catch(_){}
      renderBuilds();
    });
    renderBuilds();
    buildsInitialized=true;
    setInterval(()=>{ if(!document.hidden && buildsInitialized && buildSeasonKey()!==currentBuildSeason) renderBuilds(); },60_000);
  }

const S1_BUILD_CLASSES_LIVE=['Berserker','Paladin','Archmage','Arcanist'];

const S2_BUILD_CLASSES_LIVE=['Destroyer','Dominator','Conqueror','Guardian'];

const BUILD_SEASON_STORAGE_KEYS={s1:'sxs-build-class-s1',s2:'sxs-build-class-s2'};

const buildHtmlT4Live=buildHtmlS2;

function liveBuildSeason(){ return 's2'; }

function liveBuildClasses(){ return S2_BUILD_CLASSES_LIVE; }

function liveBuildStorageKey(){ return BUILD_SEASON_STORAGE_KEYS[liveBuildSeason()]; }

function renderBuildSeasonToggle(){
    const toggle=$('buildSeasonToggle');
    if(!toggle) return;
    const forcedS2=buildSeasonKey()==='s2';
    const season=liveBuildSeason();
    toggle.classList.toggle('s2Only',forcedS2);
    toggle.querySelectorAll('button[data-build-season]').forEach(btn=>{
      const key=btn.dataset.buildSeason;
      btn.hidden=forcedS2&&key==='s1';
      const active=key===season;
      btn.classList.toggle('active',active);
      btn.setAttribute('aria-pressed',String(active));
    });
  }

function selectBuildSeason(key){
    if(buildSeasonKey()==='s2') key='s2';
    if(key!=='s1'&&key!=='s2') return;
    currentBuildSeason=key;
    try{localStorage.setItem(BUILD_SEASON_VIEW_STORAGE_KEY,key);}catch(_){}
    currentClass='';
    normalizeLiveBuildClass();
    renderBuilds();
    setSection('builds');
  }

function normalizeLiveBuildClass(){
    const list=liveBuildClasses();
    if(list.includes(currentClass)) return;
    let saved=null;
    try{
      saved=localStorage.getItem(liveBuildStorageKey());
      if(!saved && liveBuildSeason()==='s2') saved=localStorage.getItem('sxs-build-class');
    }catch(_){}
    currentClass=list.includes(saved)?saved:list[0];
  }

buildHtml=function(cls){ return liveBuildSeason()==='s1'?buildHtmlS1(cls):buildHtmlT4Live(cls); };

const BUILD_TEMPLATE_CACHE=new Map();

let buildTemplateWarmKey='';

function buildTemplateForClass(cls){
    const key=`${liveBuildSeason()}|${cls}`;
    let template=BUILD_TEMPLATE_CACHE.get(key);
    if(!template){
      template=document.createElement('template');
      template.innerHTML=buildHtml(cls);
      BUILD_TEMPLATE_CACHE.set(key,template);
    }
    return template;
  }

function syncBuildClassTabs(list){
    const tabs=$('classTabs');
    const signature=`${liveBuildSeason()}|${list.join('|')}`;
    if(tabs.dataset.buildClassSignature!==signature){
      tabs.innerHTML=list.map(c=>`<button type="button" role="tab" aria-selected="${c===currentClass}" class="${c===currentClass?'active':''}" data-class="${c}">${c}</button>`).join('');
      tabs.dataset.buildClassSignature=signature;
    }else{
      tabs.querySelectorAll('button[data-class]').forEach(btn=>{
        const active=btn.dataset.class===currentClass;
        btn.classList.toggle('active',active);
        btn.setAttribute('aria-selected',String(active));
      });
    }
  }

function warmBuildTemplates(list){
    const key=`${liveBuildSeason()}|${list.join('|')}`;
    if(buildTemplateWarmKey===key) return;
    buildTemplateWarmKey=key;
    const work=()=>list.forEach(cls=>buildTemplateForClass(cls));
    if('requestIdleCallback' in window) requestIdleCallback(work,{timeout:500});
    else setTimeout(work,0);
  }

renderBuilds=function(){
    if(buildSeasonKey()==='s2') currentBuildSeason='s2';
    normalizeLiveBuildClass();
    renderBuildSeasonToggle();
    const list=liveBuildClasses();
    const s1=liveBuildSeason()==='s1';
    const label=document.querySelector('#buildsSection .sectionHeading span');
    const note=document.querySelector('#buildsSection .sectionHeading>p');
    if(label) label.textContent=s1?'Season 1 · Tier III build guide':'Season 2 · Tier IV build guide';
    if(note) note.textContent=s1
      ? 'Showing the live Season 1 / Tier III meta. This switches to Tier IV automatically at the Aug 30, 6:00 AM Pacific reset.'
      : 'Season 2 / Tier IV is live. Your selected class tab is remembered separately for each season.';
    syncBuildClassTabs(list);
    const host=$('buildContent');
    const template=buildTemplateForClass(currentClass);
    host.replaceChildren(template.content.cloneNode(true));
    applyDominatorBuildMode();
    /* BUILD_VISUAL_STABILITY_V2
       The recording exposed several post-render stages after a class click. Finish all of them
       synchronously so the browser gets only the final class layout. META first creates the final
       activity cards. Rich fingerprints those headings and creates the priority pair/stats panel.
       META then runs once more to re-anchor its activity selector after the newly-created priority
       pair for Guardian/Dominator. Roll populates the stats panel and Hero performs the final
       two-column summary/reflow last. */
    if(typeof window.__applyBuildMetaNow==='function') window.__applyBuildMetaNow();
    if(typeof window.__applyBuildRichNow==='function') window.__applyBuildRichNow();
    if(typeof window.__applyBuildMetaNow==='function') window.__applyBuildMetaNow();
    if(typeof window.__applyBuildRollNow==='function') window.__applyBuildRollNow();
    if(typeof window.__applyBuildHeroNow==='function') window.__applyBuildHeroNow();
    warmBuildTemplates(list);
  };

setupBuilds=function(){
    null?.addEventListener?.('click',e=>{
      const b=e.target.closest('button[data-build-season]');
      if(!b)return;
      e.preventDefault();
      e.stopPropagation();
      selectBuildSeason(b.dataset.buildSeason);
    });
    $('classTabs').addEventListener('click',e=>{
      const b=e.target.closest('button[data-class]');
      if(!b)return;
      if(b.dataset.class===currentClass)return;
      currentClass=b.dataset.class;
      try{localStorage.setItem(liveBuildStorageKey(),currentClass);}catch(_){}
      renderBuilds();
    });
    $('buildContent').addEventListener('click',e=>{
      const b=e.target.closest('button[data-dominator-mode]');
      if(!b || currentClass!=='Dominator') return;
      dominatorBuildMode=b.dataset.dominatorMode==='heals'?'heals':'dps';
      try{localStorage.setItem(DOMINATOR_BUILD_MODE_KEY,dominatorBuildMode);}catch(_){}
      applyDominatorBuildMode();
    });
    renderBuilds();
    let lastBuildSeasonTick=liveBuildSeason();
    setInterval(()=>{
      if(document.hidden||!buildsInitialized) return;
      const beforeClass=currentClass;
      const beforeSeason=lastBuildSeasonTick;
      normalizeLiveBuildClass();
      const afterSeason=liveBuildSeason();
      if(beforeClass!==currentClass || beforeSeason!==afterSeason) renderBuilds();
      lastBuildSeasonTick=afterSeason;
    },60_000);
  };
function initializeBuildsIfNeeded(){
    if(buildsInitialized) return;
    buildsInitialized=true;
    renderBuilds();
  }
function setSection(name){
    const map={timeline:'timelineSection',builds:'buildsSection',companions:'companionsSection',calculator:'calculatorSection'};
    if(!map[name]) name='timeline';
    const activeSection=document.querySelector('.sectionSwitch button[data-section].active')?.dataset.section;
    if(activeSection===name && !$(map[name]).hidden) return;
    document.querySelectorAll('.siteSection').forEach(s=>s.hidden=true);
    $(map[name]).hidden=false;
    document.querySelectorAll('.sectionSwitch button[data-section]').forEach(b=>{const active=b.dataset.section===name;b.classList.toggle('active',active);b.setAttribute('aria-selected',String(active));});
    try{ localStorage.setItem(SECTION_STORAGE_KEY,name); }catch(_){}
    window.scrollTo({top:0,behavior:'smooth'});
    if(name==='builds') initializeBuildsIfNeeded();
    if(name==='calculator') openCalculator();
  }
function updateThemeButton(){ $('themeToggle').textContent=document.documentElement.dataset.theme==='dark'?'☀':'☾'; }
loadTheme();
setupNavigation({$,setSection,saveState:saveTheme,updateThemeButton});
let initialSection='timeline';
try{const saved=localStorage.getItem(SECTION_STORAGE_KEY);if(['timeline','builds','companions','calculator'].includes(saved))initialSection=saved;}catch(_){}
setSection(initialSection);
setupTimeline();
setupBuilds();
