import catalog from '../data/relics.json';
const relics=catalog.filter(relic=>relic.visible===true);
const STORAGE_KEY='sxs-relics-owned-v1';
const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const regions=['Verdantglade','Cinder Ridge','Aqualis','Loong Haven I','Loong Haven II'];
const rarityOrder=['Mythic','Legendary','Epic','Rare','Uncommon','Common'];
const regionOf=relic=>relic.region==='Loong Haven'?(relic.pool||'other'):regions.find(region=>relic.region===region)||'other';
export function romanNumber(text){let total=0,previous=0;for(const c of [...text].reverse()){const n={I:1,V:5,X:10,L:50,C:100,D:500,M:1000}[c]||0;total+=n<previous?-n:n;previous=n;}return total;}
export function compareZones(a,b){
 if(a==='Zone not verified')return b===a?0:1;if(b==='Zone not verified')return -1;
 const rank=value=>{const order=['Verdantglade','Cinder Ridge','Aqualis','Loong Haven'];const i=order.findIndex(r=>value.startsWith(r));return i<0?order.length:i;};
 const ap=a.match(/^(.*?)\s+([IVXLCDM]+|\d+)$/),bp=b.match(/^(.*?)\s+([IVXLCDM]+|\d+)$/);
 return rank(a)-rank(b)||(ap&&bp&&ap[1]===bp[1]?(Number(ap[2])||romanNumber(ap[2]))-(Number(bp[2])||romanNumber(bp[2])):a.localeCompare(b,undefined,{numeric:true}));
}
export function matchesFilters(relic,filters,owned){
 const has=owned.has(relic.id);
 return (!filters.region||filters.region==='all'||regionOf(relic)===filters.region)&&(!filters.zone||filters.zone==='all'||(filters.zone==='unknown'?!relic.zone:relic.zone===filters.zone))&&(!filters.targets||(!has&&relic.destinyFruit===true))&&(!filters.rarity||relic.rarity===filters.rarity)&&(!filters.element||relic.element===filters.element)&&(!filters.search||relic.name.toLowerCase().includes(filters.search.toLowerCase().trim()))&&(filters.targets||filters.status==='all'||(filters.status==='owned'?has:!has))&&(filters.targets||filters.fruit==='all'||(filters.fruit==='yes'?relic.destinyFruit===true:filters.fruit==='no'?relic.destinyFruit===false:relic.destinyFruit==null));
}
function readOwned(){const raw=localStorage.getItem(STORAGE_KEY);if(!raw)return new Set();const value=JSON.parse(raw);if(!Array.isArray(value)||value.some(v=>typeof v!=='string'))throw new Error('Invalid collection');return new Set(value);}
function safeLink(url){try{const u=new URL(url);return /^https?:$/.test(u.protocol)?esc(u.href):'';}catch{return '';}}
let initialized=false;
export function initialize(){
 if(initialized)return;
 const host=document.getElementById('relicsContent');
 let owned=new Set(),storageProblem='',dialogTrigger=null;
 try{owned=readOwned();}catch{storageProblem='Saved collection could not be read. Changes will try to save again on this device.';}
 const filters={region:'Verdantglade',zone:'all',targets:false,rarity:'',element:'',search:'',status:'all',fruit:'all',sort:'zone'};
 const options=field=>[...new Set(relics.map(r=>r[field]).filter(Boolean))].sort().map(v=>`<option value="${esc(v)}">${esc(v)}</option>`).join('');
 host.innerHTML=`<header class="relicHeader"><div><h1>Relic Gallery</h1><p>Your collection, one region at a time.</p></div><div class="relicProgress"><strong id="relicProgressText"></strong><progress id="relicProgressBar" aria-label="Overall relic collection"></progress><small>Saved in this browser on this device</small></div></header>
 <nav class="relicRegionTabs" id="relicRegionTabs" aria-label="Relic regions">${[...regions,'other','all'].map(region=>`<button type="button" data-relic-region="${region}" aria-pressed="${region===filters.region}">${region==='other'?'Other':region==='all'?'All regions':region==='Loong Haven II'?'Loong Haven II · Upcoming':region}</button>`).join('')}</nav>
 <div class="relicModes" role="group" aria-label="Relic view"><button type="button" data-relic-mode="collection" aria-pressed="true">Collection</button><button type="button" data-relic-mode="targets" aria-pressed="false">Destiny Fruit Targets</button></div>
 <div class="relicFilters"><label>Search by name<input type="search" id="relicSearch" placeholder="Find a relic…"></label><label>Rarity<select id="relicRarity"><option value="">All rarities</option>${options('rarity')}</select></label><label>Element<select id="relicElement"><option value="">All elements</option>${options('element')}</select></label><label>Collection<select id="relicStatus"><option value="all">All</option><option value="owned">Owned</option><option value="missing">Missing</option></select></label><label>Destiny Fruit<select id="relicFruit"><option value="all">All</option><option value="yes">Destiny Fruit obtainable</option><option value="no">Not Destiny Fruit obtainable</option><option value="unknown">Not yet verified</option></select></label><label>Fruit zone<select id="relicZone" aria-label="Destiny Fruit drop zone"></select></label><label id="relicSortLabel" hidden>Sort zones<select id="relicSort"><option value="zone">Normal zone order</option><option value="missing">Most missing relics</option></select></label><button type="button" id="relicReset">Reset filters</button></div>
 <p id="relicTargetNote" hidden>Missing relics with verified Destiny Fruit availability. Zone counts follow your current filters.</p><p class="relicStorageStatus" id="relicStorageStatus" role="status"></p><p id="relicResultsStatus" role="status" aria-live="polite"></p><div id="relicGroups"></div><p class="relicCoverage">Through Loong Haven Relic II · ${relics.length} relics. Numbered zones refer specifically to Destiny Fruit drops.</p><p class="relicFootnote">Select a relic for acquisition details. Missing drop-zone information does not mean a relic is unobtainable.</p>
 <dialog id="relicDialog" aria-labelledby="relicDialogTitle"><button type="button" id="relicDialogClose" aria-label="Close relic details" autofocus>✕</button><div id="relicDialogContent"></div></dialog>`;
 const $=id=>host.querySelector(`#${id}`);
 function card(r){
  const rarity=(r.rarity||'unknown').toLowerCase().replace(/[^a-z]/g,'');
  return `<article class="relicCard${owned.has(r.id)?' isOwned':''}" data-relic-id="${esc(r.id)}" data-rarity="${rarity}"><button class="relicCardOpen" type="button" data-relic-open="${esc(r.id)}" aria-label="View ${esc(r.name)} acquisition details"><span class="relicImage">${r.image?`<img src="${esc(r.image)}" alt="${esc(r.name)}" width="120" height="120" loading="lazy">`:'<span aria-label="Icon unavailable">◇</span>'}</span><strong class="relicName">${esc(r.name)}</strong><span class="relicTileMeta">${esc(r.element||'')}</span>${r.zone?`<span class="relicTileZone">Fruit: ${esc(r.zone)}</span>`:''}</button><label class="relicOwned"><input type="checkbox" data-owned="${esc(r.id)}" ${owned.has(r.id)?'checked':''} aria-label="Own ${esc(r.name)}"><span>Owned</span></label></article>`;
 }
 function openDetails(id,trigger){
  const r=relics.find(item=>item.id===id);if(!r)return;
  const fruit=r.destinyFruit===true?`Destiny Fruit zone: ${r.zone||'exact zone not yet verified'}`:r.destinyFruit===false?'Cannot be obtained with Destiny Fruits through targeted exploration, according to the linked guide.':'';
  const sourceLinks=[...new Set([r.sourceUrl,...(r.sources||[]).map(s=>s.url)].filter(Boolean))].map(url=>{const href=safeLink(url);return href?`<a href="${href}" target="_blank" rel="noreferrer">${esc(new URL(url).hostname)} ↗</a>`:'';}).join(' · ');
  $('relicDialogContent').innerHTML=`<div class="relicDialogHero" data-rarity="${esc((r.rarity||'').toLowerCase())}"><span class="relicImage">${r.image?`<img src="${esc(r.image)}" alt="${esc(r.name)}" width="120" height="120">`:'◇'}</span><div><span class="relicDialogRarity">${esc(r.rarity||'Rarity not verified')}</span><h2 id="relicDialogTitle">${esc(r.name)}</h2></div></div><dl class="relicMetadata"><div><dt>Element</dt><dd>${esc(r.element||'Not verified')}</dd></div><div><dt>Region</dt><dd>${esc(r.region||'Not verified')}</dd></div>${r.pool?`<div><dt>Relic pool</dt><dd>${esc(r.pool)}</dd></div>`:''}${r.zone?`<div><dt>Destiny Fruit zone</dt><dd>${esc(r.zone)}</dd></div>`:''}<div><dt>Collection</dt><dd>${owned.has(r.id)?'Owned':'Missing'}</dd></div></dl><div class="relicDetails">${r.affinity?`<p class="relicAffinity">${esc(r.affinity)}</p>`:""}${r.effect?`<h3>Effect</h3><p class="relicEffect">${esc(r.effect)}</p>`:""}${r.set?.members?.length?`<h3>${esc(r.set.name||"Relic set")} <span class="relicSetCount">${r.set.members.filter(member=>owned.has(member.id)).length} / ${r.set.members.length} owned</span></h3><div class="relicSetMembers">${r.set.members.map(member=>`<span class="${owned.has(member.id)?"isOwned":""}">${esc(member.name)}${owned.has(member.id)?" ✓":""}</span>`).join("")}</div>`:""}${r.setBonuses?.length?`<h3>Set stats</h3><dl class="relicSetBonuses">${r.setBonuses.map(bonus=>`<div><dt>${esc(bonus.label)}</dt><dd>${esc(bonus.effect)}</dd></div>`).join("")}</dl>`:""}<h3>Acquisition</h3>${fruit?`<p class="relicFruitInfo">${esc(fruit)}</p>`:''}<ul>${(r.sources||[]).map(s=>`<li><strong>${esc(s.type)}</strong>${s.location?`: ${esc(s.location)}`:''}${s.notes?` — ${esc(s.notes)}`:''}</li>`).join('')||'<li>Additional acquisition details are not listed yet.</li>'}</ul>${r.notes?`<p>${esc(r.notes)}</p>`:''}${sourceLinks?`<p class="relicSources">Sources: ${sourceLinks}</p>`:''}</div>`;
  dialogTrigger=trigger;$('relicDialog').showModal();
 }
 function renderZones(){
  const inRegion=relics.filter(r=>filters.region==='all'||regionOf(r)===filters.region);
  const zones=[...new Set(inRegion.map(r=>r.zone).filter(Boolean))].sort(compareZones);
  const values=['all',...zones,...(inRegion.some(r=>!r.zone)?['unknown']:[])];
  $('relicZone').innerHTML=values.map(zone=>{const label=zone==='all'?'All zones':zone==='unknown'?'No fruit zone listed':filters.region==='all'?zone:zone.replace(filters.region+' ','');return `<option value="${esc(zone)}">${esc(label)}</option>`;}).join('');
  $('relicZone').value=filters.zone;
 }
 function render(){
  const count=relics.filter(r=>owned.has(r.id)).length,pct=relics.length?Math.round(count/relics.length*1000)/10:0;
  $('relicProgressText').textContent=`${count} / ${relics.length} owned · ${pct}%`;$('relicProgressBar').max=relics.length||1;$('relicProgressBar').value=count;
  $('relicStorageStatus').textContent=storageProblem;$('relicStorageStatus').hidden=!storageProblem;
  $('relicTargetNote').hidden=!filters.targets;$('relicSortLabel').hidden=!filters.targets;
  $('relicStatus').disabled=filters.targets;$('relicFruit').disabled=filters.targets;
  $('relicStatus').value=filters.targets?'missing':filters.status;$('relicFruit').value=filters.targets?'yes':filters.fruit;
  host.querySelectorAll('[data-relic-mode]').forEach(b=>b.setAttribute('aria-pressed',String((b.dataset.relicMode==='targets')===filters.targets)));
  host.querySelectorAll('[data-relic-region]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.relicRegion===filters.region)));
  $('relicZone').value=filters.zone;
  const shown=relics.filter(r=>matchesFilters(r,filters,owned)),groups=new Map();
  shown.forEach(r=>{const group=filters.targets?r.zone||'Zone not verified':r.rarity||'Rarity unverified';if(!groups.has(group))groups.set(group,[]);groups.get(group).push(r);});
  const missing=items=>items.filter(r=>!owned.has(r.id)).length;
  const rarityRank=value=>{const i=rarityOrder.indexOf(value);return i<0?rarityOrder.length:i;};
  const entries=[...groups].sort(([a,aa],[b,bb])=>filters.targets?((filters.sort==='missing'?missing(bb)-missing(aa):0)||compareZones(a,b)):rarityRank(a)-rarityRank(b)||a.localeCompare(b));
  const regionLabel=filters.region==='all'?'All regions':filters.region==='other'?'Other':filters.region;
  $('relicResultsStatus').textContent=`${regionLabel}${filters.region==='Loong Haven II'?' · Upcoming':''} · ${shown.length} ${filters.targets?'missing Destiny Fruit targets':'relics shown'}${filters.targets?` across ${groups.size} ${groups.size===1?'zone':'zones'}`:''}.`;
  $('relicGroups').innerHTML=entries.length?entries.map(([group,items])=>`<section class="${filters.targets?'relicZone':'relicRarityGroup'}"><header><h2>${esc(group)}</h2><span>${missing(items)} missing · ${items.length} ${filters.targets?'targets':'shown'}</span></header><div class="relicGrid">${items.map(card).join('')}</div></section>`).join(''):'<p class="relicEmpty">No relics match these filters.</p>';
 }
 host.addEventListener('input',e=>{if(e.target.id==='relicSearch'){filters.search=e.target.value;render();}});
 host.addEventListener('change',e=>{
  const id=e.target.dataset.owned;
  if(id){e.target.checked?owned.add(id):owned.delete(id);try{localStorage.setItem(STORAGE_KEY,JSON.stringify([...owned]));storageProblem='';}catch{storageProblem='Your browser could not save the collection. Changes remain for this visit only.';}render();const next=[...host.querySelectorAll('[data-owned]')].find(el=>el.dataset.owned===id);(next||$('relicResultsStatus')).focus({preventScroll:true});return;}
  const fields={relicZone:'zone',relicRarity:'rarity',relicElement:'element',relicStatus:'status',relicFruit:'fruit',relicSort:'sort'};if(fields[e.target.id]){filters[fields[e.target.id]]=e.target.value;render();}
 });
 host.addEventListener('click',e=>{
  const region=e.target.closest('[data-relic-region]');if(region){filters.region=region.dataset.relicRegion;filters.zone='all';renderZones();render();}
  const mode=e.target.closest('[data-relic-mode]');if(mode){filters.targets=mode.dataset.relicMode==='targets';render();}
  const tile=e.target.closest('[data-relic-open]');if(tile)openDetails(tile.dataset.relicOpen,tile);
  if(e.target.id==='relicDialogClose')$('relicDialog').close();
  if(e.target.id==='relicReset'){Object.assign(filters,{zone:'all',rarity:'',element:'',search:'',status:'all',fruit:'all',sort:'zone'});['relicSearch','relicRarity','relicElement'].forEach(id=>$(id).value='');$('relicSort').value='zone';render();}
 });
 $('relicDialog').addEventListener('close',()=>{if(dialogTrigger?.isConnected)dialogTrigger.focus({preventScroll:true});else $('relicResultsStatus').focus({preventScroll:true});});
 $('relicDialog').addEventListener('click',e=>{if(e.target===$('relicDialog')){const r=e.target.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)e.target.close();}});
 window.addEventListener('storage',e=>{if(e.key===STORAGE_KEY||e.key===null){try{owned=readOwned();storageProblem='';render();}catch{storageProblem='Collection changes in another tab could not be read.';render();}}});
 $('relicResultsStatus').tabIndex=-1;
 renderZones();render();initialized=true;
}
