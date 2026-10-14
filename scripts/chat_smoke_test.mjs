import assert from 'node:assert/strict';
import {chromium} from 'playwright';
import {pathToFileURL} from 'node:url';
import path from 'node:path';
import {mkdirSync} from 'node:fs';

const screenshots=process.env.SXS_CHAT_SCREENSHOTS;
if (screenshots) mkdirSync(screenshots,{recursive:true});

const browser = await chromium.launch({headless:true});
try {
  for (const width of [390, 1200]) {
    const page = await browser.newPage({viewport:{width,height:900}});
    const errors = [];
    page.on('pageerror', error => errors.push(String(error)));
    await page.addInitScript(() => {
      const listeners = {people:new Set(), lobby:new Set(), conversations:new Set(), dm:new Set(), board:new Set()};
      const data = {people:[{uid:'self12345678901234567',name:'Tester'},{uid:'other1234567890123456',name:'Friend'}],lobby:[],conversations:[],dm:[],board:[]};
      const emit = key => listeners[key].forEach(callback => callback([...data[key]]));
      const subscribe = key => callback => {listeners[key].add(callback);callback([...data[key]]);return () => listeners[key].delete(callback);};
      window.__SXS_CHAT_TEST_BACKEND = {
        uid:'self12345678901234567',
        async join(name) {data.people[0].name=name;emit('people');return {uid:this.uid,name};},
        subscribePeople:subscribe('people'),subscribeLobby:subscribe('lobby'),
        subscribeConversations:subscribe('conversations'),subscribeDm:(_id,callback)=>subscribe('dm')(callback),
        subscribeBoard:subscribe('board'),
        async sendLobby(text) {data.lobby.push({id:'l'+data.lobby.length,senderId:this.uid,senderName:'Tester',text});emit('lobby');},
        async openDm(otherUid) {const id=[this.uid,otherUid].sort().join('_');data.conversations.push({id,members:[this.uid,otherUid],names:{[otherUid]:'Friend'}});emit('conversations');return id;},
        async sendDm(_id,text) {data.dm.push({id:'d'+data.dm.length,senderId:this.uid,senderName:'Tester',text});emit('dm');},
        async addStroke(stroke) {data.board.push({id:'s'+data.board.length,kind:'stroke',...stroke});emit('board');},
        async clearBoard() {data.board.push({id:'c'+data.board.length,kind:'clear'});emit('board');},
        close() {}
      };
      window.__chatTestData = data;
      window.confirm = () => true;
    });
    await page.goto(pathToFileURL(path.resolve('index.html')).href);
    await page.locator('[data-section="chat"]').click();
    await page.locator('#chatName').fill('Tester');
    await page.getByRole('button',{name:'Join chat'}).click();
    await page.locator('.chatComposer textarea').fill('Hello lobby');
    await page.getByRole('button',{name:'Send'}).click();
    await assert.doesNotReject(page.getByText('Hello lobby').waitFor());
    await page.locator('.chatComposer textarea').fill('<img src=x onerror=alert(1)>');
    await page.getByRole('button',{name:'Send'}).click();
    assert.equal(await page.locator('.chatMessages img').count(),0,'message text became HTML');
    await page.getByRole('button',{name:/Friend.*other/}).click();
    await page.locator('.chatComposer textarea').fill('Hello privately');
    await page.getByRole('button',{name:'Send'}).click();
    await assert.doesNotReject(page.getByText('Hello privately').waitFor());
    const canvas = page.locator('.chatCanvas');
    const box = await canvas.boundingBox();
    assert.ok(box && box.width>100, `${width}px canvas is too narrow`);
    await page.mouse.move(box.x+30,box.y+30);
    await page.mouse.down();
    await page.mouse.move(box.x+80,box.y+50,{steps:5});
    await page.mouse.up();
    await page.waitForFunction(() => window.__chatTestData.board.some(item => item.kind==='stroke'));
    await page.getByRole('button',{name:'New page'}).click();
    await page.waitForFunction(() => window.__chatTestData.board.some(item => item.kind==='clear'));
    const metrics = await page.evaluate(() => ({overflow:document.documentElement.scrollWidth-innerWidth,board:window.__chatTestData.board}));
    assert.ok(metrics.overflow<=1, `${width}px chat overflows by ${metrics.overflow}px`);
    assert.match(metrics.board.find(item=>item.kind==='stroke').points,/^\d+,\d+(;\d+,\d+)*$/);
    assert.deepEqual(errors,[],`${width}px browser errors`);
    if (screenshots) await page.screenshot({path:path.join(screenshots,`chat-${width}.png`),fullPage:true});
    await page.close();
    console.log(`Chat smoke passed at ${width}px`);
  }
} finally {await browser.close();}
