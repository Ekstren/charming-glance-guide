// Offline catalog refresh. Curated acquisitions and stable collection IDs survive.
import {readFileSync,writeFileSync} from 'node:fs';
const input=process.argv[2];
if(!input)throw Error('Usage: node scripts/import_relic_catalog.mjs snapshot.json');
const read=p=>JSON.parse(readFileSync(p,'utf8').replace(/^\uFEFF/,''));
const current=read('data/relics.json'),incoming=read(input);
if(!Array.isArray(incoming))throw Error('Expected a catalog array');
const entries=new Map(current.map(r=>[r.id,r]));
const rarities={R:'Rare',SR:'Epic',SSR:'Legendary',Rainbow:'Mythic'};
const seen=new Set();
for(const item of incoming){
 if(!/^treasure_\d+$/.test(item.id)||seen.has(item.id)||!rarities[item.rarity]||typeof item.name!=='string'||!/^treasure_\d+\.png$/.test(item.icon))throw Error(`Invalid or duplicate entry: ${item.id}`);
 seen.add(item.id);
 const previous=entries.get(item.id);
 entries.set(item.id,{id:item.id,name:item.name,image:`assets/relics/${item.icon}`,rarity:rarities[item.rarity],element:item.element||null,region:item.region||null,zone:null,destinyFruit:null,sources:[],sourceUrl:'https://lootandwaifus.com/sword-x-staff-relics-database/',visible:false,...previous});
 // Keep existing identity corrections as well as acquisition research. Review new
 // upstream labels explicitly rather than silently replacing local corrections.
 if(previous&&previous.name!==item.name)console.warn(`Review upstream name: ${item.id}: ${previous.name} -> ${item.name}`);
}
writeFileSync('data/relics.json',JSON.stringify([...entries.values()].sort((a,b)=>a.name.localeCompare(b.name)),null,2)+'\n');
console.log(`${entries.size} entries; ${entries.size-current.length} added. Review local images and acquisition coverage.`);
