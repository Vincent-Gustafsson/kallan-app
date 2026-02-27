<script setup lang="ts">
import { computed, ref, watchEffect } from "vue";
import { useAuthStore } from "@/stores/auth";
import { apiCsrf } from "@/lib/authApi";

const auth = useAuthStore();

const dialogRef = ref<HTMLDialogElement | null>(null);
const busy = ref(false);
const errorMsg = ref<string | null>(null);

// These match your router endpoints (assuming mounted at /api/push)
const VAPID_PUBLIC_KEY_URL = "/api/push/vapid-public-key";
const SUBSCRIBE_URL = "/api/push/subscribe";

const storageKey = computed(() => {
  const id = auth.user?.id;
  return id != null ? `push_prompt_v1_${id}` : "push_prompt_v1_anon";
});

function hasChoice() {
  return Boolean(localStorage.getItem(storageKey.value));
}
function setChoice(v: string) {
  localStorage.setItem(storageKey.value, v);
}
function clearChoice() {
  localStorage.removeItem(storageKey.value);
}

function getCookie(name: string) {
  const m = document.cookie.match(new RegExp(`(?:^|; )${name}=([^;]*)`));
  return m ? decodeURIComponent(m[1]) : null;
}
function csrfHeader() {
  const token = getCookie("csrftoken");
  return token ? { "X-CSRFToken": token } : {};
}

function urlBase64ToUint8Array(base64String: string) {
  const padding = "=".repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding).replace(/-/g, "+").replace(/_/g, "/");
  const raw = atob(base64);
  return Uint8Array.from([...raw].map((c) => c.charCodeAt(0)));
}

function canUsePush() {
  return "Notification" in window && "serviceWorker" in navigator && "PushManager" in window;
}

function shouldOpen() {
  if (!auth.ready || !auth.user) return false;
  if (auth.mustResetPassword) return false;
  if (!canUsePush()) return false;
  if (hasChoice()) return false;
  if (Notification.permission !== "default") return false;
  if (dialogRef.value?.open) return false;
  return true;
}

async function ensureSubscribedAndPosted() {
  // With VitePWA, the SW is registered globally; wait until it’s ready
  const reg = await navigator.serviceWorker.ready;

  const { publicKey } = await fetch(VAPID_PUBLIC_KEY_URL, {
    method: "GET",
    credentials: "include",
    headers: { Accept: "application/json" },
  }).then((r) => r.json());

  const existing = await reg.pushManager.getSubscription();
  const sub =
    existing ||
    (await reg.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: urlBase64ToUint8Array(publicKey),
    }));

  await apiCsrf();

  const res = await fetch(SUBSCRIBE_URL, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
      ...csrfHeader(),
    },
    body: JSON.stringify(sub), // matches your SubscriptionIn schema
  });

  if (!res.ok) throw new Error("Kunde inte aktivera notiser. Försök igen.");
}

async function onEnable() {
  if (busy.value) return;
  busy.value = true;
  errorMsg.value = null;

  // mark immediately so we don’t reopen if they dismiss the browser prompt
  setChoice("prompted");

  try {
    const perm = await Notification.requestPermission();

    if (perm !== "granted") {
      setChoice(perm); // "denied" or "default"
      dialogRef.value?.close();
      return;
    }

    await ensureSubscribedAndPosted();
    setChoice("enabled");
    dialogRef.value?.close();
  } catch (e: any) {
    clearChoice(); // allow retry later
    errorMsg.value = e?.message ?? "Något gick fel. Försök igen.";
  } finally {
    busy.value = false;
  }
}

function onLater() {
  // no backend call
  setChoice("declined");
  dialogRef.value?.close();
}

watchEffect(() => {
  if (shouldOpen()) {
    errorMsg.value = null;
    dialogRef.value?.showModal();
  }
});
</script>

<template>
  <dialog ref="dialogRef" class="modal">
    <div class="modal-box">
      <h3 class="text-lg font-bold">Vill du aktivera notiser?</h3>

      <div v-if="errorMsg" class="alert alert-error mb-3">
        <span>{{ errorMsg }}</span>
      </div>

      <div class="flex gap-2 justify-end">
        <button class="btn btn-ghost" :disabled="busy" @click="onLater">Inte nu</button>
        <button class="btn btn-primary" :disabled="busy" @click="onEnable">
          <span v-if="busy" class="loading loading-spinner loading-sm"></span>
          <span v-else>Aktivera</span>
        </button>
      </div>
    </div>

    <form method="dialog" class="modal-backdrop">
      <button @click="onLater">close</button>
    </form>
  </dialog>
</template>
