<script setup lang="ts">
import { ref, watchEffect } from "vue";
import { usePushStore } from "@/stores/push";

const push = usePushStore();
const dialogRef = ref<HTMLDialogElement | null>(null);

watchEffect(() => {
  if (push.shouldShowPrompt && !dialogRef.value?.open) {
    push.error = null;
    dialogRef.value?.showModal();
  }
});

async function onEnable() {
  await push.enable();
  if (push.permission !== "default") {
    dialogRef.value?.close();
  }
}

function onLater() {
  push.dismissPrompt();
  dialogRef.value?.close();
}
</script>

<template>
  <dialog ref="dialogRef" class="modal">
    <div class="modal-box">
      <h3 class="text-lg font-bold">Vill du aktivera notiser?</h3>

      <div v-if="push.error" class="alert alert-error mb-3">
        <span>{{ push.error }}</span>
      </div>

      <div class="flex gap-2 justify-end">
        <button class="btn btn-ghost" :disabled="push.busy" @click="onLater">Inte nu</button>
        <button class="btn btn-primary" :disabled="push.busy" @click="onEnable">
          <span v-if="push.busy" class="loading loading-spinner loading-sm"></span>
          <span v-else>Aktivera</span>
        </button>
      </div>
    </div>

    <form method="dialog" class="modal-backdrop">
      <button @click="onLater">close</button>
    </form>
  </dialog>
</template>
