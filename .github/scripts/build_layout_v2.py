from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

css=r'''
/* BUILD_LAYOUT_V2 */
#buildContent>.gearPanel{display:none!important}
.guideSummary.buildSummaryCompact{grid-template-columns:minmax(0,.82fr) minmax(0,1.18fr);align-items:stretch}
.buildQuickStats{border-left:1px solid var(--line);padding-left:20px;display:flex;flex-direction:column;justify-content:center;gap:8px;min-width:0}
.buildQuickStats .quickTitle{color:var(--ink);letter-spacing:.08em;text-transform:uppercase;font-size:9px;font-weight:900}
.buildQuickStats .quickRule{color:var(--muted);font-size:10px;line-height:1.45;margin:0}
.quickGearGrid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:6px 16px}
.quickGearRow{display:grid;grid-template-columns:max-content 1fr;gap:8px;align-items:baseline;border-top:1px solid color-mix(in srgb,var(--line) 72%,transparent);padding-top:6px;min-width:0}
.quickGearRow b{color:var(--green);font-size:9px;white-space:nowrap}
.quickGearRow span{color:var(--body-text);font-size:9px;line-height:1.35;text-transform:none;letter-spacing:0;font-weight:650;min-width:0}
.priorityPair{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin-top:10px;align-items:stretch}
.priorityPair>.priorityPanel{margin-top:0;grid-template-columns:1fr;height:100%}
.priorityPair .priorityIntro{padding:17px 18px;border-bottom:1px solid var(--line)}
.priorityPair .priorityIntro>strong{font-size:16px}
.priorityPair .priorityIntro p{font-size:10px}
.priorityPair .priorityList{grid-template-columns:1fr}
.priorityPair .priorityList li{border-left:0;border-bottom:1px solid var(--line);padding:13px 15px}
.priorityPair .priorityList li:last-child{border-bottom:0}
.priorityPair .priorityList li:nth-child(n+3){border-bottom:1px solid var(--line)}
.priorityPair .priorityList li:last-child{border-bottom:0}
@media(max-width:760px){
  .guideSummary.buildSummaryCompact{grid-template-columns:1fr}
  .buildQuickStats{border-left:0;border-top:1px solid var(--line);padding:14px 0 0}
  .quickGearGrid{grid-template-columns:1fr}
  .priorityPair{grid-template-columns:1fr}
}
'''

js=r'''
// BUILD_LAYOUT_V2
function buildPriorityPanelHtml(kind,title,desc,items){
  return `<div class="priorityPanel"><div class="priorityIntro"><span>${kind}</span><strong>${title}</strong><p>${desc}</p></div><ol class="priorityList">${items.map((x,i)=>`<li><b>${i+1}</b><div><strong>${x[0]}</strong><p>${x[1]}</p></div></li>`).join('')}</ol></div>`;
}
function splitBerserkerPriorities(root){
  if(currentBuildSeason!=='s1' || currentClass!=='Berserker') return;
  const panel=[...root.children].find(el=>el.classList&&el.classList.contains('priorityPanel'));
  if(!panel || !/Core investment/i.test(panel.querySelector('.priorityIntro span')?.textContent||'')) return;
  const technique=buildPriorityPanelHtml('Core technique investment','Eclipse Slash first','Rank the techniques that actually stay equipped across the standard Season 1 Berserker builds.',[
    ['Eclipse Slash','Six-hit single-target nuke and the most universal T3 damage technique.'],
    ['Sunset Sword','Equipped in every listed Berserker build and a reliable multi-hit core.'],
    ['Lion Combo','Another universal multi-hit slot that feeds the T3 damage loop well.'],
    ["Hunter's Judgment / Flame Aura / Darkness Descends",'Content slot: grouping for general PvE, damage for bosses, mobility/dispel for PvP.']
  ]);
  const charm=buildPriorityPanelHtml('Core charm investment','Blade of Judgment first','Keep technique and charm investment separate so upgrade priorities are easier to follow.',[
    ['Blade of Judgment','The defining T3 charm and the main reason multi-hit techniques scale so well.'],
    ['Insightful Eye','Reliable Crit support across PvE, Dragon and PvP.'],
    ['Indomitable Will','The default survival investment and the safest general-purpose defensive slot.'],
    ['Blade Siphon / Blazing Clash / Frame of Battles','Content slot: sustain for general PvE, damage for bosses, PvP utility for arena.']
  ]);
  const holder=document.createElement('div');
  holder.innerHTML=technique+charm;
  panel.replaceWith(...holder.children);
}
function parseGearRows(mainText){
  if(!mainText) return [];
  const rows=[];
  mainText.split(/\.\s+/).map(x=>x.trim().replace(/\.$/,'' )).filter(Boolean).forEach(part=>{
    const idx=part.indexOf(':');
    if(idx<0) return;
    const slots=part.slice(0,idx).trim().split(/\s*\/\s*/).filter(Boolean);
    const stats=part.slice(idx+1).trim();
    slots.forEach(slot=>rows.push([slot,stats]));
  });
  return rows;
}
function polishBuildLayout(){
  const root=document.getElementById('buildContent');
  if(!root || !root.children.length) return;
  splitBerserkerPriorities(root);
  const guide=root.querySelector(':scope > .guideSummary');
  const gear=root.querySelector(':scope > .gearPanel');
  if(guide && gear && !guide.querySelector('.buildQuickStats')){
    const existing=guide.children[1];
    const rule=existing?.textContent?.replace(/^Quick stat rule\s*/i,'').trim()||'';
    const items=[...gear.querySelectorAll('.gearItem')];
    const main=items.find(x=>/^Main lines$/i.test(x.querySelector('span')?.textContent.trim()||''));
    const rows=parseGearRows(main?.querySelector('p')?.textContent.trim()||'');
    const quick=document.createElement('div');
    quick.className='buildQuickStats';
    quick.innerHTML=`<div class="quickTitle">Quick stats</div>${rule?`<p class="quickRule">${rule}</p>`:''}<div class="quickGearGrid">${rows.map(r=>`<div class="quickGearRow"><b>${r[0]}</b><span>${r[1]}</span></div>`).join('')}</div>`;
    existing?.replaceWith(quick);
    guide.classList.add('buildSummaryCompact');
    gear.hidden=true;
  }
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
(function setupBuildLayoutPolish(){
  const root=document.getElementById('buildContent');
  if(!root) return;
  let queued=false;
  const run=()=>{queued=false;polishBuildLayout();};
  const observer=new MutationObserver(()=>{if(!queued){queued=true;queueMicrotask(run);}});
  observer.observe(root,{childList:true,subtree:false});
  polishBuildLayout();
})();
'''

if '/* BUILD_LAYOUT_V2 */' not in s:
    pos=s.find('</style>')
    if pos<0: raise SystemExit('style close not found')
    s=s[:pos]+css+'\n'+s[pos:]

if '// BUILD_LAYOUT_V2\nfunction buildPriorityPanelHtml' not in s:
    pos=s.rfind('</script>')
    if pos<0: raise SystemExit('script close not found')
    s=s[:pos]+'\n'+js+'\n'+s[pos:]

p.write_text(s,encoding='utf-8')
