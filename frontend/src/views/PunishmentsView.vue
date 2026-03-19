<script setup lang="ts">
import PendingPunishments from "@/components/PendingPunishments.vue";
import ConfirmedPunishments from "@/components/ConfirmedPunishments.vue";

import { computed } from "vue";
import { usePunishmentsStore } from "@/stores/punishments";

const punishStore = usePunishmentsStore();
const hasPending = computed(() => (punishStore.pending?.length ?? 0) > 0);
</script>

<template>
  <div class="min-h-dvh bg-base-300 flex flex-col items-center px-4 pt-16 pb-28 gap-8">
    <PendingPunishments v-if="hasPending" class="w-full anim-slide-left" />
    <ConfirmedPunishments class="w-full anim-slide-right" />
  </div>
</template>

<style scoped>
@keyframes slide-from-left {
  from {
    transform: translateX(-40px);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}
@keyframes slide-from-right {
  from {
    transform: translateX(40px);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.anim-slide-left {
  animation: slide-from-left 0.35s ease both;
}
.anim-slide-right {
  animation: slide-from-right 0.35s ease both 0.1s;
}
</style>
