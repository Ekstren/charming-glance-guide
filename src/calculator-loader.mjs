// Classic-script chunks also work when the static site is opened through file://.
const chunkUrl=new URL('calculator.js',document.currentScript.src);
chunkUrl.searchParams.set('v',CALCULATOR_BUILD_ID);
let pending=null,api=null;
function status(message,retry=false){
 const host=document.getElementById('calculatorLoadStatus');
 host.replaceChildren(document.createTextNode(message));host.hidden=!message;
 if(retry){const button=document.createElement('button');button.type='button';button.textContent='Retry';button.addEventListener('click',()=>openCalculator());host.append(' ',button);}
}
function busy(value){
 const section=document.getElementById('calculatorSection');
 section.setAttribute('aria-busy',String(value));
 section.querySelector('.calculatorLayout').inert=value;
 section.querySelector('.calculatorJumpNav').inert=value;
}
function load(){
 if(api)return Promise.resolve(api);
 if(pending)return pending;
 pending=new Promise((resolve,reject)=>{
  const script=document.createElement('script');script.src=chunkUrl;script.async=true;
  script.onload=()=>{try{const loaded=window.SxsCalculator;if(!loaded?.initialize)throw new Error('Calculator did not initialize');loaded.initialize();api=loaded;resolve(api);}catch(error){script.remove();reject(error);}};
  script.onerror=()=>{script.remove();reject(new Error('Calculator download failed'));};
  document.head.append(script);
 }).catch(error=>{pending=null;throw error;});
 return pending;
}
export async function openCalculator(){
 busy(true);status('Loading calculator…');
 try{
  const calculator=await load();
  document.getElementById('calculatorSection').dataset.calculatorReady='true';
  status('');busy(false);
  // Leaving the tab during download must not start a hidden solve or move focus.
  if(!document.getElementById('calculatorSection').hidden)calculator.activate();
 }catch(error){busy(true);document.getElementById('calculatorSection').setAttribute('aria-busy','false');status('Could not load the calculator. Check your connection and try again.',true);}
}
