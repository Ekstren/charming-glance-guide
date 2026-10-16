import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

// Exercise the real backend with Firebase's I/O boundary replaced. These tests do
// not substitute for publishing and checking Firestore's server-side rules.
const source = (await readFile(new URL('../src/chat-backend.mjs', import.meta.url), 'utf8'))
  .replace(/import[\s\S]*?from 'firebase\/[a-z]+';/g, '')
  .replace(/export /g, '');

async function fixture() {
  const state = { listeners: [], writes: [], document: null, owner: false,
    reads: [], readError: null, linkError: null, provider: 'google.com', credentialCalls: 0,
    credentialUid: 'existing-google-id', tokenLinkError: null, tokenLinks: 0, credentials: [], role: {} };
  function makeUser(uid, anonymous = false) {
    return { uid, isAnonymous: anonymous,
      providerData: anonymous ? [] : [{ providerId: 'google.com' }],
      getIdTokenResult: async () => ({ claims: { firebase: { sign_in_provider: state.provider } } }) };
  }
  const user = makeUser('original-browser-id', true);
  const auth = { currentUser: user, authStateReady: async () => {} };
  const mock = {
    getApps: () => [], initializeApp: () => ({}), getAuth: () => auth,
    signInAnonymously: async () => ({ user }),
    GoogleAuthProvider: class {
      setCustomParameters() {}
      static credentialFromError(error) { return error.credential; }
      static credentialFromResult(result) { return result.credential; }
      static credential(idToken, accessToken) {
        const credential = { providerId: 'google.com', idToken, accessToken };
        state.credentials.push(credential);
        return credential;
      }
    },
    linkWithPopup: async () => {
      if (state.linkError) throw state.linkError;
      user.isAnonymous = false;
      user.providerData = [{ providerId: 'google.com' }];
      return { user, credential: { providerId: 'google.com' } };
    },
    signInWithPopup: async () => ({ user: auth.currentUser }),
    linkWithCredential: async (_user, credential) => {
      state.tokenLinks++;
      if (state.tokenLinkError) throw state.tokenLinkError;
      user.isAnonymous = false;
      user.providerData = [{ providerId: 'google.com' }];
      return { user, credential };
    },
    signInWithCredential: async () => {
      state.credentialCalls++;
      state.provider = 'google.com';
      auth.currentUser = makeUser(state.credentialUid);
      return { user: auth.currentUser };
    },
    getFirestore: () => ({}), collection: (_, ...parts) => parts.join('/'),
    doc: (_, ...parts) => parts.join('/'),
    getDoc: async ref => {
      state.reads.push(ref);
      if (state.readError) throw state.readError;
      return { exists: () => state.owner, data: () => state.role };
    },
    onSnapshot: (ref, next, error) => {
      const listener = { ref, next, error, stopped: false };
      state.listeners.push(listener);
      return () => { listener.stopped = true; };
    },
    orderBy: (...args) => ({ order: args }), query: (ref, ...constraints) => ({ ref, constraints }),
    limit: value => ({ limit: value }), where: (...args) => ({ where: args }),
    serverTimestamp: () => 'SERVER_TIMESTAMP', setDoc: () => {}, updateDoc: () => {}, addDoc: () => {},
    runTransaction: async (_, callback) => callback({
      get: async () => ({ exists: () => !!state.document, data: () => state.document }),
      set: (ref, data) => { state.writes.push({ ref, data }); state.document = data; }
    })
  };
  const create = new Function(...Object.keys(mock), `${source}; return createChatBackend;`)(...Object.values(mock));
  return { state, auth, backend: await create({ projectId: 'mock-project' }) };
}

{
  const { state, backend } = await fixture();
  await assert.rejects(backend.signInOwnerWithGoogleToken(''), /did not return an access token/);
  assert.equal(state.tokenLinks, 0);
  assert.deepEqual(await backend.signInOwnerWithGoogleToken('mock-google-access-token'), {
    uid: 'original-browser-id', changedIdentity: false
  });
  assert.deepEqual(state.credentials.at(-1), {
    providerId: 'google.com', idToken: null, accessToken: 'mock-google-access-token'
  });
  assert.equal(state.tokenLinks, 1);
  assert.equal(state.credentialCalls, 0, 'Linking an anonymous account preserves its existing chats');
  assert.equal(await backend.isOwner(), false, 'Independent Google token does not grant an owner role');
  state.owner = true;
  assert.equal(await backend.isOwner(), true);
}

{
  const { state, backend } = await fixture();
  state.provider = 'anonymous';
  state.credentialUid = backend.uid;
  assert.deepEqual(await backend.signInOwnerWithGoogleToken('mock-token'), { uid: backend.uid, changedIdentity: false });
  assert.equal(state.credentialCalls, 1, 'Credential-linked accounts still upgrade an anonymous token to Google');
  assert.equal(state.provider, 'google.com');
}

{
  const { state, backend } = await fixture();
  state.tokenLinkError = Object.assign(new Error('Credential exists'), { code: 'auth/credential-already-in-use' });
  assert.deepEqual(await backend.signInOwnerWithGoogleToken('mock-token'), {
    uid: 'existing-google-id', changedIdentity: true
  });
  assert.equal(state.tokenLinks, 1);
  assert.equal(state.credentialCalls, 1);
  await backend.signInOwnerWithGoogleToken('another-mock-token');
  assert.equal(state.tokenLinks, 1, 'Returning Google users sign in without trying to link again');
  assert.equal(state.credentialCalls, 2);
  const failed = await fixture();
  failed.state.tokenLinkError = Object.assign(new Error('Invalid token'), { code: 'auth/invalid-credential' });
  await assert.rejects(failed.backend.signInOwnerWithGoogleToken('invalid-mock-token'), { code: 'auth/invalid-credential' });
  assert.equal(failed.state.credentialCalls, 0, 'Unrelated credential failures are not swallowed');
}

{
  const { state, backend } = await fixture();
  state.provider = 'anonymous';
  state.credentialUid = backend.uid;
  state.owner = true;
  assert.deepEqual(await backend.signInOwner(), { uid: backend.uid, changedIdentity: false });
  assert.equal(state.credentialCalls, 1, 'A linked account with an anonymous token must complete Google sign-in');
  assert.equal(state.provider, 'google.com');
  assert.equal(await backend.isOwner(), true, 'Owner role becomes usable only after the Google token is established');
}

{
  const { state, backend } = await fixture();
  state.owner = true;
  assert.equal(await backend.isOwner(), false, 'Anonymous users cannot gain owner UI access from a role record alone');
  assert.equal(state.reads.at(-1), 'chatOwners/original-browser-id');
  assert.deepEqual(await backend.signInOwner(), { uid: 'original-browser-id', changedIdentity: false });
  assert.equal(backend.isGoogleSignedIn, true);
  state.provider = 'anonymous';
  assert.equal(await backend.isOwner(), false, 'Linked provider data alone is not enough without Google token sign-in');
  state.provider = 'google.com';
  state.owner = false;
  assert.equal(await backend.isOwner(), false, 'Google sign-in alone does not grant owner access');
  state.owner = true;
  assert.equal(await backend.isOwner(), true);
  assert.equal(state.reads.at(-1), 'chatOwners/original-browser-id');
  state.readError = Object.assign(new Error('Not permitted'), { code: 'permission-denied' });
  assert.equal(await backend.isOwner(), false);
  state.readError = Object.assign(new Error('Offline'), { code: 'unavailable' });
  await assert.rejects(backend.isOwner(), { code: 'unavailable' });
}

{
  const { state, auth, backend } = await fixture();
  state.provider = 'anonymous';
  state.role = { requireGoogle: false, enabled: true };
  assert.equal(await backend.isOwner(), false, 'Unregistered browser cannot enable itself by changing local state');
  state.owner = true;
  assert.equal(await backend.isOwner(), true, 'An explicitly registered browser role can authorize an anonymous account');
  assert.equal(state.reads.at(-1), `chatOwners/${auth.currentUser.uid}`);
  state.role = {};
  assert.equal(await backend.isOwner(), false, 'Missing requireGoogle defaults to requiring Google');
  state.role = { requireGoogle: true };
  assert.equal(await backend.isOwner(), false);
  state.role = { requireGoogle: 'false' };
  assert.equal(await backend.isOwner(), false, 'Only literal boolean false permits browser-only authorization');
  await backend.signInOwner();
  state.role = { requireGoogle: true };
  assert.equal(await backend.isOwner(), true);
  state.owner = false;
  state.role = { requireGoogle: false };
  assert.equal(await backend.isOwner(), false, 'Even a Google account still needs a registered owner document');
}

{
  const { state, backend } = await fixture();
  state.linkError = Object.assign(new Error('Popup closed'), { code: 'auth/popup-closed-by-user' });
  await assert.rejects(backend.signInOwner(), { code: 'auth/popup-closed-by-user' });
  assert.equal(state.credentialCalls, 0);
  state.linkError = Object.assign(new Error('Existing Google account'), {
    code: 'auth/credential-already-in-use', credential: { providerId: 'google.com' }
  });
  assert.deepEqual(await backend.signInOwner(), { uid: 'existing-google-id', changedIdentity: true });
  assert.equal(state.credentialCalls, 1, 'Caller can reload when an existing Google identity replaces the browser identity');
}

const snapshot = (data, pending = false) => ({ metadata: { hasPendingWrites: pending }, data: () => data });
const messages = (...ids) => ({ docs: ids.map(id => ({ id, data: () => ({ text: id, senderId: 'sender' }) })) });
const cutoff = { seconds: 100, nanoseconds: 12 };
{
  const { state, backend } = await fixture();
  const calls = [];
  const stop = backend.subscribeLobby((items, error) => calls.push({ items, error }));
  const metadata = state.listeners.at(-1);
  metadata.next(snapshot(undefined));
  const original = state.listeners.at(-1);
  assert.deepEqual(original.ref.constraints, [{ order: ['createdAt', 'desc'] }, { limit: 80 }],
    'A lobby with no metadata still loads its history');
  original.next(messages('newer', 'older'));
  assert.deepEqual(calls.at(-1).items.map(item => item.id), ['older', 'newer']);
  metadata.next(snapshot({ clearedAt: cutoff }, true));
  assert.equal(original.stopped, false, 'Wait for authoritative server cutoff before switching queries');
  metadata.next(snapshot({ clearedAt: cutoff }));
  const filtered = state.listeners.at(-1);
  assert.equal(original.stopped, true);
  assert.deepEqual(calls.at(-1).items, [], 'Clear visible history while replacement query loads');
  assert.deepEqual(filtered.ref.constraints[0], { where: ['createdAt', '>', cutoff] });
  assert.equal(filtered.ref.constraints.at(-1).limit, 80);
  const count = calls.length;
  original.next(messages('stale'));
  assert.equal(calls.length, count, 'Callbacks from replaced listeners cannot reintroduce cleared history');
  const listenerCount = state.listeners.length;
  metadata.next(snapshot({ clearedAt: { ...cutoff } }));
  assert.equal(state.listeners.length, listenerCount, 'Equal cutoff values do not restart message listeners');
  metadata.next(snapshot({ clearedAt: null }));
  assert.equal(filtered.stopped, true);
  assert.equal(state.listeners.at(-1).ref.constraints.length, 2, 'Undo restores unfiltered query');
  stop();
  assert.ok(state.listeners.every(listener => listener.stopped));
  const afterStop = calls.length;
  state.listeners.at(-1).next(messages('late'));
  assert.equal(calls.length, afterStop);
}

{
  const { state, backend } = await fixture();
  const calls = [];
  backend.subscribeLobby((items, error) => calls.push({ items, error }));
  const metadata = state.listeners.at(-1);
  metadata.next(snapshot(undefined));
  const error = new Error('Listener failed');
  metadata.error(error);
  assert.equal(state.listeners.at(-1).stopped, true);
  assert.equal(calls.at(-1).error, error);
  const ownerCalls = [];
  backend.subscribeLobbyMeta((data, error) => ownerCalls.push({ data, error }));
  const ownerListener = state.listeners.at(-1);
  ownerListener.next(snapshot(undefined));
  assert.deepEqual(ownerCalls.at(-1).data, { clearedAt: null, canUndo: false });
  ownerListener.next(snapshot({ clearedAt: cutoff, canUndo: true }));
  assert.equal(ownerCalls.at(-1).data.canUndo, true);
  ownerListener.error(error);
  assert.deepEqual(ownerCalls.at(-1), { data: null, error });
  backend.close();
  assert.ok(state.listeners.every(listener => listener.stopped));
}

{
  const { state, backend } = await fixture();
  await assert.rejects(backend.undoClearLobby(), /no lobby cleanup to undo/);
  assert.equal(state.writes.length, 0);
  await backend.clearLobby();
  assert.deepEqual(state.writes.at(-1), { ref: 'rooms/lobby', data: {
    clearedAt: 'SERVER_TIMESTAMP', previousClearedAt: null, clearedBy: backend.uid,
    canUndo: true, updatedAt: 'SERVER_TIMESTAMP'
  } });
  state.document.clearedAt = cutoff;
  await backend.clearLobby();
  assert.deepEqual(state.writes.at(-1).data.previousClearedAt, cutoff);
  await backend.undoClearLobby();
  assert.deepEqual(state.writes.at(-1).data, {
    clearedAt: cutoff, previousClearedAt: null, clearedBy: backend.uid,
    canUndo: false, updatedAt: 'SERVER_TIMESTAMP'
  });
  const count = state.writes.length;
  await assert.rejects(backend.undoClearLobby(), /no lobby cleanup to undo/);
  assert.equal(state.writes.length, count, 'Undo cannot repeat after the previous cutoff is restored');
  state.document = { clearedAt: cutoff, previousClearedAt: null, canUndo: true };
  await backend.undoClearLobby();
  assert.equal(state.writes.at(-1).data.clearedAt, null, 'Undoing first cleanup restores all retained history');
}

console.log('Chat owner backend: Google identity and role gates, cutoff subscriptions, listener cleanup, and reversible cleanup passed.');
