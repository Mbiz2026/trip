/* trip系ツール Service Worker(航空券サーチ司令塔 + マイルコンパス)
   方針: 本体(ナビゲーション)はネット優先(常に最新)、圏外ならキャッシュで起動。
   アイコン等の静的ファイルはキャッシュ優先。外部サイトへのリンクは一切触らない。 */
const VERSION = 'trip-tools-v2';
const ASSETS = [
  './',
  'mile.html',
  'manifest.webmanifest',
  'icon-192.png',
  'icon-512.png',
  'icon-512-maskable.png',
  'icon-180.png'
];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(VERSION).then((c) => c.addAll(ASSETS)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== VERSION).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== location.origin) return; // 外部サイトは素通し

  if (req.mode === 'navigate') {
    // 本体: ネット優先 → 圏外はキャッシュ(ページごとに保存。'./'固定にすると
    // mile.htmlを開いたとき司令塔のオフラインキャッシュが上書きされてしまう)
    e.respondWith(
      fetch(req)
        .then((res) => {
          const copy = res.clone();
          caches.open(VERSION).then((c) => c.put(req, copy));
          return res;
        })
        .catch(() => caches.match(req).then((hit) => hit || caches.match('./')))
    );
    return;
  }
  // 静的ファイル: キャッシュ優先 → 無ければ取得して保存
  e.respondWith(
    caches.match(req).then(
      (hit) =>
        hit ||
        fetch(req).then((res) => {
          const copy = res.clone();
          caches.open(VERSION).then((c) => c.put(req, copy));
          return res;
        })
    )
  );
});
