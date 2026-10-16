// Manual check against deployed rules; no chat profiles/messages are created.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
const config=JSON.parse(await readFile('chat-config.json','utf8'));
const identity='https://identitytoolkit.googleapis.com/v1/accounts:';
const response=await fetch(`${identity}signUp?key=${encodeURIComponent(config.apiKey)}`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({returnSecureToken:true})});
assert.equal(response.status,200,'anonymous test identity');
const guest=await response.json();
const root=`projects/${config.projectId}/databases/(default)/documents`;
const api=`https://firestore.googleapis.com/v1/${root}`;
const headers={'Content-Type':'application/json',Authorization:`Bearer ${guest.idToken}`};
try{
  assert.equal((await fetch(`${api}/rooms/lobby`)).status,403,'unauthenticated metadata reads are denied');
  const meta=await fetch(`${api}/rooms/lobby`,{headers});
  assert.ok([200,404].includes(meta.status),'signed-in visitors can follow lobby cleanup state');
  const escalation=await fetch(`${api}/chatOwners/${guest.localId}`,{method:'PATCH',headers,body:JSON.stringify({fields:{enabled:{booleanValue:true}}})});
  assert.equal(escalation.status,403,'visitors cannot grant themselves owner access');
  const clear=await fetch(`https://firestore.googleapis.com/v1/projects/${config.projectId}/databases/(default)/documents:commit`,{method:'POST',headers,body:JSON.stringify({writes:[{update:{name:`${root}/rooms/lobby`,fields:{previousClearedAt:{nullValue:null},clearedBy:{stringValue:guest.localId},canUndo:{booleanValue:true}}},updateTransforms:[{fieldPath:'clearedAt',setToServerValue:'REQUEST_TIME'},{fieldPath:'updatedAt',setToServerValue:'REQUEST_TIME'}]}]})});
  assert.equal(clear.status,403,'anonymous visitors cannot clear the lobby');
  console.log('Live rules: visitors can read cleanup state; owner-role escalation and lobby cleanup are denied.');
}finally{
  const removed=await fetch(`${identity}delete?key=${encodeURIComponent(config.apiKey)}`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({idToken:guest.idToken})});
  assert.equal(removed.status,200,'temporary test identity removed');
}
