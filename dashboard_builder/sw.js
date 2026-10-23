/* ============================================================================
   Civic Benevolence Dashboard: offline shell (service worker)
   ----------------------------------------------------------------------------
   Authored by Claude (Anthropic) for the requesting user on 2026-10-15.
   Purpose: let the dashboard page open without a connection. The app is one self-contained file, so this
   worker only has to keep a copy of the page itself. Live data is never cached here: the page already
   keeps its own copies in IndexedDB and labels them Cached.
   Strategy: network first for page loads (so you always get the newest page when online), then the saved
   copy when the network fails. Only GET page navigations are touched; every other request (data APIs,
   relays, downloads) goes straight to the network, untouched.
   Install: put this file next to index.html (same folder), serve over https or localhost, then use
   "Offline mode" in About & Your Data. It does nothing until the user turns that on.
   Remove: use "Turn off" in the same card, or delete this file; the cache is named civic-shell-v1 and is
   deleted on turn-off and on version change. No analytics, no network calls of its own.
   Verification: exercised in a Node sandbox with fake caches, fetch and events (install, failed install,
   activation cleanup, online page load with cache fill, offline fallback, non-page requests untouched).
   Not run in a real browser.
   ============================================================================ */
const CACHE = 'civic-shell-v1';

self.addEventListener('install', e => {
  // Best effort: if the page is not at ./index.html, the first online page load fills the cache instead.
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(['./', './index.html'])).catch(() => {}).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k.indexOf('civic-shell-') === 0 && k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

self.addEventListener('fetch', e => {
  const r = e.request;
  if (r.method !== 'GET' || r.mode !== 'navigate') return; // only the page itself
  e.respondWith(
    fetch(r).then(res => {
      if (res && res.ok) { const copy = res.clone(); caches.open(CACHE).then(c => c.put(r, copy)).catch(() => {}); }
      return res;
    }).catch(() => caches.match(r).then(m => m || caches.match('./index.html')).then(m => m || caches.match('./')))
  );
});
