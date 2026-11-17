const CACHE_NAME = 'hsla-pwa-v2';
const LOCAL = ['./', './index.html', './manifest.json', './icon-192.png', './icon-512.png'];
const CDN = [
  'https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js',
  'https://cdn.plot.ly/plotly-2.35.2.min.js'
];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE_NAME).then(async (cache) => {
    await cache.addAll(LOCAL);
    await Promise.all(CDN.map(u => cache.add(u).catch(() => {})));
  }));
  self.skipWaiting();
});

self.addEventListener('activate', (e) => {
  e.waitUntil(caches.keys().then(keys =>
    Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
  ));
  self.clients.claim();
});

self.addEventListener('fetch', (e) => {
  if (e.request.method !== 'GET') return;
  e.respondWith(caches.match(e.request).then(res => res || fetch(e.request).then(net => {
    const copy = net.clone();
    caches.open(CACHE_NAME).then(c => c.put(e.request, copy));
    return net;
  })));
});
