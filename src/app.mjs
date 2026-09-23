import { timelineData } from './timeline-data.mjs';
import { setupNavigation } from './navigation.mjs';
import { isoAddDays } from './time.mjs';
import { S1_END } from './season-clock.mjs';
import { localShortDateTimeLabel,nextResetLocalLabel } from './display-time.mjs';
import './timeline-patches.mjs';
import {openGuide} from './guide-loader.mjs';
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

function setSection(name){
    const map={timeline:'timelineSection',builds:'buildsSection',companions:'companionsSection',relics:'relicsSection',calculator:'calculatorSection'};
    if(!map[name]) name='timeline';
    const activeSection=document.querySelector('.sectionSwitch button[data-section].active')?.dataset.section;
    if(activeSection===name && !$(map[name]).hidden) return;
    document.querySelectorAll('.siteSection').forEach(s=>s.hidden=true);
    $(map[name]).hidden=false;
    document.querySelectorAll('.sectionSwitch button[data-section]').forEach(b=>{const active=b.dataset.section===name;b.classList.toggle('active',active);b.setAttribute('aria-selected',String(active));});
    try{ localStorage.setItem(SECTION_STORAGE_KEY,name); }catch(_){}
    window.scrollTo({top:0,behavior:'smooth'});
    if(name==='builds'||name==='companions'||name==='relics') openGuide(name);
    if(name==='calculator') openCalculator();
  }
function updateThemeButton(){ $('themeToggle').textContent=document.documentElement.dataset.theme==='dark'?'☀':'☾'; }
loadTheme();
setupNavigation({$,setSection,saveState:saveTheme,updateThemeButton});
let initialSection='timeline';
try{const saved=localStorage.getItem(SECTION_STORAGE_KEY);if(['timeline','builds','companions','relics','calculator'].includes(saved))initialSection=saved;}catch(_){}
setSection(initialSection);
setupTimeline();
