/* XIU DAILY Service Worker - offline app shell */
var CACHE = 'xiu-daily-v62';
var SW_VERSION = 62;
var ASSETS = [
  './',
  './index.html',
  './data.json',
  './manifest.json',
  './icon-192.png',
  './icon-512.png',
  './icon-maskable-512.png'
];

self.addEventListener('install', function (e) {
  e.waitUntil(
    caches.open(CACHE).then(function (c) { return c.addAll(ASSETS); })
      .then(function () { return self.skipWaiting(); })
  );
});

self.addEventListener('activate', function (e) {
  e.waitUntil(
    caches.keys().then(function (keys) {
      return Promise.all(keys.filter(function (k) { return k !== CACHE; })
        .map(function (k) { return caches.delete(k); }));
    }).then(function () { return self.clients.claim(); })
  );
});

self.addEventListener('message', function (e) {
  if (e.data && e.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

self.addEventListener('fetch', function (e) {
  var req = e.request;
  if (req.method !== 'GET') return;
  var url = new URL(req.url);

  // version.json must always come from network (force update mechanism)
  if (url.pathname.indexOf('version.json') !== -1) {
    e.respondWith(fetch(req).catch(function () { return new Response('{"v":0}', {headers:{'Content-Type':'application/json'}}); }));
    return;
  }

  if (url.origin !== location.origin) return; // never touch kvdb API etc.

  // HTML navigations: network-first with 2.5s timeout fallback to cache,
  // so slow networks never leave a blank screen waiting
  if (req.mode === 'navigate' || (req.headers.get('accept') || '').indexOf('text/html') > -1) {
    e.respondWith(
      Promise.race([
        fetch(req).then(function (resp) {
          if (resp && resp.ok && resp.type === 'basic') {
            var cp = resp.clone();
            caches.open(CACHE).then(function (c) { c.put(req, cp); });
          }
          return resp;
        }),
        new Promise(function (resolve) {
          setTimeout(function () {
            caches.match(req).then(function (r) {
              if (r) return resolve(r);
              return caches.match('./index.html').then(resolve);
            }).catch(function () {
              caches.match('./index.html').then(resolve);
            });
          }, 2500);
        })
      ]).catch(function () {
        return caches.match(req).then(function (r) {
          return r || caches.match('./index.html');
        });
      })
    );
    return;
  }

  // Other assets: cache-first, refresh in background
  e.respondWith(
    caches.match(req).then(function (cached) {
      var fetched = fetch(req).then(function (resp) {
        if (resp && resp.ok && resp.type === 'basic') {
          var cp = resp.clone();
          caches.open(CACHE).then(function (c) { c.put(req, cp); });
        }
        return resp;
      }).catch(function () { return cached; });
      return cached || fetched;
    })
  );
});