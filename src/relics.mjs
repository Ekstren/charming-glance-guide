import catalog from '../data/relics.json';
// The maintained visibility allowlist ends at Loong Haven Relic II.
const relics=catalog.filter(relic=>relic.visible===true);
const STORAGE_KEY='sxs-relics-owned-v1';
const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const regions=['Verdantglade','Cinder Ridge','Aqualis','Loong Haven','Aethyris','Hapadi'];
export function romanNumber(text){let total=0,previous=0;for(const c of [...text].reverse()){const n={I:1,V:5,X:10,L:50,C:100,D:500,M:1000}[c]||0;total+=n<previous?-n:n;previous=n;}return total;}
export function compareZones(a,b){
 if(a==='Zone not verified')return b===a?0:1;if(b==='Zone not verified')return -1;
 const rank=value=>{const i=regions.findIndex(r=>value.startsWith(r));return i<0?regions.length:i;};
 const ap=a.match(/^(.*?)\s+([IVXLCDM]+|\d+)$/),bp=b.match(/^(.*?)\s+([IVXLCDM]+|\d+)$/);
 return rank(a)-rank(b)||(ap&&bp&&ap[1]===bp[1]?(Number(ap[2])||romanNumber(ap[2]))-(Number(bp[2])||romanNumber(bp[2])):a.localeCompare(b,undefined,{numeric:true}));
}
export function matchesFilters(relic,filters,owned){
 const has=owned.has(relic.id);
 return (!filters.targets||(!has&&relic.destinyFruit===true))&&(!filters.rarity||relic.rarity===filters.rarity)&&(!filters.element||relic.element===filters.element)&&(!filters.search||relic.name.toLowerCase().includes(filters.search.toLowerCase().trim()))&&(filters.targets||filters.status==='all'||(filters.status==='owned'?has:!has))&&(filters.targets||filters.fruit==='all'||(filters.fruit==='yes'?relic.destinyFruit===true:filters.fruit==='no'?relic.destinyFruit===false:relic.destinyFruit==null));
}
function readOwned(){const raw=localStorage.getItem(STORAGE_KEY);if(!raw)return new Set();const value=JSON.parse(raw);if(!Array.isArray(value)||value.some(v=>typeof v!=='string'))throw new Error('Invalid collection');return new Set(value);}
function safeLink(url){try{const u=new URL(url);return /^https?:$/.test(u.protocol)?esc(u.href):'';}catch{return '';}}
let initialized=false;
export function initialize(){
 if(initialized)return;
 const host=document.getElementById('relicsContent');
 let owned=new Set(),storageProblem='';
 try{owned=readOwned();}catch{storageProblem='Saved collection could not be read. Changes will try to save again on this device.';}
 const filters={targets:false,rarity:'',element:'',search:'',status:'all',fruit:'all',sort:'zone'};
 const options=field=>[...new Set(relics.map(r=>r[field]).filter(Boolean))].sort().map(v=>`<option value="${esc(v)}">${esc(v)}</option>`).join('');
 host.innerHTML=`<header class="relicHeader"><div><h1>Relics</h1><p>Track your collection and find your next Destiny Fruit destination.</p></div><div class="relicProgress"><strong id="relicProgressText"></strong><progress id="relicProgressBar" aria-label="Overall relic collection"></progress><small>Saved in this browser on this device</small></div></header>
 <p class="relicCoverage">Through Loong Haven Relic II: ${relics.length} relics · ${relics.filter(r=>r.zone).length} exact zones verified · ${relics.filter(r=>r.destinyFruit==null).length} Destiny Fruit routes still unverified. Later releases are hidden.</p><div class="relicModes" role="group" aria-label="Relic view"><button type="button" data-relic-mode="collection" aria-pressed="true">All relics</button><button type="button" data-relic-mode="targets" aria-pressed="false">Destiny Fruit Targets</button></div>
 <div class="relicFilters"><label>Search by name<input type="search" id="relicSearch" placeholder="Find a relic…"></label><label>Rarity<select id="relicRarity"><option value="">All rarities</option>${options('rarity')}</select></label><label>Element<select id="relicElement"><option value="">All elements</option>${options('element')}</select></label><label>Collection<select id="relicStatus"><option value="all">All</option><option value="owned">Owned</option><option value="missing">Missing</option></select></label><label>Destiny Fruit<select id="relicFruit"><option value="all">All</option><option value="yes">Destiny Fruit obtainable</option><option value="no">Not Destiny Fruit obtainable</option><option value="unknown">Not yet verified</option></select></label><label>Sort zones<select id="relicSort"><option value="zone">Normal zone order</option><option value="missing">Most missing relics</option></select></label><button type="button" id="relicReset">Reset filters</button></div>
 <p id="relicTargetNote" hidden>Missing relics with verified Destiny Fruit availability. Zone counts follow your current filters.</p><p class="relicStorageStatus" id="relicStorageStatus" role="status"></p><p id="relicResultsStatus" role="status" aria-live="polite"></p><div id="relicGroups"></div><p class="relicFootnote">Expand a relic for acquisition details and source links. Unverified zones and Destiny Fruit availability are labeled separately; they are not assumed to be unavailable.</p>`;
 const $=id=>host.querySelector(`#${id}`);
 function card(r){
  const fruit=r.destinyFruit===true?`Destiny Fruit zone: ${r.zone||'exact zone not yet verified'}`:r.destinyFruit===false?'Cannot be obtained with Destiny Fruits through targeted exploration, according to the linked guide.':'Destiny Fruit availability has not yet been verified.';
  const sourceLinks=[...new Set([r.sourceUrl,...(r.sources||[]).map(s=>s.url)].filter(Boolean))].map(url=>{const href=safeLink(url);return href?`<a href="${href}" target="_blank" rel="noreferrer">${esc(new URL(url).hostname)} ↗</a>`:'';}).join(' · ');
  return `<article class="relicCard${owned.has(r.id)?' isOwned':''}" data-relic-id="${esc(r.id)}"><details><summary><span class="relicImage">${r.image?`<img src="${esc(r.image)}" alt="${esc(r.name)}" width="72" height="72" loading="lazy">`:'<span aria-label="Icon unavailable">◇</span>'}</span><span class="relicIdentity"><strong>${esc(r.name)}</strong><span class="relicBadges"><span>${esc(r.rarity||'Rarity not verified')}</span><span>${esc(r.element||'Element not verified')}</span></span><span class="relicLocation">${esc(r.region||'Region not verified')} · ${esc(r.zone||'Zone not verified')}</span><span class="relicSourceSummary">${esc((r.sources||[]).map(s=>s.type).filter((v,i,a)=>a.indexOf(v)===i).join(' · ')||'Sources not yet verified')}</span><span class="relicExpand">Acquisition details</span></span></summary><div class="relicDetails"><p>${esc(fruit)}</p><ul>${(r.sources||[]).map(s=>`<li><strong>${esc(s.type)}</strong>${s.location?`: ${esc(s.location)}`:''}${s.notes?` — ${esc(s.notes)}`:''}</li>`).join('')||'<li>Acquisition sources not yet verified.</li>'}</ul>${r.notes?`<p>${esc(r.notes)}</p>`:''}${sourceLinks?`<p class="relicSources">Sources: ${sourceLinks}</p>`:''}</div></details><label class="relicOwned"><input type="checkbox" data-owned="${esc(r.id)}" ${owned.has(r.id)?'checked':''} aria-label="Own ${esc(r.name)}"><span>${owned.has(r.id)?'Owned':'Missing'}</span></label></article>`;
 }
 function render(){
  const count=relics.filter(r=>owned.has(r.id)).length,pct=relics.length?Math.round(count/relics.length*1000)/10:0;
  $('relicProgressText').textContent=`${count} / ${relics.length} owned · ${pct}%`;$('relicProgressBar').max=relics.length||1;$('relicProgressBar').value=count;
  $('relicStorageStatus').textContent=storageProblem;$('relicStorageStatus').hidden=!storageProblem;
  $('relicTargetNote').hidden=!filters.targets;
  $('relicStatus').disabled=filters.targets;$('relicFruit').disabled=filters.targets;
  $('relicStatus').value=filters.targets?'missing':filters.status;$('relicFruit').value=filters.targets?'yes':filters.fruit;
  host.querySelectorAll('[data-relic-mode]').forEach(b=>b.setAttribute('aria-pressed',String((b.dataset.relicMode==='targets')===filters.targets)));
  const shown=relics.filter(r=>matchesFilters(r,filters,owned)),groups=new Map();
  shown.forEach(r=>{const zone=r.zone||'Zone not verified';if(!groups.has(zone))groups.set(zone,[]);groups.get(zone).push(r);});
  const missing=items=>items.filter(r=>!owned.has(r.id)).length;
  const entries=[...groups].sort(([a,aa],[b,bb])=>(filters.sort==='missing'?missing(bb)-missing(aa):0)||compareZones(a,b));
  const expanded=new Set([...host.querySelectorAll('.relicCard details[open]')].map(el=>el.closest('[data-relic-id]').dataset.relicId));
  $('relicResultsStatus').textContent=`${shown.length} ${filters.targets?'missing Destiny Fruit targets':'relics shown'} across ${groups.size} ${groups.size===1?'zone':'zones'}.`;
  $('relicGroups').innerHTML=entries.length?entries.map(([zone,items])=>`<section class="relicZone"><header><h2>${esc(zone)}</h2><span>${missing(items)} missing · ${items.length} ${filters.targets?'targets':'shown'}</span></header><div class="relicGrid">${items.sort((a,b)=>a.name.localeCompare(b.name)).map(card).join('')}</div></section>`).join(''):'<p class="relicEmpty">No relics match these filters.</p>';
  host.querySelectorAll('.relicCard').forEach(el=>{if(expanded.has(el.dataset.relicId))el.querySelector('details').open=true;});
 }
 host.addEventListener('input',e=>{if(e.target.id==='relicSearch'){filters.search=e.target.value;render();}});
 host.addEventListener('change',e=>{
  const id=e.target.dataset.owned;
  if(id){e.target.checked?owned.add(id):owned.delete(id);try{localStorage.setItem(STORAGE_KEY,JSON.stringify([...owned]));storageProblem='';}catch{storageProblem='Your browser could not save the collection. Changes remain for this visit only.';}render();const next=[...host.querySelectorAll('[data-owned]')].find(el=>el.dataset.owned===id);(next||$('relicResultsStatus')).focus({preventScroll:true});return;}
  const fields={relicRarity:'rarity',relicElement:'element',relicStatus:'status',relicFruit:'fruit',relicSort:'sort'};if(fields[e.target.id]){filters[fields[e.target.id]]=e.target.value;render();}
 });
 host.addEventListener('click',e=>{const mode=e.target.closest('[data-relic-mode]');if(mode){filters.targets=mode.dataset.relicMode==='targets';render();}if(e.target.id==='relicReset'){Object.assign(filters,{rarity:'',element:'',search:'',status:'all',fruit:'all',sort:'zone'});['relicSearch','relicRarity','relicElement'].forEach(id=>$(id).value='');$('relicSort').value='zone';render();}});
 window.addEventListener('storage',e=>{if(e.key===STORAGE_KEY||e.key===null){try{owned=readOwned();storageProblem='';render();}catch{storageProblem='Collection changes in another tab could not be read.';render();}}});
 $('relicResultsStatus').tabIndex=-1;
 render();initialized=true;
}
