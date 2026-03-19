import { defineStore } from "pinia";
import { computed, ref, watch } from "vue";
import { useAuthStore } from "@/stores/auth";
import {
  isPushSupported,
  getBrowserSubscription,
  createBrowserSubscription,
  apiSubscribe,
  apiUnsubscribe,
  apiGetNotificationPrefs,
  apiUpdateNotificationPrefs,
  type NotificationPrefs,
} from "@/lib/pushApi";

const DEFAULT_PREFS: NotificationPrefs = {
  punishment_proposed: true,
  punishment_confirmed: true,
  punishment_cancelled: true,
  punishment_taken: true,
  fikapinne_given: true,
  fikapinne_taken: true,
};

export const usePushStore = defineStore("push", () => {
  const auth = useAuthStore();

  const supported = isPushSupported();

  const permission = ref<NotificationPermission>(
    supported ? Notification.permission : "denied",
  );
  const isSubscribed = ref(false);
  const busy = ref(false);
  const error = ref<string | null>(null);

  const notifPrefs = ref<NotificationPrefs>({ ...DEFAULT_PREFS });
  const prefsBusy = ref(false);
  const prefsLoaded = ref(false);

  // Per-user localStorage key
  const storageKey = computed(
    () => `push_prompt_v1_${auth.user?.id ?? "anon"}`,
  );

  // Reactive prompt choice — updated when storageKey changes (i.e. user switches)
  const promptChoice = ref<string | null>(
    localStorage.getItem(storageKey.value),
  );
  watch(storageKey, (key) => {
    promptChoice.value = localStorage.getItem(key);
    prefsLoaded.value = false;
  });

  function setPromptChoice(value: string) {
    localStorage.setItem(storageKey.value, value);
    promptChoice.value = value;
  }

  function clearPromptChoice() {
    localStorage.removeItem(storageKey.value);
    promptChoice.value = null;
  }

  // True when the first-time prompt should be shown
  const shouldShowPrompt = computed(
    () =>
      supported &&
      auth.ready &&
      !!auth.user &&
      !auth.mustResetPassword &&
      permission.value === "default" &&
      !promptChoice.value,
  );

  async function refreshState() {
    if (!supported) return;
    permission.value = Notification.permission;
    const sub = await getBrowserSubscription();
    isSubscribed.value = !!sub;
    if (isSubscribed.value && !prefsLoaded.value) {
      await loadNotifPrefs();
    }
  }

  async function loadNotifPrefs() {
    if (prefsBusy.value) return;
    prefsBusy.value = true;
    try {
      notifPrefs.value = await apiGetNotificationPrefs();
      prefsLoaded.value = true;
    } catch {
      // non-fatal, keep defaults
    } finally {
      prefsBusy.value = false;
    }
  }

  async function updateNotifPref(
    key: keyof NotificationPrefs,
    value: boolean,
  ) {
    const updated = { ...notifPrefs.value, [key]: value };
    notifPrefs.value = updated;
    prefsBusy.value = true;
    try {
      notifPrefs.value = await apiUpdateNotificationPrefs(updated);
    } catch (e: any) {
      // revert on failure
      notifPrefs.value = { ...notifPrefs.value, [key]: !value };
      error.value = e?.message ?? "Kunde inte spara.";
    } finally {
      prefsBusy.value = false;
    }
  }

  async function enable() {
    if (!supported || busy.value) return;
    busy.value = true;
    error.value = null;
    setPromptChoice("prompted");
    try {
      const perm = await Notification.requestPermission();
      permission.value = perm;
      if (perm !== "granted") {
        setPromptChoice(perm);
        return;
      }
      const sub = await createBrowserSubscription();
      await apiSubscribe(sub);
      isSubscribed.value = true;
      setPromptChoice("enabled");
      await loadNotifPrefs();
    } catch (e: any) {
      clearPromptChoice();
      error.value = e?.message ?? "Något gick fel.";
    } finally {
      busy.value = false;
    }
  }

  async function disable() {
    if (!supported || busy.value) return;
    busy.value = true;
    error.value = null;
    try {
      const sub = await getBrowserSubscription();
      if (sub) {
        await apiUnsubscribe(sub.endpoint);
        await sub.unsubscribe();
      }
      isSubscribed.value = false;
      setPromptChoice("disabled");
    } catch (e: any) {
      error.value = e?.message ?? "Något gick fel.";
    } finally {
      busy.value = false;
    }
  }

  function dismissPrompt() {
    setPromptChoice("declined");
  }

  return {
    supported,
    permission,
    isSubscribed,
    busy,
    error,
    promptChoice,
    shouldShowPrompt,
    notifPrefs,
    prefsBusy,
    prefsLoaded,
    refreshState,
    loadNotifPrefs,
    updateNotifPref,
    enable,
    disable,
    dismissPrompt,
  };
});
