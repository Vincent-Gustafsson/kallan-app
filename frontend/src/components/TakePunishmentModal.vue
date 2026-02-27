<script setup lang="ts">
import { computed, ref } from "vue";
import { useUsersStore } from "@/stores/users";
import { usePunishmentsStore } from "@/stores/punishments";
import NumberInput from "@/components/NumberInput.vue";

const usersStore = useUsersStore();
const punishStore = usePunishmentsStore();

const dialogRef = ref<HTMLDialogElement | null>(null);

const step = ref<1 | 2>(1);

const selectedUserId = ref<number | null>(null);
const points = ref(1);

const submitting = ref(false);
const submitError = ref<string | null>(null);

const fallbackAvatar = "/kallan.svg";

function resetForm() {
  step.value = 1;
  selectedUserId.value = null;
  points.value = 1;
  submitting.value = false;
  submitError.value = null;
}

const selectedUser = computed(() =>
  selectedUserId.value == null
    ? null
    : (usersStore.users.find((u) => u.id === selectedUserId.value) ?? null),
);

const canNext = computed(() => {
  if (step.value === 1) return selectedUserId.value != null;
  if (step.value === 2) return true;
  return false;
});

function next() {
  if (!canNext.value) return;
  if (step.value < 2) step.value = 2;
}

function back() {
  if (step.value > 1) step.value = 1;
}

async function submit() {
  submitError.value = null;
  if (!selectedUserId.value) return;

  submitting.value = true;
  try {
    // TODO: implement in punishments store + backend
    // Example signature:
    // await punishStore.takeEvent({ target_id: selectedUserId.value, amount: points.value });
    await punishStore.takeEvent({
      target_id: selectedUserId.value,
      amount: points.value,
    });

    dialogRef.value?.close();
  } catch (e) {
    submitError.value = e instanceof Error ? e.message : "Kunde inte stryka straff";
  } finally {
    submitting.value = false;
  }
}
</script>

<template>
  <dialog
    ref="dialogRef"
    id="take_punishment_modal"
    class="modal"
    @close="resetForm"
    @cancel.prevent="dialogRef?.close()"
  >
    <div class="modal-box">
      <form class="flex flex-col gap-6" @submit.prevent="submit">
        <!-- Steps header -->
        <ul class="steps w-full">
          <li class="step" :class="{ 'step-primary': step >= 1 }">Vem</li>
          <li class="step" :class="{ 'step-primary': step >= 2 }">Antal</li>
        </ul>

        <!-- STEP 1: choose user -->
        <div v-if="step === 1" class="flex flex-col gap-3">
          <div class="text-2xl text-center">För vem?</div>

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

                  <div class="text-xl font-medium truncate w-full">
                    {{ user.username }}
                  </div>
                </div>
              </button>
            </div>
          </div>

          <div v-if="usersStore.error" class="text-sm text-error">
            {{ usersStore.error }}
          </div>
        </div>

        <!-- STEP 2: amount -->
        <div v-else class="flex flex-col gap-10 items-center mb-10">
          <div class="text-2xl text-center">Antal straff?</div>

          <NumberInput v-model="points" />
        </div>

        <!-- Errors -->
        <div v-if="submitError" class="text-sm text-center text-error">
          {{ submitError }}
        </div>

        <!-- Footer controls -->
        <div class="flex gap-3">
          <button
            type="button"
            class="btn btn-outline btn-lg flex-1"
            :disabled="step === 1 || submitting"
            @click="back"
          >
            Tillbaka
          </button>

          <button
            v-if="step < 2"
            type="button"
            class="btn btn-primary btn-lg flex-1"
            :disabled="!canNext || submitting"
            @click="next"
          >
            Nästa
          </button>

          <button
            v-else
            class="btn btn-error btn-lg flex-1"
            :disabled="!selectedUserId || submitting"
            type="submit"
          >
            <span v-if="submitting" class="loading loading-spinner"></span>
            Stryk straff
          </button>
        </div>
      </form>
    </div>

    <form method="dialog" class="modal-backdrop">
      <button aria-label="close">close</button>
    </form>
  </dialog>
</template>
