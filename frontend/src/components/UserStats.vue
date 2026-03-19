<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useAuthStore } from "@/stores/auth";
import { apiPunishmentStats, type PunishmentStats } from "@/lib/punishmentsApi";
import { apiFikapinneStats, type FikapinneStats } from "@/lib/fikapinnarApi";
import PunishmentIcon from "./PunishmentIcon.vue";

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
        <PunishmentIcon size="size-8" class="fill-neutral-content" />
      </div>

      <div class="stat-title">Straff</div>

      <div class="stat-value text-neutral-content min-h-10 flex items-center">
        <span v-if="loading" class="loading loading-spinner loading-sm"></span>
        <span v-else>{{ stats?.total_amount ?? 0 }}</span>
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
          viewBox="0 0 384 512"
          class="fill-neutral-content size-8"
        >
          <!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.-->
          <path
            d="M335.1 160c.6-5.3 .9-10.6 .9-16 0-79.5-64.5-144-144-144S48 64.5 48 144c0 5.4 .3 10.7 .9 16l-.9 0c-26.5 0-48 21.5-48 48s21.5 48 48 48l288 0c26.5 0 48-21.5 48-48s-21.5-48-48-48l-.9 0zM64 304L169.2 529.5c4.1 8.8 13 14.5 22.8 14.5s18.6-5.7 22.8-14.5L320 304 64 304z"
          />
        </svg>
      </div>

      <div class="stat-title">Fikapinnar</div>

      <div class="stat-value text-neutral-content min-h-10 flex items-center">
        <span v-if="fikaLoading" class="loading loading-spinner loading-sm"></span>
        <span v-else>{{ fika?.total_amount ?? 0 }}</span>
      </div>

      <div class="stat-desc">
        <span v-if="fikaError" class="text-error">{{ fikaError }}</span>
        <span v-else>+{{ fika?.month_amount ?? 0 }} denna månad</span>
      </div>
    </div>
  </div>
</template>
