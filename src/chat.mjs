import {createChatBackend,readChatConfig} from './chat-backend.mjs';

const COLORS=['#f767ad','#ffd166','#6dd5ed','#a2e875','#ae91ff','#f7f3ff'];
const EMOJIS=[['😀','smile'],['😂','laughing'],['❤️','heart'],['👍','thumbs up'],['👎','thumbs down'],['🎉','celebration'],['🔥','fire'],['👀','eyes'],['🤔','thinking'],['😭','crying'],['😎','cool'],['✨','sparkles']];
const NAME_KEY='sxs-chat-name';
let closedConversations=new Set(),expandedBoardDialog;
let host,backend,ready=false,joined=false,active=false,starting=null;
let people=[],conversations=[],strokes=[],selected='lobby',selectedName='Lobby';
let stopPeople=()=>{},stopConversations=()=>{},stopMessages=()=>{},stopBoard=()=>{};
let canvas,ctx,drawPoints=[],drawing=false,drawColor=COLORS[0],drawWidth=3;

function el(tag,className,text){const node=document.createElement(tag);if(className)node.className=className;if(text!==undefined)node.textContent=text;return node;}
function button(label,className,onClick){const node=el('button',className,label);node.type='button';node.addEventListener('click',onClick);return node;}
function errorText(error){return error?.message||'Something went wrong. Please try again.';}
function rememberedName(){try{return localStorage.getItem(NAME_KEY)||'';}catch{return '';}}
function rememberName(name){try{localStorage.setItem(NAME_KEY,name);}catch{}}
function loadClosedChats(){try{const ids=JSON.parse(localStorage.getItem(`sxs-chat-closed:${backend.uid}`)||'[]');closedConversations=new Set(Array.isArray(ids)?ids.filter(id=>typeof id==='string').slice(-200):[]);}catch{closedConversations=new Set();}}
function saveClosedChats(){try{localStorage.setItem(`sxs-chat-closed:${backend.uid}`,JSON.stringify([...closedConversations].slice(-200)));}catch{}}
function showStatus(message,isError=false){const node=host?.querySelector('.chatStatus');if(!node)return;node.textContent=message;node.hidden=!message;node.classList.toggle('isError',isError);}
function unsubscribe(){stopPeople();stopConversations();stopMessages();stopBoard();stopPeople=stopConversations=stopMessages=stopBoard=()=>{};}
function callback(render){return (items,error)=>{if(error){showStatus(errorText(error),true);return;}render(Array.isArray(items)?items:[]);};}
function shell(){
 host=document.getElementById('chatSection');if(!host)throw new Error('Chat section is missing');
 host.innerHTML='';
 const intro=el('div','chatIntro');intro.append(el('div','chatEyebrow','COMMUNITY'),el('h1','','Chat & Draw'),el('p','','Say hello in the lobby, message someone privately, or add to the shared canvas.'));
 const status=el('p','chatStatus');status.setAttribute('role','status');status.hidden=true;
 host.append(intro,status,el('div','chatBody'));
}
function renderJoin(){
 const body=host.querySelector('.chatBody');body.replaceChildren();
 const card=el('section','chatJoin card');card.append(el('h2','','Pick a name'),el('p','','Your name appears beside your messages. You can start chatting without creating an account.'));
 const form=el('form','chatJoinForm');const label=el('label','','Name');label.htmlFor='chatName';const input=el('input');input.id='chatName';input.name='name';input.type='text';input.maxLength=24;input.minLength=2;input.required=true;input.autocomplete='nickname';input.placeholder='Your name';input.value=rememberedName();
 const submit=button('Join chat','chatPrimary',()=>{});submit.type='submit';input.disabled=submit.disabled=!ready;form.append(label,input,submit);card.append(form);
 const note=el('p','chatPrivacy','Private messages are visible to their participants, but names are not verified. Keep personal information out of chat.');card.append(note);body.append(card);
 form.addEventListener('submit',async event=>{event.preventDefault();const name=input.value.trim().replace(/\s+/g,' ');if(name.length<2){showStatus('Choose a name with at least two characters.',true);input.focus();return;}submit.disabled=true;showStatus('Joining chat…');try{await backend.join(name);joined=true;rememberName(name);showStatus('');renderChat();if(active)subscribeAll();}catch(error){showStatus(errorText(error),true);}finally{submit.disabled=false;}});
}
function renderChat(){
 const body=host.querySelector('.chatBody');body.replaceChildren();
 const layout=el('div','chatLayout');
 const chat=el('section','chatPanel card');chat.setAttribute('aria-label','Messages');
 const tabs=el('div','chatTabs');tabs.setAttribute('role','tablist');tabs.setAttribute('aria-label','Conversations');
 const header=el('div','chatConversationHeader');header.append(el('h2','chatConversationTitle',selectedName),el('span','chatConversationHint',selected==='lobby'?'Everyone can read this room.':'Only participants can read this conversation.'));
 const messages=el('ol','chatMessages');messages.setAttribute('aria-label','Chat messages');
 const form=el('form','chatComposer');const textarea=el('textarea');textarea.id='chatMessage';textarea.maxLength=280;textarea.rows=2;textarea.placeholder='Write a message…';textarea.setAttribute('aria-label','Message');const send=button('Send','chatPrimary',()=>{});send.type='submit';
 const composerInput=el('div','chatComposerInput'),composerActions=el('div','chatComposerActions'),emojiPicker=el('div','chatEmojiPicker');emojiPicker.id='chatEmojiPicker';emojiPicker.hidden=true;emojiPicker.setAttribute('role','group');emojiPicker.setAttribute('aria-label','Emojis');
 const emojiToggle=button('😀','chatEmojiToggle chatSubtle',()=>{emojiPicker.hidden=!emojiPicker.hidden;emojiToggle.setAttribute('aria-expanded',String(!emojiPicker.hidden));if(!emojiPicker.hidden)emojiPicker.querySelector('button')?.focus();});emojiToggle.setAttribute('aria-label','Choose emoji');emojiToggle.setAttribute('aria-expanded','false');emojiToggle.setAttribute('aria-controls',emojiPicker.id);
 for(const [emoji,name] of EMOJIS){const pick=button(emoji,'chatEmoji',()=>{const start=textarea.selectionStart,end=textarea.selectionEnd;if(textarea.value.length-(end-start)+emoji.length>textarea.maxLength){showStatus('Your message is already at the 280-character limit.',true);return;}textarea.setRangeText(emoji,start,end,'end');emojiPicker.hidden=true;emojiToggle.setAttribute('aria-expanded','false');textarea.focus();});pick.setAttribute('aria-label',`Insert ${name}`);emojiPicker.append(pick);}
 composerInput.append(textarea,emojiPicker);composerActions.append(emojiToggle,send);form.append(composerInput,composerActions);
 form.addEventListener('keydown',event=>{if(event.key==='Escape'&&!emojiPicker.hidden){event.preventDefault();emojiPicker.hidden=true;emojiToggle.setAttribute('aria-expanded','false');emojiToggle.focus();}});
 form.addEventListener('submit',async event=>{event.preventDefault();const value=textarea.value.trim();if(!value)return;send.disabled=true;try{if(selected==='lobby')await backend.sendLobby(value);else await backend.sendDm(selected,value);textarea.value='';showStatus('');textarea.focus();}catch(error){showStatus(errorText(error),true);}finally{send.disabled=false;}});
 textarea.addEventListener('keydown',event=>{if(event.key==='Enter'&&!event.shiftKey){event.preventDefault();form.requestSubmit();}});
 chat.append(tabs,header,messages,form);
 const aside=el('aside','chatAside');const peopleCard=el('section','chatPeople card');peopleCard.append(el('h2','','Recent people'),el('p','chatHelp','Choose someone to start a private message.'),el('div','chatPeopleList'));aside.append(peopleCard);
 const boardCard=el('section','chatBoard card');const boardHeading=el('div','chatBoardHeading');boardHeading.append(el('div','',''));boardHeading.firstChild.append(el('h2','','Shared canvas'),el('p','chatHelp','Draw together. A stroke is shared when you lift your finger or mouse.'));
 const clear=button('New page','chatSubtle',async()=>{if(!window.confirm('Clear the shared canvas for everyone?'))return;clear.disabled=true;try{await backend.clearBoard();showStatus('');}catch(error){showStatus(errorText(error),true);}finally{clear.disabled=false;}});
 const boardDialog=el('dialog','chatBoardDialog');boardDialog.setAttribute('aria-label','Expanded shared canvas');expandedBoardDialog=boardDialog;
 const expand=button('Expand','chatSubtle chatExpand',()=>{if(boardDialog.open){boardDialog.close();return;}boardDialog.append(boardCard);expand.textContent='Collapse';expand.setAttribute('aria-expanded','true');boardDialog.showModal();});expand.setAttribute('aria-label','Expand drawing board');expand.setAttribute('aria-expanded','false');
 boardDialog.addEventListener('close',()=>{aside.append(boardCard);expand.textContent='Expand';expand.setAttribute('aria-expanded','false');expand.setAttribute('aria-label','Expand drawing board');if(active)expand.focus();});
 expand.addEventListener('click',()=>expand.setAttribute('aria-label',boardDialog.open?'Collapse drawing board':'Expand drawing board'));
 const boardActions=el('div','chatBoardActions');boardActions.append(expand,clear);boardHeading.append(boardActions);
 const tools=el('div','chatDrawTools');tools.setAttribute('role','group');tools.setAttribute('aria-label','Drawing tools');const palette=el('div','chatPalette');for(const color of COLORS){const swatch=button('', 'chatSwatch',()=>{drawColor=color;refreshTools();});swatch.style.setProperty('--swatch',color);swatch.dataset.color=color;swatch.setAttribute('aria-label',`Draw with ${color}`);swatch.title=color;palette.append(swatch);}const sizes=el('div','chatSizes');for(const width of [3,7]){const size=button(width===3?'Fine':'Bold','chatSize',()=>{drawWidth=width;refreshTools();});size.dataset.width=String(width);sizes.append(size);}tools.append(palette,sizes);
 const frame=el('div','chatCanvasFrame');canvas=el('canvas','chatCanvas');canvas.setAttribute('aria-label','Shared drawing canvas');canvas.setAttribute('role','img');canvas.width=1000;canvas.height=600;frame.append(canvas);boardCard.append(boardHeading,tools,frame);aside.append(boardCard);layout.append(chat,aside);body.append(layout,boardDialog);
 ctx=canvas.getContext('2d');canvas.addEventListener('pointerdown',pointerDown);canvas.addEventListener('pointermove',pointerMove);canvas.addEventListener('pointerup',pointerUp);canvas.addEventListener('pointercancel',pointerUp);refreshTools();renderTabs();renderPeople();
}
function refreshTools(){host.querySelectorAll('.chatSwatch').forEach(node=>node.setAttribute('aria-pressed',String(node.dataset.color===drawColor)));host.querySelectorAll('.chatSize').forEach(node=>node.setAttribute('aria-pressed',String(Number(node.dataset.width)===drawWidth)));}
function renderTabs(){
 const tabs=host.querySelector('.chatTabs');if(!tabs)return;tabs.replaceChildren();
 const makeTab=(id,label)=>{
  const group=el('div','chatConversationTab');
  const node=button(label,'chatTab',()=>openConversation(id,label));node.setAttribute('role','tab');node.dataset.conversation=id;node.setAttribute('aria-selected',String(selected===id));group.append(node);
  if(id!=='lobby'){
   const close=button('×','chatCloseTab',()=>{closedConversations.add(id);saveClosedChats();if(selected===id)openConversation('lobby','Lobby');else renderTabs();});
   close.setAttribute('aria-label',`Close chat with ${label}`);group.append(close);
  }
  tabs.append(group);
 };
 makeTab('lobby','Lobby');
 for(const convo of conversations){
  if(closedConversations.has(convo.id))continue;
  const other=convo.members?.find(uid=>uid!==backend.uid),person=people.find(p=>p.uid===other);
  const label=person?.name||convo.names?.[other]||`Guest ${String(other||'').slice(0,6)}`;makeTab(convo.id,label);
 }
 if(selected!=='lobby'&&!closedConversations.has(selected)&&!conversations.some(c=>c.id===selected))makeTab(selected,selectedName);
}
function renderPeople(){const list=host.querySelector('.chatPeopleList');if(!list)return;list.replaceChildren();const others=people.filter(person=>person.uid!==backend.uid);if(!others.length){list.append(el('p','chatEmpty','No one else has joined yet.'));return;}for(const person of others){const name=String(person.name||'Guest').slice(0,24);const item=button(`${name}  ·  ${String(person.uid).slice(0,5)}`,'chatPerson',async()=>{item.disabled=true;try{const result=await backend.openDm(person.uid);const id=typeof result==='string'?result:result?.id;if(!id)throw new Error('Could not open private message.');openConversation(id,name);}catch(error){showStatus(errorText(error),true);}finally{item.disabled=false;}});item.title=`Message ${name}`;list.append(item);}}
function openConversation(id,label){if(id!=='lobby'&&closedConversations.delete(id))saveClosedChats();if(selected===id)return;selected=id;selectedName=label;renderTabs();const title=host.querySelector('.chatConversationTitle');if(title)title.textContent=label;const hint=host.querySelector('.chatConversationHint');if(hint)hint.textContent=id==='lobby'?'Everyone can read this room.':'Only participants can read this conversation.';const messages=host.querySelector('.chatMessages');if(messages)messages.replaceChildren(el('li','chatEmpty','Loading messages…'));subscribeMessages();}
function renderMessages(items){const list=host.querySelector('.chatMessages');if(!list)return;const nearBottom=list.scrollHeight-list.scrollTop-list.clientHeight<90;list.replaceChildren();if(!items.length){list.append(el('li','chatEmpty',selected==='lobby'?'No messages yet. Say hello!':'No messages yet. Start the conversation.'));return;}for(const message of items){const item=el('li','chatMessage');if(message.senderId===backend.uid)item.classList.add('mine');const author=el('strong','chatAuthor',String(message.senderName||'Guest').slice(0,24));const text=el('p','chatMessageText',String(message.text||''));item.append(author,text);list.append(item);}if(nearBottom)list.scrollTop=list.scrollHeight;}
function subscribeMessages(){stopMessages();stopMessages=()=>{};if(!active||!ready)return;const list=host.querySelector('.chatMessages');if(list)list.replaceChildren(el('li','chatEmpty','Loading messages…'));try{stopMessages=selected==='lobby'?backend.subscribeLobby(callback(renderMessages)):backend.subscribeDm(selected,callback(renderMessages));}catch(error){showStatus(errorText(error),true);}}
function subscribeAll(){unsubscribe();if(!active||!ready||!joined)return;try{stopPeople=backend.subscribePeople(callback(items=>{people=items;renderPeople();renderTabs();}));stopConversations=backend.subscribeConversations(callback(items=>{conversations=items;renderTabs();}));stopBoard=backend.subscribeBoard(callback(items=>{strokes=items;renderCanvas();}));subscribeMessages();}catch(error){showStatus(errorText(error),true);}}
function point(event){const bounds=canvas.getBoundingClientRect();return [Math.max(0,Math.min(1000,Math.round((event.clientX-bounds.left)/bounds.width*1000))),Math.max(0,Math.min(1000,Math.round((event.clientY-bounds.top)/bounds.height*1000)))];}
function parsePoints(value){if(typeof value!=='string')return [];return value.split(';').slice(0,400).map(pair=>pair.split(',').map(Number)).filter(pair=>pair.length===2&&pair.every(n=>Number.isFinite(n)&&n>=0&&n<=1000));}
function strokePath(points,color,width){if(!points.length)return;ctx.strokeStyle=color;ctx.fillStyle=color;ctx.lineWidth=width*canvas.width/1000;ctx.lineJoin='round';ctx.lineCap='round';ctx.beginPath();ctx.moveTo(points[0][0]*canvas.width/1000,points[0][1]*canvas.height/1000);for(let i=1;i<points.length;i++)ctx.lineTo(points[i][0]*canvas.width/1000,points[i][1]*canvas.height/1000);if(points.length===1){ctx.arc(points[0][0]*canvas.width/1000,points[0][1]*canvas.height/1000,ctx.lineWidth/2,0,Math.PI*2);ctx.fill();}else ctx.stroke();}
function renderCanvas(){if(!ctx)return;ctx.fillStyle='#fffdfb';ctx.fillRect(0,0,canvas.width,canvas.height);let start=0;for(let i=strokes.length-1;i>=0;i--){if(strokes[i].kind==='clear'){start=i+1;break;}}for(const item of strokes.slice(start)){if(item.kind==='stroke'&&COLORS.includes(item.color))strokePath(parsePoints(item.points),item.color,Number(item.width)||4);}if(drawing)strokePath(drawPoints,drawColor,drawWidth);}
function pointerDown(event){if(event.button!==0&&event.pointerType==='mouse')return;drawing=true;drawPoints=[point(event)];canvas.setPointerCapture(event.pointerId);renderCanvas();}
function pointerMove(event){if(!drawing||!canvas.hasPointerCapture(event.pointerId))return;const next=point(event);const last=drawPoints.at(-1);if(last&&Math.hypot(next[0]-last[0],next[1]-last[1])<3)return;if(drawPoints.length<180)drawPoints.push(next);renderCanvas();}
async function pointerUp(event){if(!drawing||!canvas.hasPointerCapture(event.pointerId))return;drawing=false;try{canvas.releasePointerCapture(event.pointerId);}catch{}const points=drawPoints.map(pair=>pair.join(',')).join(';');drawPoints=[];renderCanvas();try{await backend.addStroke({color:drawColor,width:drawWidth,points});}catch(error){showStatus(errorText(error),true);}}
export function initialize(){if(host)return; shell();}
export async function activate(){initialize();active=true;if(ready){subscribeAll();return;}if(starting)return starting;showStatus('Connecting to chat…');starting=(async()=>{try{if(window.__SXS_CHAT_TEST_BACKEND){backend=window.__SXS_CHAT_TEST_BACKEND;}else{const config=await readChatConfig();if(!active)return;backend=await createChatBackend(config);}ready=true;loadClosedChats();showStatus('');renderJoin();}catch(error){showStatus(`Chat needs setup: ${errorText(error)}`,true);const body=host.querySelector('.chatBody');body.replaceChildren(el('p','chatSetup','Chat is not connected yet. The site owner needs to finish the Firebase setup.'));throw error;}finally{starting=null;}})();return starting;}
export function deactivate(){active=false;expandedBoardDialog?.close();unsubscribe();}
