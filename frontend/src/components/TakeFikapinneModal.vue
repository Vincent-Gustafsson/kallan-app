<script setup lang="ts">
import { ref, computed } from "vue";
import { useUsersStore } from "@/stores/users";
import { apiTakeFikapinnar } from "@/lib/fikapinnarApi";

const usersStore = useUsersStore();

const dialogRef = ref<HTMLDialogElement | null>(null);
const step = ref<1 | 2>(1);

const selectedUserId = ref<number | null>(null);
const amount = ref<3 | 5>(3);

const submitting = ref(false);
const submitError = ref<string | null>(null);

const fallbackAvatar = "/kallan.svg";

function resetForm() {
  step.value = 1;
  selectedUserId.value = null;
  amount.value = 3;
  submitting.value = false;
  submitError.value = null;
}

const canNext = computed(() => (step.value === 1 ? selectedUserId.value != null : true));

function next() {
  if (!canNext.value) return;
  step.value = 2;
}

function back() {
  step.value = 1;
}

async function submit() {
  submitError.value = null;
  if (!selectedUserId.value) return;

  submitting.value = true;
  try {
    await apiTakeFikapinnar(selectedUserId.value, amount.value);
    dialogRef.value?.close();
  } catch (e) {
    submitError.value = e instanceof Error ? e.message : "Kunde inte stryka fikapinnar";
  } finally {
    submitting.value = false;
  }
}
</script>

<template>
  <dialog
    ref="dialogRef"
    id="take_fikapinne_modal"
    class="modal"
    @close="resetForm"
    @cancel.prevent="dialogRef?.close()"
  >
    <div class="modal-box">
      <form class="flex flex-col gap-6" @submit.prevent="submit">
        <ul class="steps w-full">
          <li class="step" :class="{ 'step-primary': step >= 1 }">Vem</li>
          <li class="step" :class="{ 'step-primary': step >= 2 }">Antal</li>
        </ul>

        <div v-if="step === 1" class="flex flex-col gap-3">
          <div class="text-2xl text-center">Stryk fikapinnar</div>
          <div class="text-lg text-center opacity-70">Från vem?</div>

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
        </div>

        <div v-else class="flex flex-col gap-4">
          <div class="text-2xl text-center">Hur många?</div>

          <div class="flex justify-center">
            <div class="inline-flex">
              <label
                class="btn btn-outline border-2 rounded-r-none"
                :class="amount === 3 ? 'btn-primary' : ''"
              >
                <input class="sr-only" type="radio" :value="3" v-model="amount" />
                Ta bort 3
              </label>

              <label
                class="btn btn-outline border-2 rounded-l-none -ml-px"
                :class="amount === 5 ? 'btn-primary' : ''"
              >
                <input class="sr-only" type="radio" :value="5" v-model="amount" />
                Ta bort 5
              </label>
            </div>
          </div>
        </div>

        <div v-if="submitError" class="text-sm text-error">{{ submitError }}</div>

        <div class="flex gap-3">
          <button
            type="button"
            class="btn btn-outline btn-lg flex-1"
            :disabled="submitting || step === 1"
            @click="back"
          >
            Tillbaka
          </button>

          <button
            v-if="step === 1"
            type="button"
            class="btn btn-primary btn-lg flex-1"
            :disabled="!canNext || submitting"
            @click="next"
          >
            Nästa
          </button>

          <button
            v-else
            type="submit"
            class="btn btn-primary btn-lg flex-1"
            :disabled="!selectedUserId || submitting"
          >
            <span v-if="submitting" class="loading loading-spinner"></span>
            Stryk
          </button>
        </div>
      </form>
    </div>

    <form method="dialog" class="modal-backdrop">
      <button aria-label="close">close</button>
    </form>
  </dialog>
</template>
