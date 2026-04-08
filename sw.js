const CACHE_NAME = 'pizza-king-v56';
const ASSETS = [
  'index.html',
  'manifest.json',
  'logo.png',
  'https://telegram.org/js/telegram-web-app.js',
  'https://html2canvas.hertzen.com/dist/html2canvas.min.js'
];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE_NAME).then(cache => cache.addAll(ASSETS)));
});

self.addEventListener('fetch', (e) => {
  e.respondWith(caches.match(e.request).then(res => res || fetch(e.request)));
});
