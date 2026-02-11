// chache everytime you update so service worker knows that you updated
const CACHE_NAME = "tutor-app-v8";

const FILES_TO_CACHE = [
  "/",
  "/static/offline.html",
  "/static/manifest.json",
  "/static/css/style.css",
  "/static/images/icon.png",
  "/static/images/john.jpg",
  "/static/images/jane.jpg",
  "/static/images/mike.jpg",
  "/static/images/sarah.jpg",
  "/static/images/icon-192.png",
  "/static/images/icon-512.png",
];

// Install Event - Caches the files
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log("Caching files...");
      return cache.addAll(FILES_TO_CACHE);
    }),
  );
  // Forces the waiting service worker to become the active one immediately
  self.skipWaiting();
});

// Activate Event - Cleans up old caches
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            console.log("Deleting old cache:", key);
            return caches.delete(key);
          }
        }),
      );
    }),
  );
  // Claims control of all clients immediately
  self.clients.claim();
});

// Fetch Event - Serves files from cache or network
self.addEventListener("fetch", (event) => {
  // 1. Navigation Requests (HTML Pages)
  if (event.request.mode === "navigate") {
    event.respondWith(
      fetch(event.request).catch(() => {
        // If network fails, serve the offline page
        return caches.match("/static/offline.html");
      }),
    );
    return;
  }

  // 2. Asset Requests (CSS, Images, JS)
  event.respondWith(
    caches
      .match(event.request, { ignoreSearch: true })
      .then((cachedResponse) => {
        // If found in cache, return it
        if (cachedResponse) {
          return cachedResponse;
        }
        // If not in cache, try network
        return fetch(event.request);
      }),
  );
});
