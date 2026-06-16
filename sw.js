// Help Kit offline service worker. Precaches all guides + PDFs so the kit works
// fully offline after one visit. Cache-first; network used only to fill the cache.
const CACHE = "help-kit-v32";
const ASSETS = [
  "/help-kit/",
  "/help-kit/404.html",
  "/help-kit/allergy/",
  "/help-kit/allergy/allergy-onepager.pdf",
  "/help-kit/bleeding/",
  "/help-kit/bleeding/bleeding-onepager.pdf",
  "/help-kit/burns/",
  "/help-kit/burns/burns-onepager.pdf",
  "/help-kit/choking/",
  "/help-kit/choking/choking-onepager.pdf",
  "/help-kit/cold/",
  "/help-kit/cold/cold-onepager.pdf",
  "/help-kit/cpr/",
  "/help-kit/cpr/cpr-onepager.pdf",
  "/help-kit/favicon.ico",
  "/help-kit/heart/",
  "/help-kit/heart/heart-onepager.pdf",
  "/help-kit/heat/",
  "/help-kit/heat/buddy-check.html",
  "/help-kit/heat/cooling-guide.html",
  "/help-kit/heat/flyer.html",
  "/help-kit/heat/heat-onepager.pdf",
  "/help-kit/heat/organizer-60-minute-setup.html",
  "/help-kit/heat/scripts.html",
  "/help-kit/help-kit-print-pack.pdf",
  "/help-kit/icon-192.png",
  "/help-kit/icon-512.png",
  "/help-kit/localize.html",
  "/help-kit/manifest.webmanifest",
  "/help-kit/naloxone/",
  "/help-kit/naloxone/naloxone-onepager.pdf",
  "/help-kit/og-image.png",
  "/help-kit/ors/",
  "/help-kit/ors/ors-onepager.pdf",
  "/help-kit/seizure/",
  "/help-kit/seizure/seizure-onepager.pdf",
  "/help-kit/smoke/",
  "/help-kit/smoke/smoke-onepager.pdf",
  "/help-kit/stroke/",
  "/help-kit/stroke/stroke-onepager.pdf",
  "/help-kit/style.css",
  "/help-kit/triage/",
  "/help-kit/triage/triage-onepager.pdf"
];
self.addEventListener("install", (e) => {
  e.waitUntil(
    caches.open(CACHE).then((c) => c.addAll(ASSETS)).then(() => self.skipWaiting())
  );
});
self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});
self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;
  e.respondWith(
    caches.match(req).then((hit) => {
      if (hit) return hit;
      return fetch(req).then((res) => {
        // Cache successful same-origin responses for later offline use.
        if (res && res.status === 200 && res.type === "basic") {
          const copy = res.clone();
          caches.open(CACHE).then((c) => c.put(req, copy));
        }
        return res;
      }).catch(() => {
        // Offline fallback for page navigations: serve the styled custom 404
        // page (it uses root-absolute asset paths so it renders correctly at any
        // URL), falling back to the home page if that is somehow not cached.
        if (req.mode === "navigate") {
          return caches.match("/help-kit/404.html").then((r) => r || caches.match("/help-kit/"));
        }
        return new Response("", { status: 504, statusText: "Offline" });
      });
    })
  );
});
