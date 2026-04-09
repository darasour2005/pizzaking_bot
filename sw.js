// sw.js - DYNAMIC AUTO-SYNC ENGINE (For Active Development & Live Updates)
const CACHE_NAME = 'pizza-king-live-cache-v1';

// 1. INSTALLATION: Take over immediately
self.addEventListener('install', event => {
    self.skipWaiting(); 
});

// 2. ACTIVATION: Claim the browser immediately
self.addEventListener('activate', event => {
    event.waitUntil(self.clients.claim()); 
});

// 3. THE AUTO-SYNC FETCH STRATEGY (Network-First)
self.addEventListener('fetch', event => {
    // Only intercept basic web requests (HTML, CSS, JS, Images)
    if (event.request.method !== 'GET') return;

    event.respondWith(
        fetch(event.request)
            .then(liveResponse => {
                // SUCCESS: We are online and the server responded!
                // Save a silent, fresh backup of this file to the phone's hard drive
                if (liveResponse && liveResponse.status === 200 && liveResponse.type === 'basic') {
                    const responseToCache = liveResponse.clone();
                    caches.open(CACHE_NAME).then(cache => {
                        cache.put(event.request, responseToCache);
                    });
                }
                // Deliver the fresh code to the user instantly
                return liveResponse;
            })
            .catch(() => {
                // FAILURE: The user is offline or the server is down.
                // Pull the most recent backup from the cache so the app doesn't crash.
                return caches.match(event.request);
            })
    );
});
