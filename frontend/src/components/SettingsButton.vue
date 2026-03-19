<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import { usePushStore } from "@/stores/push";
import type { NotificationPrefs } from "@/lib/pushApi";

const router = useRouter();
const auth = useAuthStore();
const push = usePushStore();
const loading = ref(false);
const errorMsg = ref<string | null>(null);
const settingsDialog = ref<HTMLDialogElement | null>(null);

async function openModal() {
  await push.refreshState();
  settingsDialog.value?.showModal();
}

async function onLogout() {
  errorMsg.value = null;
  loading.value = true;
  try {
    await auth.logout();
    await router.replace({ name: "login" });
  } catch (e) {
    errorMsg.value = e instanceof Error ? e.message : "Logout failed";
  } finally {
    loading.value = false;
  }
}

const notifLabels: Record<keyof NotificationPrefs, string> = {
  punishment_proposed: "Nytt straff-förslag",
  punishment_confirmed: "Straff bekräftat",
  punishment_cancelled: "Straff ångrat",
  punishment_taken: "Straff strukna",
  fikapinne_given: "Fikapinne mottagen",
  fikapinne_taken: "Fikapinnar borttagna",
};
</script>

<template>
  <!-- Trigger button -->
  <button class="btn btn-circle btn-ghost" @click="openModal()">
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" class="size-5 fill-current">
      <path
        d="M195.1 9.5C198.1-5.3 211.2-16 226.4-16l59.8 0c15.2 0 28.3 10.7 31.3 25.5L332 79.5c14.1 6 27.3 13.7 39.3 22.8l67.8-22.5c14.4-4.8 30.2 1.2 37.8 14.4l29.9 51.8c7.6 13.2 4.9 29.8-6.5 39.9L447 233.3c.9 7.4 1.3 15 1.3 22.7s-.5 15.3-1.3 22.7l53.4 47.5c11.4 10.1 14 26.8 6.5 39.9l-29.9 51.8c-7.6 13.1-23.4 19.2-37.8 14.4l-67.8-22.5c-12.1 9.1-25.3 16.7-39.3 22.8l-14.4 69.9c-3.1 14.9-16.2 25.5-31.3 25.5l-59.8 0c-15.2 0-28.3-10.7-31.3-25.5l-14.4-69.9c-14.1-6-27.2-13.7-39.3-22.8L73.5 432.3c-14.4 4.8-30.2-1.2-37.8-14.4L5.8 366.1c-7.6-13.2-4.9-29.8 6.5-39.9l53.4-47.5c-.9-7.4-1.3-15-1.3-22.7s.5-15.3 1.3-22.7L12.3 185.8c-11.4-10.1-14-26.8-6.5-39.9L35.7 94.1c7.6-13.2 23.4-19.2 37.8-14.4l67.8 22.5c12.1-9.1 25.3-16.7 39.3-22.8L195.1 9.5zM256.3 336a80 80 0 1 0 -.6-160 80 80 0 1 0 .6 160z"
      />
    </svg>
  </button>

  <!-- Settings modal -->
  <dialog ref="settingsDialog" class="modal">
    <div class="modal-box flex flex-col gap-6">
      <h3 class="text-lg font-bold">Inställningar</h3>

      <!-- Push notifications -->
      <div v-if="push.supported" class="flex flex-col gap-4">
        <div class="flex flex-col gap-1">
          <h4 class="font-semibold">Notiser</h4>
          <span v-if="push.permission === 'denied'" class="text-sm text-base-content/50">
            Blockerade i webbläsaren
          </span>
        </div>

        <!-- Master toggle -->
        <label v-if="push.permission !== 'denied'" class="flex items-center justify-between">
          <span class="text-sm">Aktiverade</span>
          <input
            type="checkbox"
            class="toggle toggle-primary"
            :checked="push.isSubscribed"
            :disabled="push.busy"
            @change="push.isSubscribed ? push.disable() : push.enable()"
          />
        </label>

        <!-- Per-type toggles — only shown when subscribed -->
        <template v-if="push.isSubscribed">
          <label
            v-for="(label, key) in notifLabels"
            :key="key"
            class="flex items-center justify-between"
          >
            <span class="text-sm">{{ label }}</span>
            <input
              type="checkbox"
              class="toggle toggle-sm"
              :checked="push.notifPrefs[key]"
              :disabled="push.prefsBusy"
              @change="push.updateNotifPref(key, !push.notifPrefs[key])"
            />
          </label>
        </template>

        <div v-if="push.error" class="text-sm text-error">{{ push.error }}</div>
      </div>

      <!-- Logout -->
      <div class="flex items-center justify-between">
        <span class="text-sm">Logga ut</span>
        <div class="flex flex-col items-end gap-1">
          <button
            class="btn btn-outline btn-sm btn-error"
            type="button"
            :class="{ 'btn-disabled': loading }"
            @click="onLogout"
          >
            <span v-if="loading" class="loading loading-spinner loading-xs"></span>
            <span v-else>Logga ut</span>
          </button>
          <div v-if="errorMsg" class="text-xs text-error">{{ errorMsg }}</div>
        </div>
      </div>
    </div>

    <!-- Click outside to close -->
    <form method="dialog" class="modal-backdrop">
      <button>close</button>
    </form>
  </dialog>
</template>
