<script setup lang="ts">
import { computed, onMounted } from "vue";
import { usePunishmentsStore } from "@/stores/punishments";
import ConfirmedPunishmentCard from "@/components/ConfirmedPunishmentCard.vue";

const punishStore = usePunishmentsStore();
const items = computed(() => punishStore.confirmed ?? []);

onMounted(() => {
  if (!punishStore.loadingConfirmed && items.value.length === 0) {
    punishStore.fetchConfirmed({ limit: 10 });
  }
});
</script>

<template>
  <div class="w-full">
    <div class="pb-2 text-md opacity-60">Senaste straffen</div>

    <div v-if="punishStore.loadingConfirmed" class="px-4 pb-4">
      <span class="loading loading-spinner"></span>
    </div>

    <div v-else>
      <ul v-if="items.length > 0" class="list bg-base-100 rounded-box border border-base-200">
        <ConfirmedPunishmentCard v-for="p in items" :key="p.id" :p="p" />
      </ul>

      <div v-else class="opacity-60 text-sm py-2">Inga bekräftade straff än</div>
    </div>

    <div v-if="punishStore.error" class="px-4 pb-4 text-sm text-error">
      {{ punishStore.error }}
    </div>
  </div>
</template>
