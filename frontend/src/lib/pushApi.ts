import { apiCsrf } from "@/lib/authApi";

const VAPID_PUBLIC_KEY_URL = "/api/push/vapid-public-key";
const SUBSCRIBE_URL = "/api/push/subscribe";
const UNSUBSCRIBE_URL = "/api/push/unsubscribe";
const NOTIFICATION_PREFS_URL = "/api/push/notification-prefs";

export type NotificationPrefs = {
  punishment_proposed: boolean;
  punishment_confirmed: boolean;
  punishment_cancelled: boolean;
  punishment_taken: boolean;
  fikapinne_given: boolean;
  fikapinne_taken: boolean;
};

function getCookie(name: string) {
  const m = document.cookie.match(new RegExp(`(?:^|; )${name}=([^;]*)`));
  return m ? decodeURIComponent(m[1]!) : null;
}

function csrfHeader(): Record<string, string> {
  const token = getCookie("csrftoken");
  return token ? { "X-CSRFToken": token } : {};
}

function urlBase64ToUint8Array(base64String: string): Uint8Array<ArrayBuffer> {
  const padding = "=".repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding).replace(/-/g, "+").replace(/_/g, "/");
  const raw = atob(base64);
  return Uint8Array.from([...raw].map((c) => c.charCodeAt(0))) as Uint8Array<ArrayBuffer>;
}

export function isPushSupported(): boolean {
  return "Notification" in window && "serviceWorker" in navigator && "PushManager" in window;
}

export async function getBrowserSubscription(): Promise<PushSubscription | null> {
  const reg = await navigator.serviceWorker.ready;
  return reg.pushManager.getSubscription();
}

export async function createBrowserSubscription(): Promise<PushSubscription> {
  const reg = await navigator.serviceWorker.ready;

  const existing = await reg.pushManager.getSubscription();
  if (existing) return existing;

  const res = await fetch(VAPID_PUBLIC_KEY_URL, {
    credentials: "include",
    headers: { Accept: "application/json" },
  });
  const { publicKey } = await res.json();

  return reg.pushManager.subscribe({
    userVisibleOnly: true,
    applicationServerKey: urlBase64ToUint8Array(publicKey),
  });
}

export async function apiSubscribe(sub: PushSubscription): Promise<void> {
  await apiCsrf();
  const res = await fetch(SUBSCRIBE_URL, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
      ...csrfHeader(),
    },
    body: JSON.stringify(sub),
  });
  if (!res.ok) throw new Error("Kunde inte aktivera notiser.");
}

export async function apiUnsubscribe(endpoint: string): Promise<void> {
  await apiCsrf();
  const res = await fetch(UNSUBSCRIBE_URL, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
      ...csrfHeader(),
    },
    body: JSON.stringify({ endpoint }),
  });
  if (!res.ok) throw new Error("Kunde inte inaktivera notiser.");
}

export async function apiGetNotificationPrefs(): Promise<NotificationPrefs> {
  const res = await fetch(NOTIFICATION_PREFS_URL, {
    credentials: "include",
    headers: { Accept: "application/json" },
  });
  if (!res.ok) throw new Error("Kunde inte hämta notis-inställningar.");
  return res.json();
}

export async function apiUpdateNotificationPrefs(
  prefs: NotificationPrefs,
): Promise<NotificationPrefs> {
  await apiCsrf();
  const res = await fetch(NOTIFICATION_PREFS_URL, {
    method: "PUT",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
      ...csrfHeader(),
    },
    body: JSON.stringify(prefs),
  });
  if (!res.ok) throw new Error("Kunde inte spara notis-inställningar.");
  return res.json();
}
