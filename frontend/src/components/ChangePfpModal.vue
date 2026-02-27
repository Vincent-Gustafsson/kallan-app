<script setup lang="ts">
import { computed, onBeforeUnmount, ref } from "vue";
import { useAuthStore } from "@/stores/auth";

import ProfilePicture from "@/components/ProfilePicture.vue";

const auth = useAuthStore();

const currentAvatarUrl = computed(() => auth.user?.avatar_url ?? "/kallan.svg");

const fileEl = ref<HTMLInputElement | null>(null);
const file = ref<File | null>(null);

const previewUrl = ref<string | null>(null);
let lastUrl: string | null = null;

const avatarSrc = computed(() => previewUrl.value ?? currentAvatarUrl.value);

const loading = ref(false);
const errorMsg = ref<string | null>(null);

function openPicker() {
  fileEl.value?.click();
}

function onPick(e: Event) {
  errorMsg.value = null;

  const input = e.target as HTMLInputElement;
  const f = input.files?.[0];
  if (!f) return;

  // Basic client-side validation (optional)
  if (!f.type.startsWith("image/")) {
    errorMsg.value = "Please pick an image file.";
    input.value = "";
    return;
  }
  const maxBytes = 5 * 1024 * 1024;
  if (f.size > maxBytes) {
    errorMsg.value = "Image too large (max 5MB).";
    input.value = "";
    return;
  }

  file.value = f;

  if (lastUrl) URL.revokeObjectURL(lastUrl);
  lastUrl = URL.createObjectURL(f);
  previewUrl.value = lastUrl;

  // allow selecting the same file again
  input.value = "";
}

async function save() {
  if (!file.value) return;

  errorMsg.value = null;
  loading.value = true;

  try {
    await auth.uploadAvatar(file.value);

    // clear local preview after successful upload
    previewUrl.value = null;
    file.value = null;

    // close modal (daisyUI)
    (document.getElementById("my_modal_1") as HTMLDialogElement | null)?.close();
  } catch (e) {
    errorMsg.value = e instanceof Error ? e.message : "Avatar upload failed";
  } finally {
    loading.value = false;
  }
}

onBeforeUnmount(() => {
  if (lastUrl) URL.revokeObjectURL(lastUrl);
});
</script>

<template>
  <dialog id="my_modal_1" class="modal">
    <div class="modal-box">
      <h3 class="text-lg font-bold">Byt profilbild</h3>

      <input ref="fileEl" type="file" accept="image/*" class="hidden" @change="onPick" />

      <div class="flex flex-col items-center gap-8 mt-10">
        <ProfilePicture :avatarUrl="avatarSrc" />

        <div
          class="alert alert-error text-sm shadow-md text-center justify-center min-h-12 transition-opacity duration-150 w-full"
          :class="errorMsg ? 'opacity-100' : 'opacity-0 pointer-events-none'"
          aria-live="polite"
        >
          <span>{{ errorMsg ?? "\u00A0" }}</span>
        </div>

        <div class="join w-full">
          <button
            type="button"
            class="btn btn-neutral btn-lg join-item flex-1"
            :disabled="loading"
            @click="openPicker"
          >
            Välj bild
          </button>

          <button
            type="button"
            class="btn btn-primary btn-lg join-item flex-1"
            :disabled="loading || !file"
            @click="save"
          >
            <span v-if="loading" class="loading loading-spinner"></span>
            <span v-else>Spara</span>
          </button>
        </div>
      </div>
    </div>

    <form method="dialog" class="modal-backdrop">
      <button aria-label="close">close</button>
    </form>
  </dialog>
</template>
