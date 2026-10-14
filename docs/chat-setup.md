# Connect the community chat

The Chat tab needs Firebase because GitHub Pages cannot host a realtime database. The web app config in `chat-config.json` identifies the Firebase project; it is public configuration, not a secret. Access is controlled by Firebase Authentication and `firestore.rules`.

1. In the [Firebase console](https://console.firebase.google.com/), create a project for this site. Disable Google Analytics unless you want it.
2. In **Project settings → Your apps**, register a **Web** app. Copy its `apiKey`, `authDomain`, `projectId`, and `appId` into the root `chat-config.json`. Do not paste a service account key or private key into the site.
3. In **Authentication → Sign-in method**, enable **Anonymous**. Check **Authentication → Settings → Authorized domains** and add `ekstren.github.io` if it is not listed. Visitors will type a display name, while Firebase gives each browser an anonymous account used to protect private messages. These accounts persist in browser storage; clearing it creates a new identity and loses access to old DMs. Display names are not verified or unique.
4. In **Firestore Database**, create a database in a region close to most visitors. Start in production mode; the rules deployed in the next step grant the required access. Never leave the test-mode default rules in place.
5. From this repository root, run `npx firebase-tools login`, then `npx firebase-tools use --add` to select the new project, then `npx firebase-tools deploy --only firestore:rules`. Alternatively, paste the contents of `firestore.rules` into **Firestore Database → Rules** and publish them. Confirm the published rules match this file before publishing the chat UI.
6. Run `npm test`, commit the config and site changes, and publish via the existing GitHub Pages workflow. Open the site in two fresh browser profiles to check lobby messages, DMs, and the shared drawing board.

The name list shows recent participants, not live presence. DMs are readable only by their two Firebase account IDs under the supplied rules, but they are **not end-to-end encrypted**. Anyone can choose the same display name, so the UI also shows an account ID suffix. The shared board stores short strokes in Firestore. The site reads only the newest 120 drawing events and 80 messages per room; older records remain in Firestore. Keep an eye on usage in the Firebase console for a public site, and consider App Check if automated abuse appears.

To roll back the release, revert the site commit. If you need to disable chat immediately, replace Firestore rules with deny-all rules in the Firebase console; this also disables the board and DMs until restored.
