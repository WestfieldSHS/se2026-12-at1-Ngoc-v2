// Names the cache so we can version it and force updates when we change files
const CACHE_NAME = "tutor-app-v7";

// Lists only files that are guaranteed to exist and are safe to precache
const FILES_TO_CACHE = [
  "/", // Caches the home page so it can open offline
  "/static/offline.html", // Caches the offline fallback page
  "/static/manifest.json", // Caches the PWA manifest so it does not fail offline
  "/static/css/style.css", // Caches the stylesheet for consistent design offline
  "/static/images/icon.png", // Caches the site logo (and tab icon if you use it)
  "/static/images/john.jpg", // Caches tutor image
  "/static/images/jane.jpg", // Caches tutor image
  "/static/images/mike.jpg", // Caches tutor image
  "/static/images/sarah.jpg", // Caches tutor image
  "/static/images/icon-192.png", // Caches the PWA icon
  "/static/images/icon-512.png", // Caches the PWA icon
]; // Ends the precache list

// Runs once when the service worker is installed
self.addEventListener("install", (event) => {
  // Forces the browser to wait until caching finishes before completing install
  event.waitUntil(
    // Opens (or creates) the cache storage using our versioned name
    caches.open(CACHE_NAME).then((cache) => {
      // Adds all listed files to the cache (fails if any file path is wrong)
      return cache.addAll(FILES_TO_CACHE);
    })
  ); // Ends install waitUntil
}); // Ends install event listener

// Runs when the service worker activates (after install)
self.addEventListener("activate", (event) => {
  // Forces the browser to wait while we clean up old cache versions
  event.waitUntil(
    // Gets every cache name currently stored in the browser
    caches.keys().then((keys) => {
      // Deletes all caches that do not match the current version name
      return Promise.all(
        keys.map((key) => {
          // Checks if this cache is an older version
          if (key !== CACHE_NAME) {
            // Deletes the old cache to prevent conflicts
            return caches.delete(key);
          } // Ends old-cache check
          // Returns null when we keep the current cache
          return null;
        })
      ); // Ends Promise.all
    })
  ); // Ends activate waitUntil
}); // Ends activate event listener

// Runs every time the browser requests something (pages, images, css, js)
self.addEventListener("fetch", (event) => {
  // Checks if this request is loading a full HTML page (navigation)
  const isNavigation = event.request.mode === "navigate";

  // Intercepts the request and responds with our custom logic
  event.respondWith(
    // First tries to return a cached version of the request (ignores ?query strings)
    caches.match(event.request, { ignoreSearch: true }).then((cached) => {
      // If we found a cached response, return it immediately
      if (cached) {
        return cached;
      } // Ends cached check

      // If it is a page navigation, try network, then fall back to offline page
      if (isNavigation) {
        // Attempts to fetch the page from the internet when online
        return fetch(event.request).catch(() => {
          // If offline, return the offline fallback page from cache
          return caches.match("/static/offline.html");
        });
      } // Ends navigation handling

      // For non-page files (images/css), try network, then try cache
      return fetch(event.request).catch(() => {
        // If offline, try to find a cached copy of that file
        return caches.match(event.request, { ignoreSearch: true });
      }); // Ends non-navigation handling
    })
  ); // Ends respondWith
}); // Ends fetch event listener