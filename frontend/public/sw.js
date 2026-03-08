// ILMA Service Worker - Cache-first with network fallback
const CACHE_NAME = 'ilma-v3';
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/fonts/inter-latin.woff2',
  '/fonts/inter-latin-ext.woff2',
  '/fonts/nunito-latin.woff2',
  '/fonts/nunito-latin-ext.woff2',
];

// Install: pre-cache static assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(STATIC_ASSETS);
    })
  );
  self.skipWaiting();
});

// Activate: clean old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
      );
    })
  );
  self.clients.claim();
});

// Fetch: strategy depends on request type
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // API calls & cross-origin: network-first
  if (url.pathname.startsWith('/api') || url.hostname !== self.location.hostname) {
    event.respondWith(
      fetch(request)
        .then((response) => {
          if (request.method === 'GET' && response.ok) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(request, clone));
          }
          return response;
        })
        .catch(() => caches.match(request))
    );
    return;
  }

  // Navigation requests (HTML): network-first so we always get the latest index.html
  // This prevents stale HTML from referencing old chunk hashes after a rebuild
  if (request.mode === 'navigate') {
    event.respondWith(
      fetch(request)
        .then((response) => {
          if (response.ok) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(request, clone));
          }
          return response;
        })
        .catch(() => caches.match(request))
    );
    return;
  }

  // Hashed assets (/assets/*): cache-first (immutable by content hash)
  // Other static assets: cache-first with network fallback
  event.respondWith(
    caches.match(request).then((cached) => {
      return cached || fetch(request).then((response) => {
        if (response.ok) {
          const clone = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(request, clone));
        }
        return response;
      });
    })
  );
});

// Background Sync support
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-progress') {
    event.waitUntil(syncPendingItems());
  }
});

async function syncPendingItems() {
  try {
    // Open IndexedDB and get pending items
    const db = await new Promise((resolve, reject) => {
      const req = indexedDB.open('ilma-db', 2);
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => reject(req.error);
    });

    const tx = db.transaction('syncQueue', 'readonly');
    const store = tx.objectStore('syncQueue');
    const items = await new Promise((resolve, reject) => {
      const req = store.getAll();
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => reject(req.error);
    });

    if (!items || items.length === 0) return;

    // Try to sync via the batch endpoint
    const response = await fetch('/api/v1/offline/sync', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ events: items.map(i => i.payload) }),
    });

    if (response.ok) {
      // Clear synced items
      const clearTx = db.transaction('syncQueue', 'readwrite');
      clearTx.objectStore('syncQueue').clear();
    }
  } catch (e) {
    // Will retry on next sync event
    console.log('[SW] Background sync failed, will retry:', e);
  }
}

// Listen for update messages from the app
self.addEventListener('message', (event) => {
  if (event.data === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});
