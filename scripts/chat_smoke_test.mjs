import assert from 'node:assert/strict';
import {chromium} from 'playwright';
import {pathToFileURL} from 'node:url';
import path from 'node:path';
import {mkdirSync} from 'node:fs';

const screenshots=process.env.SXS_CHAT_SCREENSHOTS;
if (screenshots) mkdirSync(screenshots,{recursive:true});

const browser = await chromium.launch({headless:true});
try {
  for (const width of [320, 390, 1200]) {
    const page = await browser.newPage({viewport:{width,height:900}});
    const errors = [];
    page.on('pageerror', error => errors.push(String(error)));
    await page.addInitScript(() => {
      const listeners = {people:new Set(), lobby:new Set(), conversations:new Set(), dm:new Set(), board:new Set()};
      const data = {people:[{uid:'self12345678901234567',name:'Tester'},{uid:'other1234567890123456',name:'Friend'}],lobby:[],conversations:[],dm:[],board:[]};
      data.conversations=[{id:['self12345678901234567','other1234567890123456'].sort().join('_'),members:data.people.map(person=>person.uid),names:{other1234567890123456:'Friend'}}];
      const emit = key => listeners[key].forEach(callback => callback([...data[key]]));
      const subscribe = key => callback => {listeners[key].add(callback);callback([...data[key]]);return () => listeners[key].delete(callback);};
      window.__SXS_CHAT_TEST_BACKEND = {
        uid:'self12345678901234567',
        async join(name) {data.people[0].name=name;emit('people');return {uid:this.uid,name};},
        subscribePeople:subscribe('people'),subscribeLobby:subscribe('lobby'),
        subscribeConversations:subscribe('conversations'),subscribeDm:(_id,callback)=>subscribe('dm')(callback),
        subscribeBoard:subscribe('board'),
        async sendLobby(text) {data.lobby.push({id:'l'+data.lobby.length,senderId:this.uid,senderName:'Tester',text});emit('lobby');},
        async openDm(otherUid) {const id=[this.uid,otherUid].sort().join('_');if(!data.conversations.some(item=>item.id===id))data.conversations.push({id,members:[this.uid,otherUid],names:{[otherUid]:'Friend'}});emit('conversations');return id;},
        async sendDm(_id,text) {data.dm.push({id:'d'+data.dm.length,senderId:this.uid,senderName:'Tester',text});emit('dm');},
        async addStroke(stroke) {data.board.push({id:'s'+data.board.length,kind:'stroke',...stroke});emit('board');},
        async clearBoard() {data.board.push({id:'c'+data.board.length,kind:'clear'});emit('board');},
        close() {}
      };
      for(const method of ['sendLobby','sendDm']){
        const send=window.__SXS_CHAT_TEST_BACKEND[method];
        window.__SXS_CHAT_TEST_BACKEND[method]=async function(...args){
          window.__chatSendAttempts=(window.__chatSendAttempts||0)+1;
          if(window.__chatHoldSend)await new Promise(resolve=>{(window.__chatReleaseSends||=[]).push(resolve);});
          if(window.__chatFailSend)throw new Error('Test send failed');
          return send.apply(this,args);
        };
      }
      window.__chatTestData = data;
      window.confirm = () => true;
    });
    await page.goto(pathToFileURL(path.resolve('index.html')).href);
    await page.locator('[data-section="chat"]').click();
    await page.locator('#chatName').fill('Tester');
    await page.getByRole('button',{name:'Join chat'}).click();
    const input=page.locator('.chatComposer textarea');
    async function checkRapidSend(room,text){
      await page.evaluate(()=>{window.__chatHoldSend=true;window.__chatSendAttempts=0;window.__chatReleaseSends=[];});
      await input.fill(text);
      await input.press('Enter');
      await input.press('Enter');
      await input.press('Enter');
      await page.locator('.chatComposer').evaluate(form=>form.requestSubmit());
      assert.equal(await page.evaluate(()=>window.__chatSendAttempts),1,`${room}: repeated Enter and submit must share one in-flight send`);
      await page.evaluate(()=>{window.__chatHoldSend=false;window.__chatReleaseSends.forEach(resolve=>resolve());});
      await page.waitForFunction(()=>!document.querySelector('.chatComposer button[type=submit]').disabled);
      assert.equal(await page.evaluate(({room,text})=>window.__chatTestData[room].filter(message=>message.text===text).length,{room,text}),1,`${room}: one message is delivered`);
    }
    await checkRapidSend('lobby','Rapid lobby message');
    await page.evaluate(()=>{window.__chatFailSend=true;});
    await input.fill('Retry this message');
    await input.press('Enter');
    await page.getByText('Test send failed',{exact:true}).waitFor();
    assert.equal(await input.inputValue(),'Retry this message','failed sends keep the message');
    await page.evaluate(()=>{window.__chatFailSend=false;});
    await input.press('Enter');
    await page.getByText('Retry this message',{exact:true}).waitFor();
    await input.fill('Hello there');
    await input.evaluate(el=>el.setSelectionRange(5,5));
    await page.getByRole('button',{name:'Choose emoji'}).click();
    if(screenshots)await page.screenshot({path:path.join(screenshots,`emoji-${width}.png`)});
    await page.getByRole('button',{name:'Insert thumbs up',exact:true}).click();
    assert.equal(await input.inputValue(),'Hello👍 there','emoji inserts at the cursor');
    await page.getByRole('button',{name:'Send',exact:true}).click();
    await page.getByText('Hello👍 there',{exact:true}).waitFor();
    await input.fill('x'.repeat(280));
    await page.getByRole('button',{name:'Choose emoji'}).click();
    await page.getByRole('button',{name:'Insert heart',exact:true}).click();
    assert.equal((await input.inputValue()).length,280,'emoji respects message limit');
    await page.keyboard.press('Escape');
    assert.equal(await page.locator('.chatEmojiPicker').isVisible(),false);
    await page.locator('.chatComposer textarea').fill('Hello lobby');
    await page.getByRole('button',{name:'Send'}).click();
    await assert.doesNotReject(page.getByText('Hello lobby').waitFor());
    await page.locator('.chatComposer textarea').fill('<img src=x onerror=alert(1)>');
    await page.getByRole('button',{name:'Send'}).click();
    assert.equal(await page.locator('.chatMessages img').count(),0,'message text became HTML');
    await page.getByRole('button',{name:/Friend.*other/}).click();
    await checkRapidSend('dm','Rapid private message');
    await page.locator('.chatComposer textarea').fill('Hello privately');
    await page.getByRole('button',{name:'Send'}).click();
    await assert.doesNotReject(page.getByText('Hello privately').waitFor());
    await page.getByRole('button',{name:'Close chat with Friend'}).click();
    assert.equal(await page.getByRole('tab',{name:'Friend',exact:true}).count(),0,'closed DM stays hidden');
    assert.equal(await page.getByRole('tab',{name:'Lobby',exact:true}).getAttribute('aria-selected'),'true');
    assert.equal(await page.getByRole('button',{name:'Close chat with Lobby'}).count(),0,'lobby cannot be closed');
    await page.getByRole('button',{name:/Friend.*other/}).click();
    await page.getByText('Hello privately').waitFor();
    const canvas = page.locator('.chatCanvas');
    const originalBox=await canvas.boundingBox();
    await page.getByRole('button',{name:'Expand drawing board'}).click();
    assert.equal(await page.getByRole('dialog',{name:'Expanded shared canvas'}).isVisible(),true);
    assert.ok(await page.getByRole('dialog',{name:'Expanded shared canvas'}).evaluate(el=>el.scrollWidth<=el.clientWidth+1),'expanded drawing controls overflow');
    if(width>620){const placement=await page.getByRole('dialog',{name:'Expanded shared canvas'}).evaluate(el=>{const r=el.getBoundingClientRect(),s=getComputedStyle(el);return {x:r.x,width:r.width,viewport:innerWidth,margin:s.margin};});assert.ok(Math.abs(placement.x-(placement.viewport-placement.width)/2)<10,`desktop drawing board is not centered: ${JSON.stringify(placement)}`);}
    const box = await canvas.boundingBox();
    assert.ok(box && box.width>100, `${width}px canvas is too narrow`);
    assert.ok(box.width>originalBox.width+5,`${width}px expanded board did not grow`);
    await page.mouse.move(box.x+30,box.y+30);
    await page.mouse.down();
    await page.mouse.move(box.x+80,box.y+50,{steps:5});
    await page.mouse.up();
    await page.waitForFunction(() => window.__chatTestData.board.some(item => item.kind==='stroke'));
    const strokePixel=await canvas.evaluate(el=>Array.from(el.getContext('2d').getImageData(Math.round(30/el.clientWidth*1000),Math.round(30/el.clientHeight*600),1,1).data));
    assert.notDeepEqual(strokePixel,[255,253,251,255],'brush draws colored pixels');
    await page.getByRole('button',{name:'Eraser',exact:true}).click();
    assert.equal(await page.getByRole('button',{name:'Eraser',exact:true}).getAttribute('aria-pressed'),'true');
    await page.mouse.move(box.x+30,box.y+30);
    await page.mouse.down();
    await page.mouse.move(box.x+80,box.y+50,{steps:5});
    await page.mouse.up();
    await page.waitForFunction(()=>window.__chatTestData.board.some(item=>item.color==='#f7f3ff'));
    const erasedPixel=await canvas.evaluate(el=>Array.from(el.getContext('2d').getImageData(Math.round(30/el.clientWidth*1000),Math.round(30/el.clientHeight*600),1,1).data));
    assert.deepEqual(erasedPixel,[255,253,251,255],'eraser restores the board background');
    await page.getByRole('button',{name:'Draw with #f767ad',exact:true}).click();
    assert.equal(await page.getByRole('button',{name:'Eraser',exact:true}).getAttribute('aria-pressed'),'false','choosing a color returns to drawing');
    const beforeLongStroke=await page.evaluate(()=>window.__chatTestData.board.length);
    await page.mouse.move(box.x+box.width*.1,box.y+box.height*.6);
    await page.mouse.down();
    await canvas.evaluate(el=>{
      const box=el.getBoundingClientRect();
      const pointerId=1;
      for(let i=1;i<=320;i++)el.dispatchEvent(new PointerEvent('pointermove',{pointerId,clientX:box.x+box.width*(i%2?.8:.1),clientY:box.y+box.height*.6}));

    });
    await page.mouse.up();
    await page.waitForFunction(before=>window.__chatTestData.board.length>=before+3,beforeLongStroke);
    const chunks=await page.evaluate(before=>window.__chatTestData.board.slice(before),beforeLongStroke);
    assert.equal(chunks.reduce((total,item)=>total+item.points.split(';').length,0),323,'long strokes retain every point and connecting endpoints');
    assert.ok(chunks.every(item=>item.points.length<=1800),'stroke chunks fit the backend limit');
    if(screenshots)await page.screenshot({path:path.join(screenshots,`expanded-${width}.png`)});
    const drawing=await canvas.evaluate(el=>el.toDataURL());
    await page.keyboard.press('Escape');
    assert.equal(await page.getByRole('dialog',{name:'Expanded shared canvas'}).isVisible(),false);
    assert.equal(await canvas.evaluate(el=>el.toDataURL()),drawing,'closing expanded board preserves drawing');
    await page.getByRole('button',{name:'Expand drawing board'}).click();
    await page.getByRole('button',{name:'Collapse drawing board'}).click();
    assert.equal(await page.getByRole('dialog',{name:'Expanded shared canvas'}).isVisible(),false);
    await page.getByRole('button',{name:'New page'}).click();
    await page.waitForFunction(() => window.__chatTestData.board.some(item => item.kind==='clear'));
    const metrics = await page.evaluate(() => ({overflow:document.documentElement.scrollWidth-innerWidth,board:window.__chatTestData.board}));
    assert.ok(metrics.overflow<=1, `${width}px chat overflows by ${metrics.overflow}px`);
    assert.match(metrics.board.find(item=>item.kind==='stroke').points,/^\d+,\d+(;\d+,\d+)*$/);
    assert.deepEqual(errors,[],`${width}px browser errors`);
    if (screenshots) await page.screenshot({path:path.join(screenshots,`chat-${width}.png`),fullPage:true});
    await page.getByRole('button',{name:'Close chat with Friend'}).click();
    await page.reload();
    await page.locator('#chatName').fill('Tester');
    await page.getByRole('button',{name:'Join chat'}).click();
    await page.locator('.chatComposer').waitFor();
    assert.equal(await page.getByRole('tab',{name:'Friend',exact:true}).count(),0,'closed tabs remain closed after reload');
    await page.close();
    console.log(`Chat smoke passed at ${width}px`);
  }
} finally {await browser.close();}
