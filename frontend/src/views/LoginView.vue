<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";

import WaffleRain from "@/components/WaffleRain.vue";

const router = useRouter();
const auth = useAuthStore();

const username = ref("");
const password = ref("");
const loading = ref(false);
const errorMsg = ref<string | null>(null);

async function onSubmit() {
  errorMsg.value = null;
  loading.value = true;

  try {
    await auth.login(username.value.trim(), password.value);
    await router.replace({ name: auth.mustResetPassword ? "set-password" : "home" });
  } catch (e) {
    errorMsg.value = e instanceof Error ? e.message : "Login failed";
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <WaffleRain />

  <div class="min-h-dvh flex flex-col items-center justify-center gap-6 relative z-10">
    <img src="/kallan.svg" class="size-50" />

    <form class="flex flex-col gap-4 w-full max-w-md px-10" @submit.prevent="onSubmit">
      <div
        class="alert alert-error text-sm shadow-md text-center justify-center min-h-12 transition-opacity duration-150"
        :class="errorMsg ? 'opacity-100' : 'opacity-0 pointer-events-none'"
        aria-live="polite"
      >
        <span>{{ errorMsg ?? "\u00A0" }}</span>
      </div>

      <input
        id="username"
        v-model="username"
        class="input input-bordered input-xl w-full"
        placeholder="Källannamn"
        autocomplete="username"
        inputmode="text"
        autocapitalize="none"
        autocorrect="off"
        :disabled="loading"
        required
      />

      <input
        id="password"
        v-model="password"
        type="password"
        class="input input-bordered input-xl w-full"
        placeholder="Lösenord"
        autocomplete="current-password"
        :disabled="loading"
        required
      />

      <button class="btn btn-primary btn-block mt-2 h-12 text-lg" :disabled="loading" type="submit">
        <span v-if="loading" class="loading loading-spinner"></span>
        <span v-else>Logga in</span>
      </button>
    </form>
  </div>
</template>
