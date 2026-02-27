<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useAuthStore } from "@/stores/auth";
import { apiPunishmentStats, type PunishmentStats } from "@/lib/punishmentsApi";
import { apiFikapinneStats, type FikapinneStats } from "@/lib/fikapinnarApi";

const props = defineProps<{ userId?: number }>();

const auth = useAuthStore();
const effectiveUserId = computed(() => props.userId ?? auth.user?.id ?? null);

const loading = ref(false);
const error = ref<string | null>(null);
const stats = ref<PunishmentStats | null>(null);

const fikaLoading = ref(false);
const fikaError = ref<string | null>(null);
const fika = ref<FikapinneStats | null>(null);

async function load() {
  if (!effectiveUserId.value) return;

  loading.value = true;
  fikaLoading.value = true;
  error.value = null;
  fikaError.value = null;

  try {
    const [pStats, fStats] = await Promise.all([
      apiPunishmentStats({ target_id: effectiveUserId.value }),
      apiFikapinneStats({ target_id: effectiveUserId.value }),
    ]);
    stats.value = pStats;
    fika.value = fStats;
  } catch (e) {
    // you can split errors if you want; simplest:
    stats.value = null;
    fika.value = null;
    const msg = e instanceof Error ? e.message : "Failed to load stats";
    error.value = msg;
    fikaError.value = msg;
  } finally {
    loading.value = false;
    fikaLoading.value = false;
  }
}

onMounted(load);
watch(effectiveUserId, () => load());
</script>

<template>
  <div class="stats shadow bg-base-100 w-full">
    <div class="stat p-4">
      <div class="stat-figure text-secondary">
        <!-- trophy icon -->
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 320 512"
          fill="currentColor"
          class="size-8"
        >
          <path
            d="M32.6 25.7C35.6 10.8 48.7 0 64 0L256 0c15.3 0 28.4 10.8 31.4 25.7L316.8 173c2.1 10.5 3.2 21.2 3.2 32l0 3c0 77.4-55 142-128 156.8l0 115.2 64 0c17.7 0 32 14.3 32 32s-14.3 32-32 32L64 544c-17.7 0-32-14.3-32-32s14.3-32 32-32l64 0 0-115.2C55 350 0 285.4 0 208l0-3c0-10.7 1.1-21.4 3.2-32L32.6 25.7zM77.4 128l165.1 0-12.8-64-139.5 0-12.8 64z"
          />
        </svg>
      </div>

      <div class="stat-title">Straff</div>

      <div v-if="loading" class="stat-value text-neutral-content">
        <span class="loading loading-spinner loading-sm"></span>
      </div>
      <div v-else class="stat-value text-neutral-content">
        {{ stats?.total_amount ?? 0 }}
      </div>

      <div class="stat-desc">
        <span v-if="error" class="text-error">{{ error }}</span>
        <span v-else>+{{ stats?.week_amount ?? 0 }} denna vecka</span>
      </div>
    </div>

    <div class="stat p-4">
      <div class="stat-figure text-secondary">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 512 512"
          fill="currentColor"
          class="size-8"
        >
          <path
            d="M257.5 27.6c-.8-5.4-4.9-9.8-10.3-10.6-22.1-3.1-44.6 .9-64.4 11.4l-74 39.5C89.1 78.4 73.2 94.9 63.4 115L26.7 190.6c-9.8 20.1-13 42.9-9.1 64.9l14.5 82.8c3.9 22.1 14.6 42.3 30.7 57.9l60.3 58.4c16.1 15.6 36.6 25.6 58.7 28.7l83 11.7c22.1 3.1 44.6-.9 64.4-11.4l74-39.5c19.7-10.5 35.6-27 45.4-47.2l36.7-75.5c9.8-20.1 13-42.9 9.1-64.9-.9-5.3-5.3-9.3-10.6-10.1-51.5-8.2-92.8-47.1-104.5-97.4-1.8-7.6-8-13.4-15.7-14.6-54.6-8.7-97.7-52-106.2-106.8z"
          />
        </svg>
      </div>

      <div class="stat-title">Fikapinnar</div>

      <div v-if="fikaLoading" class="stat-value text-neutral-content">
        <span class="loading loading-spinner loading-sm"></span>
      </div>
      <div v-else class="stat-value text-neutral-content">
        {{ fika?.total_amount ?? 0 }}
      </div>

      <div class="stat-desc">
        <span v-if="fikaError" class="text-error">{{ fikaError }}</span>
        <span v-else>+{{ fika?.month_amount ?? 0 }} denna månad</span>
      </div>
    </div>
  </div>
</template>
