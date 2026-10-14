// Chat and Firebase are loaded only when the visitor opens the chat tab.
const chunkUrl = new URL('chat.js', document.currentScript.src);
chunkUrl.searchParams.set('v', CHAT_BUILD_ID);
const styleUrl = new URL('chat.css', document.currentScript.src);
styleUrl.searchParams.set('v', CHAT_STYLE_ID);
let pending;
let api;
let styles;
let styleReady;

function showError(message) {
  const section = document.getElementById('chatSection');
  section.replaceChildren();
  const notice = document.createElement('p');
  notice.className = 'chatLoadError';
  notice.textContent = message;
  const retry = document.createElement('button');
  retry.type = 'button';
  retry.textContent = 'Retry';
  retry.addEventListener('click', openChat);
  section.append(notice, retry);
}

async function load() {
  if (api) return api;
  if (pending) return pending;
  pending = new Promise((resolve, reject) => {
    if (!styles) {
      styles=document.createElement('link');
      styles.rel='stylesheet';
      styles.href=styleUrl;
      styleReady=new Promise((done,fail)=>{styles.onload=done;styles.onerror=()=>fail(new Error('Chat styles failed to load'));});
      document.head.append(styles);
    }
    const script = document.createElement('script');
    script.async = true;
    script.src = chunkUrl;
    script.onload = async () => {
      try {
        await styleReady;
        if (!window.SxsChat?.initialize) throw new Error('Chat failed to initialize');
        window.SxsChat.initialize();
        api = window.SxsChat;
        resolve(api);
      } catch (error) { reject(error); }
    };
    script.onerror = () => reject(new Error('Chat download failed'));
    document.head.append(script);
  }).catch(error => { pending = null; throw error; });
  return pending;
}

export async function openChat() {
  const section = document.getElementById('chatSection');
  section.setAttribute('aria-busy', 'true');
  try {
    const chat = await load();
    section.setAttribute('aria-busy', 'false');
    if (!section.hidden) {
      try { await chat.activate(); }
      catch (_) { /* The chat UI shows its own setup or connection error. */ }
    }
  } catch (error) {
    section.setAttribute('aria-busy', 'false');
    showError('Could not load chat. Check your connection and try again.');
  }
}

export function closeChat() { api?.deactivate?.(); }
