// Run manually after configuring Firebase. Creates two setup profiles and messages.
import assert from 'node:assert/strict';
import {createServer} from 'node:http';
import {readFile, mkdir} from 'node:fs/promises';
import path from 'node:path';
import {chromium} from 'playwright';

const root=process.cwd();
const config=JSON.parse(await readFile('chat-config.json','utf8'));
assert.ok(config.apiKey && config.projectId,'Configure Firebase before running this check');
const types={'.html':'text/html','.js':'text/javascript','.css':'text/css','.json':'application/json','.svg':'image/svg+xml','.png':'image/png'};
const server=createServer(async(req,res)=>{
  const file=path.resolve(root,'.'+(new URL(req.url,'http://localhost').pathname==='/'?'/index.html':decodeURIComponent(new URL(req.url,'http://localhost').pathname)));
  if(!file.startsWith(root+path.sep)){res.writeHead(403);res.end();return;}
  try{res.writeHead(200,{'Content-Type':types[path.extname(file)]||'application/octet-stream'});res.end(await readFile(file));}
  catch{res.writeHead(404);res.end();}
});
await new Promise(done=>server.listen(0,'127.0.0.1',done));
const base=`http://localhost:${server.address().port}`;
const browser=await chromium.launch();
try{
  const contexts=await Promise.all([browser.newContext({viewport:{width:1200,height:900}}),browser.newContext({viewport:{width:390,height:900}})]);
  const [a,b]=await Promise.all(contexts.map(context=>context.newPage()));
  const errors=[];
  for(const page of [a,b])page.on('pageerror',error=>errors.push(String(error)));
  async function join(page,name){
    await page.goto(base);
    await page.locator('[data-section="chat"]').click();
    await page.locator('#chatName').fill(name);
    await page.getByRole('button',{name:'Join chat'}).click();
    await page.locator('.chatComposer').waitFor({timeout:30000});
  }
  await join(a,'Site setup A');await join(b,'Site setup B');
  await a.locator('.chatComposer textarea').fill('Chat connection check: lobby delivery works.');
  await a.getByRole('button',{name:'Send',exact:true}).click();
  await b.getByText('Chat connection check: lobby delivery works.',{exact:true}).waitFor({timeout:30000});
  await a.getByRole('button',{name:/Site setup B/}).click();
  await a.locator('.chatConversationTitle').filter({hasText:'Site setup B'}).waitFor();
  await a.locator('.chatComposer textarea').fill('Private connection check: received only by participants.');
  await a.getByRole('button',{name:'Send',exact:true}).click();
  await b.getByRole('tab',{name:'Site setup A',exact:true}).click();
  await b.getByText('Private connection check: received only by participants.',{exact:true}).waitFor({timeout:30000});
  const dmId=await a.locator('.chatTab[aria-selected="true"]').getAttribute('data-conversation');
  assert.ok(dmId && dmId!=='lobby');
  const guestResponse=await fetch(`https://identitytoolkit.googleapis.com/v1/accounts:signUp?key=${encodeURIComponent(config.apiKey)}`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({returnSecureToken:true})});
  assert.equal(guestResponse.status,200,'third anonymous account creation');
  const guest=await guestResponse.json();
  const dmUrl=`https://firestore.googleapis.com/v1/projects/${config.projectId}/databases/(default)/documents/dms/${dmId}`;
  assert.equal((await fetch(dmUrl,{headers:{Authorization:`Bearer ${guest.idToken}`}})).status,403,'nonparticipant can read private conversation');
  assert.equal((await fetch(dmUrl)).status,403,'unauthenticated visitor can read private conversation');
  const canvas=a.locator('.chatCanvas');await canvas.scrollIntoViewIfNeeded();
  const box=await canvas.boundingBox();
  await a.mouse.move(box.x+box.width*.1,box.y+box.height*.1);await a.mouse.down();
  await a.mouse.move(box.x+box.width*.3,box.y+box.height*.3,{steps:12});await a.mouse.up();
  await b.waitForFunction(()=>{const data=document.querySelector('.chatCanvas').getContext('2d').getImageData(200,120,1,1).data;return data[0]>200&&data[1]<150;},{},{timeout:30000});
  await a.reload();await join(a,'Site setup A');
  await a.locator(`[data-conversation="${dmId}"]`).waitFor({timeout:30000});
  await a.locator(`[data-conversation="${dmId}"]`).click();
  await a.getByText('Private connection check: received only by participants.',{exact:true}).waitFor({timeout:30000});
  assert.deepEqual(errors,[]);
  await mkdir('test-results/chat-live',{recursive:true});
  await b.screenshot({path:'test-results/chat-live/mobile.png',fullPage:true});
  a.on('dialog',dialog=>dialog.accept());
  await a.getByRole('button',{name:'New page',exact:true}).click();
  console.log('Live Firebase passed: two-browser lobby, incoming DM, persisted identity, shared canvas, and denied private reads for outsiders.');
}finally{await browser.close();await new Promise(done=>server.close(done));}
