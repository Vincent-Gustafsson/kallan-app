<script setup lang="ts">
import { ref } from "vue";
import { useUsersStore } from "@/stores/users";
import { apiGiveFikapinne } from "@/lib/fikapinnarApi";

const usersStore = useUsersStore();

const dialogRef = ref<HTMLDialogElement | null>(null);
const selectedUserId = ref<number | null>(null);

const submitting = ref(false);
const submitError = ref<string | null>(null);

const fallbackAvatar = "/kallan.svg";

function resetForm() {
  selectedUserId.value = null;
  submitting.value = false;
  submitError.value = null;
}

async function submit() {
  submitError.value = null;
  if (!selectedUserId.value) return;

  submitting.value = true;
  try {
    await apiGiveFikapinne(selectedUserId.value);
    dialogRef.value?.close();
  } catch (e) {
    submitError.value = e instanceof Error ? e.message : "Kunde inte ge fikapinne";
  } finally {
    submitting.value = false;
  }
}
</script>

<template>
  <dialog
    ref="dialogRef"
    id="give_fikapinne_modal"
    class="modal"
    @close="resetForm"
    @cancel.prevent="dialogRef?.close()"
  >
    <div class="modal-box">
      <form class="flex flex-col gap-4" @submit.prevent="submit">
        <div class="text-2xl text-center">Ge fikapinne</div>
        <div class="text-lg text-center opacity-70">Till vem?</div>

        <div v-if="usersStore.loading" class="flex items-center gap-2">
          <span class="loading loading-spinner"></span>
          <span class="text-sm opacity-70">Laddar...</span>
        </div>

        <div v-else class="max-h-72 overflow-y-auto pr-1">
          <div class="grid grid-cols-2 gap-3">
            <button
              v-for="user in usersStore.users"
              :key="user.id"
              type="button"
              class="card bg-base-100 shadow text-left border"
              :class="selectedUserId === user.id ? 'border-accent' : 'border-base-200'"
              @click="selectedUserId = user.id"
            >
              <div class="card-body p-3 items-center text-center gap-2">
                <div class="avatar">
                  <div
                    class="ring-primary ring-offset-base-100 size-12 rounded-full ring-2 ring-offset-2 overflow-hidden"
                  >
                    <img :src="user.avatar_url || fallbackAvatar" alt="Avatar" loading="lazy" />
                  </div>
                </div>
                <div class="text-xl font-medium truncate w-full">{{ user.username }}</div>
              </div>
            </button>
          </div>
        </div>

        <div v-if="submitError" class="text-sm text-error">{{ submitError }}</div>

        <div class="flex gap-3">
          <button
            type="button"
            class="btn btn-outline btn-lg flex-1"
            :disabled="submitting"
            @click="dialogRef?.close()"
          >
            Stäng
          </button>

          <button
            class="btn btn-primary btn-lg flex-1"
            type="submit"
            :disabled="!selectedUserId || submitting"
          >
            <span v-if="submitting" class="loading loading-spinner"></span>
            Ge
          </button>
        </div>
      </form>
    </div>

    <form method="dialog" class="modal-backdrop">
      <button aria-label="close">close</button>
    </form>
  </dialog>
</template>
