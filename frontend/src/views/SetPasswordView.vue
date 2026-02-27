<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";

import WaffleRain from "@/components/WaffleRain.vue";

const router = useRouter();
const auth = useAuthStore();

const newPassword = ref("");
const confirmPassword = ref("");

const loading = ref(false);
const errorMsg = ref<string | null>(null);

function validate(): string | null {
  if (newPassword.value.length < 8) return "Use at least 8 characters.";
  if (newPassword.value !== confirmPassword.value) return "Passwords do not match.";
  return null;
}

async function onSubmit() {
  errorMsg.value = null;

  const v = validate();
  if (v) {
    errorMsg.value = v;
    return;
  }

  loading.value = true;
  try {
    await auth.setPassword(newPassword.value);
    await router.replace({ name: "home" });
  } catch (e) {
    errorMsg.value = e instanceof Error ? e.message : "Password change failed";
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <WaffleRain />

  <div class="min-h-dvh flex flex-col items-center justify-center gap-6 relative z-10">
    <img src="/kallan.svg" class="size-50" />

    <div class="text-center px-10">
      <h1 class="text-2xl font-bold">Välj ett nytt lösenord</h1>
    </div>

    <form class="flex flex-col gap-4 w-full max-w-md px-10" @submit.prevent="onSubmit">
      <div
        class="alert alert-error text-sm shadow-md text-center justify-center min-h-12 transition-opacity duration-150"
        :class="errorMsg ? 'opacity-100' : 'opacity-0 pointer-events-none'"
        aria-live="polite"
      >
        <span>{{ errorMsg ?? "\u00A0" }}</span>
      </div>

      <input
        v-model="newPassword"
        type="password"
        class="input input-bordered input-xl w-full"
        placeholder="Lösenord"
        autocomplete="new-password"
        :disabled="loading"
        required
      />

      <input
        v-model="confirmPassword"
        type="password"
        class="input input-bordered input-xl w-full"
        placeholder="Upprepa lösenord"
        autocomplete="new-password"
        :disabled="loading"
        required
      />

      <button class="btn btn-primary btn-block mt-2 h-12 text-lg" :disabled="loading" type="submit">
        <span v-if="loading" class="loading loading-spinner"></span>
        <span v-else>Byt lösenord</span>
      </button>
    </form>
  </div>
</template>
