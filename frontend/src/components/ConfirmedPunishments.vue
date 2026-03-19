<script setup lang="ts">
import { computed, onMounted } from "vue";
import { usePunishmentsStore } from "@/stores/punishments";
import FullPunishmentRow from "@/components/FullPunishmentRow.vue";

const punishStore = usePunishmentsStore();
const items = computed(() => punishStore.confirmed ?? []);
const LIMIT = 10;

onMounted(() => {
  if (!punishStore.loadingConfirmed && items.value.length === 0) {
    punishStore.fetchConfirmed({ limit: LIMIT });
  }
});
</script>

<template>
  <div class="w-full">
    <p class="text-xs font-semibold opacity-50 tracking-widest uppercase mb-2 px-1">
      Senaste straffen
    </p>
    <ul class="list bg-base-100 w-full rounded-box shadow-md overflow-hidden">
      <template v-if="punishStore.loadingConfirmed">
        <li v-for="i in LIMIT" :key="'sk-' + i" class="list-row items-center">
          <div class="flex -space-x-2 shrink-0">
            <div class="skeleton size-8 rounded-full"></div>
            <div class="skeleton size-8 rounded-full"></div>
            <div class="skeleton size-8 rounded-full"></div>
          </div>
          <div class="min-w-0 flex-1 flex flex-col gap-1">
            <div class="skeleton h-4 w-32"></div>
            <div class="skeleton h-3 w-24"></div>
            <div class="skeleton h-3 w-36"></div>
          </div>
          <div class="flex flex-col items-end gap-1 shrink-0">
            <div class="skeleton h-3 w-16 rounded"></div>
            <div class="skeleton h-4 w-10 rounded"></div>
          </div>
        </li>
      </template>

      <template v-else>
        <li v-if="items.length === 0" class="p-4 text-sm opacity-60">
          Inga bekräftade straff än 🎉
        </li>
        <FullPunishmentRow
          v-else
          v-for="(p, idx) in items"
          :key="p.id"
          :p="p"
          class="punch-row"
          :style="{ '--delay': `${idx * 0.06}s` }"
        />
      </template>
    </ul>

    <div v-if="punishStore.error" class="text-sm text-error mt-2 px-1">
      {{ punishStore.error }}
    </div>
  </div>
</template>

<style scoped>
@keyframes slide-in-left {
  from { transform: translateX(-100%); opacity: 0; }
  to   { transform: translateX(0);     opacity: 1; }
}

:deep(.punch-row) {
  animation: slide-in-left 0.3s ease both;
  animation-delay: var(--delay, 0s);
}
</style>
