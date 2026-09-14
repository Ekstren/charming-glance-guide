// Capture the shell URL while its classic script is executing (also supports file://).
const base=document.currentScript.src;
const definitions={builds:['Builds','SxsBuilds'],companions:['Companions','SxsCompanions']};
const pending=new Map(),ready=new Set();
export async function openGuide(name){
 if(ready.has(name))return;
 const section=document.getElementById(`${name}Section`);
 let status=section.querySelector('.guideLoadStatus');
 if(!status){status=document.createElement('div');status.className='guideLoadStatus';status.setAttribute('role','status');section.prepend(status);}
 const content=[...section.children].filter(el=>el!==status);
 const busy=value=>{section.setAttribute('aria-busy',String(value));content.forEach(el=>{el.inert=value;});};
 busy(true);status.hidden=false;status.textContent=`Loading ${definitions[name][0].toLowerCase()}…`;
 if(!pending.has(name))pending.set(name,new Promise((resolve,reject)=>{
  const script=document.createElement('script');
  const url=new URL(`${name}-section.js`,base);url.searchParams.set('v',GUIDE_BUILD_IDS[name]);
  script.src=url;script.async=true;
  script.onload=()=>{try{
   const api=window[definitions[name][1]];
   if(typeof api?.initialize!=='function')throw new Error('Guide did not initialize');
   api.initialize();ready.add(name);resolve();
  }catch(error){script.remove();reject(error);}};
  script.onerror=()=>{script.remove();reject(new Error('Guide download failed'));};
  document.head.append(script);
 }).catch(error=>{pending.delete(name);throw error;}));
 try{
  await pending.get(name);section.dataset.guideReady='true';status.hidden=true;busy(false);
 }catch(error){
  section.setAttribute('aria-busy','false');
  status.textContent=`Could not load ${definitions[name][0].toLowerCase()}. Check your connection and try again. `;
  const retry=document.createElement('button');retry.type='button';retry.textContent='Retry';
  retry.addEventListener('click',()=>openGuide(name));status.append(retry);
 }
}
