import { getApps, initializeApp } from 'firebase/app';
import { getAuth, signInAnonymously } from 'firebase/auth';
import {
  getFirestore, collection, doc, getDoc, onSnapshot, orderBy, query, limit,
  where, serverTimestamp, setDoc, updateDoc, addDoc, runTransaction
} from 'firebase/firestore';

const MAX_NAME = 24;
const MAX_MESSAGE = 280;
const STROKE_PATTERN = /^(?:\d{1,4},\d{1,4})(?:;\d{1,4},\d{1,4})*$/;
const COLORS = new Set(['#f7f3ff', '#f767ad', '#6dd5ed', '#ffd166', '#a2e875', '#ae91ff']);

export async function readChatConfig() {
  const response = await fetch('chat-config.json', { cache: 'no-store' });
  if (!response.ok) throw new Error('Chat configuration is unavailable.');
  const config = await response.json();
  if (!config || !['apiKey', 'authDomain', 'projectId', 'appId'].every(key =>
    typeof config[key] === 'string' && config[key].trim())) {
    throw new Error('Chat is awaiting Firebase setup.');
  }
  return config;
}

function cleanName(value) {
  const name = String(value ?? '').trim().replace(/\s+/g, ' ');
  if (!name || name.length > MAX_NAME) throw new Error(`Choose a name of 1–${MAX_NAME} characters.`);
  return name;
}

function cleanMessage(value) {
  const text = String(value ?? '').trim();
  if (!text || text.length > MAX_MESSAGE) throw new Error(`Messages must be 1–${MAX_MESSAGE} characters.`);
  return text;
}

function listen(queryRef, map, callback) {
  return onSnapshot(queryRef,
    snapshot => callback(snapshot.docs.map(item => ({ id: item.id, ...map(item.data()) }))),
    error => callback([], error));
}

export async function createChatBackend(config) {
  if (!config?.projectId) throw new Error('Missing Firebase configuration.');
  const app = getApps().find(item => item.name === 'sxs-chat') || initializeApp(config, 'sxs-chat');
  const auth = getAuth(app);
  await auth.authStateReady();
  const user = auth.currentUser || (await signInAnonymously(auth)).user;
  const uid = user.uid;
  const db = getFirestore(app);
  const users = collection(db, 'users');
  const lobby = collection(db, 'rooms', 'lobby', 'messages');
  const dms = collection(db, 'dms');
  const board = collection(db, 'boards', 'main', 'strokes');
  const subscriptions = new Set();

  function track(unsubscribe) {
    subscriptions.add(unsubscribe);
    return () => { unsubscribe(); subscriptions.delete(unsubscribe); };
  }

  async function profileName() {
    const snapshot = await getDoc(doc(users, uid));
    if (!snapshot.exists()) throw new Error('Enter your name to join chat.');
    return snapshot.data().name;
  }

  return {
    uid,
    async join(rawName) {
      const name = cleanName(rawName);
      const profile = doc(users, uid);
      const existing = await getDoc(profile);
      if (existing.exists()) await updateDoc(profile, { name, lastActive: serverTimestamp() });
      else await setDoc(profile, { name, createdAt: serverTimestamp(), lastActive: serverTimestamp() });
      return { uid, name };
    },
    subscribePeople(callback) {
      return track(listen(query(users, orderBy('lastActive', 'desc'), limit(50)),
        data => ({ uid: data.uid, name: data.name }),
        (items, error) => callback(items.map(item => ({ uid: item.id, name: item.name })), error)));
    },
    subscribeLobby(callback) {
      return track(listen(query(lobby, orderBy('createdAt', 'desc'), limit(80)),
        data => ({ senderId: data.senderId, senderName: data.senderName, text: data.text, createdAt: data.createdAt }),
        (items, error) => callback(items.reverse(), error)));
    },
    async sendLobby(value) {
      const text = cleanMessage(value);
      const senderName = await profileName();
      await addDoc(lobby, { senderId: uid, senderName, text, createdAt: serverTimestamp() });
    },
    subscribeConversations(callback) {
      return track(listen(query(dms, where('members', 'array-contains', uid), limit(30)),
        data => ({ members: data.members, names: data.names, createdAt: data.createdAt }), callback));
    },
    async openDm(otherUid) {
      if (typeof otherUid !== 'string' || !/^[A-Za-z0-9]{20,128}$/.test(otherUid) || otherUid === uid)
        throw new Error('Choose another chat participant.');
      const other = await getDoc(doc(users, otherUid));
      if (!other.exists()) throw new Error('That participant is unavailable.');
      const name = await profileName();
      const members = [uid, otherUid].sort();
      const id = members.join('_');
      const names = { [uid]: name, [otherUid]: other.data().name };
      const target = doc(dms, id);
      await runTransaction(db, async transaction => {
        const existing = await transaction.get(target);
        if (!existing.exists()) transaction.set(target, { members, names, createdAt: serverTimestamp() });
      });
      return id;
    },
    subscribeDm(id, callback) {
      return track(listen(query(collection(db, 'dms', id, 'messages'), orderBy('createdAt', 'desc'), limit(80)),
        data => ({ senderId: data.senderId, senderName: data.senderName, text: data.text, createdAt: data.createdAt }),
        (items, error) => callback(items.reverse(), error)));
    },
    async sendDm(id, value) {
      const text = cleanMessage(value);
      const senderName = await profileName();
      await addDoc(collection(db, 'dms', id, 'messages'),
        { senderId: uid, senderName, text, createdAt: serverTimestamp() });
    },
    subscribeBoard(callback) {
      return track(listen(query(board, orderBy('createdAt', 'desc'), limit(120)),
        data => ({ kind: data.kind, authorId: data.authorId, color: data.color, width: data.width,
          points: data.points, createdAt: data.createdAt }),
        (items, error) => callback(items.reverse(), error)));
    },
    async addStroke(stroke) {
      if (!COLORS.has(stroke?.color) || ![3, 7].includes(stroke?.width) ||
        typeof stroke?.points !== 'string' || stroke.points.length > 1800 ||
        !STROKE_PATTERN.test(stroke.points)) throw new Error('Invalid drawing stroke.');
      await addDoc(board, { kind: 'stroke', authorId: uid, color: stroke.color, width: stroke.width,
        points: stroke.points, createdAt: serverTimestamp() });
    },
    async clearBoard() {
      await addDoc(board, { kind: 'clear', authorId: uid, createdAt: serverTimestamp() });
    },
    close() {
      for (const unsubscribe of subscriptions) unsubscribe();
      subscriptions.clear();
    }
  };
}
