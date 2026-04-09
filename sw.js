// sw.js - HEADLESS AUTO-SYNC ENGINE V1.7 (GitHub + WP Optimized)
const CACHE_NAME = 'pizza-king-live-cache-v1.7';

// 1. INSTALLATION
self.addEventListener('install', event => {
    self.skipWaiting(); 
});

// 2. ACTIVATION
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheName !== CACHE_NAME) {
                        return caches.delete(cacheName);
                    }
                })
            );
        }).then(() => self.clients.claim())
    );
});

// 3. FETCH STRATEGY (Network-First + API Bypass)
self.addEventListener('fetch', event => {
    if (event.request.method !== 'GET') return;

    const url = new URL(event.request.url);

    // CRITICAL: DO NOT CACHE WORDPRESS OR RENDER APIS!
    // We want live data from the database every single time.
    if (url.hostname.includes('phsar.me') || url.hostname.includes('render.com') || url.hostname.includes('api.qrserver.com')) {
        return; // Bypass the service worker entirely for APIs
    }

    // For GitHub Pages (HTML, CSS, JS, Images) -> Network First, fallback to cache
    event.respondWith(
        fetch(event.request)
            .then(liveResponse => {
                if (liveResponse && liveResponse.status === 200 && liveResponse.type === 'basic') {
                    const responseToCache = liveResponse.clone();
                    caches.open(CACHE_NAME).then(cache => {
                        cache.put(event.request, responseToCache);
                    });
                }
                return liveResponse;
            })
            .catch(() => {
                return caches.match(event.request);
            })
    );
});
