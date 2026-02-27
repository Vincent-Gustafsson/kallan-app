<script setup lang="ts">
import GivePunishmentModal from "@/components/GivePunishmentModal.vue";
import TakePunishmentModal from "@/components/TakePunishmentModal.vue";
import PendingPunishments from "@/components/PendingPunishments.vue";
import ConfirmedPunishments from "@/components/ConfirmedPunishments.vue";

import { computed } from "vue";
import { usePunishmentsStore } from "@/stores/punishments";
import { useAuthStore } from "@/stores/auth";

const punishStore = usePunishmentsStore();
const hasPending = computed(() => (punishStore.pending?.length ?? 0) > 0);

const authStore = useAuthStore();
const tier = computed(() => authStore.user?.tier ?? "bandana");
const showMenu = computed(() => tier.value !== "bandana");
const showTake = computed(() => tier.value === "vest");
</script>

<template>
  <div class="min-h-dvh bg-base-300 flex flex-col items-center justify-center px-4 gap-4">
    <GivePunishmentModal />
    <TakePunishmentModal />

    <PendingPunishments v-if="hasPending" class="mt-20" />

    <ConfirmedPunishments :class="[hasPending ? 'flex-2' : 'flex-2 mt-20', 'mb-20']" />
  </div>

  <ul
    v-if="showMenu"
    class="menu fixed w-max bottom-20 left-1/2 -translate-x-1/2 menu-horizontal font-bold bg-neutral rounded-box"
  >
    <li onclick="give_punishment_modal.showModal()">
      <a>Ge straff</a>
    </li>

    <li v-if="showTake" onclick="take_punishment_modal.showModal()">
      <a>Stryk straff</a>
    </li>
  </ul>
</template>
