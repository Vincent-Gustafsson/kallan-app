/// <reference lib="webworker" />

import { clientsClaim } from "workbox-core";
import { cleanupOutdatedCaches, precacheAndRoute } from "workbox-precaching";

declare let self: ServiceWorkerGlobalScope;

self.skipWaiting();
clientsClaim();

cleanupOutdatedCaches();
precacheAndRoute(self.__WB_MANIFEST);

self.addEventListener("push", (event) => {
  const data = event.data ? event.data.json() : {};
  const title = data.title || "Notis";
  const options: NotificationOptions = {
    body: data.body || "",
    icon: data.icon || "/pwa-192x192.png",
    data: { url: data.url || "/" },
  };

  event.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener("notificationclick", (event) => {
  event.notification.close();

  const path = (event.notification.data as any)?.url || "/";
  const targetUrl = new URL(path, self.location.origin).href;

  event.waitUntil(
    (async () => {
      const windowClients = await self.clients.matchAll({
        type: "window",
        includeUncontrolled: true,
      });

      if (windowClients.length > 0) {
        const client = windowClients[0];
        await client.focus();
        client.postMessage({ type: "NAVIGATE", to: path });
        return;
      }

      await self.clients.openWindow(targetUrl);
    })(),
  );
});
