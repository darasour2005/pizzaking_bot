// sw.js - AGGRESSIVE CACHE CONTROLLER V3.0

// 🛑 ARCHITECT RULE: YOU MUST CHANGE THIS NAME EVERY TIME YOU UPLOAD NEW CODE
const CACHE_NAME = 'pizza-king-cache-v3.0'; 

const urlsToCache = [
    '/',
    '/index.html',
    '/orders.html',
    '/movie.html',
    '/sale.html',
    '/style.css',
    '/nav.js',
    '/pwa.js',
    '/logo.png'
];

// 1. INSTALLATION: Force the new worker to take over IMMEDIATELY
self.addEventListener('install', event => {
    self.skipWaiting(); // Kills the zombie worker
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => {
            console.log('Opened cache');
            return cache.addAll(urlsToCache);
        })
    );
});

// 2. ACTIVATION: Annihilate any old versions of the cache
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    // If the cache name doesn't match our current version, delete it
                    if (cacheName !== CACHE_NAME) {
                        console.log('Destroying old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        }).then(() => self.clients.claim()) // Force all open app windows to use the new code
    );
});

// 3. FETCH STRATEGY: Network-First (Always check the internet for updates first!)
self.addEventListener('fetch', event => {
    event.respondWith(
        fetch(event.request)
            .then(response => {
                // If we got a valid response from the internet, clone it and update the cache
                if (response && response.status === 200 && response.type === 'basic') {
                    const responseToCache = response.clone();
                    caches.open(CACHE_NAME).then(cache => {
                        cache.put(event.request, responseToCache);
                    });
                }
                return response;
            })
            .catch(() => {
                // If the internet is down, fallback to the saved PWA files
                return caches.match(event.request);
            })
    );
});
