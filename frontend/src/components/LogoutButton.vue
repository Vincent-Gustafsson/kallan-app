<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const props = withDefaults(
  defineProps<{
    to?: string;
    label?: string;
    compact?: boolean;
  }>(),
  {
    to: "login",
    label: "Logga ut",
    compact: false,
  },
);

const router = useRouter();
const auth = useAuthStore();

const loading = ref(false);
const errorMsg = ref<string | null>(null);

async function onClick() {
  errorMsg.value = null;
  loading.value = true;

  try {
    await auth.logout();
    await router.replace({ name: props.to });
  } catch (e) {
    errorMsg.value = e instanceof Error ? e.message : "Logout failed";
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="flex flex-col items-end gap-2">
    <button
      class="btn"
      :class="[compact ? 'btn-ghost btn-sm' : 'btn-outline', loading ? 'btn-disabled' : '']"
      type="button"
      @click="onClick"
    >
      <span v-if="loading" class="loading loading-spinner"></span>
      <span v-else>{{ label }}</span>
    </button>

    <div v-if="errorMsg" class="text-xs text-error">{{ errorMsg }}</div>
  </div>
</template>
