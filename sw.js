// Basic Service Worker for caching static assets
const CACHE_NAME = 'charming-glance-cache-v1';
const urlsToCache = [
  '/',
  '/index.html',
  '/assets/site.min.css',
  '/assets/runtime.min.js',
  // Add other assets you want cached here
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(self.clients.claim());
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request).then(response => {
      return response || fetch(event.request);
    })
  );
});
