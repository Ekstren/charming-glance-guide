let loading;
function loadGoogleIdentity(){
 if(window.google?.accounts?.oauth2)return Promise.resolve(window.google.accounts.oauth2);
 if(loading)return loading;
 loading=new Promise((resolve,reject)=>{
  const script=document.createElement('script');script.src='https://accounts.google.com/gsi/client';script.async=true;
  const fail=()=>{clearTimeout(timeout);script.remove();loading=null;reject(new Error('Google sign-in could not load. Check your connection and try again.'));};
  const timeout=setTimeout(fail,15000);
  script.onload=()=>{clearTimeout(timeout);if(window.google?.accounts?.oauth2)resolve(window.google.accounts.oauth2);else fail();};script.onerror=fail;document.head.append(script);
 });
 return loading;
}
// Prepare when owner controls open; requesting the popup stays inside the click gesture.
export async function prepareGoogleOwnerSignIn(clientId){
 if(typeof clientId!=='string'||!clientId.endsWith('.apps.googleusercontent.com'))throw new Error('Google owner sign-in is not configured yet.');
 const oauth=await loadGoogleIdentity();
 let pending;
 const finish=(error,token)=>{if(!pending)return;const request=pending;pending=null;clearTimeout(request.timeout);if(error)request.reject(error);else request.resolve(token);};
 const client=oauth.initTokenClient({client_id:clientId,scope:'openid email profile',include_granted_scopes:false,
  callback:response=>{if(response?.access_token&&!response.error)finish(null,response.access_token);else finish(new Error('Google sign-in was not authorized. Please try again.'));},
  error_callback:error=>finish(new Error(error?.type==='popup_failed_to_open'?'Your browser blocked Google sign-in. Allow the sign-in window and try again.':'Google sign-in did not finish. Please try again.'))});
 return ()=>{
  if(pending)return Promise.reject(new Error('Google sign-in is already in progress.'));
  return new Promise((resolve,reject)=>{pending={resolve,reject,timeout:setTimeout(()=>finish(new Error('Google sign-in timed out. Please try again.')),90000)};try{client.requestAccessToken({prompt:'select_account'});}catch(error){finish(error);}});
 };
}
