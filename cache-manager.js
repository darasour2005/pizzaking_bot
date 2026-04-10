// cache-manager.js - MASTER SMART CACHE ENGINE V1.0
// Zero-Omission Protocol: Universal Cache with TTL (Time-To-Live)

const CacheEngine = {
    /**
     * Save data to local storage with a timestamp
     */
    set: function(key, data) {
        const cachePayload = {
            timestamp: Date.now(),
            data: data
        };
        localStorage.setItem(key, JSON.stringify(cachePayload));
    },

    /**
     * Load data from cache ONLY if it is newer than the allowed hours (TTL)
     * @param {string} key - The cache name
     * @param {number} hoursValid - How many hours before it expires (e.g., 24 for products, 0.05 for orders)
     */
    get: function(key, hoursValid) {
        const rawCache = localStorage.getItem(key);
        if (!rawCache) return null; // No cache found

        try {
            const parsedCache = JSON.parse(rawCache);
            const cacheAgeInMilliseconds = Date.now() - parsedCache.timestamp;
            const maxAgeInMilliseconds = hoursValid * 60 * 60 * 1000;

            if (cacheAgeInMilliseconds > maxAgeInMilliseconds) {
                // Cache is too old. Destroy it and force a fresh pull.
                localStorage.removeItem(key);
                return null;
            }

            // Cache is valid and fresh!
            return parsedCache.data;
        } catch (e) {
            // If cache gets corrupted, clear it safely
            localStorage.removeItem(key);
            return null;
        }
    },

    /**
     * Manually wipe a specific cache (Useful for Pull-to-Refresh buttons)
     */
    clear: function(key) {
        localStorage.removeItem(key);
    }
};
